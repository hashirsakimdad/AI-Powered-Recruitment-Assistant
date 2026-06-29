# Bug: KeyError in build_scoring_prompt() when scoring resumes

## Summary
Resume scoring fails with `KeyError: '\n  "score"'` when `build_scoring_prompt()` calls `.format()` on `CV_SCORING_PROMPT`.

## Steps to Reproduce
1. Start the app: `flask run`
2. Log in as a candidate
3. Upload a resume for any job posting
4. Background scoring thread crashes

## Expected Behavior
- Prompt builds successfully with job/resume placeholders filled in
- Scoring completes and dashboard shows a numeric score

## Actual Behavior
```
KeyError: '\n  "score"'
  File "ai/llm_scorer.py", line 51, in build_scoring_prompt
    return CV_SCORING_PROMPT.format(...)
```

## Root Cause
`CV_SCORING_PROMPT` contains a JSON schema example with single curly braces `{` `}`. Python's `str.format()` treats these as placeholder fields, causing a KeyError for `"score"`.

## Proposed Fix
Escape JSON example braces by doubling them (`{{` and `}}`) while keeping real placeholders like `{title}`, `{resume_text}` unchanged.

## Labels
`bug`, `scoring`, `llm`
