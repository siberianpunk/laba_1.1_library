"""library.py - класс Library (фасад предметной области «Библиотека»)."""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path
from typing import List, Optional

from .book import Book
from .exceptions import (
    BookNotAvailableError,
    BookNotFoundError,
    LoanNotFoundError,
    LibraryError,
    ReaderNotFoundError,
    ValidationError,
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

    # свойства-обёртки только для чтения

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
        book = self.find_book_by_id(book_id)
        reader = self.find_reader_by_id(reader_id)

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
        loan = self.find_loan_by_id(loan_id)
        loan.close(return_date)
        loan.book.is_available = True

    # внутренний счётчик выдач

    def _allocate_loan_id(self) -> int:
        current = self._next_loan_id
        self._next_loan_id += 1
        return current

    # сохранение в JSON

    def save_json(self, path: str) -> None:
        """Сохранить состояние библиотеки в JSON-файл.

        Ошибки записи (нет прав, нет места и т.п.) превращаются
        в LibraryError, чтобы программа не падала.
        """
        data = {
            "books": [b.to_dict() for b in self._books],
            "readers": [r.to_dict() for r in self._readers],
            "loans": [l.to_dict() for l in self._loans],
            "next_loan_id": self._next_loan_id,
        }

        try:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except OSError as e:
            raise LibraryError(f"Не удалось записать JSON в {path}: {e}") from e

    # загрузка из JSON

    def load_json(self, path: str) -> None:
        """Загрузить состояние библиотеки из JSON-файла.

        Любая проблема (нет файла, битый JSON, нехватка полей,
        неверные типы) превращается в понятное исключение, а не
        валит программу.
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            raise LibraryError(f"Файл {path} не найден") from None
        except json.JSONDecodeError as e:
            raise ValidationError(f"Некорректный JSON в {path}: {e}") from e
        except OSError as e:
            raise LibraryError(f"Ошибка чтения {path}: {e}") from e

        # сначала строим новые коллекции в локальных переменных,
        # потом — только если всё ок — заменяем состояние библиотеки.
        try:
            books = [Book.from_dict(b) for b in data["books"]]
            readers = [Reader.from_dict(r) for r in data["readers"]]
            books_by_id = {b.id: b for b in books}
            readers_by_id = {r.id: r for r in readers}
            loans = [
                Loan.from_dict(l, books_by_id, readers_by_id)
                for l in data["loans"]
            ]
            next_loan_id = int(data["next_loan_id"])
        except KeyError as e:
            raise ValidationError(f"Отсутствует обязательное поле: {e}") from e
        except (TypeError, ValueError) as e:
            raise ValidationError(f"Некорректные данные в {path}: {e}") from e

        self._books = books
        self._readers = readers
        self._loans = loans
        self._next_loan_id = next_loan_id

    # сохранение в XML

    def save_xml(self, path: str) -> None:
        """Сохранить состояние библиотеки в XML-файл."""
        root = ET.Element("library")

        books_el = ET.SubElement(root, "books")
        for b in self._books:
            book_el = ET.SubElement(books_el, "book", {
                "id": str(b.id),
                "is_available": str(b.is_available).lower(),
            })
            ET.SubElement(book_el, "title").text = b.title
            ET.SubElement(book_el, "author").text = b.author
            ET.SubElement(book_el, "isbn").text = b.isbn
            ET.SubElement(book_el, "year").text = str(b.year)

        readers_el = ET.SubElement(root, "readers")
        for r in self._readers:
            reader_el = ET.SubElement(readers_el, "reader", {"id": str(r.id)})
            ET.SubElement(reader_el, "full_name").text = r.full_name
            ET.SubElement(reader_el, "email").text = r.email
            ET.SubElement(reader_el, "phone").text = r.phone

        loans_el = ET.SubElement(root, "loans")
        for l in self._loans:
            loan_el = ET.SubElement(loans_el, "loan", {
                "id": str(l.id),
                "book_id": str(l.book.id),
                "reader_id": str(l.reader.id),
                "is_returned": str(l.is_returned).lower(),
            })
            ET.SubElement(loan_el, "loan_date").text = l.loan_date.isoformat()
            # пустой тег, если книга ещё не возвращена
            return_el = ET.SubElement(loan_el, "return_date")
            if l.return_date is not None:
                return_el.text = l.return_date.isoformat()

        ET.SubElement(root, "next_loan_id").text = str(self._next_loan_id)

        tree = ET.ElementTree(root)
        try:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            ET.indent(tree, space="    ")  # Python 3.9+
            tree.write(path, encoding="UTF-8", xml_declaration=True)
        except OSError as e:
            raise LibraryError(f"Не удалось записать XML в {path}: {e}") from e

    # загрузка из XML

    def load_xml(self, path: str) -> None:
        """Загрузить состояние библиотеки из XML-файла."""
        try:
            tree = ET.parse(path)
        except FileNotFoundError:
            raise LibraryError(f"Файл {path} не найден") from None
        except ET.ParseError as e:
            raise ValidationError(f"Некорректный XML в {path}: {e}") from e
        except OSError as e:
            raise LibraryError(f"Ошибка чтения {path}: {e}") from e

        root = tree.getroot()
        if root.tag != "library":
            raise ValidationError(
                f"Ожидался корневой тег <library>, получен <{root.tag}>"
            )

        # всё строим в локальных переменных, состояние меняем в конце
        try:
            books = []
            books_el = root.find("books")
            if books_el is None:
                raise ValidationError("Отсутствует секция <books>")
            for book_el in books_el.findall("book"):
                books.append(Book(
                    id=int(book_el.get("id")),
                    title=book_el.findtext("title", ""),
                    author=book_el.findtext("author", ""),
                    isbn=book_el.findtext("isbn", ""),
                    year=int(book_el.findtext("year", "0")),
                    is_available=(
                        book_el.get("is_available", "true").lower() == "true"
                    ),
                ))

            readers = []
            readers_el = root.find("readers")
            if readers_el is None:
                raise ValidationError("Отсутствует секция <readers>")
            for reader_el in readers_el.findall("reader"):
                readers.append(Reader(
                    id=int(reader_el.get("id")),
                    full_name=reader_el.findtext("full_name", ""),
                    email=reader_el.findtext("email", ""),
                    phone=reader_el.findtext("phone", ""),
                ))

            books_by_id = {b.id: b for b in books}
            readers_by_id = {r.id: r for r in readers}

            loans = []
            loans_el = root.find("loans")
            if loans_el is None:
                raise ValidationError("Отсутствует секция <loans>")
            for loan_el in loans_el.findall("loan"):
                loan_date_str = loan_el.findtext("loan_date")
                if loan_date_str is None:
                    raise ValidationError(
                        f"У выдачи id={loan_el.get('id')} нет <loan_date>"
                    )
                return_date_str = loan_el.findtext("return_date")
                loans.append(Loan.from_dict(
                    {
                        "id": int(loan_el.get("id")),
                        "book_id": int(loan_el.get("book_id")),
                        "reader_id": int(loan_el.get("reader_id")),
                        "loan_date": loan_date_str,
                        "return_date": return_date_str or None,
                        "is_returned": (
                            loan_el.get("is_returned", "false").lower() == "true"
                        ),
                    },
                    books_by_id,
                    readers_by_id,
                ))

            next_loan_id_str = root.findtext("next_loan_id")
            if next_loan_id_str is None:
                raise ValidationError("Отсутствует <next_loan_id>")
            next_loan_id = int(next_loan_id_str)

        except (TypeError, ValueError) as e:
            raise ValidationError(f"Некорректные данные в {path}: {e}") from e

        self._books = books
        self._readers = readers
        self._loans = loans
        self._next_loan_id = next_loan_id

    # магические методы

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