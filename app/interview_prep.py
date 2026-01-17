"""
Interview Prep Module
Curated interview questions and tips for each role
"""


INTERVIEW_QUESTIONS = {
    "Frontend Developer": {
        "technical": [
            {
                "question": "Explain the difference between var, let, and const in JavaScript.",
                "tip": "Focus on scope (function vs block), hoisting, and reassignment rules.",
                "difficulty": "Easy"
            },
            {
                "question": "What is the Virtual DOM and how does React use it?",
                "tip": "Explain the diffing algorithm and why it improves performance.",
                "difficulty": "Medium"
            },
            {
                "question": "How would you optimize a slow-loading web page?",
                "tip": "Mention lazy loading, code splitting, image optimization, caching, and CDNs.",
                "difficulty": "Medium"
            },
            {
                "question": "Explain CSS Flexbox vs Grid. When would you use each?",
                "tip": "Flexbox for 1D layouts, Grid for 2D. Give specific use cases.",
                "difficulty": "Easy"
            },
            {
                "question": "What are React Hooks? Explain useState and useEffect.",
                "tip": "Describe how they replace class lifecycle methods with examples.",
                "difficulty": "Medium"
            }
        ],
        "behavioral": [
            {
                "question": "Tell me about a challenging UI bug you fixed.",
                "tip": "Use STAR method: Situation, Task, Action, Result.",
                "difficulty": "Medium"
            },
            {
                "question": "How do you stay updated with frontend technologies?",
                "tip": "Mention blogs, conferences, side projects, Twitter/X follows.",
                "difficulty": "Easy"
            }
        ]
    },
    "Backend Developer": {
        "technical": [
            {
                "question": "Explain RESTful API design principles.",
                "tip": "Cover HTTP methods, status codes, statelessness, and resource naming.",
                "difficulty": "Medium"
            },
            {
                "question": "How do you handle database optimization?",
                "tip": "Discuss indexing, query optimization, caching, and denormalization.",
                "difficulty": "Medium"
            },
            {
                "question": "What is the difference between SQL and NoSQL databases?",
                "tip": "Compare structure, scalability, ACID vs BASE, and use cases.",
                "difficulty": "Easy"
            },
            {
                "question": "Explain microservices architecture vs monolithic.",
                "tip": "Discuss pros/cons, when to use each, and communication patterns.",
                "difficulty": "Hard"
            },
            {
                "question": "How would you design a rate limiter?",
                "tip": "Mention token bucket, sliding window, and distributed considerations.",
                "difficulty": "Hard"
            }
        ],
        "behavioral": [
            {
                "question": "Describe a time you improved system performance.",
                "tip": "Quantify the improvement with metrics (e.g., 50% faster).",
                "difficulty": "Medium"
            },
            {
                "question": "How do you handle production incidents?",
                "tip": "Discuss monitoring, alerting, debugging, and post-mortems.",
                "difficulty": "Medium"
            }
        ]
    },
    "Data Analyst": {
        "technical": [
            {
                "question": "Write a SQL query to find the second highest salary.",
                "tip": "Use subquery, LIMIT OFFSET, or window functions (DENSE_RANK).",
                "difficulty": "Medium"
            },
            {
                "question": "How do you handle missing data in a dataset?",
                "tip": "Discuss deletion, imputation, and when to use each approach.",
                "difficulty": "Medium"
            },
            {
                "question": "Explain the difference between correlation and causation.",
                "tip": "Use a real-world example like ice cream sales and drowning.",
                "difficulty": "Easy"
            },
            {
                "question": "What metrics would you track for an e-commerce website?",
                "tip": "Mention conversion rate, AOV, cart abandonment, and customer lifetime value.",
                "difficulty": "Medium"
            },
            {
                "question": "How do you present data findings to non-technical stakeholders?",
                "tip": "Focus on storytelling, visualizations, and actionable insights.",
                "difficulty": "Easy"
            }
        ],
        "behavioral": [
            {
                "question": "Tell me about an analysis that drove a business decision.",
                "tip": "Quantify the business impact (revenue, cost savings, efficiency).",
                "difficulty": "Medium"
            },
            {
                "question": "How do you prioritize multiple data requests?",
                "tip": "Discuss stakeholder alignment, impact assessment, and deadlines.",
                "difficulty": "Easy"
            }
        ]
    },
    "Full Stack Developer": {
        "technical": [
            {
                "question": "Design the architecture for a social media app.",
                "tip": "Cover frontend, backend, database, caching, and CDN layers.",
                "difficulty": "Hard"
            },
            {
                "question": "How do you ensure security in a web application?",
                "tip": "Mention HTTPS, input validation, CSRF, XSS, and authentication.",
                "difficulty": "Medium"
            },
            {
                "question": "Explain the request-response cycle in a web app.",
                "tip": "Walk through DNS, server, routing, controller, view, and response.",
                "difficulty": "Medium"
            },
            {
                "question": "What is the difference between authentication and authorization?",
                "tip": "Auth = who you are, Authz = what you can do. Give JWT/OAuth examples.",
                "difficulty": "Easy"
            },
            {
                "question": "How would you implement real-time features?",
                "tip": "Discuss WebSockets, Server-Sent Events, and polling trade-offs.",
                "difficulty": "Medium"
            }
        ],
        "behavioral": [
            {
                "question": "Describe a project where you worked on both frontend and backend.",
                "tip": "Highlight your ability to understand the full system.",
                "difficulty": "Easy"
            },
            {
                "question": "How do you decide between building vs buying a solution?",
                "tip": "Discuss time, cost, maintenance, and customization needs.",
                "difficulty": "Medium"
            }
        ]
    },
    "Machine Learning Engineer": {
        "technical": [
            {
                "question": "Explain the bias-variance tradeoff.",
                "tip": "Use graphs and examples of underfitting vs overfitting.",
                "difficulty": "Medium"
            },
            {
                "question": "How do you handle imbalanced datasets?",
                "tip": "Mention oversampling, undersampling, SMOTE, and class weights.",
                "difficulty": "Medium"
            },
            {
                "question": "Explain the difference between bagging and boosting.",
                "tip": "Bagging = parallel (Random Forest), Boosting = sequential (XGBoost).",
                "difficulty": "Medium"
            },
            {
                "question": "How would you deploy an ML model to production?",
                "tip": "Cover containerization, serving (Flask/FastAPI), monitoring, and A/B testing.",
                "difficulty": "Hard"
            },
            {
                "question": "What is gradient descent and how does it work?",
                "tip": "Explain learning rate, local minima, and variants (SGD, Adam).",
                "difficulty": "Medium"
            }
        ],
        "behavioral": [
            {
                "question": "Tell me about a model that didn't perform well. What did you do?",
                "tip": "Show debugging skills: data quality, features, model selection.",
                "difficulty": "Medium"
            },
            {
                "question": "How do you explain ML concepts to non-technical stakeholders?",
                "tip": "Use analogies and focus on business impact, not math.",
                "difficulty": "Easy"
            }
        ]
    },
    "DevOps Engineer": {
        "technical": [
            {
                "question": "Explain CI/CD pipeline. What tools have you used?",
                "tip": "Cover stages, automation, testing, and deployment strategies.",
                "difficulty": "Medium"
            },
            {
                "question": "What is Infrastructure as Code? Which tools do you prefer?",
                "tip": "Explain Terraform, CloudFormation, or Pulumi with examples.",
                "difficulty": "Medium"
            },
            {
                "question": "How do you monitor application health?",
                "tip": "Mention metrics, logs, traces, and tools (Prometheus, Grafana, ELK).",
                "difficulty": "Medium"
            },
            {
                "question": "Explain containerization vs virtualization.",
                "tip": "Discuss resource efficiency, isolation, and use cases.",
                "difficulty": "Easy"
            },
            {
                "question": "How would you handle a production outage?",
                "tip": "Walk through incident response: detect, mitigate, communicate, post-mortem.",
                "difficulty": "Hard"
            }
        ],
        "behavioral": [
            {
                "question": "Describe a time you automated a manual process.",
                "tip": "Quantify time saved and error reduction.",
                "difficulty": "Easy"
            },
            {
                "question": "How do you balance speed vs reliability?",
                "tip": "Discuss SLOs, error budgets, and progressive rollouts.",
                "difficulty": "Medium"
            }
        ]
    },
    "Product Manager": {
        "technical": [
            {
                "question": "How do you prioritize features on a product roadmap?",
                "tip": "Mention frameworks like RICE, MoSCoW, or value vs effort.",
                "difficulty": "Medium"
            },
            {
                "question": "How would you measure the success of a new feature?",
                "tip": "Define success metrics before launch, track leading/lagging indicators.",
                "difficulty": "Medium"
            },
            {
                "question": "Walk me through how you would launch a new product.",
                "tip": "Cover research, MVP, testing, launch, and iteration.",
                "difficulty": "Hard"
            },
            {
                "question": "How do you handle conflicting stakeholder priorities?",
                "tip": "Discuss data-driven decisions, alignment sessions, and tradeoffs.",
                "difficulty": "Medium"
            },
            {
                "question": "Describe your approach to user research.",
                "tip": "Cover qualitative (interviews) and quantitative (surveys, analytics).",
                "difficulty": "Medium"
            }
        ],
        "behavioral": [
            {
                "question": "Tell me about a product you launched. What was the result?",
                "tip": "Use metrics: user adoption, revenue, retention improvements.",
                "difficulty": "Medium"
            },
            {
                "question": "Describe a time you had to say no to a stakeholder.",
                "tip": "Focus on how you communicated the tradeoff.",
                "difficulty": "Medium"
            }
        ]
    },
    "UX Designer": {
        "technical": [
            {
                "question": "Walk me through your design process.",
                "tip": "Cover research, ideation, prototyping, testing, and iteration.",
                "difficulty": "Medium"
            },
            {
                "question": "How do you validate design decisions?",
                "tip": "Discuss user testing, A/B tests, analytics, and heuristic evaluation.",
                "difficulty": "Medium"
            },
            {
                "question": "Explain the difference between UX and UI.",
                "tip": "UX = overall experience, UI = visual interface. They overlap.",
                "difficulty": "Easy"
            },
            {
                "question": "How do you design for accessibility?",
                "tip": "Mention WCAG guidelines, color contrast, screen readers, and keyboard nav.",
                "difficulty": "Medium"
            },
            {
                "question": "How do you handle design critique?",
                "tip": "Show openness to feedback while defending user-backed decisions.",
                "difficulty": "Easy"
            }
        ],
        "behavioral": [
            {
                "question": "Tell me about a design that didn't work. What did you learn?",
                "tip": "Be honest about failure and show growth.",
                "difficulty": "Medium"
            },
            {
                "question": "How do you collaborate with developers?",
                "tip": "Discuss handoff, design systems, and iterative feedback.",
                "difficulty": "Easy"
            }
        ]
    }
}


def get_interview_questions(target_role: str) -> dict:
    """
    Get interview questions for the target role.
    """
    default_questions = {
        "technical": [
            {
                "question": "Tell me about your technical background.",
                "tip": "Highlight relevant skills and projects.",
                "difficulty": "Easy"
            },
            {
                "question": "How do you approach learning new technologies?",
                "tip": "Show curiosity and self-learning ability.",
                "difficulty": "Easy"
            },
            {
                "question": "Describe a challenging project you worked on.",
                "tip": "Use STAR method and highlight your contributions.",
                "difficulty": "Medium"
            }
        ],
        "behavioral": [
            {
                "question": "Why are you interested in this role?",
                "tip": "Connect your skills to the job requirements.",
                "difficulty": "Easy"
            },
            {
                "question": "Where do you see yourself in 5 years?",
                "tip": "Show ambition while being realistic.",
                "difficulty": "Easy"
            }
        ]
    }
    
    return INTERVIEW_QUESTIONS.get(target_role, default_questions)


def get_interview_tips() -> list:
    """
    General interview tips.
    """
    return [
        "Research the company before the interview",
        "Prepare questions to ask the interviewer",
        "Use the STAR method for behavioral questions",
        "Practice coding problems if it's a technical role",
        "Follow up with a thank-you email within 24 hours"
    ]


def generate_resume_questions(resume_text: str, strengths: list = None, skill_gaps: dict = None) -> list:
    """
    Generate interview questions based on the resume content.
    Looks for specific projects, technologies, and experiences.
    """
    questions = []
    resume_lower = resume_text.lower()
    
    # Check for common technologies/projects and generate questions
    tech_patterns = {
        "react": {
            "question": "I see you have experience with React. Can you walk me through a complex component you built?",
            "tip": "Describe the component's purpose, state management, and any performance optimizations you made."
        },
        "python": {
            "question": "Tell me about a Python project you're most proud of.",
            "tip": "Focus on the problem it solved, architecture decisions, and any libraries you used."
        },
        "machine learning": {
            "question": "What ML model did you build and how did you evaluate its performance?",
            "tip": "Discuss metrics, validation approach, and how you handled overfitting."
        },
        "aws": {
            "question": "Describe your experience with AWS. What services have you used?",
            "tip": "Mention specific services, infrastructure setup, and cost optimization if applicable."
        },
        "docker": {
            "question": "How have you used Docker in your projects?",
            "tip": "Explain containerization benefits, Dockerfile structure, and orchestration if any."
        },
        "api": {
            "question": "Tell me about an API you designed or worked with.",
            "tip": "Discuss endpoints, authentication, error handling, and documentation."
        },
        "database": {
            "question": "What databases have you worked with? How did you optimize queries?",
            "tip": "Mention specific databases, indexing strategies, and query optimization techniques."
        },
        "team": {
            "question": "Describe a successful team project. What was your role?",
            "tip": "Highlight collaboration, communication, and your specific contributions."
        },
        "lead": {
            "question": "Tell me about your leadership experience.",
            "tip": "Discuss team size, challenges you faced, and how you motivated your team."
        },
        "intern": {
            "question": "What did you learn during your internship?",
            "tip": "Focus on technical skills gained, projects completed, and professional growth."
        },
        "project": {
            "question": "Walk me through the most challenging project on your resume.",
            "tip": "Use STAR method: explain the challenge, your approach, and the outcome."
        },
        "agile": {
            "question": "How do you work in an Agile environment?",
            "tip": "Discuss sprints, standups, retrospectives, and how you adapt to changing requirements."
        },
        "git": {
            "question": "Describe your Git workflow and collaboration practices.",
            "tip": "Mention branching strategy, code reviews, and handling merge conflicts."
        }
    }
    
    # Check resume for tech patterns
    found_patterns = []
    for pattern, qa in tech_patterns.items():
        if pattern in resume_lower and pattern not in found_patterns:
            questions.append(qa)
            found_patterns.append(pattern)
            if len(questions) >= 5:  # Limit to 5 resume-based questions
                break
    
    # Add questions based on strengths
    if strengths and len(questions) < 5:
        for strength in strengths[:2]:
            questions.append({
                "question": f"Your resume mentions '{strength}'. Can you give me a specific example of this?",
                "tip": "Prepare a concrete story that demonstrates this strength with measurable results."
            })
    
    # Add questions based on skill gaps (what you're learning)
    if skill_gaps and len(questions) < 6:
        core_gaps = skill_gaps.get("core", [])[:1]
        for gap in core_gaps:
            questions.append({
                "question": f"This role requires {gap}. How do you plan to develop this skill?",
                "tip": "Show initiative by mentioning courses, projects, or self-study plans you've started."
            })
    
    # If no patterns found, add generic resume questions
    if not questions:
        questions = [
            {
                "question": "Walk me through your resume. What's your career story?",
                "tip": "Create a narrative that connects your experiences to this role."
            },
            {
                "question": "What's the most impactful project you've worked on?",
                "tip": "Choose a project relevant to the role and quantify your impact."
            },
            {
                "question": "What technical skills are you currently developing?",
                "tip": "Show continuous learning and mention specific resources you're using."
            }
        ]
    
    return questions

