from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models import User, StudentProfile, CareerRecommendation, SavedCareer, Exam
from app.schemas import StudentProfileResponse, StudentProfileUpdate
from datetime import datetime

router = APIRouter(prefix="/student", tags=["student"])

@router.get("/profile", response_model=StudentProfileResponse)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Student profile not found")
    return profile

@router.put("/profile", response_model=StudentProfileResponse)
def update_profile(
    profile_in: StudentProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Student profile not found")
        
    update_data = profile_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
        
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile

@router.get("/dashboard-widgets")
def get_dashboard_widgets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Student profile not found")
        
    # Count recommendations
    recs_count = db.query(CareerRecommendation).filter(CareerRecommendation.user_id == current_user.id).count()
    
    # Get top 3 recommendations
    top_recs = db.query(CareerRecommendation).filter(
        CareerRecommendation.user_id == current_user.id
    ).order_by(CareerRecommendation.score.desc()).limit(3).all()
    
    # Get saved careers count
    saved_count = db.query(SavedCareer).filter(SavedCareer.user_id == current_user.id).count()
    
    # Calculate profile completion percentage
    fields = [
        profile.class_name, profile.academic_board, profile.city, 
        profile.state, profile.percentage, profile.preferred_stream,
        profile.favorite_subjects, profile.interests, profile.skills, 
        profile.personality_type
    ]
    filled_fields = sum(1 for f in fields if f is not None and (type(f) != list or len(f) > 0))
    completion_rate = round((filled_fields / len(fields)) * 100)
    
    # Fetch upcoming exams
    exams = db.query(Exam).all()
    exam_alerts = []
    for exam in exams:
        # Check dates
        dates = exam.important_dates # Dict
        for event, date_str in dates.items():
            if "last date" in event.lower() or "exam date" in event.lower() or "registration" in event.lower():
                exam_alerts.append({
                    "exam_name": exam.name,
                    "event": event,
                    "date": date_str,
                    "registration_link": exam.registration_link
                })
                
    # Activities list
    activities = []
    if profile.completed_assessment:
        activities.append({
            "action": "Career assessment completed",
            "time": "Recent"
        })
    if saved_count > 0:
        activities.append({
            "action": f"Saved {saved_count} careers of interest",
            "time": "Recent"
        })
    if completion_rate > 50:
        activities.append({
            "action": "Profile detail settings updated",
            "time": "Recent"
        })
    else:
        activities.append({
            "action": "Setup profile details to improve matchmaking accuracy",
            "time": "Action Required"
        })

    return {
        "profile_completion": completion_rate,
        "completed_assessment": profile.completed_assessment,
        "recommendations_count": recs_count,
        "top_recommendations": [
            {
                "id": r.career.id,
                "name": r.career.name,
                "score": r.score,
                "category": r.career.category
            } for r in top_recs
        ],
        "saved_count": saved_count,
        "exam_alerts": exam_alerts[:4], # top 4 alerts
        "recent_activities": activities
    }
