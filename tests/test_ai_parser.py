from ai.parser import parse_resume


def test_parse_resume_returns_expected_keys():
    text = "Skills: Python, Flask\nBachelor degree\nSoftware Developer at Acme"
    result = parse_resume(text)
    assert "skills" in result
    assert "education" in result
    assert "experiences" in result
    assert "raw_text" in result
