from ai.llm_scorer import build_scoring_prompt


def test_build_scoring_prompt_no_keyerror():
    """JSON schema braces in CV_SCORING_PROMPT must not break str.format()."""
    profile = {"raw_text": "Python developer with 3 years experience."}
    job = {
        "title": "Backend Engineer",
        "required_skills": "Python, Flask",
        "description": "Build REST APIs.",
    }
    prompt = build_scoring_prompt(profile, job)
    assert "Backend Engineer" in prompt
    assert "Python developer" in prompt
    assert '"score": 78' in prompt


def test_build_scoring_prompt_escapes_user_braces():
    profile = {"raw_text": "Skills: {python}"}
    job = {
        "title": "Role {senior}",
        "required_skills": "Python",
        "description": "Build {APIs}.",
    }
    prompt = build_scoring_prompt(profile, job)
    assert "Role (senior)" in prompt
    assert "(python)" in prompt
    assert "(APIs)" in prompt

def test_build_scoring_prompt_truncates_long_resume():
    profile = {"raw_text": "x" * 20000}
    job = {"title": "Role", "required_skills": "", "description": ""}
    prompt = build_scoring_prompt(profile, job)
    assert "...[truncated]" in prompt
