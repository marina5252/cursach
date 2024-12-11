import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTableWidget, QTableWidgetItem, QFormLayout,
    QCalendarWidget, QDialog, QMessageBox, QComboBox, QDateEdit
)
from PyQt6.QtCore import Qt, QDate
import sqlite3


# Инициализация базы данных
def initialize_database():
    connection = sqlite3.connect("fitness_club.db")
    cursor = connection.cursor()

    # Таблица пользователей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    """)
    cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin')")
    cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES ('client', 'client123', 'client')")

    # Таблицы для функционала
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            last_name TEXT,
            phone TEXT,
            email TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            date TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            type TEXT,
            FOREIGN KEY (client_id) REFERENCES clients (id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            schedule_id INTEGER,
            FOREIGN KEY (client_id) REFERENCES clients (id),
            FOREIGN KEY (schedule_id) REFERENCES schedules (id)
        )
    """)

    connection.commit()
    connection.close()


# Форма для авторизации
class LoginForm(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("Авторизация")
        self.setFixedSize(400, 300)

        self.layout = QVBoxLayout()

        self.username_label = QLabel("Логин")
        self.username_input = QLineEdit()

        self.password_label = QLabel("Пароль")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.login_button = QPushButton("Войти")
        self.login_button.clicked.connect(self.login)

        self.register_button = QPushButton("Регистрация")
        self.register_button.clicked.connect(self.register)

        self.layout.addWidget(self.username_label)
        self.layout.addWidget(self.username_input)
        self.layout.addWidget(self.password_label)
        self.layout.addWidget(self.password_input)
        self.layout.addWidget(self.login_button)
        self.layout.addWidget(self.register_button)

        self.setLayout(self.layout)
        self.setStyleSheet("""
                            QMainWindow {
                                background-color: #2a0314;
                                color: #ffffff;
                            }
                            QPushButton {
                                background-color: #e97e63;
                                color: #ffffff;
                                border: none;
                                padding: 10px;
                            }
                            QPushButton:hover {
                                background-color: #c1245b;
                            }
                        """)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        connection = sqlite3.connect("fitness_club.db")
        cursor = connection.cursor()

        # Проверяем данные в базе
        cursor.execute("SELECT id, role FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        connection.close()

        if user:
            user_id, role = user
            if role == "admin":
                self.main_window.switch_to_admin()
            elif role == "client":
                self.main_window.switch_to_client(user_id)
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль.")

    def register(self):
        registration_window = RegistrationForm(self.main_window)
        registration_window.exec()
class RegistrationForm(QDialog):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("Регистрация")
        self.setFixedSize(400, 300)

        self.layout = QVBoxLayout()

        self.username_label = QLabel("Логин")
        self.username_input = QLineEdit()

        self.password_label = QLabel("Пароль")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.first_name_label = QLabel("Имя")
        self.first_name_input = QLineEdit()

        self.last_name_label = QLabel("Фамилия")
        self.last_name_input = QLineEdit()

        self.register_button = QPushButton("Зарегистрироваться")
        self.register_button.clicked.connect(self.register)

        self.layout.addWidget(self.username_label)
        self.layout.addWidget(self.username_input)
        self.layout.addWidget(self.password_label)
        self.layout.addWidget(self.password_input)
        self.layout.addWidget(self.first_name_label)
        self.layout.addWidget(self.first_name_input)
        self.layout.addWidget(self.last_name_label)
        self.layout.addWidget(self.last_name_input)
        self.layout.addWidget(self.register_button)
        self.setStyleSheet("""
                                   QMainWindow {
                                       background-color: #2a0314;
                                       color: #ffffff;
                                   }
                                   QPushButton {
                                       background-color: #e97e63;
                                       color: #ffffff;
                                       border: none;
                                       padding: 10px;
                                   }
                                   QPushButton:hover {
                                       background-color: #c1245b;
                                   }
                               """)

        self.setLayout(self.layout)

    def register(self):
        username = self.username_input.text()
        password = self.password_input.text()
        first_name = self.first_name_input.text()
        last_name = self.last_name_input.text()

        if not username or not password or not first_name or not last_name:
            QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены!")
            return

        connection = sqlite3.connect("fitness_club.db")
        cursor = connection.cursor()

        # Проверяем, существует ли уже такой пользователь
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            QMessageBox.warning(self, "Ошибка", "Пользователь с таким логином уже существует!")
            connection.close()
            return

        # Добавляем клиента в базу данных
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, "client"))
        user_id = cursor.lastrowid  # Получаем id нового клиента
        cursor.execute("INSERT INTO clients (id, first_name, last_name) VALUES (?, ?, ?)", (user_id, first_name, last_name))
        connection.commit()
        connection.close()

        QMessageBox.information(self, "Успех", "Регистрация успешна!")
        self.close()
        self.main_window.switch_to_client(user_id)


# Экран администратора
class AdminScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()

        self.clients_button = QPushButton("Клиенты")
        self.clients_button.clicked.connect(self.manage_clients)

        self.schedule_button = QPushButton("Расписание")
        self.schedule_button.clicked.connect(self.manage_schedule)

        self.attendance_button = QPushButton("Посещаемость")
        self.attendance_button.clicked.connect(self.manage_attendance)

        self.subscriptions_button = QPushButton("Управление абонементами")
        self.subscriptions_button.clicked.connect(self.manage_subscriptions)

        self.reports_button = QPushButton("Генерация отчетов")
        self.reports_button.clicked.connect(self.generate_reports)

        self.layout.addWidget(self.clients_button)
        self.layout.addWidget(self.schedule_button)
        self.layout.addWidget(self.attendance_button)
        self.layout.addWidget(self.subscriptions_button)
        self.layout.addWidget(self.reports_button)
        self.setStyleSheet("""
                                   QMainWindow {
                                       background-color: #2a0314;
                                       color: #ffffff;
                                   }
                                   QPushButton {
                                       background-color: #e97e63;
                                       color: #ffffff;
                                       border: none;
                                       padding: 10px;
                                   }
                                   QPushButton:hover {
                                       background-color: #c1245b;
                                   }
                               """)

        self.setLayout(self.layout)

    def manage_clients(self):
        self.client_management_window = ClientManagementWindow()
        self.client_management_window.show()

    def manage_schedule(self):
        self.schedule_management_window = ScheduleManagementWindow()
        self.schedule_management_window.show()

    def manage_attendance(self):
        self.attendance_management_window = AttendanceManagementWindow()
        self.attendance_management_window.show()

    def manage_subscriptions(self):
        self.subscription_management_window = SubscriptionManagementWindow()
        self.subscription_management_window.show()

    def generate_reports(self):
        self.report_generation_window = ReportGenerationWindow()
        self.report_generation_window.show()


# Экран клиента
class ClientScreen(QWidget):
    def __init__(self, client_id, parent=None):
        super().__init__(parent)
        self.client_id = client_id
        self.layout = QVBoxLayout()

        self.schedule_button = QPushButton("Расписание")
        self.schedule_button.clicked.connect(self.view_schedule)

        self.subscription_button = QPushButton("Купить абонемент")
        self.subscription_button.clicked.connect(self.buy_subscription)

        self.layout.addWidget(self.schedule_button)
        self.layout.addWidget(self.subscription_button)
        self.setStyleSheet("""
                                   QMainWindow {
                                       background-color: #2a0314;
                                       color: #ffffff;
                                   }
                                   QPushButton {
                                       background-color: #e97e63;
                                       color: #ffffff;
                                       border: none;
                                       padding: 10px;
                                   }
                                   QPushButton:hover {
                                       background-color: #c1245b;
                                   }
                               """)

        self.setLayout(self.layout)

    def view_schedule(self):
        self.schedule_window = ScheduleSelectionWindow(client_id=self.client_id)
        self.schedule_window.show()

    def buy_subscription(self):
        self.subscription_window = SubscriptionPurchaseWindow()
        self.subscription_window.show()


# Окно для управления клиентами (Добавление, удаление)
class ClientManagementWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Управление клиентами")
        self.setFixedSize(600, 400)

        self.layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Имя", "Фамилия", "Телефон", "Email"])

        self.refresh_clients()

        self.add_button = QPushButton("Добавить клиента")
        self.add_button.clicked.connect(self.add_client)

        self.delete_button = QPushButton("Удалить клиента")
        self.delete_button.clicked.connect(self.delete_client)

        self.layout.addWidget(self.table)
        self.layout.addWidget(self.add_button)
        self.layout.addWidget(self.delete_button)
        self.setStyleSheet("""
                                   QMainWindow {
                                       background-color: #2a0314;
                                       color: #ffffff;
                                   }
                                   QPushButton {
                                       background-color: #e97e63;
                                       color: #ffffff;
                                       border: none;
                                       padding: 10px;
                                   }
                                   QPushButton:hover {
                                       background-color: #c1245b;
                                   }
                               """)
        self.setLayout(self.layout)

    def refresh_clients(self):
        connection = sqlite3.connect("fitness_club.db")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM clients")
        clients = cursor.fetchall()
        connection.close()

        self.table.setRowCount(len(clients))
        for row, client in enumerate(clients):
            for col, data in enumerate(client):
                self.table.setItem(row, col, QTableWidgetItem(str(data)))

    def add_client(self):
        self.client_form = ClientForm()
        self.client_form.show()

    def delete_client(self):
        selected_row = self.table.currentRow()
        if selected_row != -1:
            client_id = self.table.item(selected_row, 0).text()
            connection = sqlite3.connect("fitness_club.db")
            cursor = connection.cursor()
            cursor.execute("DELETE FROM clients WHERE id = ?", (client_id,))
            connection.commit()
            connection.close()
            self.refresh_clients()


# Форма для добавления нового клиента
class ClientForm(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Добавление клиента")
        self.setFixedSize(300, 200)

        self.layout = QFormLayout()

        self.first_name_input = QLineEdit()
        self.last_name_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.email_input = QLineEdit()

        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_client)

        self.layout.addRow("Имя:", self.first_name_input)
        self.layout.addRow("Фамилия:", self.last_name_input)
        self.layout.addRow("Телефон:", self.phone_input)
        self.layout.addRow("Email:", self.email_input)
        self.layout.addWidget(self.save_button)
        self.setStyleSheet("""
                                   QMainWindow {
                                       background-color: #2a0314;
                                       color: #ffffff;
                                   }
                                   QPushButton {
                                       background-color: #e97e63;
                                       color: #ffffff;
                                       border: none;
                                       padding: 10px;
                                   }
                                   QPushButton:hover {
                                       background-color: #c1245b;
                                   }
                               """)
        self.setLayout(self.layout)

    def save_client(self):
        first_name = self.first_name_input.text()
        last_name = self.last_name_input.text()
        phone = self.phone_input.text()
        email = self.email_input.text()

        if first_name and last_name and phone and email:
            connection = sqlite3.connect("fitness_club.db")
            cursor = connection.cursor()
            cursor.execute("INSERT INTO clients (first_name, last_name, phone, email) VALUES (?, ?, ?, ?)",
                           (first_name, last_name, phone, email))
            connection.commit()
            connection.close()

            QMessageBox.information(self, "Успех", "Клиент добавлен!")
            self.close()


# Окно для управления расписанием
class ScheduleManagementWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Управление расписанием")
        self.setFixedSize(600, 400)

        self.layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Тренировка", "Дата"])

        self.refresh_schedule()

        self.add_button = QPushButton("Добавить тренировку")
        self.add_button.clicked.connect(self.add_schedule)

        self.layout.addWidget(self.table)
        self.layout.addWidget(self.add_button)
        self.setStyleSheet("""
                                   QMainWindow {
                                       background-color: #2a0314;
                                       color: #ffffff;
                                   }
                                   QPushButton {
                                       background-color: #e97e63;
                                       color: #ffffff;
                                       border: none;
                                       padding: 10px;
                                   }
                                   QPushButton:hover {
                                       background-color: #c1245b;
                                   }
                               """)
        self.setLayout(self.layout)

    def refresh_schedule(self):
        connection = sqlite3.connect("fitness_club.db")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM schedules")
        schedules = cursor.fetchall()
        connection.close()

        self.table.setRowCount(len(schedules))
        for row, schedule in enumerate(schedules):
            for col, data in enumerate(schedule):
                self.table.setItem(row, col, QTableWidgetItem(str(data)))

    def add_schedule(self):
        self.schedule_form = ScheduleForm()
        self.schedule_form.show()


# Форма для добавления новой тренировки
class ScheduleForm(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Добавление тренировки")
        self.setFixedSize(300, 200)

        self.layout = QFormLayout()

        self.title_input = QLineEdit()
        self.date_input = QDateEdit(calendarPopup=True)
        self.date_input.setDate(QDate.currentDate())

        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_schedule)

        self.layout.addRow("Тренировка:", self.title_input)
        self.layout.addRow("Дата:", self.date_input)
        self.layout.addWidget(self.save_button)
        self.setStyleSheet("""
                                   QMainWindow {
                                       background-color: #2a0314;
                                       color: #ffffff;
                                   }
                                   QPushButton {
                                       background-color: #e97e63;
                                       color: #ffffff;
                                       border: none;
                                       padding: 10px;
                                   }
                                   QPushButton:hover {
                                       background-color: #c1245b;
                                   }
                               """)
        self.setLayout(self.layout)

    def save_schedule(self):
        title = self.title_input.text()
        date = self.date_input.date().toString("yyyy-MM-dd")

        if title:
            connection = sqlite3.connect("fitness_club.db")
            cursor = connection.cursor()
            cursor.execute("INSERT INTO schedules (title, date) VALUES (?, ?)", (title, date))
            connection.commit()
            connection.close()

            QMessageBox.information(self, "Успех", "Тренировка добавлена!")
            self.close()


# Окно для управления посещаемостью
class AttendanceManagementWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Управление посещаемостью")
        self.setFixedSize(600, 400)

        self.layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID клиента", "Тренировка", "Дата", "Записать"])

        self.refresh_attendance()
        self.setStyleSheet("""
                                   QMainWindow {
                                       background-color: #2a0314;
                                       color: #ffffff;
                                   }
                                   QPushButton {
                                       background-color: #e97e63;
                                       color: #ffffff;
                                       border: none;
                                       padding: 10px;
                                   }
                                   QPushButton:hover {
                                       background-color: #c1245b;
                                   }
                               """)
        self.layout.addWidget(self.table)
        self.setLayout(self.layout)

    def refresh_attendance(self):
        connection = sqlite3.connect("fitness_club.db")
        cursor = connection.cursor()
        cursor.execute("SELECT c.id, c.first_name, c.last_name, s.title, s.date FROM clients c "
                       "JOIN attendance a ON c.id = a.client_id "
                       "JOIN schedules s ON a.schedule_id = s.id")
        attendance_data = cursor.fetchall()
        connection.close()

        self.table.setRowCount(len(attendance_data))
        for row, data in enumerate(attendance_data):
            for col, value in enumerate(data):
                self.table.setItem(row, col, QTableWidgetItem(str(value)))

# Окно для управления абонементами
class SubscriptionManagementWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Управление абонементами")
        self.setFixedSize(400, 300)

        self.layout = QVBoxLayout()

        # Выпадающий список клиентов
        self.client_combo = QComboBox()
        self.load_clients()

        # Тип абонемента
        self.subscription_type_combo = QComboBox()
        self.subscription_type_combo.addItems(["Месячный", "Квартальный", "Годовой"])

        self.add_button = QPushButton("Добавить абонемент")
        self.add_button.clicked.connect(self.add_subscription)

        self.layout.addWidget(QLabel("Выберите клиента"))
        self.layout.addWidget(self.client_combo)
        self.layout.addWidget(QLabel("Выберите тип абонемента"))
        self.layout.addWidget(self.subscription_type_combo)
        self.layout.addWidget(self.add_button)
        self.setStyleSheet("""
                                   QMainWindow {
                                       background-color: #2a0314;
                                       color: #ffffff;
                                   }
                                   QPushButton {
                                       background-color: #e97e63;
                                       color: #ffffff;
                                       border: none;
                                       padding: 10px;
                                   }
                                   QPushButton:hover {
                                       background-color: #c1245b;
                                   }
                               """)
        self.setLayout(self.layout)

    def load_clients(self):
        connection = sqlite3.connect("fitness_club.db")
        cursor = connection.cursor()
        cursor.execute("SELECT id, first_name || ' ' || last_name FROM clients")
        clients = cursor.fetchall()
        connection.close()

        for client_id, client_name in clients:
            self.client_combo.addItem(client_name, client_id)

    def add_subscription(self):
        client_id = self.client_combo.currentData()
        subscription_type = self.subscription_type_combo.currentText()

        if client_id:
            connection = sqlite3.connect("fitness_club.db")
            cursor = connection.cursor()
            cursor.execute("INSERT INTO subscriptions (client_id, type) VALUES (?, ?)", (client_id, subscription_type))
            connection.commit()
            connection.close()

            QMessageBox.information(self, "Успех", "Абонемент успешно добавлен!")

# Окно для генерации отчетов
class ReportGenerationWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Генерация отчетов")
        self.setFixedSize(400, 200)

        self.layout = QVBoxLayout()

        self.generate_button = QPushButton("Сгенерировать отчет")
        self.generate_button.clicked.connect(self.generate_report)

        self.layout.addWidget(self.generate_button)
        self.setStyleSheet("""
                                   QMainWindow {
                                       background-color: #2a0314;
                                       color: #ffffff;
                                   }
                                   QPushButton {
                                       background-color: #e97e63;
                                       color: #ffffff;
                                       border: none;
                                       padding: 10px;
                                   }
                                   QPushButton:hover {
                                       background-color: #c1245b;
                                   }
                               """)
        self.setLayout(self.layout)

    def generate_report(self):
        connection = sqlite3.connect("fitness_club.db")
        cursor = connection.cursor()

        # Подсчёт количества клиентов
        cursor.execute("""
            SELECT COUNT(*) FROM clients
        """)
        clients_count = cursor.fetchone()[0]

        # Подсчёт количества проданных абонементов
        cursor.execute("""
            SELECT COUNT(*) FROM subscriptions
        """)
        subscriptions_count = cursor.fetchone()[0]

        # Подсчёт количества занятий
        cursor.execute("""
            SELECT COUNT(*) FROM schedules
        """)
        trainings_count = cursor.fetchone()[0]

        connection.close()

        # Формирование отчёта
        report = (
            "Общий отчет:\n\n"
            f"Количество клиентов: {clients_count}\n"
            f"Количество проданных абонементов: {subscriptions_count}\n"
            f"Количество проведённых занятий: {trainings_count}"
        )

        QMessageBox.information(self, "Отчет", report)


# Окно для покупки абонемента клиентом
class SubscriptionPurchaseWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Покупка абонемента")
        self.setFixedSize(400, 300)

        self.layout = QVBoxLayout()

        self.subscription_type_combo = QComboBox()
        self.subscription_type_combo.addItems(["Месячный", "Квартальный", "Годовой"])

        self.buy_button = QPushButton("Купить абонемент")
        self.buy_button.clicked.connect(self.buy_subscription)

        self.layout.addWidget(QLabel("Выберите тип абонемента"))
        self.layout.addWidget(self.subscription_type_combo)
        self.layout.addWidget(self.buy_button)
        self.setStyleSheet("""
                                   QMainWindow {
                                       background-color: #2a0314;
                                       color: #ffffff;
                                   }
                                   QPushButton {
                                       background-color: #e97e63;
                                       color: #ffffff;
                                       border: none;
                                       padding: 10px;
                                   }
                                   QPushButton:hover {
                                       background-color: #c1245b;
                                   }
                               """)
        self.setLayout(self.layout)

    def buy_subscription(self):
        subscription_type = self.subscription_type_combo.currentText()

        connection = sqlite3.connect("fitness_club.db")
        cursor = connection.cursor()
        cursor.execute("INSERT INTO subscriptions (client_id, type) VALUES (?, ?)",
                       (1, subscription_type))  # Подразумеваем, что клиент с id 1
        connection.commit()
        connection.close()

        QMessageBox.information(self, "Успех", "Абонемент успешно приобретен!")

# Окно для отображения расписания
class ScheduleSelectionWindow(QDialog):
    def __init__(self, client_id):
        super().__init__()
        self.setWindowTitle("Просмотр расписания")
        self.setFixedSize(600, 400)

        self.client_id = client_id
        self.layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Тренировка", "Дата"])

        self.refresh_schedule()

        self.book_button = QPushButton("Записаться на тренировку")
        self.book_button.clicked.connect(self.book_training)

        self.layout.addWidget(self.table)
        self.layout.addWidget(self.book_button)
        self.setStyleSheet("""
                                   QMainWindow {
                                       background-color: #2a0314;
                                       color: #ffffff;
                                   }
                                   QPushButton {
                                       background-color: #e97e63;
                                       color: #ffffff;
                                       border: none;
                                       padding: 10px;
                                   }
                                   QPushButton:hover {
                                       background-color: #c1245b;
                                   }
                               """)
        self.setLayout(self.layout)

    def refresh_schedule(self):
        connection = sqlite3.connect("fitness_club.db")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM schedules")
        schedules = cursor.fetchall()
        connection.close()

        self.table.setRowCount(len(schedules))
        for row, schedule in enumerate(schedules):
            for col, data in enumerate(schedule):
                self.table.setItem(row, col, QTableWidgetItem(str(data)))

    def book_training(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите тренировку для записи!")
            return

        schedule_id = self.table.item(selected_row, 0).text()

        connection = sqlite3.connect("fitness_club.db")
        cursor = connection.cursor()

        # Проверка, не записан ли клиент уже на эту тренировку
        cursor.execute("""
            SELECT * FROM attendance WHERE client_id = ? AND schedule_id = ?
        """, (self.client_id, schedule_id))
        if cursor.fetchone():
            QMessageBox.warning(self, "Ошибка", "Вы уже записаны на эту тренировку!")
        else:
            cursor.execute("""
                INSERT INTO attendance (client_id, schedule_id) VALUES (?, ?)
            """, (self.client_id, schedule_id))
            connection.commit()
            QMessageBox.information(self, "Успех", "Вы успешно записались на тренировку!")
        connection.close()



# Главное окно
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        initialize_database()

        self.setWindowTitle("FITNESS CLUB")
        self.setFixedSize(400, 300)
        self.setStyleSheet("""
                    QMainWindow {
                        background-color: #2a0314;
                        color: #ffffff;
                    }
                    QPushButton {
                        background-color: #e97e63;
                        color: #ffffff;
                        border: none;
                        padding: 10px;
                    }
                    QPushButton:hover {
                        background-color: #c1245b;
                    }
                """)

        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        self.login_form = LoginForm(self)
        self.admin_screen = AdminScreen(self)
        self.client_screen = ClientScreen(self)

        self.central_widget.addWidget(self.login_form)
        self.central_widget.addWidget(self.admin_screen)
        self.central_widget.addWidget(self.client_screen)

    def switch_to_admin(self):
        self.central_widget.setCurrentWidget(self.admin_screen)

    def switch_to_client(self, client_id):
        self.client_screen = ClientScreen(client_id)
        self.central_widget.addWidget(self.client_screen)
        self.central_widget.setCurrentWidget(self.client_screen)


# Запуск приложения
app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
sys.exit(app.exec())


