from database import Database

class ClientManager :
    def __init__(self, db) :
        self.db = db

    def client_menu(self) :
        print("Доброго дня!")
        while True :
            main_menu = (f"Головне меню\n"
                        f"Введіть 1 - Записатись до майстра\n"
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
                self.db.client_booking()