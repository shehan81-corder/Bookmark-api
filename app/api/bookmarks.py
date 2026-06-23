from sqlalchemy import text
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.bookmark import Bookmark
from app.models.tag import Tag
from app.models.user import User
from app.schemas.bookmarks import BookmarkCreate, BookmarkUpdate, BookmarkResponse
from datetime import date
from sqlalchemy import func
from typing import Optional
from app.core.security import get_current_user
from app.models.tag import Tag
from app.core.exceptions import BookmarkNotFound

router = APIRouter(tags=["bookmarks"])


def get_or_create_tags(tag_names: list[str], db: Session) -> list[Tag]:
    tags = []
    for name in tag_names:
        tag = db.query(Tag).filter(Tag.name == name).first()
        if not tag:
            tag = Tag(name=name)
            db.add(tag)
            db.flush()
        tags.append(tag)
    return tags


@router.post("", response_model=BookmarkResponse, status_code=201, responses={
    401: {"description": "Not authenticated"},
    422: {"description": "Validation error"}
})
def create_bookmark(
    data: BookmarkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Creates a new bookmark for the current user.
    """
    bookmark = Bookmark(
        url=str(data.url),
        title=data.title,
        description=data.description,
        user_id=current_user.id
    )
    db.add(bookmark)
    db.flush()

    if data.tags:
        bookmark.tags = get_or_create_tags(data.tags, db)

    db.commit()
    db.refresh(bookmark)
    return bookmark


@router.get("/stats")
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns aggregated statistics for the current user's bookmarks
    including total counts, top tags, and monthly breakdown.
    """
    total_bookmarks = db.execute(
        text("SELECT COUNT(*) FROM bookmarks WHERE user_id = :user_id"),
        {"user_id": current_user.id}
    ).scalar()

    total_tags = db.execute(
        text("""
            SELECT COUNT(DISTINCT t.id)
            FROM tags t
            JOIN bookmark_tags bt ON bt.tag_id = t.id
            JOIN bookmarks b ON b.id = bt.bookmark_id
            WHERE b.user_id = :user_id
        """),
        {"user_id": current_user.id}
    ).scalar()

    top_tags = db.execute(
        text("""
            SELECT t.name, COUNT(bt.bookmark_id) as count
            FROM tags t
            JOIN bookmark_tags bt ON bt.tag_id = t.id
            JOIN bookmarks b ON b.id = bt.bookmark_id
            WHERE b.user_id = :user_id
            GROUP BY t.name
            ORDER BY count DESC
            LIMIT 5
        """),
        {"user_id": current_user.id}
    ).fetchall()

    bookmarks_per_month = db.execute(
        text("""
            SELECT strftime('%Y-%m', created_at) as month, COUNT(*) as count
            FROM bookmarks
            WHERE user_id = :user_id
            GROUP BY month
            ORDER BY month ASC
        """),
        {"user_id": current_user.id}
    ).fetchall()

    return {
        "total_bookmarks": total_bookmarks,
        "total_tags": total_tags,
        "top_tags": [{"name": row[0], "count": row[1]} for row in top_tags],
        "bookmarks_per_month": [{"month": row[0], "count": row[1]} for row in bookmarks_per_month]
    }


@router.get("/{bookmark_id}", response_model=BookmarkResponse)
def get_bookmark(
    bookmark_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns the bookmark with the specified ID if it belongs to the current user.
    """
    bookmark = db.query(Bookmark).filter(
        Bookmark.id == bookmark_id,
        Bookmark.user_id == current_user.id
    ).first()
    if not bookmark:
        raise BookmarkNotFound()
    return bookmark


@router.put("/{bookmark_id}", response_model=BookmarkResponse)
def update_bookmark(
    bookmark_id: int,
    data: BookmarkUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Updates the bookmark with the specified ID if it belongs to the current user.
    """
    bookmark = db.query(Bookmark).filter(
        Bookmark.id == bookmark_id,
        Bookmark.user_id == current_user.id
    ).first()
    if not bookmark:
        raise BookmarkNotFound()

    if data.url is not None:
        bookmark.url = str(data.url)
    if data.title is not None:
        bookmark.title = data.title
    if data.description is not None:
        bookmark.description = data.description
    if data.tags is not None:
        bookmark.tags = get_or_create_tags(data.tags, db)

    db.commit()
    db.refresh(bookmark)
    return bookmark


@router.delete("/{bookmark_id}", status_code=204)
def delete_bookmark(
    bookmark_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Deletes the bookmark with the specified ID if it belongs to the current user.
    """
    bookmark = db.query(Bookmark).filter(
        Bookmark.id == bookmark_id,
        Bookmark.user_id == current_user.id
    ).first()
    if not bookmark:
        raise BookmarkNotFound()

    db.delete(bookmark)
    db.commit()


@router.get("", response_model=dict)
def list_bookmarks(
    tag: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    from_date: Optional[date] = Query(None, alias="from"),
    to_date: Optional[date] = Query(None, alias="to"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns a list of bookmarks for the current user with optional filtering and pagination.
    """
    query = db.query(Bookmark).filter(Bookmark.user_id == current_user.id)

    if tag:
        query = query.filter(Bookmark.tags.any(Tag.name == tag.lower()))

    if q:
        query = query.filter(Bookmark.title.ilike(f"%{q}%"))

    if from_date:
        query = query.filter(Bookmark.created_at >= from_date)

    if to_date:
        query = query.filter(Bookmark.created_at <= to_date)

    total = query.count()

    bookmarks = query.offset((page - 1) * page_size).limit(page_size).all()

    return {
        "data": [BookmarkResponse.model_validate(b) for b in bookmarks],
        "meta": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    }
