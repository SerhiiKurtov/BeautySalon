from database import Database

class MasterManager :
    def __init__(self, db) :
        self.db = db

    def master_menu(self, user_id) :
        its_me = self.db.fetch_all("SELECT id, name FROM Masters WHERE user_id = %s", (user_id,))
        if not its_me :
            print("Майстра не існує!")
        else :
            for me in its_me :
                master_id = me[0]
                master_name = me[1]
            print(f"Вітаємо, {master_name}! Ви увійшли в робочий кабінет.")
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
                    self.db.view_master_schedule(master_id)