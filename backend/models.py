from pydantic import BaseModel, Field
from typing import Literal

class TaskRequest(BaseModel):
    task: str = Field(min_length=1, max_length=10000)

class Verification(BaseModel):
    name: str
    status: Literal["PASS","FAIL","WARN","NOT_APPLICABLE"]
    detail: str

class Evidence(BaseModel):
    id: str
    title: str
    text: str
    relevance: float
    supports: bool | None = None
    url: str = ""

class TaskResponse(BaseModel):
    decision: Literal["ACCEPT","REJECT","HOLD","CLARIFY"]
    answer: str
    confidence: float
    revision: int
    verifications: list[Verification]
    evidence: list[Evidence]
    audit: list[str]
    clarification: str | None = None
