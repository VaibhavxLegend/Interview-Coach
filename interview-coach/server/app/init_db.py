import asyncio
from .database import engine, Base, SessionLocal
from .models import IdealAnswer
from .embeddings import embed_text


async def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Seed a couple of ideal answers if none exist
        count = db.query(IdealAnswer).count()
        if count == 0:
            examples = [
                ("software engineer", "mid", "Structure answers with STAR, quantify impact, and explain trade-offs succinctly."),
                ("software engineer", "senior", "Demonstrate system design thinking, clear assumptions, and measurable outcomes.")
            ]
            for role, seniority, text in examples:
                emb = await embed_text(text)
                db.add(IdealAnswer(role=role, seniority=seniority, answer=text, embedding=emb))
            db.commit()
    finally:
        db.close()


def init():
    asyncio.run(seed())


if __name__ == "__main__":
    init()
