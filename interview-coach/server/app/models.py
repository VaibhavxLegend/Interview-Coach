from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column
from pgvector.sqlalchemy import Vector
from .database import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    sessions: Mapped[list["InterviewSession"]] = relationship("InterviewSession", back_populates="user")


class InterviewSession(Base):
    __tablename__ = "interview_sessions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    role: Mapped[str] = mapped_column(String(100), default="general")
    seniority: Mapped[str] = mapped_column(String(50), default="mid")
    status: Mapped[str] = mapped_column(String(20), default="active")  # active|completed
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    user: Mapped[User | None] = relationship("User", back_populates="sessions")
    answers: Mapped[list["Answer"]] = relationship("Answer", back_populates="session")


class Answer(Base):
    __tablename__ = "answers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("interview_sessions.id"))
    question: Mapped[str] = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text)  # user response
    transcript: Mapped[str | None] = mapped_column(Text, nullable=True)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1536), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    session: Mapped[InterviewSession] = relationship("InterviewSession", back_populates="answers")
    evaluation: Mapped["Evaluation" | None] = relationship("Evaluation", back_populates="answer", uselist=False)

    __table_args__ = (
        Index("ix_answers_session_created", "session_id", "created_at"),
    )


class Evaluation(Base):
    __tablename__ = "evaluations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    answer_id: Mapped[int] = mapped_column(ForeignKey("answers.id"), unique=True)
    clarity: Mapped[float] = mapped_column(Float)
    conciseness: Mapped[float] = mapped_column(Float)
    confidence: Mapped[float] = mapped_column(Float)
    technical_depth: Mapped[float] = mapped_column(Float)
    overall: Mapped[float] = mapped_column(Float)
    feedback: Mapped[str] = mapped_column(Text)
    suggestions: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    answer: Mapped[Answer] = relationship("Answer", back_populates="evaluation")


class QuestionCache(Base):
    __tablename__ = "question_cache"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    role: Mapped[str] = mapped_column(String(100), index=True)
    seniority: Mapped[str] = mapped_column(String(50), index=True)
    question: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class IdealAnswer(Base):
    __tablename__ = "ideal_answers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    role: Mapped[str] = mapped_column(String(100), index=True)
    seniority: Mapped[str] = mapped_column(String(50), index=True)
    answer: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1536), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
