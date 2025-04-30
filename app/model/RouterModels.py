from pydantic import BaseModel
from typing import List, Union

class UuidsOut(BaseModel):
    uuid_in: str
    uuids_out: Union[List[str], str] =None
    message: str