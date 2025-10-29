import psycopg2
from datetime import datetime
import os
import sys

class DatabaseMigrator:
    def __init__(self, config):
        """
        Инициализация мигратора
        
        Args:
            config (dict): Конфигурация подключения к БД
        """
        self.config = config
        self.connection = None
        self.cursor = None
        
    def connect(self):
        """Подключение к базе данных"""
        try:
            self.connection = psycopg2.connect(
                host=self.config['host'],
                port=self.config['port'],
                database=self.config.get('database', 'python_db'),
                user=self.config['user'],
                password=self.config['password']
            )
            self.cursor = self.connection.cursor()
            print("✅ Успешное подключение к PostgreSQL для миграций")
            return True
        except Exception as e:
            print(f"❌ Ошибка подключения: {e}")
            return False
            
    def disconnect(self):
        """Закрытие соединения"""
        if self.connection:
            self.cursor.close()
            self.connection.close()
            
    def create_migrations_table(self):
        """Создание таблицы для отслеживания миграций"""
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS migrations (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL UNIQUE,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.connection.commit()
            print("✅ Таблица миграций создана/проверена")
            return True
        except Exception as e:
            print(f"❌ Ошибка создания таблицы миграций: {e}")
            return False
            
    def is_migration_applied(self, migration_name):
        """Проверка, применена ли уже миграция"""
        try:
            self.cursor.execute("SELECT id FROM migrations WHERE name = %s", (migration_name,))
            return self.cursor.fetchone() is not None
        except Exception as e:
            print(f"❌ Ошибка проверки миграции: {e}")
            return False
            
    def mark_migration_applied(self, migration_name):
        """Отметка миграции как примененной"""
        try:
            self.cursor.execute(
                "INSERT INTO migrations (name) VALUES (%s)", 
                (migration_name,)
            )
            self.connection.commit()
            return True
        except Exception as e:
            print(f"❌ Ошибка отметки миграции: {e}")
            return False
            
    def run_migration(self, migration_name, sql_commands):
        """
        Выполнение миграции
        
        Args:
            migration_name (str): Название миграции
            sql_commands (list): Список SQL команд для выполнения
        """
        if self.is_migration_applied(migration_name):
            print(f"✅ Миграция '{migration_name}' уже применена")
            return True
            
        print(f"🔄 Применение миграции: {migration_name}")
        
        try:
            for i, sql in enumerate(sql_commands, 1):
                print(f"  Выполнение команды {i}/{len(sql_commands)}...")
                self.cursor.execute(sql)
                
            self.connection.commit()
            
            if self.mark_migration_applied(migration_name):
                print(f"✅ Миграция '{migration_name}' успешно применена")
                return True
            else:
                print(f"❌ Не удалось отметить миграцию как примененную")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка выполнения миграции '{migration_name}': {e}")
            self.connection.rollback()
            return False

def get_migrations():
    """
    Определение всех доступных миграций
    
    Returns:
        dict: Словарь с миграциями {название: [sql_commands]}
    """
    migrations = {
        '001_add_phone_column': [
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS phone VARCHAR(20)",
            "COMMENT ON COLUMN users.phone IS 'Номер телефона пользователя'"
        ],
        
        '002_add_status_column': [
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'active'",
            "COMMENT ON COLUMN users.status IS 'Статус пользователя: active/inactive'",
            "ALTER TABLE users ADD CONSTRAINT check_status CHECK (status IN ('active', 'inactive'))"
        ],
        
        '003_create_user_profiles_table': [
            """
            CREATE TABLE IF NOT EXISTS user_profiles (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                address TEXT,
                city VARCHAR(100),
                country VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            "CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id)"
        ],
        
        '004_add_user_profile_data': [
            """
            INSERT INTO user_profiles (user_id, city, country)
            SELECT id, 'Москва', 'Россия' FROM users
            WHERE NOT EXISTS (SELECT 1 FROM user_profiles WHERE user_profiles.user_id = users.id)
            """
        ],
        
        '005_create_audit_log_table': [
            """
            CREATE TABLE IF NOT EXISTS audit_log (
                id SERIAL PRIMARY KEY,
                table_name VARCHAR(100) NOT NULL,
                record_id INTEGER NOT NULL,
                action VARCHAR(10) NOT NULL,
                old_data JSONB,
                new_data JSONB,
                changed_by VARCHAR(100),
                changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            "CREATE INDEX IF NOT EXISTS idx_audit_log_table_record ON audit_log(table_name, record_id)",
            "CREATE INDEX IF NOT EXISTS idx_audit_log_changed_at ON audit_log(changed_at)"
        ]
    }
    
    return migrations

def run_all_migrations():
    """Запуск всех миграций"""
    try:
        from db_config import DB_CONFIG
    except ImportError:
        print("❌ Файл конфигурации не найден. Запустите setup.py сначала.")
        return False
        
    migrator = DatabaseMigrator(DB_CONFIG)
    
    if not migrator.connect():
        return False
        
    if not migrator.create_migrations_table():
        migrator.disconnect()
        return False
        
    migrations = get_migrations()
    applied_count = 0
    
    print(f"🔄 Найдено {len(migrations)} миграций для применения")
    print("=" * 50)
    
    for migration_name, sql_commands in migrations.items():
        if migrator.run_migration(migration_name, sql_commands):
            applied_count += 1
        else:
            print(f"❌ Прерывание миграций из-за ошибки")
            migrator.disconnect()
            return False
            
    migrator.disconnect()
    
    print("=" * 50)
    print(f"🎉 Миграции завершены! Применено: {applied_count}/{len(migrations)}")
    
    return applied_count == len(migrations)

def show_migration_status():
    """Показать статус миграций"""
    try:
        from db_config import DB_CONFIG
    except ImportError:
        print("❌ Файл конфигурации не найден.")
        return
        
    migrator = DatabaseMigrator(DB_CONFIG)
    
    if not migrator.connect():
        return
        
    if not migrator.create_migrations_table():
        migrator.disconnect()
        return
        
    migrations = get_migrations()
    
    print("📊 Статус миграций:")
    print("-" * 40)
    
    for migration_name in migrations.keys():
        if migrator.is_migration_applied(migration_name):
            print(f"✅ {migration_name} - ПРИМЕНЕНА")
        else:
            print(f"❌ {migration_name} - НЕ ПРИМЕНЕНА")
            
    migrator.disconnect()

def rollback_last_migration():
    """Откат последней миграции (для экстренных случаев)"""
    try:
        from db_config import DB_CONFIG
    except ImportError:
        print("❌ Файл конфигурации не найден.")
        return False
        
    migrator = DatabaseMigrator(DB_CONFIG)
    
    if not migrator.connect():
        return False
        
    try:
        # Получаем последнюю примененную миграцию
        migrator.cursor.execute("""
            SELECT name FROM migrations 
            ORDER BY applied_at DESC, id DESC 
            LIMIT 1
        """)
        last_migration = migrator.cursor.fetchone()
        
        if not last_migration:
            print("❌ Нет примененных миграций для отката")
            migrator.disconnect()
            return False
            
        migration_name = last_migration[0]
        print(f"🔄 Откат миграции: {migration_name}")
        
        # Определяем команды для отката каждой миграции
        rollback_commands = {
            '001_add_phone_column': [
                "ALTER TABLE users DROP COLUMN IF EXISTS phone"
            ],
            '002_add_status_column': [
                "ALTER TABLE users DROP CONSTRAINT IF EXISTS check_status",
                "ALTER TABLE users DROP COLUMN IF EXISTS status"
            ],
            '003_create_user_profiles_table': [
                "DROP TABLE IF EXISTS user_profiles"
            ],
            '004_add_user_profile_data': [
                "TRUNCATE TABLE user_profiles"  # Эта миграция только добавляла данные
            ],
            '005_create_audit_log_table': [
                "DROP TABLE IF EXISTS audit_log"
            ]
        }
        
        if migration_name in rollback_commands:
            for sql in rollback_commands[migration_name]:
                migrator.cursor.execute(sql)
                
            # Удаляем запись о миграции
            migrator.cursor.execute("DELETE FROM migrations WHERE name = %s", (migration_name,))
            migrator.connection.commit()
            
            print(f"✅ Миграция '{migration_name}' успешно откатана")
            migrator.disconnect()
            return True
        else:
            print(f"❌ Не найдены команды для отката миграции '{migration_name}'")
            migrator.disconnect()
            return False
            
    except Exception as e:
        print(f"❌ Ошибка отката миграции: {e}")
        migrator.connection.rollback()
        migrator.disconnect()
        return False

def main():
    """Главное меню миграций"""
    print("🚀 Система миграций базы данных")
    print("=" * 40)
    
    while True:
        print("\nВыберите действие:")
        print("1. Применить все миграции")
        print("2. Показать статус миграций")
        print("3. Откатить последнюю миграцию")
        print("4. Выход")
        
        choice = input("Ваш выбор (1-4): ").strip()
        
        if choice == '1':
            run_all_migrations()
        elif choice == '2':
            show_migration_status()
        elif choice == '3':
            confirm = input("Вы уверены? Это действие нельзя отменить (yes/NO): ").strip().lower()
            if confirm == 'yes':
                rollback_last_migration()
            else:
                print("❌ Откат отменен")
        elif choice == '4':
            print("👋 Выход из системы миграций")
            break
        else:
            print("❌ Неверный выбор")

if __name__ == "__main__":
    main()