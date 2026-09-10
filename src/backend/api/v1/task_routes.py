from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_db, require_teacher, get_current_user
from backend.services.task_service import TaskService
from backend.schemas.task.task_create import TaskCreate
from backend.schemas.task.task_response import TaskResponse
from backend.schemas.task.task_update import TaskUpdate

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post(
    "/course/{course_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_task(
    course_id: UUID,
    data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_teacher)
):
    service = TaskService(db)

    return await service.create_task(
        current_user,
        course_id,
        data.model_dump()
    )


@router.get(
    "/course/{course_id}",
    response_model=List[TaskResponse]
)
async def get_tasks_by_course(
    course_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = TaskService(db)

    return await service.get_tasks_by_course(
        current_user,
        course_id,
        skip,
        limit
    )

@router.get(
    "/class/{class_id}",
    response_model=List[TaskResponse]
)
async def get_tasks_by_class(
    class_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = TaskService(db)

    return await service.get_tasks_by_class(
        current_user,
        class_id,
        skip,
        limit
    )

@router.get(
    "/{task_id}",
    response_model=TaskResponse
)
async def get_task_detail(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = TaskService(db)

    return await service.get_task_detail(current_user, task_id)


@router.put(
    "/{task_id}",
    response_model=TaskResponse
)
async def update_task(
    task_id: UUID,
    data: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_teacher)
):
    service = TaskService(db)

    return await service.update_task(
        current_user,
        task_id,
        data.model_dump(exclude_unset=True)
    )


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_teacher)
):
    service = TaskService(db)

    await service.delete_task(current_user, task_id)