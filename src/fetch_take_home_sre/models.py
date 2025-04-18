from pydantic import BaseModel
from typing import Optional

class EndpointHealthCheckConfig(BaseModel):
    """Model config for health check data in yaml files
    """    
    body: Optional[str] = None
    headers: dict[str, str] = None
    method: Optional[str] = "GET"
    name: str
    url: str