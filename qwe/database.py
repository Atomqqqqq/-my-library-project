import psycopg2

class Database:
    def __init__(self):
        """Инициализация подключения к базе данных"""
        self.connection = None
        self.cursor = None
        self.config = self.load_config()
        
    def load_config(self):
        """Загрузка конфигурации из файла"""
        try:
            from db_config import DB_CONFIG
            return DB_CONFIG
        except ImportError:
            print("❌ Файл конфигурации не найден. Запустите setup.py сначала.")
            return None
        
    def connect(self):
        """Установка соединения с PostgreSQL"""
        if not self.config:
            return False
            
        try:
            self.connection = psycopg2.connect(
                host=self.config['host'],
                port=self.config['port'],
                database="python_db",
                user=self.config['user'],
                password=self.config['password']
            )
            self.cursor = self.connection.cursor()
            print("✅ Успешное подключение к PostgreSQL")
            return True
        except Exception as e:
            print(f"❌ Ошибка подключения: {e}")
            return False
            
    def disconnect(self):
        """Закрытие соединения с базой данных"""
        if self.connection:
            self.cursor.close()
            self.connection.close()
            print("✅ Соединение с базой данных закрыто")
            
    def execute_query(self, query, params=None):
        """Выполнение SQL запроса"""
        if not self.connection:
            print("❌ Нет подключения к базе данных")
            return False
            
        try:
            self.cursor.execute(query, params or ())
            self.connection.commit()
            return True
        except Exception as e:
            print(f"❌ Ошибка выполнения запроса: {e}")
            if self.connection:
                self.connection.rollback()
            return False
            
    def fetch_all(self, query, params=None):
        """Получение всех результатов запроса"""
        if not self.connection:
            print("❌ Нет подключения к базе данных")
            return []
            
        try:
            self.cursor.execute(query, params or ())
            return self.cursor.fetchall()
        except Exception as e:
            print(f"❌ Ошибка получения данных: {e}")
            return []
            
    def fetch_one(self, query, params=None):
        """Получение одной строки результата"""
        if not self.connection:
            print("❌ Нет подключения к базе данных")
            return None
            
        try:
            self.cursor.execute(query, params or ())
            return self.cursor.fetchone()
        except Exception as e:
            print(f"❌ Ошибка получения данных: {e}")
            return None

def test_connection():
    """Тестирование подключения к базе данных"""
    db = Database()
    if db.connect():
        print("✅ Тест подключения: УСПЕШНО")
        db.disconnect()
        return True
    else:
        print("❌ Тест подключения: НЕУДАЧНО")
        return False