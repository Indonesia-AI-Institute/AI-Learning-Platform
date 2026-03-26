from typing import Optional
from pydantic import BaseModel


class ClassUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None