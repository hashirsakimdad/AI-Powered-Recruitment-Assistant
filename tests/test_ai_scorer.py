from ai.scorer import score_candidate


def test_scorer_returns_float_between_0_and_100():
    profile = {"raw_text": "python flask developer 5 years experience skills: python, django"}
    job = {
        "title": "Dev",
        "description": "python flask api development",
        "required_skills": "python, flask, rest",
    }
    result = score_candidate(profile, job)
    assert 0 <= result["score"] <= 100


def test_scorer_handles_empty_resume():
    profile = {"raw_text": ""}
    job = {"title": "Dev", "description": "work", "required_skills": "python"}
    result = score_candidate(profile, job)
    assert "score" in result


def test_scorer_explanation_contains_required_keys():
    profile = {"raw_text": "python developer with 3 years experience"}
    job = {
        "title": "Dev",
        "description": "python backend",
        "required_skills": "python, sql",
    }
    result = score_candidate(profile, job)
    assert "skill_match" in result
    assert "experience_match" in result
    assert "rationale" in result
