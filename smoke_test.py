"""smoke_test.py - файл, предназначенный для быстрого тестирования.
Ожидаемый вывод:

Выдача #1: книга "Мастер и Маргарита" → Вася Петров (2026-10-03) [не возвращена]
Ошибка: Book with id=1 is not available
[1] "Мастер и Маргарита" — Булгаков (1967), ISBN 978-5-00000-000-0 [доступна]
Library(books=2, readers=2, loans=1)

"""

from datetime import date
from library_app import Book, Reader, Library, BookNotAvailableError

lib = Library()

lib.add_book(Book(1, "Мастер и Маргарита", "Булгаков", "978-5-00000-000-0", 1967))
lib.add_book(Book(2, "1984", "Оруэлл", "978-5-00000-001-7", 1949))
lib.add_reader(Reader(1, "Вася Петров", "vasya@example.com", "+7-927-228-67-69"))
lib.add_reader(Reader(2, "Петя Васечкин", "petya@example.com", "+7-927-306-13-37"))

loan = lib.issue_loan(book_id=1, reader_id=1)
print(loan)

try:
    lib.issue_loan(book_id=1, reader_id=2)
except BookNotAvailableError as e:
    print("Ошибка:", e)

lib.return_loan(loan.id)
print(lib.find_book_by_id(1))
print(lib)