import os
import shutil
import tempfile

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from api.models import (
    AnswerRequest,
    AnswerResponse,
    InterviewCreateResponse,
    InterviewStartResponse,
    InterviewStatusResponse,
)
from api.service import InterviewService

app = FastAPI(
    title="AI Mock Interview API",
    version="1.0.0",
    description="FastAPI backend for the resume-driven AI mock interview system.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

service = InterviewService()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v1/interviews", response_model=InterviewCreateResponse)
async def create_interview(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF resumes are supported.")

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
            temp_path = temp.name
            shutil.copyfileobj(file.file, temp)

        session = service.create_session(temp_path, file.filename)
        return InterviewCreateResponse(
            interview_id=session.interview_id,
            filename=session.filename,
            topics=session.topics,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


@app.post("/api/v1/interviews/{interview_id}/start", response_model=InterviewStartResponse)
def start_interview(interview_id: str):
    try:
        topic, difficulty, question = service.start(interview_id)
        return InterviewStartResponse(
            interview_id=interview_id,
            topic=topic,
            difficulty=difficulty,
            question=question,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/v1/interviews/{interview_id}/answer", response_model=AnswerResponse)
def submit_answer(interview_id: str, payload: AnswerRequest):
    try:
        result = service.answer(
            interview_id=interview_id,
            question=payload.question,
            answer=payload.answer,
        )
        return AnswerResponse(interview_id=interview_id, **result)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/v1/interviews/{interview_id}", response_model=InterviewStatusResponse)
def interview_status(interview_id: str):
    try:
        session = service.get_session(interview_id)
        state = session.state
        return InterviewStatusResponse(
            interview_id=interview_id,
            current_topic=state.current_topic,
            difficulty=state.current_difficulty,
            question_number=state.question_number,
            covered_topics=state.covered_topics,
            asked_questions=state.asked_questions,
            evaluation_history=state.evaluation_history,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
