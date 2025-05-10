from pydantic import BaseModel
from typing import List, Union

class UuidsOut(BaseModel):
    uuid_in: str
    uuids_out: Union[List[str], str] =None
    message: str

class DatasetVersion(BaseModel):
    name: str = None
    description: str = None
    updated: str = None
    uuid: str = None

class UpdateResponse(BaseModel):
    message: str
    name: str = None
    description: str = None
    uuid: str = None