from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def seed_doc_types():
    db = SessionLocal()
    fixed_data = [
        {"id": 1, "name": "BRD",     "sort_id": 1},
        {"id": 2, "name": "UI/UX",   "sort_id": 3},
        {"id": 3, "name": "Anyname", "sort_id": 2},
    ]
    try:
        for item in fixed_data:
            existing = db.query(models.DocType).filter(models.DocType.id == item["id"]).first()
            if not existing:
                new_type = models.DocType(id=item["id"], name=item["name"], sort_id=item["sort_id"])
                db.add(new_type)
        db.commit()
    except Exception as e:
        print(f"Error seeding: {e}")
    finally:
        db.close()

seed_doc_types()

@app.get("/")
def read_root():
    return RedirectResponse(url="/docs")

class DocTypeResponse(BaseModel):
    id: int
    name: str
    sort_id: int
    class Config:
        from_attributes = True  

class DocumentInput(BaseModel):
    name_id: Optional[int] = None
    link1: Optional[str] = None
    link2: Optional[str] = None
    comment: Optional[str] = None
    created_by: Optional[str] = None
    approved_by: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name_id": "",
                "link1": "",
                "link2": "",
                "comment": "",
                "created_by": "",
                "approved_by": ""
            }
        }

class DocumentResponse(BaseModel):
    id: int
    name_id: int
    link1: Optional[str] = None
    link2: Optional[str] = None
    comment: Optional[str] = None
    created_by: str
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


@app.get("/doc-type/", response_model=List[DocTypeResponse])
def get_doc_types(db: Session = Depends(get_db)):
    return db.query(models.DocType).order_by(models.DocType.sort_id).all()

@app.post("/documents/", response_model=DocumentResponse)
def create_document(item: DocumentInput, db: Session = Depends(get_db)):
    if not db.query(models.DocType).filter(models.DocType.id == item.name_id).first():
        raise HTTPException(status_code=404, detail="DocType ID not found (Use 1, 2, or 3)")

    new_doc = models.Documents(
        name_id=item.name_id,
        link1=item.link1,
        link2=item.link2,
        comment=item.comment,
        created_by=item.created_by,
        approved_by=item.approved_by
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    return new_doc

@app.put("/documents/{doc_id}", response_model=DocumentResponse)
def update_document(doc_id: int, item: DocumentInput, db: Session = Depends(get_db)):
    db_doc = db.query(models.Documents).filter(models.Documents.id == doc_id).first()
    if not db_doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if not db.query(models.DocType).filter(models.DocType.id == item.name_id).first():
        raise HTTPException(status_code=404, detail="DocType ID not found")

    db_doc.name_id = item.name_id
    db_doc.link1 = item.link1
    db_doc.link2 = item.link2
    db_doc.comment = item.comment
    db_doc.created_by = item.created_by
    db_doc.approved_by = item.approved_by
    
    if item.approved_by:
        db_doc.approved_at = datetime.utcnow()

    db.commit()
    db.refresh(db_doc)
    return db_doc

@app.get("/documents/", response_model=List[DocumentResponse])
def get_documents(db: Session = Depends(get_db)):
    return db.query(models.Documents).all()

@app.get("/documents/{doc_id}", response_model=DocumentResponse)
def get_document_by_id(doc_id: int, db: Session = Depends(get_db)):
    document = db.query(models.Documents).filter(models.Documents.id == doc_id).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return document
