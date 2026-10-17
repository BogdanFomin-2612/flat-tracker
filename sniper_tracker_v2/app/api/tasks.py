from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_async_session
from app.models.domain import SearchTask, User, SubscriptionPlan
from app.schemas.task import TaskCreate, TaskResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_in: TaskCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    # 1. Принудительно читаем актуального юзера напрямую из БД (обход кэша сессии)
    user_result = await db.execute(select(User).where(User.id == current_user.id))
    fresh_user = user_result.scalar_one()

    # 2. Получаем лимиты пользователя по его свежей подписке
    plan_query = select(SubscriptionPlan).where(SubscriptionPlan.id == fresh_user.plan_id)
    plan_result = await db.execute(plan_query)
    user_plan = plan_result.scalar_one_or_none()
    
    max_tasks = user_plan.max_active_tasks if user_plan else 1
    interval = user_plan.check_interval_minutes if user_plan else 60

    # 3. Считаем текущие активные задачи
    count_query = select(func.count(SearchTask.id)).where(
        SearchTask.user_id == fresh_user.id,
        SearchTask.is_active == True
    )
    count_result = await db.execute(count_query)
    current_task_count = count_result.scalar() or 0

    # 4. Жесткая проверка квоты
    if current_task_count >= max_tasks:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Достигнут лимит задач для вашего тарифа ({max_tasks}). Пожалуйста, обновите подписку для расширения лимитов."
        )

    # 5. Создание задачи
    new_task = SearchTask(
        user_id=fresh_user.id,
        title=task_in.title,
        url=task_in.url,
        min_price=task_in.min_price,
        max_price=task_in.max_price,
        rooms=task_in.rooms,
        owner_only=task_in.owner_only,
        check_interval_minutes=interval
    )

    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)

    return new_task

@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(SearchTask).where(SearchTask.user_id == current_user.id)
    )
    return result.scalars().all()

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    query = select(SearchTask).where(
        SearchTask.id == task_id,
        SearchTask.user_id == current_user.id
    )
    
    result = await db.execute(query)
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена или у вас нет прав на её удаление"
        )
        
    await db.delete(task)
    await db.commit()
    
    return None