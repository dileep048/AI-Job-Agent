from uuid import UUID

from fastapi import APIRouter, Response, status

from app.schemas.education import EducationCreate, EducationResponse, EducationUpdate
from app.schemas.experience import ExperienceCreate, ExperienceResponse, ExperienceUpdate
from app.schemas.profile import ProfileCreate, ProfileResponse, ProfileUpdate
from app.schemas.skill import SkillCreate, SkillResponse, SkillUpdate
from app.security.dependencies import CurrentUser, DbSession
from app.services.education_service import EducationService
from app.services.experience_service import ExperienceService
from app.services.profile_service import ProfileService
from app.services.skill_service import SkillService

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=ProfileResponse)
def get_profile(current_user: CurrentUser, db: DbSession) -> ProfileResponse:
    return ProfileResponse.model_validate(ProfileService(db).get(current_user.id))


@router.post("", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
def create_profile(
    payload: ProfileCreate, current_user: CurrentUser, db: DbSession
) -> ProfileResponse:
    return ProfileResponse.model_validate(ProfileService(db).create(current_user.id, payload))


@router.put("", response_model=ProfileResponse)
def update_profile(
    payload: ProfileUpdate, current_user: CurrentUser, db: DbSession
) -> ProfileResponse:
    return ProfileResponse.model_validate(ProfileService(db).update(current_user.id, payload))


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_profile(current_user: CurrentUser, db: DbSession) -> Response:
    ProfileService(db).delete(current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/skills", response_model=list[SkillResponse])
def list_skills(current_user: CurrentUser, db: DbSession) -> list[SkillResponse]:
    return [SkillResponse.model_validate(s) for s in SkillService(db).list(current_user.id)]


@router.post("/skills", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
def create_skill(payload: SkillCreate, current_user: CurrentUser, db: DbSession) -> SkillResponse:
    return SkillResponse.model_validate(SkillService(db).create(current_user.id, payload))


@router.put("/skills/{skill_id}", response_model=SkillResponse)
def update_skill(
    skill_id: UUID, payload: SkillUpdate, current_user: CurrentUser, db: DbSession
) -> SkillResponse:
    return SkillResponse.model_validate(SkillService(db).update(current_user.id, skill_id, payload))


@router.delete("/skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_skill(skill_id: UUID, current_user: CurrentUser, db: DbSession) -> Response:
    SkillService(db).delete(current_user.id, skill_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/experience", response_model=list[ExperienceResponse])
def list_experience(current_user: CurrentUser, db: DbSession) -> list[ExperienceResponse]:
    return [
        ExperienceResponse.model_validate(item)
        for item in ExperienceService(db).list(current_user.id)
    ]


@router.post("/experience", response_model=ExperienceResponse, status_code=status.HTTP_201_CREATED)
def create_experience(
    payload: ExperienceCreate, current_user: CurrentUser, db: DbSession
) -> ExperienceResponse:
    return ExperienceResponse.model_validate(ExperienceService(db).create(current_user.id, payload))


@router.put("/experience/{experience_id}", response_model=ExperienceResponse)
def update_experience(
    experience_id: UUID,
    payload: ExperienceUpdate,
    current_user: CurrentUser,
    db: DbSession,
) -> ExperienceResponse:
    return ExperienceResponse.model_validate(
        ExperienceService(db).update(current_user.id, experience_id, payload)
    )


@router.delete("/experience/{experience_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_experience(experience_id: UUID, current_user: CurrentUser, db: DbSession) -> Response:
    ExperienceService(db).delete(current_user.id, experience_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/education", response_model=list[EducationResponse])
def list_education(current_user: CurrentUser, db: DbSession) -> list[EducationResponse]:
    return [
        EducationResponse.model_validate(item)
        for item in EducationService(db).list(current_user.id)
    ]


@router.post("/education", response_model=EducationResponse, status_code=status.HTTP_201_CREATED)
def create_education(
    payload: EducationCreate, current_user: CurrentUser, db: DbSession
) -> EducationResponse:
    return EducationResponse.model_validate(EducationService(db).create(current_user.id, payload))


@router.put("/education/{education_id}", response_model=EducationResponse)
def update_education(
    education_id: UUID,
    payload: EducationUpdate,
    current_user: CurrentUser,
    db: DbSession,
) -> EducationResponse:
    return EducationResponse.model_validate(
        EducationService(db).update(current_user.id, education_id, payload)
    )


@router.delete("/education/{education_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_education(education_id: UUID, current_user: CurrentUser, db: DbSession) -> Response:
    EducationService(db).delete(current_user.id, education_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
