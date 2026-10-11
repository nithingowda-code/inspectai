import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from backend.app.database.session import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Expected Dimensions
    expected_length = Column(Float, nullable=False, default=100.0)
    expected_width = Column(Float, nullable=False, default=50.0)
    expected_thickness = Column(Float, nullable=True)
    unit = Column(String(20), nullable=False, default="mm")
    
    # Tolerances
    pos_tolerance = Column(Float, nullable=False, default=2.0)
    neg_tolerance = Column(Float, nullable=False, default=2.0)
    
    # Calibration (pixels per physical unit)
    calibration_factor = Column(Float, nullable=False, default=10.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    references = relationship("ProductReference", back_populates="product", cascade="all, delete-orphan")
    inspections = relationship("InspectionRecord", back_populates="product", cascade="all, delete-orphan")

class ProductReference(Base):
    __tablename__ = "product_references"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    file_path = Column(String(512), nullable=False)
    filename = Column(String(255), nullable=False)
    is_primary = Column(Boolean, default=False)
    embedding_path = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="references")
