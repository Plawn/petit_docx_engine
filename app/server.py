import logging
import time
import traceback
from dataclasses import dataclass
from typing import Dict, List

import minio
from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse

from .dto import ConfigureDTO, DeleteTemplate, GetPlaceholderDTO, PublipostDTO, TemplateInfos
from .engine import Template
from .utils import download_minio_stream


class Context:
    def __init__(self):
        self.minio_client: minio.Minio = None


context = Context()


@dataclass
class TemplateContainer:
    templater: Template
    pulled_at: float


# in memory database
# rebuilded at each boot
db: Dict[str, TemplateContainer] = {}


# in memory database
# rebuilded at each boot
db: Dict[str, TemplateContainer] = {}

app = FastAPI()


@app.post('/configure')
def configure(body: ConfigureDTO):
    try:
        minio_client = minio.Minio(
            body.host, body.access_key, body.pass_key, secure=body.secure)
        # checking that the instance is correct
        minio_client.list_buckets()
        context.minio_client = minio_client
        return JSONResponse({'error': False}, 200)
    except:
        return JSONResponse({'error': True}, 400)


def pull_template(template_infos: TemplateInfos):
    doc = context.minio_client.get_object(
        template_infos.remote_bucket, template_infos.template_name)
    _file = download_minio_stream(doc)
    template = Template(_file)
    db[template_infos.exposed_as] = TemplateContainer(template, time.time())
    return template


@app.post('/load_templates')
def load_template(data: List[TemplateInfos]):
    success = []
    failed = []
    for template_infos in data:
        try:
            template = pull_template(template_infos)
            success.append({
                'template_name': template_infos.exposed_as,
                'fields': template.fields
            })
        except:
            logging.error(traceback.format_exc())
            failed.append({'template_name': template_infos.exposed_as})
    return JSONResponse({'success': success, 'failed': failed})


@app.post('/get_placeholders')
def get_placeholders(data: GetPlaceholderDTO):
    return JSONResponse(db[data.name].templater.fields)


@app.post('/publipost')
def publipost(body: PublipostDTO):
    output = None
    try:
        output = db[body.template_name].templater.render(body.data)
        length = len(output.getvalue())
        output.seek(0)
        if body.push_result:
            # should make abstraction to push the result here
            context.minio_client.put_object(
                body.output_bucket, body.output_name, output, length=length
            )
            return JSONResponse({'error': False})
        else:
            # not used for now
            # should push the file back
            return JSONResponse({'result': 'OK'})
    except Exception as e:
        logging.error(traceback.format_exc())
        return JSONResponse({'error': traceback.format_exc()}, 500)


@app.get('/list')
def get_templates():
    return JSONResponse({
        key: value.pulled_at for key, value in db.items()
    })


@app.delete('/remove_template')
def remove_template(body: DeleteTemplate):
    try:
        del db[body.template_name]
        return JSONResponse({'error': False})
    except:
        return JSONResponse({'error': True}, 400)


@app.get('/live')
def is_live():
    return Response('OK', 200) if context.minio_client is not None else Response('KO', 402)
