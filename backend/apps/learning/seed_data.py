"""Demo learning resources for the hackathon walkthrough (Phase 8).

Idempotent: resources already present by (skill, title) are skipped. The rows
are realistic, real-world content links tagged to catalog skills so that the
personalized roadmap always has genuine material to recommend.
"""

from apps.skills.models import Skill

from .models import LearningResource

# (skill name, type, level, title, url, estimated duration in minutes)
_DEMO_RESOURCES: list[tuple] = [
    # --- Python ---
    ("Python", "COURSE", "BEGINNER", "Python for Everybody (Coursera)", "https://www.coursera.org/specializations/python", 2400),
    ("Python", "DOCUMENTATION", "BEGINNER", "The Python Tutorial — official docs", "https://docs.python.org/3/tutorial/", 600),
    ("Python", "VIDEO", "BEGINNER", "Learn Python — Full Course (freeCodeCamp)", "https://www.youtube.com/watch?v=rfscVS0vtbw", 270),
    ("Python", "PRACTICE", "BEGINNER", "Practice Python — 40+ beginner exercises", "https://www.practicepython.org/", 300),
    ("Python", "PROJECT", "INTERMEDIATE", "Automate the Boring Stuff with Python", "https://automatetheboringstuff.com/", 1800),
    ("Python", "QUIZ", "INTERMEDIATE", "Python Online Quiz — GeeksforGeeks", "https://www.geeksforgeeks.org/python-online-test/", 20),

    # --- Django ---
    ("Django", "COURSE", "BEGINNER", "Django for Everybody (Coursera)", "https://www.coursera.org/specializations/django", 1800),
    ("Django", "DOCUMENTATION", "BEGINNER", "Writing your first Django app — official tutorial", "https://docs.djangoproject.com/en/5.0/intro/tutorial01/", 540),
    ("Django", "VIDEO", "INTERMEDIATE", "Python Django Web Framework — freeCodeCamp", "https://www.youtube.com/watch?v=F5mRW0jo-U4", 240),
    ("Django", "PROJECT", "INTERMEDIATE", "Build a blog with Django Girls tutorial", "https://tutorial.djangogirls.org/en/", 480),
    ("Django", "PRACTICE", "ADVANCED", "Django REST Framework official tutorial", "https://www.django-rest-framework.org/tutorial/1-serialization/", 420),

    # --- SQL ---
    ("SQL", "COURSE", "BEGINNER", "SQL for Data Science (Coursera)", "https://www.coursera.org/learn/sql-for-data-science", 1200),
    ("SQL", "DOCUMENTATION", "BEGINNER", "W3Schools SQL Tutorial", "https://www.w3schools.com/sql/", 300),
    ("SQL", "PRACTICE", "INTERMEDIATE", "SQLBolt — interactive SQL lessons", "https://sqlbolt.com/", 180),
    ("SQL", "PRACTICE", "INTERMEDIATE", "SQLZoo — interactive exercises", "https://sqlzoo.net/wiki/SQL_Tutorial", 240),
    ("SQL", "QUIZ", "INTERMEDIATE", "W3Schools SQL Quiz", "https://www.w3schools.com/sql/sql_quiz.asp", 15),

    # --- DSA ---
    ("Data Structures & Algorithms", "COURSE", "BEGINNER", "Data Structures & Algorithms Specialization (Coursera)", "https://www.coursera.org/specializations/data-structures-algorithms", 2400),
    ("Data Structures & Algorithms", "VIDEO", "BEGINNER", "Data Structures Easy to Advanced — freeCodeCamp", "https://www.youtube.com/watch?v=RBSGKlAvoiM", 480),
    ("Data Structures & Algorithms", "PRACTICE", "INTERMEDIATE", "GeeksforGeeks DSA Self-Paced problems", "https://www.geeksforgeeks.org/data-structures/", 600),
    ("Data Structures & Algorithms", "PRACTICE", "INTERMEDIATE", "LeetCode — Top Interview Questions", "https://leetcode.com/problem-list/top-interview-questions/", 600),
    ("Data Structures & Algorithms", "QUIZ", "INTERMEDIATE", "DSA Online Quiz — Sanfoundry", "https://www.sanfoundry.com/1000-data-structure-questions-answers/", 30),

    # --- Git ---
    ("Git", "COURSE", "BEGINNER", "Version Control with Git (Coursera)", "https://www.coursera.org/learn/version-control-with-git", 600),
    ("Git", "DOCUMENTATION", "BEGINNER", "Git — the simple guide", "https://rogerdudler.github.io/git-guide/", 60),
    ("Git", "VIDEO", "BEGINNER", "Git and GitHub for Beginners — freeCodeCamp", "https://www.youtube.com/watch?v=RGOj5yH7evk", 60),
    ("Git", "PRACTICE", "INTERMEDIATE", "Learn Git Branching — interactive", "https://learngitbranching.js.org/", 120),
    ("Git", "QUIZ", "BEGINNER", "Git Quiz — GeeksforGeeks", "https://www.geeksforgeeks.org/git-github-interview-questions/", 15),

    # --- JavaScript ---
    ("JavaScript", "COURSE", "BEGINNER", "JavaScript Algorithms and Data Structures (freeCodeCamp)", "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/", 1800),
    ("JavaScript", "DOCUMENTATION", "BEGINNER", "MDN JavaScript Guide", "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide", 900),
    ("JavaScript", "VIDEO", "BEGINNER", "JavaScript Full Course — freeCodeCamp", "https://www.youtube.com/watch?v=PkZNo7MFNFg", 180),
    ("JavaScript", "PRACTICE", "INTERMEDIATE", "JavaScript30 — 30 coding challenges", "https://javascript30.com/", 600),
    ("JavaScript", "QUIZ", "INTERMEDIATE", "W3Schools JavaScript Quiz", "https://www.w3schools.com/js/js_quiz.asp", 15),

    # --- React ---
    ("React", "COURSE", "BEGINNER", "React — The Complete Guide (Udemy)", "https://www.udemy.com/course/react-the-complete-guide-incl-redux/", 3000),
    ("React", "DOCUMENTATION", "BEGINNER", "React Quick Start — official docs", "https://react.dev/learn", 480),
    ("React", "VIDEO", "INTERMEDIATE", "React Course for Beginners — freeCodeCamp", "https://www.youtube.com/watch?v=bMknfKXIFA8", 660),
    ("React", "PROJECT", "INTERMEDIATE", "Tic-Tac-Toe tutorial — official docs", "https://react.dev/learn/tutorial-tic-tac-toe", 120),
    ("React", "QUIZ", "INTERMEDIATE", "React Interview Questions & Quiz", "https://www.interviewbit.com/react-interview-questions/", 30),

    # --- HTML / CSS (for frontend career) ---
    ("HTML", "COURSE", "BEGINNER", "Responsive Web Design (freeCodeCamp)", "https://www.freecodecamp.org/learn/2022/responsive-web-design/", 1800),
    ("HTML", "PRACTICE", "BEGINNER", "HTML Exercises — W3Schools", "https://www.w3schools.com/html/html_exercises.asp", 120),
    ("CSS", "COURSE", "BEGINNER", "CSS Tutorial — W3Schools", "https://www.w3schools.com/css/", 240),
    ("CSS", "VIDEO", "INTERMEDIATE", "Learn CSS — full course (freeCodeCamp)", "https://www.youtube.com/watch?v=OXGznpKZ_sA", 300),
    ("CSS", "PRACTICE", "INTERMEDIATE", "Flexbox Froggy — interactive game", "https://flexboxfroggy.com/", 45),

    # --- TypeScript ---
    ("TypeScript", "COURSE", "INTERMEDIATE", "Understanding TypeScript (Udemy)", "https://www.udemy.com/course/understanding-typescript/", 2400),
    ("TypeScript", "DOCUMENTATION", "INTERMEDIATE", "TypeScript Handbook — official docs", "https://www.typescriptlang.org/docs/handbook/intro.html", 480),
    ("TypeScript", "VIDEO", "BEGINNER", "TypeScript Course for Beginners — freeCodeCamp", "https://www.youtube.com/watch?v=BwuLxPH8IDs", 180),

    # --- REST API (used by rejection feedback demo) ---
    ("REST API", "COURSE", "BEGINNER", "REST API Concepts & Examples — freeCodeCamp", "https://www.youtube.com/watch?v=lsMQRaeKNDk", 300),
    ("REST API", "DOCUMENTATION", "BEGINNER", "REST API best practices — MDN Web Docs", "https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/REST_APIs", 240),
    ("REST API", "PRACTICE", "INTERMEDIATE", "Postman Learning Center — your first API request", "https://learning.postman.com/", 120),

    # --- Data Science skills ---
    ("Statistics", "COURSE", "BEGINNER", "Statistics with R / Python (Coursera)", "https://www.coursera.org/specializations/statistics", 1800),
    ("Statistics", "VIDEO", "BEGINNER", "Statistics Fundamentals — Khan Academy", "https://www.khanacademy.org/math/statistics-probability", 900),
    ("Statistics", "DOCUMENTATION", "INTERMEDIATE", "Stat Trek — statistics tutorials", "https://stattrek.com/", 300),
    ("Statistics", "PRACTICE", "INTERMEDIATE", "Probability & Statistics exercises (Khan Academy)", "https://www.khanacademy.org/math/statistics-probability/probability-library", 300),
    ("Statistics", "QUIZ", "INTERMEDIATE", "Statistics Quiz — GeeksforGeeks", "https://www.geeksforgeeks.org/probability-and-statistics-gq/", 20),

    ("Pandas", "COURSE", "BEGINNER", "Python Data Analysis with Pandas (freeCodeCamp)", "https://www.freecodecamp.org/learn/data-analysis-with-python/", 1800),
    ("Pandas", "DOCUMENTATION", "INTERMEDIATE", "Pandas User Guide — official docs", "https://pandas.pydata.org/docs/user_guide/index.html", 600),
    ("Pandas", "VIDEO", "BEGINNER", "Pandas Tutorial — Corey Schafer", "https://www.youtube.com/playlist?list=PL-osiE80TeTsWmV9i9c58mdDCSskIFdDS", 240),
    ("Pandas", "PRACTICE", "INTERMEDIATE", "Pandas Exercises — Kaggle Learn", "https://www.kaggle.com/learn/pandas", 240),

    ("Machine Learning", "COURSE", "BEGINNER", "Machine Learning Specialization (Coursera / Andrew Ng)", "https://www.coursera.org/specializations/machine-learning-introduction", 3000),
    ("Machine Learning", "VIDEO", "INTERMEDIATE", "Machine Learning for Everybody — freeCodeCamp", "https://www.youtube.com/watch?v=i_LwzRVP7bg", 300),
    ("Machine Learning", "DOCUMENTATION", "INTERMEDIATE", "scikit-learn User Guide", "https://scikit-learn.org/stable/user_guide.html", 600),
    ("Machine Learning", "PRACTICE", "INTERMEDIATE", "Kaggle Intro to Machine Learning", "https://www.kaggle.com/learn/intro-to-machine-learning", 360),

    # --- Cloud / DevOps ---
    ("Docker", "COURSE", "BEGINNER", "Docker Mastery (Udemy)", "https://www.udemy.com/course/docker-mastery-with-kubernetes/", 1800),
    ("Docker", "DOCUMENTATION", "BEGINNER", "Docker Get Started — official docs", "https://docs.docker.com/get-started/", 180),
    ("Docker", "VIDEO", "BEGINNER", "Docker Tutorial for Beginners — freeCodeCamp", "https://www.youtube.com/watch?v=fqMOX6JJhGo", 120),
    ("Docker", "PRACTICE", "INTERMEDIATE", "Play with Docker — hands-on lab", "https://labs.play-with-docker.com/", 180),
    ("Docker", "QUIZ", "BEGINNER", "Docker Quiz — Tutorials Point", "https://www.tutorialspoint.com/docker/docker_online_quiz.htm", 15),

    ("Kubernetes", "COURSE", "INTERMEDIATE", "Kubernetes for the Absolute Beginner (KodeKloud)", "https://kodekloud.com/courses/kubernetes-for-the-absolute-beginners/", 900),
    ("Kubernetes", "DOCUMENTATION", "BEGINNER", "Kubernetes Basics — official tutorial", "https://kubernetes.io/docs/tutorials/kubernetes-basics/", 300),
    ("Kubernetes", "VIDEO", "INTERMEDIATE", "Kubernetes Course — freeCodeCamp", "https://www.youtube.com/watch?v=d6WC5n9G_sM", 300),
    ("Kubernetes", "PRACTICE", "INTERMEDIATE", "Killercoda — interactive Kubernetes playground", "https://killercoda.com/killercoda/scenario/kubernetes", 240),

    ("AWS", "COURSE", "BEGINNER", "AWS Cloud Practitioner Essentials", "https://aws.amazon.com/training/learn-about/cloud-practitioner/", 360),
    ("AWS", "DOCUMENTATION", "INTERMEDIATE", "AWS Documentation — official", "https://docs.aws.amazon.com/", 300),
    ("AWS", "VIDEO", "BEGINNER", "AWS Certified Cloud Practitioner Course — freeCodeCamp", "https://www.youtube.com/watch?v=3hLmDS179YE", 780),
    ("AWS", "PRACTICE", "INTERMEDIATE", "AWS hands-on labs — official", "https://aws.amazon.com/getting-started/hands-on/", 480),

    # --- Tools skills used by careers ---
    ("Linux", "COURSE", "BEGINNER", "Linux Command Line Basics (Udacity)", "https://www.udacity.com/course/linux-command-line-basics--ud595", 600),
    ("Linux", "DOCUMENTATION", "BEGINNER", "Ubuntu command-line reference", "https://ubuntu.com/tutorials/command-line-for-beginners", 120),
    ("Linux", "PRACTICE", "INTERMEDIATE", "OverTheWire Bandit — shell practice", "https://overthewire.org/wargames/bandit/", 240),
]


def ensure_demo_resources() -> int:
    """Create demo learning resources that don't exist yet. Returns created count."""
    created = 0
    existing = {
        (skill_name, title)
        for skill_name, title in LearningResource.objects.select_related("skill").values_list(
            "skill__name", "title"
        )
    }
    for skill_name, rtype, level, title, url, minutes in _DEMO_RESOURCES:
        if (skill_name, title) in existing:
            continue
        skill = Skill.objects.filter(name=skill_name).first()
        if skill is None:
            continue  # catalog not seeded yet
        LearningResource.objects.create(
            title=title,
            description="",
            skill=skill,
            level=level,
            type=rtype,
            url=url,
            estimated_duration_minutes=minutes,
            is_active=True,
        )
        created += 1
    return created
