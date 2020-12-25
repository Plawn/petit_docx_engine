import copy
import os
import io
import re
import uuid
from typing import *

import docx
from docx.document import Document
from docx.parts.document import DocumentPart
from docxtpl import DocxTemplate

from . import utils


class Template:

    def __init__(self, _file: io.BytesIO):
        self.fields: List[str] = list()
        self.file = _file
        self.__load_fields()

    def __load_fields(self):
        doc = DocxTemplate(self.file)
        # here we get all the fields in the styles and paragraphs
        fields = set(utils.xml_cleaner(set(re.findall(
            r"\{{(.*?)\}}", doc.get_xml(), re.MULTILINE))))

        all_text: Set[str] = set()
        doc: Document = docx.Document(self.file)
        all_text.update(utils.get_text_from_doc_part(doc))
        
        for section in doc.sections:
            # not entirely working
            all_text.update(utils.get_text_from_doc_part(section.footer))
            all_text.update(utils.get_text_from_doc_part(section.first_page_footer))
            # working as expected
            all_text.update(utils.get_text_from_doc_part(section.header))
            all_text.update(utils.get_text_from_doc_part(section.first_page_header))

        others = set(
            re.findall(r"\{{(.*?)\}}", ''.join(all_text), re.MULTILINE)
        )

        fields.update(others)
        self.fields = list(fields)

    def __apply_template(self, data: Dict[str, str]) -> DocxTemplate:
        """
        Applies the data to the template and returns a `Template`
        """

        # kinda ugly i know but
        # we can avoid re reading the file from the disk as we already cached it
        renderer = DocxTemplate(self.file)
        # here we restore the content of the docx inside the new renderer
        renderer.render(data)
        return renderer

    def render(self, data: Dict[str, object]) -> io.BytesIO:
        doc = self.__apply_template(data)
        _file = io.BytesIO()
        doc.save(_file)
        return _file
