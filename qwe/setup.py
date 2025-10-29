import psycopg2

def get_db_config():
    """Получение настроек базы данных от пользователя"""
    print("🔧 Настройка подключения к PostgreSQL")
    print("=" * 50)
    
    host = input("Хост [localhost]: ").strip() or "localhost"
    port = input("Порт [5432]: ").strip() or "5432"
    user = input("Пользователь [postgres]: ").strip() or "postgres"
    password = input("Пароль: ").strip()
    
    return {
        'host': host,
        'port': port,
        'user': user,
        'password': password
    }

def create_database(config):
    """Создание базы данных и таблиц"""
    try:
        print("\n🔄 Создание базы данных...")
        
        # Подключаемся к стандартной базе данных postgres
        conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            database="postgres"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Проверяем существование базы данных
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'python_db'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute("CREATE DATABASE python_db")
            print("✅ База данных 'python_db' создана")
        else:
            print("✅ База данных 'python_db' уже существует")
        
        cursor.close()
        conn.close()
        
        # Подключаемся к нашей базе данных
        conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            database="python_db"
        )
        cursor = conn.cursor()
        
        # Создаем основную таблицу users
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                age INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Таблица 'users' создана")
        
        # Добавляем тестовые данные
        cursor.execute("""
            INSERT INTO users (name, email, age) 
            VALUES 
                ('Иван Иванов', 'ivan@example.com', 25),
                ('Петр Петров', 'petr@example.com', 30),
                ('Мария Сидорова', 'maria@example.com', 28)
            ON CONFLICT (email) DO NOTHING
        """)
        
        conn.commit()
        print("✅ Тестовые данные добавлены")
        
        cursor.close()
        conn.close()
        
        # Сохраняем конфигурацию
        save_config(config)
        
        # Запускаем миграции
        print("\n🔄 Запуск миграций базы данных...")
        try:
            from migrations import run_all_migrations
            if run_all_migrations():
                print("✅ Все миграции успешно применены")
            else:
                print("❌ Возникли проблемы с миграциями")
        except ImportError as e:
            print(f"⚠️ Модуль миграций не найден: {e}")
        except Exception as e:
            print(f"⚠️ Ошибка при запуске миграций: {e}")
        
        print("\n🎉 Настройка завершена успешно!")
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Ошибка подключения: {e}")
        print("\n🔧 Проверьте:")
        print("   - Запущен ли PostgreSQL")
        print("   - Правильность пароля")
        print("   - Доступность хоста и порта")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def save_config(config):
    """Сохраняем конфигурацию в файл"""
    try:
        with open('db_config.py', 'w', encoding='utf-8') as f:
            f.write(f"DB_CONFIG = {config}")
        print("✅ Конфигурация сохранена в db_config.py")
    except Exception as e:
        print(f"⚠️ Не удалось сохранить конфигурацию: {e}")

def check_existing_config():
    """Проверка существующей конфигурации"""
    try:
        from db_config import DB_CONFIG
        print("\n⚠️ Найдена существующая конфигурация.")
        print("Хотите использовать текущие настройки?")
        reuse = input("Использовать текущие настройки? (yes/NO): ").strip().lower()
        if reuse == 'yes':
            return DB_CONFIG
    except ImportError:
        pass
    return None

if __name__ == "__main__":
    print("🚀 Настройка PostgreSQL Python Project")
    print("=" * 50)
    
    # Проверяем существующую конфигурацию
    existing_config = check_existing_config()
    
    if existing_config:
        config = existing_config
        print("✅ Используем существующие настройки")
    else:
        config = get_db_config()
    
    success = create_database(config)
    
    if success:
        print("\n🚀 Теперь можно запустить основное приложение:")
        print("python main.py")
    else:
        print("\n❌ Настройка не завершена. Проверьте параметры подключения.")