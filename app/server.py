import traceback
from flask import Flask, request, jsonify
import minio
from .engine import Template
from typing import List, Dict
import os
import logging

minio_client: minio.Minio = None
db: Dict[str, Template] = {}
template_folder = 'templates'

if not os.path.exists(template_folder):
    os.mkdir(template_folder)


app = Flask(__name__)


@app.route('/configure', methods=['POST'])
def configure():
    global minio_client
    data = request.get_json()

    host = data['host']
    access_key = data['access_key']
    pass_key = data['pass_key']
    secure = data['secure']
    minio_client = minio.Minio(host, access_key, pass_key, secure)
    # checking that the instance is correct
    minio_client.list_buckets()
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
            logging.error(traceback.format_exc())
            traceback.print_exc()
            failed.append(item)
    return jsonify({'success': success, 'failed': failed})


@app.route('/get_placeholders', methods=['POST'])
def get_placeholders():
    data = request.get_json()
    return jsonify(db[data['name']].fields)


@app.route('/publipost', methods=['POST'])
def publipost():
    body:Dict[str, object] = request.get_json()
    try:

        data: str = body['data']
        name: str = body['template_name']
        output_bucket: str = body['output_bucket']
        output_name: str = body['output_name']
        # don't actually know if will get used
        options = body.get('options', [])
        push_result = body.get('push_result', True)
        output = db[name].render(data)

        if push_result :
            minio_client.fput_object(output_bucket, output_name, output)
            return jsonify({'error': False})
        else:
            # not used for now
            # should push the file back
            return jsonify({'result':'OK'})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': True}), 500

    finally:
        os.remove(output)
