from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.models import User
from app.database import get_db
from app.services import BookService
from app.schemas import Book, BookCreate, BookUpdate, BookList
from app.api.deps import get_current_active_user, get_current_active_superuser

router = APIRouter()


@router.get("/", response_model=BookList)
async def list_books(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> Any:
    """Get a list of books"""
    books = await BookService.get_multi(db=db, skip=skip, limit=limit)
    total = await BookService.get_total_count(db=db)

    return {
        "books": books,
        "total": total,
        "page": skip // limit + 1,
        "per_page": limit,
        "pages": (total + limit - 1) // limit
    }


@router.get("/{book_id}", response_model=Book)
async def read_book(book_id: int, db: AsyncSession = Depends(get_db)) -> Any:
    """Get a book by id"""
    book = await BookService.get(db=db, book_id=book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )
    return book


@router.post("/", response_model=Book)
async def create_book(
    book_create: BookCreate,
    current_user: User = Depends(get_current_active_superuser),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Create a new book, admin only"""
    book = await BookService.create(db=db, book_create=book_create)
    return book


@router.put("/{book_id}", response_model=Book)
async def update_book(
    book_id: int,
    book_update: BookUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """Update a book (Admin only)"""
    book = await BookService.get(db=db, book_id=book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )

    book = await BookService.update(db=db, book=book, book_update=book_update)
    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
) -> None:
    """Delete a book"""
    book = await BookService.get(db=db, book_id=book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )

    book = await BookService.delete(db, book=book)
    return None


