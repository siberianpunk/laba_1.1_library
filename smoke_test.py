"""smoke_test.py - файл, предназначенный для быстрого тестирования.
Ожидаемый вывод:

Выдача #1: книга "Мастер и Маргарита" → Вася Петров (2026-10-03) [не возвращена]
Ошибка: Book with id=1 is not available
[1] "Мастер и Маргарита" — Булгаков (1967), ISBN 978-5-00000-000-0 [доступна]
Library(books=2, readers=2, loans=1)
Записано в data/library.json и data/library.xml
Прочитано из JSON: Library(books=2, readers=2, loans=1)
Прочитано из XML:  Library(books=2, readers=2, loans=1)
Ошибка: Файл no_such_file.json не найден
"""

from datetime import date
from library_app import Book, Reader, Library, BookNotAvailableError
from library_app import LibraryError

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

# сохранение в оба формата

lib.save_json("data/library.json")
lib.save_xml("data/library.xml")
print("Записано в data/library.json и data/library.xml")

# загрузка из JSON в новую библиотеку

lib_from_json = Library()
lib_from_json.load_json("data/library.json")
print("Прочитано из JSON:", lib_from_json)

# загрузка из XML в ещё одну новую библиотеку

lib_from_xml = Library()
lib_from_xml.load_xml("data/library.xml")
print("Прочитано из XML: ", lib_from_xml)

# проверка обработки ошибок: несуществующий файл

try:
    Library().load_json("no_such_file.json")
except LibraryError as e:
    print("Ошибка:", e)