"""Класс Library — фасад предметной области «Библиотека».

Library агрегирует книги (Book) и читателей (Reader), композирует выдачи (Loan).
"""

from __future__ import annotations

from datetime import date
from typing import List, Optional

from .book import Book
from .exceptions import (
    BookNotAvailableError,
    BookNotFoundError,
    LoanNotFoundError,
    LibraryError,
    ReaderNotFoundError,
)
from .loan import Loan
from .reader import Reader


class Library:
    """Управляющий класс библиотеки."""

    def __init__(self) -> None:
        self._books: List[Book] = []
        self._readers: List[Reader] = []
        self._loans: List[Loan] = []
        self._next_loan_id: int = 1

    # свойства-обёртки (только для чтения)

    @property
    def books(self) -> List[Book]:
        return list(self._books)

    @property
    def readers(self) -> List[Reader]:
        return list(self._readers)

    @property
    def loans(self) -> List[Loan]:
        return list(self._loans)

    # работа с книгами и читателями

    def add_book(self, book: Book) -> None:
        if any(b.id == book.id for b in self._books):
            raise LibraryError(f"Book with id={book.id} already exists")
        self._books.append(book)

    def add_reader(self, reader: Reader) -> None:
        if any(r.id == reader.id for r in self._readers):
            raise LibraryError(f"Reader with id={reader.id} already exists")
        self._readers.append(reader)

    def find_book_by_id(self, book_id: int) -> Book:
        for book in self._books:
            if book.id == book_id:
                return book
        raise BookNotFoundError(book_id)

    def find_reader_by_id(self, reader_id: int) -> Reader:
        for reader in self._readers:
            if reader.id == reader_id:
                return reader
        raise ReaderNotFoundError(reader_id)

    def find_loan_by_id(self, loan_id: int) -> Loan:
        for loan in self._loans:
            if loan.id == loan_id:
                return loan
        raise LoanNotFoundError(loan_id)

    # бизнес-логика выдачи

    def issue_loan(
        self,
        book_id: int,
        reader_id: int,
        loan_date: Optional[date] = None,
    ) -> Loan:
        """Выдать книгу читателю. Возвращает созданный Loan."""
        book = self.find_book_by_id(book_id)      # может бросить BookNotFoundError
        reader = self.find_reader_by_id(reader_id)  # ReaderNotFoundError

        if not book.is_available:
            raise BookNotAvailableError(book_id)

        loan = Loan(
            id=self._allocate_loan_id(),
            book=book,
            reader=reader,
            loan_date=loan_date or date.today(),
        )
        book.is_available = False
        self._loans.append(loan)
        return loan

    def return_loan(
        self,
        loan_id: int,
        return_date: Optional[date] = None,
    ) -> None:
        """Закрыть выдачу и вернуть книгу в фонд."""
        loan = self.find_loan_by_id(loan_id)  # может бросить LoanNotFoundError
        loan.close(return_date)               # может бросить LibraryError
        loan.book.is_available = True

    # вспомогательное

    def _allocate_loan_id(self) -> int:
        current = self._next_loan_id
        self._next_loan_id += 1
        return current

    def __str__(self) -> str:
        return (
            f"Library(books={len(self._books)}, "
            f"readers={len(self._readers)}, "
            f"loans={len(self._loans)})"
        )

    def __repr__(self) -> str:
        return (
            f"Library(books={len(self._books)}, "
            f"readers={len(self._readers)}, "
            f"loans={len(self._loans)})"
        )