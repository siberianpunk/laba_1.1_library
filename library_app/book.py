"""Класс Book — книга в библиотеке."""

from __future__ import annotations

from .exceptions import ValidationError


class Book:
    """Модель книги.

    Атрибуты:
        id            — уникальный идентификатор (int > 0)
        title         — название
        author        — автор
        isbn          — ISBN
        year          — год издания
        is_available  — доступна ли книга для выдачи
    """

    def __init__(
        self,
        id: int,
        title: str,
        author: str,
        isbn: str,
        year: int,
        is_available: bool = True,
    ) -> None:
        self._validate(id=id, title=title, author=author, isbn=isbn, year=year)

        self._id: int = id
        self._title: str = title.strip()
        self._author: str = author.strip()
        self._isbn: str = isbn.strip()
        self._year: int = year
        self._is_available: bool = bool(is_available)

    # валидация

    @staticmethod
    def _validate(
        id: int, title: str, author: str, isbn: str, year: int
    ) -> None:
        if not isinstance(id, int) or id <= 0:
            raise ValidationError("Book.id must be a positive integer")
        if not isinstance(title, str) or not title.strip():
            raise ValidationError("Book.title must be a non-empty string")
        if not isinstance(author, str) or not author.strip():
            raise ValidationError("Book.author must be a non-empty string")
        if not isinstance(isbn, str) or not isbn.strip():
            raise ValidationError("Book.isbn must be a non-empty string")
        if not isinstance(year, int) or year < 0 or year > 2100:
            raise ValidationError("Book.year must be between 0 and 2100")

    # свойства

    @property
    def id(self) -> int:
        return self._id

    @property
    def title(self) -> str:
        return self._title

    @property
    def author(self) -> str:
        return self._author

    @property
    def isbn(self) -> str:
        return self._isbn

    @property
    def year(self) -> int:
        return self._year

    @property
    def is_available(self) -> bool:
        return self._is_available

    @is_available.setter
    def is_available(self, value: bool) -> None:
        self._is_available = bool(value)

    # магические методы

    def __str__(self) -> str:
        status = "доступна" if self._is_available else "выдана"
        return (
            f'[{self._id}] "{self._title}" — {self._author} '
            f"({self._year}), ISBN {self._isbn} [{status}]"
        )

    def __repr__(self) -> str:
        return (
            f"Book(id={self._id}, title={self._title!r}, "
            f"author={self._author!r}, year={self._year})"
        )

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Book) and self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)

    # (де)сериализация

    def to_dict(self) -> dict:
        return {
            "id": self._id,
            "title": self._title,
            "author": self._author,
            "isbn": self._isbn,
            "year": self._year,
            "is_available": self._is_available,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Book":
        return cls(
            id=data["id"],
            title=data["title"],
            author=data["author"],
            isbn=data["isbn"],
            year=data["year"],
            is_available=data.get("is_available", True),
        )