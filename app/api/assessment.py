from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models import User, AssessmentQuestion, AssessmentResponse, CareerRecommendation
from app.schemas import AssessmentQuestionResponse, AssessmentResponseSubmit, CareerRecommendationResponse
from app.services.recommendation import save_and_get_recommendations

router = APIRouter(prefix="/assessment", tags=["assessment"])

@router.get("/questions", response_model=List[AssessmentQuestionResponse])
def get_questions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    questions = db.query(AssessmentQuestion).all()
    return questions

@router.post("/submit", response_model=List[CareerRecommendationResponse])
def submit_assessment(
    submit_in: AssessmentResponseSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify answers is not empty
    if not submit_in.responses:
        raise HTTPException(status_code=400, detail="Responses cannot be empty")
        
    # Save the raw responses
    # Convert keys to integer to check validity
    cleaned_responses = {}
    for q_id_str, opt_idx in submit_in.responses.items():
        try:
            q_id = int(q_id_str)
            cleaned_responses[str(q_id)] = opt_idx
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid question ID format")
            
    # Store or update in DB
    existing_resp = db.query(AssessmentResponse).filter(AssessmentResponse.user_id == current_user.id).first()
    if existing_resp:
        existing_resp.response_data = cleaned_responses
        db.add(existing_resp)
    else:
        new_resp = AssessmentResponse(
            user_id=current_user.id,
            response_data=cleaned_responses
        )
        db.add(new_resp)
        
    db.commit()
    
    # Calculate and store recommendations using recommendation engine service
    recommendations = save_and_get_recommendations(db, current_user.id)
    
    # Format and return the top recommendations
    # Filter the computed list which is sorted by score
    top_recommendations = db.query(CareerRecommendation).filter(
        CareerRecommendation.user_id == current_user.id
    ).order_by(CareerRecommendation.score.desc()).all()
    
    return top_recommendations
    
@router.get("/results", response_model=List[CareerRecommendationResponse])
def get_results(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    recommendations = db.query(CareerRecommendation).filter(
        CareerRecommendation.user_id == current_user.id
    ).order_by(CareerRecommendation.score.desc()).all()
    
    if not recommendations:
        raise HTTPException(status_code=404, detail="No assessment results found for this user. Please take the assessment first.")
        
    return recommendations
