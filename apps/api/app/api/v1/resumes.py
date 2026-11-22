from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, File, Response, UploadFile, status
from fastapi.responses import Response as FastAPIResponse

from app.schemas.resume import ResumeCreate, ResumeResponse, ResumeUpdate
from app.security.dependencies import CurrentUser, DbSession
from app.services.resume_service import ResumeService

router = APIRouter(prefix="/resumes", tags=["resumes"])


@router.get("", response_model=list[ResumeResponse])
def list_resumes(current_user: CurrentUser, db: DbSession) -> list[ResumeResponse]:
    return [ResumeResponse.model_validate(item) for item in ResumeService(db).list(current_user.id)]


@router.post("", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
def create_resume(
    payload: ResumeCreate, current_user: CurrentUser, db: DbSession
) -> ResumeResponse:
    return ResumeResponse.model_validate(ResumeService(db).create(current_user.id, payload))


@router.post("/upload", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    current_user: CurrentUser,
    db: DbSession,
    file: Annotated[UploadFile, File()],
) -> ResumeResponse:
    data = await file.read()
    resume = ResumeService(db).upload(
        current_user.id,
        filename=file.filename,
        content_type=file.content_type,
        data=data,
    )
    return ResumeResponse.model_validate(resume)


@router.get("/{resume_id}", response_model=ResumeResponse)
def get_resume(resume_id: UUID, current_user: CurrentUser, db: DbSession) -> ResumeResponse:
    return ResumeResponse.model_validate(ResumeService(db).get(current_user.id, resume_id))


@router.put("/{resume_id}", response_model=ResumeResponse)
def update_resume(
    resume_id: UUID, payload: ResumeUpdate, current_user: CurrentUser, db: DbSession
) -> ResumeResponse:
    return ResumeResponse.model_validate(
        ResumeService(db).update(current_user.id, resume_id, payload)
    )


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(resume_id: UUID, current_user: CurrentUser, db: DbSession) -> Response:
    ResumeService(db).delete(current_user.id, resume_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{resume_id}/set-default", response_model=ResumeResponse)
def set_default(resume_id: UUID, current_user: CurrentUser, db: DbSession) -> ResumeResponse:
    return ResumeResponse.model_validate(ResumeService(db).set_default(current_user.id, resume_id))


@router.get("/{resume_id}/download")
def download_resume(resume_id: UUID, current_user: CurrentUser, db: DbSession) -> FastAPIResponse:
    resume, data = ResumeService(db).download(current_user.id, resume_id)
    media_type = resume.file_type or "application/octet-stream"
    headers = {
        "Content-Disposition": f'attachment; filename="{resume.file_name or "resume"}"',
    }
    return FastAPIResponse(content=data, media_type=media_type, headers=headers)
