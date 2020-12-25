from pydantic import BaseModel


class ConfigureDTO(BaseModel):
    host: str
    access_key: str
    pass_key: str
    secure: bool



class DeleteTemplate(BaseModel):
    template_name: str