from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any

import httpx
from pydantic import BaseModel, Field, ValidationError

from app.config import get_settings
from app.services.matching.dto import JobRequirements, MatchResult

logger = logging.getLogger("ai_job_agent")


class SkillImportance(BaseModel):
    name: str
    importance: str = "required"


class LLMRequirements(BaseModel):
    required_skills: list[SkillImportance] = Field(default_factory=list)
    preferred_skills: list[SkillImportance] = Field(default_factory=list)
    minimum_years_experience: int | None = None
    education_requirements: list[str] = Field(default_factory=list)
    workplace_type: str | None = None


class LLMReasoning(BaseModel):
    summary: str
    strengths: list[str] = Field(default_factory=list)
    concerns: list[str] = Field(default_factory=list)


@dataclass
class LLMExtractedRequirements:
    required_skills: list[str] = field(default_factory=list)
    preferred_skills: list[str] = field(default_factory=list)
    minimum_years_experience: int | None = None


def extract_requirements_with_llm(title: str, description: str | None) -> LLMExtractedRequirements:
    payload = _chat(
        system=(
            "Extract job requirements from the posting. Return JSON only. "
            "Do not invent skills or years not supported by the text."
        ),
        user=json.dumps({"title": title, "description": (description or "")[:8000]}),
        schema_name="requirements",
        schema={
            "type": "object",
            "properties": {
                "required_skills": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "importance": {"type": "string"},
                        },
                        "required": ["name", "importance"],
                        "additionalProperties": False,
                    },
                },
                "preferred_skills": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "importance": {"type": "string"},
                        },
                        "required": ["name", "importance"],
                        "additionalProperties": False,
                    },
                },
                "minimum_years_experience": {"type": ["integer", "null"]},
                "education_requirements": {"type": "array", "items": {"type": "string"}},
                "workplace_type": {"type": ["string", "null"]},
            },
            "required": [
                "required_skills",
                "preferred_skills",
                "minimum_years_experience",
                "education_requirements",
                "workplace_type",
            ],
            "additionalProperties": False,
        },
    )
    if payload is None:
        return LLMExtractedRequirements(required_skills=[], preferred_skills=[])
    try:
        parsed = LLMRequirements.model_validate(payload)
    except ValidationError:
        logger.info("matching llm requirements validation failed")
        return LLMExtractedRequirements(required_skills=[], preferred_skills=[])
    return LLMExtractedRequirements(
        required_skills=[item.name.strip() for item in parsed.required_skills if item.name.strip()],
        preferred_skills=[item.name.strip() for item in parsed.preferred_skills if item.name.strip()],
        minimum_years_experience=parsed.minimum_years_experience,
    )


def explain_with_llm(result: MatchResult, requirements: JobRequirements) -> LLMReasoning | None:
    payload = _chat(
        system=(
            "Generate a concise match explanation from structured scores only. "
            "Never invent candidate skills, companies, titles, or years. Return JSON only."
        ),
        user=json.dumps(
            {
                "score": result.score,
                "recommendation": result.recommendation,
                "matched_skills": result.matched_skills,
                "missing_skills": result.missing_skills,
                "strengths": result.strengths,
                "concerns": result.concerns,
                "job_title": requirements.title,
                "years_required": requirements.minimum_years_experience,
            }
        ),
        schema_name="reasoning",
        schema={
            "type": "object",
            "properties": {
                "summary": {"type": "string"},
                "strengths": {"type": "array", "items": {"type": "string"}},
                "concerns": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["summary", "strengths", "concerns"],
            "additionalProperties": False,
        },
    )
    if payload is None:
        return None
    try:
        return LLMReasoning.model_validate(payload)
    except ValidationError:
        logger.info("matching llm reasoning validation failed")
        return None


def _chat(
    *,
    system: str,
    user: str,
    schema_name: str,
    schema: dict[str, Any],
) -> dict[str, Any] | None:
    settings = get_settings()
    api_key = (settings.openai_api_key or "").strip()
    if not api_key:
        return None
    body = {
        "model": settings.openai_model,
        "temperature": 0,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {"name": schema_name, "strict": True, "schema": schema},
        },
    }
    try:
        response = httpx.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=body,
            timeout=20.0,
        )
        if response.status_code >= 400:
            logger.info("matching llm request failed status=%s", response.status_code)
            return None
        content = response.json()["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        return parsed if isinstance(parsed, dict) else None
    except Exception:
        logger.info("matching llm unavailable", exc_info=True)
        return None
