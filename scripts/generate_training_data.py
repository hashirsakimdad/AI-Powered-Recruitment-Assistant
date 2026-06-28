import json
import random

SKILLS_POOL = [
    "Python", "JavaScript", "Java", "C++", "SQL", "MongoDB",
    "React", "Django", "Flask", "Node.js", "Docker", "Kubernetes",
    "AWS", "Machine Learning", "TensorFlow", "PyTorch", "FastAPI",
    "PostgreSQL", "Redis", "Git", "Linux", "REST APIs"
]

JOB_TITLES = [
    "Python Developer", "Full Stack Developer", "ML Engineer",
    "Backend Developer", "Data Scientist", "DevOps Engineer",
    "Frontend Developer", "Software Engineer"
]

def generate_sample(match_level):
    """Generate resume-job pair with known match level"""
    
    job_skills = random.sample(SKILLS_POOL, 5)
    
    if match_level == "high":
        # Resume has 4-5 of required skills
        resume_skills = job_skills[:4] + random.sample(SKILLS_POOL, 3)
        score = random.uniform(70, 95)
    elif match_level == "medium":
        # Resume has 2-3 of required skills  
        resume_skills = job_skills[:2] + random.sample(SKILLS_POOL, 4)
        score = random.uniform(45, 69)
    else:
        # Resume has 0-1 of required skills
        resume_skills = random.sample(
            [s for s in SKILLS_POOL if s not in job_skills], 5
        )
        score = random.uniform(10, 44)
    
    title = random.choice(JOB_TITLES)
    
    return {
        "job_title": title,
        "job_skills": job_skills,
        "job_description": f"Looking for {title}. Required: {', '.join(job_skills)}",
        "resume_skills": resume_skills,
        "resume_text": f"Experienced developer. Skills: {', '.join(resume_skills)}. 3 years experience.",
        "score": round(score, 1),
        "label": 1 if score >= 60 else 0
    }

# Generate 500 samples
data = []
for _ in range(200):
    data.append(generate_sample("high"))
for _ in range(150):
    data.append(generate_sample("medium"))
for _ in range(150):
    data.append(generate_sample("low"))

random.shuffle(data)

with open("training/data/synthetic_resume_data.json", "w") as f:
    json.dump(data, f, indent=2)

print(f"Generated {len(data)} training samples")
print(f"High match: 200, Medium: 150, Low: 150")
