import io
import logging
import os
import time
import traceback
from dataclasses import dataclass
from typing import Dict, List

import minio
from flask import Flask, jsonify, request

from .engine import Template
from .utils import download_minio_stream, ensure_folder_exists

minio_client: minio.Minio = None


@dataclass
class TemplateContainer:
    templater: Template
    pulled_at: float


# in memory database
# rebuilded at each boot
db: Dict[str, TemplateContainer] = {}

TEMPLATE_FOLDER = 'templates'
TEMP_FOLDER = 'temp'
# ensure we can pull the data in the folder
ensure_folder_exists(TEMPLATE_FOLDER)
# ensure we can save temporary in this folder
ensure_folder_exists(TEMP_FOLDER)

# in memory database
# rebuilded at each boot
db: Dict[str, TemplateContainer] = {}

app = Flask(__name__)


def make_name(filename: str) -> str:
    return os.path.join(TEMPLATE_FOLDER, filename)


@app.route('/configure', methods=['POST'])
def configure():
    # maybe have a global conf object instead
    global minio_client
    data = request.get_json()

    host = data['host']
    access_key = data['access_key']
    pass_key = data['pass_key']
    secure = data['secure']
    try:
        minio_client = minio.Minio(host, access_key, pass_key, secure=secure)
        # checking that the instance is correct
        minio_client.list_buckets()
    except:
        minio_client = None
    return jsonify({'error': False}), 200


def pull_template(template_infos: dict):
    remote_bucket = template_infos['bucket_name']
    template_name = template_infos['template_name']
    exposed_as = template_infos['exposed_as']
    doc = minio_client.get_object(remote_bucket, template_name)
    name = make_name(template_name)
    _file = io.BytesIO()
    download_minio_stream(doc, _file)
    template = Template(_file)
    db[exposed_as] = TemplateContainer(template, time.time())
    # removing the file -> no need to persist it, it's loaded in memory now
    # os.remove(name)
    return template


@app.route('/load_templates', methods=['POST'])
def load_template():
    data: List[dict] = request.get_json()
    success = []
    failed = []
    for template_infos in data:
        try:
            template = pull_template(template_infos)
            success.append({
                'template_name': template_infos['exposed_as'],
                'fields': template.fields
            })
        except:
            logging.error(traceback.format_exc())
            failed.append({'template_name': template_infos['exposed_as']})
    return jsonify({'success': success, 'failed': failed})


@app.route('/get_placeholders', methods=['POST'])
def get_placeholders():
    data = request.get_json()
    return jsonify(db[data['name']].templater.fields)


@app.route('/publipost', methods=['POST'])
def publipost():
    body: Dict[str, object] = request.get_json()
    output = None
    try:

        data: str = body['data']
        template_name: str = body['template_name']
        output_bucket: str = body['output_bucket']
        output_name: str = body['output_name']
        # don't actually know if will get used
        options = body.get('options', [])
        push_result = body.get('push_result', True)
        output = db[template_name].templater.render(data)
        length = len(output.getvalue())
        output.seek(0)
        if push_result:
            # should make abstraction to push the result here
            minio_client.put_object(
                output_bucket, output_name, output, length=length
            )
            return jsonify({'error': False})
        else:
            # not used for now
            # should push the file back
            return jsonify({'result': 'OK'})
    except Exception as e:
        logging.error(traceback.format_exc())
        return jsonify({'error':traceback.format_exc()}), 500


@app.route('/list', methods=['GET'])
def get_templates():
    return jsonify({key: value.pulled_at for key, value in db.items()})


@app.route('/remove_template', methods=['DELETE'])
def remove_template():
    js = request.get_json()
    try:
        template_name: str = js['template_name']
        del db[template_name]
        return jsonify({'error': False})
    except:
        return jsonify({'error': True}), 400


@app.route('/live', methods=['GET'])
def is_live():
    return ('OK', 200) if minio_client is not None else ('KO', 402)
