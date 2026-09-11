from typing import List
from uuid import UUID

from backend.api.deps import get_current_user, get_db, require_teacher
from backend.schemas.task.task_create import TaskCreate
from backend.schemas.task.task_response import TaskResponse
from backend.schemas.task.task_update import TaskUpdate
from backend.services.task_service import TaskService
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

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
    try:
        return await service.create_task(
            current_user,
            course_id,
            data.model_dump()
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


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
    try:
        return await service.get_tasks_by_course(
            current_user,
            course_id,
            skip,
            limit
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

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
    try:
        return await service.get_tasks_by_class(
            current_user,
            class_id,
            skip,
            limit
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

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
    try:
        return await service.get_task_detail(current_user, task_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


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
    try:
        return await service.update_task(
            current_user,
            task_id,
            data.model_dump(exclude_unset=True)
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


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
    try:
        await service.delete_task(current_user, task_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
