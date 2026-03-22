from database import Database

class MasterManager :
    def __init__(self, db, master_repo, booking_repo) :
        self.db = db
        self.master_repo = master_repo
        self.booking_repo = booking_repo

    def master_menu(self, user_id) :
        master_id = self.master_repo.get_by_user_id(user_id)
        if not master_id :
            print("Майстра не існує!")
            return
        print(f"Вітаємо, {master_id}! Ви увійшли в робочий кабінет.")
        while True :
            main_menu = (f"Головне меню\n"
                        f"Введіть 1 - розклад\n"
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
                self.view_master_schedule(master_id)

    def view_master_schedule(self, master_id) :
            rows = self.booking_repo.get_by_master_id(master_id)
            if not rows :
                print("Запису не існує")
            else :
                for row in rows :
                        print(f"ID: {row[0]:<3} | Статус: {row[1]:<30} | Майстер: {row[2]:<30} | Процедура: {row[3]:<30} | Клієнт: {row[4]:<30} | Дата: {row[5]:<10} | Час: {row[6]:<10}")
                        