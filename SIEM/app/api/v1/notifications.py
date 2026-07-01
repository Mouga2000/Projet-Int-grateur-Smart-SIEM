# app/api/v1/notifications.py
# -------------------------------
# Endpoints /api/v1/notifications -- Gestion des notifications

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.repositories.notification_repo import NotificationRepository

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/")
async def list_notifications(
    unread_only: bool = Query(False, description="Uniquement les non lues"),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Liste les notifications de l'utilisateur connecte."""
    repo = NotificationRepository(db)
    items = await repo.get_user_notifications(
        user_id=current_user["id"],
        unread_only=unread_only,
        limit=size,
        offset=(page - 1) * size,
    )
    unread = await repo.count_unread(current_user["id"])
    return {
        "items": items,
        "total": len(items),
        "page": page,
        "size": size,
        "unread_count": unread,
    }


@router.get("/unread-count")
async def unread_count(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Nombre de notifications non lues."""
    repo = NotificationRepository(db)
    count = await repo.count_unread(current_user["id"])
    return {"unread": count}


@router.patch("/{notification_id}/read")
async def mark_as_read(
    notification_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Marque une notification comme lue."""
    repo = NotificationRepository(db)
    success = await repo.mark_as_read(notification_id, current_user["id"])
    if not success:
        raise HTTPException(status_code=404, detail="Notification non trouvee")
    return {"message": "Notification marquee comme lue"}


@router.post("/read-all")
async def mark_all_as_read(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Marque toutes les notifications comme lues."""
    repo = NotificationRepository(db)
    count = await repo.mark_all_as_read(current_user["id"])
    return {"marked_as_read": count}
