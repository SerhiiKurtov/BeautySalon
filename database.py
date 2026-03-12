import psycopg2

import os
from dotenv import load_dotenv

load_dotenv()

from werkzeug.security import generate_password_hash, check_password_hash

import getpass

import calendar

from datetime import datetime

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
            if "RETURNING" in query.upper() :
                row = self.cur.fetchone()
                if row :
                    result = row[0]
            self.conn.commit()
            return result
        except Exception as e :
            self.conn.rollback()
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
                user_id INTEGER REFERENCES Users(id),
                is_active BOOLEAN DEFAULT TRUE
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
                master_id INTEGER REFERENCES Masters (id),
                UNIQUE (work_date, work_time, master_id)
        );

            CREATE TABLE IF NOT EXISTS MasterServices (
                id SERIAL PRIMARY KEY,
                master_id INTEGER REFERENCES Masters (id),
                services_id INTEGER REFERENCES Services (id)
        );

            CREATE TABLE IF NOT EXISTS Bookings (
                id SERIAL PRIMARY KEY,
                status VARCHAR(20) DEFAULT 'pending',
                master_id INTEGER REFERENCES Masters (id),
                client_id INTEGER REFERENCES Client (id),
                services_id INTEGER REFERENCES Services (id),
                schedule_id INTEGER REFERENCES Schedule (id)
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

    def delete_masters(self) :
        self.show_all_masters()
        try :
            del_master = int(input("Оберіть ID майстра якого хочете видалити: ").strip())
            check = self.fetch_all("SELECT 1 FROM Masters WHERE id = %s AND is_active = TRUE", (del_master,))
            if not check :
                print(f"Майстра під ID {del_master} не існує")
            else :
                self.execute_query("UPDATE Masters SET is_active = %s WHERE id = %s", (False, del_master))
                self.execute_query("DELETE FROM Schedule WHERE master_id = %s AND work_date >= CURRENT_DATE", (del_master,))
                self.execute_query("DELETE FROM MasterServices WHERE master_id = %s", (del_master,))
                print(f"Майстра з ID {del_master} видалено!")
        except ValueError :
            print("Помилка, введіть ID цифрою!")
        except Exception as e:
            print(f"Виникла системна помилка: {e}")

    def add_service(self) :
        masters = self.fetch_all("SELECT id, name, specialization FROM Masters")
        print("\n--- Список майстрів ---")
        for m in masters:
            print(f"ID: {m[0]} | {m[1]} ({m[2]})")
        try :
            master_id = int(input("Оберіть ID майстра, якому додаємо послуги: ").strip())
            while True:
                service_name = input("Введіть назву процедури ('стоп' для завершення):Назва процедури: ").strip()
                if service_name == 'стоп' :
                    break
                try:
                    price_name = int(input(f"Ціна для '{service_name}': ").strip())
                    service_id = self.execute_query("INSERT INTO Services (title, price) VALUES (%s, %s) RETURNING id", (service_name, price_name))
                    if service_id :
                        self.execute_query("INSERT INTO MasterServices (master_id, services_id) VALUES (%s, %s)", (master_id, service_id))
                        print(f"Послуга '{service_name}' додана та закріплена за майстром!")
                except ValueError :
                    print("Помилка, ціна має бути числом!")
            print("Всі послуги для цього майстра збережено.")
        except ValueError :
            print("Помилка, введіть коректний ID.")

    def edit_price(self) :
        self.show_all_masters()
        try :
            master_price = int(input("Оберіть ID майстра якому бажаєте змінити прайс: ").strip())
            check = self.fetch_all('''SELECT s.id, s.title, s.price
                                     FROM Services s
                                     JOIN MasterServices ms ON s.id = ms.services_id
                                     WHERE ms.master_id = %s
                                    ''', (master_price,))
            if not check :
                print(f"У майстра під ID {master_price} ще немає призначених послуг або ID вказано невірно")
            else :
                for c in check :
                    print(f"ID: {c[0]} | Процедура: {c[1]} | Ціна: {c[2]} грн")
                service = int(input("Оберіть ID процедури для зміни ціни: ").strip())
                allowed_ids = [c[0] for c in check]
                if service in allowed_ids : 
                    new_price = int(input("Введіть нову ціну: ").strip())
                    self.execute_query("UPDATE Services SET price = %s WHERE id = %s", (new_price, service))
                    print("Ціну оновлено!")
                else :
                    print("Помилка, ви обрали ID послуги, якої немає у цього майстра")
        except ValueError :
            print("Помилка, введіть коректний ID.")

    def delete_service(self) :
        self.show_all_masters()
        try :
            master_id = int(input("Оберіть ID майстра якому бажаєте змінити прайс: ").strip())
            check = self.fetch_all('''SELECT s.id, s.title, s.price
                                     FROM Services s
                                     JOIN MasterServices ms ON s.id = ms.services_id
                                     WHERE ms.master_id = %s
                                    ''', (master_id,))
            if not check :
                print(f"У майстра під ID {master_id} ще немає призначених послуг або ID вказано невірно")
            else :
                for c in check :
                    print(f"ID: {c[0]} | Процедура: {c[1]} | Ціна: {c[2]} грн")
                service = int(input("Оберіть ID для видалення процедури: ").strip())
                allowed_ids = [c[0] for c in check]
                if service in allowed_ids :
                    self.execute_query("DELETE FROM MasterServices WHERE master_id = %s AND services_id = %s", (master_id, service))
                    print("Процедуру видалено!")
                else :
                    print("Помилка, ви обрали ID послуги, якої немає у цього майстра")
        except ValueError :
            print("Помилка, введіть коректний ID.")

    def show_all_masters(self) :
        rows = self.fetch_all("SELECT id, name, specialization FROM Masters WHERE is_active = TRUE")
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
            if not 1 <= month <= 12 :
                print("Місяць має бути від 1 до 12")
                return
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
            try :
                valid_time = datetime.strptime(hour, "%H:%M").time()
                if hour not in time_day :
                    time_day.append(valid_time.strftime("%H:%M"))
                    print(f"Час {valid_time} прийнято.")
            except ValueError :
                print("Помилка! Введіть час у форматі HH:MM (наприклад, 09:00).")
        
        for day in range(1, num_day + 1) :
            current_data = f"{year}-{month:02}-{day:02}"
            for hour in time_day :
                try :
                    self.execute_query("INSERT INTO Schedule (work_date, work_time, master_id) VALUES (%s, %s, %s)", (current_data, hour, m_id))
                except psycopg2.IntegrityError :
                    self.conn.rollback()
                    print(f"Помилка: Час {hour} на цю дату вже існує!")
                except Exception as e :
                    self.conn.rollback()
                    print(f"Виникла помилка: {e}")

        weekend_input = input("Введіть числа місяця, які будуть вихідними (через пробіл): ").strip().split()
        for day_off in weekend_input :
            if day_off.isdigit() and int(day_off) <= num_day and int(day_off) > 0 :
                weekends = f"{year}-{month:02}-{int(day_off):02}"
                self.execute_query("UPDATE Schedule SET is_available = 2 WHERE work_date = %s AND master_id = %s", (weekends, m_id))
                print(f"Вихідні: {weekends} майстра {m_id}")
            else :
                print("Помилка: введіть коректне значення!")

    def client_booking(self) :
        full_spec = self.fetch_all("SELECT DISTINCT specialization FROM Masters")
        if not full_spec :
            print("Спеціаліста не існує")
        else :
            for num, spec in enumerate(full_spec, start=1) :
                print(f"ID: {num} - {spec[0]}")
            try :
                spec_index = int(input("Оберіть ID бажаної спеціальності: ").strip())
            except Exception as e :
                print(f"Виникла помилка {e}, введіть ID цифрою!")
                return
            
            if 1 <= spec_index <= len(full_spec) :
                select_spec = full_spec[spec_index - 1][0]
                services = self.fetch_all('''SELECT DISTINCT s.id, s.title, s.price
                                          FROM Services s
                                          JOIN MasterServices ms ON s.id = ms.services_id
                                          JOIN Masters m ON ms.master_id = m.id
                                          WHERE m.specialization = %s
                                          ''', (select_spec,))
                if not services :
                    print("Послуги не існує!")
                else :
                    for row in services :
                        print(f"ID: {row[0]:<3} | Процедура: {row[1]:<30} | Ціна: {row[2]}")
                    try :
                        s_id = int(input("Оберіть ID бажаної процедури: ").strip())
                    except :
                        print("Введіть значення цифрою")
                        return
                    
                    master_id = self.fetch_all('''SELECT m.id, m.name
                                               FROM Masters m
                                               JOIN MasterServices ms ON m.id = ms.master_id
                                               WHERE ms.services_id = %s
                                               ''', (s_id,))
                    if not master_id :
                        print("Спеціаліста не існує!")
                    else :
                        for master in master_id :
                            print(f"ID: {master[0]:<3} | Спеціаліст: {master[1]:<30} |")
                        try :
                            final_master_id = int(input("Оберіть ID бажаного спеціаліста: ").strip())
                        except :
                            print("Введіть значення цифрою")
                            return
                        
                    date_id = self.fetch_all('''SELECT id, work_date, work_time
                                 FROM Schedule
                                 WHERE master_id = %s AND is_available = 1
                                 ''', (final_master_id,))
                    for row in date_id :
                        time_short = str(row[2])[:5]
                        print(f"{row[0]} | {row[1]} - {time_short}")
                    try :
                        d_id = int(input("Оберіть ID бажаного часу: ").strip())
                    except :
                        print("Введіть значення цифрою")
                        return
                    
                    while True :
                        name = input("Введіть ваше ім'я та прізвище: ").strip()
                        if " " in name and len(name) >= 5 :
                            break
                        else :
                            print("Помилка: введіть, будь ласка, і ім'я, і прізвище!")
                            continue
                    
                    while True :
                        phone = input("Введіть номер телефону: ").strip()
                        if phone.isdigit() and len(phone) == 10 :
                            print("Дякуємо! Номер прийнято.")
                            break
                        else :
                            print("Введіть коретний номер телефону!")
                            continue
                    
                    try :
                        new_client_id = self.execute_query("INSERT INTO Client (name, phone) VALUES (%s, %s) RETURNING id", (name, phone))
                        self.execute_query("INSERT INTO Bookings (master_id, services_id, schedule_id, client_id) VALUES (%s, %s, %s, %s)", (final_master_id, s_id, d_id, new_client_id))
                        self.execute_query("UPDATE Schedule SET is_available = 0 WHERE id = %s", (d_id,))
                    except psycopg2.IntegrityError :
                        print(f"Помилка: цей час уже заброньовано!")
                    except Exception as e :
                        print(f"Виникла помилка: {e}")
                    print(f"Вітаємо, {name}! Ви успішно записані. Чекаємо на вас!")
            else :
                print(f"Спеціаліста з ID {spec_index} не існує")
                return

    def change_booking_status(self) :
        rows = self.fetch_all('''SELECT b.id, b.status, m.name, s.title, c.name, sch.work_date, sch.work_time, sch.id
                        FROM Bookings b
                        JOIN Client c ON b.client_id = c.id
                        JOIN Masters m ON b.master_id = m.id
                        JOIN Services s ON b.services_id = s.id
                        JOIN Schedule sch ON b.schedule_id = sch.id
                        WHERE b.status = 'pending'
                        ''')
        if not rows :
            print("Запису не існує")
        else :
            for row in rows :
                    print(f"ID: {row[0]:<3} | Статус: {row[1]:<30} | Майстер: {row[2]:<30} | Процедура: {row[3]:<30} | Клієнт: {row[4]:<30} | Дата: {row[5]:<10} | Час: {row[6]:<10}")

        booking_to_schedule = {row[0]: row[7] for row in rows}

        while True :
            try :
                confirm = input("Виберіть ID для підтвердження(0 для завершення):").strip()
                confirm_id = int(confirm)
            except ValueError :
                print("Введіть значення цифрою")
                continue
            if confirm_id == 0 :
                print("Допобачення")
                break
            elif not booking_to_schedule :
                print("Записів немає")
                break
            elif confirm_id in booking_to_schedule :
                try :
                    choice = int(input("Виберіть: 1 - Підтвердити, 2 - Скасувати: ").strip())
                except ValueError :
                    print("Введіть значення цифрою")
                    continue
                if choice == 1 :
                    self.execute_query("UPDATE Bookings SET status = %s WHERE id = %s", ('confirmed', confirm_id))
                    del booking_to_schedule[confirm_id]
                    print(f"Запис №{confirm_id} підтверджено!")
                elif choice == 2 :
                    self.execute_query("UPDATE Bookings SET status = %s WHERE id = %s", ('cancelled', confirm_id))
                    sch_id = booking_to_schedule[confirm_id]
                    self.execute_query("UPDATE Schedule SET is_available = 1 WHERE id = %s", (sch_id,))
                    del booking_to_schedule[confirm_id]
                    print(f"Запис №{confirm_id} скасовано!")
                else :
                    print("Оберіть пункт 1 або 2")
                    continue
            else :
                print("Введіть коректне ID")

    def delete_booking(self) :
        rows = self.fetch_all('''SELECT b.id, b.status, m.name, s.title, c.name, sch.work_date, sch.work_time, sch.id
                        FROM Bookings b
                        JOIN Client c ON b.client_id = c.id
                        JOIN Masters m ON b.master_id = m.id
                        JOIN Services s ON b.services_id = s.id
                        JOIN Schedule sch ON b.schedule_id = sch.id
                        WHERE b.status IN ('confirmed', 'cancelled')
                        ''')
        if not rows :
            print("Запису не існує")
        else :
            for row in rows :
                    print(f"ID: {row[0]:<3} | Статус: {row[1]:<30} | Майстер: {row[2]:<30} | Процедура: {row[3]:<30} | Клієнт: {row[4]:<30} | Дата: {row[5]:<10} | Час: {row[6]:<10}")

        booking_to_schedule = {row[0]: row[7] for row in rows}
        
        while True :
            try :
                delete = input("Виберіть ID для видалення(0 для завершення):").strip()
                delete_id = int(delete)
            except ValueError :
                print("Введіть значення цифрою")
                continue
            if delete_id == 0 :
                print("Допобачення")
                break
            elif not booking_to_schedule :
                print("Записів немає")
                break
            elif delete_id in booking_to_schedule :
                self.execute_query("DELETE FROM Bookings WHERE id = %s", (delete_id,))
                sch_id = booking_to_schedule[delete_id]
                self.execute_query("UPDATE Schedule SET is_available = 1 WHERE id = %s", (sch_id,))
                del booking_to_schedule[delete_id]
                print(f"Запис №{delete_id} видалено!")
            else :
                print("Введіть коректне ID")
                continue

    def view_master_schedule(self, master_id) :
        actual_master = self.fetch_all("SELECT id FROM Masters WHERE user_id = %s", (master_id,))
        if not actual_master :
            print("Записів немає")
        else :
            final_master_id = actual_master[0][0]
            rows = self.fetch_all('''SELECT b.id, b.status, m.name, s.title, c.name, sch.work_date, sch.work_time, sch.id
                            FROM Bookings b
                            JOIN Client c ON b.client_id = c.id
                            JOIN Masters m ON b.master_id = m.id
                            JOIN Services s ON b.services_id = s.id
                            JOIN Schedule sch ON b.schedule_id = sch.id
                            WHERE b.master_id = %s
                            ORDER BY sch.work_date, sch.work_time 
                            ''', (final_master_id,))
            if not rows :
                print("Запису не існує")
            else :
                for row in rows :
                        print(f"ID: {row[0]:<3} | Статус: {row[1]:<30} | Майстер: {row[2]:<30} | Процедура: {row[3]:<30} | Клієнт: {row[4]:<30} | Дата: {row[5]:<10} | Час: {row[6]:<10}")
                        