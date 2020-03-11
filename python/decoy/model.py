from dataclasses import dataclass, field
from typing import List


@dataclass
class Function:
    FunctionName: str
    FunctionArn: str
    Runtime: str
    Role: str
    Handler: str
    CodeSize: int
    Description: str
    Timeout: int
    MemorySize: float
    LastModified: str
    CodeSha256: str
    Version: str
    TracingConfig: dict
    RevisionId: str
    Environment: str = ""
    Layers: list = field(default_factory=list)


@dataclass
class ResponseMetadata:
    RequestId: str
    HTTPStatusCode: int
    HTTPHeaders: dict


@dataclass
class LambdaList:
    ResponseMetadata: ResponseMetadata
    Functions: List[Function]

    def __post_init__(self):
        self.Functions = [Function(**i) for i in self.Functions]  # noqa
