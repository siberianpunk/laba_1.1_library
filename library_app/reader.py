"""Класс Reader — читатель библиотеки."""

from __future__ import annotations

import re

from .exceptions import ValidationError


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class Reader:
    """Модель читателя.

    Атрибуты:
        id         — уникальный идентификатор (int > 0)
        full_name  — ФИО
        email      — email
        phone      — телефон
    """

    def __init__(self, id: int, full_name: str, email: str, phone: str) -> None:
        self._validate(id=id, full_name=full_name, email=email, phone=phone)

        self._id: int = id
        self._full_name: str = full_name.strip()
        self._email: str = email.strip()
        self._phone: str = phone.strip()

    # валидация

    @staticmethod
    def _validate(id: int, full_name: str, email: str, phone: str) -> None:
        if not isinstance(id, int) or id <= 0:
            raise ValidationError("Reader.id must be a positive integer")
        if not isinstance(full_name, str) or not full_name.strip():
            raise ValidationError("Reader.full_name must be a non-empty string")
        if not isinstance(email, str) or not EMAIL_RE.match(email.strip()):
            raise ValidationError(f"Reader.email is invalid: {email!r}")
        if not isinstance(phone, str) or not phone.strip():
            raise ValidationError("Reader.phone must be a non-empty string")

    # свойства

    @property
    def id(self) -> int:
        return self._id

    @property
    def full_name(self) -> str:
        return self._full_name

    @property
    def email(self) -> str:
        return self._email

    @property
    def phone(self) -> str:
        return self._phone

    # магические методы

    def __str__(self) -> str:
        return (
            f"[{self._id}] {self._full_name} <{self._email}>, "
            f"тел.: {self._phone}"
        )

    def __repr__(self) -> str:
        return (
            f"Reader(id={self._id}, full_name={self._full_name!r}, "
            f"email={self._email!r})"
        )

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Reader) and self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)

    # (де)сериализация 

    def to_dict(self) -> dict:
        return {
            "id": self._id,
            "full_name": self._full_name,
            "email": self._email,
            "phone": self._phone,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Reader":
        return cls(
            id=data["id"],
            full_name=data["full_name"],
            email=data["email"],
            phone=data["phone"],
        )