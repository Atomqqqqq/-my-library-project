my_python_project/
├── app.py
├── database.py
├── models.py
├── requirements.txt
└── README.md
Создаем файлы:
requirements.txt

txt
sqlite3
Создаем файлы:
require.txt

txt
sqlite3
импорт sqlite3
из моделей импорт create_tables

class DatabaseManager:
"""Класс для управления базой данных SQLite"""

def __init__(self, db_name="library.db"):
    self.db_name = db_name
    self.connection = None

def connect(self):
    """Установка соединения с базой данных"""
    try:
        self.connection = sqlite3.connect(self.db_name)
        print("✅ Соединение с базой данных установлено")
        return self.connection
    except sqlite3.Error as e:
        print(f"❌ Ошибка подключения к базе: {e}")
        return None

def disconnect(self):
    """Закрытие соединения с базой данных"""
    if self.connection:
        self.connection.close()
        print("✅ Соединение с базой данных закрыто")

def initialize_database(self):
    """Инициализация базы данных и создание таблиц"""
    connection = self.connect()
    if connection:
        create_tables(connection)
        self.disconnect()
models.py - модели данных
def create_tables(connection):
"""
Создание таблиц в базе данных

Args:
    connection: соединение с базой данных SQLite
"""
cursor = connection.cursor()

# Создание таблицы книг
cursor.execute('''
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        year INTEGER,
        is_available BOOLEAN DEFAULT 1
    )
''')

# Создание таблицы пользователей
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL
    )
''')

connection.commit()
print("✅ Таблицы успешно созданы")
Класс Книга:
"""Класс для представления книги"""

def __init__(self, title, author, year, is_available=True):
    self.title = title
    self.author = author
    self.year = year
    self.is_available = is_available

def save(self, connection):
    """Сохранение книги в базу данных"""
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO books (title, author, year, is_available)
        VALUES (?, ?, ?, ?)
    ''', (self.title, self.author, self.year, self.is_available))
    connection.commit()
    return cursor.lastrowid
class User:
"""Класс для представления пользователя"""

def __init__(self, name, email):
    self.name = name
    self.email = email

def save(self, connection):
    """Сохранение пользователя в базу данных"""
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO users (name, email)
        VALUES (?, ?)
    ''', (self.name, self.email))
    connection.commit()
    return cursor.lastrowid
app.py - основной файл приложения
из импорта базы данных DatabaseManager
из импорта моделей Книга, Пользователь

def main():
"""
Основная функция приложения
Демонстрирует работу с базой данных
"""
# Инициализация менеджера
базы данных db_manager = DatabaseManager()

# Создание таблиц
print("🔄 Инициализация базы данных...")
db_manager.initialize_database()

# Подключение к базе данных
connection = db_manager.connect()

if connection:
    try:
        # Создание тестовых данных
        print("\n📚 Добавление книг в библиотеку...")
        
        # Создание книг
        books = [
            Book("Война и мир", "Лев Толстой", 1869),
            Book("Преступление и наказание", "Федор Достоевский", 1866),
            Book("Мастер и Маргарита", "Михаил Булгаков", 1967)
        ]
        
        # Сохранение книг в базу
        for book in books:
            book_id = book.save(connection)
            print(f"✅ Добавлена книга: {book.title} (ID: {book_id})")
        
        # Создание пользователей
        print("\n👥 Добавление пользователей...")
        users = [
            User("Иван Иванов", "ivan@example.com"),
            User("Петр Петров", "petr@example.com")
        ]
        
        for user in users:
            user_id = user.save(connection)
            print(f"✅ Добавлен пользователь: {user.name} (ID: {user_id})")
        
        # Демонстрация чтения данных
        print("\n📖 Список всех книг:")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM books")
        books = cursor.fetchall()
        
        for book in books:
            print(f"ID: {book[0]}, Название: {book[1]}, Автор: {book[2]}, Год: {book[3]}")
        
        print("\n👥 Список всех пользователей:")
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        
        for user in users:
            print(f"ID: {user[0]}, Имя: {user[1]}, Email: {user[2]}")
            
    except Exception as e:
        print(f"❌ Ошибка при работе с базой данных: {e}")
    finally:
        # Закрытие соединения
        db_manager.disconnect()

print("\n🎉 Программа успешно завершена!")
если имя == " main ":
main()
[README.md]
