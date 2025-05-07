from pydantic import BaseModel

class FlowchartRequest(BaseModel):
    prompt: str
    direction: str
    complexity: str