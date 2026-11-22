from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ALGORITHM_VERSION = "s3.0.0"


class MatchWeights(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env", "../../.env"), extra="ignore")

    match_skill_weight: float = Field(default=0.40, alias="MATCH_SKILL_WEIGHT")
    match_experience_weight: float = Field(default=0.20, alias="MATCH_EXPERIENCE_WEIGHT")
    match_title_weight: float = Field(default=0.10, alias="MATCH_TITLE_WEIGHT")
    match_location_weight: float = Field(default=0.10, alias="MATCH_LOCATION_WEIGHT")
    match_workplace_weight: float = Field(default=0.05, alias="MATCH_WORKPLACE_WEIGHT")
    match_employment_weight: float = Field(default=0.05, alias="MATCH_EMPLOYMENT_WEIGHT")
    match_salary_weight: float = Field(default=0.10, alias="MATCH_SALARY_WEIGHT")
    match_semantic_weight: float = Field(default=0.10, alias="MATCH_SEMANTIC_WEIGHT")
    match_apply_threshold: float = Field(default=80.0, alias="MATCH_APPLY_THRESHOLD")
    match_consider_threshold: float = Field(default=65.0, alias="MATCH_CONSIDER_THRESHOLD")

    @field_validator(
        "match_skill_weight",
        "match_experience_weight",
        "match_title_weight",
        "match_location_weight",
        "match_workplace_weight",
        "match_employment_weight",
        "match_salary_weight",
        "match_semantic_weight",
    )
    @classmethod
    def _non_negative(cls, value: float) -> float:
        return max(0.0, value)

    def structured_weights(self) -> dict[str, float]:
        raw = {
            "skills": self.match_skill_weight,
            "experience": self.match_experience_weight,
            "title": self.match_title_weight,
            "location": self.match_location_weight,
            "workplace": self.match_workplace_weight,
            "employment": self.match_employment_weight,
            "salary": self.match_salary_weight,
        }
        structured_total = sum(raw.values())
        semantic = self.match_semantic_weight
        if structured_total <= 0:
            return raw
        scale = (1.0 - semantic) / structured_total if semantic < 1.0 else 0.0
        return {key: round(value * scale, 4) for key, value in raw.items()}

    def semantic_weight(self) -> float:
        return min(max(self.match_semantic_weight, 0.0), 1.0)


@lru_cache
def get_match_weights() -> MatchWeights:
    return MatchWeights()
