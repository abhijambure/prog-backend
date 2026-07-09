from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models import User, Career, College, Exam, Scholarship, SavedCareer
from app.schemas import CareerBriefResponse, CareerResponse, CollegeResponse, ExamResponse, ScholarshipResponse, SavedCareerToggle

router = APIRouter(tags=["directories"])

# --- Careers Directory ---
@router.get("/careers", response_model=List[CareerBriefResponse])
def get_careers(
    search: Optional[str] = None,
    category: Optional[str] = None,
    demand: Optional[str] = None,
    min_salary: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Career)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Career.name.like(search_term),
                Career.category.like(search_term),
                Career.overview.like(search_term),
                Career.eligibility.like(search_term)
            )
        )
        
    if category:
        query = query.filter(Career.category == category)
        
    if demand:
        query = query.filter(Career.demand == demand)
        
    results = query.all()
    
    # Filter by salary if specified
    if min_salary is not None:
        filtered = []
        for c in results:
            # salary_india is stored as JSON: {"min": int, "max": int, "average": int}
            avg_sal = c.salary_india.get("average", 0) if isinstance(c.salary_india, dict) else 0
            if avg_sal >= min_salary:
                filtered.append(c)
        return filtered
        
    return results

@router.get("/careers/{career_id}", response_model=CareerResponse)
def get_career_by_id(career_id: int, db: Session = Depends(get_db)):
    career = db.query(Career).filter(Career.id == career_id).first()
    if not career:
        raise HTTPException(status_code=404, detail="Career not found")
    return career

# --- Colleges Directory ---
@router.get("/colleges", response_model=List[CollegeResponse])
def get_colleges(
    search: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(College)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                College.name.like(search_term),
                College.admission_process.like(search_term)
            )
        )
    if city:
        query = query.filter(College.city == city)
    if state:
        query = query.filter(College.state == state)
    return query.all()

@router.get("/colleges/{college_id}", response_model=CollegeResponse)
def get_college_by_id(college_id: int, db: Session = Depends(get_db)):
    college = db.query(College).filter(College.id == college_id).first()
    if not college:
        raise HTTPException(status_code=404, detail="College not found")
    return college

# --- Entrance Examinations Directory ---
@router.get("/exams", response_model=List[ExamResponse])
def get_exams(
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Exam)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Exam.name.like(search_term),
                Exam.eligibility.like(search_term)
            )
        )
    return query.all()

@router.get("/exams/{exam_id}", response_model=ExamResponse)
def get_exam_by_id(exam_id: int, db: Session = Depends(get_db)):
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Examination not found")
    return exam

# --- Scholarships Directory ---
@router.get("/scholarships", response_model=List[ScholarshipResponse])
def get_scholarships(
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Scholarship)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Scholarship.name.like(search_term),
                Scholarship.eligibility.like(search_term)
            )
        )
    return query.all()

@router.get("/scholarships/{scholarship_id}", response_model=ScholarshipResponse)
def get_scholarship_by_id(scholarship_id: int, db: Session = Depends(get_db)):
    scholarship = db.query(Scholarship).filter(Scholarship.id == scholarship_id).first()
    if not scholarship:
        raise HTTPException(status_code=404, detail="Scholarship not found")
    return scholarship

# --- Saved Careers Toggle & List ---
@router.post("/careers/save")
def toggle_save_career(
    saved_in: SavedCareerToggle,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify career exists
    career = db.query(Career).filter(Career.id == saved_in.career_id).first()
    if not career:
        raise HTTPException(status_code=404, detail="Career not found")
        
    # Check if already saved
    existing = db.query(SavedCareer).filter(
        SavedCareer.user_id == current_user.id,
        SavedCareer.career_id == saved_in.career_id
    ).first()
    
    if existing:
        # Unsave
        db.delete(existing)
        db.commit()
        return {"saved": False, "message": "Career removed from saved list"}
    else:
        # Save
        new_saved = SavedCareer(
            user_id=current_user.id,
            career_id=saved_in.career_id
        )
        db.add(new_saved)
        db.commit()
        return {"saved": True, "message": "Career saved successfully"}

@router.get("/careers/saved/list", response_model=List[CareerBriefResponse])
def get_saved_careers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    saved_records = db.query(SavedCareer).filter(SavedCareer.user_id == current_user.id).all()
    return [record.career for record in saved_records]
