# Career Copilot AI

An intelligent resume analysis and career guidance platform powered by AI.

## 🚀 Features

- **Resume Analysis** - AI-powered resume parsing and role fit scoring
- **Cover Letter Generator** - Personalized cover letters using LLaMA 3.1
- **Interview Prep** - Resume-based interview questions
- **Job Search** - Links to 5 major job platforms
- **Google Sheets Export** - Export analysis to spreadsheet

## 🛠️ Tech Stack

- **Backend**: FastAPI, Python 3.12
- **AI/ML**: LLaMA 3.1 (Groq), Google Gemini, BGE Embeddings, ChromaDB
- **Frontend**: Tailwind CSS, Jinja2
- **PDF**: pdfplumber, ReportLab

## 🔧 Local Setup

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/career-copilot-ai.git
cd career-copilot-ai
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set environment variables:
```bash
# Windows PowerShell
$env:GEMINI_API_KEY = "your_gemini_api_key"
$env:GROQ_API_KEY = "your_groq_api_key"

# Linux/Mac
export GEMINI_API_KEY="your_gemini_api_key"
export GROQ_API_KEY="your_groq_api_key"
```

4. Run the application:
```bash
cd app
uvicorn main:app --reload
```

5. Open http://127.0.0.1:8000

## 🌐 Deployment

### Deploy to Render (Free)

1. Push to GitHub
2. Go to [render.com](https://render.com)
3. Create new Web Service
4. Connect your GitHub repo
5. Set environment variables (GEMINI_API_KEY, GROQ_API_KEY)
6. Deploy!

## 📄 License

MIT License
