"""Preprint Latex Models (Phase 124)."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database.connection import Base
from database.models.memory import GUID

class DBPreprintManuscript(Base):
    __tablename__ = "preprint_manuscripts"
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(GUID(), nullable=False, index=True)
    manuscript_title = Column(String(255), nullable=False)
    journal_target_format = Column(String(100), default="Nature Biotechnology / bioRxiv", nullable=False)
    total_words = Column(Integer, default=4500, nullable=False)
    compilation_status = Column(String(50), default="COMPILED_SUCCESS", nullable=False)
    latex_source_code = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    citations = relationship("DBCitationGraphNode", back_populates="manuscript", cascade="all, delete-orphan")

class DBCitationGraphNode(Base):
    __tablename__ = "preprint_citations"
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    manuscript_id = Column(GUID(), ForeignKey("preprint_manuscripts.id", ondelete="CASCADE"), nullable=False, index=True)
    citation_key = Column(String(100), nullable=False)
    doi_or_pmid = Column(String(100), nullable=False)
    bibtex_entry = Column(Text, nullable=False)
    verified_valid = Column(Float, default=1.0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    manuscript = relationship("DBPreprintManuscript", back_populates="citations")
