from typing import Any, Optional

from pydantic import BaseModel, Field


class InterviewCreateResponse(BaseModel):
    interview_id: str
    filename: str
    topics: list[str]


class InterviewStartResponse(BaseModel):
    interview_id: str
    topic: str
    difficulty: str
    question: str


class AnswerRequest(BaseModel):
    question: str = Field(min_length=1)
    answer: str = Field(min_length=1)


class AnswerResponse(BaseModel):
    interview_id: str
    evaluation: dict[str, Any]
    next_topic: Optional[str] = None
    next_difficulty: Optional[str] = None
    next_question: Optional[str] = None
    completed: bool = False


class InterviewStatusResponse(BaseModel):
    interview_id: str
    current_topic: str
    difficulty: str
    question_number: int
    covered_topics: list[str]
    asked_questions: list[str]
    evaluation_history: list[dict[str, Any]]
