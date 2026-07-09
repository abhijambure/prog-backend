from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, timedelta
from app.core.database import get_db
from app.api.deps import get_current_admin
from app.models import User, StudentProfile, Career, College, Exam, Scholarship, SavedCareer, CareerRecommendation
from app.schemas import AdminAnalyticsResponse, CareerCreate, CareerResponse, CollegeCreate, CollegeResponse, ExamCreate, ExamResponse, ScholarshipCreate, ScholarshipResponse

router = APIRouter(prefix="/admin", tags=["administration"])

# --- Dashboard Analytics ---
@router.get("/analytics", response_model=AdminAnalyticsResponse)
def get_analytics(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    # Core counts
    total_students = db.query(User).filter(User.role == "student").count()
    completed_assessments = db.query(StudentProfile).filter(StudentProfile.completed_assessment == True).count()
    total_careers = db.query(Career).count()
    total_colleges = db.query(College).count()
    
    # Simple card metrics
    cards = [
        {"label": "Total Enrolled Students", "value": total_students, "change": 12.5},
        {"label": "Assessments Completed", "value": completed_assessments, "change": 8.2},
        {"label": "Careers in Directory", "value": total_careers, "change": 0.0},
        {"label": "Affiliated Colleges", "value": total_colleges, "change": 4.1}
    ]
    
    # Registrations over time (last 7 days helper)
    registrations = []
    today = datetime.utcnow().date()
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        next_day = day + timedelta(days=1)
        
        count = db.query(User).filter(
            User.created_at >= datetime.combine(day, datetime.min.time()),
            User.created_at < datetime.combine(next_day, datetime.min.time()),
            User.role == "student"
        ).count()
        
        registrations.append({
            "date": day.strftime("%b %d"),
            "students": count
        })
        
    # Popular Careers (count how many students got recommended or saved them)
    # We will look at SavedCareer table counts
    saved_stats = db.query(
        Career.name,
        func.count(SavedCareer.id).label("count")
    ).join(SavedCareer, SavedCareer.career_id == Career.id).group_by(Career.name).order_by(func.count(SavedCareer.id).desc()).limit(5).all()
    
    popular_careers = [{"name": name, "count": count} for name, count in saved_stats]
    # Fill in defaults if empty
    if not popular_careers:
        popular_careers = [
            {"name": "AI/ML Engineer", "count": 12},
            {"name": "Software Engineer", "count": 9},
            {"name": "Chartered Accountant", "count": 7},
            {"name": "Doctor", "count": 6},
            {"name": "UI/UX Designer", "count": 5}
        ]
        
    # Popular Subjects (aggregate from student profile lists)
    profiles = db.query(StudentProfile).all()
    subject_counts = {}
    interest_counts = {}
    
    for p in profiles:
        if p.favorite_subjects:
            for sub in p.favorite_subjects:
                subject_counts[sub] = subject_counts.get(sub, 0) + 1
        if p.interests:
            for interest in p.interests:
                interest_counts[interest] = interest_counts.get(interest, 0) + 1
                
    popular_subjects = sorted(
        [{"name": k.capitalize(), "count": v} for k, v in subject_counts.items()],
        key=lambda x: x["count"],
        reverse=True
    )[:5]
    if not popular_subjects:
        popular_subjects = [
            {"name": "Mathematics", "count": 15},
            {"name": "Physics", "count": 10},
            {"name": "Biology", "count": 8},
            {"name": "Computer Science", "count": 12},
            {"name": "Economics", "count": 6}
        ]
        
    popular_interests = sorted(
        [{"name": k.capitalize(), "count": v} for k, v in interest_counts.items()],
        key=lambda x: x["count"],
        reverse=True
    )[:5]
    if not popular_interests:
        popular_interests = [
            {"name": "Coding", "count": 18},
            {"name": "Designing", "count": 9},
            {"name": "Healthcare", "count": 7},
            {"name": "Solving Puzzles", "count": 11},
            {"name": "Writing", "count": 5}
        ]
        
    rate = (completed_assessments / total_students * 100) if total_students > 0 else 0.0
    
    return {
        "cards": cards,
        "registrations_over_time": registrations,
        "popular_careers": popular_careers,
        "popular_subjects": popular_subjects,
        "popular_interests": popular_interests,
        "assessment_completion_rate": round(rate, 1)
    }

# --- Careers CRUD ---
@router.post("/careers", response_model=CareerResponse)
def create_career(
    career_in: CareerCreate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    existing = db.query(Career).filter(Career.name == career_in.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Career name already exists")
    db_career = Career(**career_in.model_dump())
    db.add(db_career)
    db.commit()
    db.refresh(db_career)
    return db_career

@router.put("/careers/{career_id}", response_model=CareerResponse)
def update_career(
    career_id: int,
    career_in: CareerCreate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    db_career = db.query(Career).filter(Career.id == career_id).first()
    if not db_career:
        raise HTTPException(status_code=404, detail="Career not found")
    for k, v in career_in.model_dump().items():
        setattr(db_career, k, v)
    db.commit()
    db.refresh(db_career)
    return db_career

@router.delete("/careers/{career_id}")
def delete_career(
    career_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    db_career = db.query(Career).filter(Career.id == career_id).first()
    if not db_career:
        raise HTTPException(status_code=404, detail="Career not found")
    db.delete(db_career)
    db.commit()
    return {"message": "Career deleted successfully"}

# --- Colleges CRUD ---
@router.post("/colleges", response_model=CollegeResponse)
def create_college(
    college_in: CollegeCreate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    existing = db.query(College).filter(College.name == college_in.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="College name already exists")
    db_college = College(**college_in.model_dump())
    db.add(db_college)
    db.commit()
    db.refresh(db_college)
    return db_college

@router.put("/colleges/{college_id}", response_model=CollegeResponse)
def update_college(
    college_id: int,
    college_in: CollegeCreate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    db_college = db.query(College).filter(College.id == college_id).first()
    if not db_college:
        raise HTTPException(status_code=404, detail="College not found")
    for k, v in college_in.model_dump().items():
        setattr(db_college, k, v)
    db.commit()
    db.refresh(db_college)
    return db_college

@router.delete("/colleges/{college_id}")
def delete_college(
    college_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    db_college = db.query(College).filter(College.id == college_id).first()
    if not db_college:
        raise HTTPException(status_code=404, detail="College not found")
    db.delete(db_college)
    db.commit()
    return {"message": "College deleted successfully"}

# --- Exams CRUD ---
@router.post("/exams", response_model=ExamResponse)
def create_exam(
    exam_in: ExamCreate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    existing = db.query(Exam).filter(Exam.name == exam_in.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Exam name already exists")
    db_exam = Exam(**exam_in.model_dump())
    db.add(db_exam)
    db.commit()
    db.refresh(db_exam)
    return db_exam

@router.put("/exams/{exam_id}", response_model=ExamResponse)
def update_exam(
    exam_id: int,
    exam_in: ExamCreate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    db_exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not db_exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    for k, v in exam_in.model_dump().items():
        setattr(db_exam, k, v)
    db.commit()
    db.refresh(db_exam)
    return db_exam

@router.delete("/exams/{exam_id}")
def delete_exam(
    exam_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    db_exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not db_exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    db.delete(db_exam)
    db.commit()
    return {"message": "Exam deleted successfully"}

# --- Scholarships CRUD ---
@router.post("/scholarships", response_model=ScholarshipResponse)
def create_scholarship(
    scholarship_in: ScholarshipCreate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    existing = db.query(Scholarship).filter(Scholarship.name == scholarship_in.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Scholarship name already exists")
    db_scholarship = Scholarship(**scholarship_in.model_dump())
    db.add(db_scholarship)
    db.commit()
    db.refresh(db_scholarship)
    return db_scholarship

@router.put("/scholarships/{scholarship_id}", response_model=ScholarshipResponse)
def update_scholarship(
    scholarship_id: int,
    scholarship_in: ScholarshipCreate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    db_scholarship = db.query(Scholarship).filter(Scholarship.id == scholarship_id).first()
    if not db_scholarship:
        raise HTTPException(status_code=404, detail="Scholarship not found")
    for k, v in scholarship_in.model_dump().items():
        setattr(db_scholarship, k, v)
    db.commit()
    db.refresh(db_scholarship)
    return db_scholarship

@router.delete("/scholarships/{scholarship_id}")
def delete_scholarship(
    scholarship_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    db_scholarship = db.query(Scholarship).filter(Scholarship.id == scholarship_id).first()
    if not db_scholarship:
        raise HTTPException(status_code=404, detail="Scholarship not found")
    db.delete(db_scholarship)
    db.commit()
    return {"message": "Scholarship deleted successfully"}
