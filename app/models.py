from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table, Float, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

# Junction tables for many-to-many relationships
career_college_association = Table(
    'career_colleges',
    Base.metadata,
    Column('career_id', Integer, ForeignKey('careers.id', ondelete='CASCADE'), primary_key=True),
    Column('college_id', Integer, ForeignKey('colleges.id', ondelete='CASCADE'), primary_key=True)
)

career_exam_association = Table(
    'career_exams',
    Base.metadata,
    Column('career_id', Integer, ForeignKey('careers.id', ondelete='CASCADE'), primary_key=True),
    Column('exam_id', Integer, ForeignKey('exams.id', ondelete='CASCADE'), primary_key=True)
)

career_scholarship_association = Table(
    'career_scholarships',
    Base.metadata,
    Column('career_id', Integer, ForeignKey('careers.id', ondelete='CASCADE'), primary_key=True),
    Column('scholarship_id', Integer, ForeignKey('scholarships.id', ondelete='CASCADE'), primary_key=True)
)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="student", nullable=False) # "student", "admin"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    student_profile = relationship("StudentProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    assessment_responses = relationship("AssessmentResponse", back_populates="user", cascade="all, delete-orphan")
    recommendations = relationship("CareerRecommendation", back_populates="user", cascade="all, delete-orphan")
    saved_careers = relationship("SavedCareer", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")

class StudentProfile(Base):
    __tablename__ = "student_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    class_name = Column(String(50), nullable=True) # "10th Standard", "12th Standard"
    academic_board = Column(String(100), nullable=True) # "CBSE", "ICSE", "State Board"
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    percentage = Column(Float, nullable=True)
    preferred_stream = Column(String(100), nullable=True) # "Science", "Commerce", "Arts"
    favorite_subjects = Column(JSON, nullable=True) # List of strings
    interests = Column(JSON, nullable=True) # List of strings
    skills = Column(JSON, nullable=True) # List of strings
    personality_type = Column(String(50), nullable=True) # E.g., "Analytical", "Creative"
    hobbies = Column(JSON, nullable=True) # List of strings
    career_goals = Column(JSON, nullable=True) # List of strings
    completed_assessment = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="student_profile")

class Career(Base):
    __tablename__ = "careers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    category = Column(String(50), nullable=False) # e.g. Engineering, Creative
    overview = Column(Text, nullable=False)
    responsibilities = Column(JSON, nullable=False) # List of duties
    eligibility = Column(Text, nullable=False)
    salary_india = Column(JSON, nullable=False) # {min: int, max: int, average: int}
    salary_global = Column(JSON, nullable=False) # {min: int, max: int, average: int}
    demand = Column(String(50), nullable=False) # High, Medium, Low
    duration = Column(String(50), nullable=False) # e.g., "4 Years"
    degree = Column(String(100), nullable=False) # e.g., "B.Tech"
    roadmap = Column(JSON, nullable=False) # List of roadmap stages with descriptions
    
    # Relationships
    colleges = relationship("College", secondary=career_college_association, back_populates="careers")
    exams = relationship("Exam", secondary=career_exam_association, back_populates="careers")
    scholarships = relationship("Scholarship", secondary=career_scholarship_association, back_populates="careers")
    recommendations = relationship("CareerRecommendation", back_populates="career", cascade="all, delete-orphan")
    saved_by_users = relationship("SavedCareer", back_populates="career", cascade="all, delete-orphan")

class College(Base):
    __tablename__ = "colleges"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), unique=True, index=True, nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    ranking = Column(Integer, nullable=True)
    website = Column(String(200), nullable=True)
    programs = Column(JSON, nullable=False) # List of degrees/programs
    admission_process = Column(Text, nullable=True)
    
    # Relationships
    careers = relationship("Career", secondary=career_college_association, back_populates="colleges")

class Exam(Base):
    __tablename__ = "exams"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    eligibility = Column(Text, nullable=False)
    syllabus = Column(JSON, nullable=False) # List of key topics
    exam_pattern = Column(Text, nullable=False)
    important_dates = Column(JSON, nullable=False) # Dictionary of events & dates
    registration_link = Column(String(200), nullable=True)
    website = Column(String(200), nullable=True)
    
    # Relationships
    careers = relationship("Career", secondary=career_exam_association, back_populates="exams")

class Scholarship(Base):
    __tablename__ = "scholarships"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), unique=True, index=True, nullable=False)
    eligibility = Column(Text, nullable=False)
    award_amount = Column(String(100), nullable=False)
    deadline = Column(String(100), nullable=False)
    website = Column(String(200), nullable=True)
    
    # Relationships
    careers = relationship("Career", secondary=career_scholarship_association, back_populates="scholarships")

class AssessmentQuestion(Base):
    __tablename__ = "assessment_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(Text, nullable=False)
    category = Column(String(50), nullable=False) # "interests", "skills", "personality", "subjects"
    options = Column(JSON, nullable=False) # List of options: [{text: str, career_weights: {career_name: weight_int}}]

class AssessmentResponse(Base):
    __tablename__ = "assessment_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    response_data = Column(JSON, nullable=False) # dict of question_id: option_index
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="assessment_responses")

class CareerRecommendation(Base):
    __tablename__ = "career_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    career_id = Column(Integer, ForeignKey("careers.id", ondelete="CASCADE"), nullable=False)
    score = Column(Float, nullable=False) # 0 to 100
    reasons = Column(JSON, nullable=False) # List of string explanations
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="recommendations")
    career = relationship("Career", back_populates="recommendations")

class SavedCareer(Base):
    __tablename__ = "saved_careers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    career_id = Column(Integer, ForeignKey("careers.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="saved_careers")
    career = relationship("Career", back_populates="saved_by_users")

class Blog(Base):
    __tablename__ = "blogs"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    author = Column(String(100), default="Career Guide")
    created_at = Column(DateTime, default=datetime.utcnow)

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
