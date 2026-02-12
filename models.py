from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class DocType(Base):
    __tablename__ = "doc_type"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    sort_id = Column(Integer)

    documents = relationship("Documents", back_populates="doc_type")

class Documents(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    name_id = Column(Integer, ForeignKey("doc_type.id"))

    link1 = Column(String)
    link2 = Column(String)
    comment = Column(String)

    created_by = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    approved_by = Column(String)
    approved_at = Column(DateTime)

    created_time = Column(DateTime, default=datetime.utcnow)
    updated_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    doc_type = relationship("DocType", back_populates="documents")