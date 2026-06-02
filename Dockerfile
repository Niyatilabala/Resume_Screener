FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    poppler-utils \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

COPY . /app

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

RUN python -m spacy download en_core_web_sm

RUN python -c "import nltk; nltk.download('stopwords')"

RUN mkdir -p Uploaded_Resumes

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]