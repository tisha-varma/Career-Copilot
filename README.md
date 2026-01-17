<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/FastAPI-0.104+-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/LLaMA%203.1-Groq-orange?style=for-the-badge" alt="LLaMA"/>
  <img src="https://img.shields.io/badge/Google%20Gemini-AI-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Gemini"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License"/>
</p>

<h1 align="center">🚀 Career Copilot AI</h1>

<p align="center">
  <strong>An Intelligent AI-Powered Career Guidance Platform</strong><br>
  Transform your job search with advanced resume analysis, personalized learning roadmaps, and AI-generated career assets.
</p>

<p align="center">
  <a href="#-key-features">Features</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-tech-stack">Tech Stack</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-demo">Demo</a> •
  <a href="#-deployment">Deployment</a>
</p>

---

## 🎯 Problem Statement

Job seekers often struggle with:
- Understanding how well their resume matches target roles
- Identifying skill gaps and creating effective learning plans  
- Writing compelling, personalized cover letters
- Preparing for role-specific technical interviews
- Efficiently searching across multiple job platforms

**Career Copilot AI** solves these challenges using a multi-agent AI system that provides comprehensive career guidance in one unified platform.

---

## ✨ Key Features

### 📊 **Intelligent Resume Analysis**
- Upload PDF resumes with automatic text extraction using **pdfplumber**
- 4-step agentic analysis workflow powered by **Google Gemini**:
  1. **Resume Understanding** - Extracts skills, education, experience
  2. **Role Fit Analysis** - Calculates match score against 8 target roles
  3. **Learning Roadmap** - Generates prioritized skill development plan
  4. **Reflection** - Validates analysis completeness

### ✉️ **AI Cover Letter Generator**
- Generates personalized, professional cover letters using **LLaMA 3.1** (via Groq)
- Leverages **BGE Embeddings** + **ChromaDB** for semantic resume understanding
- Extracts and highlights specific projects, technologies, and achievements
- Download as professionally formatted PDF using **ReportLab**

### 🎤 **Interview Preparation**
- Role-specific technical and behavioral questions for 8 career paths
- **LLM-powered personalized questions** based on YOUR resume
- Difficulty levels (Easy/Medium/Hard) with expert tips
- STAR method guidance for behavioral responses

### 🔍 **Multi-Platform Job Search**
- Direct links to 5 major job platforms (LinkedIn, Indeed, Glassdoor, Google Jobs, Wellfound)
- Pre-configured search queries based on your target role
- Role-specific job search tips and strategies

### 📈 **Google Sheets Export**
- One-click export of analysis to Google Sheets via **OAuth 2.0**
- Organized tabs: Summary, Skills Gap, Learning Roadmap
- Perfect for tracking progress and sharing with mentors

### 🎬 **YouTube Learning Resources**
- Curated video recommendations based on identified skill gaps
- Links to top tech learning channels
- Personalized learning content suggestions

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              Frontend Layer                              │
│                    HTML/CSS (Tailwind) + Jinja2 Templates                │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           FastAPI Backend                                │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │
│  │   /analyze   │ │ /cover-letter│ │  /interview  │ │    /jobs     │   │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          AI/ML Processing Layer                          │
│  ┌────────────────────┐  ┌────────────────────┐  ┌──────────────────┐  │
│  │   Google Gemini    │  │   LLaMA 3.1 (Groq) │  │  BGE Embeddings  │  │
│  │   (Analysis Agent) │  │  (Cover Letters)   │  │   + ChromaDB     │  │
│  └────────────────────┘  └────────────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          Integration Layer                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐  │
│  │ Google Sheets   │  │  PDF Generation │  │   Resume Extraction     │  │
│  │ (OAuth 2.0)     │  │   (ReportLab)   │  │    (pdfplumber)         │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

### Agentic Workflow

The resume analysis uses a **multi-step agentic loop** where each step builds on previous results:

```
Resume Upload → Text Extraction → Gemini Agent Loop
                                        │
        ┌───────────────────────────────┼───────────────────────────────┐
        ▼                               ▼                               ▼
  Step 1: Understand              Step 2: Analyze               Step 3: Plan
  Extract skills,                 Calculate role fit,           Generate learning
  experience, education           identify gaps                 roadmap
        │                               │                               │
        └───────────────────────────────┼───────────────────────────────┘
                                        ▼
                                 Step 4: Reflect
                                 Validate completeness,
                                 iterate if needed
```

---

## 🛠️ Tech Stack

### **Backend Framework**
| Technology | Purpose |
|------------|---------|
| **FastAPI** | High-performance async web framework |
| **Uvicorn** | ASGI server with hot reload |
| **Jinja2** | Server-side templating |

### **AI/ML Stack**
| Technology | Purpose |
|------------|---------|
| **Google Gemini 1.5** | Primary analysis agent (4-step reasoning loop) |
| **LLaMA 3.1 (Groq)** | Cover letter generation, interview questions |
| **BGE Embeddings** | Semantic understanding of resume content |
| **ChromaDB** | Vector store for similarity search |
| **Sentence Transformers** | Local embedding generation |

### **Document Processing**
| Technology | Purpose |
|------------|---------|
| **pdfplumber** | PDF text extraction |
| **ReportLab** | PDF cover letter generation |

### **Google Cloud Integration**
| Technology | Purpose |
|------------|---------|
| **Google Sheets API** | Export analysis data |
| **OAuth 2.0** | Secure authentication |
| **Google Generative AI** | Gemini API access |

### **Frontend**
| Technology | Purpose |
|------------|---------|
| **Tailwind CSS** | Modern, responsive styling |
| **HTML5** | Semantic markup |
| **Vanilla JS** | Interactive components |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+ (recommended: 3.12)
- pip package manager
- API keys for Gemini and Groq (free tiers available)

### 1. Clone the Repository

```bash
git clone https://github.com/tisha-varma/Career-Copilot-AI.git
cd Career-Copilot-AI
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Environment Variables

```bash
# Windows PowerShell
$env:GEMINI_API_KEY = "your_gemini_api_key_here"
$env:GROQ_API_KEY = "your_groq_api_key_here"

# Linux/Mac
export GEMINI_API_KEY="your_gemini_api_key_here"
export GROQ_API_KEY="your_groq_api_key_here"
```

<details>
<summary>📌 How to get API Keys (Click to expand)</summary>

#### Google Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy and save the key

#### Groq API Key (for LLaMA 3.1)
1. Go to [Groq Console](https://console.groq.com/keys)
2. Create a free account
3. Generate a new API key
4. Copy and save the key

</details>

### 5. Run the Application

```bash
cd app
uvicorn main:app --reload
```

### 6. Open in Browser

Navigate to **http://127.0.0.1:8000**

---

## 📸 Demo

### Home Page
Upload your resume (PDF) and select your target role from 8 career paths.

### Analysis Dashboard
View your role fit score, strengths, skill gaps, and personalized learning roadmap.

### Cover Letter Generator
Input job details and receive an AI-crafted cover letter tailored to your experience.

### Interview Prep
Practice with role-specific questions generated from YOUR resume.

---

## 🎯 Supported Career Paths

| Role | Technical Focus |
|------|-----------------|
| 🖥️ **Frontend Developer** | React, JavaScript, CSS, TypeScript |
| ⚙️ **Backend Developer** | Python, Java, APIs, Databases |
| 🔧 **Full Stack Developer** | End-to-end web development |
| 📊 **Data Analyst** | SQL, Python, Visualization, Statistics |
| 🤖 **Machine Learning Engineer** | TensorFlow, PyTorch, MLOps |
| 🚀 **DevOps Engineer** | Docker, Kubernetes, CI/CD |
| 📱 **Product Manager** | Strategy, Roadmapping, Agile |
| 🎨 **UX Designer** | Figma, User Research, Prototyping |

---

## 🌐 Deployment

### Deploy to Render (Recommended - Free Tier)

1. Push your code to GitHub
2. Go to [render.com](https://render.com) and create account
3. Click **New** → **Web Service**
4. Connect your GitHub repository
5. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd app && uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables:
   - `GEMINI_API_KEY`
   - `GROQ_API_KEY`
7. Click **Deploy**

### Deploy with Docker

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
WORKDIR /app/app

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t career-copilot .
docker run -p 8000:8000 \
  -e GEMINI_API_KEY=your_key \
  -e GROQ_API_KEY=your_key \
  career-copilot
```

---

## 📁 Project Structure

```
Career-Copilot-AI/
├── app/
│   ├── main.py              # FastAPI application & routes
│   ├── agent.py             # Gemini agentic analysis loop
│   ├── prompts.py           # LLM prompt templates
│   ├── resume_parser.py     # PDF upload handling
│   ├── resume_extractor.py  # Structured data extraction
│   ├── llama_analyzer.py    # LLaMA + BGE + ChromaDB integration
│   ├── cover_letter.py      # Cover letter generation
│   ├── interview_prep.py    # Interview questions database
│   ├── resume_analyzer.py   # LLM interview question generation
│   ├── job_search.py        # Job platform URLs & tips
│   ├── youtube_search.py    # Learning video recommendations
│   ├── sheets_api.py        # Google Sheets OAuth & export
│   ├── sheets_export.py     # TSV data formatting
│   ├── pdf_generator.py     # Cover letter PDF creation
│   ├── templates/           # Jinja2 HTML templates
│   │   ├── index.html       # Home page
│   │   ├── result.html      # Analysis results
│   │   ├── cover_letter.html
│   │   ├── interview.html
│   │   └── jobs.html
│   └── static/              # CSS, JS, images
├── requirements.txt         # Python dependencies
├── render.yaml              # Render deployment config
├── Procfile                 # Heroku/Render process file
└── README.md
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes | Google Gemini API key for resume analysis |
| `GROQ_API_KEY` | Yes | Groq API key for LLaMA 3.1 access |
| `GOOGLE_CLIENT_ID` | Optional | For Google Sheets export |
| `GOOGLE_CLIENT_SECRET` | Optional | For Google Sheets export |

### Demo Mode

If API keys are unavailable or quota is exceeded, the app automatically switches to **demo mode** with keyword-based analysis. This ensures the application remains functional for demonstration purposes.

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Google** for Gemini AI and Google Cloud APIs
- **Meta** for LLaMA 3.1 open-source model
- **Groq** for lightning-fast LLaMA inference
- **Hugging Face** for Sentence Transformers and BGE embeddings
- **ChromaDB** team for the excellent vector database

---

<p align="center">
  <strong>Built with ❤️ for job seekers everywhere</strong><br>
  <sub>Star ⭐ this repo if you find it helpful!</sub>
</p>
