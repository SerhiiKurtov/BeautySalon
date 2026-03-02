import getpass

from database import Database
from admin import AdminManager
from client import ClientManager

db = Database()
db.init_admin()
admin_manager = AdminManager(db)

client_manager = ClientManager(db)

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
        login = input("Ввeдіть логін адміністратора або майстра: ")
        password = getpass.getpass("Введіть пароль: ")
        user = db.authenticate(login, password)
        if user and user['role'] == 'admin' :
            admin_manager.admin_menu(user['id'])
        elif user and user['role'] == 'master' :
            print("Меню майстра в розробці...")
        else :
            print("Невірний логін або пароль!")
    else :
        print("Такого пункту не існує!")
        continue