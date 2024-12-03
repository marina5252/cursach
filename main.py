import sys
import sqlite3
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTabWidget, QWidget, QTableWidget, QTableWidgetItem, QMessageBox, QDateEdit
)
from PyQt6.QtCore import Qt, QDate


class LoginWindow(QMainWindow):
    """Окно авторизации администратора."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Авторизация администратора")
        self.setGeometry(200, 200, 300, 150)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Логин:"))
        self.login_input = QLineEdit()
        layout.addWidget(self.login_input)

        layout.addWidget(QLabel("Пароль:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        self.login_button = QPushButton("Войти")
        self.login_button.clicked.connect(self.handle_login)
        layout.addWidget(self.login_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def handle_login(self):
        login = self.login_input.text()
        password = self.password_input.text()

        if login == "admin" and password == "1234":
            self.main_app = FitnessApp()
            self.main_app.show()
            self.close()

        elif not login or not password:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите имя пользователя и пароль.")
            return

        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль!")


class FitnessApp(QMainWindow):
    """Основное приложение."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Учет клиентов фитнес-центра")
        self.setGeometry(100, 100, 800, 600)

        self.connection = sqlite3.connect("fitness_center.db")
        self.initialize_database()

        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_clients_tab(), "Клиенты")
        self.tabs.addTab(self.create_visits_tab(), "Посещения")
        self.tabs.addTab(self.create_memberships_tab(), "Абонементы")
        self.tabs.addTab(self.create_reports_tab(), "Отчеты")

        self.setCentralWidget(self.tabs)

    def initialize_database(self):
        """Создание таблиц базы данных."""
        cursor = self.connection.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Клиенты (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            имя TEXT NOT NULL,
            фамилия TEXT NOT NULL,
            дата_рождения TEXT NOT NULL,
            телефон TEXT,
            адрес TEXT
        )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Посещения (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            клиент_id INTEGER NOT NULL,
            дата_посещения TEXT NOT NULL,
            FOREIGN KEY (клиент_id) REFERENCES Клиенты (id)
        )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Абонементы (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            клиент_id INTEGER NOT NULL,
            тип TEXT NOT NULL,
            дата_начала TEXT NOT NULL,
            срок_действия TEXT NOT NULL,
            FOREIGN KEY (клиент_id) REFERENCES Клиенты (id)
        )
        """)
        self.connection.commit()

    def create_clients_tab(self):
        """Вкладка для работы с клиентами."""
        tab = QWidget()
        layout = QVBoxLayout()

        # Поля для ввода данных клиента
        self.name_input = QLineEdit()
        self.surname_input = QLineEdit()
        self.birthdate_input = QDateEdit(calendarPopup=True)
        self.birthdate_input.setDate(QDate.currentDate())
        self.phone_input = QLineEdit()
        self.address_input = QLineEdit()

        add_button = QPushButton("Добавить клиента")
        add_button.clicked.connect(self.add_client)

        layout.addWidget(QLabel("Имя:"))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("Фамилия:"))
        layout.addWidget(self.surname_input)
        layout.addWidget(QLabel("Дата рождения:"))
        layout.addWidget(self.birthdate_input)
        layout.addWidget(QLabel("Телефон:"))
        layout.addWidget(self.phone_input)
        layout.addWidget(QLabel("Адрес:"))
        layout.addWidget(self.address_input)
        layout.addWidget(add_button)

        # Таблица для отображения клиентов
        self.clients_table = QTableWidget()
        self.clients_table.setColumnCount(5)
        self.clients_table.setHorizontalHeaderLabels(["ID", "Имя", "Фамилия", "Дата рождения", "Телефон"])
        layout.addWidget(self.clients_table)

        self.load_clients_data()

        tab.setLayout(layout)
        return tab

    def add_client(self):
        """Добавление клиента в базу данных."""
        name = self.name_input.text()
        surname = self.surname_input.text()
        birthdate = self.birthdate_input.text()
        phone = self.phone_input.text()
        address = self.address_input.text()

        if not name or not surname or not birthdate:
            QMessageBox.warning(self, "Ошибка", "Заполните все обязательные поля!")
            return

        cursor = self.connection.cursor()
        cursor.execute("""
        INSERT INTO Клиенты (имя, фамилия, дата_рождения, телефон, адрес)
        VALUES (?, ?, ?, ?, ?)
        """, (name, surname, birthdate, phone, address))
        self.connection.commit()
        self.load_clients_data()

    def load_clients_data(self):
        """Загрузка данных клиентов в таблицу."""
        cursor = self.connection.cursor()
        cursor.execute("SELECT id, имя, фамилия, дата_рождения, телефон FROM Клиенты")
        rows = cursor.fetchall()

        self.clients_table.setRowCount(len(rows))
        for row_idx, row_data in enumerate(rows):
            for col_idx, col_data in enumerate(row_data):
                self.clients_table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))

    def create_visits_tab(self):
        """Вкладка для учета посещений."""
        tab = QWidget()
        layout = QVBoxLayout()

        self.client_id_input = QLineEdit()
        self.visit_date_input = QDateEdit(calendarPopup=True)
        self.visit_date_input.setDate(QDate.currentDate())

        add_button = QPushButton("Добавить посещение")
        add_button.clicked.connect(self.add_visit)

        layout.addWidget(QLabel("ID клиента:"))
        layout.addWidget(self.client_id_input)
        layout.addWidget(QLabel("Дата посещения:"))
        layout.addWidget(self.visit_date_input)
        layout.addWidget(add_button)

        # Таблица для отображения посещений
        self.visits_table = QTableWidget()
        self.visits_table.setColumnCount(3)
        self.visits_table.setHorizontalHeaderLabels(["ID", "ID клиента", "Дата посещения"])
        layout.addWidget(self.visits_table)

        self.load_visits_data()

        tab.setLayout(layout)
        return tab

    def add_visit(self):
        """Добавление посещения в базу данных."""
        client_id = self.client_id_input.text()
        visit_date = self.visit_date_input.text()

        if not client_id or not visit_date:
            QMessageBox.warning(self, "Ошибка", "Заполните все обязательные поля!")
            return

        cursor = self.connection.cursor()
        cursor.execute("""
        INSERT INTO Посещения (клиент_id, дата_посещения)
        VALUES (?, ?)
        """, (client_id, visit_date))
        self.connection.commit()
        self.load_visits_data()

    def load_visits_data(self):
        """Загрузка данных посещений в таблицу."""
        cursor = self.connection.cursor()
        cursor.execute("SELECT id, клиент_id, дата_посещения FROM Посещения")
        rows = cursor.fetchall()

        self.visits_table.setRowCount(len(rows))
        for row_idx, row_data in enumerate(rows):
            for col_idx, col_data in enumerate(row_data):
                self.visits_table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))

    def create_memberships_tab(self):
        """Вкладка для управления абонементами."""
        tab = QWidget()
        layout = QVBoxLayout()

        self.client_id_input_membership = QLineEdit()
        self.membership_type_input = QLineEdit()
        self.membership_start_date_input = QDateEdit(calendarPopup=True)
        self.membership_start_date_input.setDate(QDate.currentDate())
        self.membership_duration_input = QLineEdit()

        add_button = QPushButton("Добавить абонемент")
        add_button.clicked.connect(self.add_membership)

        layout.addWidget(QLabel("ID клиента:"))
        layout.addWidget(self.client_id_input_membership)
        layout.addWidget(QLabel("Тип абонемента:"))
        layout.addWidget(self.membership_type_input)
        layout.addWidget(QLabel("Дата начала:"))
        layout.addWidget(self.membership_start_date_input)
        layout.addWidget(QLabel("Срок действия (месяцев):"))
        layout.addWidget(self.membership_duration_input)
        layout.addWidget(add_button)

        # Таблица для отображения абонементов
        self.memberships_table = QTableWidget()
        self.memberships_table.setColumnCount(5)
        self.memberships_table.setHorizontalHeaderLabels(
            ["ID", "ID клиента", "Тип абонемента", "Дата начала", "Срок действия"]
        )
        layout.addWidget(self.memberships_table)

        self.load_memberships_data()

        tab.setLayout(layout)
        return tab

    def add_membership(self):
        """Добавление абонемента в базу данных."""
        client_id = self.client_id_input_membership.text()
        membership_type = self.membership_type_input.text()
        start_date = self.membership_start_date_input.text()
        duration = self.membership_duration_input.text()

        if not client_id or not membership_type or not start_date or not duration:
            QMessageBox.warning(self, "Ошибка", "Заполните все обязательные поля!")
            return

        cursor = self.connection.cursor()
        cursor.execute("""
        INSERT INTO Абонементы (клиент_id, тип, дата_начала, срок_действия)
        VALUES (?, ?, ?, ?)
        """, (client_id, membership_type, start_date, duration))
        self.connection.commit()
        self.load_memberships_data()

    def load_memberships_data(self):
        """Загрузка данных абонементов в таблицу."""
        cursor = self.connection.cursor()
        cursor.execute("SELECT id, клиент_id, тип, дата_начала, срок_действия FROM Абонементы")
        rows = cursor.fetchall()

        self.memberships_table.setRowCount(len(rows))
        for row_idx, row_data in enumerate(rows):
            for col_idx, col_data in enumerate(row_data):
                self.memberships_table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))

    def create_reports_tab(self):
        """Вкладка для генерации отчетов."""
        tab = QWidget()
        layout = QVBoxLayout()

        self.report_button = QPushButton("Сгенерировать отчет")
        self.report_button.clicked.connect(self.generate_report)

        self.report_output = QTableWidget()
        layout.addWidget(self.report_button)
        layout.addWidget(self.report_output)

        tab.setLayout(layout)
        return tab

    def generate_report(self):
        """Генерация простого отчета по клиентам и их посещениям."""
        cursor = self.connection.cursor()
        cursor.execute("""
        SELECT Клиенты.имя, Клиенты.фамилия, COUNT(Посещения.id) AS посещения
        FROM Клиенты
        LEFT JOIN Посещения ON Клиенты.id = Посещения.клиент_id
        GROUP BY Клиенты.id
        """)
        rows = cursor.fetchall()

        self.report_output.setRowCount(len(rows))
        self.report_output.setColumnCount(3)
        self.report_output.setHorizontalHeaderLabels(["Имя", "Фамилия", "Посещения"])

        for row_idx, row_data in enumerate(rows):
            for col_idx, col_data in enumerate(row_data):
                self.report_output.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec())
