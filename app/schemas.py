from pydantic import BaseModel, EmailStr, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    role: str

class TokenData(BaseModel):
    user_id: Optional[int] = None
    role: Optional[str] = None

# User Schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str = "student" # "student", "admin"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Student Profile Schemas
class StudentProfileCreate(BaseModel):
    full_name: str
    class_name: Optional[str] = None
    academic_board: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    percentage: Optional[float] = None
    preferred_stream: Optional[str] = None
    favorite_subjects: List[str] = []
    interests: List[str] = []
    skills: List[str] = []
    personality_type: Optional[str] = None
    hobbies: List[str] = []
    career_goals: List[str] = []

class StudentProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    class_name: Optional[str] = None
    academic_board: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    percentage: Optional[float] = None
    preferred_stream: Optional[str] = None
    favorite_subjects: Optional[List[str]] = None
    interests: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    personality_type: Optional[str] = None
    hobbies: Optional[List[str]] = None
    career_goals: Optional[List[str]] = None

class StudentProfileResponse(BaseModel):
    id: int
    user_id: int
    full_name: str
    class_name: Optional[str] = None
    academic_board: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    percentage: Optional[float] = None
    preferred_stream: Optional[str] = None
    favorite_subjects: Optional[List[str]] = []
    interests: Optional[List[str]] = []
    skills: Optional[List[str]] = []
    personality_type: Optional[str] = None
    hobbies: Optional[List[str]] = []
    career_goals: Optional[List[str]] = []
    completed_assessment: bool

    class Config:
        from_attributes = True

# College Brief & Detail
class CollegeBrief(BaseModel):
    id: int
    name: str
    city: str
    state: str
    ranking: Optional[int] = None
    website: Optional[str] = None
    
    class Config:
        from_attributes = True

class CollegeCreate(BaseModel):
    name: str
    city: str
    state: str
    ranking: Optional[int] = None
    website: Optional[str] = None
    programs: List[str] = []
    admission_process: Optional[str] = None

class CollegeResponse(CollegeCreate):
    id: int
    
    class Config:
        from_attributes = True

# Exam Brief & Detail
class ExamBrief(BaseModel):
    id: int
    name: str
    important_dates: Dict[str, str] = {}
    website: Optional[str] = None
    
    class Config:
        from_attributes = True

class ExamCreate(BaseModel):
    name: str
    eligibility: str
    syllabus: List[str] = []
    exam_pattern: str
    important_dates: Dict[str, str] = {}
    registration_link: Optional[str] = None
    website: Optional[str] = None

class ExamResponse(ExamCreate):
    id: int
    
    class Config:
        from_attributes = True

# Scholarship Brief & Detail
class ScholarshipBrief(BaseModel):
    id: int
    name: str
    award_amount: str
    deadline: str
    website: Optional[str] = None
    
    class Config:
        from_attributes = True

class ScholarshipCreate(BaseModel):
    name: str
    eligibility: str
    award_amount: str
    deadline: str
    website: Optional[str] = None

class ScholarshipResponse(ScholarshipCreate):
    id: int
    
    class Config:
        from_attributes = True

# Career Schemas
class CareerBriefResponse(BaseModel):
    id: int
    name: str
    category: str
    demand: str
    duration: str
    degree: str
    salary_india: Dict[str, int]
    
    class Config:
        from_attributes = True

class CareerCreate(BaseModel):
    name: str
    category: str
    overview: str
    responsibilities: List[str] = []
    eligibility: str
    salary_india: Dict[str, int] # e.g. {"min": 300000, "max": 1500000, "average": 700000}
    salary_global: Dict[str, int]
    demand: str
    duration: str
    degree: str
    roadmap: List[Dict[str, str]] = [] # e.g. [{"stage": "10th", "desc": "Take math"}]

class CareerResponse(CareerCreate):
    id: int
    colleges: List[CollegeBrief] = []
    exams: List[ExamBrief] = []
    scholarships: List[ScholarshipBrief] = []
    
    class Config:
        from_attributes = True

# Assessment Schemas
class AssessmentOption(BaseModel):
    text: str
    career_weights: Dict[str, int] # e.g. {"Software Engineer": 5, "Doctor": 0}

class AssessmentQuestionResponse(BaseModel):
    id: int
    question_text: str
    category: str
    options: List[AssessmentOption]
    
    class Config:
        from_attributes = True

class AssessmentResponseSubmit(BaseModel):
    # Dict of question_id (as string) to option index (int)
    responses: Dict[str, int]

class CareerRecommendationResponse(BaseModel):
    career: CareerBriefResponse
    score: float
    reasons: List[str]
    
    class Config:
        from_attributes = True

# Saved Career Schemas
class SavedCareerToggle(BaseModel):
    career_id: int

# Chat Schemas
class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, str]] = [] # list of {"sender": "user"|"ai", "text": "message"}

class ChatResponse(BaseModel):
    reply: str
    suggested_careers: List[CareerBriefResponse] = []

# Admin Analytics Schemas
class AnalyticsCard(BaseModel):
    label: str
    value: int
    change: float # percentage change

class PopularItem(BaseModel):
    name: str
    count: int

class AdminAnalyticsResponse(BaseModel):
    cards: List[AnalyticsCard]
    registrations_over_time: List[Dict[str, Any]] # [{"date": "2026-07-01", "students": 10, "admins": 1}]
    popular_careers: List[PopularItem]
    popular_subjects: List[PopularItem]
    popular_interests: List[PopularItem]
    assessment_completion_rate: float
