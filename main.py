import getpass

import os
from dotenv import load_dotenv

load_dotenv()

from werkzeug.security import generate_password_hash, check_password_hash

from database import Database
from repositories import UserRepository
from repositories import MasterRepository
from repositories import ServiceRepository
from repositories import BookingRepository
from repositories import ScheduleRepository
from repositories import ClientRepository

from admin import AdminManager
from master import MasterManager
from client import ClientManager

def main() :
    db = Database()
    #db.create_tables()

    user_repo = UserRepository(db)
    master_repo = MasterRepository(db)
    service_repo = ServiceRepository(db)
    booking_repo = BookingRepository(db)
    schedule_repo = ScheduleRepository(db)
    client_repo = ClientRepository(db)

    admin_log = os.getenv('ADMIN_LOGIN')
    admin_pass = os.getenv('ADMIN_PASSWORD')

    if not user_repo.add_admin() :
        if admin_log and admin_pass :
            hashed_password = generate_password_hash(admin_pass)
            user_repo.create(admin_log, hashed_password, 'admin')
            print("Головний адміністратор створений!")
        else:
            print("Помилка: ADMIN_LOGIN або ADMIN_PASSWORD не знайдено в .env")

    admin_manager = AdminManager(db, user_repo, master_repo, service_repo, booking_repo, schedule_repo, client_repo)
    master_manager = MasterManager(db, master_repo, booking_repo)
    client_manager = ClientManager(db, master_repo, service_repo, booking_repo, schedule_repo, client_repo)

    while True :
        main_menu = (f"Головне меню\n"
                    f"Введіть 1 - Меню клієнта\n"
                    f"Введіть 2 - Вхід для персоналу\n"
                    f"Введіть 0 - Вихід")
        print(main_menu)
        try :
            action = int(input("Оберіть дію: ").strip())
        except Exception as e :
            print(f"Виникла помилка: {e}, введіть данні цифрами!")
            continue
        if action == 0 :
            break
        elif action == 1 :
            client_manager.client_menu()
        elif action == 2 :
            print("\n--- ВХІД ДЛЯ ПЕРСОНАЛУ ---")
            u_login = input("Введіть логін: ").strip()
            u_password = getpass.getpass("Введіть пароль: ")
            user_data = user_repo.get_by_login(u_login)
            if user_data :
                db_id = user_data[0]
                db_hash = user_data[1]
                db_role = user_data[2]
                if check_password_hash(db_hash, u_password):
                    print(f"\nУспішний вхід! Роль: {db_role}")
                    if db_role == 'admin':
                        admin_manager.admin_menu(db_id)
                    elif db_role == 'master':
                        master_manager.master_menu(db_id)
                else:
                    print("Помилка: Невірний пароль!")
            else:
                print("Помилка: Користувача з таким логіном не існує!")

main()