class MasterRepository :
    def __init__(self, db) :
        self.db = db

    def get_all_active(self) :
        masters = self.db.fetch_all("SELECT id, name, specialization FROM Masters WHERE is_active = TRUE")
        return masters
    
    def add_master(self, m_name, m_spec, new_master) :
        result = self.db.execute_query("INSERT INTO Masters (name, specialization, user_id) VALUES (%s, %s, %s) RETURNING id", (m_name, m_spec, new_master))
        return result
    
    def delete_master(self, del_master) :
        self.db.execute_query("UPDATE Masters SET is_active = FALSE WHERE id = %s", (del_master,))

    def get_all_specializations(self) :
        result = self.db.fetch_all("SELECT DISTINCT specialization FROM Masters WHERE is_active = TRUE")
        return result
    
    def get_by_service(self, service_id) :
        result = self.db.fetch_all('''SELECT m.id, m.name
                                   FROM Masters m
                                   JOIN MasterServices ms ON m.id = ms.master_id
                                   WHERE ms.services_id = %s AND m.is_active = TRUE
                                   ''', (service_id,))
        return result
    
    def get_by_user_id(self, user_id) :
        result = self.db.fetch_all("SELECT id FROM Masters WHERE user_id = %s", (user_id,))
        return result[0][0] if result else None
    
    def ms_delete(self, del_master) :
        self.db.execute_query("DELETE FROM MasterServices WHERE master_id = %s", (del_master,))

    def check_master(self, del_master) :
        result = self.db.fetch_all("SELECT 1 FROM Masters WHERE id = %s AND is_active = TRUE", (del_master,))
        return result

class ServiceRepository :
    def __init__(self, db) :
        self.db = db

    def get_by_master(self, master_id) :
        services = self.db.fetch_all('''SELECT s.id, s.title, s.price
                                     FROM Services s
                                     JOIN MasterServices ms ON s.id = ms.services_id
                                     WHERE ms.master_id = %s
                                     ''', (master_id,))
        return services
    
    def get_all(self) :
        result = self.db.fetch_all("SELECT id, title, price FROM Services")
        return result
    
    def add_service(self, service_name, price_name, master_id) :
        id_service = self.db.execute_query("INSERT INTO Services (title, price) VALUES (%s, %s) RETURNING id", (service_name, price_name))
        if id_service:
            self.db.execute_query("INSERT INTO MasterServices (master_id, services_id) VALUES (%s, %s)", (master_id, id_service))
        else:
            print("Помилка")
        return id_service
    
    def update_price(self, service_id, new_price) :
        self.db.execute_query("UPDATE Services SET price = %s WHERE id = %s", (new_price, service_id))

    def remove_master_service(self, master_id, service_id) :
        self.db.execute_query("DELETE FROM MasterServices WHERE master_id = %s AND services_id = %s", (master_id, service_id))

    def get_by_specialization(self, specialization) :
        result = self.db.fetch_all('''SELECT DISTINCT s.id, s.title, s.price
                                   FROM Services s
                                   JOIN MasterServices ms ON s.id = ms.services_id
                                   JOIN Masters m ON ms.master_id = m.id
                                   WHERE m.specialization = %s AND m.is_active = TRUE
                                    ''', (specialization,))
        return result

class BookingRepository :
    def __init__(self, db) :
        self.db = db

    def add_booking(self, final_master_id, s_id, d_id, new_client_id) :
        self.db.execute_query("INSERT INTO Bookings (master_id, services_id, schedule_id, client_id) VALUES (%s, %s, %s, %s)", (final_master_id, s_id, d_id, new_client_id))
        self.db.execute_query("UPDATE Schedule SET is_available = 0 WHERE id = %s", (d_id,))

    def get_booking(self, booking_id) :
        booking = self.db.fetch_all('''SELECT b.id, m.name, m.specialization, s.title, s.price, sch.work_date, sch.work_time
                                    FROM Bookings b
                                    JOIN Masters m ON b.master_id = m.id
                                    JOIN Services s ON b.services_id = s.id
                                    JOIN Schedule sch ON b.schedule_id = sch.id
                                    WHERE b.id = %s
                                    ''', (booking_id,))
        return booking
    
    def get_pending_bookings(self) :
        query = self.db.fetch_all('''SELECT b.id, b.status, m.name, s.title, c.name, sch.work_date, sch.work_time, sch.id
                                    FROM Bookings b
                                    JOIN Client c ON b.client_id = c.id
                                    JOIN Masters m ON b.master_id = m.id
                                    JOIN Services s ON b.services_id = s.id
                                    JOIN Schedule sch ON b.schedule_id = sch.id
                                    WHERE b.status = 'pending'      
                                    ''')
        return query
    
    def update_status(self, new_status, booking_id) :
        self.db.execute_query("UPDATE Bookings SET status = %s WHERE id = %s", (new_status, booking_id))

    def get_inactive_bookings(self) :
        query = self.db.fetch_all('''SELECT b.id, b.status, m.name, s.title, c.name, sch.work_date, sch.work_time, sch.id
                                    FROM Bookings b
                                    JOIN Client c ON b.client_id = c.id
                                    JOIN Masters m ON b.master_id = m.id
                                    JOIN Services s ON b.services_id = s.id
                                    JOIN Schedule sch ON b.schedule_id = sch.id
                                    WHERE b.status IN ('confirmed', 'cancelled')
                                    ''')
        return query
    
    def delete_booking(self, booking_id) :
        self.db.execute_query("DELETE FROM Bookings WHERE id = %s", (booking_id,))

    def get_by_master_id(self, master_id) :
        query = self.db.fetch_all('''SELECT b.id, b.status, m.name, s.title, c.name, sch.work_date, sch.work_time, sch.id
                                    FROM Bookings b
                                    JOIN Client c ON b.client_id = c.id
                                    JOIN Masters m ON b.master_id = m.id
                                    JOIN Services s ON b.services_id = s.id
                                    JOIN Schedule sch ON b.schedule_id = sch.id
                                    WHERE b.master_id = %s
                                    ORDER BY sch.work_date, sch.work_time
                                    ''', (master_id,))
        return query
    
    def get_report_data(self, start_date, end_date, master_id=0) :
        query = self.db.fetch_all('''SELECT b.id, b.status, m.name, s.title, s.price, c.name, c.phone, sch.work_date, sch.work_time, sch.id
                                    FROM Bookings b
                                    JOIN Client c ON b.client_id = c.id
                                    JOIN Masters m ON b.master_id = m.id
                                    JOIN Services s ON b.services_id = s.id
                                    JOIN Schedule sch ON b.schedule_id = sch.id
                                    WHERE (sch.work_date BETWEEN %s AND %s) AND (%s = 0 OR m.id = %s)
                                    ORDER BY sch.work_date, sch.work_time
                                    ''', (start_date, end_date, master_id, master_id))
        return query
    
class UserRepository :
    def __init__(self, db) :
        self.db = db
    
    def create(self, login, hashed_password, role) :
        personnel = self.db.execute_query("INSERT INTO Users (login, password, role) VALUES (%s, %s, %s) RETURNING id", (login, hashed_password, role))
        return personnel
    
    def get_by_login(self, login) :
        log = self.db.fetch_all("SELECT id, password, role, is_new_user FROM Users WHERE login = %s", (login,))
        return log[0] if log else None
    
    def get_by_id(self, user_id) :
        result = self.db.fetch_all("SELECT id, login, password, role, is_new_user FROM Users WHERE id = %s", (user_id,))
        return result[0] if result else None
    
    def add_admin(self) :
        result = self.db.fetch_all("SELECT id FROM Users WHERE role = %s", ('admin',))
        return result or None
    
    def update_password(self, user_id, hashed_password) :
        self.db.execute_query("UPDATE Users SET password = %s, is_new_user = FALSE WHERE id = %s", (hashed_password, user_id))

class ScheduleRepository :
    def __init__(self, db) :
        self.db = db

    def add_slot(self, current_date, hour, m_id) :
        result = self.db.execute_query("INSERT INTO Schedule (work_date, work_time, master_id) VALUES (%s, %s, %s)", (current_date, hour, m_id))
        return result

    def set_day_off(self, weekends, m_id) :
        result = self.db.execute_query("UPDATE Schedule SET is_available = 2 WHERE work_date = %s AND master_id = %s", (weekends, m_id))
        return result

    def get_free_slots(self, master_id, date) :
        result = self.db.fetch_all("SELECT id, work_date, work_time FROM Schedule WHERE master_id = %s AND work_date = %s AND is_available = 1", (master_id, date))
        return result 
    
    def reserve_slot(self, schedule_id) :
        self.db.execute_query("UPDATE Schedule SET is_available = 0 WHERE id = %s", (schedule_id,))

    def release_slot(self, s_id) :
        self.db.execute_query("UPDATE Schedule SET is_available = 1 WHERE id = %s", (s_id,))

    def sch_delete(self, del_master) :
        self.db.execute_query("DELETE FROM Schedule WHERE master_id = %s AND work_date >= CURRENT_DATE", (del_master,))

    def get_available_slots(self, master_id) :
        result = self.db.fetch_all("SELECT id, work_date, work_time FROM Schedule WHERE master_id = %s AND is_available = 1 AND work_date >= CURRENT_DATE ORDER BY work_date, work_time", (master_id,))
        return result
    
class ClientRepository :
    def __init__(self, db) :
        self.db = db 

    def create(self, name, phone) :
        result = self.db.execute_query("INSERT INTO Client (name, phone) VALUES (%s, %s) ON CONFLICT (phone) DO UPDATE SET name = EXCLUDED.name RETURNING id", (name, phone))
        return result