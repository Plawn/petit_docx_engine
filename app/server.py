import traceback
from flask import Flask, request, jsonify
import minio
from .engine import Template
from typing import List, Dict
import os

minio_client: minio.Minio = None
db: Dict[str, Template] = {}
template_folder = 'templates'

app = Flask(__name__)


@app.route('/configure', methods=['POST'])
def configure():
    global minio_client
    data = request.get_json()

    host = data['host']
    access_key = data['access_key']
    pass_key = data['pass_key']
    minio_client = minio.Minio(host, access_key, pass_key)
    return jsonify({'error': False}), 200


def make_name(filename: str) -> str:
    return os.path.join(template_folder, filename)


@app.route('/load_templates', methods=['POST'])
def load_template():
    data: List[dict] = request.get_json()
    success = []
    failed = []
    for item in data:
        try:
            remote_bucket = item['bucket_name']
            filename = item['template_name']
            doc = minio_client.get_object(remote_bucket, filename)
            name = make_name(filename)
            with open(name, 'wb') as file_data:
                for d in doc.stream(32*1024):
                    file_data.write(d)
            db[filename] = Template(name)
            success.append(item)
        except:
            traceback.print_exc()
            failed.append(item)
    return jsonify({'success': success, 'failed': failed})


@app.route('/get_placeholders', methods=['POST'])
def get_placeholders():
    data = request.get_json()
    return jsonify(db[data['name']].fields)


@app.route('/publipost', methods=['POST'])
def publipost():
    body = request.get_json()
    try:

        data = body['data']
        name = body['template_name']
        output_bucket = body['output_bucket']
        output_name = body['output_name']

        output = db[name].render(data)

        minio_client.fput_object(output_bucket, output_name, output)

        return jsonify({'error': False})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': True})
