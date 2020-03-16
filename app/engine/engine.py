from docxtpl import DocxTemplate as _docxTemplate
import re
import copy
from . import utils
from typing import Dict
import docx
import os
import uuid


class docxTemplate(_docxTemplate):
    """Proxying the real class in order to be able to copy.copy the template docx file
    """

    def __init__(self, filename: str = '', document:docx.Document=None):
        self.crc_to_new_media = {}
        self.crc_to_new_embedded = {}
        self.pic_to_replace = {}
        self.pic_map = {}
        self.docx = document if document is not None else docx.Document(
            filename)


class Template:
    def __init__(self, filename: str):
        self.doc:docxTemplate = None
        self.fields: Set[str] = set()
        self.init(filename)
        self.temp_dir = 'temp'

    def init(self, filename: str) -> None:
        """Loads the document from the filename and inits it's values
        """
        # pulled filename
        self.doc = docxTemplate(filename)
        self.__load_fields()

    def __load_fields(self):
        self.fields = list(utils.xml_cleaner(set(re.findall(
            r"\{{(.*?)\}}", self.doc.get_xml(), re.MULTILINE))))

    def __apply_template(self, data: Dict[str, str]) -> docxTemplate:
        """
        Applies the data to the template and returns a `Template`
        """

        # kinda ugly i know but
        # we can avoid re reading the file from the disk as we already cached it
        doc = copy.copy(self.doc.docx)
        renderer = docxTemplate(document=doc)
        # here we restore the content of the docx inside the new renderer
        renderer.render(data)
        return doc

    def render(self, data: Dict[str, object]) -> str:
        save_path = os.path.join(self.temp_dir, str(uuid.uuid4()))
        doc = self.__apply_template(data)
        doc.save(save_path)
        return save_path