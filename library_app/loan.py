"""Класс Loan — запись о выдаче книги читателю."""


from __future__ import annotations

from datetime import date
from typing import Optional

from .book import Book
from .exceptions import LibraryError, ValidationError
from .reader import Reader


class Loan:
    """Модель выдачи книги.

    Атрибуты:
        id           — идентификатор выдачи
        book         — выданная книга (Book)
        reader       — читатель, взявший книгу (Reader)
        loan_date    — дата выдачи (date)
        return_date  — дата возврата или None
        is_returned  — возвращена ли книга
    """

    def __init__(
        self,
        id: int,
        book: Book,
        reader: Reader,
        loan_date: date,
        return_date: Optional[date] = None,
        is_returned: bool = False,
    ) -> None:
        self._validate(
            id=id, book=book, reader=reader,
            loan_date=loan_date, return_date=return_date,
        )

        self._id: int = id
        self._book: Book = book
        self._reader: Reader = reader
        self._loan_date: date = loan_date
        self._return_date: Optional[date] = return_date
        self._is_returned: bool = bool(is_returned)

    # валидация

    @staticmethod
    def _validate(
        id: int,
        book: Book,
        reader: Reader,
        loan_date: date,
        return_date: Optional[date],
    ) -> None:
        if not isinstance(id, int) or id <= 0:
            raise ValidationError("Loan.id must be a positive integer")
        if not isinstance(book, Book):
            raise ValidationError("Loan.book must be a Book instance")
        if not isinstance(reader, Reader):
            raise ValidationError("Loan.reader must be a Reader instance")
        if not isinstance(loan_date, date):
            raise ValidationError("Loan.loan_date must be a date")
        if return_date is not None and return_date < loan_date:
            raise ValidationError(
                "Loan.return_date cannot be earlier than Loan.loan_date"
            )

    # свойства

    @property
    def id(self) -> int:
        return self._id

    @property
    def book(self) -> Book:
        return self._book

    @property
    def reader(self) -> Reader:
        return self._reader

    @property
    def loan_date(self) -> date:
        return self._loan_date

    @property
    def return_date(self) -> Optional[date]:
        return self._return_date

    @property
    def is_returned(self) -> bool:
        return self._is_returned

    # логика

    def close(self, return_date: Optional[date] = None) -> None:
        """Закрыть выдачу: зафиксировать дату возврата."""
        if self._is_returned:
            raise LibraryError(f"Loan {self._id} is already closed")

        new_date = return_date or date.today()
        if new_date < self._loan_date:
            raise ValidationError(
                "Return date cannot be earlier than loan date"
            )

        self._return_date = new_date
        self._is_returned = True

    # магические методы

    def __str__(self) -> str:
        status = (
            f"возвращена {self._return_date}" if self._is_returned
            else "не возвращена"
        )
        return (
            f"Выдача #{self._id}: книга \"{self._book.title}\" "
            f"→ {self._reader.full_name} ({self._loan_date}) [{status}]"
        )

    def __repr__(self) -> str:
        return (
            f"Loan(id={self._id}, book_id={self._book.id}, "
            f"reader_id={self._reader.id}, is_returned={self._is_returned})"
        )

    # (де)сериализация

    def to_dict(self) -> dict:
        return {
            "id": self._id,
            "book_id": self._book.id,
            "reader_id": self._reader.id,
            "loan_date": self._loan_date.isoformat(),
            "return_date": (
                self._return_date.isoformat() if self._return_date else None
            ),
            "is_returned": self._is_returned,
        }

    @classmethod
    def from_dict(
        cls,
        data: dict,
        books_by_id: dict,
        readers_by_id: dict,
    ) -> "Loan":
        book_id = data["book_id"]
        reader_id = data["reader_id"]

        if book_id not in books_by_id:
            raise ValidationError(f"Loan references unknown book_id={book_id}")
        if reader_id not in readers_by_id:
            raise ValidationError(
                f"Loan references unknown reader_id={reader_id}"
            )

        return_date = data.get("return_date")

        return cls(
            id=data["id"],
            book=books_by_id[book_id],
            reader=readers_by_id[reader_id],
            loan_date=date.fromisoformat(data["loan_date"]),
            return_date=(
                date.fromisoformat(return_date) if return_date else None
            ),
            is_returned=data.get("is_returned", False),
        )