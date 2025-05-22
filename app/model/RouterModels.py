from pydantic import BaseModel
from typing import List, Union, Dict

class UuidResponse(BaseModel):
    """Returns the response to a user inout uuid query, both on frontend and /api/materials/{uuid}"""
    uuid_in: str
    material_info: List[Dict] = None
    message: str

class DatasetVersion(BaseModel):
    """Stores the most recent dataset version and answering an API call on /api/dataset_info"""
    name: str = None
    description: str = None
    updated: str = None
    uuid: str = None

class UpdateResponse(BaseModel):
    """Answer to an an API call on /api/update"""
    message: str
    name: str = None
    description: str = None
    uuid: str = None