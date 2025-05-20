from pydantic import BaseModel
from typing import List, Union

from typing import Optional, List

class MaterialMatchOut(BaseModel):
    specific_material: Optional[dict] = None
    matches: Optional[List[dict]] = None
    message: str

class UuidsOut(BaseModel):
    """Used for returning the response to a user inout uuid query, both on frontend and /api/materials/{uuid}"""
    uuid_in: str
    uuids_out: Union[List[str], str] = None
    message: str
    matches_info: Union[list, None] = None

class DatasetVersion(BaseModel):
    """Used for storing the most recent dataset version and answering an API call on /api/dataset_info"""
    name: str = None
    description: str = None
    updated: str = None
    uuid: str = None

class UpdateResponse(BaseModel):
    """Used for answering an API call on /api/update"""
    message: str
    name: str = None
    description: str = None
    uuid: str = None