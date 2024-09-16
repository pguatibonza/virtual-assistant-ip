from langchain_core.pydantic_v1 import BaseModel, Field

class CompleteOrEscalate(BaseModel):
    """A tool to mark the current task as completed and/or to escalate control of the dialog to the main assistant,
    who can re-route the dialog based on the student's needs."""

    cancel: bool =True
    reason: str

class toConceptualAssistant(BaseModel):
    """
    Transfers work to a specialized assistant  to handle any conceptual doubts/inquiries about the programming course. The doubts must be about programming
    """
    request: str=Field(description="Any necessary follow-up questions the conceptual assistant  should clarify  before proceeding. The questions must be about programming. ")

class toFeedbackAssistant(BaseModel):
    """
    Transfers work to a specialized assistant to give detailed feedback about a code problem
    """
    code : str=Field(description="The code block which the student wants to get feedback from")
    name : str=Field(description= "The name of the coding problem which the student wants to get feedback from")

def get_insights():
    