import os
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db, DATA_DIR
from backend.app.models.product import Product, ProductReference
from backend.app.schemas.product import ProductCreate, ProductUpdate, ProductOut, ProductReferenceOut
from backend.app.ml.reference_bank import ProductReferenceBank

router = APIRouter(prefix="/products", tags=["Products"])

def format_product_out(p: Product) -> ProductOut:
    return ProductOut(
        id=p.id,
        name=p.name,
        category=p.category,
        description=p.description,
        expected_length=p.expected_length,
        expected_width=p.expected_width,
        expected_thickness=p.expected_thickness,
        unit=p.unit,
        pos_tolerance=p.pos_tolerance,
        neg_tolerance=p.neg_tolerance,
        calibration_factor=p.calibration_factor,
        created_at=p.created_at,
        updated_at=p.updated_at,
        references=[ProductReferenceOut.model_validate(r) for r in p.references],
        inspections_count=len(p.inspections) if p.inspections else 0
    )

@router.get("", response_model=List[ProductOut])
def list_products(db: Session = Depends(get_db)):
    products = db.query(Product).order_by(Product.created_at.desc()).all()
    return [format_product_out(p) for p in products]

@router.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    product = Product(
        name=payload.name,
        category=payload.category,
        description=payload.description,
        expected_length=payload.expected_length,
        expected_width=payload.expected_width,
        expected_thickness=payload.expected_thickness,
        unit=payload.unit,
        pos_tolerance=payload.pos_tolerance,
        neg_tolerance=payload.neg_tolerance,
        calibration_factor=payload.calibration_factor
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return format_product_out(product)

@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: str, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    return format_product_out(p)

@router.put("/{product_id}", response_model=ProductOut)
def update_product(product_id: str, payload: ProductUpdate, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        if val is not None:
            setattr(p, field, val)

    db.commit()
    db.refresh(p)
    return format_product_out(p)

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: str, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")

    # Clean up reference files
    for ref in p.references:
        if os.path.exists(ref.file_path):
            try:
                os.remove(ref.file_path)
            except OSError:
                pass

    db.delete(p)
    db.commit()
    return None

@router.post("/{product_id}/references", response_model=ProductReferenceOut)
async def upload_reference_image(
    product_id: str,
    file: UploadFile = File(...),
    is_primary: bool = Form(False),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/webp", "image/bmp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid image file format. Supported: JPEG, PNG, WEBP, BMP")

    ref_dir = os.path.join(DATA_DIR, "references", product_id)
    os.makedirs(ref_dir, exist_ok=True)

    ext = os.path.splitext(file.filename or "")[1] or ".jpg"
    safe_filename = f"ref_{uuid.uuid4().hex[:12]}{ext}"
    dest_path = os.path.join(ref_dir, safe_filename)

    contents = await file.read()
    with open(dest_path, "wb") as f:
        f.write(contents)

    ref = ProductReference(
        product_id=product_id,
        file_path=dest_path,
        filename=file.filename or safe_filename,
        is_primary=is_primary or (len(product.references) == 0)
    )
    db.add(ref)
    db.commit()
    db.refresh(ref)

    # Immediately update the product's visual feature bank
    all_refs = db.query(ProductReference).filter(ProductReference.product_id == product_id).all()
    all_paths = [r.file_path for r in all_refs if os.path.exists(r.file_path)]
    bank = ProductReferenceBank(product_id)
    bank.build_or_update(all_paths)

    return ProductReferenceOut.model_validate(ref)

@router.delete("/{product_id}/references/{ref_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reference_image(product_id: str, ref_id: str, db: Session = Depends(get_db)):
    ref = db.query(ProductReference).filter(
        ProductReference.id == ref_id,
        ProductReference.product_id == product_id
    ).first()
    if not ref:
        raise HTTPException(status_code=404, detail="Reference image not found")

    if os.path.exists(ref.file_path):
        try:
            os.remove(ref.file_path)
        except OSError:
            pass

    db.delete(ref)
    db.commit()

    # Rebuild reference bank with remaining references
    remaining_refs = db.query(ProductReference).filter(ProductReference.product_id == product_id).all()
    all_paths = [r.file_path for r in remaining_refs if os.path.exists(r.file_path)]
    bank = ProductReferenceBank(product_id)
    bank.build_or_update(all_paths)

    return None
