"""
Intelligent Skill Inference Module
Infers skills from experience, projects, and work descriptions even if not explicitly listed.
"""
import re
from typing import Dict, List, Set, Tuple


# Skill inference patterns - maps keywords/context to likely skills
SKILL_INFERENCE_PATTERNS = {
    # Machine Learning & AI
    "machine learning": ["python", "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy", "ml", "ai"],
    "deep learning": ["python", "tensorflow", "pytorch", "keras", "neural networks", "cnn", "rnn"],
    "data science": ["python", "pandas", "numpy", "matplotlib", "seaborn", "jupyter", "sql", "statistics"],
    "data analysis": ["python", "pandas", "excel", "sql", "statistics", "data visualization"],
    "natural language processing": ["python", "nltk", "spacy", "transformers", "nlp", "bert"],
    "computer vision": ["python", "opencv", "tensorflow", "pytorch", "image processing"],
    
    # Backend Development
    "backend": ["python", "java", "node.js", "express", "django", "flask", "spring", "rest api", "graphql"],
    "api development": ["rest", "graphql", "json", "http", "api", "microservices"],
    "server": ["linux", "nginx", "apache", "docker", "kubernetes", "aws", "azure", "gcp"],
    "database": ["sql", "mysql", "postgresql", "mongodb", "redis", "database design"],
    "microservices": ["docker", "kubernetes", "microservices", "distributed systems"],
    
    # Frontend Development
    "frontend": ["javascript", "html", "css", "react", "vue", "angular", "typescript"],
    "web development": ["html", "css", "javascript", "react", "vue", "angular", "responsive design"],
    "ui/ux": ["figma", "adobe xd", "sketch", "user interface", "user experience", "design"],
    "responsive design": ["css", "bootstrap", "tailwind", "mobile-first", "responsive"],
    
    # Cloud & DevOps
    "cloud": ["aws", "azure", "gcp", "cloud computing", "s3", "ec2", "lambda"],
    "devops": ["docker", "kubernetes", "ci/cd", "jenkins", "gitlab", "github actions", "terraform"],
    "deployment": ["docker", "kubernetes", "ci/cd", "deployment", "automation"],
    
    # Mobile Development
    "mobile": ["android", "ios", "react native", "flutter", "swift", "kotlin", "mobile app"],
    "android": ["java", "kotlin", "android studio", "android sdk"],
    "ios": ["swift", "objective-c", "xcode", "ios development"],
    
    # Programming Languages (inferred from projects)
    "python": ["django", "flask", "pandas", "numpy", "tensorflow", "pytorch"],
    "java": ["spring", "spring boot", "hibernate", "maven", "gradle"],
    "javascript": ["node.js", "react", "vue", "angular", "express", "typescript"],
    "sql": ["database", "mysql", "postgresql", "query optimization"],
    
    # Testing & QA
    "testing": ["unit testing", "integration testing", "test automation", "selenium", "jest", "pytest"],
    "qa": ["quality assurance", "test cases", "bug tracking", "jira"],
    
    # Version Control
    "version control": ["git", "github", "gitlab", "bitbucket", "svn"],
    
    # Agile & Project Management
    "agile": ["scrum", "kanban", "sprint", "agile methodology", "jira"],
    "project management": ["project planning", "jira", "trello", "asana", "leadership"],
}


def infer_skills_from_text(text: str, explicit_skills: List[str] = None) -> Tuple[Set[str], Dict[str, List[str]]]:
    """
    Infer skills from resume text based on experience, projects, and work descriptions.
    
    Args:
        text: Full resume text
        explicit_skills: List of explicitly listed skills (to avoid duplication)
        
    Returns:
        Tuple of (inferred_skills_set, inference_details)
        inference_details maps each inferred skill to the context that led to inference
    """
    if not text:
        return set(), {}
    
    text_lower = text.lower()
    explicit_skills_lower = {s.strip().lower() for s in (explicit_skills or [])}
    
    inferred_skills = set()
    inference_details = {}
    
    # Check each pattern
    for context_keyword, likely_skills in SKILL_INFERENCE_PATTERNS.items():
        # Check if context keyword appears in text
        if context_keyword in text_lower:
            # Find surrounding context (50 chars before and after)
            pattern = re.escape(context_keyword)
            matches = list(re.finditer(pattern, text_lower))
            
            for match in matches:
                start = max(0, match.start() - 50)
                end = min(len(text_lower), match.end() + 50)
                context = text_lower[start:end]
                
                # Infer skills that are likely based on this context
                for skill in likely_skills:
                    # Skip if already explicitly listed
                    if skill.lower() in explicit_skills_lower:
                        continue
                    
                    # Check if skill-related terms appear in context
                    skill_variations = [
                        skill,
                        skill.replace(" ", ""),
                        skill.replace("-", " "),
                        skill.replace("_", " "),
                    ]
                    
                    skill_found = any(
                        variation in context or 
                        any(term in context for term in skill.split() if len(term) > 3)
                        for variation in skill_variations
                    )
                    
                    if skill_found:
                        inferred_skills.add(skill)
                        if skill not in inference_details:
                            inference_details[skill] = []
                        inference_details[skill].append(f"Inferred from '{context_keyword}' context")
    
    # Additional inference: Check for project descriptions
    project_patterns = [
        r"project[:\s]+(.*?)(?=\n|experience|education|skills|$)",
        r"built\s+(.*?)(?:using|with|in)",
        r"developed\s+(.*?)(?:using|with|in)",
        r"created\s+(.*?)(?:using|with|in)",
        r"implemented\s+(.*?)(?:using|with|in)",
    ]
    
    for pattern in project_patterns:
        matches = re.findall(pattern, text_lower, re.IGNORECASE | re.DOTALL)
        for match in matches:
            project_desc = match[:200]  # Limit context
            
            # Check for technology mentions
            tech_keywords = {
                "python": ["python", "django", "flask", "pandas", "numpy"],
                "java": ["java", "spring", "hibernate"],
                "javascript": ["javascript", "js", "node", "react", "vue", "angular"],
                "sql": ["sql", "database", "mysql", "postgresql"],
                "aws": ["aws", "amazon web services", "s3", "ec2"],
                "docker": ["docker", "containerization"],
                "kubernetes": ["kubernetes", "k8s"],
                "react": ["react", "reactjs", "react.js"],
                "node.js": ["node", "nodejs", "node.js", "express"],
            }
            
            for skill, keywords in tech_keywords.items():
                if any(kw in project_desc for kw in keywords):
                    if skill.lower() not in explicit_skills_lower:
                        inferred_skills.add(skill)
                        if skill not in inference_details:
                            inference_details[skill] = []
                        inference_details[skill].append("Inferred from project description")
    
    # Infer from experience descriptions
    experience_patterns = [
        r"experience[:\s]+(.*?)(?=\n|education|skills|projects|$)",
        r"worked\s+(?:with|on|in)\s+(.*?)(?:\.|,|\n)",
        r"responsible\s+for\s+(.*?)(?:\.|,|\n)",
    ]
    
    for pattern in experience_patterns:
        matches = re.findall(pattern, text_lower, re.IGNORECASE | re.DOTALL)
        for match in matches:
            exp_desc = match[:200]
            
            # Check for common technology patterns
            if "api" in exp_desc or "rest" in exp_desc:
                if "api" not in explicit_skills_lower and "rest api" not in explicit_skills_lower:
                    inferred_skills.add("REST API")
                    if "REST API" not in inference_details:
                        inference_details["REST API"] = []
                    inference_details["REST API"].append("Inferred from API development experience")
            
            if "database" in exp_desc or "sql" in exp_desc:
                if "sql" not in explicit_skills_lower:
                    inferred_skills.add("SQL")
                    if "SQL" not in inference_details:
                        inference_details["SQL"] = []
                    inference_details["SQL"].append("Inferred from database experience")
    
    return inferred_skills, inference_details


def combine_explicit_and_inferred_skills(
    explicit_skills: List[str],
    resume_text: str
) -> Dict[str, any]:
    """
    Combine explicitly listed skills with inferred skills.
    
    Returns:
        Dictionary with:
        - all_skills: Combined set of explicit and inferred skills
        - explicit_skills: List of explicitly listed skills
        - inferred_skills: List of inferred skills
        - inference_details: Details about how each skill was inferred
    """
    # Extract explicit skills from list
    explicit_set = set()
    for skill_line in explicit_skills:
        for skill in skill_line.split(','):
            skill = skill.strip()
            if skill:
                explicit_set.add(skill)
    
    # Infer additional skills
    inferred_set, inference_details = infer_skills_from_text(resume_text, list(explicit_set))
    
    # Combine (inferred skills should not duplicate explicit ones)
    all_skills = explicit_set.union(inferred_set)
    
    return {
        "all_skills": sorted(list(all_skills)),
        "explicit_skills": sorted(list(explicit_set)),
        "inferred_skills": sorted(list(inferred_set)),
        "inference_details": inference_details,
    }

