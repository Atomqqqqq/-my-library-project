from database import Database

class User:
    def __init__(self, name, email, age, id=None, created_at=None):
        """
        Модель пользователя
        
        Args:
            name (str): Имя пользователя
            email (str): Email пользователя
            age (int): Возраст пользователя
            id (int, optional): ID пользователя в базе данных
            created_at (str, optional): Дата создания записи
        """
        self.id = id
        self.name = name
        self.email = email
        self.age = age
        self.created_at = created_at
        
    def save(self):
        """
        Сохранение пользователя в базу данных
        
        Returns:
            bool: True если успешно, False если ошибка
        """
        db = Database()
        if not db.connect():
            return False
        
        success = False
        try:
            if self.id is None:
                # Создание нового пользователя
                query = """
                    INSERT INTO users (name, email, age) 
                    VALUES (%s, %s, %s) 
                    RETURNING id
                """
                success = db.execute_query(query, (self.name, self.email, self.age))
                if success:
                    result = db.fetch_one("SELECT id FROM users WHERE email = %s", (self.email,))
                    self.id = result[0] if result else None
            else:
                # Обновление существующего пользователя
                query = """
                    UPDATE users 
                    SET name = %s, email = %s, age = %s 
                    WHERE id = %s
                """
                success = db.execute_query(query, (self.name, self.email, self.age, self.id))
        except Exception as e:
            print(f"❌ Ошибка при сохранении пользователя: {e}")
            success = False
        finally:
            db.disconnect()
            
        return success
        
    @staticmethod
    def get_all():
        """
        Получение всех пользователей из базы данных
        
        Returns:
            list: Список объектов User
        """
        db = Database()
        if not db.connect():
            return []
        
        query = """
            SELECT id, name, email, age, created_at 
            FROM users 
            ORDER BY id
        """
        results = db.fetch_all(query)
        
        db.disconnect()
        
        users = []
        for row in results:
            user = User(
                name=row[1], 
                email=row[2], 
                age=row[3], 
                id=row[0],
                created_at=row[4]
            )
            users.append(user)
            
        return users
        
    @staticmethod
    def get_by_id(user_id):
        """
        Получение пользователя по ID
        
        Args:
            user_id (int): ID пользователя
            
        Returns:
            User: Объект пользователя или None если не найден
        """
        db = Database()
        if not db.connect():
            return None
        
        query = """
            SELECT id, name, email, age, created_at 
            FROM users 
            WHERE id = %s
        """
        result = db.fetch_one(query, (user_id,))
        
        db.disconnect()
        
        if result:
            return User(
                name=result[1], 
                email=result[2], 
                age=result[3], 
                id=result[0],
                created_at=result[4]
            )
        return None
        
    @staticmethod
    def get_by_email(email):
        """
        Получение пользователя по email
        
        Args:
            email (str): Email пользователя
            
        Returns:
            User: Объект пользователя или None если не найден
        """
        db = Database()
        if not db.connect():
            return None
        
        query = "SELECT id, name, email, age FROM users WHERE email = %s"
        result = db.fetch_one(query, (email,))
        
        db.disconnect()
        
        if result:
            return User(
                name=result[1], 
                email=result[2], 
                age=result[3], 
                id=result[0]
            )
        return None
        
    def delete(self):
        """
        Удаление пользователя из базы данных
        
        Returns:
            bool: True если успешно, False если ошибка
        """
        if self.id is None:
            print("❌ Нельзя удалить пользователя без ID")
            return False
            
        db = Database()
        if not db.connect():
            return False
        
        query = "DELETE FROM users WHERE id = %s"
        success = db.execute_query(query, (self.id,))
        
        db.disconnect()
        return success
        
    def __str__(self):
        """Строковое представление пользователя"""
        return f"User(id={self.id}, name='{self.name}', email='{self.email}', age={self.age})"