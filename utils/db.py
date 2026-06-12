from sqlalchemy import create_engine, Column, Integer, String, LargeBinary, Text
from sqlalchemy.orm import DeclarativeBase, Session
import streamlit as st

DATABASE_URL = "sqlite:///kpss_questions.db"

class Base(DeclarativeBase):
    pass

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    subject = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    image = Column(LargeBinary, nullable=True)          # fotoğraf BLOB olarak
    raw_text = Column(Text, nullable=True)              # OCR ham metin
    question_text = Column(Text, nullable=True)         # düzeltilmiş soru kökü
    option_a = Column(Text, nullable=True)
    option_b = Column(Text, nullable=True)
    option_c = Column(Text, nullable=True)
    option_d = Column(Text, nullable=True)
    option_e = Column(Text, nullable=True)
    correct_answer = Column(String, nullable=True)      # 'A','B','C','D','E'

@st.cache_resource
def get_engine():
    engine = create_engine(DATABASE_URL, echo=False)
    Base.metadata.create_all(engine)
    return engine

def get_session():
    engine = get_engine()
    return Session(engine)

def add_question(subject, year, image_bytes, raw_text, parsed):
    session = get_session()
    q = Question(
        subject=subject,
        year=year,
        image=image_bytes,
        raw_text=raw_text,
        question_text=parsed.get("question", ""),
        option_a=parsed.get("A", ""),
        option_b=parsed.get("B", ""),
        option_c=parsed.get("C", ""),
        option_d=parsed.get("D", ""),
        option_e=parsed.get("E", ""),
        correct_answer=None   # başlangıçta boş
    )
    session.add(q)
    session.commit()
    session.close()

def update_question(question_id, **kwargs):
    session = get_session()
    q = session.query(Question).filter_by(id=question_id).first()
    if q:
        for key, value in kwargs.items():
            setattr(q, key, value)
        session.commit()
    session.close()

def get_all_questions(subject=None, year=None):
    session = get_session()
    query = session.query(Question)
    if subject:
        query = query.filter_by(subject=subject)
    if year:
        query = query.filter_by(year=year)
    results = query.all()
    session.close()
    return results

def delete_all():
    session = get_session()
    session.query(Question).delete()
    session.commit()
    session.close()
