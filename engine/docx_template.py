# import copy
# import json
# import re
# from typing import Dict, Generator, Set, Union
# import os
# import docx
# from docxtpl import DocxTemplate as _docxTemplate
# import uuid
# from ..base_template_engine import TemplateEngine
# from ..ReplacerMiddleware import MultiReplacer
# from . import utils
# from ..model_handler import Model, SyntaxtKit
# from ...minio_creds import PullInformations, MinioPath

# TEMP_FOLDER = 'temp'
# SYNTAX_KIT = SyntaxtKit('{{', '}}', '.')


# # placeholder for now
# def add_infos(_dict: dict) -> None:
#     """Will add infos to the field on the fly
#     """
#     _dict.update({'traduction': ''})


# class DocxTemplator(TemplateEngine):
#     """
#     """
#     requires_env = []

#     def __init__(self, pull_infos: PullInformations, replacer: MultiReplacer, temp_dir: str, settings: dict):
#         self.doc: docxTemplate = None
#         self.temp_dir = temp_dir
#         self.init()

#     def __load_fields(self) -> None:
#         fields: Set[str] = set(re.findall(
#             r"\{{(.*?)\}}", self.doc.get_xml(), re.MULTILINE))
#         cleaned = list()
#         for field in utils.xml_cleaner(fields):
#             field, additional_infos = self.replacer.from_doc(field)
#             add_infos(additional_infos)
#             cleaned.append((field.strip(), additional_infos))
#         self.model = Model(cleaned, self.replacer, SYNTAX_KIT)

#     def init(self) -> None:
#         """Loads the document from the filename and inits it's values
#         """
#         # pulling template from the bucket
#         doc = self.pull_infos.minio.get_object(
#             self.pull_infos.remote.bucket,
#             self.pull_infos.remote.filename)
#         with open(self.filename, 'wb') as file_data:
#             for d in doc.stream(32*1024):
#                 file_data.write(d)
#         self.doc = docxTemplate(self.filename)
#         self.__load_fields()


