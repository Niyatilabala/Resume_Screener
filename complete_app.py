import streamlit as st
import pandas as pd
import random, time, datetime, io, base64, re
import hashlib
import json

import nltk
import spacy
from pyresparser import ResumeParser
from pdfminer.high_level import extract_text
from streamlit_tags import st_tags
from PIL import Image
import pymysql
import plotly.express as px
import pafy

ds_course = [['Machine Learning Crash Course by Google [Free]', 'https://developers.google.com/machine-learning/crash-course'],
             ['Machine Learning A-Z by Udemy','https://www.udemy.com/course/machinelearning/'],
             ['Machine Learning by Andrew NG','https://www.coursera.org/learn/machine-learning'],
             ['Data Scientist Master Program of Simplilearn (IBM)','https://www.simplilearn.com/big-data-and-analytics/senior-data-scientist-masters-program-training'],
             ['Data Science Foundations: Fundamentals by LinkedIn','https://www.linkedin.com/learning/data-science-foundations-fundamentals-5']]

web_course = [['Django Crash course [Free]','https://youtu.be/e1IyzVyrLSU'],
              ['Python and Django Full Stack Web Developer Bootcamp','https://www.udemy.com/course/python-and-django-full-stack-web-developer-bootcamp'],
              ['React Crash Course [Free]','https://youtu.be/Dorf8i6lCuk'],
              ['ReactJS Project Development Training','https://www.dotnettricks.com/training/masters-program/reactjs-certification-training'],
              ['Full Stack Web Developer - MEAN Stack','https://www.simplilearn.com/full-stack-web-developer-mean-stack-certification-training']]

android_course = [['Android Development for Beginners [Free]','https://youtu.be/fis26HvvDII'],
                  ['Android App Development Specialization','https://www.coursera.org/specializations/android-app-development'],
                  ['Associate Android Developer Certification','https://grow.google/androiddev/#?modal_active=none'],
                  ['Become an Android Kotlin Developer by Udacity','https://www.udacity.com/course/android-kotlin-developer-nanodegree--nd940']]

ios_course = [['IOS App Development by LinkedIn','https://www.linkedin.com/learning/subscription/topics/ios'],
              ['iOS & Swift - The Complete iOS App Development Bootcamp','https://www.udemy.com/course/ios-13-app-development-bootcamp/'],
              ['Become an iOS Developer','https://www.udacity.com/course/ios-developer-nanodegree--nd003'],
              ['iOS App Development with Swift Specialization','https://www.coursera.org/specializations/app-development']]

uiux_course = [['Google UX Design Professional Certificate','https://www.coursera.org/professional-certificates/google-ux-design'],
               ['UI / UX Design Specialization','https://www.coursera.org/specializations/ui-ux-design'],
               ['The Complete App Design Course - UX, UI and Design Thinking','https://www.udemy.com/course/the-complete-app-design-course-ux-and-ui-design/'],
               ['UX & Web Design Master Course: Strategy, Design, Development','https://www.udemy.com/course/ux-web-design-master-course-strategy-design-development/']]

resume_videos = ['https://youtu.be/y8YH0Qbu5h4','https://youtu.be/J-4Fv8nq1iA',
                 'https://youtu.be/yp693O87GmM','https://youtu.be/UeMmCex9uTU']

interview_videos = ['https://youtu.be/Ji46s5BHdr0','https://youtu.be/seVxXHi2YMs',
                    'https://youtu.be/9FgfsLa_SmY','https://youtu.be/2HQmjLu-6RQ']

#SETUP
st.set_page_config("Smart Resume Analyzer", "./Logo/SRA_Logo.ico", layout="wide")

nltk.download("stopwords")
try:
    nlp = spacy.load("en_core_web_sm")
except:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

#DB CONNECTION
def get_db_connection(db_name=None):
    try:
        if db_name:
            connection = pymysql.connect(
                host="localhost",
                user="root",
                password="Niyu2211#",
                db=db_name
            )
        else:
            connection = pymysql.connect(
                host="localhost",
                user="root",
                password="Niyu2211#"
            )
        return connection, connection.cursor()
    except Exception as e:
        print(f"Database connection error: {e}")
        return None, None

connection, cursor = None, None

# -------------------- DB SETUP --------------------
@st.cache_resource
def setup_database():
    """Setup database and all required tables"""
    
    conn, cur = get_db_connection()
    if not conn or not cur:
        print("❌ Cannot connect to MySQL server")
        return False
    
    try:
        print("Creating database sra_app...")
        cur.execute("CREATE DATABASE IF NOT EXISTS sra_app;")
        conn.commit()
        print("✅ Database created")
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False
    finally:
        cur.close()
        conn.close()
    
    # Step 3: Connect to the new database
    import time
    time.sleep(0.5)  # Small delay to ensure database is created
    
    conn, cur = get_db_connection("sra_app")
    if not conn or not cur:
        print("❌ Cannot connect to sra_app database")
        return False
    
    try:
        tables = [
            """CREATE TABLE IF NOT EXISTS admin_users (
                ID INT NOT NULL AUTO_INCREMENT,
                Username VARCHAR(50) UNIQUE NOT NULL,
                Email VARCHAR(100) UNIQUE NOT NULL,
                Password VARCHAR(255) NOT NULL,
                Company_Name VARCHAR(100),
                Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (ID)
            )""",
            
            """CREATE TABLE IF NOT EXISTS regular_users (
                ID INT NOT NULL AUTO_INCREMENT,
                Username VARCHAR(50) UNIQUE NOT NULL,
                Email VARCHAR(100) UNIQUE NOT NULL,
                Password VARCHAR(255) NOT NULL,
                Full_Name VARCHAR(100),
                Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (ID)
            )""",
            
            """CREATE TABLE IF NOT EXISTS job_descriptions (
                ID INT NOT NULL AUTO_INCREMENT,
                Admin_ID INT NOT NULL,
                Job_Title VARCHAR(100) NOT NULL,
                Company_Name VARCHAR(100),
                Description TEXT,
                Required_Skills VARCHAR(500),
                Recommended_Skills VARCHAR(500),
                Experience_Level VARCHAR(30),
                Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (ID),
                FOREIGN KEY (Admin_ID) REFERENCES admin_users(ID) ON DELETE CASCADE
            )""",
            
            """CREATE TABLE IF NOT EXISTS user_applications (
                ID INT NOT NULL AUTO_INCREMENT,
                User_ID INT NOT NULL,
                Job_ID INT NOT NULL,
                Admin_ID INT NOT NULL,
                Resume_Score VARCHAR(8),
                Predicted_Field VARCHAR(50),
                User_Level VARCHAR(30),
                Actual_Skills VARCHAR(300),
                Recommended_Skills VARCHAR(300),
                Recommended_Courses VARCHAR(600),
                Applied_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (ID),
                FOREIGN KEY (User_ID) REFERENCES regular_users(ID) ON DELETE CASCADE,
                FOREIGN KEY (Job_ID) REFERENCES job_descriptions(ID) ON DELETE CASCADE,
                FOREIGN KEY (Admin_ID) REFERENCES admin_users(ID) ON DELETE CASCADE
            )""",
            
            """CREATE TABLE IF NOT EXISTS resume_data (
                ID INT NOT NULL AUTO_INCREMENT,
                User_ID INT NOT NULL,
                Job_ID INT NOT NULL,
                Admin_ID INT NOT NULL,
                Name VARCHAR(100),
                Email VARCHAR(100),
                Phone VARCHAR(20),
                LinkedIn VARCHAR(200),
                GitHub VARCHAR(200),
                Years_of_Experience INT,
                Skills VARCHAR(500),
                Page_Count INT,
                Parsed_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (ID),
                FOREIGN KEY (User_ID) REFERENCES regular_users(ID) ON DELETE CASCADE,
                FOREIGN KEY (Job_ID) REFERENCES job_descriptions(ID) ON DELETE CASCADE,
                FOREIGN KEY (Admin_ID) REFERENCES admin_users(ID) ON DELETE CASCADE
            )"""
        ]
        
        for i, table_sql in enumerate(tables):
            try:
                cur.execute(table_sql)
                print(f"✅ Table {i+1}/{len(tables)} created")
            except Exception as table_error:
                if "already exists" in str(table_error):
                    print(f"✅ Table {i+1}/{len(tables)} already exists")
                else:
                    print(f"❌ Error creating table {i+1}: {table_error}")
        
        conn.commit()
        print("✅ Database setup complete!")
        return True
        
    except Exception as e:
        print(f"❌ Database setup error: {e}")
        return False
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

# Initialize database on startup
setup_database()

# SKILL MAP
SKILL_MAP = {
    "Data Science": {
        "keywords": ["tensorflow", "keras", "pytorch", "machine learning", "flask", "streamlit", "data", "ml"],
        "skills": ["ML", "DL", "Scikit-learn", "TensorFlow", "PyTorch"],
        "courses": ds_course
    },
    "Web Development": {
        "keywords": ["react", "django", "node", "javascript", "flask", "web", "html", "css"],
        "skills": ["React", "Node.js", "Django", "JavaScript"],
        "courses": web_course
    },
    "Android": {
        "keywords": ["android", "kotlin", "flutter", "java"],
        "skills": ["Android", "Kotlin", "Flutter"],
        "courses": android_course
    },
    "iOS": {
        "keywords": ["ios", "swift", "xcode", "objective"],
        "skills": ["Swift", "iOS Dev", "Xcode"],
        "courses": ios_course
    },
    "UI/UX": {
        "keywords": ["figma", "ux", "ui", "photoshop", "design"],
        "skills": ["Figma", "Wireframing", "UX Research"],
        "courses": uiux_course
    }
}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def read_pdf(path):
    return extract_text(path)

def show_pdf(path):
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    st.markdown(
        f'<iframe src="data:application/pdf;base64,{b64}" width="700" height="900"></iframe>',
        unsafe_allow_html=True
    )

def parse_resume(path, job_skills):
    try:
        data = ResumeParser(path).get_extracted_data()
        if data and data.get("skills"):
            return data
    except:
        pass

    text = read_pdf(path)

    lines = [l.strip() for l in text.split("\n") if l.strip()]
    name = lines[0] if len(lines[0].split()) <= 4 else ""

    email = re.search(r"[\w\.-]+@[\w\.-]+", text)
    phone = re.search(r"\+?\d[\d\s\-]{7,}", text)
    linkedin = re.search(r"(linkedin\.com/in/[A-Za-z0-9\-_/]+)", text.lower())
    github = re.search(r"(github\.com/[A-Za-z0-9\-_/]+)", text.lower())

    return {
        "name": name,
        "email": email.group(0) if email else "",
        "mobile_number": phone.group(0) if phone else "",
        "linkedin_url": linkedin.group(0) if linkedin else "",
        "github_url": github.group(0) if github else "",
        "skills": extract_skills(text, job_skills),  
        "no_of_pages": max(1, text.count("\f") + 1)
    }

def extract_skills(resume_text, job_skills):
    resume_text = resume_text.lower()
    job_skill_list = [s.strip().lower() for s in job_skills.split(",")]

    matched_skills = []
    for skill in job_skill_list:
        if skill and skill in resume_text:
            matched_skills.append(skill.title())

    return matched_skills

def detect_field(skills):
    for field, data in SKILL_MAP.items():
        for skill in skills:
            if skill.lower() in data["keywords"]:
                return field, data
    return None, None

def get_user_level(years):
    if years == 0:
        return "Fresher"
    elif years < 5:
        return "Intermediate"
    else:
        return "Expert"


def calculate_resume_score(resume_data, resume_text, job_skills):
    score = 0
    text = resume_text.lower()

    if resume_data.get("name"):
        score += 10
    if resume_data.get("email"):
        score += 10
    if resume_data.get("mobile_number"):
        score += 10

    if len(resume_data.get("skills", [])) >= 5:
        score += 20

    # EXPERIENCE BASED ON JOB SKILLS
    job_skill_list = [s.strip().lower() for s in job_skills.split(",")]
    matched = [s for s in job_skill_list if s in text]

    ratio = len(matched) / max(len(job_skill_list), 1)
    if ratio >= 0.5:
        score += 20
    elif ratio >= 0.3:
        score += 10

    education_keywords = [
        "education", "b.tech", "bachelor",
        "degree", "university", "college"
    ]
    if any(k in text for k in education_keywords):
        score += 10

    if resume_data.get("no_of_pages", 1) in [1, 2]:
        score += 10

    return min(score, 100)

def recommend_courses(courses):
    st.subheader("🎓 Recommended Courses")
    random.shuffle(courses)
    for i, (name, link) in enumerate(courses[:4], 1):
        st.markdown(f"{i}. [{name}]({link})")

def get_table_download_link(df, filename):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">📥 Download Report</a>'
    return href

# -------------------- AUTHENTICATION --------------------
def admin_signup(username, email, password, company_name):
    conn, cur = get_db_connection("sra_app")
    if not conn or not cur:
        st.error("Database not available")
        return False
    try:
        hashed_pwd = hash_password(password)
        cur.execute(
            "INSERT INTO admin_users (Username, Email, Password, Company_Name) VALUES (%s, %s, %s, %s)",
            (username, email, hashed_pwd, company_name)
        )
        conn.commit()
        st.success("✅ Admin signup successful! Please login.")
        return True
    except pymysql.IntegrityError:
        st.error("❌ Username or Email already exists")
        return False
    except Exception as e:
        st.error(f"❌ Error: {e}")
        return False
    finally:
        cur.close()
        conn.close()

def admin_login(username, password):
    conn, cur = get_db_connection("sra_app")
    if not conn or not cur:
        st.error("Database not available")
        return None
    try:
        hashed_pwd = hash_password(password)
        cur.execute(
            "SELECT ID, Username, Company_Name FROM admin_users WHERE Username = %s AND Password = %s",
            (username, hashed_pwd)
        )
        result = cur.fetchone()
        return result
    except Exception as e:
        st.error(f"❌ Error: {e}")
        return None
    finally:
        cur.close()
        conn.close()

def user_signup(username, email, password, full_name):
    conn, cur = get_db_connection("sra_app")
    if not conn or not cur:
        st.error("Database not available")
        return False
    try:
        hashed_pwd = hash_password(password)
        cur.execute(
            "INSERT INTO regular_users (Username, Email, Password, Full_Name) VALUES (%s, %s, %s, %s)",
            (username, email, hashed_pwd, full_name)
        )
        conn.commit()
        st.success("✅ User signup successful! Please login.")
        return True
    except pymysql.IntegrityError:
        st.error("❌ Username or Email already exists")
        return False
    except Exception as e:
        st.error(f"❌ Error: {e}")
        return False
    finally:
        cur.close()
        conn.close()

def user_login(username, password):
    conn, cur = get_db_connection("sra_app")
    if not conn or not cur:
        st.error("Database not available")
        return None
    
    try:
        hashed_pwd = hash_password(password)
        cur.execute(
            "SELECT ID, Username, Full_Name FROM regular_users WHERE Username = %s AND Password = %s",
            (username, hashed_pwd)
        )
        result = cur.fetchone()
        return result
    except Exception as e:
        st.error(f"❌ Error: {e}")
        return None
    finally:
        cur.close()
        conn.close()

# -------------------- MAIN APP --------------------
def main():
    st.title("🚀 Smart Resume Analyzer")
    
    # Check database connection
    test_conn, test_cur = get_db_connection("sra_app")
    if not test_conn or not test_cur:
        st.error("""
        ❌ **Database Connection Failed**
        
        Please ensure:
        1. MySQL Server is running
        2. Database credentials are correct:
           - Host: localhost
           - User: root
           - Password: Niyu2211#
        
        To start MySQL on Windows:
        - Open Services (services.msc)
        - Find "MySQL80" and click "Start the service"
        - Or run: `net start MySQL80` in Command Prompt (as Admin)
        """)
        return
    else:
        test_cur.close()
        test_conn.close()
    
    # Initialize session state
    if 'user_logged_in' not in st.session_state:
        st.session_state.user_logged_in = False
        st.session_state.user_id = None
        st.session_state.user_name = None
        st.session_state.admin_logged_in = False
        st.session_state.admin_id = None
        st.session_state.admin_name = None
        st.session_state.company_name = None
    
    # Main mode selector
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        mode = st.radio("Select Mode", ["🏠 Home", "👤 User", "👨‍💼 Admin"], horizontal=True)
    
    if mode == "🏠 Home":
        st.markdown("---")
        st.markdown("""
        # Welcome to Smart Resume Analyzer
        
        Choose your role:
        - **👤 User**: Upload your resume and match it with job openings
        - **👨‍💼 Admin**: Post job openings and view applicant data
        """)
    
    elif mode == "👤 User":
        user_mode()
    
    elif mode == "👨‍💼 Admin":
        admin_mode()

# -------------------- USER MODE --------------------
def user_mode():
    st.header("👤 User Dashboard")
    
    if not st.session_state.user_logged_in:
        st.markdown("---")
        tab1, tab2 = st.tabs(["🔓 Login", "📝 Sign Up"])
        
        with tab1:
            st.subheader("Login to Your Account")
            username = st.text_input("Username", key="user_login_username")
            password = st.text_input("Password", type="password", key="user_login_password")
            
            if st.button("🔓 Login"):
                result = user_login(username, password)
                if result:
                    st.session_state.user_logged_in = True
                    st.session_state.user_id = result[0]
                    st.session_state.user_name = result[2]
                    st.success(f"✅ Welcome, {result[2]}!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")
        
        with tab2:
            st.subheader("Create New Account")
            new_username = st.text_input("Username", key="user_signup_username")
            new_email = st.text_input("Email", key="user_signup_email")
            new_password = st.text_input("Password", type="password", key="user_signup_password")
            full_name = st.text_input("Full Name", key="user_signup_fullname")
            
            if st.button("📝 Sign Up"):
                if new_username and new_email and new_password and full_name:
                    if user_signup(new_username, new_email, new_password, full_name):
                        time.sleep(1)
                else:
                    st.error("❌ All fields are required")
    
    else:
        # User logged in
        st.markdown(f"**Logged in as**: {st.session_state.user_name}")
        
        if st.button("🚪 Logout", key="user_logout"):
            st.session_state.user_logged_in = False
            st.session_state.user_id = None
            st.session_state.user_name = None
            st.rerun()
        
        st.markdown("---")
        
        # Show available jobs
        conn, cur = get_db_connection("sra_app")
        if not conn or not cur:
            st.error("Database not available")
            return
        
        try:
            cur.execute("SELECT ID, Admin_ID, Job_Title, Company_Name, Required_Skills, Experience_Level FROM job_descriptions ORDER BY Created_At DESC")
            jobs = cur.fetchall()
            
            if not jobs:
                st.info("📭 No job openings available at the moment")
            else:
                st.subheader("📋 Available Jobs")
                
                for job in jobs:
                    job_id, admin_id, title, company, req_skills, exp_level = job
                    
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"### {title}")
                            st.markdown(f"**Company**: {company if company else 'N/A'}")
                            st.markdown(f"**Experience Level**: {exp_level}")
                            st.markdown(f"**Required Skills**: {req_skills}")
                        
                        with col2:
                            if st.button(f"➡️ Apply", key=f"apply_{job_id}"):
                                st.session_state.selected_job_id = job_id
                                st.session_state.selected_admin_id = admin_id
                                st.session_state.selected_job_title = title
                                st.session_state.selected_req_skills = req_skills
                                st.rerun()
                        
                        st.markdown("---")
                
                # If job selected, show application form
                if hasattr(st.session_state, 'selected_job_id') and st.session_state.selected_job_id:
                    st.markdown("---")
                    st.subheader(f"📄 Apply for: {st.session_state.selected_job_title}")
                    
                    pdf_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"], key=f"resume_{st.session_state.selected_job_id}")
                    
                    if pdf_file:
                        save_path = f"./Uploaded_Resumes/{st.session_state.user_id}_{pdf_file.name}"
                        with open(save_path, "wb") as f:
                            f.write(pdf_file.read())
                        
                        show_pdf(save_path)                       
                        # Parse resume
                        resume_data = parse_resume(
                            save_path,
                            st.session_state.selected_req_skills
                        )                     
                        st.markdown("---")
                        st.subheader("📊 Resume Analysis")
                        
                        # Basic Information
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("**Name**: " + (resume_data.get("name") or "Not detected"))
                            st.markdown("**Email**: " + (resume_data.get("email") or "Not detected"))
                            st.markdown("**Phone**: " + (resume_data.get("mobile_number") or "Not detected"))
                        with col2:
                            st.markdown("**LinkedIn**: " + (resume_data.get("linkedin_url") or "Not detected"))
                            st.markdown("**GitHub**: " + (resume_data.get("github_url") or "Not detected"))
                            st.markdown("**Pages**: " + str(resume_data.get("no_of_pages", 1)))
                        
                        # Skills detected
                        st.markdown("**Skills Detected**:")
                        skills = resume_data.get("skills", [])
                        
                        if skills:
                            skill_text = ", ".join(skills[:10])
                            st.write(f"🔹 {skill_text}")
                        else:
                            st.write("No skills detected")
                        
                        # Detect career field
                        field, field_info = detect_field(skills)
                        
                        # Calculate experience
                        text = read_pdf(save_path)
                        years_match = re.findall(r'(\d+)\s*(?:years?|yrs?)', text.lower())
                        if years_match:
                            years = int(years_match[0])
                        else:
                            years = 0
                        user_level = get_user_level(years)
                            
                        st.markdown(f"**Experience Level**: {user_level} ({years} years)")
                        
                        if field:
                            st.success(f"✅ **Detected Field**: {field}")
                            st.markdown("**Recommended Skills**:")
                            for skill in field_info["skills"]:
                                st.write(f"  • {skill}")
                        
                        # Calculate resume score
                        resume_text = read_pdf(save_path)

                        resume_score = calculate_resume_score(
                            resume_data,
                            resume_text,
                            st.session_state.selected_req_skills
                        )
                        
                        st.markdown("---")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Resume Score", f"{resume_score:.1f}/100")
                        
                        # Job matching
                        st.markdown("---")
                        st.subheader("🎯 Job Match Analysis")
                        
                        user_skills_list = [s.lower() for s in skills]
                        required_skills_list = [
                            s.strip().lower()
                            for s in st.session_state.selected_req_skills.split(",")
                            if s.strip()
                        ]
                        matched = [s for s in user_skills_list if s in required_skills_list]
                        missing = [s for s in required_skills_list if s not in user_skills_list]
                        
                        match_pct = (len(matched) / len(required_skills_list) * 100) if required_skills_list else 0
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Match Score", f"{match_pct:.1f}%")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("**✅ Skills You Have**:")
                            if matched:
                                for skill in matched:
                                    st.success(f"✓ {skill.title()}")
                            else:
                                st.write("No matching skills")
                        
                        with col2:
                            st.markdown("**❌ Skills You Need**:")
                            if missing:
                                for skill in missing:
                                    st.error(f"✗ {skill.title()}")
                            else:
                                st.write("All skills matched!")
                        
                        # Recommended courses
                        if field and field_info:
                            st.markdown("---")
                            recommend_courses(field_info["courses"])
                        
                        # Save application
                        if st.button("✅ Submit Application"):
                            conn_submit, cur_submit = get_db_connection("sra_app")
                            if conn_submit and cur_submit:
                                try:
                                    actual_skills = ", ".join(skills[:20]) if skills else ""
                                    recommended_skills = ", ".join(field_info["skills"]) if field else ""
                                    recommended_courses = ", ".join([c[0] for c in field_info["courses"][:5]]) if field else ""
                                    
                                    cur_submit.execute("""
                                        INSERT INTO user_applications 
                                        (User_ID, Job_ID, Admin_ID, Resume_Score, Predicted_Field, User_Level, Actual_Skills, Recommended_Skills, Recommended_Courses)
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                                    """, (
                                        st.session_state.user_id,
                                        st.session_state.selected_job_id,
                                        st.session_state.selected_admin_id,
                                        f"{resume_score:.2f}",
                                        field or "Not Detected",
                                        user_level,
                                        actual_skills,
                                        recommended_skills,
                                        recommended_courses
                                    ))
                                    
                                    cur_submit.execute("""
                                        INSERT INTO resume_data
                                        (User_ID, Job_ID, Admin_ID, Name, Email, Phone, LinkedIn, GitHub, Years_of_Experience, Skills, Page_Count)
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                    """, (
                                        st.session_state.user_id,
                                        st.session_state.selected_job_id,
                                        st.session_state.selected_admin_id,
                                        resume_data.get("name", ""),
                                        resume_data.get("email", ""),
                                        resume_data.get("mobile_number", ""),
                                        resume_data.get("linkedin_url", ""),
                                        resume_data.get("github_url", ""),
                                        years,
                                        actual_skills,
                                        resume_data.get("no_of_pages", 1)
                                    ))
                                    
                                    conn_submit.commit()
                                    st.success("✅ Application submitted successfully!")
                                    
                                    # Clear selected job
                                    del st.session_state.selected_job_id
                                    time.sleep(1)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Error: {e}")
                                finally:
                                    cur_submit.close()
                                    conn_submit.close()
        
        except Exception as e:
            st.error(f"❌ Error: {e}")
        finally:
            cur.close()
            conn.close()

# -------------------- ADMIN MODE --------------------
def admin_mode():
    st.header("👨‍💼 Admin Dashboard")
    
    if not st.session_state.admin_logged_in:
        st.markdown("---")
        tab1, tab2 = st.tabs(["🔓 Login", "📝 Sign Up"])
        
        with tab1:
            st.subheader("Admin Login")
            username = st.text_input("Username", key="admin_login_username")
            password = st.text_input("Password", type="password", key="admin_login_password")
            
            if st.button("🔓 Login"):
                result = admin_login(username, password)
                if result:
                    st.session_state.admin_logged_in = True
                    st.session_state.admin_id = result[0]
                    st.session_state.admin_name = result[1]
                    st.session_state.company_name = result[2]
                    st.success(f"✅ Welcome, Admin {result[1]}!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")
        
        with tab2:
            st.subheader("Create Admin Account")
            new_username = st.text_input("Username", key="admin_signup_username")
            new_email = st.text_input("Email", key="admin_signup_email")
            new_password = st.text_input("Password", type="password", key="admin_signup_password")
            company = st.text_input("Company Name", key="admin_signup_company")
            
            if st.button("📝 Sign Up"):
                if new_username and new_email and new_password and company:
                    if admin_signup(new_username, new_email, new_password, company):
                        time.sleep(1)
                else:
                    st.error("❌ All fields are required")
    
    else:
        # Admin logged in
        st.markdown(f"**Logged in as**: {st.session_state.admin_name} ({st.session_state.company_name})")
        
        if st.button("🚪 Logout", key="admin_logout"):
            st.session_state.admin_logged_in = False
            st.session_state.admin_id = None
            st.session_state.admin_name = None
            st.session_state.company_name = None
            st.rerun()
        
        st.markdown("---")
        
        # Admin tabs
        tab1, tab2, tab3 = st.tabs(["📋 Job Postings", "📊 Applicants", "📈 Analytics"])
        
        # Tab 1: Job Postings
        with tab1:
            st.subheader("📋 Manage Job Postings")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Create New Job Posting**")
                job_title = st.text_input("Job Title")
                job_company = st.text_input("Company Name", value=st.session_state.company_name)
                job_desc = st.text_area("Job Description")
                req_skills = st.text_input("Required Skills (comma-separated)")
                rec_skills = st.text_input("Recommended Skills (comma-separated)")
                exp_level = st.selectbox("Experience Level", ["Fresher", "Intermediate", "Expert"])
                
                if st.button("➕ Post Job"):
                    if job_title and req_skills:
                        conn, cur = get_db_connection("sra_app")
                        if conn and cur:
                            try:
                                cur.execute("""
                                    INSERT INTO job_descriptions
                                    (Admin_ID, Job_Title, Company_Name, Description, Required_Skills, Recommended_Skills, Experience_Level)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                                """, (
                                    st.session_state.admin_id,
                                    job_title,
                                    job_company,
                                    job_desc,
                                    req_skills,
                                    rec_skills,
                                    exp_level
                                ))
                                conn.commit()
                                st.success("✅ Job posted successfully!")
                                time.sleep(1)
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error: {e}")
                            finally:
                                cur.close()
                                conn.close()
                    else:
                        st.error("❌ Job title and required skills are mandatory")
            
            with col2:
                st.markdown("**Your Posted Jobs**")
                conn, cur = get_db_connection("sra_app")
                if conn and cur:
                    try:
                        cur.execute(
                            "SELECT ID, Job_Title, Experience_Level, Required_Skills, Created_At FROM job_descriptions WHERE Admin_ID = %s ORDER BY Created_At DESC",
                            (st.session_state.admin_id,)
                        )
                        jobs = cur.fetchall()
                        
                        if jobs:
                            for job in jobs:
                                job_id, title, exp, req, created = job
                                st.markdown(f"**{title}** | {exp}")
                                st.text(f"Required: {req[:50]}...")
                                st.text(f"Posted: {created}")
                                
                                if st.button("🗑️ Delete", key=f"delete_job_{job_id}"):
                                    cur.execute("DELETE FROM job_descriptions WHERE ID = %s", (job_id,))
                                    conn.commit()
                                    st.success("Job deleted!")
                                    time.sleep(1)
                                    st.rerun()
                                
                                st.markdown("---")
                        else:
                            st.info("No job postings yet")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
                    finally:
                        cur.close()
                        conn.close()
        
        # Tab 2: Applicants
        with tab2:
            st.subheader("📊 Applicant Data")
            
            # Get admin's jobs
            conn, cur = get_db_connection("sra_app")
            if conn and cur:
                try:
                    cur.execute(
                        "SELECT ID, Job_Title FROM job_descriptions WHERE Admin_ID = %s",
                        (st.session_state.admin_id,)
                    )
                    jobs = cur.fetchall()
                    
                    if not jobs:
                        st.info("No job postings yet")
                    else:
                        selected_job = st.selectbox(
                            "Select Job to View Applicants",
                            [f"{j[1]} (ID: {j[0]})" for j in jobs],
                            key="job_select"
                        )
                        
                        job_id = int(selected_job.split("(ID: ")[1].rstrip(")"))
                        
                        # Get applicants for this job
                        cur.execute("""
                            SELECT 
                                ua.ID, u.Full_Name, u.Email,
                                ua.Resume_Score, ua.User_Level, ua.Predicted_Field,
                                ua.Actual_Skills, ua.Applied_At
                            FROM user_applications ua
                            JOIN regular_users u ON ua.User_ID = u.ID
                            WHERE ua.Job_ID = %s AND ua.Admin_ID = %s
                            ORDER BY ua.Resume_Score DESC
                        """, (job_id, st.session_state.admin_id))
                        
                        applicants = cur.fetchall()
                        
                        if applicants:
                            st.success(f"✅ Total Applicants: {len(applicants)}")
                            
                            # Create dataframe
                            df = pd.DataFrame(applicants, columns=[
                                "ID", "Name", "Email", "Resume Score",
                                "Experience Level", "Field", "Skills", "Applied Date"
                            ])
                            
                            st.dataframe(df, use_container_width=True)
                            
                            # Download report
                            st.markdown(get_table_download_link(df, f"applicants_{job_id}.csv"), unsafe_allow_html=True)
                        else:
                            st.info("No applicants for this job yet")
                
                except Exception as e:
                    st.error(f"❌ Error: {e}")
                finally:
                    cur.close()
                    conn.close()
        
        # Tab 3: Analytics
        with tab3:
            st.subheader("📈 Analytics & Reports")
            
            conn, cur = get_db_connection("sra_app")
            if conn and cur:
                try:
                    # Total applicants
                    cur.execute(
                        "SELECT COUNT(*) FROM user_applications WHERE Admin_ID = %s",
                        (st.session_state.admin_id,)
                    )
                    total_applicants = cur.fetchone()[0]
                    
                    # Total jobs posted
                    cur.execute(
                        "SELECT COUNT(*) FROM job_descriptions WHERE Admin_ID = %s",
                        (st.session_state.admin_id,)
                    )
                    total_jobs = cur.fetchone()[0]
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Jobs Posted", total_jobs)
                    with col2:
                        st.metric("Total Applicants", total_applicants)
                    with col3:
                        avg_applicants = total_applicants / max(total_jobs, 1)
                        st.metric("Avg Applicants/Job", f"{avg_applicants:.1f}")
                    
                    st.markdown("---")
                    
                    # Charts
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Experience level pie chart
                        cur.execute("""
                            SELECT User_Level, COUNT(*) as count
                            FROM user_applications
                            WHERE Admin_ID = %s
                            GROUP BY User_Level
                        """, (st.session_state.admin_id,))
                        
                        exp_data = cur.fetchall()
                        if exp_data:
                            exp_df = pd.DataFrame(exp_data, columns=["Experience Level", "Count"])
                            fig = px.pie(exp_df, names="Experience Level", values="Count",
                                       title="Applicants by Experience Level")
                            st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        # Field pie chart
                        cur.execute("""
                            SELECT Predicted_Field, COUNT(*) as count
                            FROM user_applications
                            WHERE Admin_ID = %s
                            GROUP BY Predicted_Field
                        """, (st.session_state.admin_id,))
                        
                        field_data = cur.fetchall()
                        if field_data:
                            field_df = pd.DataFrame(field_data, columns=["Field", "Count"])
                            fig = px.pie(field_df, names="Field", values="Count",
                                       title="Applicants by Field")
                            st.plotly_chart(fig, use_container_width=True)
                
                except Exception as e:
                    st.error(f"❌ Error: {e}")
                finally:
                    cur.close()
                    conn.close()

if __name__ == "__main__":
    main()
