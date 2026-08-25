import os
import shutil
import tempfile
from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from api.auth import create_token, get_current_user, hash_password, verify_password
from api.database import Database
from api.schemas import (
    AnswerRequest,
    AnswerResponse,
    AuthResponse,
    LoginRequest,
    RegisterRequest,
    ResumeResponse,
    StartResponse,
)
from api.service import InterviewService

app = FastAPI(
    title="AI Mock Interview API",
    version="2.0.0",
    description="Authenticated FastAPI backend for the resume-driven AI mock interview system.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

service = InterviewService()


def db() -> Database:
    return Database()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/v1/auth/register", response_model=AuthResponse)
def register(payload: RegisterRequest, database: Database = Depends(db)):
    if database.get_user_by_email(payload.email):
        raise HTTPException(status_code=409, detail="Email already registered")

    user = database.create_user(payload.email, hash_password(payload.password))
    return AuthResponse(
        user_id=user["id"],
        email=user["email"],
        access_token=create_token(user["id"]),
    )


@app.post("/api/v1/auth/login", response_model=AuthResponse)
def login(payload: LoginRequest, database: Database = Depends(db)):
    user = database.get_user_by_email(payload.email)
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return AuthResponse(
        user_id=user["id"],
        email=user["email"],
        access_token=create_token(user["id"]),
    )


@app.post("/api/v1/resumes", response_model=ResumeResponse)
async def upload_resume(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
    database: Database = Depends(db),
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF resumes are supported.")

    resume_dir = Path(os.getenv("RESUME_STORAGE", "data/resumes")) / user["id"]
    resume_dir.mkdir(parents=True, exist_ok=True)
    resume_id = None
    final_path = resume_dir / file.filename

    try:
        with final_path.open("wb") as output:
            shutil.copyfileobj(file.file, output)

        # Run the complete resume/RAG preparation pipeline now.
        # Start Interview only performs the interactive interview stage.
        session = service.create_session(
            str(final_path),
            file.filename,
            user["id"],
        )
        resume_id = database.create_resume(user["id"], file.filename, str(final_path))

        # Replace the generated session id with a database-backed interview id.
        database.create_interview(user["id"], resume_id)

        return ResumeResponse(
            resume_id=resume_id,
            filename=file.filename,
            topics=session.topics,
        )
    except Exception as exc:
        if final_path.exists():
            final_path.unlink()
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/v1/interviews/{interview_id}/start", response_model=StartResponse)
def start_interview(
    interview_id: str,
    user: dict = Depends(get_current_user),
):
    try:
        topic, difficulty, question = service.start(interview_id, user["id"])
        return StartResponse(
            interview_id=interview_id,
            topic=topic,
            difficulty=difficulty,
            question=question,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/v1/interviews/{interview_id}/answer", response_model=AnswerResponse)
def submit_answer(
    interview_id: str,
    payload: AnswerRequest,
    user: dict = Depends(get_current_user),
):
    try:
        result = service.answer(
            interview_id,
            user["id"],
            payload.question,
            payload.answer,
        )
        return AnswerResponse(interview_id=interview_id, **result)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
