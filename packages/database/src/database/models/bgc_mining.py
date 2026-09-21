"""BGC Models (Phase 123)."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database.connection import Base
from database.models.memory import GUID

class DBMicrobialBGCGenome(Base):
    __tablename__ = "bgc_genomes"
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(GUID(), nullable=False, index=True)
    organism_species_name = Column(String(100), nullable=False)
    genome_size_mbp = Column(Float, default=8.66, nullable=False)
    total_detected_bgcs = Column(Integer, default=26, nullable=False)
    novel_scaffold_fraction = Column(Float, default=0.42, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    clusters = relationship("DBBiosyntheticClusterCluster", back_populates="genome", cascade="all, delete-orphan")

class DBBiosyntheticClusterCluster(Base):
    __tablename__ = "bgc_clusters"
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    genome_id = Column(GUID(), ForeignKey("bgc_genomes.id", ondelete="CASCADE"), nullable=False, index=True)
    bgc_type = Column(String(100), nullable=False)
    core_synthetase_genes = Column(String(100), nullable=False)
    predicted_chemical_class = Column(String(100), nullable=False)
    mibiig_known_homology_pct = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    genome = relationship("DBMicrobialBGCGenome", back_populates="clusters")
