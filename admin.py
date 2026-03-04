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
                        f"Введіть 2 - для запису на процедуру\n"
                        f"Введіть 3 - переглянути персонал\n"
                        f"Введіть 4 - налаштувати графік\n"
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
                for master in all_master :
                    print(master)

            elif action == 2 :
                self.db.add_service()
                all_services = self.db.fetch_all("SELECT * FROM Services")
                for service in all_services:
                    print(service)

            elif action == 3 :
                users = self.db.fetch_all("SELECT id, login, role FROM Users")
                print("Список користувачів у базі:")
                for user in users :
                    print(user)

            elif action == 4 :
                self.db.add_schedule()