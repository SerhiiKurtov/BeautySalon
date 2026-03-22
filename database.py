import psycopg2

import os
from dotenv import load_dotenv

load_dotenv()

class Database :
    def __init__(self) :
        try :
            self.conn = psycopg2.connect(dbname='beauty_salon', user='postgres', password=os.getenv('DB_PASSWORD'), host='localhost', port='5432')
            self.cur = self.conn.cursor()
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
                phone VARCHAR(10) UNIQUE NOT NULL
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