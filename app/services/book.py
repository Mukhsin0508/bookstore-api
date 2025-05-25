from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Book
from app.schemas.book import BookCreate, BookUpdate



class BookService:
    @staticmethod
    async def get(db: AsyncSession, book_id: int) -> Optional[Book]:
        """Get a book by id"""
        result = await db.execute(
            select(Book).where(Book.id == book_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_multi(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Book]:
        """Get multiple books in descending order"""
        result = await db.execute(
            select(Book).offset(skip).limit(limit).order_by(Book.created_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_total_count(db: AsyncSession) -> int:
        """Get a total count of books"""
        result = await db.execute(select(func.count(Book.id)))
        return result.scalar_one()

    @staticmethod
    async def create(db: AsyncSession, book_create: BookCreate) -> Book:
        """Create a new book"""
        book = Book(**book_create.model_dump())
        db.add(book)
        await db.commit()
        await db.refresh(book)
        return book

    @staticmethod
    async def update(db: AsyncSession, book: Book, book_update: BookUpdate) -> Book:
        """Update a book"""
        updated_data = book_update.model_dump(exclude_unset=True)

        for f, v in updated_data.items():
            setattr(book, f, v)

        await db.commit()
        await db.refresh(book)
        return book

    @staticmethod
    async def delete(db: AsyncSession, book: Book) -> Optional[Book]:
        """Delete a book"""
        pass

    @staticmethod
    async def check_stock(db: AsyncSession, book_id: int, quantity: int) -> bool:
        """Check if a book has enough stocks"""
        book = await BookService.get(db, book_id)
        if not book:
            return False
        return book.stock_quantity >= quantity

    @staticmethod
    async def update_stock(db: AsyncSession, book_id: int, quantity_change: int) -> Optional[Book]:
        """Update book stock (negative for deduction)"""
        book = await BookService.get(db, book_id)
        if not book:
            return None

        new_quantity = book.stock_quantity + quantity_change
        if new_quantity < 0:
            return None

        book.stock_quantity = new_quantity
        await db.commit()
        await db.refresh(book)
        return book





