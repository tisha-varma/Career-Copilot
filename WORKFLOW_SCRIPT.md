# Career Copilot AI - Step-by-Step Workflow Script
## Narration for Screen Recording

---

# 🎬 WORKFLOW NARRATION SCRIPT

---

## FLOW 1: RESUME UPLOAD & ANALYSIS
### What happens when you click "Analyze Resume"

---

**[SCREEN: Home Page - http://127.0.0.1:8000]**

> "This is the Career Copilot AI home page. Let me upload a resume and show you exactly what happens in the backend."

**[ACTION: Select PDF file]**

> "I'm selecting a PDF resume file. The frontend uses a drag-and-drop interface built with Tailwind CSS."

**[ACTION: Select role - "Machine Learning Engineer"]**

> "I'm selecting the target role. This role will be used to compare against the resume."

**[ACTION: Click "Analyze Resume"]**

> "Now when I click 'Analyze Resume', here's exactly what happens in the backend..."

---

### BACKEND PROCESS - STEP BY STEP:

> "**STEP 1: File Upload & Parsing**
> 
> The PDF file is sent to our FastAPI server at the `/analyze` endpoint.
> 
> ```
> Technology: FastAPI (Python web framework)
> File: main.py
> ```
> 
> The server receives the PDF as bytes and passes it to pdfplumber for text extraction.
> 
> ```
> Technology: pdfplumber
> File: resume_parser.py
> Input: PDF bytes
> Output: Plain text string (entire resume content)
> ```
> 
> This converts the visual PDF into machine-readable text that our AI can understand."

---

> "**STEP 2: Store in Session**
> 
> The extracted text is stored in an in-memory session dictionary.
> 
> ```python
> session_data["resume_text"] = extracted_text
> session_data["role"] = "Machine Learning Engineer"
> ```
> 
> This allows other features like Cover Letter and Interview Prep to access the resume later without re-uploading."

---

> "**STEP 3: AI Analysis Pipeline (4-Step Agentic Process)**
> 
> Now comes the core AI analysis. We use a multi-step agentic pipeline:
> 
> ```
> Technology: Google Gemini API (gemini-1.5-flash)
> File: agent.py
> Architecture: Multi-step reasoning with context passing
> ```

> **Step 3.1: Resume Understanding**
> ```
> Input: Raw resume text
> Prompt: "Extract skills, education, experience level, and strengths"
> LLM Call: Gemini API
> Output: JSON { skills: [...], education_level: "Bachelor's", experience_level: "Entry", strengths: [...] }
> ```
> This first LLM call extracts structured information from unstructured text.

> **Step 3.2: Role Fit Analysis**
> ```
> Input: Extracted skills + Target role ("Machine Learning Engineer")
> Prompt: "Compare skills against role requirements. What's missing?"
> LLM Call: Gemini API
> Output: JSON { role_fit_score: 75, missing_core_skills: ["TensorFlow", "MLOps"], missing_supporting_skills: ["Docker"] }
> ```
> The second call compares extracted skills against what the role requires.

> **Step 3.3: Learning Roadmap Generation**
> ```
> Input: Missing skills list
> Prompt: "Create a prioritized learning roadmap"
> LLM Call: Gemini API
> Output: JSON { roadmap: [{ skill: "TensorFlow", priority: "High", time: "2 months", outcome: "..." }] }
> ```
> Third call creates a personalized learning plan.

> **Step 3.4: Reflection (Self-Evaluation)**
> ```
> Input: Score + Roadmap count
> Prompt: "Is this roadmap sufficient? Evaluate your own output."
> LLM Call: Gemini API
> Output: JSON { status: "sufficient", reason: "Covers all critical gaps" }
> ```
> The final call evaluates whether the generated roadmap is adequate - this is what makes it 'agentic'."

---

> "**STEP 4: Enrich with Additional Data**
> 
> After AI analysis, we add supplementary features:
> 
> ```
> YouTube Recommendations:
> Technology: Pre-curated video database
> File: youtube_search.py
> Input: Skills from roadmap
> Output: Relevant tutorial videos
> 
> Job Search URLs:
> Technology: URL encoding
> File: job_search.py
> Input: Target role
> Output: LinkedIn, Indeed, Glassdoor search links
> 
> Interview Questions:
> Technology: Pre-defined question bank
> File: interview_prep.py
> Input: Target role
> Output: Technical + Behavioral questions
> ```"

---

> "**STEP 5: Render Results Page**
> 
> Finally, all data is passed to the Jinja2 template engine:
> 
> ```
> Technology: Jinja2 templating
> File: templates/result.html
> Styling: Tailwind CSS
> 
> Data passed to template:
> - role_fit_score (number)
> - strengths (array)
> - skill_gaps (object with core/supporting)
> - roadmap (array of learning items)
> - youtube_recommendations (array)
> - job_search_urls (object)
> ```
> 
> The HTML is generated server-side and sent to the browser."

---

**[SCREEN: Results Page appears]**

> "And here's the results page! Let me walk through what's displayed:
> 
> - **Role Fit Score**: 75% - calculated by comparing your skills to role requirements
> - **Your Strengths**: Skills detected that match the role
> - **Skill Gaps**: What you need to learn, split into Core (critical) and Supporting
> - **Learning Roadmap**: Prioritized learning plan with time estimates
> - **YouTube Videos**: Curated tutorials for each gap skill
> - **Navigation Cards**: Links to Jobs, Interview Prep, and Cover Letter generator"

---

## FLOW 2: COVER LETTER GENERATION
### What happens when you click "Generate Cover Letter"

---

**[SCREEN: Click on "Cover Letter Generator" card]**

> "Now let me show you the Cover Letter Generator - this is where our LLaMA 3.1 and embeddings system really shines."

**[SCREEN: Cover Letter Form]**

> "I'll fill in:
> - Name: Tisha Varma
> - Company: Google
> - Position: Machine Learning Engineer
> - Job Description: [paste sample JD]"

**[ACTION: Click "Generate Cover Letter"]**

> "When I click Generate, here's what happens..."

---

### BACKEND PROCESS - STEP BY STEP:

> "**STEP 1: Retrieve Resume from Session**
> 
> ```python
> resume_text = session_data.get("resume_text")
> # Gets the resume that was uploaded earlier
> ```"

---

> "**STEP 2: Create Resume Embeddings**
> 
> ```
> Technology: sentence-transformers (BGE-Large-en-v1.5)
> File: llama_analyzer.py
> 
> Process:
> 1. Split resume into chunks (by sections/paragraphs)
> 2. Each chunk → 1024-dimensional vector
> 3. Store vectors in ChromaDB
> ```
> 
> ```python
> from sentence_transformers import SentenceTransformer
> 
> model = SentenceTransformer('BAAI/bge-large-en-v1.5')
> chunks = chunk_resume(resume_text)  # ["Project 1...", "Skills...", "Experience..."]
> embeddings = model.encode(chunks)   # [[0.1, 0.3, ...], [0.2, 0.5, ...], ...]
> ```
> 
> BGE-Large converts text into mathematical vectors where similar meanings are close together."

---

> "**STEP 3: Store Embeddings in ChromaDB**
> 
> ```
> Technology: ChromaDB (vector database)
> Storage: In-memory
> 
> collection.add(
>     documents=chunks,      # Original text
>     embeddings=embeddings, # 1024-dim vectors
>     ids=["chunk_0", "chunk_1", ...]
> )
> ```
> 
> ChromaDB allows us to search by similarity, not just keywords."

---

> "**STEP 4: Semantic Search for Relevant Sections**
> 
> ```
> Input: Job description
> Query: "Python ML experience TensorFlow computer vision"
> 
> Process:
> 1. Embed the job description
> 2. Search ChromaDB for similar resume chunks
> 3. Return top 5 most relevant sections
> ```
> 
> ```python
> # Find resume sections matching job requirements
> relevant_projects = semantic_search(collection, "ML projects", n_results=3)
> relevant_skills = semantic_search(collection, "Python TensorFlow", n_results=3)
> relevant_experience = semantic_search(collection, "work experience", n_results=3)
> ```
> 
> This is called RAG - Retrieval Augmented Generation. We RETRIEVE relevant context BEFORE generating."

---

> "**STEP 5: Extract Structured Data via LLaMA**
> 
> ```
> Technology: LLaMA 3.1 70B via Groq API
> File: llama_analyzer.py
> 
> Prompt to LLaMA:
> "Extract from this resume:
> - projects (name, description, technologies)
> - experience (role, company, achievements)
> - skills (programming, frameworks, tools)
> Return as JSON."
> 
> Output:
> {
>   "projects": [
>     {"name": "HerDefenders", "technologies": ["ML", "OpenCV", "Python"]},
>     {"name": "PharmaMate", "technologies": ["OCR", "ML"]}
>   ],
>   "skills": {"programming": ["Python", "Java"], ...}
> }
> ```
> 
> LLaMA understands context - it knows 'HerDefenders' is a project name, not random text."

---

> "**STEP 6: Generate Cover Letter via LLaMA**
> 
> ```
> Technology: LLaMA 3.1 70B
> 
> Prompt includes:
> - Candidate name
> - Company & Position
> - RELEVANT resume sections (from Step 4)
> - STRUCTURED data (from Step 5)
> - Job description
> 
> Instructions:
> "Write a cover letter mentioning:
> - SPECIFIC projects: HerDefenders, PharmaMate
> - ACTUAL technologies: Python, OpenCV, TensorFlow
> - REAL achievements: Google Girl Hackathon Finalist"
> ```
> 
> Because we fed LLaMA with specific, relevant context, it generates accurate, grounded content."

---

> "**STEP 7: Render Cover Letter Page**
> 
> ```
> Technology: Jinja2
> File: templates/cover_letter.html
> 
> The generated cover letter text is displayed in a preview box.
> User can click "Download PDF" to get a formatted PDF.
> ```"

---

**[SCREEN: Cover Letter displayed]**

> "Look at the generated cover letter! It specifically mentions:
> - 'HerDefenders' project with ML and OpenCV
> - 'PharmaMate' with OCR technology
> - Google Girl Hackathon Finalist achievement
> 
> This is NOT generic - it's pulled directly from the resume using semantic search and LLaMA understanding."

---

## FLOW 3: PDF DOWNLOAD
### What happens when you click "Download PDF"

---

**[ACTION: Click "Download PDF"]**

> "**PDF Generation Process:**
> 
> ```
> Technology: ReportLab
> File: pdf_generator.py
> 
> Process:
> 1. Take cover letter text
> 2. Apply professional formatting (fonts, margins, spacing)
> 3. Generate PDF in memory
> 4. Return as downloadable response
> ```
> 
> ```python
> from reportlab.platypus import SimpleDocTemplate, Paragraph
> 
> doc = SimpleDocTemplate(buffer, pagesize=letter)
> story = [
>     Paragraph(candidate_name, header_style),
>     Paragraph(cover_letter_text, body_style)
> ]
> doc.build(story)
> # Returns PDF bytes
> ```"

---

## FLOW 4: INTERVIEW QUESTIONS
### What happens on the Interview Prep page

---

**[SCREEN: Navigate to Interview Prep]**

> "The Interview Prep page also uses LLaMA + embeddings:
> 
> **Process:**
> 
> ```
> 1. Semantic search: Find project and experience chunks
> 2. LLaMA extraction: Get structured resume info
> 3. LLaMA generation: Create specific questions like:
>    - "Tell me about your HerDefenders project. What challenges did you face with OpenCV?"
>    - "How did you implement OCR in PharmaMate?"
> ```
> 
> Questions reference ACTUAL projects and technologies, not generic placeholders."

---

## TECHNOLOGY SUMMARY

---

> "To summarize the technologies used at each step:

| Action | Technology | Purpose |
|--------|------------|---------|
| Upload PDF | FastAPI | Handle HTTP file upload |
| Extract text | pdfplumber | PDF → plain text |
| AI Analysis | Gemini API | 4-step reasoning pipeline |
| Store resume | In-memory session | Cross-feature access |
| Create embeddings | BGE-Large | Text → 1024-dim vectors |
| Store vectors | ChromaDB | Semantic search capability |
| Find relevant sections | Cosine similarity | Match JD to resume |
| Extract structure | LLaMA 3.1 70B | JSON extraction |
| Generate content | LLaMA 3.1 70B | Cover letter/questions |
| Generate PDF | ReportLab | Cover letter PDF |
| Render HTML | Jinja2 | Template engine |
| Styling | Tailwind CSS | Modern UI |

> This multi-technology stack ensures accuracy, speed, and reliability with fallback mechanisms at each layer."

---

## COMPLETE DATA FLOW DIAGRAM

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           USER CLICKS "ANALYZE RESUME"                           │
└─────────────────────────────────────────────┬───────────────────────────────────┘
                                              │
                                              ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│ STEP 1: PDF PARSING                                                              │
│ Technology: pdfplumber                                                          │
│ Input: PDF file (bytes)                                                         │
│ Output: Plain text string                                                       │
│ Time: ~0.5 seconds                                                              │
└─────────────────────────────────────────────┬───────────────────────────────────┘
                                              │
                                              ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│ STEP 2: RESUME UNDERSTANDING                                                     │
│ Technology: Gemini API (gemini-1.5-flash)                                       │
│ Input: Resume text + prompt                                                     │
│ Output: { skills, education, experience_level, strengths }                      │
│ Time: ~2 seconds                                                                │
└─────────────────────────────────────────────┬───────────────────────────────────┘
                                              │
                                              ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│ STEP 3: ROLE FIT ANALYSIS                                                        │
│ Technology: Gemini API                                                          │
│ Input: Skills + Target Role                                                     │
│ Output: { role_fit_score, missing_core_skills, missing_supporting_skills }      │
│ Time: ~2 seconds                                                                │
└─────────────────────────────────────────────┬───────────────────────────────────┘
                                              │
                                              ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│ STEP 4: LEARNING ROADMAP                                                         │
│ Technology: Gemini API                                                          │
│ Input: Missing skills                                                           │
│ Output: [{ skill, priority, time_estimate, outcome }]                           │
│ Time: ~2 seconds                                                                │
└─────────────────────────────────────────────┬───────────────────────────────────┘
                                              │
                                              ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│ STEP 5: REFLECTION                                                               │
│ Technology: Gemini API                                                          │
│ Input: Score + Roadmap                                                          │
│ Output: { status: "sufficient/insufficient", reason }                           │
│ Time: ~1 second                                                                 │
└─────────────────────────────────────────────┬───────────────────────────────────┘
                                              │
                                              ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│ STEP 6: ENRICH DATA                                                              │
│ • YouTube recommendations (youtube_search.py)                                   │
│ • Job search URLs (job_search.py)                                               │
│ • Interview questions (interview_prep.py)                                       │
│ Time: ~0.1 seconds                                                              │
└─────────────────────────────────────────────┬───────────────────────────────────┘
                                              │
                                              ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│ STEP 7: RENDER RESULTS                                                           │
│ Technology: Jinja2 + Tailwind CSS                                               │
│ Template: result.html                                                           │
│ Output: Formatted HTML page                                                     │
│ Time: ~0.1 seconds                                                              │
└─────────────────────────────────────────────┬───────────────────────────────────┘
                                              │
                                              ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           RESULTS PAGE DISPLAYED                                 │
│ Total Time: ~8-10 seconds                                                       │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## COVER LETTER FLOW DIAGRAM

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                      USER CLICKS "GENERATE COVER LETTER"                         │
└─────────────────────────────────────────────┬───────────────────────────────────┘
                                              │
                                              ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│ STEP 1: CREATE EMBEDDINGS                                                        │
│ Technology: BGE-Large (sentence-transformers)                                   │
│ Input: Resume text chunks                                                       │
│ Output: 1024-dimensional vectors                                                │
│ Time: ~3 seconds (first load), ~0.5s after                                      │
└─────────────────────────────────────────────┬───────────────────────────────────┘
                                              │
                                              ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│ STEP 2: STORE IN CHROMADB                                                        │
│ Technology: ChromaDB (in-memory vector DB)                                      │
│ Input: Chunks + Embeddings                                                      │
│ Output: Searchable collection                                                   │
│ Time: ~0.1 seconds                                                              │
└─────────────────────────────────────────────┬───────────────────────────────────┘
                                              │
                                              ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│ STEP 3: SEMANTIC SEARCH                                                          │
│ Technology: ChromaDB cosine similarity                                          │
│ Input: Job description                                                          │
│ Output: Top 5 most relevant resume sections                                     │
│ Time: ~0.1 seconds                                                              │
└─────────────────────────────────────────────┬───────────────────────────────────┘
                                              │
                                              ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│ STEP 4: EXTRACT STRUCTURE                                                        │
│ Technology: LLaMA 3.1 70B (Groq API)                                            │
│ Input: Resume text                                                              │
│ Output: JSON { projects, skills, experience, achievements }                     │
│ Time: ~2 seconds                                                                │
└─────────────────────────────────────────────┬───────────────────────────────────┘
                                              │
                                              ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│ STEP 5: GENERATE COVER LETTER                                                    │
│ Technology: LLaMA 3.1 70B (Groq API)                                            │
│ Input: Relevant sections + Structured data + Job description                    │
│ Output: Personalized cover letter text                                          │
│ Time: ~3 seconds                                                                │
└─────────────────────────────────────────────┬───────────────────────────────────┘
                                              │
                                              ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│ STEP 6: RENDER & OPTION TO DOWNLOAD                                              │
│ Preview: Jinja2 template                                                        │
│ Download: ReportLab PDF generation                                              │
│ Time: ~0.5 seconds                                                              │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

**END OF WORKFLOW SCRIPT**
