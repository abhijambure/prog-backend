import json
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.core.security import hash_password
from app.models import (
    User, StudentProfile, Career, College, Exam, Scholarship, 
    AssessmentQuestion, career_college_association, 
    career_exam_association, career_scholarship_association
)

def seed_db():
    print("Starting database seeding...")
    
    # 1. Ensure all tables are created
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        # 2. Seed Users
        admin_user = db.query(User).filter(User.email == "admin@careercompass.com").first()
        if not admin_user:
            admin_user = User(
                email="admin@careercompass.com",
                hashed_password=hash_password("AdminPassword123"),
                role="admin"
            )
            db.add(admin_user)
            db.commit()
            print("Admin user seeded (admin@careercompass.com / AdminPassword123)")
            
        student_user = db.query(User).filter(User.email == "student@careercompass.com").first()
        if not student_user:
            student_user = User(
                email="student@careercompass.com",
                hashed_password=hash_password("StudentPassword123"),
                role="student"
            )
            db.add(student_user)
            db.commit()
            
            profile = StudentProfile(
                user_id=student_user.id,
                full_name="Abhi Jain",
                class_name="12th Standard",
                academic_board="CBSE",
                city="Mumbai",
                state="Maharashtra",
                percentage=88.5,
                preferred_stream="Science",
                favorite_subjects=["Mathematics", "Physics", "Computer Science"],
                interests=["Coding", "Solving Puzzles", "Gaming"],
                skills=["Problem Solving", "Logical Reasoning"],
                personality_type="Analytical",
                hobbies=["Reading", "Chess"],
                career_goals=["Become a Tech Lead", "Build scalable AI systems"]
            )
            db.add(profile)
            db.commit()
            print("Student user seeded (student@careercompass.com / StudentPassword123)")

        # 3. Seed Colleges
        col1 = db.query(College).filter(College.name == "Indian Institute of Technology (IIT) Bombay").first()
        if not col1:
            col1 = College(
                name="Indian Institute of Technology (IIT) Bombay",
                city="Mumbai",
                state="Maharashtra",
                ranking=1,
                website="https://www.iitb.ac.in",
                programs=["B.Tech Computer Science", "B.Tech Electrical", "M.Tech AI/ML"],
                admission_process="Requires clearing JEE Main and JEE Advanced with top ranks."
            )
            db.add(col1)
        
        col2 = db.query(College).filter(College.name == "All India Institute of Medical Sciences (AIIMS) Delhi").first()
        if not col2:
            col2 = College(
                name="All India Institute of Medical Sciences (AIIMS) Delhi",
                city="New Delhi",
                state="Delhi",
                ranking=1,
                website="https://www.aiims.edu",
                programs=["MBBS", "B.Sc Nursing", "M.D. Surgery"],
                admission_process="Requires clearing NEET-UG exam with top 100 AIR rank."
            )
            db.add(col2)
            
        col3 = db.query(College).filter(College.name == "Shri Ram College of Commerce (SRCC)").first()
        if not col3:
            col3 = College(
                name="Shri Ram College of Commerce (SRCC)",
                city="New Delhi",
                state="Delhi",
                ranking=1,
                website="https://www.srcc.edu",
                programs=["B.Com (Honours)", "B.A. Economics (Honours)"],
                admission_process="Admissions based on CUET-UG examination percentile scores."
            )
            db.add(col3)
            
        col4 = db.query(College).filter(College.name == "National Institute of Design (NID)").first()
        if not col4:
            col4 = College(
                name="National Institute of Design (NID)",
                city="Ahmedabad",
                state="Gujarat",
                ranking=1,
                website="https://www.nid.edu",
                programs=["Bachelor of Design (B.Des)", "Master of Design (M.Des)"],
                admission_process="Based on NID Design Aptitude Test (DAT) Prelims and Mains."
            )
            db.add(col4)
            
        db.commit()
        print("Colleges seeded.")

        # 4. Seed Exams
        ex1 = db.query(Exam).filter(Exam.name == "JEE Main & Advanced").first()
        if not ex1:
            ex1 = Exam(
                name="JEE Main & Advanced",
                eligibility="Passed 12th standard with Physics, Chemistry, and Mathematics (PCM).",
                syllabus=["Physics (Mechanics, Electromagnetism)", "Chemistry (Organic, Inorganic, Physical)", "Mathematics (Calculus, Algebra, Coordinate Geometry)"],
                exam_pattern="Two stages: JEE Main (Computer-Based MCQ testing) and JEE Advanced (Complex numerical/multi-select questions).",
                important_dates={
                    "Registration Starts": "November 2026",
                    "JEE Main Session 1": "January 2027",
                    "JEE Main Session 2": "April 2027",
                    "JEE Advanced Exam": "May 2027"
                },
                registration_link="https://jeemain.nta.ac.in",
                website="https://jeemain.nta.ac.in"
            )
            db.add(ex1)
            
        ex2 = db.query(Exam).filter(Exam.name == "NEET UG").first()
        if not ex2:
            ex2 = Exam(
                name="NEET UG",
                eligibility="Passed 12th standard with Physics, Chemistry, Biology/Biotechnology (PCB). Minimum age of 17.",
                syllabus=["Biology (Botany & Zoology)", "Physics (General, Optics, Thermodynamics)", "Chemistry (Organic, Physical)"],
                exam_pattern="Pen & Paper based exam, 200 minutes, 180 questions to be answered (out of 200). Negative marking is applied.",
                important_dates={
                    "Registration Starts": "February 2027",
                    "Exam Date": "May 2027",
                    "Results Declared": "June 2027"
                },
                registration_link="https://neet.nta.nic.in",
                website="https://neet.nta.nic.in"
            )
            db.add(ex2)
            
        ex3 = db.query(Exam).filter(Exam.name == "CLAT (Common Law Admission Test)").first()
        if not ex3:
            ex3 = Exam(
                name="CLAT (Common Law Admission Test)",
                eligibility="Passed 12th standard with minimum 45% marks. No upper age limit.",
                syllabus=["English Language", "Current Affairs & GK", "Legal Reasoning", "Logical Reasoning", "Quantitative Techniques"],
                exam_pattern="Offline paper of 120 marks containing 120 multiple-choice questions over 2 hours.",
                important_dates={
                    "Registration Open": "July 2026",
                    "Last Date to Apply": "November 2026",
                    "Exam Date": "December 2026"
                },
                registration_link="https://consortiumofnlus.ac.in",
                website="https://consortiumofnlus.ac.in"
            )
            db.add(ex3)
            
        db.commit()
        print("Exams seeded.")

        # 5. Seed Scholarships
        sch1 = db.query(Scholarship).filter(Scholarship.name == "National Talent Search Scholarship").first()
        if not sch1:
            sch1 = Scholarship(
                name="National Talent Search Scholarship",
                eligibility="Students studying in Class 10 or 12, nominated through national talent screening.",
                award_amount="₹1,250 per month for Class 11-12; ₹2,000 per month for Undergraduates.",
                deadline="September annually",
                website="https://ncert.nic.in"
            )
            db.add(sch1)
            
        sch2 = db.query(Scholarship).filter(Scholarship.name == "L'Oréal India For Young Women In Science").first()
        if not sch2:
            sch2 = Scholarship(
                name="L'Oréal India For Young Women In Science",
                eligibility="Female students who passed 12th Standard in Science with at least 85%. Annual family income under 6 Lakhs.",
                award_amount="₹2,50,000 for graduation studies.",
                deadline="October annually",
                website="https://www.loreal.com"
            )
            db.add(sch2)
            
        db.commit()
        print("Scholarships seeded.")

        # 6. Seed Careers
        c1 = db.query(Career).filter(Career.name == "AI/ML Engineer").first()
        if not c1:
            c1 = Career(
                name="AI/ML Engineer",
                category="Engineering",
                overview="An AI/ML Engineer designs, builds, and deploys intelligent algorithms and machines capable of learning, reasoning, and acting autonomously. They work with deep learning networks, generative AI, and statistical models.",
                responsibilities=[
                    "Build statistical models to analyze big data.",
                    "Design and implement deep learning algorithms and transformers.",
                    "Optimize machine learning pipelines for real-time production.",
                    "Collaborate with data engineers to build robust training systems."
                ],
                eligibility="Completed 12th with Physics, Chemistry, and Mathematics (PCM). Bachelor's degree in Computer Science, Data Science, or related engineering stream.",
                salary_india={"min": 600000, "max": 3000000, "average": 1500000},
                salary_global={"min": 90000, "max": 250000, "average": 140000},
                demand="High",
                duration="4 Years",
                degree="B.Tech or B.E. in Computer Science / AI / DS",
                roadmap=[
                    {"stage": "10th Standard", "desc": "Focus on score optimization in Mathematics and Computer Applications."},
                    {"stage": "12th Standard", "desc": "Opt for Science stream (PCM) and prepare for engineering entrance exams like JEE."},
                    {"stage": "College Admission", "desc": "Join a reputable institute for a B.Tech/B.E in Computer Science or Data Science."},
                    {"stage": "Degree & Skills", "desc": "Learn Python, Linear Algebra, Calculus, SQL, and libraries like PyTorch or TensorFlow."},
                    {"stage": "Internship & Growth", "desc": "Build portfolio projects on GitHub and secure a Machine Learning Internship."},
                    {"stage": "Employment", "desc": "Apply for Junior AI/ML Engineer, Data Scientist, or NLP Engineer roles."}
                ]
            )
            db.add(c1)
            
        c2 = db.query(Career).filter(Career.name == "Software Engineer").first()
        if not c2:
            c2 = Career(
                name="Software Engineer",
                category="Engineering",
                overview="A Software Engineer writes, tests, and debugs code to create robust software systems, web platforms, and mobile apps. They apply computer science theories to build solutions for modern consumer and business needs.",
                responsibilities=[
                    "Write clean, maintainable, and scalable code in languages like JavaScript, Java, Go, or Python.",
                    "Collaborate in Agile teams to design features and software components.",
                    "Conduct peer code reviews and optimize database operations.",
                    "Troubleshoot production systems and resolve server/UI defects."
                ],
                eligibility="Completed 12th standard with mathematics. B.Tech / B.E / BCA / MCA in IT or Computer Science.",
                salary_india={"min": 400000, "max": 2500000, "average": 900000},
                salary_global={"min": 75000, "max": 180000, "average": 110000},
                demand="High",
                duration="3-4 Years",
                degree="B.Tech Computer Science or BCA+MCA",
                roadmap=[
                    {"stage": "10th Standard", "desc": "Develop strong logical thinking and try simple coding tutorials (HTML/CSS/JS)."},
                    {"stage": "12th Standard", "desc": "Choose Science/Mathematics and score well in exams. Explore algorithms."},
                    {"stage": "College", "desc": "Secure a seat in B.Tech CS/IT or BCA. Excel in Data Structures and DBMS."},
                    {"stage": "Practical Projects", "desc": "Develop full-stack web projects using modern stacks (React, Node, FastAPI)."},
                    {"stage": "Job Search", "desc": "Solve algorithmic puzzles (LeetCode/HackerRank) and crack campus placements."}
                ]
            )
            db.add(c2)
            
        c3 = db.query(Career).filter(Career.name == "Doctor").first()
        if not c3:
            c3 = Career(
                name="Doctor",
                category="Medical",
                overview="A Medical Doctor diagnoses illnesses, prescribes medicines, conducts clinical treatments, and performs surgeries to restore patient health. They are the backbone of the public and private healthcare ecosystem.",
                responsibilities=[
                    "Examine patients and record medical history details.",
                    "Prescribe diagnostic tests and interpret radiological/lab findings.",
                    "Design and execute long-term treatment strategies.",
                    "Perform clinical procedures or coordinate surgical interventions."
                ],
                eligibility="Completed 12th standard in PCB (Physics, Chemistry, Biology) with at least 50%. Pass the national NEET-UG exam.",
                salary_india={"min": 700000, "max": 3500000, "average": 1200000},
                salary_global={"min": 150000, "max": 400000, "average": 220000},
                demand="High",
                duration="5.5 Years",
                degree="MBBS (Bachelor of Medicine, Bachelor of Surgery)",
                roadmap=[
                    {"stage": "10th Standard", "desc": "Focus heavily on Biology, Chemistry, and general sciences."},
                    {"stage": "12th Standard", "desc": "Select PCB stream. Join entrance coaching and dedicate time to NEET-UG preparation."},
                    {"stage": "NEET Exam", "desc": "Qualify for NEET and secure admission into a government or private medical college."},
                    {"stage": "MBBS Study", "desc": "Complete 4.5 years of rigorous clinical curriculum and theory exams."},
                    {"stage": "Internship", "desc": "Complete 1 year of compulsory rotating internship in hospitals."},
                    {"stage": "Specialization (Optional)", "desc": "Crack NEET-PG to study MD/MS specializing in cardiology, pediatrics, or surgery."}
                ]
            )
            db.add(c3)

        c4 = db.query(Career).filter(Career.name == "Chartered Accountant").first()
        if not c4:
            c4 = Career(
                name="Chartered Accountant",
                category="Management",
                overview="A Chartered Accountant (CA) is a certified expert in auditing, corporate taxation, forensic accounting, financial planning, and business analysis. They manage company portfolios, verify tax filings, and consult on growth strategies.",
                responsibilities=[
                    "Conduct financial audits to verify statutory compliance.",
                    "Formulate corporate tax planning and file returns.",
                    "Analyze business expenditure and provide budget advisory.",
                    "Resolve corporate financial disputes or forensic investigations."
                ],
                eligibility="Passed 10+2 standard from any stream (preferably Commerce). Pass all three levels of the ICAI CA program.",
                salary_india={"min": 600000, "max": 2000000, "average": 1000000},
                salary_global={"min": 60000, "max": 150000, "average": 90000},
                demand="High",
                duration="4-5 Years",
                degree="CA Qualification (ICAI)",
                roadmap=[
                    {"stage": "10th Standard", "desc": "Select Commerce stream with Mathematics or Accountancy."},
                    {"stage": "CA Foundation", "desc": "Register with ICAI and pass the CA Foundation exam after 12th."},
                    {"stage": "CA Intermediate", "desc": "Complete intermediate study and pass Group 1 & 2 exams."},
                    {"stage": "Articleship", "desc": "Complete 2 years of practical training under an active practicing CA firm."},
                    {"stage": "CA Final", "desc": "Crack the challenging CA Final examinations to earn your license."}
                ]
            )
            db.add(c4)

        c5 = db.query(Career).filter(Career.name == "UI/UX Designer").first()
        if not c5:
            c5 = Career(
                name="UI/UX Designer",
                category="Creative",
                overview="UI/UX Designers study user journeys, build interactive wireframes, and design the visual interface of software systems, web platforms, and mobile apps to ensure maximum accessibility and visual beauty.",
                responsibilities=[
                    "Conduct user interviews and research target demographics.",
                    "Design wireframes, journey maps, and high-fidelity mockups.",
                    "Collaborate with software engineers to implement custom css assets.",
                    "Conduct usability testing to optimize conversion and click rates."
                ],
                eligibility="Completed 12th standard from any stream. A degree or diploma in Visual Communication, Interaction Design, or Design.",
                salary_india={"min": 350000, "max": 1800000, "average": 750000},
                salary_global={"min": 55000, "max": 130000, "average": 85000},
                demand="High",
                duration="3-4 Years",
                degree="Bachelor of Design (B.Des) or related certification",
                roadmap=[
                    {"stage": "10th Standard", "desc": "Engage in hobbies like painting, sketch art, or digital graphics editor software."},
                    {"stage": "12th Standard", "desc": "Choose any stream. Prepare for creative examinations like NID DAT or UCEED."},
                    {"stage": "Design College", "desc": "Pursue a B.Des or take intensive courses on user interfaces and prototyping."},
                    {"stage": "Portfolio Building", "desc": "Master tools like Figma and Adobe XD. Publish projects on Behance/Dribbble."},
                    {"stage": "Internship & Job", "desc": "Apply for UX Research internships and build corporate client profiles."}
                ]
            )
            db.add(c5)

        db.commit()
        print("Careers seeded.")

        # --- Link Careers to Colleges, Exams, and Scholarships (Many-to-Many) ---
        # Fetch seeded instances
        db_c1 = db.query(Career).filter(Career.name == "AI/ML Engineer").first()
        db_c2 = db.query(Career).filter(Career.name == "Software Engineer").first()
        db_c3 = db.query(Career).filter(Career.name == "Doctor").first()
        db_c4 = db.query(Career).filter(Career.name == "Chartered Accountant").first()
        db_c5 = db.query(Career).filter(Career.name == "UI/UX Designer").first()
        
        db_col1 = db.query(College).filter(College.name == "Indian Institute of Technology (IIT) Bombay").first()
        db_col2 = db.query(College).filter(College.name == "All India Institute of Medical Sciences (AIIMS) Delhi").first()
        db_col3 = db.query(College).filter(College.name == "Shri Ram College of Commerce (SRCC)").first()
        db_col4 = db.query(College).filter(College.name == "National Institute of Design (NID)").first()
        
        db_ex1 = db.query(Exam).filter(Exam.name == "JEE Main & Advanced").first()
        db_ex2 = db.query(Exam).filter(Exam.name == "NEET UG").first()
        db_ex3 = db.query(Exam).filter(Exam.name == "CLAT (Common Law Admission Test)").first()
        
        db_sch1 = db.query(Scholarship).filter(Scholarship.name == "National Talent Search Scholarship").first()
        db_sch2 = db.query(Scholarship).filter(Scholarship.name == "L'Oréal India For Young Women In Science").first()

        # Build associations
        if db_c1 and db_col1 and db_col1 not in db_c1.colleges:
            db_c1.colleges.append(db_col1)
        if db_c1 and db_ex1 and db_ex1 not in db_c1.exams:
            db_c1.exams.append(db_ex1)
        if db_c1 and db_sch2 and db_sch2 not in db_c1.scholarships:
            db_c1.scholarships.append(db_sch2)

        if db_c2 and db_col1 and db_col1 not in db_c2.colleges:
            db_c2.colleges.append(db_col1)
        if db_c2 and db_ex1 and db_ex1 not in db_c2.exams:
            db_c2.exams.append(db_ex1)

        if db_c3 and db_col2 and db_col2 not in db_c3.colleges:
            db_c3.colleges.append(db_col2)
        if db_c3 and db_ex2 and db_ex2 not in db_c3.exams:
            db_c3.exams.append(db_ex2)
            
        if db_c4 and db_col3 and db_col3 not in db_c4.colleges:
            db_c4.colleges.append(db_col3)
            
        if db_c5 and db_col4 and db_col4 not in db_c5.colleges:
            db_c5.colleges.append(db_col4)
            
        db.commit()
        print("Career directory links created.")

        # 7. Seed Assessment Questions
        q_count = db.query(AssessmentQuestion).count()
        if q_count == 0:
            questions = [
                {
                    "question_text": "Which of these activities sounds most exciting to you on a weekend?",
                    "category": "interests",
                    "options": [
                        {"text": "Writing code or creating a small website script.", "career_weights": {"Software Engineer": 5, "AI/ML Engineer": 5}},
                        {"text": "Reading about medical research or human biology updates.", "career_weights": {"Doctor": 5}},
                        {"text": "Designing visual flyers, sketching, or editing interface graphics.", "career_weights": {"UI/UX Designer": 5}},
                        {"text": "Creating budgets, tracking stock lists, or checking business numbers.", "career_weights": {"Chartered Accountant": 5}}
                    ]
                },
                {
                    "question_text": "What subject did you find yourself looking forward to the most during standard school hours?",
                    "category": "subjects",
                    "options": [
                        {"text": "Mathematics, Algebra, or Logic puzzles.", "career_weights": {"Software Engineer": 4, "AI/ML Engineer": 5, "Chartered Accountant": 4}},
                        {"text": "Biology, botany, zoology, or healthcare topics.", "career_weights": {"Doctor": 5}},
                        {"text": "Art, visual drawing, or creative writing portfolios.", "career_weights": {"UI/UX Designer": 5}},
                        {"text": "Economics, bookkeeping, or commercial math.", "career_weights": {"Chartered Accountant": 5}}
                    ]
                },
                {
                    "question_text": "When resolving a complex challenge, what is your primary strength?",
                    "category": "skills",
                    "options": [
                        {"text": "Breaking it down logically and solving it step-by-step.", "career_weights": {"Software Engineer": 5, "AI/ML Engineer": 5, "Chartered Accountant": 3}},
                        {"text": "Empathizing with others and finding patient care options.", "career_weights": {"Doctor": 5}},
                        {"text": "Visualizing a creative layout or abstract graphical solution.", "career_weights": {"UI/UX Designer": 5}},
                        {"text": "Analyzing financial audit metrics and finding accounting slips.", "career_weights": {"Chartered Accountant": 5}}
                    ]
                },
                {
                    "question_text": "Which of these work environments sounds most appealing to your style?",
                    "category": "personality",
                    "options": [
                        {"text": "A tech startup coding software features inside collaborative teams.", "career_weights": {"Software Engineer": 5, "AI/ML Engineer": 4}},
                        {"text": "A bustling hospital or clinical environment directly helping patients.", "career_weights": {"Doctor": 5}},
                        {"text": "A creative visual studio brainstorming aesthetic digital solutions.", "career_weights": {"UI/UX Designer": 5}},
                        {"text": "An corporate office consulting firms on financial accounting and taxation.", "career_weights": {"Chartered Accountant": 5}}
                    ]
                },
                {
                    "question_text": "How do you feel about statistics, big datasets, and looking for patterns?",
                    "category": "personality",
                    "options": [
                        {"text": "I love data! I enjoy finding insights and building prediction engines.", "career_weights": {"AI/ML Engineer": 5, "Chartered Accountant": 3}},
                        {"text": "I like using logical calculations to build system algorithms.", "career_weights": {"Software Engineer": 5}},
                        {"text": "I am interested in patient cases and diagnostics more than raw numbers.", "career_weights": {"Doctor": 4}},
                        {"text": "I prefer visual style configurations and creative aesthetics.", "career_weights": {"UI/UX Designer": 4}}
                    ]
                }
            ]
            
            for q_data in questions:
                q = AssessmentQuestion(
                    question_text=q_data["question_text"],
                    category=q_data["category"],
                    options=q_data["options"]
                )
                db.add(q)
            db.commit()
            print("Assessment questions seeded successfully.")
            
        print("Database seeding completed successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
