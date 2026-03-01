from database import Database

db = Database()

admin = db.add_user('admin_login', 'admin_pass12345', 'admin')
users = db.fetch_all("SELECT id, login, role FROM Users")
print("Список користувачів у базі:")
for user in users :
    print(user)

db.add_master()
all_master = db.fetch_all("SELECT * FROM Masters")
for master in all_master :
    print(master)

db.add_service()
all_services = db.fetch_all("SELECT * FROM Services")
for service in all_services:
    print(service)