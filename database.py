import psycopg2

import os
from dotenv import load_dotenv

load_dotenv()

from werkzeug.security import generate_password_hash, check_password_hash

import getpass

import calendar

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
                role VARCHAR(20) NOT NULL,
                is_new_user BOOLEAN DEFAULT TRUE
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
    
    def change_password(self, user_id) :
        while True :
            new_pass = getpass.getpass("Введіть новий пароль: ")
            has_digit = any(char.isdigit() for char in new_pass)
            has_upper = any(char.isupper() for char in new_pass)
            if len(new_pass) >= 8 and has_digit and has_upper : 
                print("Пароль надійний!")
            else :
                print("Помилка! Пароль має бути більше 8 символів, мати мінімум одну цифру і одну велику літеру!")
            confirm_pass = getpass.getpass("Повторіть пароль: ")
            if new_pass == confirm_pass :
                print("Пароль збігається!")
                break
            else :
                print("Помилка, перевірте пароль і спробуйте знову!")
                continue
        hashed_password = generate_password_hash(new_pass)
        self.execute_query("UPDATE Users SET password = %s WHERE id = %s", (hashed_password, user_id))
        print("Пароль успішно змінено!")

    def add_master(self) :
        m_name = input("Введіть імя майстра: ")
        m_spec = input("Введіть спеціалізацію: ")
        m_login = input("Створіть логін для майстра:")
        while True :
            m_pass = getpass.getpass("Створіть пароль для майстра:")
            has_digit = any(char.isdigit() for char in m_pass)
            has_upper = any(char.isupper() for char in m_pass)
            if len(m_pass) >= 8 and has_digit and has_upper : 
                print("Пароль надійний!")
            else :
                print("Помилка! Пароль має бути більше 8 символів, мати мінімум одну цифру і одну велику літеру!")
            confirm_pass = getpass.getpass("Повторіть пароль: ")
            if m_pass == confirm_pass :
                print("Пароль збігається!")
                break
            else :
                print("Помилка, перевірте пароль і спробуйте знову!")
                continue
        try :
            new_master = self.add_user(m_login, m_pass, 'master')
            self.execute_query("INSERT INTO Masters (name, specialization, user_id) VALUES (%s, %s, %s)", (m_name, m_spec, new_master))
            print(f"Майстер {m_name}, спеціальність {m_spec} збережено!")
        except Exception as e :
            print(f"Виникла помилка: {e}")

    def add_service(self) :
        while True :
            s_title = input("Введіть назву процедури (для завершення введіть стоп): ")
            if s_title.lower() == 'стоп' :
                break
            try :
                s_price = int(input("Введіть ціну: ").strip())
            except ValueError :
                print("Помилка! Ціна має бути числом. Спробуйте ще раз.")
                continue
            new_s_id = self.execute_query("INSERT INTO Services (title, price) VALUES (%s, %s) RETURNING id", (s_title, s_price))
            print(f"Процедура {s_title}, ціна {s_price} збережено!")

            self.show_all_masters()
            m_ids_input = input("Введіть ID майстрів через пробіл: ").strip().split()
            for m_id in m_ids_input :
                if m_id.isdigit() :
                    self.execute_query("INSERT INTO MasterServices (master_id, services_id) VALUES (%s, %s) RETURNING id", (m_id, new_s_id))

    def show_all_masters(self) :
        rows = self.fetch_all("SELECT id, name, specialization FROM Masters")
        if not rows :
            print("Майстра не існує!")
        else :
            for row in rows :
                print(f"ID: {row[0]:<3} | Майстер: {row[1]:<30} | Спеціальність: {row[2]:<30}")

    def init_admin(self) :
        admin_login = os.getenv('ADMIN_LOGIN')
        admin_password = os.getenv('ADMIN_PASSWORD')
        if not admin_login or not admin_password :
            print("Помилка: ADMIN_LOGIN або ADMIN_PASSWORD не знайдені в .env")
            return
        self.cur.execute("SELECT id FROM Users WHERE role = %s", ('admin',))
        admin_exists = self.cur.fetchone()
        if not admin_exists :
            self.add_user(admin_login, admin_password, 'admin')
            print("Адміністратора успішно створено!")   
        else:
            pass

    def authenticate(self, login, password) :
        self.cur.execute("SELECT id, password, role FROM Users WHERE login = %s", (login,))
        user_data = self.cur.fetchone()
        if user_data:
            user_id, hashed_password, role = user_data
            if check_password_hash(hashed_password, password) :
                return {'id': user_id, 'role': role}
        return None
    
    def add_schedule(self) :
        self.show_all_masters()
        try :
            m_id = int(input("Оберіть id майстра: ").strip())
            year = int(input("Oберіть рік (наприклад 2026): ").strip())
            month = int(input("Oберіть місяць від 1 до 12: ").strip())
        except Exception as e :
            print(f"Виникла помилка: {e}, введіть данні цифрами!")
            return
        
        num_day = calendar.monthrange(year, month)[1]

        time_day = []
        while True :
            hour = input("Введіть час прийому (у форматі HH:MM), для завершення введіть стоп: ").strip()
            if hour.lower() == 'стоп' :
                print("Робоці години визначені!")
                break
            time_day.append(hour)
        
        for day in range(1, num_day + 1) :
            current_data = f"{year}-{month:02}-{day:02}"
            for hour in time_day :
                try :
                    self.execute_query("INSERT INTO Schedule (work_date, work_time, master_id) VALUES (%s, %s, %s)", (current_data, hour, m_id))
                except psycopg2.IntegrityError :
                    print(f"Помилка: Час {hour} на цю дату вже існує!")
                except Exception as e :
                    print(f"Виникла помилка: {e}")

        weekend_input = input("Введіть числа місяця, які будуть вихідними (через пробіл): ").strip().split()
        for day_off in weekend_input :
            if day_off.isdigit() and int(day_off) <= num_day and int(day_off) > 0 :
                weekends = f"{year}-{month:02}-{int(day_off):02}"
                self.execute_query("UPDATE Schedule SET is_available = 2 WHERE work_date = %s AND master_id = %s", (weekends, m_id))
                print(f"Вихідні: {weekends} майстра {m_id}")
            else :
                print("Помилка: введіть коректне значення!")        