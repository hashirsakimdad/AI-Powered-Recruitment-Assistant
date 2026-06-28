from ai.chatbot import generate_fallback_feedback, generate_feedback


def test_fallback_feedback_shape():
    result = generate_fallback_feedback(65.0, ["docker", "kubernetes"])
    assert "overall_assessment" in result
    assert "strengths" in result
    assert "missing_skills" in result
    assert "next_steps" in result
    assert "interview_tips" in result
    assert result["source"] == "fallback"


def test_generate_feedback_without_api_key():
    profile = {
        "raw_text": "Python developer with Flask experience. 3 years of experience.",
        "skills": ["Python", "Flask"],
        "years_experience": 3,
    }
    job = {
        "title": "Backend Engineer",
        "description": "Build APIs with Python and Flask",
        "required_skills": "Python, Flask, Docker",
    }
    feedback = generate_feedback(profile, job)
    assert feedback.get("overall_assessment")
    assert feedback.get("next_steps")
    assert "score_breakdown" in feedback
