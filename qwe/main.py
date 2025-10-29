from models import User
from database import test_connection

def main():
    """
    Основная функция приложения
    Управляет главным меню и взаимодействием с пользователем
    """
    print("🚀 Приложение для работы с PostgreSQL")
    print("=" * 50)
    
    # Проверка подключения к базе данных
    if not test_connection():
        print("\n❌ Не удалось подключиться к базе данных.")
        print("Пожалуйста, проверьте настройки или запустите setup.py заново")
        print("Команда для настройки: python setup.py")
        return
    
    show_main_menu()

def show_main_menu():
    """Отображение главного меню приложения"""
    while True:
        print("\n" + "="*50)
        print("📋 ГЛАВНОЕ МЕНЮ")
        print("="*50)
        print("1. 👥 Показать всех пользователей")
        print("2. ➕ Добавить нового пользователя")
        print("3. 🔍 Найти пользователя по ID")
        print("4. 📧 Найти пользователя по email")
        print("5. ✏️  Обновить данные пользователя")
        print("6. 🗑️  Удалить пользователя")
        print("7. 📊 Показать расширенную информацию")
        print("8. 🚀 Управление миграциями БД")
        print("9. ❌ Выход")
        print("="*50)
        
        choice = input("Выберите действие (1-9): ").strip()
        
        if choice == '1':
            show_all_users()
        elif choice == '2':
            add_new_user()
        elif choice == '3':
            find_user_by_id()
        elif choice == '4':
            find_user_by_email()
        elif choice == '5':
            update_user()
        elif choice == '6':
            delete_user()
        elif choice == '7':
            show_extended_info()
        elif choice == '8':
            run_migrations_menu()
        elif choice == '9':
            print("\n👋 До свидания! Спасибо за использование приложения!")
            break
        else:
            print("❌ Неверный выбор. Пожалуйста, выберите действие от 1 до 9.")

def show_all_users():
    """Показать всех пользователей из базы данных"""
    print("\n📋 Список всех пользователей:")
    print("-" * 40)
    
    users = User.get_all()
    
    if not users:
        print("❌ В базе данных нет пользователей")
        return
        
    for i, user in enumerate(users, 1):
        print(f"{i}. ID: {user.id}")
        print(f"   Имя: {user.name}")
        print(f"   Email: {user.email}")
        print(f"   Возраст: {user.age if user.age else 'Не указан'}")
        if hasattr(user, 'phone') and user.phone:
            print(f"   Телефон: {user.phone}")
        if hasattr(user, 'status') and user.status:
            print(f"   Статус: {user.status}")
        if user.created_at:
            print(f"   📅 Создан: {user.created_at}")
        print()

def add_new_user():
    """Добавить нового пользователя в базу данных"""
    print("\n➕ Добавление нового пользователя:")
    print("-" * 35)
    
    name = input("Введите имя: ").strip()
    email = input("Введите email: ").strip()
    age = input("Введите возраст: ").strip()
    phone = input("Введите телефон (опционально): ").strip()
    
    # Валидация данных
    if not name or not email:
        print("❌ Имя и email обязательны для заполнения")
        return
        
    # Проверка уникальности email
    existing_user = User.get_by_email(email)
    if existing_user:
        print(f"❌ Пользователь с email '{email}' уже существует")
        return
        
    try:
        age = int(age) if age else None
        if age is not None and (age < 1 or age > 150):
            print("❌ Возраст должен быть от 1 до 150 лет")
            return
    except ValueError:
        print("❌ Возраст должен быть числом")
        return
        
    # Создание и сохранение пользователя
    user = User(name=name, email=email, age=age)
    
    # Добавляем телефон, если он есть
    if phone:
        user.phone = phone
    
    if user.save():
        print(f"✅ Пользователь '{name}' успешно добавлен! ID: {user.id}")
        
        # Сохраняем профиль, если есть дополнительные данные
        if phone:
            save_user_profile(user.id, phone)
    else:
        print("❌ Ошибка при добавлении пользователя")

def find_user_by_id():
    """Найти пользователя по ID"""
    print("\n🔍 Поиск пользователя по ID:")
    print("-" * 30)
    
    user_id = input("Введите ID пользователя: ").strip()
    
    try:
        user_id = int(user_id)
        if user_id <= 0:
            print("❌ ID должен быть положительным числом")
            return
    except ValueError:
        print("❌ ID должен быть числом")
        return
        
    user = User.get_by_id(user_id)
    
    if user:
        print(f"\n✅ Найден пользователь:")
        print(f"   ID: {user.id}")
        print(f"   Имя: {user.name}")
        print(f"   Email: {user.email}")
        print(f"   Возраст: {user.age if user.age else 'Не указан'}")
        if hasattr(user, 'phone') and user.phone:
            print(f"   Телефон: {user.phone}")
        if hasattr(user, 'status') and user.status:
            print(f"   Статус: {user.status}")
        if user.created_at:
            print(f"   Дата создания: {user.created_at}")
    else:
        print(f"❌ Пользователь с ID {user_id} не найден")

def find_user_by_email():
    """Найти пользователя по email"""
    print("\n📧 Поиск пользователя по email:")
    print("-" * 35)
    
    email = input("Введите email пользователя: ").strip()
    
    if not email:
        print("❌ Email не может быть пустым")
        return
        
    user = User.get_by_email(email)
    
    if user:
        print(f"\n✅ Найден пользователь:")
        print(f"   ID: {user.id}")
        print(f"   Имя: {user.name}")
        print(f"   Email: {user.email}")
        print(f"   Возраст: {user.age if user.age else 'Не указан'}")
        if hasattr(user, 'phone') and user.phone:
            print(f"   Телефон: {user.phone}")
        if hasattr(user, 'status') and user.status:
            print(f"   Статус: {user.status}")
    else:
        print(f"❌ Пользователь с email '{email}' не найден")

def update_user():
    """Обновить данные пользователя"""
    print("\n✏️ Обновление данных пользователя:")
    print("-" * 35)
    
    user_id = input("Введите ID пользователя для обновления: ").strip()
    
    try:
        user_id = int(user_id)
        if user_id <= 0:
            print("❌ ID должен быть положительным числом")
            return
    except ValueError:
        print("❌ ID должен быть числом")
        return
        
    user = User.get_by_id(user_id)
    
    if not user:
        print(f"❌ Пользователь с ID {user_id} не найден")
        return
        
    print(f"\nТекущие данные пользователя:")
    print(f"1. Имя: {user.name}")
    print(f"2. Email: {user.email}")
    print(f"3. Возраст: {user.age if user.age else 'Не указан'}")
    if hasattr(user, 'phone'):
        print(f"4. Телефон: {user.phone if user.phone else 'Не указан'}")
    if hasattr(user, 'status'):
        print(f"5. Статус: {user.status if user.status else 'Не указан'}")
    
    print("\nКакие данные вы хотите обновить?")
    print("1 - Имя, 2 - Email, 3 - Возраст, 4 - Телефон, 5 - Статус")
    field_choice = input("Выберите поле для обновления (1-5): ").strip()
    
    if field_choice == '1':
        new_name = input("Введите новое имя: ").strip()
        if new_name:
            user.name = new_name
    elif field_choice == '2':
        new_email = input("Введите новый email: ").strip()
        if new_email:
            # Проверяем уникальность нового email
            existing = User.get_by_email(new_email)
            if existing and existing.id != user.id:
                print(f"❌ Пользователь с email '{new_email}' уже существует")
                return
            user.email = new_email
    elif field_choice == '3':
        new_age = input("Введите новый возраст: ").strip()
        if new_age:
            try:
                user.age = int(new_age)
                if user.age < 1 or user.age > 150:
                    print("❌ Возраст должен быть от 1 до 150 лет")
                    return
            except ValueError:
                print("❌ Возраст должен быть числом")
                return
    elif field_choice == '4' and hasattr(user, 'phone'):
        new_phone = input("Введите новый телефон: ").strip()
        user.phone = new_phone
    elif field_choice == '5' and hasattr(user, 'status'):
        print("Доступные статусы: active, inactive")
        new_status = input("Введите новый статус: ").strip().lower()
        if new_status in ['active', 'inactive']:
            user.status = new_status
        else:
            print("❌ Неверный статус. Используйте 'active' или 'inactive'")
            return
    else:
        print("❌ Неверный выбор поля")
        return
    
    if user.save():
        print("✅ Данные пользователя успешно обновлены!")
    else:
        print("❌ Ошибка при обновлении данных пользователя")

def delete_user():
    """Удалить пользователя из базы данных"""
    print("\n🗑️ Удаление пользователя:")
    print("-" * 25)
    
    user_id = input("Введите ID пользователя для удаления: ").strip()
    
    try:
        user_id = int(user_id)
        if user_id <= 0:
            print("❌ ID должен быть положительным числом")
            return
    except ValueError:
        print("❌ ID должен быть числом")
        return
        
    user = User.get_by_id(user_id)
    
    if not user:
        print(f"❌ Пользователь с ID {user_id} не найден")
        return
        
    print(f"\n⚠️ ВНИМАНИЕ: Вы собираетесь удалить пользователя:")
    print(f"   ID: {user.id}")
    print(f"   Имя: {user.name}")
    print(f"   Email: {user.email}")
    
    confirm = input("\n❓ Вы уверены? (yes/NO): ").strip().lower()
    
    if confirm == 'yes':
        if user.delete():
            print(f"✅ Пользователь '{user.name}' успешно удален!")
        else:
            print("❌ Ошибка при удалении пользователя")
    else:
        print("✅ Удаление отменено")

def show_extended_info():
    """Показать расширенную информацию о пользователях"""
    from database import Database
    
    print("\n📊 Расширенная информация:")
    print("-" * 30)
    
    db = Database()
    if not db.connect():
        return
    
    try:
        # Статистика по пользователям
        db.cursor.execute("SELECT COUNT(*) FROM users")
        total_users = db.cursor.fetchone()[0]
        
        db.cursor.execute("SELECT COUNT(*) FROM users WHERE age IS NOT NULL")
        users_with_age = db.cursor.fetchone()[0]
        
        db.cursor.execute("SELECT AVG(age) FROM users WHERE age IS NOT NULL")
        avg_age = db.cursor.fetchone()[0]
        
        # Проверяем наличие дополнительных таблиц
        db.cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'user_profiles'
            )
        """)
        has_profiles = db.cursor.fetchone()[0]
        
        if has_profiles:
            db.cursor.execute("SELECT COUNT(*) FROM user_profiles")
            profiles_count = db.cursor.fetchone()[0]
        else:
            profiles_count = 0
            
        print(f"📈 Общая статистика:")
        print(f"   Всего пользователей: {total_users}")
        print(f"   Пользователей с указанным возрастом: {users_with_age}")
        if avg_age:
            print(f"   Средний возраст: {avg_age:.1f} лет")
        print(f"   Создано профилей: {profiles_count}")
        
        # Последние добавленные пользователи
        print(f"\n🆕 Последние пользователи:")
        db.cursor.execute("""
            SELECT name, email, created_at 
            FROM users 
            ORDER BY created_at DESC 
            LIMIT 3
        """)
        recent_users = db.cursor.fetchall()
        
        for i, (name, email, created_at) in enumerate(recent_users, 1):
            print(f"   {i}. {name} ({email}) - {created_at}")
            
    except Exception as e:
        print(f"❌ Ошибка при получении статистики: {e}")
    finally:
        db.disconnect()

def run_migrations_menu():
    """Запуск меню миграций"""
    try:
        from migrations import main as migrations_main
        print("\n🚀 Запуск системы миграций...")
        migrations_main()
    except ImportError as e:
        print(f"❌ Модуль миграций не найден: {e}")
        print("Убедитесь, что файл migrations.py находится в той же папке")
    except Exception as e:
        print(f"❌ Ошибка при запуске миграций: {e}")

def save_user_profile(user_id, phone):
    """Сохранение профиля пользователя (если таблица существует)"""
    from database import Database
    
    db = Database()
    if not db.connect():
        return
    
    try:
        # Проверяем существование таблицы user_profiles
        db.cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'user_profiles'
            )
        """)
        has_profiles_table = db.cursor.fetchone()[0]
        
        if has_profiles_table:
            db.cursor.execute("""
                INSERT INTO user_profiles (user_id, city, country) 
                VALUES (%s, 'Москва', 'Россия')
                ON CONFLICT (user_id) DO NOTHING
            """, (user_id,))
            db.connection.commit()
            print("✅ Профиль пользователя создан")
            
    except Exception as e:
        print(f"⚠️ Не удалось создать профиль: {e}")
    finally:
        db.disconnect()

if __name__ == "__main__":
    main()