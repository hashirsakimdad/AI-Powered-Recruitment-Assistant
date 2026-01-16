"""
Section-Aware Feedback Control
Generates unique, section-specific feedback for each resume section.
Ensures no repetitive feedback and all suggestions are derived from actual resume content.
"""
import re
from typing import Dict, List, Set


def extract_sections(text: str) -> Dict[str, str]:
    """
    Extract different sections from resume text.
    
    Returns:
        Dictionary mapping section names to their content
    """
    sections = {}
    text_lower = text.lower()
    
    # Common section headers
    section_patterns = {
        "summary": r"(?:summary|profile|objective|about)\s*:?\s*\n(.*?)(?=\n\s*(?:experience|education|skills|$))",
        "experience": r"(?:experience|work history|employment|career)\s*:?\s*\n(.*?)(?=\n\s*(?:education|skills|projects|$))",
        "education": r"(?:education|academic|qualifications)\s*:?\s*\n(.*?)(?=\n\s*(?:skills|experience|projects|$))",
        "skills": r"(?:skills|technical skills|competencies|proficiencies)\s*:?\s*\n(.*?)(?=\n\s*(?:experience|education|projects|$))",
        "projects": r"(?:projects|project experience)\s*:?\s*\n(.*?)(?=\n\s*(?:education|skills|experience|$))",
    }
    
    for section_name, pattern in section_patterns.items():
        matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL | re.MULTILINE)
        if matches:
            sections[section_name] = matches[0].strip()
    
    # If no structured sections found, try to infer from content
    if not sections:
        # Try to find sections by common keywords
        lines = text.split('\n')
        current_section = None
        section_content = []
        
        for line in lines:
            line_lower = line.lower().strip()
            # Check if line is a section header
            if any(keyword in line_lower for keyword in ["summary", "profile", "objective"]):
                if current_section and section_content:
                    sections[current_section] = '\n'.join(section_content)
                current_section = "summary"
                section_content = []
            elif any(keyword in line_lower for keyword in ["experience", "work", "employment"]):
                if current_section and section_content:
                    sections[current_section] = '\n'.join(section_content)
                current_section = "experience"
                section_content = []
            elif any(keyword in line_lower for keyword in ["education", "degree", "university"]):
                if current_section and section_content:
                    sections[current_section] = '\n'.join(section_content)
                current_section = "education"
                section_content = []
            elif any(keyword in line_lower for keyword in ["skills", "competencies", "technical"]):
                if current_section and section_content:
                    sections[current_section] = '\n'.join(section_content)
                current_section = "skills"
                section_content = []
            elif current_section:
                section_content.append(line)
        
        if current_section and section_content:
            sections[current_section] = '\n'.join(section_content)
    
    return sections


def generate_section_feedback(
    section_name: str,
    section_content: str,
    resume_data: Dict[str, any],
    job_data: Dict[str, str]
) -> List[str]:
    """
    Generate section-specific feedback based on actual content.
    
    Args:
        section_name: Name of the section (e.g., "summary", "experience")
        section_content: Content of the section
        resume_data: Full parsed resume data
        job_data: Job posting data
        
    Returns:
        List of section-specific feedback suggestions
    """
    if not section_content or len(section_content.strip()) < 10:
        return [f"The {section_name} section appears to be missing or too brief. Consider adding relevant content."]
    
    feedback = []
    content_lower = section_content.lower()
    job_title = job_data.get("title", "").lower()
    job_desc = job_data.get("description", "").lower()
    required_skills = {s.strip().lower() for s in job_data.get("required_skills", "").split(",") if s.strip()}
    
    # Section-specific feedback rules
    if section_name == "summary":
        # Check for metrics/quantification
        has_numbers = bool(re.search(r'\d+', section_content))
        if not has_numbers:
            feedback.append("Add quantifiable achievements or metrics to your summary (e.g., '5 years of experience', 'increased revenue by 20%').")
        
        # Check length
        if len(section_content) < 50:
            feedback.append("Summary section is too brief. Expand to 2-3 sentences highlighting key qualifications.")
        elif len(section_content) > 200:
            feedback.append("Summary section is lengthy. Condense to 2-3 impactful sentences.")
        
        # Check for job-relevant keywords
        job_keywords = set(job_title.split() + job_desc.split()[:10])
        section_keywords = set(content_lower.split())
        overlap = job_keywords.intersection(section_keywords)
        if len(overlap) < 2:
            feedback.append("Incorporate relevant keywords from the job description into your summary to improve ATS matching.")
    
    elif section_name == "experience":
        # Check for action verbs
        action_verbs = ["developed", "created", "implemented", "managed", "led", "designed", "built", "improved", "optimized"]
        has_action_verbs = any(verb in content_lower for verb in action_verbs)
        if not has_action_verbs:
            feedback.append("Use strong action verbs (e.g., 'developed', 'implemented', 'led') to describe your achievements.")
        
        # Check for metrics
        has_metrics = bool(re.search(r'\d+%|\$\d+|\d+\s*(years|months|people|users)', content_lower))
        if not has_metrics:
            feedback.append("Quantify your achievements with specific numbers, percentages, or impact metrics.")
        
        # Check for STAR format indicators
        has_results = any(word in content_lower for word in ["result", "impact", "achieved", "increased", "reduced"])
        if not has_results:
            feedback.append("Include results and outcomes for each role using the STAR method (Situation, Task, Action, Result).")
        
        # Check job relevance
        job_skills_in_exp = [skill for skill in required_skills if skill in content_lower]
        if job_skills_in_exp:
            feedback.append(f"Good: Your experience mentions relevant skills: {', '.join(job_skills_in_exp[:3])}.")
        else:
            feedback.append("Highlight how your experience aligns with the job requirements more explicitly.")
    
    elif section_name == "education":
        # Check for degree information
        has_degree = bool(re.search(r'(bachelor|master|ph\.?d|bs|ms|ba|ma)', content_lower))
        if not has_degree:
            feedback.append("Include your degree type and field of study in the education section.")
        
        # Check for institution
        has_institution = any(word in content_lower for word in ["university", "college", "institute", "school"])
        if not has_institution:
            feedback.append("Include the name of your educational institution.")
        
        # Check for graduation date or year
        has_date = bool(re.search(r'\b(19|20)\d{2}\b', content_lower))
        if not has_date:
            feedback.append("Consider including your graduation year or expected graduation date.")
    
    elif section_name == "skills":
        # Extract skills from section
        section_skills = set()
        for line in section_content.split('\n'):
            for skill in line.split(','):
                skill = skill.strip().lower()
                if skill:
                    section_skills.add(skill)
        
        # Check for required skills
        missing_in_section = required_skills - section_skills
        if missing_in_section and len(missing_in_section) <= 5:
            feedback.append(f"Consider adding these job-relevant skills if you have them: {', '.join(list(missing_in_section)[:3])}.")
        
        # Check for technical skills organization
        if len(section_skills) > 10:
            feedback.append("Organize skills into categories (e.g., 'Programming Languages', 'Frameworks', 'Tools') for better readability.")
        
        # Check for proficiency levels
        has_levels = any(word in content_lower for word in ["expert", "proficient", "familiar", "beginner", "advanced"])
        if not has_levels and len(section_skills) > 5:
            feedback.append("Consider indicating proficiency levels for key skills to provide more context.")
    
    elif section_name == "projects":
        # Check for project descriptions
        if len(section_content) < 100:
            feedback.append("Expand project descriptions to include technologies used, your role, and key achievements.")
        
        # Check for links or repositories
        has_links = bool(re.search(r'http|github|gitlab|bitbucket', content_lower))
        if not has_links:
            feedback.append("Include links to project repositories or live demos if available.")
        
        # Check for technologies mentioned
        tech_keywords = ["python", "java", "javascript", "react", "node", "sql", "api", "database"]
        has_tech = any(tech in content_lower for tech in tech_keywords)
        if not has_tech:
            feedback.append("Specify the technologies, frameworks, and tools used in each project.")
    
    # Ensure feedback is based on actual content
    if not feedback:
        # Generic but content-aware feedback
        if len(section_content) < 50:
            feedback.append(f"The {section_name} section could be expanded with more specific details.")
        else:
            feedback.append(f"Review the {section_name} section to ensure it highlights your most relevant qualifications for this role.")
    
    return feedback[:3]  # Limit to 3 suggestions per section


def generate_section_aware_feedback(
    resume_data: Dict[str, any],
    job_data: Dict[str, str]
) -> Dict[str, List[str]]:
    """
    Generate section-aware feedback that is unique per section and derived from resume content.
    
    Args:
        resume_data: Parsed resume data
        job_data: Job posting data
        
    Returns:
        Dictionary mapping section names to their specific feedback
    """
    raw_text = resume_data.get("raw_text", "")
    if not raw_text:
        return {
            "general": ["Unable to extract text from resume. Please ensure the document is readable."]
        }
    
    sections = extract_sections(raw_text)
    section_feedback = {}
    used_suggestions: Set[str] = set()  # Track to avoid repetition
    
    # Generate feedback for each detected section
    for section_name, section_content in sections.items():
        feedback = generate_section_feedback(section_name, section_content, resume_data, job_data)
        
        # Filter out repetitive suggestions
        unique_feedback = []
        for suggestion in feedback:
            suggestion_lower = suggestion.lower()
            # Check if similar suggestion already exists
            is_duplicate = any(
                suggestion_lower[:30] in used or used[:30] in suggestion_lower
                for used in used_suggestions
            )
            if not is_duplicate:
                unique_feedback.append(suggestion)
                used_suggestions.add(suggestion_lower)
        
        if unique_feedback:
            section_feedback[section_name] = unique_feedback
    
    # If no sections detected, provide general feedback based on parsed data
    if not section_feedback:
        general_feedback = []
        raw_text_lower = raw_text.lower()
        
        # Skills feedback - check actual content
        resume_skills = resume_data.get("skills", [])
        required_skills = {s.strip().lower() for s in job_data.get("required_skills", "").split(",") if s.strip()}
        
        if not resume_skills:
            general_feedback.append("Add a dedicated skills section listing your technical and soft skills.")
        else:
            # Check if skills are mentioned in text
            skills_mentioned = any(skill in raw_text_lower for skill in required_skills)
            if not skills_mentioned and required_skills:
                missing_skills = list(required_skills)[:3]
                general_feedback.append(
                    f"Your resume doesn't clearly highlight these required skills: {', '.join(missing_skills)}. "
                    "Consider adding a dedicated skills section or mentioning them in your experience."
                )
        
        # Experience feedback - check actual content
        years_exp = resume_data.get("years_experience", 0)
        has_experience_keywords = any(kw in raw_text_lower for kw in ["experience", "work", "employment", "position", "role"])
        
        if years_exp == 0 and not has_experience_keywords:
            general_feedback.append("Include your work experience with specific roles, responsibilities, and achievements.")
        elif years_exp > 0:
            # Check if experience is quantified
            has_metrics = bool(re.search(r'\d+%|\$\d+|\d+\s*(years|months|people|users|projects)', raw_text_lower))
            if not has_metrics:
                general_feedback.append(
                    f"With {years_exp} years of experience, add specific metrics and quantifiable achievements to demonstrate impact."
                )
        
        # Education feedback - check actual content
        education = resume_data.get("education", [])
        has_education_keywords = any(kw in raw_text_lower for kw in ["education", "degree", "university", "college", "bachelor", "master"])
        
        if not education and not has_education_keywords:
            general_feedback.append("Include your educational background with degrees and institutions.")
        
        # Job-specific feedback
        job_title = job_data.get("title", "").lower()
        job_desc = job_data.get("description", "").lower()
        
        # Check if resume mentions job-relevant terms
        job_keywords = set(job_title.split() + job_desc.split()[:15])
        resume_keywords = set(raw_text_lower.split())
        keyword_overlap = len(job_keywords.intersection(resume_keywords))
        
        if keyword_overlap < 5:
            general_feedback.append(
                "Your resume uses different terminology than the job description. "
                "Incorporate key phrases and terms from the job posting to improve ATS matching."
            )
        elif keyword_overlap < 10:
            general_feedback.append(
                f"Good keyword alignment ({keyword_overlap} matching terms). "
                "Consider adding a few more job-specific terms to further optimize your resume."
            )
        
        # Resume length feedback
        if len(raw_text) < 500:
            general_feedback.append("Your resume appears brief. Expand sections with more detail about your achievements and responsibilities.")
        elif len(raw_text) > 3000:
            general_feedback.append("Your resume is quite lengthy. Consider condensing to 1-2 pages while keeping the most relevant information.")
        
        if general_feedback:
            section_feedback["general"] = general_feedback[:5]  # Limit to 5 general suggestions
    
    return section_feedback

