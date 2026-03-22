from database import Database

import getpass

import calendar

from datetime import datetime

from werkzeug.security import generate_password_hash

class AdminManager :
    def __init__(self, db, user_repo, master_repo, service_repo, booking_repo, schedule_repo, client_repo) :
        self.db = db
        self.user_repo = user_repo
        self.master_repo = master_repo
        self.service_repo = service_repo
        self.booking_repo = booking_repo
        self.schedule_repo = schedule_repo
        self.client_repo = client_repo

    def _force_change_password(self, user_id) :
        print("\n--- ПЕРШИЙ ВХІД: ПОТРІБНО ЗМІНИТИ ПАРОЛЬ ---")
        while True:
            new_p = getpass.getpass("Новий пароль: ")
            has_letter = any(char.isalpha() for char in new_p)
            has_digit = any(char.isdigit() for char in new_p)
            conf_p = getpass.getpass("Підтвердіть пароль: ")
            if new_p == conf_p and len(new_p) >= 8 and has_letter and has_digit :
                h_pass = generate_password_hash(new_p)
                self.user_repo.update_password(user_id, h_pass)
                print("Пароль змінено успішно!\n")
                break
            else:
                print("Паролі не збігаються або занадто короткі!")

    def admin_menu(self, user_id) :
        user = self.user_repo.get_by_id(user_id)
        if user and user[4] :
            self._force_change_password(user_id)
        while True :
            main_menu = (f"Головне меню\n"
                        f"Введіть 1 - додати майстра\n"
                        f"Введіть 2 - додати послугу\n"
                        f"Введіть 3 - переглянути персонал\n"
                        f"Введіть 4 - налаштувати графік\n"
                        f"Введіть 5 - підтвердження/скасування запису\n"
                        f"Введіть 6 - видалення запису\n"
                        f"Введіть 7 - видалення майстра\n"
                        f"Введіть 8 - зміна прайсу\n"
                        f"Введіть 9 - видалення процедур\n"
                        f"Введіть 10 - звіт\n"
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
                self.add_master()

            elif action == 2 :
                self.add_services()

            elif action == 3 :
                self.show_all_staff()

            elif action == 4 :
                self.add_schedule()

            elif action == 5 :
                self.change_status()

            elif action == 6 :
                self.delete_booking()

            elif action == 7 :
                self.delete_master()

            elif action == 8 :
                self.edit_price()

            elif action == 9 :
                self.delete_service()

            elif action == 10 :
                self.general_report()

    def add_master(self) :
        m_name = input("Введіть імя майстра: ")
        m_spec = input("Введіть спеціалізацію: ")
        m_login = input("Створіть логін для майстра: ")
        hashed_pass = None
        while True :
            m_pass = getpass.getpass("Створіть пароль для майстра:")
            has_digit = any(char.isdigit() for char in m_pass)
            has_upper = any(char.isupper() for char in m_pass)
            if len(m_pass) >= 8 and has_digit and has_upper : 
                print("Пароль надійний!")
            else :
                print("Помилка! Пароль має бути більше 8 символів, мати мінімум одну цифру і одну велику літеру!")
                continue
            confirm_pass = getpass.getpass("Повторіть пароль: ")
            if m_pass != confirm_pass :
                print("Помилка, перевірте пароль і спробуйте знову!")
                continue
            hashed_pass = generate_password_hash(m_pass)
            print("Пароль підтверджено та захешовано.")
            break
        try :
            new_master = self.user_repo.create(m_login, hashed_pass, 'master')
            if new_master :
                self.master_repo.add_master(m_name, m_spec, new_master)
                print(f"Майстер {m_name}, спеціальність {m_spec} збережено!")
            else:
                print("Помилка, не вдалося створити обліковий запис користувача.")
        except Exception as e :
            print(f"Виникла помилка: {e}")

    def add_services(self) :
        self.show_all_staff()
        try :
            master_id = int(input("Оберіть ID майстра, якому додаємо послуги: ").strip())
            while True:
                service_name = input("Введіть назву процедури ('стоп' для завершення):Назва процедури: ").strip()
                if service_name.lower() == 'стоп' :
                    break
                try:
                    price_name = int(input(f"Ціна для '{service_name}': ").strip())
                    self.service_repo.add_service(service_name, price_name, master_id)
                    print(f"Послуга '{service_name}' додана та закріплена за майстром!")
                except ValueError :
                    print("Помилка, ціна має бути числом!")
            print("Всі послуги для цього майстра збережено.")
        except ValueError :
            print("Помилка, введіть коректний ID.")

    def show_all_staff(self) :
        rows = self.master_repo.get_all_active()
        if not rows :
            print("Майстра не існує!")
        else :
            for row in rows :
                print(f"ID: {row[0]:<3} | Майстер: {row[1]:<30} | Спеціальність: {row[2]:<30}")

    def add_schedule(self) :
        self.show_all_staff()
        try :
            m_id = int(input("Оберіть id майстра: ").strip())
            year = int(input("Oберіть рік (наприклад 2026): ").strip())
            month = int(input("Oберіть місяць від 1 до 12: ").strip())
            if not 1 <= month <= 12 :
                print("Місяць має бути від 1 до 12")
                return
        except Exception as e :
            print(f"Виникла помилка: {e}, введіть данні цифрами!")
            return
        
        num_day = calendar.monthrange(year, month)[1]

        time_day = []
        while True :
            hour = input("Введіть час прийому (у форматі HH:MM), для завершення введіть стоп: ").strip()
            if hour.lower() == 'стоп' :
                print("Робоці години визначені!")
                break
            try :
                valid_time = datetime.strptime(hour, "%H:%M").time()
                if hour not in time_day :
                    time_day.append(valid_time.strftime("%H:%M"))
                    print(f"Час {valid_time} прийнято.")
            except ValueError :
                print("Помилка! Введіть час у форматі HH:MM (наприклад, 09:00).")
        
        for day in range(1, num_day + 1) :
            current_date = f"{year}-{month:02}-{day:02}"
            for hour in time_day :
                try :
                    self.schedule_repo.add_slot(current_date, hour, m_id)
                except Exception as e :
                    print(f"Виникла помилка: {e}")

        weekend_input = input("Введіть числа місяця, які будуть вихідними (через пробіл): ").strip().split()
        for day_off in weekend_input :
            if day_off.isdigit() and int(day_off) <= num_day and int(day_off) > 0 :
                weekends = f"{year}-{month:02}-{int(day_off):02}"
                self.schedule_repo.set_day_off(weekends, m_id)
                print(f"Вихідні: {weekends} майстра {m_id}")
            else :
                print("Помилка: введіть коректне значення!")

    def change_status(self) :
        rows = self.booking_repo.get_pending_bookings()
        if not rows :
            print("Запису не існує")
        else :
            for row in rows :
                    print(f"ID: {row[0]:<3} | Статус: {row[1]:<30} | Майстер: {row[2]:<30} | Процедура: {row[3]:<30} | Клієнт: {row[4]:<30} | Дата: {row[5]:<10} | Час: {row[6]:<10}")

        booking_to_schedule = {row[0]: row[7] for row in rows}

        while True :
            try :
                confirm = input("Виберіть ID для підтвердження(0 для завершення):").strip()
                booking_id = int(confirm)
            except ValueError :
                print("Введіть значення цифрою")
                continue
            if booking_id == 0 :
                print("Допобачення")
                break
            elif not booking_to_schedule :
                print("Записів немає")
                break
            elif booking_id in booking_to_schedule :
                try :
                    choice = int(input("Виберіть: 1 - Підтвердити, 2 - Скасувати: ").strip())
                except ValueError :
                    print("Введіть значення цифрою")
                    continue
                if choice == 1 :
                    new_status = 'confirmed'
                    self.booking_repo.update_status(new_status, booking_id)
                    del booking_to_schedule[booking_id]
                    print(f"Запис №{booking_id} підтверджено!")
                elif choice == 2 :
                    new_status = 'cancelled'
                    self.booking_repo.update_status(new_status, booking_id)
                    s_id = booking_to_schedule[booking_id]
                    self.schedule_repo.release_slot(s_id,)
                    del booking_to_schedule[booking_id]
                    print(f"Запис №{booking_id} скасовано!")
                else :
                    print("Оберіть пункт 1 або 2")
                    continue
            else :
                print("Введіть коректне ID")

    def delete_booking(self) :
        rows = self.booking_repo.get_inactive_bookings()
        if not rows :
            print("Запису не існує")
        else :
            for row in rows :
                    print(f"ID: {row[0]:<3} | Статус: {row[1]:<30} | Майстер: {row[2]:<30} | Процедура: {row[3]:<30} | Клієнт: {row[4]:<30} | Дата: {row[5]:<10} | Час: {row[6]:<10}")

        booking_to_schedule = {row[0]: row[7] for row in rows}
        
        while True :
            try :
                delete = input("Виберіть ID для видалення(0 для завершення):").strip()
                delete_id = int(delete)
            except ValueError :
                print("Введіть значення цифрою")
                continue
            if delete_id == 0 :
                print("Допобачення")
                break
            elif not booking_to_schedule :
                print("Записів немає")
                break
            elif delete_id in booking_to_schedule :
                self.booking_repo.delete_booking(delete_id)
                sch_id = booking_to_schedule[delete_id]
                self.schedule_repo.release_slot(sch_id)
                del booking_to_schedule[delete_id]
                print(f"Запис №{delete_id} видалено!")
            else :
                print("Введіть коректне ID")
                continue

    def delete_master(self) :
        self.show_all_staff()
        try :
            del_master = int(input("Оберіть ID майстра якого хочете видалити: ").strip())
            check = self.master_repo.check_master(del_master)
            if not check :
                print(f"Майстра під ID {del_master} не існує")
            else :
                self.master_repo.delete_master(del_master)
                self.schedule_repo.sch_delete(del_master)
                self.master_repo.ms_delete(del_master)
                print(f"Майстра з ID {del_master} видалено!")
        except ValueError :
            print("Помилка, введіть ID цифрою!")
        except Exception as e:
            print(f"Виникла системна помилка: {e}")

    def edit_price(self) :
        self.show_all_staff()
        try :
            master_id = int(input("Оберіть ID майстра якому бажаєте змінити прайс: ").strip())
            check = self.service_repo.get_by_master(master_id)
            if not check :
                print(f"У майстра під ID {master_id} ще немає призначених послуг або ID вказано невірно")
            else :
                for c in check :
                    print(f"ID: {c[0]} | Процедура: {c[1]} | Ціна: {c[2]} грн")
                service_id = int(input("Оберіть ID процедури для зміни ціни: ").strip())
                allowed_ids = [c[0] for c in check]
                if service_id in allowed_ids : 
                    new_price = int(input("Введіть нову ціну: ").strip())
                    self.service_repo.update_price(new_price, service_id)
                    print("Ціну оновлено!")
                else :
                    print("Помилка, ви обрали ID послуги, якої немає у цього майстра")
        except ValueError :
            print("Помилка, введіть коректний ID.")

    def delete_service(self) :
        self.show_all_staff()
        try :
            master_id = int(input("Оберіть ID майстра якому бажаєте змінити прайс: ").strip())
            check = self.service_repo.get_by_master(master_id)
            if not check :
                print(f"У майстра під ID {master_id} ще немає призначених послуг або ID вказано невірно")
            else :
                for c in check :
                    print(f"ID: {c[0]} | Процедура: {c[1]} | Ціна: {c[2]} грн")
                service_id = int(input("Оберіть ID процедури для зміни ціни: ").strip())
                allowed_ids = [c[0] for c in check]
                if service_id in allowed_ids :
                    self.service_repo.remove_master_service(master_id, service_id)
                    print("Процедуру видалено!")
                else :
                    print("Помилка, ви обрали ID послуги, якої немає у цього майстра")
        except ValueError :
            print("Помилка, введіть коректний ID.")

    def general_report(self) :
        try :
            start_date = input("Вкажіть початкову дату звіту(РРРР-ММ-ДД): ")
            end_date = input("Вкажіть кінцеву дату звіту(РРРР-ММ-ДД): ")
            datetime.strptime(start_date, "%Y-%m-%d")
            datetime.strptime(end_date, "%Y-%m-%d")
            self.show_all_staff()
            master_id = int(input("Оберіть ID майстра(для загального звіту вкажіть 0): ").strip())
            rows = self.booking_repo.get_report_data(start_date, end_date, master_id)
            if not rows :
                print("Запису не існує")
            else :
                total_revenue = 0
                confirmed_count = 0
                for row in rows :
                            if row[1] == 'confirmed' :
                                total_revenue += (row[4] or 0)
                                confirmed_count +=1
                            print(f"ID: {row[0]:<3} | Статус: {row[1]:<10} | Майстер: {row[2]:<30} | Процедура: {row[3]:<30} | Ціна в грн: {row[4]:<6} | Клієнт: {row[5]:<30} | Номер телефону: {row[6]:<12} | Дата: {row[7]:<10} | Час: {row[8]:<10}")
                print(f"Кількість підтверджених процедур: {confirmed_count}")
                print(f"Сума прибутку: {total_revenue}")

        except ValueError:
            print("Помилкаб невірний формат дати або ID (використовуйте РРРР-ММ-ДД та цифри).")
        except Exception as e:
            print(f"Сталася системна помилка: {e}")
