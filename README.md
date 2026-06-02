# 🚀 AI Powered Resume Screener

An intelligent resume screening and job matching platform built using **Python, Streamlit, Machine Learning, MySQL, Docker, and Kubernetes**. The application helps recruiters and job seekers by automatically analyzing resumes, extracting skills, matching candidates with job requirements, and generating resume scores.

---

## Features

### Candidate Features

* User Registration & Login
* Resume Upload (PDF)
* Automatic Resume Parsing
* Resume Skill Extraction
* Resume Scoring
* Job Match Analysis
* Apply for Available Jobs
* Resume Recommendations

### Recruiter Features

* Recruiter Login
* Post New Jobs
* View Applications
* Candidate Filtering
* Skill-Based Candidate Search
* Recruitment Analytics

### AI Features

* Resume Parsing using NLP
* Skill Extraction
* Resume Scoring Algorithm
* Job Requirement Matching
* Candidate Recommendation System

---

## Tech Stack

#### Frontend: Streamlit

#### Backend: Python

#### Database: MySQL 8.0

#### Machine Learning & NLP

* Scikit-Learn
* Pandas
* NumPy
* PyResParser
* NLTK

#### Containerization

* Docker
* Docker Compose

### Container Orchestration

* Kubernetes

---

## 📂 Project Structure

```text
Resume_Screener/
│
├── app.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── deployment.yaml
├── service.yaml
├── .gitignore
└── README.md
```

---

## Docker Implementation

The application has been containerized using Docker.

### Build Docker Image

```bash
docker build -t resume-screener .
```

### Run Docker Container

```bash
docker run -p 8501:8501 resume-screener
```

### Run Using Docker Compose

```bash
docker compose up
```

Application URL:

```text
http://localhost:8501
```

---

## Kubernetes Deployment

The project also supports Kubernetes deployment.

### Deploy Application

```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

### Check Resources

```bash
kubectl get pods
kubectl get services
```

### Access Application

```bash
kubectl port-forward service/resume-service 8501:80
```

Open:

```text
http://localhost:8501
```

---

## 🗄️ Database

MySQL is used for:

* User Management
* Recruiter Management
* Job Listings
* Application Tracking
* Resume Records

---

## 📊 Workflow

```text
Candidate Uploads Resume
            ↓
      Resume Parsing
            ↓
      Skill Extraction
            ↓
      Resume Scoring
            ↓
     Job Match Analysis
            ↓
      Application Submit
            ↓
Recruiter Reviews Candidate
```

---


