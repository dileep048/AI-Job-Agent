from __future__ import annotations

import re

_NON_ALNUM = re.compile(r"[^a-z0-9+.#]+")

ALIASES: dict[str, str] = {
    "js": "javascript",
    "node": "javascript",
    "nodejs": "javascript",
    "node.js": "javascript",
    "ts": "typescript",
    "py": "python",
    "python3": "python",
    "golang": "go",
    "postgres": "postgresql",
    "psql": "postgresql",
    "k8s": "kubernetes",
    "gcp": "google cloud",
    "amazon web services": "aws",
    "react.js": "react",
    "reactjs": "react",
    "next": "next.js",
    "nextjs": "next.js",
    "vuejs": "vue",
    "vue.js": "vue",
    "ci/cd": "ci cd",
    "c++": "cpp",
    "c#": "csharp",
    "ml": "machine learning",
    "ai": "artificial intelligence",
    "llms": "llm",
    "large language models": "llm",
    "rest apis": "rest",
    "restful": "rest",
    "fastapi": "fastapi",
}


def normalize_skill(value: str) -> str:
    text = (value or "").strip().lower()
    text = text.replace("&", " and ")
    text = _NON_ALNUM.sub(" ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return ALIASES.get(text, text)


def skill_tokens(value: str) -> set[str]:
    key = normalize_skill(value)
    if not key:
        return set()
    parts = {key, *key.split()}
    return {part for part in parts if len(part) > 1}


def skills_match(required: str, candidate: str) -> bool:
    req = normalize_skill(required)
    cand = normalize_skill(candidate)
    if not req or not cand:
        return False
    if req == cand:
        return True
    if req in cand or cand in req:
        return len(min(req, cand, key=len)) >= 3
    req_tokens = skill_tokens(req)
    cand_tokens = skill_tokens(cand)
    if req in cand_tokens or cand in req_tokens:
        return True
    overlap = req_tokens & cand_tokens
    return bool(overlap) and (req in cand or any(token == req for token in cand_tokens))
