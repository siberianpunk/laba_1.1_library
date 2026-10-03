"""
Иерархия собственных исключений предметной области «Библиотека».

Все собственные исключения наследуются от LibraryError
"""


class LibraryError(Exception):
    """Базовое исключение для всех ошибок предметной области."""

    def __init__(self, message: str = "Library error") -> None:
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return self.message


class ValidationError(LibraryError):
    """Ошибка валидации данных (некорректные поля сущности)."""

    def __init__(self, message: str = "Validation failed") -> None:
        super().__init__(message)


class BookNotFoundError(LibraryError):
    """Книга с указанным идентификатором не найдена."""

    def __init__(self, book_id: int) -> None:
        super().__init__(f"Book with id={book_id} not found")
        self.book_id = book_id


class BookNotAvailableError(LibraryError):
    """Книга уже выдана другому читателю."""

    def __init__(self, book_id: int) -> None:
        super().__init__(f"Book with id={book_id} is not available")
        self.book_id = book_id


class ReaderNotFoundError(LibraryError):
    """Читатель с указанным идентификатором не найден."""

    def __init__(self, reader_id: int) -> None:
        super().__init__(f"Reader with id={reader_id} not found")
        self.reader_id = reader_id


class LoanNotFoundError(LibraryError):
    """Выдача с указанным идентификатором не найдена."""

    def __init__(self, loan_id: int) -> None:
        super().__init__(f"Loan with id={loan_id} not found")
        self.loan_id = loan_id