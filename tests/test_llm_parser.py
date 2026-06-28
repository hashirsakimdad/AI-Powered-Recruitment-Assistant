import pytest

from ai.llm_parser import normalize_cv_analysis, parse_llm_json, strip_code_fences


def test_strip_code_fences_json():
    raw = '```json\n{"score": 80}\n```'
    assert strip_code_fences(raw) == '{"score": 80}'


def test_parse_llm_json_with_fences():
    raw = """Here is the result:
```json
{
  "score": 78,
  "summary": "Good fit",
  "strengths": ["Python"],
  "weaknesses": ["DevOps"],
  "recommendation": "consider"
}
```
"""
    data = parse_llm_json(raw)
    normalized = normalize_cv_analysis(data)
    assert normalized["score"] == 78.0
    assert normalized["summary"] == "Good fit"
    assert normalized["strengths"] == ["Python"]


def test_parse_llm_json_pure():
    raw = '{"score": 65, "summary": "ok", "strengths": [], "weaknesses": [], "recommendation": "consider"}'
    data = parse_llm_json(raw)
    assert data["score"] == 65


def test_parse_llm_json_missing_score_raises():
    with pytest.raises(ValueError, match="score"):
        normalize_cv_analysis({"summary": "no score"})


def test_normalize_cv_analysis_clamps_score():
    result = normalize_cv_analysis(
        {
            "score": 150,
            "summary": "x",
            "strengths": "single",
            "weaknesses": None,
            "recommendation": "hire",
        }
    )
    assert result["score"] == 100.0
    assert result["strengths"] == ["single"]
