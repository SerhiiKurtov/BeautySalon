import psycopg2

import os
from dotenv import load_dotenv

load_dotenv()

from werkzeug.security import generate_password_hash

class Database :
    def __init__(self) :
        try :
            self.conn = psycopg2.connect(dbname='beauty_salon', user='postgres', password=os.getenv('DB_PASSWORD'), host='localhost', port='5432')
            self.cur = self.conn.cursor()
            self.create_tables()
        except Exception as e :
            print(f"Помилка при підключенні: {e}")

    def execute_query(self, query, params=()) :
        try :
            result = None
            self.cur.execute(query, params)
            if "RETURNING" in query.upper():
                result = self.cur.fetchone()[0]
            self.conn.commit()
            return result
        except Exception as e :
            print(f"Виникла помилка: {e}")

    def fetch_all(self, query, params=()) :
        try :
            self.cur.execute(query, params)
            return self.cur.fetchall()
        except Exception as e :
            print(f"Виникла помилка: {e}")

    def create_tables(self) :
        sql_tables = '''
            DROP TABLE IF EXISTS Bookings CASCADE;
            DROP TABLE IF EXISTS Users CASCADE;
            DROP TABLE IF EXISTS MasterServices CASCADE;
            DROP TABLE IF EXISTS Services CASCADE;
            DROP TABLE IF EXISTS Masters CASCADE;
            DROP TABLE IF EXISTS Schedule CASCADE;
            DROP TABLE IF EXISTS Client CASCADE;

            CREATE TABLE IF NOT EXISTS Users (
                id SERIAL PRIMARY KEY,
                login VARCHAR(30) UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role VARCHAR(20) NOT NULL
        );

            CREATE TABLE IF NOT EXISTS Masters (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                specialization VARCHAR(50) NOT NULL,
                user_id INTEGER REFERENCES Users(id)
        );

            CREATE TABLE IF NOT EXISTS Services (
                id SERIAL PRIMARY KEY,
                title VARCHAR(30) NOT NULL,
                price INTEGER NOT NULL
        );

            CREATE TABLE IF NOT EXISTS Client (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                phone VARCHAR(10) NOT NULL
        );

            CREATE TABLE IF NOT EXISTS Schedule (
                id SERIAL PRIMARY KEY,
                work_date DATE NOT NULL,
                work_time TIME NOT NULL,
                is_available INTEGER DEFAULT 1,
                master_id INTEGER REFERENCES Masters (id)
        );

            CREATE TABLE IF NOT EXISTS MasterServices (
                id SERIAL PRIMARY KEY,
                master_id INTEGER REFERENCES Masters (id),
                services_id INTEGER REFERENCES Services (id)
        );

            CREATE TABLE IF NOT EXISTS Bookings (
                id SERIAL PRIMARY KEY,
                status VARCHAR(20) DEFAULT 'pending',
                full_time VARCHAR(30) NOT NULL,
                master_id INTEGER REFERENCES Masters (id),
                client_id INTEGER REFERENCES Client (id),
                services_id INTEGER REFERENCES Services (id)
        );
        '''

        self.cur.execute(sql_tables)
        self.conn.commit()

    def add_user(self, login, password, role) :
        password_code = generate_password_hash(password)
        new_profile = self.execute_query("INSERT INTO Users (login, password, role) VALUES (%s, %s, %s) RETURNING id", (login, password_code, role))
        return new_profile

    def add_master(self) :
        m_name = input("Введіть імя майстра: ")
        m_spec = input("Введіть спеціалізацію: ")
        m_login = input("Створіть логін для майстра:")
        m_pass = input("Створіть пароль для майстра:")
        try :
            new_master = self.add_user(m_login, m_pass, 'master')
            self.execute_query("INSERT INTO Masters (name, specialization, user_id) VALUES (%s, %s, %s)", (m_name, m_spec, new_master))
            print(f"Майстер {m_name}, спеціальність {m_spec} збережено!")
        except Exception as e :
            print(f"Виникла помилка: {e}")


db = Database()

admin = db.add_user('admin_login', 'admin_pass12345', 'admin')
users = db.fetch_all("SELECT id, login, role FROM Users")
print("Список користувачів у базі:")
for user in users :
    print(user)

db.add_master()
all_master = db.fetch_all("SELECT * FROM Masters")
for master in all_master :
    print(master)