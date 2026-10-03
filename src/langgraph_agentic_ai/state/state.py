from typing import Annotated
from typing_extensions import TypedDict, List

from langgraph.graph.message import add_messages


class State(TypedDict):
    """
    Represents the structure of the state used in the graph.
    """

    messages: Annotated[List, add_messages]

    frequency: str
    news_data: list
    summary: str
    filename: str