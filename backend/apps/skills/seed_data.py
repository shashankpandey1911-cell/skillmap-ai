"""Default master skill catalog (idempotent, used by seeding and tests).

Realistic skills across the nine categories — demo data lives in the
database, never hardcoded in the UI.
"""

from .models import Skill

SKILL_CATALOG: list[tuple[str, str, str]] = [
    # (name, category, short description)
    ("Python", "Programming", "General-purpose language; scripting, automation, backends."),
    ("Java", "Programming", "Object-oriented language used in enterprise and Android."),
    ("Data Structures & Algorithms", "Programming", "Foundational problem-solving and interview skills."),
    ("System Design", "Programming", "Designing scalable, maintainable software systems."),
    ("C++", "Programming", "Systems language; competitive programming, game engines."),
    ("JavaScript", "Programming", "Language of the web; used across front and back end."),
    ("TypeScript", "Programming", "Typed superset of JavaScript."),
    ("Go", "Programming", "Compiled language for cloud and backend services."),
    ("C", "Programming", "Low-level language; fundamentals of systems programming."),
    ("Rust", "Programming", "Memory-safe systems language."),
    ("Dart", "Programming", "Language behind Flutter cross-platform apps."),
    ("Kotlin", "Programming", "Modern JVM language for Android development."),
    ("Swift", "Programming", "Language for iOS/macOS development."),
    ("React", "Web Development", "Component-based UI library."),
    ("React Native", "Web Development", "Mobile apps from React components."),
    ("Next.js", "Web Development", "React framework with SSR and routing."),
    ("Vue.js", "Web Development", "Progressive JavaScript UI framework."),
    ("Angular", "Web Development", "Structured TypeScript framework for web apps."),
    ("HTML", "Web Development", "Structure of web pages."),
    ("CSS", "Web Development", "Styling and layout of web pages."),
    ("Tailwind CSS", "Web Development", "Utility-first CSS framework."),
    ("Node.js", "Web Development", "JavaScript runtime for backend services."),
    ("Django", "Web Development", "High-level Python web framework."),
    ("Flask", "Web Development", "Lightweight Python web framework."),
    ("FastAPI", "Web Development", "Modern async Python API framework."),
    ("REST API", "Web Development", "Designing and consuming HTTP APIs."),
    ("Express.js", "Web Development", "Minimal Node.js web framework."),
    ("Spring Boot", "Web Development", "Java framework for production apps."),
    ("SQL", "Database", "Querying and managing relational databases."),
    ("PostgreSQL", "Database", "Advanced open-source relational database."),
    ("MySQL", "Database", "Popular open-source relational database."),
    ("MongoDB", "Database", "Document-oriented NoSQL database."),
    ("Redis", "Database", "In-memory data store / cache."),
    ("Firebase", "Database", "Backend-as-a-service with realtime database."),
    ("AWS", "Cloud", "Amazon cloud platform."),
    ("Azure", "Cloud", "Microsoft cloud platform."),
    ("Google Cloud", "Cloud", "Google cloud platform."),
    ("Docker", "Cloud", "Containerization platform."),
    ("Kubernetes", "Cloud", "Container orchestration."),
    ("Terraform", "Cloud", "Infrastructure as code."),
    ("Machine Learning", "AI/ML", "Algorithms that learn from data."),
    ("Deep Learning", "AI/ML", "Neural-network based learning."),
    ("NLP", "AI/ML", "Processing and understanding text."),
    ("Computer Vision", "AI/ML", "Understanding images and video."),
    ("TensorFlow", "AI/ML", "ML framework by Google."),
    ("PyTorch", "AI/ML", "ML framework with dynamic graphs."),
    ("Scikit-learn", "AI/ML", "Classic ML algorithms in Python."),
    ("Hugging Face", "AI/ML", "Pretrained model hub and tooling."),
    ("Prompt Engineering", "AI/ML", "Designing effective LLM instructions."),
    ("Pandas", "Data Science", "Data manipulation in Python."),
    ("NumPy", "Data Science", "Numerical computing in Python."),
    ("Matplotlib", "Data Science", "Plotting and visualization in Python."),
    ("Data Visualization", "Data Science", "Communicating data visually."),
    ("Statistics", "Data Science", "Foundations of data analysis."),
    ("Excel", "Data Science", "Spreadsheet analysis and modeling."),
    ("Tableau", "Data Science", "Business intelligence dashboards."),
    ("Power BI", "Data Science", "Microsoft analytics dashboards."),
    ("Git", "Tools", "Version control."),
    ("GitHub", "Tools", "Git hosting and collaboration."),
    ("VS Code", "Tools", "Code editor."),
    ("Postman", "Tools", "API testing and exploration."),
    ("Linux", "Tools", "Operating system and shell workflows."),
    ("Figma", "Tools", "UI design and prototyping."),
    ("Communication", "Soft Skills", "Clear written and spoken exchange."),
    ("Teamwork", "Soft Skills", "Collaborating effectively in groups."),
    ("Leadership", "Soft Skills", "Guiding and motivating teams."),
    ("Problem Solving", "Soft Skills", "Breaking down and solving challenges."),
    ("Time Management", "Soft Skills", "Prioritizing and meeting deadlines."),
    ("Public Speaking", "Soft Skills", "Presenting to audiences."),
    ("Microsoft Office", "Other", "Word, PowerPoint and productivity suite."),
    ("Photography", "Other", "Capturing and editing images."),
]


def ensure_skill_catalog() -> int:
    """Create catalog entries that do not exist yet. Returns count created."""
    created = 0
    existing = {name for name in Skill.objects.values_list("name", flat=True)}
    for name, category, description in SKILL_CATALOG:
        if name not in existing:
            Skill.objects.create(name=name, category=category, description=description)
            created += 1
    return created
