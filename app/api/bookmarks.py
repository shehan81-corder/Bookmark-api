from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.bookmark import Bookmark
from app.models.tag import Tag
from app.models.user import User
from app.schemas.bookmarks import BookmarkCreate, BookmarkUpdate, BookmarkResponse
from app.core.security import get_current_user

router = APIRouter()


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


@router.post("", response_model=BookmarkResponse, status_code=201)
def create_bookmark(
    data: BookmarkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
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


@router.get("", response_model=list[BookmarkResponse])
def list_bookmarks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Bookmark).filter(Bookmark.user_id == current_user.id).all()


@router.get("/{bookmark_id}", response_model=BookmarkResponse)
def get_bookmark(
    bookmark_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    bookmark = db.query(Bookmark).filter(
        Bookmark.id == bookmark_id,
        Bookmark.user_id == current_user.id
    ).first()
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    return bookmark


@router.put("/{bookmark_id}", response_model=BookmarkResponse)
def update_bookmark(
    bookmark_id: int,
    data: BookmarkUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    bookmark = db.query(Bookmark).filter(
        Bookmark.id == bookmark_id,
        Bookmark.user_id == current_user.id
    ).first()
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")

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
    bookmark = db.query(Bookmark).filter(
        Bookmark.id == bookmark_id,
        Bookmark.user_id == current_user.id
    ).first()
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")

    db.delete(bookmark)
    db.commit()
