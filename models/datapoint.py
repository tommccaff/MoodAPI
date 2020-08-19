from pydantic import BaseModel

class Datapoint(BaseModel):
    username: str
    epochday: int
