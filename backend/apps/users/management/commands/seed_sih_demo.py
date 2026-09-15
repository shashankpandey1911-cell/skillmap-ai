"""Seed comprehensive demo data for Smart India Hackathon presentation.

Run:  python manage.py seed_sih_demo
      python manage.py seed_sih_demo --reset    (wipe and reseed everything)

Creates:
  - 10 students with diverse skill profiles
  - 5 professors
  - 5 assessments with 10 questions each (50 total)
  - 20 applications across students at various pipeline stages
  - Career feedback for terminal (rejected/selected) decisions

Assumes the base catalog, careers, opportunities and learning resources are
already seeded by the standard seed_demo command (or this command calls them).
"""

import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.applications.models import Application
from apps.applications.seed_data import ensure_demo_applications
from apps.assessments.models import Assessment, Option, Question
from apps.assessments.seed_data import ensure_demo_assessments
from apps.careers.seed_data import ensure_demo_careers
from apps.feedback.seed_data import ensure_demo_feedback
from apps.learning.seed_data import ensure_demo_resources
from apps.opportunities.models import Opportunity
from apps.opportunities.seed_data import ensure_demo_opportunities
from apps.skills.models import Skill, UserSkill
from apps.skills.seed_data import ensure_skill_catalog
from apps.students.models import Certification, Project, StudentProfile

User = get_user_model()

# ---------------------------------------------------------------------------
# Professors
# ---------------------------------------------------------------------------
DEMO_PROFESSORS = [
    {
        "username": "prof_anita",
        "email": "professor@skillmap.ai",
        "first_name": "Anita",
        "last_name": "Desai",
        "password": "Prof@2026",
        "role": "PROFESSOR",
    },
    {
        "username": "prof_vikram",
        "email": "vikram.sharma@demo.edu",
        "first_name": "Vikram",
        "last_name": "Sharma",
        "password": "Prof@2026",
        "role": "PROFESSOR",
    },
    {
        "username": "prof_meera",
        "email": "meera.nair@demo.edu",
        "first_name": "Meera",
        "last_name": "Nair",
        "password": "Prof@2026",
        "role": "PROFESSOR",
    },
    {
        "username": "prof_arjun",
        "email": "arjun.reddy@demo.edu",
        "first_name": "Arjun",
        "last_name": "Reddy",
        "password": "Prof@2026",
        "role": "PROFESSOR",
    },
    {
        "username": "prof_sunita",
        "email": "sunita.gupta@demo.edu",
        "first_name": "Sunita",
        "last_name": "Gupta",
        "password": "Prof@2026",
        "role": "PROFESSOR",
    },
]

# ---------------------------------------------------------------------------
# Students — each has a unique career goal, skill mix and experience level
# ---------------------------------------------------------------------------
DEMO_STUDENTS = [
    {
        "username": "rohan_mehta",
        "email": "student@skillmap.ai",
        "first_name": "Rohan",
        "last_name": "Mehta",
        "password": "Student@2026",
        "profile": {
            "college": "National Institute of Technology, Trichy",
            "course": "B.Tech Computer Science",
            "branch": "Computer Science and Engineering",
            "year": 3,
            "cgpa": 8.6,
            "semester": 5,
            "achievements": "Winner, Smart India Hackathon 2025; Dean's List (3 semesters)",
            "career_goal": "Software Development Engineer at a top product company",
            "preferred_domain": "Full-stack / AI-ML",
            "interests": "Machine learning, open source, competitive programming",
            "about": "CSE undergraduate passionate about building products that solve real problems.",
        },
        "skills": [
            ("Python", 5, "ADVANCED"),
            ("Django", 4, "ADVANCED"),
            ("React", 4, "INTERMEDIATE"),
            ("SQL", 4, "INTERMEDIATE"),
            ("PostgreSQL", 3, "INTERMEDIATE"),
            ("Git", 5, "ADVANCED"),
            ("Docker", 3, "INTERMEDIATE"),
            ("Machine Learning", 4, "INTERMEDIATE"),
            ("Data Visualization", 3, "INTERMEDIATE"),
            ("Communication", 4, "ADVANCED"),
        ],
        "projects": [
            {
                "name": "SkillMap AI",
                "description": "Career-guidance platform that scores student skills, finds gaps and matches careers.",
                "technologies": "React, Django REST Framework, PostgreSQL",
                "github_url": "https://github.com/rohanmehta/skillmap",
            },
            {
                "name": "Campus Placement Tracker",
                "description": "Web app for students to track drives, deadlines and preparation progress.",
                "technologies": "React, Node.js, MongoDB",
                "github_url": "https://github.com/rohanmehta/placement-tracker",
            },
        ],
        "certifications": [
            {
                "name": "AWS Certified Cloud Practitioner",
                "provider": "Amazon Web Services",
                "credential_url": "https://www.credly.com/badges/aws-cp",
            },
            {
                "name": "Python for Everybody Specialization",
                "provider": "Coursera / University of Michigan",
            },
        ],
    },
    {
        "username": "priya_nair",
        "email": "priya.nair@demo.edu",
        "first_name": "Priya",
        "last_name": "Nair",
        "password": "Student@2026",
        "profile": {
            "college": "Indian Institute of Technology, Bombay",
            "course": "B.Tech Electrical Engineering",
            "branch": "Electrical Engineering",
            "year": 3,
            "cgpa": 9.1,
            "semester": 5,
            "achievements": "ACM-ICPC Regionalist; Google Summer of Code contributor",
            "career_goal": "AI/ML Engineer at a research-focused company",
            "preferred_domain": "AI/ML / Data Science",
            "interests": "Deep learning, NLP, computer vision, open-source ML tools",
            "about": "Research-oriented student with published paper in NLP.",
        },
        "skills": [
            ("Python", 5, "EXPERT"),
            ("Machine Learning", 5, "ADVANCED"),
            ("Deep Learning", 4, "ADVANCED"),
            ("PyTorch", 4, "ADVANCED"),
            ("Pandas", 4, "ADVANCED"),
            ("Statistics", 5, "ADVANCED"),
            ("SQL", 3, "INTERMEDIATE"),
            ("Git", 4, "ADVANCED"),
            ("Communication", 4, "ADVANCED"),
            ("Problem Solving", 5, "EXPERT"),
        ],
        "projects": [
            {
                "name": "Sentiment Analysis Pipeline",
                "description": "End-to-end NLP pipeline for multilingual sentiment analysis using transformer models.",
                "technologies": "Python, PyTorch, Hugging Face, FastAPI",
                "github_url": "https://github.com/priya-nair/sentiment-pipeline",
            },
            {
                "name": "Vision Transformer Fine-tuner",
                "description": "Web tool for fine-tuning ViT models on custom image datasets without coding.",
                "technologies": "Python, PyTorch, Gradio, Hugging Face",
                "github_url": "https://github.com/priya-nair/vit-finetuner",
            },
        ],
        "certifications": [
            {
                "name": "Deep Learning Specialization",
                "provider": "Coursera / DeepLearning.AI",
            },
            {
                "name": "TensorFlow Developer Certificate",
                "provider": "Google",
                "credential_url": "https://www.credential.net/tf-dev",
            },
        ],
    },
    {
        "username": "arjun_reddy",
        "email": "arjun.r@demo.edu",
        "first_name": "Arjun",
        "last_name": "Reddy",
        "password": "Student@2026",
        "profile": {
            "college": "BITS Pilani",
            "course": "B.E. Computer Science",
            "branch": "Computer Science",
            "year": 2,
            "cgpa": 7.8,
            "semester": 3,
            "achievements": "Hackathon finalist at TechCrunch Disrupt",
            "career_goal": "Frontend Developer at a design-focused startup",
            "preferred_domain": "Frontend / UI Engineering",
            "interests": "Design systems, animation, accessibility, CSS art",
            "about": "Design-minded developer building beautiful, accessible interfaces.",
        },
        "skills": [
            ("JavaScript", 5, "ADVANCED"),
            ("React", 5, "ADVANCED"),
            ("TypeScript", 4, "ADVANCED"),
            ("CSS", 5, "EXPERT"),
            ("HTML", 5, "EXPERT"),
            ("Git", 4, "ADVANCED"),
            ("Figma", 4, "ADVANCED"),
            ("Python", 2, "BEGINNER"),
            ("Teamwork", 4, "ADVANCED"),
            ("Communication", 5, "ADVANCED"),
        ],
        "projects": [
            {
                "name": "Design System Starter Kit",
                "description": "Open-source React component library with Tailwind CSS, accessibility built-in.",
                "technologies": "React, TypeScript, Tailwind CSS, Storybook",
                "github_url": "https://github.com/arjun-reddy/design-kit",
            },
        ],
        "certifications": [
            {
                "name": "Meta Front-End Developer Professional Certificate",
                "provider": "Coursera / Meta",
            },
        ],
    },
    {
        "username": "sneha_patel",
        "email": "sneha.p@demo.edu",
        "first_name": "Sneha",
        "last_name": "Patel",
        "password": "Student@2026",
        "profile": {
            "college": "Delhi Technological University",
            "course": "B.Tech Information Technology",
            "branch": "Information Technology",
            "year": 4,
            "cgpa": 8.9,
            "semester": 7,
            "achievements": "Google Code-in mentor; hackathon winner at HackDTU",
            "career_goal": "Cloud/DevOps Engineer at a SaaS company",
            "preferred_domain": "Cloud / DevOps / SRE",
            "interests": "Cloud architecture, Kubernetes, automation, monitoring",
            "about": "Infrastructure enthusiast who loves automating everything.",
        },
        "skills": [
            ("AWS", 5, "ADVANCED"),
            ("Docker", 5, "ADVANCED"),
            ("Kubernetes", 4, "ADVANCED"),
            ("Linux", 5, "ADVANCED"),
            ("Git", 5, "ADVANCED"),
            ("Python", 4, "ADVANCED"),
            ("SQL", 3, "INTERMEDIATE"),
            ("Terraform", 4, "ADVANCED"),
            ("Problem Solving", 4, "ADVANCED"),
            ("Communication", 3, "INTERMEDIATE"),
        ],
        "projects": [
            {
                "name": "AutoScaler Pro",
                "description": "Kubernetes-based auto-scaling solution that adjusts pod counts based on custom metrics.",
                "technologies": "Kubernetes, Python, Prometheus, Grafana",
                "github_url": "https://github.com/sneha-patel/autoscaler-pro",
            },
            {
                "name": "Cloud Cost Optimizer",
                "description": "CLI tool that analyzes AWS spending and recommends rightsizing for EC2 and RDS.",
                "technologies": "Python, AWS SDK, Click",
                "github_url": "https://github.com/sneha-patel/cloud-cost",
            },
        ],
        "certifications": [
            {
                "name": "AWS Solutions Architect – Associate",
                "provider": "Amazon Web Services",
                "credential_url": "https://www.credly.com/badges/aws-saa",
            },
            {
                "name": "Certified Kubernetes Application Developer (CKAD)",
                "provider": "The Linux Foundation",
            },
        ],
    },
    {
        "username": "rahul_verma",
        "email": "rahul.v@demo.edu",
        "first_name": "Rahul",
        "last_name": "Verma",
        "password": "Student@2026",
        "profile": {
            "college": "VIT Vellore",
            "course": "B.Tech Computer Science",
            "branch": "Computer Science and Engineering",
            "year": 3,
            "cgpa": 8.2,
            "semester": 5,
            "achievements": "LeetCode 5-star rating; Codeforces Specialist",
            "career_goal": "Backend Developer at a high-scale fintech",
            "preferred_domain": "Backend / Distributed Systems",
            "interests": "System design, distributed systems, databases, DSA",
            "about": "Problem-solver at heart, building reliable backend systems.",
        },
        "skills": [
            ("Python", 4, "ADVANCED"),
            ("Java", 4, "ADVANCED"),
            ("SQL", 4, "ADVANCED"),
            ("Data Structures & Algorithms", 5, "EXPERT"),
            ("System Design", 3, "INTERMEDIATE"),
            ("Git", 4, "ADVANCED"),
            ("REST API", 4, "ADVANCED"),
            ("PostgreSQL", 3, "INTERMEDIATE"),
            ("Problem Solving", 5, "EXPERT"),
            ("Communication", 3, "INTERMEDIATE"),
        ],
        "projects": [
            {
                "name": "Rate Limiter Library",
                "description": "Distributed rate limiter using sliding window algorithm with Redis backend.",
                "technologies": "Python, Redis, asyncio",
                "github_url": "https://github.com/rahul-verma/rate-limiter",
            },
        ],
        "certifications": [
            {
                "name": "HackerRank Python (Intermediate)",
                "provider": "HackerRank",
            },
        ],
    },
    {
        "username": "ananya_singh",
        "email": "ananya.s@demo.edu",
        "first_name": "Ananya",
        "last_name": "Singh",
        "password": "Student@2026",
        "profile": {
            "college": "NIT Warangal",
            "course": "B.Tech Computer Science",
            "branch": "Computer Science",
            "year": 2,
            "cgpa": 8.5,
            "semester": 3,
            "achievements": "Hackathon winner at NITW HackFest",
            "career_goal": "Data Analyst at a consumer internet company",
            "preferred_domain": "Data Science / Analytics",
            "interests": "Data storytelling, visualization, statistics, business metrics",
            "about": "Numbers enthusiast turning raw data into actionable insights.",
        },
        "skills": [
            ("Python", 3, "INTERMEDIATE"),
            ("SQL", 4, "ADVANCED"),
            ("Pandas", 4, "ADVANCED"),
            ("Statistics", 4, "ADVANCED"),
            ("Data Visualization", 5, "ADVANCED"),
            ("Excel", 4, "ADVANCED"),
            ("Tableau", 3, "INTERMEDIATE"),
            ("Communication", 5, "ADVANCED"),
            ("Problem Solving", 3, "INTERMEDIATE"),
            ("Teamwork", 4, "ADVANCED"),
        ],
        "projects": [
            {
                "name": "E-Commerce Sales Dashboard",
                "description": "Interactive Tableau dashboard analyzing 2 years of sales data with YoY trends.",
                "technologies": "Tableau, SQL, Python",
                "github_url": "https://github.com/ananya-singh/sales-dashboard",
            },
        ],
        "certifications": [
            {
                "name": "Google Data Analytics Professional Certificate",
                "provider": "Coursera / Google",
            },
        ],
    },
    {
        "username": "karan_joshi",
        "email": "karan.j@demo.edu",
        "first_name": "Karan",
        "last_name": "Joshi",
        "password": "Student@2026",
        "profile": {
            "college": "IIIT Hyderabad",
            "course": "B.Tech Computer Science",
            "branch": "Computer Science",
            "year": 4,
            "cgpa": 9.3,
            "semester": 7,
            "achievements": "ACM-ICPC World Finalist; GSoC 2025",
            "career_goal": "Full-Stack Developer at a product company",
            "preferred_domain": "Full-stack / Web Development",
            "interests": "Web architecture, performance, testing, developer experience",
            "about": "Seasoned developer with full-stack experience across 4+ production apps.",
        },
        "skills": [
            ("JavaScript", 5, "EXPERT"),
            ("React", 5, "EXPERT"),
            ("Node.js", 5, "ADVANCED"),
            ("Python", 4, "ADVANCED"),
            ("Django", 4, "ADVANCED"),
            ("SQL", 4, "ADVANCED"),
            ("TypeScript", 5, "ADVANCED"),
            ("Git", 5, "EXPERT"),
            ("Docker", 4, "ADVANCED"),
            ("Communication", 4, "ADVANCED"),
        ],
        "projects": [
            {
                "name": "Real-Time Chat Platform",
                "description": "WebSocket-based chat app with rooms, typing indicators and message search.",
                "technologies": "React, Node.js, Socket.io, PostgreSQL",
                "github_url": "https://github.com/karan-joshi/chat-platform",
            },
            {
                "name": "Code Review Bot",
                "description": "GitHub Action that runs automated code reviews using AST analysis.",
                "technologies": "TypeScript, Node.js, GitHub API",
                "github_url": "https://github.com/karan-joshi/review-bot",
            },
        ],
        "certifications": [
            {
                "name": "MongoDB Certified Developer",
                "provider": "MongoDB University",
            },
        ],
    },
    {
        "username": "meera_iyer",
        "email": "meera.i@demo.edu",
        "first_name": "Meera",
        "last_name": "Iyer",
        "password": "Student@2026",
        "profile": {
            "college": "PSG College of Technology",
            "course": "B.Tech Computer Science",
            "branch": "Computer Science",
            "year": 3,
            "cgpa": 8.0,
            "semester": 5,
            "achievements": "Smart India Hackathon 2025 finalist",
            "career_goal": "Mobile App Developer at a consumer startup",
            "preferred_domain": "Mobile / Cross-platform",
            "interests": "Mobile development, UI/UX, React Native, Flutter",
            "about": "Building beautiful mobile experiences that people love.",
        },
        "skills": [
            ("JavaScript", 4, "ADVANCED"),
            ("React", 3, "INTERMEDIATE"),
            ("React Native", 4, "ADVANCED"),
            ("TypeScript", 3, "INTERMEDIATE"),
            ("CSS", 4, "ADVANCED"),
            ("HTML", 4, "ADVANCED"),
            ("Git", 3, "INTERMEDIATE"),
            ("Figma", 3, "INTERMEDIATE"),
            ("Teamwork", 4, "ADVANCED"),
            ("Communication", 4, "ADVANCED"),
        ],
        "projects": [
            {
                "name": "HealthTrack Mobile",
                "description": "Cross-platform health tracking app with habit streaks and progress charts.",
                "technologies": "React Native, TypeScript, Firebase",
                "github_url": "https://github.com/meera-iyer/healthtrack",
            },
        ],
        "certifications": [
            {
                "name": "React Native — The Practical Guide (Udemy)",
                "provider": "Udemy",
            },
        ],
    },
    {
        "username": "david_kumar",
        "email": "david.k@demo.edu",
        "first_name": "David",
        "last_name": "Kumar",
        "password": "Student@2026",
        "profile": {
            "college": "Manipal Institute of Technology",
            "course": "B.Tech Computer Science",
            "branch": "Computer Science",
            "year": 2,
            "cgpa": 7.5,
            "semester": 3,
            "achievements": "",
            "career_goal": "Software Developer at a mid-size company",
            "preferred_domain": "General Software Development",
            "interests": "Python scripting, web scraping, automation",
            "about": "Exploring different areas of CS to find my niche.",
        },
        "skills": [
            ("Python", 3, "INTERMEDIATE"),
            ("Java", 2, "BEGINNER"),
            ("SQL", 2, "BEGINNER"),
            ("HTML", 2, "BEGINNER"),
            ("CSS", 2, "BEGINNER"),
            ("Git", 2, "BEGINNER"),
            ("Problem Solving", 3, "INTERMEDIATE"),
            ("Communication", 3, "INTERMEDIATE"),
        ],
        "projects": [
            {
                "name": "Web Scraper Toolkit",
                "description": "Python library for building configurable web scrapers with proxy support.",
                "technologies": "Python, BeautifulSoup, Requests",
                "github_url": "https://github.com/david-kumar/scraper-toolkit",
            },
        ],
        "certifications": [],
    },
    {
        "username": "isha_gupta",
        "email": "isha.g@demo.edu",
        "first_name": "Isha",
        "last_name": "Gupta",
        "password": "Student@2026",
        "profile": {
            "college": "Thapar Institute of Engineering",
            "course": "B.Tech Computer Engineering",
            "branch": "Computer Engineering",
            "year": 3,
            "cgpa": 8.4,
            "semester": 5,
            "achievements": "Dean's List; AWS Community Builder",
            "career_goal": "Site Reliability Engineer at a cloud-native company",
            "preferred_domain": "SRE / Platform Engineering",
            "interests": "Reliability engineering, observability, incident response, automation",
            "about": "Keeping systems running so users never notice the complexity underneath.",
        },
        "skills": [
            ("Linux", 5, "ADVANCED"),
            ("AWS", 4, "ADVANCED"),
            ("Docker", 4, "ADVANCED"),
            ("Kubernetes", 3, "INTERMEDIATE"),
            ("Python", 4, "ADVANCED"),
            ("SQL", 3, "INTERMEDIATE"),
            ("Git", 4, "ADVANCED"),
            ("System Design", 3, "INTERMEDIATE"),
            ("Problem Solving", 4, "ADVANCED"),
            ("Communication", 4, "ADVANCED"),
        ],
        "projects": [
            {
                "name": "Uptime Monitor",
                "description": "Multi-protocol uptime monitoring service with Slack and PagerDuty alerts.",
                "technologies": "Python, PostgreSQL, Redis, Docker",
                "github_url": "https://github.com/isha-gupta/uptime-monitor",
            },
        ],
        "certifications": [
            {
                "name": "AWS Solutions Architect – Associate",
                "provider": "Amazon Web Services",
            },
        ],
    },
]

# ---------------------------------------------------------------------------
# Assessments — 5 assessments, 10 questions each (50 questions)
# ---------------------------------------------------------------------------
DEMO_ASSESSMENTS = [
    {
        "title": "Python Fundamentals",
        "description": "Core Python: data types, functions, collections, exceptions and operators.",
        "skill": "Python",
        "difficulty": "INTERMEDIATE",
        "duration_minutes": 15,
        "questions": [
            {"text": "Which keyword is used to define a function in Python?", "options": ["function", "def", "func", "define"], "correct": 1},
            {"text": "Which of these data types is immutable?", "options": ["List", "Set", "Tuple", "Dictionary"], "correct": 2},
            {"text": "What does `print(type([]))` output?", "options": ["<class 'list'>", "<class 'tuple'>", "<class 'array'>", "<class 'dict'>"], "correct": 0},
            {"text": "Which statement is used to handle exceptions in Python?", "options": ["if / else", "for / while", "try / except", "switch / case"], "correct": 2},
            {"text": "Which list method appends an element at the end?", "options": ["push()", "append()", "add()", "insert()"], "correct": 1},
            {"text": "What is the result of `2 ** 3`?", "options": ["6", "8", "9", "5"], "correct": 1},
            {"text": "Which keyword is used to create a generator function?", "options": ["yield", "generate", "return", "async"], "correct": 0},
            {"text": "What is the output of `len({'a': 1, 'b': 2})`?", "options": ["1", "2", "3", "4"], "correct": 1},
            {"text": "Which of these is NOT a valid Python variable name?", "options": ["_count", "count2", "2count", "__count__"], "correct": 2},
            {"text": "What does `isinstance(True, int)` return in Python?", "options": ["True", "False", "TypeError", "None"], "correct": 0},
        ],
    },
    {
        "title": "SQL Basics",
        "description": "Structured Query Language: queries, joins, aggregation and filtering.",
        "skill": "SQL",
        "difficulty": "BEGINNER",
        "duration_minutes": 10,
        "questions": [
            {"text": "Which SQL statement retrieves data from a table?", "options": ["GET", "SELECT", "FETCH", "USE"], "correct": 1},
            {"text": "Which keyword is used to combine rows from two tables on a condition?", "options": ["MERGE", "LINK", "JOIN", "COMBINE"], "correct": 2},
            {"text": "Which aggregate function counts the number of rows?", "options": ["SUM()", "AVG()", "TOTAL()", "COUNT()"], "correct": 3},
            {"text": "Which clause filters groups created by GROUP BY?", "options": ["WHERE", "HAVING", "FILTER", "LIMIT"], "correct": 1},
            {"text": "Which SQL clause is used to sort the result set?", "options": ["SORT BY", "ORDER BY", "ARRANGE BY", "GROUP BY"], "correct": 1},
            {"text": "What does the WHERE clause do?", "options": ["Groups rows", "Sorts rows", "Filters rows", "Joins tables"], "correct": 2},
            {"text": "Which JOIN returns all rows from both tables?", "options": ["INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "FULL OUTER JOIN"], "correct": 3},
            {"text": "Which statement is used to add a new row to a table?", "options": ["ADD", "INSERT INTO", "UPDATE", "CREATE"], "correct": 1},
            {"text": "Which command removes all rows from a table without logging each row deletion?", "options": ["DELETE", "DROP", "TRUNCATE", "REMOVE"], "correct": 2},
            {"text": "What is the primary key constraint?", "options": ["Allows NULLs", "Must be unique and not null", "Can have duplicates", "Is always auto-incremented"], "correct": 1},
        ],
    },
    {
        "title": "JavaScript Essentials",
        "description": "Modern JavaScript: ES6+, async/await, DOM manipulation and closures.",
        "skill": "JavaScript",
        "difficulty": "INTERMEDIATE",
        "duration_minutes": 12,
        "questions": [
            {"text": "Which keyword declares a block-scoped variable in ES6?", "options": ["var", "let", "define", "dim"], "correct": 1},
            {"text": "What does `===` check in JavaScript?", "options": ["Value only", "Type only", "Value and type", "Reference"], "correct": 2},
            {"text": "Which method converts a JSON string to a JavaScript object?", "options": ["JSON.stringify()", "JSON.parse()", "JSON.toObject()", "JSON.decode()"], "correct": 1},
            {"text": "What is a closure in JavaScript?", "options": ["A type of loop", "A function with access to its outer scope", "A way to close the browser", "An error handler"], "correct": 1},
            {"text": "Which method adds an element to the end of an array?", "options": ["append()", "push()", "add()", "insert()"], "correct": 1},
            {"text": "What does `typeof null` return in JavaScript?", "options": ["\"null\"", "\"undefined\"", "\"object\"", "\"boolean\""], "correct": 2},
            {"text": "Which keyword is used to define a constant in ES6?", "options": ["const", "let", "var", "define"], "correct": 0},
            {"text": "What is the output of `console.log(0.1 + 0.2 === 0.3)`?", "options": ["true", "false", "undefined", "NaN"], "correct": 1},
            {"text": "Which array method returns a new array with elements that pass a test?", "options": ["map()", "forEach()", "filter()", "reduce()"], "correct": 2},
            {"text": "What is the purpose of the `async` keyword?", "options": ["Makes a function run in parallel", "Declares an asynchronous function", "Creates a thread", "Pauses execution"], "correct": 1},
        ],
    },
    {
        "title": "React Fundamentals",
        "description": "Component-based UI: hooks, props, state, rendering and lifecycle.",
        "skill": "React",
        "difficulty": "INTERMEDIATE",
        "duration_minutes": 12,
        "questions": [
            {"text": "What is the primary way to update a component's state in functional components?", "options": ["this.setState()", "useState", "updateState", "setState"], "correct": 1},
            {"text": "Which hook runs after every render to perform side effects?", "options": ["useMemo", "useCallback", "useEffect", "useRef"], "correct": 2},
            {"text": "What is JSX?", "options": ["A new programming language", "JavaScript XML syntax extension", "A CSS framework", "A testing library"], "correct": 1},
            {"text": "Which prop is used to pass children elements to a component?", "options": ["key", "ref", "children", "props"], "correct": 2},
            {"text": "What does the `key` prop help React with?", "options": ["Styling", "Accessibility", "Identifying list items efficiently", "Form validation"], "correct": 2},
            {"text": "Which hook is used to reference a DOM element directly?", "options": ["useEffect", "useRef", "useMemo", "useCallback"], "correct": 1},
            {"text": "What is prop drilling?", "options": ["Validating props", "Passing props through many component layers", "Creating custom props", "Deleting props"], "correct": 1},
            {"text": "Which method is used to memoize a value to avoid recalculating?", "options": ["useCallback", "useMemo", "useRef", "useState"], "correct": 1},
            {"text": "What is the virtual DOM?", "options": ["A lightweight copy of the real DOM", "A 3D rendering engine", "A database for UI", "A CSS preprocessor"], "correct": 0},
            {"text": "Which React method is called when a class component is first rendered?", "options": ["componentDidUpdate", "componentWillUnmount", "componentDidMount", "render"], "correct": 2},
        ],
    },
    {
        "title": "Data Structures & Algorithms",
        "description": "Core DSA: arrays, trees, graphs, sorting, searching and complexity.",
        "skill": "Data Structures & Algorithms",
        "difficulty": "ADVANCED",
        "duration_minutes": 20,
        "questions": [
            {"text": "What is the time complexity of binary search on a sorted array of n elements?", "options": ["O(n)", "O(log n)", "O(n log n)", "O(1)"], "correct": 1},
            {"text": "Which data structure uses FIFO (First In, First Out) ordering?", "options": ["Stack", "Queue", "Tree", "Graph"], "correct": 1},
            {"text": "What is the worst-case time complexity of quicksort?", "options": ["O(n)", "O(n log n)", "O(n^2)", "O(log n)"], "correct": 2},
            {"text": "Which tree structure keeps nodes sorted and supports O(log n) search?", "options": ["Binary Heap", "Binary Search Tree", "Trie", "Hash Table"], "correct": 1},
            {"text": "What is the space complexity of merge sort?", "options": ["O(1)", "O(log n)", "O(n)", "O(n^2)"], "correct": 2},
            {"text": "Which algorithm finds the shortest path in an unweighted graph?", "options": ["Dijkstra's", "BFS", "DFS", "Bellman-Ford"], "correct": 1},
            {"text": "What is the average time complexity of hash table lookup?", "options": ["O(n)", "O(log n)", "O(1)", "O(n log n)"], "correct": 2},
            {"text": "Which data structure is best for implementing a priority queue?", "options": ["Array", "Linked List", "Heap", "Stack"], "correct": 2},
            {"text": "What is dynamic programming?", "options": ["A type of sorting", "Solving problems by breaking into overlapping subproblems", "A machine learning technique", "A database optimization"], "correct": 1},
            {"text": "Which sorting algorithm is stable and has O(n log n) worst case?", "options": ["Quicksort", "Merge Sort", "Heap Sort", "Selection Sort"], "correct": 1},
        ],
    },
]

# ---------------------------------------------------------------------------
# Applications — 20 applications across students at various stages
# ---------------------------------------------------------------------------
DEMO_APPLICATIONS = [
    # (student_email, opportunity_title, company, status, days_ago)
    # Rohan — active applications
    ("student@skillmap.ai", "Software Engineering Intern", "Zoho Corporation", "APPLIED", 2),
    ("student@skillmap.ai", "Associate Software Engineer (Backend)", "Razorpay", "UNDER_REVIEW", 5),
    ("student@skillmap.ai", "Software Development Engineer Intern", "Walmart Global Tech India", "SHORTLISTED", 10),
    # Rohan — terminal decisions
    ("student@skillmap.ai", "Product Engineering Intern", "PhonePe", "REJECTED", 15),
    ("student@skillmap.ai", "Graduate Trainee Program", "Infosys", "SELECTED", 25),
    # Priya — ML-focused applications
    ("priya.nair@demo.edu", "Data Science Intern", "Fractal Analytics", "UNDER_REVIEW", 4),
    ("priya.nair@demo.edu", "Machine Learning Engineer", "Freshworks", "SHORTLISTED", 8),
    ("priya.nair@demo.edu", "Software Development Engineer Intern", "Walmart Global Tech India", "APPLIED", 1),
    ("priya.nair@demo.edu", "Graduate Trainee Program", "Infosys", "REJECTED", 20),
    # Arjun — frontend applications
    ("arjun.r@demo.edu", "Frontend Engineer", "CRED", "INTERVIEW", 12),
    ("arjun.r@demo.edu", "Software Engineering Intern", "Zoho Corporation", "APPLIED", 3),
    ("arjun.r@demo.edu", "Graduate Trainee Program", "Infosys", "SUBMITTED", 6),
    # Sneha — cloud/devops applications
    ("sneha.p@demo.edu", "DevOps Engineer Intern", "CloudSek", "SELECTED", 18),
    ("sneha.p@demo.edu", "Software Development Engineer Intern", "Walmart Global Tech India", "SHORTLISTED", 9),
    # Rahul — backend applications
    ("rahul.v@demo.edu", "Associate Software Engineer (Backend)", "Razorpay", "INTERVIEW", 11),
    ("rahul.v@demo.edu", "Software Engineering Intern", "Zoho Corporation", "UNDER_REVIEW", 5),
    # Ananya — data applications
    ("ananya.s@demo.edu", "Data Science Intern", "Fractal Analytics", "APPLIED", 2),
    ("ananya.s@demo.edu", "Graduate Trainee Program", "Infosys", "SUBMITTED", 7),
    # Karan — full-stack applications
    ("karan.j@demo.edu", "Software Engineering Intern", "Zoho Corporation", "SELECTED", 22),
    ("karan.j@demo.edu", "Associate Software Engineer (Backend)", "Razorpay", "APPLIED", 3),
]

# ---------------------------------------------------------------------------
# Command
# ---------------------------------------------------------------------------
class Command(BaseCommand):
    help = "Seed comprehensive demo data for the Smart India Hackathon presentation."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete all demo data and reseed from scratch",
        )

    def handle(self, *args, **options):
        reset = options["reset"]

        if reset:
            self._full_reset()

        # 1. Base catalogs
        self._seed("Skill catalog", ensure_skill_catalog)
        self._seed("Career catalog", ensure_demo_careers)
        self._seed("Learning resources", ensure_demo_resources)
        self._seed("Opportunities", ensure_demo_opportunities)

        # 1b. Admin user (needed for assessments)
        admin_data = {
            "username": "demo_admin",
            "email": "admin@skillmap.ai",
            "first_name": "Platform",
            "last_name": "Admin",
            "password": "Admin@2026",
            "role": "ADMIN",
        }
        admin_user, admin_created = self._get_or_create_user(admin_data)
        if admin_created:
            self.stdout.write(self.style.SUCCESS("Created admin user."))

        # 2. Professors
        professor_count = 0
        for data in DEMO_PROFESSORS:
            user, created = self._get_or_create_user(data)
            if created:
                professor_count += 1
        if professor_count:
            self.stdout.write(self.style.SUCCESS(f"Created {professor_count} professors."))

        # 3. Students + profiles + skills + projects + certs
        student_count = 0
        for data in DEMO_STUDENTS:
            user, created = self._get_or_create_user(data)
            if created:
                student_count += 1
                self._create_student_data(user, data)
        if student_count:
            self.stdout.write(self.style.SUCCESS(f"Created {student_count} students with profiles, skills and projects."))

        # 4. Assessments with questions
        assessment_count = self._seed_assessments()
        if assessment_count:
            self.stdout.write(self.style.SUCCESS(f"Created {assessment_count} assessments with 50 questions total."))

        # 5. Applications
        application_count = self._seed_applications()
        if application_count:
            self.stdout.write(self.style.SUCCESS(f"Created {application_count} applications across students."))

        # 6. Feedback for terminal decisions
        self._seed("Career feedback", ensure_demo_feedback)

        # Summary
        self.stdout.write(self.style.SUCCESS("\n" + "=" * 60))
        self.stdout.write(self.style.SUCCESS("SIH DEMO DATA SEEDED SUCCESSFULLY"))
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(f"  Students:       {User.objects.filter(role='STUDENT').count()}")
        self.stdout.write(f"  Professors:     {User.objects.filter(role='PROFESSOR').count()}")
        self.stdout.write(f"  Skills catalog: {Skill.objects.count()}")
        self.stdout.write(f"  Careers:        5 (with skill requirements)")
        self.stdout.write(f"  Assessments:    {Assessment.objects.count()} ({Question.objects.count()} questions)")
        self.stdout.write(f"  Opportunities:  {Opportunity.objects.count()}")
        self.stdout.write(f"  Applications:   {Application.objects.count()}")
        self.stdout.write(f"  User skills:    {UserSkill.objects.count()}")
        self.stdout.write(f"  Projects:       {Project.objects.count()}")
        self.stdout.write(f"  Certifications: {Certification.objects.count()}")
        self.stdout.write(self.style.SUCCESS("\nLogin credentials:"))
        for data in DEMO_STUDENTS[:3]:
            self.stdout.write(f"  Student:  {data['email']} / {data['password']}")
        for data in DEMO_PROFESSORS[:1]:
            self.stdout.write(f"  Professor: {data['email']} / {data['password']}")
        self.stdout.write(f"  Admin:    admin@skillmap.ai / Admin@2026")

    # -----------------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------------
    def _full_reset(self):
        """Delete all demo data to start fresh."""
        from apps.applications.models import Application
        from apps.feedback.models import ApplicationFeedback
        from apps.learning.models import ResourceCompletion
        from apps.notifications.models import Notification

        from apps.assessments.models import Assessment, Option, Question

        # Delete in reverse dependency order
        Option.objects.all().delete()
        Question.objects.all().delete()
        Assessment.objects.all().delete()
        ApplicationFeedback.objects.all().delete()
        Application.objects.all().delete()
        ResourceCompletion.objects.all().delete()
        Notification.objects.all().delete()
        UserSkill.objects.all().delete()
        Project.objects.all().delete()
        Certification.objects.all().delete()
        StudentProfile.objects.all().delete()
        # Delete all users except superusers
        User.objects.filter(is_superuser=False).delete()
        self.stdout.write(self.style.WARNING("Full reset complete — all demo data removed."))

    def _seed(self, label, func):
        count = func()
        if count:
            self.stdout.write(self.style.SUCCESS(f"Seeded {count} {label}."))

    def _get_or_create_user(self, data):
        email = data["email"]
        user = User.objects.filter(email=email).first()
        if user is not None:
            return user, False
        user = User(
            username=data["username"],
            email=email,
            first_name=data["first_name"],
            last_name=data["last_name"],
            role=data.get("role", User.Role.STUDENT),
        )
        user.set_password(data["password"])
        user.save()
        return user, True

    def _create_student_data(self, user, data):
        # Profile
        profile_data = data.get("profile", {})
        StudentProfile.objects.get_or_create(user=user, defaults=profile_data)

        # Skills
        for skill_name, proficiency, experience in data.get("skills", []):
            skill = Skill.objects.filter(name=skill_name).first()
            if skill:
                UserSkill.objects.get_or_create(
                    user=user,
                    skill=skill,
                    defaults={
                        "proficiency_level": proficiency,
                        "experience_level": experience,
                    },
                )

        # Projects
        for project_data in data.get("projects", []):
            Project.objects.get_or_create(
                user=user,
                name=project_data["name"],
                defaults=project_data,
            )

        # Certifications
        for cert_data in data.get("certifications", []):
            Certification.objects.get_or_create(
                user=user,
                name=cert_data["name"],
                defaults=cert_data,
            )

    def _seed_assessments(self):
        created = 0
        admin_user = User.objects.filter(role=User.Role.ADMIN).first()
        for spec in DEMO_ASSESSMENTS:
            if Assessment.objects.filter(title=spec["title"]).exists():
                continue
            skill = Skill.objects.filter(name=spec["skill"]).first()
            if skill is None:
                continue
            assessment = Assessment.objects.create(
                title=spec["title"],
                description=spec["description"],
                skill=skill,
                difficulty=spec["difficulty"],
                duration_minutes=spec["duration_minutes"],
                is_published=True,
                created_by=admin_user,
            )
            for position, qspec in enumerate(spec["questions"], start=1):
                question = Question.objects.create(
                    assessment=assessment,
                    text=qspec["text"],
                    order=position,
                )
                Option.objects.bulk_create(
                    [
                        Option(
                            question=question,
                            text=text,
                            is_correct=index == qspec["correct"],
                            order=index,
                        )
                        for index, text in enumerate(qspec["options"])
                    ]
                )
            created += 1
        return created

    def _seed_applications(self):
        created = 0
        now = timezone.now()
        for email, title, company, status, days_ago in DEMO_APPLICATIONS:
            student = User.objects.filter(email=email).first()
            if student is None:
                continue
            opportunity = Opportunity.objects.filter(title=title, company=company).first()
            if opportunity is None:
                continue
            if Application.objects.filter(student=student, opportunity=opportunity).exists():
                continue
            Application.objects.create(
                student=student,
                opportunity=opportunity,
                status=status,
                applied_at=now - timedelta(days=days_ago),
            )
            created += 1
        return created
