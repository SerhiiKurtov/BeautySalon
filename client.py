from database import Database

class ClientManager :
    def __init__(self, db, master_repo, service_repo, booking_repo, schedule_repo, client_repo) :
        self.db = db
        self.master_repo = master_repo
        self.service_repo = service_repo
        self.booking_repo = booking_repo
        self.schedule_repo = schedule_repo
        self.client_repo = client_repo

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
                self.client_booking()

    def client_booking(self) :
        full_spec = self.master_repo.get_all_specializations()
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
                specialization = full_spec[spec_index - 1][0]
                services = self.service_repo.get_by_specialization(specialization)
                if not services :
                    print("Послуги не існує!")
                else :
                    for row in services :
                        print(f"ID: {row[0]:<3} | Процедура: {row[1]:<30} | Ціна: {row[2]}")
                    try :
                        service_id = int(input("Оберіть ID бажаної процедури: ").strip())
                    except :
                        print("Введіть значення цифрою")
                        return
                    
                    master_id = self.master_repo.get_by_service(service_id)
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
                        
                    date_id = self.schedule_repo.get_available_slots(final_master_id)
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
                        new_client_id = self.client_repo.create(name, phone)
                        self.booking_repo.add_booking(final_master_id, service_id, d_id, new_client_id)
                        self.schedule_repo.reserve_slot(d_id)
                    except Exception as e :
                        print(f"Виникла помилка: {e}")
                    print(f"Вітаємо, {name}! Ви успішно записані. Чекаємо на вас!")
            else :
                print(f"Спеціаліста з ID {spec_index} не існує")
                return