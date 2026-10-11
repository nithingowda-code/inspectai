from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class ProductReferenceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    file_path: str
    filename: str
    is_primary: bool
    created_at: datetime

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    category: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    expected_length: float = Field(..., gt=0)
    expected_width: float = Field(..., gt=0)
    expected_thickness: Optional[float] = Field(None, gt=0)
    unit: str = Field(default="mm", max_length=20)
    pos_tolerance: float = Field(..., ge=0)
    neg_tolerance: float = Field(..., ge=0)
    calibration_factor: float = Field(default=10.0, gt=0)

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    expected_length: Optional[float] = Field(None, gt=0)
    expected_width: Optional[float] = Field(None, gt=0)
    expected_thickness: Optional[float] = Field(None, gt=0)
    unit: Optional[str] = None
    pos_tolerance: Optional[float] = Field(None, ge=0)
    neg_tolerance: Optional[float] = Field(None, ge=0)
    calibration_factor: Optional[float] = Field(None, gt=0)

class ProductOut(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime
    references: List[ProductReferenceOut] = []
    inspections_count: int = 0
