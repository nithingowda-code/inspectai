from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text
from backend.app.database.session import Base

class ModelMetadata(Base):
    __tablename__ = "model_metadata"

    id = Column(String(50), primary_key=True, default="default_model")
    name = Column(String(255), nullable=False)
    architecture = Column(String(255), nullable=False)
    weights_info = Column(String(255), nullable=False)
    device = Column(String(50), nullable=False)
    embedding_dim = Column(Integer, default=512)
    reference_banks_count = Column(Integer, default=0)
    total_samples_indexed = Column(Integer, default=0)
    last_evaluated_at = Column(DateTime, nullable=True)
    evaluation_metrics_json = Column(Text, nullable=True, default="{}")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
