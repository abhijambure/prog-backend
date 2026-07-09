import os
from sqlalchemy.orm import Session
from app.models import Career, StudentProfile
import urllib.request
import json

def get_ai_reply(db: Session, user_id: int, message: str, history: list) -> dict:
    """
    Generates a reply for the AI Career Assistant.
    Supports a smart local search/rule-engine and checks for a Gemini API key.
    """
    msg_lower = message.lower().strip()
    
    # 1. Fetch careers for matching
    careers = db.query(Career).all()
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
    
    # Check for Gemini API key
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        try:
            # We can run a direct HTTP request to Gemini API to avoid dependency errors.
            # Using Gemini 1.5 Flash API endpoint:
            # POST https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=YOUR_API_KEY
            url = f"https://genergenerativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
            # Let's fix the domain (generativelanguage.googleapis.com, wait, my typo, let's write it carefully)
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
            
            # Construct career database context for the AI
            db_context = "Available careers in our system: " + ", ".join([c.name for c in careers]) + ".\n"
            if profile:
                db_context += f"Current student profile: Name={profile.full_name}, Stream={profile.preferred_stream or 'None'}, Subjects={profile.favorite_subjects or 'None'}, Interests={profile.interests or 'None'}, Personality={profile.personality_type or 'None'}.\n"
            
            # Format history for prompt
            hist_str = ""
            for chat in history[-4:]: # last 4 messages
                hist_str += f"{chat.get('sender', 'user').capitalize()}: {chat.get('text', '')}\n"
            
            system_instruction = (
                "You are Career Compass AI, a helpful, encouraging, and expert career guidance counselor.\n"
                "Provide brief, clear, and structured educational career advice.\n"
                "Never make definitive promises. Guide the student using their skills and interests.\n"
                "Refer to careers in our database when relevant. Always suggest next steps (e.g. assessments or courses).\n"
                f"{db_context}"
            )
            
            prompt = f"{system_instruction}\n{hist_str}User: {message}\nAI:"
            
            body = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ]
            }
            
            req = urllib.request.Request(
                url,
                data=json.dumps(body).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                reply_text = res_data['candidates'][0]['content']['parts'][0]['text']
                
                # Check for matching careers to return in schema
                suggested = []
                for c in careers:
                    if c.name.lower() in reply_text.lower():
                        suggested.append(c)
                
                return {
                    "reply": reply_text.strip(),
                    "suggested_careers": suggested[:3]
                }
        except Exception as e:
            # Fallback to local rule engine if API call fails
            pass

    # --- Smart Local Rule & Database Search Engine ---
    reply = ""
    suggested = []
    
    # Rule 1: Specific career matches
    matched_careers = []
    for c in careers:
        if c.name.lower() in msg_lower:
            matched_careers.append(c)
            
    if matched_careers:
        c = matched_careers[0]
        suggested.append(c)
        salary_avg = c.salary_india.get("average", 500000)
        formatted_salary = f"₹{salary_avg:,} per year" if salary_avg else "Variable"
        reply = (
            f"**{c.name}** is a great career path under the **{c.category}** sector!\n\n"
            f"**Overview:** {c.overview}\n\n"
            f"**Key Details:**\n"
            f"- **Degree Required:** {c.degree} ({c.duration})\n"
            f"- **Eligibility:** {c.eligibility}\n"
            f"- **Average Salary in India:** {formatted_salary}\n"
            f"- **Job Demand:** {c.demand}\n\n"
            f"You can view the full vertical timeline roadmap and top colleges for {c.name} in our Career Directory."
        )
        # Add extra suggestions if more matched
        if len(matched_careers) > 1:
            suggested.extend(matched_careers[1:3])
            
    # Rule 2: 10th standard query
    elif "10th" in msg_lower or "after 10" in msg_lower:
        reply = (
            "After the 10th standard, you typically choose a stream that aligns with your interest and future career goals:\n\n"
            "1. **Science (PCM/PCB):** Ideal for careers in engineering, technology, medicine, pharmaceuticals, and pure sciences.\n"
            "2. **Commerce:** Ideal for finance, accounting, business management, marketing, chartered accountancy, and economics.\n"
            "3. **Arts (Humanities):** Ideal for law, design, writing, civil services, psychology, and journalism.\n\n"
            "I highly recommend completing your profile details, specifying your favorite subjects, and taking our **Career Assessment** so we can compute a personalized compatibility ranking for you."
        )
        
    # Rule 3: 12th standard query
    elif "12th" in msg_lower or "after 12" in msg_lower:
        reply = (
            "After 12th standard, you typically apply for professional degrees or specialized college programs. "
            "Depending on your stream, you can target specific national entrance examinations:\n\n"
            "- **Science Stream:** JEE Main/Advanced (Engineering), NEET (Medical), B.Sc, BCA.\n"
            "- **Commerce Stream:** CA Foundation, CMA, B.Com, BBA, Eco (Hons).\n"
            "- **Arts Stream:** CLAT (Law), NID/UCEED (Design), B.A. programs.\n\n"
            "Check our **Entrance Examination** and **College Directory** tabs to explore applications, key patterns, and syllabus files."
        )
        
    # Rule 4: Coding / Programming / Software / Computer
    elif any(k in msg_lower for k in ["code", "coding", "software", "program", "computer", "tech"]):
        eng_careers = [c for c in careers if c.category.lower() in ["engineering", "technology"]]
        suggested.extend(eng_careers[:3])
        reply = (
            "If you enjoy coding and technology, you have several exciting career paths:\n\n"
            "- **Software Engineer:** Focuses on developing web, mobile, and desktop applications.\n"
            "- **AI/ML Engineer:** Focuses on neural networks, statistical analysis, and machine learning models.\n\n"
            "Both paths typically require a degree like a B.Tech/B.E in Computer Science or a BCA/MCA. "
            "Important skills include programming (Python, JavaScript, Java), algorithms, and data structures. "
            "Check our Career Directory for detail timelines!"
        )
        
    # Rule 5: Biology / Medicine / Doctor / Health
    elif any(k in msg_lower for k in ["biology", "medical", "doctor", "health", "science", "pcb"]):
        med_careers = [c for c in careers if c.category.lower() in ["medical", "science"]]
        suggested.extend(med_careers[:3])
        reply = (
            "A background in biology opens up pathways in medical sciences and biotechnology:\n\n"
            "- **Doctor (MBBS):** Traditional career in clinical practice and healthcare.\n"
            "- **Pharmacist:** Focuses on chemical composition and medical drugs.\n\n"
            "To qualify for medicine in India, you must crack the NEET-UG examination. "
            "Other fields include Biotechnology, Nursing, Physiotherapy, and Psychology. "
            "Check out our directories to find participating medical colleges and syllabus information."
        )
        
    # Rule 6: High salary
    elif any(k in msg_lower for k in ["salary", "earn", "money", "paying", "highest"]):
        # Sort careers by average salary in India
        def get_avg_salary(c):
            return c.salary_india.get("average", 0)
        sorted_careers = sorted(careers, key=get_avg_salary, reverse=True)
        suggested.extend(sorted_careers[:3])
        reply = (
            "Some of the highest paying career paths in India include:\n\n"
            "1. **AI/ML Engineer:** Highly sought after as industries adopt automation.\n"
            "2. **Software Engineer:** Excellent career growth, especially in product-based tech firms.\n"
            "3. **Chartered Accountant:** Crucial for corporate finance, auditing, and tax strategies.\n"
            "4. **Marketing Manager:** Leading brand expansion and digital growth models.\n\n"
            "Note that salaries depend heavily on skills, college tier, experience, and performance. "
            "Click on the suggested careers below to see their detailed ranges."
        )
        
    # Default Rule: General greeting or unknown query
    else:
        # Try to suggest based on student profile if available
        if profile and profile.preferred_stream:
            stream_careers = [c for c in careers if c.category.lower() == profile.preferred_stream.lower()]
            suggested.extend(stream_careers[:3])
            reply = (
                f"Hello {profile.full_name}! Based on your profile, you are interested in the **{profile.preferred_stream}** stream. "
                "You can ask me questions about specific careers, college requirements, entrance exams, or stream choices.\n\n"
                "Try asking me: *'What subjects are needed to become a Software Engineer?'* or *'Tell me about CA syllabus'*. "
                "Don't forget to take the **Assessment** to see your compatibility matches!"
            )
        else:
            suggested.extend(careers[:3])
            reply = (
                "Welcome to Career Compass AI Assistant! I can help you answer questions about careers, "
                "colleges, entrance examinations, stream choices, and salaries.\n\n"
                "Try asking:\n"
                "- *'What should I do after 10th?'*\n"
                "- *'How can I become an AI Engineer?'*\n"
                "- *'Which careers pay the most?'*\n\n"
                "To get started, please complete your profile details and complete the **Career Assessment** questionnaire."
            )
            
    # Clean duplicates in suggested list
    seen_ids = set()
    cleaned_suggested = []
    for c in suggested:
        if c.id not in seen_ids:
            seen_ids.add(c.id)
            cleaned_suggested.append(c)
            
    return {
        "reply": reply,
        "suggested_careers": cleaned_suggested[:3]
    }
