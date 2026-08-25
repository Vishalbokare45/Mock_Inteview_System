from typing import Any
from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    user_id: str
    email: str
    access_token: str
    token_type: str = "bearer"


class ResumeResponse(BaseModel):
    resume_id: str
    filename: str
    topics: list[str]


class StartResponse(BaseModel):
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
    next_topic: str | None = None
    next_difficulty: str | None = None
    next_question: str | None = None
    completed: bool = False
