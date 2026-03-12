from database import Database

class AdminManager :
    def __init__(self, db) :
        self.db = db

    def admin_menu(self, user_id) :
        is_new = self.db.fetch_all("SELECT is_new_user FROM Users WHERE id = %s", (user_id,))[0][0]
        if is_new :
            print("Обовязкова зміна пароля!")
            self.db.change_password(user_id)
            self.db.execute_query("UPDATE Users SET is_new_user = FALSE WHERE id = %s", (user_id,))
        while True :
            main_menu = (f"Головне меню\n"
                        f"Введіть 1 - додати майстра\n"
                        f"Введіть 2 - додавання процедури\n"
                        f"Введіть 3 - переглянути персонал\n"
                        f"Введіть 4 - налаштувати графік\n"
                        f"Введіть 5 - підтвердження/скасування запису\n"
                        f"Введіть 6 - видалення запису\n"
                        f"Введіть 7 - видалення майстра\n"
                        f"Введіть 8 - зміна прайсу\n"
                        f"Введіть 9 - видалення процедур\n"
                        f"Введіть 0 - вихід\n")
            print(main_menu)
            try :
                action = int(input("Оберіть дію: ").strip())
            except Exception as e :
                print(f"Виникла помилка: {e}, введіть данні цифрами!")
                continue
            if action == 0 :
                break

            elif action == 1 :
                self.db.add_master()
                all_master = self.db.fetch_all("SELECT * FROM Masters")
                if not all_master :
                    print("Список порожній")
                else :
                    for master in all_master :
                        print(f"ID: {master[0]} | Ім'я: {master[1]} | Спеціальність: {master[2]}")

            elif action == 2 :
                self.db.add_service()
                all_services = self.db.fetch_all("SELECT * FROM Services")
                if not all_services :
                    print("Список порожній")
                else :
                    for service in all_services:
                        print(f"ID: {service[0]} | Процедура: {service[1]} | Ціна: {service[2]} грн")

            elif action == 3 :
                users = self.db.fetch_all("SELECT id, login, role FROM Users")
                print("Список користувачів у базі:")
                for user in users :
                    print(f"ID: {user[0]:<3} | Логін: {user[1]:<15} | Роль: {user[2]}")

            elif action == 4 :
                self.db.add_schedule()

            elif action == 5 :
                self.db.change_booking_status()

            elif action == 6 :
                self.db.delete_booking()

            elif action == 7 :
                self.db.delete_masters()
                all_master = self.db.fetch_all("SELECT * FROM Masters WHERE is_active = TRUE")
                if not all_master :
                    print("Список порожній")
                else :
                    for master in all_master :
                        print(f"ID: {master[0]} | Ім'я: {master[1]} | Спеціальність: {master[2]}")

            elif action == 8 :
                self.db.edit_price()

            elif action == 9 :
                self.db.delete_service()