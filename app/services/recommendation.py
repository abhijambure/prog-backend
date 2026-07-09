from sqlalchemy.orm import Session
from app.models import StudentProfile, Career, AssessmentQuestion, AssessmentResponse, CareerRecommendation
import json

def calculate_recommendations(db: Session, user_id: int):
    # 1. Fetch student profile
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
    if not profile:
        return []
    
    # 2. Fetch assessment responses
    response_record = db.query(AssessmentResponse).filter(AssessmentResponse.user_id == user_id).order_by(AssessmentResponse.id.desc()).first()
    
    # 3. Fetch all careers
    careers = db.query(Career).all()
    
    # Initialize career scores and reason maps
    # We will score each career out of 100 max.
    career_scores = {c.id: 0.0 for c in careers}
    career_reasons = {c.id: [] for c in careers}
    
    # Map career names to objects to lookup IDs
    career_name_map = {c.name.lower(): c for c in careers}
    
    # --- Part A: Process Questionnaire Responses ---
    if response_record and response_record.response_data:
        responses = response_record.response_data # e.g. {"1": 2, "2": 0}
        
        # Fetch all questions to reference weights
        questions = db.query(AssessmentQuestion).all()
        questions_map = {str(q.id): q for q in questions}
        
        for q_id_str, opt_idx in responses.items():
            question = questions_map.get(q_id_str)
            if not question:
                continue
            
            try:
                options = question.options # JSON list
                if opt_idx < len(options):
                    chosen_opt = options[opt_idx]
                    weights = chosen_opt.get("career_weights", {})
                    
                    # Accumulate weights for matching careers
                    for c_name, weight in weights.items():
                        c_obj = career_name_map.get(c_name.lower())
                        if c_obj:
                            career_scores[c_obj.id] += float(weight)
                            # Add simple response-based reason if weight is high
                            if weight >= 3 and len(career_reasons[c_obj.id]) < 2:
                                text_snippet = chosen_opt.get("text", "").lower()
                                career_reasons[c_obj.id].append(f"Your response '{text_snippet}' indicates a high match.")
            except Exception as e:
                # Logging or silent ignore for malformed question/option data
                continue

    # --- Part B: Process Profile-based Heuristics ---
    for c in careers:
        c_name_lower = c.name.lower()
        c_cat_lower = c.category.lower()
        
        # 1. Stream Match
        if profile.preferred_stream:
            stream = profile.preferred_stream.lower()
            # Science matches Software, Doctor, etc.
            # Commerce matches CA, Marketing, Finance
            # Arts matches Creative, Humanities, Writer
            is_science_career = c_cat_lower in ["engineering", "medical", "technology", "science"]
            is_commerce_career = c_cat_lower in ["management", "finance", "business"]
            is_arts_career = c_cat_lower in ["creative", "humanities", "arts", "law"]
            
            if (stream == "science" and is_science_career) or \
               (stream == "commerce" and is_commerce_career) or \
               (stream == "arts" and is_arts_career):
                career_scores[c.id] += 15.0
                career_reasons[c.id].append(f"Highly compatible with your preferred '{profile.preferred_stream}' stream.")
        
        # 2. Subjects Match
        if profile.favorite_subjects:
            fav_subs = [s.lower() for s in profile.favorite_subjects]
            # Match specific keywords in overview or roadmap
            sub_matches = []
            for sub in fav_subs:
                if sub in c.overview.lower() or sub in c.eligibility.lower() or sub in c.degree.lower():
                    sub_matches.append(sub)
            if sub_matches:
                score_to_add = min(len(sub_matches) * 8.0, 24.0)
                career_scores[c.id] += score_to_add
                matched_subs_str = ", ".join([s.capitalize() for s in sub_matches[:2]])
                career_reasons[c.id].append(f"Aligns with your favorite academic subject(s): {matched_subs_str}.")
        
        # 3. Interests Match
        if profile.interests:
            interests = [i.lower() for i in profile.interests]
            interest_matches = []
            for interest in interests:
                if interest in c.overview.lower() or interest in c_cat_lower:
                    interest_matches.append(interest)
            if interest_matches:
                score_to_add = min(len(interest_matches) * 10.0, 20.0)
                career_scores[c.id] += score_to_add
                matched_ints_str = ", ".join([i.capitalize() for i in interest_matches[:2]])
                career_reasons[c.id].append(f"Matches your personal interest in: {matched_ints_str}.")
                
        # 4. Skills Match
        if profile.skills:
            skills = [s.lower() for s in profile.skills]
            skill_matches = []
            # Check career required skills
            career_skills = c.responsibilities # let's search here or in required skills
            c_skills_str = json.dumps(career_skills).lower() + " " + c.overview.lower()
            for skill in skills:
                if skill in c_skills_str:
                    skill_matches.append(skill)
            if skill_matches:
                score_to_add = min(len(skill_matches) * 8.0, 16.0)
                career_scores[c.id] += score_to_add
                matched_skills_str = ", ".join([s.capitalize() for s in skill_matches[:2]])
                career_reasons[c.id].append(f"Utilizes your skill in {matched_skills_str}.")

        # 5. Personality Match
        if profile.personality_type:
            personality = profile.personality_type.lower()
            # Analytical -> Engineering, Science, Finance
            # Creative -> Designer, Artist, Writer
            # Social -> Medicine, Counseling, Human Resources
            # Enterprising -> Marketing, Leadership, Law
            is_analytical_career = c_cat_lower in ["engineering", "science", "technology", "finance"] or "analytical" in c.overview.lower()
            is_creative_career = c_cat_lower in ["creative", "arts", "design"] or "creative" in c.overview.lower()
            is_social_career = c_cat_lower in ["medical", "humanities", "counseling"] or "patient" in c.overview.lower()
            is_enterprising_career = c_cat_lower in ["management", "business", "law"] or "business" in c.overview.lower()
            
            if (personality == "analytical" and is_analytical_career) or \
               (personality == "creative" and is_creative_career) or \
               (personality == "social" and is_social_career) or \
               (personality == "enterprising" and is_enterprising_career):
                career_scores[c.id] += 15.0
                career_reasons[c.id].append(f"Perfect fit for your '{profile.personality_type}' personality profile.")

    # --- Part C: Normalize Scores to 0-100 ---
    results = []
    # Find max raw score to normalize nicely (minimum raw max of 50 to avoid scaling up tiny matches)
    max_raw_score = max(max(career_scores.values()), 50.0)
    
    # Empty standard database, let's create a response list
    for c in careers:
        # Normalize between 0 and 100
        raw = career_scores[c.id]
        normalized = round((raw / max_raw_score) * 100.0)
        # Ensure it's at least 30 if there's any basic category/stream match, cap at 98
        if raw > 0 and normalized < 40:
            normalized = 40.0
        normalized = min(normalized, 98.0)
        
        # Ensure reasons are unique and limited to top 3
        reasons = []
        for r in career_reasons[c.id]:
            if r not in reasons:
                reasons.append(r)
        
        if not reasons:
            reasons = ["Good general matching potential based on demographic averages."]
            
        results.append({
            "career": c,
            "score": normalized,
            "reasons": reasons[:3]
        })
        
    # Sort by compatibility score in descending order
    results.sort(key=lambda x: x["score"], reverse=True)
    return results

def save_and_get_recommendations(db: Session, user_id: int):
    """Calculates recommendations, saves them in db, and updates StudentProfile status"""
    # Delete old recommendations for user
    db.query(CareerRecommendation).filter(CareerRecommendation.user_id == user_id).delete()
    
    # Calculate new ones
    recs = calculate_recommendations(db, user_id)
    
    # Save top recommendations
    for r in recs[:8]: # Save top 8 recommendations
        rec_db = CareerRecommendation(
            user_id=user_id,
            career_id=r["career"].id,
            score=r["score"],
            reasons=r["reasons"]
        )
        db.add(rec_db)
    
    # Update profile status
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
    if profile:
        profile.completed_assessment = True
        db.add(profile)
        
    db.commit()
    return recs
