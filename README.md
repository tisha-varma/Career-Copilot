<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/FastAPI-0.104+-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/LLaMA%203.3-Groq-orange?style=for-the-badge" alt="LLaMA"/>
  <img src="https://img.shields.io/badge/Railway-Deploys-000000?style=for-the-badge&logo=railway&logoColor=white" alt="Railway"/>
</p>

<h1 align="center">🚀 Career Copilot AI</h1>

<p align="center">
  <strong>The Ultimate AI-Powered Carrier Guidance & Resume Optimization Platform</strong><br>
  Analyze your resume, generate high-conversion career assets, and prepare for interviews with precision.
</p>

<p align="center">
  <a href="#-key-features">Features</a> •
  <a href="#-production-readiness">Production Ready</a> •
  <a href="#-tech-stack">Tech Stack</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-deployment-on-railway">Deployment</a> •
  <a href="#-feedback-system">Feedback</a>
</p>

---

## 🎯 What is Career Copilot AI?

**Career Copilot AI** is a professional-grade platform designed to help job seekers land their dream roles. Unlike simple resume scanners, it uses a **multi-agent AI workflow** to provide deep insights, personalized learning plans, and optimized interview preparation.

---

## ✨ Key Features

### 📊 **Deep Resume Analysis**
- **Smart Parsing**: Extract skills and experience using `pdfplumber`.
- **Match Scoring**: Get an instant percentage match against 12+ industry roles.
- **Skill Gap Roadmap**: Receive a prioritized plan to acquire missing technical and soft skills.

### 🎤 **Personalized Interview Preparation**
- **AI-Generated Questions**: Questions specifically tailored to *your* unique background.
- **Role-specific preparation**: Targeted prep for Frontend, Backend, AI Engineer, and more.
- **Expert Tips**: Detailed guidance on answering behavioral questions using the STAR method.

### ✉️ **High-Conversion Cover Letter Generator**
- **Context-Aware**: Generates letters based on your specific projects and achievements.
- **PDF Export**: Download professional, recruiter-ready cover letters instantly.
- **Automatic Name Detection**: Pre-fills your details directly from your resume.

### 🔍 **Smart Job Discovery**
- **Role-Specific Strategy**: AI-generated search strategies for your target role.
- **One-Click Search**: Pre-configured filters for LinkedIn, Google Jobs, and Indeed.

---

## 🛡️ Production-Ready Features

This version has been optimized for high-reliability cloud deployment:

- **🔄 Persistent Sessions**: Robust file-based session management. Your data survives server restarts and works perfectly across multiple web-workers.
- **⚡ Rate Limiting**: Built-in protection against API abuse (per-IP rate limiting).
- **💾 Consolidated Storage**: All persistent data (resumes, sessions, feedback) is stored in a unified `/app/data/` folder for easy cloud volume mounting.
- **🛡️ Input Validation**: Strict validation for file uploads (PDF only, 10MB limit) and role selection.
- **🏠 Resume Session**: Accidentally refreshed? The homepage detects your last analysis so you can resume instantly.

---

## 🛠️ Tech Stack

### **Core Backend**
- **FastAPI**: Modern, high-performance Python web framework.
- **Groq/LLaMA 3.3**: Ultra-fast LLM inference for analysis and generation.
- **pdfplumber**: High-fidelity PDF text extraction.
- **ReportLab**: Dynamic PDF generation for career reports.

### **Intelligence & Data**
- **Persistent Sessions**: JSON-based file storage for multi-worker environments.
- **ChromaDB**: Native vector storage for semantic resume matching.
- **Sentence Transformers**: Local embedding generation for fast processing.

### **Frontend & UI**
- **Tailwind CSS**: Premium, responsive glassmorphism design.
- **Jinja2**: Server-side template rendering.

---

## 🚀 Quick Start

### 1. Initial Setup
```bash
git clone https://github.com/tisha-varma/Career-Copilot.git
cd Career-Copilot
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure API Keys
Create a `keys` file or set environment variables:
```bash
export GROQ_API_KEY="your_api_key_here"
```

### 3. Run Locally
```bash
cd app
python -m uvicorn main:app --reload
```
Navigate to `http://127.0.0.1:8000`

---

## 🚅 Deployment on Railway

This app is pre-configured for **Railway** deployment:

1. **GitHub Connection**: Link this repository to your Railway project.
2. **Persistent Volume (Vital)**: 
   - Mount a volume to: `/app/app/data`
   - *This ensures your resumes, sessions, and feedback remain safe during deployments.*
3. **Environment Variables**: Add your `GROQ_API_KEY`.
4. **Build Config**: The `Procfile` is automatically detected to start the server.

---

## 📝 Feedback & Insights

We value continuous improvement!
- Users can submit feedback directly from the results page.
- **Administrator Export**: Download the collected feedback in an Excel-ready format (`.csv`) by visiting:
  `your-app-url.railway.app/export-feedback-csv`

---

Built with ❤️ by **Tisha Varma** for job seekers everywhere.
