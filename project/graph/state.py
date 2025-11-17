from typing import TypedDict, Optional, Annotated
import operator

class SupportState(TypedDict):
    messages: Annotated[list[dict], operator.add]
    calls: int