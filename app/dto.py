from typing import Any, Dict

from pydantic import BaseModel


class ConfigureDTO(BaseModel):
    host: str
    access_key: str
    pass_key: str
    secure: bool


class DeleteTemplate(BaseModel):
    template_name: str


class PublipostDTO(BaseModel):
    data: Dict[str, Any]
    template_name: str
    output_bucket: str
    output_name: str
    # don't actually know if will get used
    options: list = []
    push_result: bool = True


class GetPlaceholderDTO(BaseModel):
    name: str


class TemplateInfos(BaseModel):
    bucket_name: str
    template_name: str
    exposed_as: str
