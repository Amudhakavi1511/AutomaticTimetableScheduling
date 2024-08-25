import sys,sqlite3,smtplib,random,ast,json
from PyQt5.QtGui import QFont,QPixmap,QBrush,QIcon,QPainter
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import pyqtSignal, QTimer,Qt,QSize
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog,QVBoxLayout, QTableWidgetItem,QTableWidget,QPushButton,QGroupBox, QMessageBox,QLabel, QLineEdit,QTextEdit, QSizePolicy, QTabWidget, QHBoxLayout, QRadioButton,QSpacerItem, QComboBox, QFormLayout, QDialog,QStackedWidget
conn = sqlite3.connect('staff.db')
cursor = conn.cursor()
user=None
user_dept=None

class StaffTimetableWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        # Create table widget
        self.table = QTableWidget()
        layout.addWidget(self.table)

        # Set table properties
        self.table.setRowCount(5)  # Number of weekdays
        self.table.setColumnCount(10)  # Number of time periods and breaks
        self.table.setHorizontalHeaderLabels(['Time Period 1', 'Time Period 2', ' ', 'Time Period 3', 'Time Period 4', ' ', 'Time Period 5', 'Time Period 6', ' ', 'Time Period 7'])

        # Set uniform column width
        for col in range(10):
            if col in [2, 5, 8]:
                self.table.setColumnWidth(col, 10)
            else:
                self.table.setColumnWidth(col, 200)

        row_height = 50  # Set this to the desired row height
        for row in range(5):
            self.table.setRowHeight(row, row_height)

        # Set weekday headers
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        for i, day in enumerate(weekdays):
            item = QTableWidgetItem(day)
            item.setFont(QFont('Arial', 12, QFont.Bold))
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setVerticalHeaderItem(i, item)

        # Apply styles to the headers
        self.table.setStyleSheet("""
            QHeaderView::section {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                border: 1px solid #6c6c6c;
                padding: 5px;
            }
            QTableWidget QTableCornerButton::section {
                background-color: #4CAF50;
                border: 1px solid #6c6c6c;
            }
            QTableWidget::item {
                padding: 5px;
                border: 1px solid #6c6c6c;
            }
        """)

    def populate_timetable(self, timetable):
        # Clear the existing items in the table, but keep headers
        self.table.clearContents()

        # Define columns to skip
        columns_to_skip = [2, 5, 8]
        break_letters = ['B', 'R', 'E', 'A', 'K']
        lunch_letters = ['L', 'U', 'N', 'C', 'H']

        # Populate table with the provided timetable data
        for i, row in enumerate(timetable):
            for j in range(self.table.columnCount()):
                if j in columns_to_skip:
                    # Fill "Break" and "Lunch" columns with individual letters
                    if j == 2 or j == 8:
                        item = QTableWidgetItem(break_letters[i])
                    elif j == 5:
                        item = QTableWidgetItem(lunch_letters[i])
                else:
                    adjusted_index = j - sum(k < j for k in columns_to_skip)
                    if adjusted_index < len(row):
                        subject = row[adjusted_index]
                        if isinstance(subject, list):
                            subject = ", ".join(subject)  # Convert list to string if necessary
                        item = QTableWidgetItem(subject if subject != 0 else "")
                    else:
                        item = QTableWidgetItem("")  # Fill with empty item if index is out of range
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, j, item)

    def save_table_as_pdf(self, file_path):
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(file_path)

        # Calculate scale factors to fit the table on one page
        table_size = self.table.size()
        printer_rect = printer.pageRect(QPrinter.DevicePixel)
        scale_x = printer_rect.width() / table_size.width()
        scale_y = printer_rect.height() / table_size.height()
        scale = min(scale_x, scale_y)

        # Begin painting
        painter = QPainter(printer)
        painter.scale(scale, scale)
        self.table.render(painter)
        painter.end()

class TimetableWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        # Create table widget
        self.table = QTableWidget()
        layout.addWidget(self.table)

        # Set table properties
        self.table.setRowCount(5)  # Number of weekdays
        self.table.setColumnCount(10)  # Number of time periods and breaks
        self.table.setHorizontalHeaderLabels(['Time Period 1', 'Time Period 2', ' ', 'Time Period 3', 'Time Period 4', ' ', 'Time Period 5', 'Time Period 6', ' ', 'Time Period 7'])

        # Set uniform column width
        for col in range(10):
            if col in [2, 5, 8]:
                self.table.setColumnWidth(col, 10)
            else:
                self.table.setColumnWidth(col, 200)

        row_height = 50  # Set this to the desired row height
        for row in range(5):
            self.table.setRowHeight(row, row_height)

        # Set weekday headers
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        for i, day in enumerate(weekdays):
            item = QTableWidgetItem(day)
            item.setFont(QFont('Arial', 12, QFont.Bold))
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setVerticalHeaderItem(i, item)

        # Apply styles to the headers
        self.table.setStyleSheet("""
            QHeaderView::section {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                border: 1px solid #6c6c6c;
                padding: 5px;
            }
            QTableWidget QTableCornerButton::section {
                background-color: #4CAF50;
                border: 1px solid #6c6c6c;
            }
            QTableWidget::item {
                padding: 5px;
                border: 1px solid #6c6c6c;
            }
        """)

    def populate_timetable(self, timetable):
        # Clear the existing items in the table, but keep headers
        self.table.clearContents()

        # Define columns to skip
        columns_to_skip = [2, 5, 8]
        break_letters = ['B', 'R', 'E', 'A', 'K']
        lunch_letters = ['L', 'U', 'N', 'C', 'H']

        # Populate table with the provided timetable data
        for i, row in enumerate(timetable):
            for j in range(self.table.columnCount()):
                if j in columns_to_skip:
                    # Fill "Break" and "Lunch" columns with individual letters
                    if j == 2 or j == 8:
                        item = QTableWidgetItem(break_letters[i])
                    elif j == 5:
                        item = QTableWidgetItem(lunch_letters[i])
                else:
                    adjusted_index = j - sum(k < j for k in columns_to_skip)
                    if adjusted_index < len(row):
                        subject = row[adjusted_index]
                        if isinstance(subject, list):
                            subject = ", ".join(subject)  # Convert list to string if necessary
                        item = QTableWidgetItem(subject if subject != 0 else "")
                    else:
                        item = QTableWidgetItem("")  # Fill with empty item if index is out of range
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, j, item)

    def save_table_as_pdf(self, file_path):
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(file_path)

        # Calculate scale factors to fit the table on one page
        table_size = self.table.size()
        printer_rect = printer.pageRect(QPrinter.DevicePixel)
        scale_x = printer_rect.width() / table_size.width()
        scale_y = printer_rect.height() / table_size.height()
        scale = min(scale_x, scale_y)

        # Begin painting
        painter = QPainter(printer)
        painter.scale(scale, scale)
        self.table.render(painter)
        painter.end()


class LabTimetableWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create table widget
        self.table = QTableWidget()
        layout.addWidget(self.table)

        # Set table properties
        self.table.setRowCount(5)  # Number of weekdays
        self.table.setColumnCount(3)  # Number of time periods and breaks
        self.table.setHorizontalHeaderLabels(['', '1', '2'])

        # Set uniform column width
        for col in range(3):
            self.table.setColumnWidth(col, 250)

        for row in range(5):
            self.table.setRowHeight(row,50)

        # Set weekday headers
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        for i, day in enumerate(weekdays):
            item = QTableWidgetItem(day)
            item.setFont(QFont('Arial', 12, QFont.Bold))
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setVerticalHeaderItem(i, item)

        # Apply styles to the headers
        self.table.setStyleSheet("""
            QHeaderView::section {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                border: 1px solid #6c6c6c;
                padding: 5px;
            }
            QTableWidget QTableCornerButton::section {
                background-color: #4CAF50;
                border: 1px solid #6c6c6c;
            }
            QTableWidget::item {
                padding: 5px;
                border: 1px solid #6c6c6c;
            }
        """)

    def populate_timetable(self, timetable):
        # Clear the existing items in the table
        self.table.clearContents()

        # Populate table with the provided timetable data
        for i, day in enumerate(['MON', 'TUE', 'WED', 'THUR', 'FRI']):
            row = timetable.get(day, [])
            for j, period in enumerate(row, start=1):  # Start filling from column index 1
                subject = ", ".join(period) if period else ""
                item = QTableWidgetItem(subject)
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, j, item)

    def save_table_as_pdf(self, file_path):
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(file_path)

        # Calculate scale factors to fit the table on one page
        table_size = self.table.size()
        printer_rect = printer.pageRect(QPrinter.DevicePixel)
        scale_x = printer_rect.width() / table_size.width()
        scale_y = printer_rect.height() / table_size.height()
        scale = min(scale_x, scale_y)

        # Begin painting
        painter = QPainter(printer)
        painter.scale(scale, scale)
        self.table.render(painter)
        painter.end()

class AdminViewLab(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('ADMIN VIEW LAB PAGE')
        self.showMaximized()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(20)

        # Department ComboBox
        self.department_label = QLabel('DEPARTMENT:')
        self.department_label.setStyleSheet("""
            font-weight: bold;
            color: white;
            font-size: 16px;
            background-color: #2E8B57;
            padding: 10px;
            border: 2px solid #4CAF50;
            border-radius: 5px;
        """)
        layout.addWidget(self.department_label)
        self.department_combobox = QComboBox()
        self.department_combobox.addItems(['Select Department', 'BME', 'CHEM', 'CIVIL', 'CSE', 'ECE', 'EEE', 'MECH', 'IT', 'PHY'])
        self.department_combobox.setStyleSheet("""
            QComboBox {
                background-color: #f0f0f0;
                border: 2px solid #4CAF50;
                border-radius: 5px;
                padding: 5px;
            }
            QComboBox::down-arrow {
                image: url("C:/Users/madhu/Downloads/arrow.png");  # Use a custom arrow image if desired
                width: 20px;
                height: 20px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left-width: 1px;
                border-left-color: darkgray;
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }
            QComboBox::down-arrow {
                image: url("C:/Users/madhu/Downloads/arrow.png");  # Use a custom arrow image if desired
                width: 20px;
                height: 20px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                border: 2px solid #4CAF50;
                selection-background-color: #4CAF50;
            }
        """)
        self.department_combobox.currentIndexChanged.connect(self.populate_lab_names)
        layout.addWidget(self.department_combobox)

        # Staff Name ComboBox
        self.staff_label = QLabel('LAB NAME:')
        self.staff_label.setStyleSheet("""
            font-weight: bold;
            color: white;
            font-size: 16px;
            background-color: #2E8B57;
            padding: 10px;
            border: 2px solid #4CAF50;
            border-radius: 5px;
        """)
        layout.addWidget(self.staff_label)
        self.staff_combobox = QComboBox()
        self.staff_combobox.addItems(['Select Lab'])
        self.staff_combobox.setStyleSheet("""
            QComboBox {
                background-color: #f0f0f0;
                border: 2px solid #4CAF50;
                border-radius: 5px;
                padding: 5px;
            }
            QComboBox::down-arrow {
                image: url("C:/Users/madhu/Downloads/arrow.png");  # Use a custom arrow image if desired
                width: 20px;
                height: 20px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left-width: 1px;
                border-left-color: darkgray;
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                border: 2px solid #4CAF50;
                selection-background-color: #4CAF50;
            }
        """)
        layout.addWidget(self.staff_combobox)

        self.generate_button = QPushButton('Generate Timetable')
        self.generate_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                padding: 10px 20px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3e8e41;
            }
        """)
        self.generate_button.clicked.connect(self.generate_timetable)
        layout.addWidget(self.generate_button)
        
        # Timetable Display
        self.timetable_label = QLabel('TIMETABLE:')
        self.timetable_label.setStyleSheet("""
            font-weight: bold;
            color: white;
            font-size: 16px;
            background-color: #2E8B57;
            padding: 10px;
            border: 2px solid #4CAF50;
            border-radius: 5px;
        """)
        layout.addWidget(self.timetable_label)

        self.timetable_widget = LabTimetableWidget()
        self.timetable_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.timetable_widget, 1)  # Adding the stretch factor to make it expand

        # Save as PDF Button
        self.save_pdf_button = QPushButton('Save Timetable as PDF')
        self.save_pdf_button.setStyleSheet('''
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                padding: 10px 20px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3e8e41;
            }'''
        )
        self.save_pdf_button.clicked.connect(self.save_timetable_as_pdf)
        layout.addWidget(self.save_pdf_button)

    def save_timetable_as_pdf(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Timetable as PDF", "", "PDF Files (.pdf);;All Files ()")
        if file_path:
            self.timetable_widget.save_table_as_pdf(file_path)

    def generate_timetable(self):
        staff_name = self.staff_combobox.currentText()
        selected_department = self.department_combobox.currentText()
        if staff_name == 'Select Staff':
            return

        # Fetch the timetable for the selected staff member from the database
        cursor.execute('SELECT lab_value FROM labs_table WHERE name = ?', (staff_name,))
        row = cursor.fetchone()
        if row:
            timetable_data = ast.literal_eval(row[0])
            self.timetable_widget.populate_timetable(timetable_data)

    def populate_lab_names(self):
        # Fetch staff names from database based on the selected department
        selected_department = self.department_combobox.currentText()
        
        if selected_department != 'Select Department':
            cursor.execute("SELECT SUBJECT,MON,TUE,WED,THUR,FRI FROM lab WHERE dept=?",('CSE',))
            rows = cursor.fetchall()
            staff_names = [row[0] for row in rows]  # Extract names from rows
        else:
            staff_names = ['Select Staff']
        
        self.staff_combobox.clear()
        self.staff_combobox.addItems(staff_names)

class AdminViewStaff(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('ADMIN VIEW STAFF PAGE')
        self.showMaximized()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(20)

        # Department ComboBox
        self.department_label = QLabel('DEPARTMENT:')
        self.department_label.setStyleSheet("""
            font-weight: bold;
            color: white;
            font-size: 16px;
            background-color: #2E8B57;
            padding: 10px;
            border: 2px solid #4CAF50;
            border-radius: 5px;
        """)
        layout.addWidget(self.department_label)
        self.department_combobox = QComboBox()
        self.department_combobox.addItems(['Select Department', 'BME', 'CHEM', 'CIVIL', 'CSE', 'ECE', 'EEE', 'ENG', 'MECH', 'IT', 'PHY', 'TAM'])
        self.department_combobox.setStyleSheet("""
            QComboBox {
                background-color: #f0f0f0;
                border: 2px solid #4CAF50;
                border-radius: 5px;
                padding: 5px;
            }
            QComboBox::down-arrow {
                image: url("C:/Users/madhu/Downloads/arrow.png");  # Use a custom arrow image if desired
                width: 20px;
                height: 20px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left-width: 1px;
                border-left-color: darkgray;
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                border: 2px solid #4CAF50;
                selection-background-color: #4CAF50;
            }
        """)
        self.department_combobox.currentIndexChanged.connect(self.populate_staff_names)
        layout.addWidget(self.department_combobox)

        # Staff Name ComboBox
        self.staff_label = QLabel('STAFF NAME:')
        self.staff_label.setStyleSheet("""
            font-weight: bold;
            color: white;
            font-size: 16px;
            background-color: #2E8B57;
            padding: 10px;
            border: 2px solid #4CAF50;
            border-radius: 5px;""")
        layout.addWidget(self.staff_label)
        self.staff_combobox = QComboBox()
        self.staff_combobox.addItems(['Select Staff'])
        self.staff_combobox.setStyleSheet("""
            QComboBox {
                background-color: #f0f0f0;
                border: 2px solid #4CAF50;
                border-radius: 5px;
                padding: 5px;
            }
            QComboBox::down-arrow {
                image: url("C:/Users/madhu/Downloads/arrow.png");  # Use a custom arrow image if desired
                width: 20px;
                height: 20px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left-width: 1px;
                border-left-color: darkgray;
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                border: 2px solid #4CAF50;
                selection-background-color: #4CAF50;
            }
        """)
        layout.addWidget(self.staff_combobox)

        self.generate_button = QPushButton('Generate Timetable')
        self.generate_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                padding: 10px 20px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3e8e41;
            }
        """)
        self.generate_button.clicked.connect(self.generate_timetable)
        layout.addWidget(self.generate_button)
        
        # Timetable Display
        self.timetable_label = QLabel('TIMETABLE:')
        self.timetable_label.setStyleSheet("""
            font-weight: bold;
            color: white;
            font-size: 16px;
            background-color: #2E8B57;
            padding: 10px;
            border: 2px solid #4CAF50;
            border-radius: 5px;
        """)
        layout.addWidget(self.timetable_label)

        # Timetable Widget
        self.timetable_widget = StaffTimetableWidget()
        layout.addWidget(self.timetable_widget)

        self.staff_name= QLabel(f'STAFF NAME : {self.staff_combobox.currentText()}')
        self.staff_name.setStyleSheet("""
            font-weight: bold;
            color: black;
            font-size: 16px;
            padding: 10px;
            border: 2px solid #4CAF50;
            border-radius: 5px;
        """)
        layout.addWidget(self.staff_name)

        # Save as PDF Button
        self.save_pdf_button = QPushButton('Save Timetable as PDF')
        self.save_pdf_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                padding: 10px 20px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3e8e41;
            }
        """)
        self.save_pdf_button.clicked.connect(self.save_timetable_as_pdf)
        layout.addWidget(self.save_pdf_button)

    def generate_timetable(self):
        staff_name = self.staff_combobox.currentText()
        if staff_name == 'Select Staff':
            return

        self.staff_name.setText(f'STAFF NAME : {staff_name}')
        
        # Fetch the timetable for the selected staff member from the database
        cursor.execute('SELECT MON,TUE,WED,THUR,FRI FROM staffn WHERE name = ?', (staff_name,))
        rows = cursor.fetchone()
        print(rows)
        converted_rows = [ast.literal_eval(row) for row in rows]
        print(converted_rows)
        self.timetable_widget.populate_timetable(converted_rows)

    def save_timetable_as_pdf(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Timetable as PDF", "", "PDF Files (.pdf);;All Files ()")
        if file_path:
            self.timetable_widget.save_table_as_pdf(file_path)

    def populate_staff_names(self):
        # Fetch staff names from database based on the selected department
        selected_department = self.department_combobox.currentText()
        
        if selected_department != 'Select Department':
            cursor.execute('SELECT name FROM staffn WHERE dept = ?', (selected_department,))
            rows = cursor.fetchall()
            staff_names = [row[0] for row in rows]  # Extract names from rows
        else:
            staff_names = ['Select Staff']
        
        self.staff_combobox.clear()
        self.staff_combobox.addItems(staff_names)

class AdminViewSection(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('ADMIN VIEW SECTION PAGE')
        self.showMaximized()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(20)

        # Department ComboBox
        self.department_label = QLabel('DEPARTMENT:')
        self.department_label.setStyleSheet("""
            font-weight: bold;
            color: white;
            font-size: 16px;
            background-color: #2E8B57;
            padding: 10px;
            border: 2px solid #4CAF50;
            border-radius: 5px;
        """)
        layout.addWidget(self.department_label)
        self.department_combobox = QComboBox()
        self.department_combobox.addItems(['Select Department', 'BME', 'CHEM', 'CIVIL', 'CSE', 'ECE', 'EEE', 'MECH', 'IT', 'PHY'])
        self.department_combobox.setStyleSheet("""
            QComboBox {
                background-color: #f0f0f0;
                border: 2px solid #4CAF50;
                border-radius: 5px;
                padding: 5px;
            
            }
            QComboBox::down-arrow {
                image: url("C:/Users/madhu/Downloads/arrow.png");  # Use a custom arrow image if desired
                width: 20px;
                height: 20px;
            }

            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left-width: 1px;
                border-left-color: darkgray;
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                border: 2px solid #4CAF50;
                selection-background-color: #4CAF50;
            }
        """)
        self.department_combobox.currentIndexChanged.connect(self.populate_lab_names)
        layout.addWidget(self.department_combobox)

        # Staff Name ComboBox
        self.staff_label = QLabel('SECTION:')
        self.staff_label.setStyleSheet("""
            font-weight: bold;
            color: white;
            font-size: 16px;
            background-color: #2E8B57;
            padding: 10px;
            border: 2px solid #4CAF50;
            border-radius: 5px;
        """)
        layout.addWidget(self.staff_label)
        self.staff_combobox = QComboBox()
        self.staff_combobox.addItems(['Select Section'])
        self.staff_combobox.setStyleSheet("""
            QComboBox {
                background-color: #f0f0f0;
                border: 2px solid #4CAF50;
                border-radius: 5px;
                padding: 5px;
            }
            QComboBox::down-arrow {
                image: url("C:/Users/madhu/Downloads/arrow.png");  # Use a custom arrow image if desired
                width: 20px;
                height: 20px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left-width: 1px;
                border-left-color: darkgray;
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                border: 2px solid #4CAF50;
                selection-background-color: #4CAF50;
            }
        """)
        layout.addWidget(self.staff_combobox)

        self.generate_button = QPushButton('View Timetable')
        self.generate_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                padding: 10px 20px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3e8e41;
            }
        """)
        self.generate_button.clicked.connect(self.generate_timetable)
        layout.addWidget(self.generate_button)
        
        # Timetable Display
        self.timetable_label = QLabel('TIMETABLE:')
        self.timetable_label.setStyleSheet("""
            font-weight: bold;
            color: white;
            font-size: 16px;
            background-color: #2E8B57;
            padding: 10px;
            border: 2px solid #4CAF50;
            border-radius: 5px;
        """)
        layout.addWidget(self.timetable_label)

        self.timetable_widget = TimetableWidget()
        layout.addWidget(self.timetable_widget)

        # Save as PDF Button
        self.save_pdf_button = QPushButton('Save Timetable as PDF')
        self.save_pdf_button.setStyleSheet('''
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                padding: 10px 20px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3e8e41;
            }'''
        )
        self.save_pdf_button.clicked.connect(self.save_timetable_as_pdf)
        layout.addWidget(self.save_pdf_button)
        
    def save_timetable_as_pdf(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Timetable as PDF", "", "PDF Files (.pdf);;All Files ()")
        if file_path:
            self.timetable_widget.save_table_as_pdf(file_path)

    def generate_timetable(self):
     staff_name = self.staff_combobox.currentText()
     selected_department = self.department_combobox.currentText()
     if staff_name == 'Select Staff':
         return
    # Fetch the timetable for the selected staff member from the database
     cursor.execute('SELECT data FROM schedule_data WHERE department = ? and section = ?', (selected_department, staff_name))
     row = cursor.fetchone()
     if row:
        timetable_data = ast.literal_eval(row[0])  # Parse the JSON string
        if isinstance(timetable_data, dict):
            # Extract values corresponding to days
            timetable_data = [timetable_data[key] for key in ('MON', 'TUE', 'WED', 'THUR', 'FRI')]
            self.timetable_widget.populate_timetable(timetable_data)

    def populate_lab_names(self):
        # Fetch staff names from database based on the selected department
        selected_department = self.department_combobox.currentText()
        selected_section=self.department_combobox.currentText()
        if selected_department != 'Select Department':
            cursor.execute("SELECT section FROM schedule_data WHERE department=?",(selected_department,))
            rows = cursor.fetchall()
            
            staff_names = [row[0] for row in rows]  # Extract names from rows
        else:
            staff_names = ['Select Staff']
        
        self.staff_combobox.clear()
        self.staff_combobox.addItems(staff_names)

class ViewWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('ADMIN VIEW PAGE')
        self.setGeometry(100, 100, 500, 600)
        self.showMaximized()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(20)

        # Create a horizontal layout to centralize the buttons
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(40)
        layout.addLayout(button_layout)

        # Add Staff button with image and label
        self.staff_widget = QWidget()
        self.staff_layout = QVBoxLayout(self.staff_widget)
        self.staff_layout.setAlignment(Qt.AlignHCenter)
        self.view_staff_button = QPushButton()
        self.view_staff_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.view_staff_button.clicked.connect(self.view_staff)
        self.set_button_image(self.view_staff_button, "C:/Users/KAVI/Downloads/stafficon.png")  # Update with the correct path
        self.staff_label = QLabel("VIEW STAFF")
        self.staff_label.setAlignment(Qt.AlignCenter)
        self.staff_label.setFont(QFont("Arial", 20, QFont.Bold))
        self.staff_label.setStyleSheet('color:white;')
        self.staff_layout.addWidget(self.view_staff_button)
        self.staff_layout.addWidget(self.staff_label)
        button_layout.addWidget(self.staff_widget)

        # Add Subject button with image and label
        self.subj_widget = QWidget()
        self.subj_layout = QVBoxLayout(self.subj_widget)
        self.subj_layout.setAlignment(Qt.AlignHCenter)
        self.add_subj_button = QPushButton()
        self.add_subj_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.add_subj_button.clicked.connect(self.view_section)
        self.set_button_image(self.add_subj_button, "C:/Users/KAVI/Downloads/sectionicon.png")  # Update with the correct path
        self.subj_label = QLabel("VIEW SECTION")
        self.subj_label.setAlignment(Qt.AlignCenter)
        self.subj_label.setFont(QFont("Arial", 20, QFont.Bold))
        self.subj_label.setStyleSheet('color:white;')
        self.subj_layout.addWidget(self.add_subj_button)
        self.subj_layout.addWidget(self.subj_label)
        button_layout.addWidget(self.subj_widget)

        # Add Lab button with image and label
        self.lab_widget = QWidget()
        self.lab_layout = QVBoxLayout(self.lab_widget)
        self.lab_layout.setAlignment(Qt.AlignHCenter)
        self.view_lab_button = QPushButton()
        self.view_lab_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.view_lab_button.clicked.connect(self.view_lab)
        self.set_button_image(self.view_lab_button, "C:/Users/KAVI/Downloads/labicon.webp")  # Update with the correct path
        self.lab_label = QLabel("VIEW LAB")
        self.lab_label.setAlignment(Qt.AlignCenter)
        self.lab_label.setFont(QFont("Arial", 20, QFont.Bold))
        self.lab_label.setStyleSheet('color:white;')
        self.lab_layout.addWidget(self.view_lab_button)
        self.lab_layout.addWidget(self.lab_label)
        button_layout.addWidget(self.lab_widget)

        self.setLayout(layout)
        
        # Initialize background image
        self.background_image = QPixmap("C:/Users/KAVI/Downloads/addwindow.jpeg")

    def set_button_image(self, button, image_path):
        button.setIcon(QIcon(image_path))
        button.setIconSize(QSize(200, 200))  # Set icon size to match button size
        button.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 100px; /* Half of the icon size */
                background-color: transparent;
                width: 200px; /* Button width */
                height: 200px; /* Button height */
                margin: 20px;
            }
            QPushButton::hover {
                background-color: rgba(255, 255, 255, 50);
            }
        """)

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.rect()
        if not self.background_image.isNull():
            scaled_image = self.background_image.scaled(rect.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            painter.drawPixmap(rect.center() - scaled_image.rect().center(), scaled_image)

    def view_lab(self):
        self.view_lab_page = AdminViewLab()
        self.view_lab_page.show()

    def view_staff(self):
        self.view_staff_page = AdminViewStaff()
        self.view_staff_page.show()

    def view_section(self):
        self.view_section_page = AdminViewSection()
        self.view_section_page.show()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Time Table Management')
        self.setFixedSize(500,500)

        # Set the background image for the main window
        self.setStyleSheet("""
            QWidget {
                background-image: url(C:/Users/KAVI/Downloads/unnamed.png);
                background-position: center;
                background-repeat: no-repeat;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(20)

        self.welcome_label = QLabel('WELCOME TO TIME TABLE MANAGEMENT SYSTEM')
        self.welcome_label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.welcome_label.setStyleSheet("""
            font-weight: bold;
            color: white;
            background-color: black;
            padding: 10px;
            border-radius: 10px;
        """)
        self.welcome_label.setFont(QFont("Times New Roman", 20, QFont.Bold))
        layout.addWidget(self.welcome_label)

        self.login_button = QPushButton('GET STARTED')
        self.login_button.setStyleSheet("""
            background-color: white;
            color: black;
            font-weight: bold;
            border: 2px solid white;
            border-radius: 10px;
            padding: 10px;
        """)
        self.login_button.setFont(QFont("Times New Roman", 16, QFont.Bold))
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)

    def login(self):
        self.welcome = WelcomeWindow()  
        self.welcome.show()
        self.close()

class WelcomeWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('WELCOME PAGE')
        self.resize(500,500)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(20)
        
        self.adminlogin_button = QPushButton('LOGIN AS ADMIN')
        self.adminlogin_button.setIcon(QIcon("C:/Users/KAVI/Downloads/adminicon.png"))
        self.adminlogin_button.setIconSize(QSize(45, 45))
        self.adminlogin_button.setStyleSheet("""
            QPushButton {
                background-color: lightgreen;
                color: black;
                font-weight: bold;
                font-size: 24px;
                border-radius: 30px;
                padding: 20px;
                border: 2px solid black;
            }
            QPushButton:hover {
                background-color: #45a049;
                border: 10px solid #45a049;
            }
        """)
        self.adminlogin_button.setMinimumHeight(100)
        self.adminlogin_button.clicked.connect(self.login_admin)
        layout.addWidget(self.adminlogin_button)

        self.userlogin_button = QPushButton('LOGIN AS USER')
        self.userlogin_button.setIcon(QIcon("C:/Users/KAVI/Downloads/person.webp"))
        self.userlogin_button.setIconSize(QSize(45, 45))
        self.userlogin_button.setStyleSheet("""
            QPushButton {
                background-color: lightblue;
                color: black;
                font-weight: bold;
                font-size: 24px;
                border-radius: 30px;
                padding: 20px;
                border: 2px solid black;
            }
            QPushButton:hover {
                background-color: lightgrey;
                border: 2px solid lightgrey;
            }
        """)
        self.userlogin_button.setMinimumHeight(100)
        self.userlogin_button.clicked.connect(self.login_user)
        layout.addWidget(self.userlogin_button)  

        self.background_image = QPixmap("C:/Users/KAVI/Downloads/welcome.jpg")
    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.rect()
        if not self.background_image.isNull():
            scaled_image = self.background_image.scaled(rect.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            painter.drawPixmap(rect.center() - scaled_image.rect().center(), scaled_image)
  
    def login_admin(self):
        self.admin_window = AdminLoginWindow()
        self.admin_window.login_successful.connect(self.show_admin_main)
        self.admin_window.show()

    def login_user(self):
        self.user_window = UserLoginWindow()
        self.user_window.login_successful.connect(self.show_user_main)
        self.user_window.show()

    def show_admin_main(self, username):
        self.admin_main_window = AdminMainWindow(username)
        self.admin_main_window.show()
        self.hide()

    def show_user_main(self, username):
        self.user_main_window = UserMainWindow(username)
        self.user_main_window.show()
        self.hide()

class AdminLoginWindow(QWidget):
    login_successful = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle('ADMIN LOGIN PAGE')
        self.resize(500,600)
        self.background_image = QPixmap("C:/Users/KAVI/OneDrive/Documents/adminlog.jpg")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(20)

        icon_label = QLabel()
        icon_label.setPixmap(QPixmap("C:/Users/KAVI/Downloads/adminicon.png").scaled(100, 100, Qt.KeepAspectRatio))
        icon_layout = QHBoxLayout()
        icon_layout.addStretch()
        icon_layout.addWidget(icon_label)
        icon_layout.addStretch()
        layout.addLayout(icon_layout)

        welcome_label = QLabel("ADMIN LOGIN")  
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("font-weight: bold; color: black; font-size: 32px;")
        layout.addWidget(welcome_label)
        
        self.username_label = QLabel('USERNAME:')
        self.username_label.setStyleSheet("font-weight: bold; color: white;")
        self.username_label.setFont(QFont("Times New Roman", 14, QFont.Bold))
        layout.addWidget(self.username_label)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('ENTER USERNAME HERE')
        self.username_input.setStyleSheet("QLineEdit { font-size: 16px; padding: 8px; border: 2px solid gray; border-radius: 8px; background-color: white; }")
        layout.addWidget(self.username_input)

        password_layout = QHBoxLayout()
        self.password_label = QLabel('PASSWORD:')
        self.password_label.setStyleSheet("font-weight: bold; color: white;")
        self.password_label.setFont(QFont("Times New Roman", 14, QFont.Bold))
        layout.addWidget(self.password_label)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('ENTER PASSWORD HERE')
        self.password_input.setStyleSheet("QLineEdit { font-size: 16px; padding: 8px; border: 2px solid gray; border-radius: 8px; background-color: white; }")
        self.password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(self.password_input)

        self.toggle_password_button = QPushButton()
        self.toggle_password_button.setIcon(QIcon("C:/Users/KAVI/Downloads/hide.jpg"))  # Replace with your hide icon path
        self.toggle_password_button.setIconSize(QSize(24, 24))
        self.toggle_password_button.setCheckable(True)
        self.toggle_password_button.clicked.connect(self.toggle_password_visibility)
        password_layout.addWidget(self.toggle_password_button)
        
        layout.addLayout(password_layout)

        self.login_button = QPushButton('LOGIN')
        self.login_button.setMinimumHeight(50)
        self.login_button.setStyleSheet("""
            QPushButton { 
                background-color: rgba(0, 191, 255, 1.0); 
                color: white; 
                font-weight: bold; 
                font-size: 16px;
                border: none; /* Remove button border */
                border-radius: 8px; /* Rounded corners */
            }
            QPushButton:hover { 
                background-color: #2ca02c; 
            }
            QPushButton:pressed { 
                background-color: #116611; 
            }
        """)
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def toggle_password_visibility(self):
        if self.password_input.echoMode() == QLineEdit.Password:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.toggle_password_button.setIcon(QIcon("C:/Users/KAVI/Downloads/showicon.jpeg"))  # Replace with your show icon path
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.toggle_password_button.setIcon(QIcon("C:/Users/KAVI/Downloads/hide.jpg"))

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if username == "admin" and password == "admin":
            self.login_successful.emit("admin")
        else:
            QMessageBox.warning(self, 'LOGIN FAILED', 'INVALID USERNAME AND PASSWORD')

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.rect()
        if not self.background_image.isNull():
            scaled_image = self.background_image.scaled(rect.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            painter.drawPixmap(rect.center() - scaled_image.rect().center(), scaled_image)

class AdminMainWindow(QWidget):
    def __init__(self, username):
        super().__init__()
        self.setWindowTitle('ADMIN PAGE')
        self.resize(500,600)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(20)

        button_width = 300
        button_height = 80

        self.add_button = QPushButton('ADD NEW STAFF / SUBJECT')
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: black;
                color: white;
                font-weight: bold;
                border-radius: 10px;
                width: %dpx;
                height: %dpx;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3c9039;
            }
        """ % (button_width, button_height))
        self.add_button.setFont(QFont("Times New Roman", 16, QFont.Bold))
        self.add_button.clicked.connect(self.add)
        layout.addWidget(self.add_button)

        self.view_button = QPushButton('VIEW TIMETABLE')
        self.view_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: black;
                font-weight: bold;
                border-radius: 10px ;
                width: %dpx;
                height: %dpx;
            }
            QPushButton:hover {
                background-color: red;
            }
            QPushButton:pressed {
                background-color: #006186;
            }
        """ % (button_width, button_height))
        self.view_button.setFont(QFont("Times New Roman", 16, QFont.Bold))
        self.view_button.clicked.connect(self.view)
        layout.addWidget(self.view_button)

        self.feedback_button = QPushButton('SEE FEEDBACK')
        self.feedback_button.setStyleSheet("""
            QPushButton {
                background-color: darkbrown;
                color: white;
                font-weight: bold;
                border-radius: 10px;
                width: %dpx;
                height: %dpx;
                border-radius: 5px solid white;
            }
            QPushButton:hover {
                background-color: #007aa3;
            }
            QPushButton:pressed {
                background-color: #006186;
            }
        """ % (button_width, button_height))
        self.feedback_button.setFont(QFont("Times New Roman", 16, QFont.Bold))
        self.feedback_button.clicked.connect(self.see_feedback)
        layout.addWidget(self.feedback_button)

        self.generate_button = QPushButton('GENERATE TIMETABLE')
        self.generate_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: black;
                font-weight: bold;
                border-radius: 10px;
                width: %dpx;
                height: %dpx;
            }
            QPushButton:hover {
                background-color: #e6bf00;
            }
            QPushButton:pressed {
                background-color: #cca200;
            }
        """ % (button_width, button_height))
        self.generate_button.setFont(QFont("Times New Roman", 16, QFont.Bold))
        self.generate_button.clicked.connect(self.generate_timetable)
        layout.addWidget(self.generate_button)

        self.background_image = QPixmap("C:/Users/KAVI/OneDrive/Documents/adminmain.jpg")
    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.rect()
        if not self.background_image.isNull():
            scaled_image = self.background_image.scaled(rect.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            painter.drawPixmap(rect.center() - scaled_image.rect().center(), scaled_image)

    def see_feedback(self):
        self.see_feedbacks=AdminFeedbackView()
        self.see_feedbacks.show()

    def add(self):
        self.add_window = AddWindow()
        self.add_window.show()

    def view(self):
        self.view_button=ViewWindow()
        self.view_button.show()

    def generate_timetable(self):
        self.generate=GenerateTimeTable()
        self.generate.show()

class AdminFeedbackView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Admin Feedback View')
        self.resize(500,600)

        # Layout
        layout = QVBoxLayout()

        # Feedback Text Display
        self.feedback_display = QTextEdit(self)
        self.feedback_display.setReadOnly(True)
        self.feedback_display.setStyleSheet("""
            QTextEdit {
                background-color: #f0f0f0;
                color: #333;
                font-family: Arial, sans-serif;
                font-size: 14px;
                border: 2px solid #ccc;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        layout.addWidget(self.feedback_display)

        # Close Button
        self.close_button = QPushButton('CLOSE', self)
        self.close_button.clicked.connect(self.close)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: #5cb85c;
                color: white;
                font-weight: bold;
                font-family: Arial, sans-serif;
                font-size: 14px;
                border: 2px solid #4cae4c;
                border-radius: 5px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #4cae4c;
                border: 2px solid #45a049;
            }
            QPushButton:pressed {
                background-color: #45a049;
                border: 2px solid #398439;
            }
        """)
        layout.addWidget(self.close_button)

        # Set Layout
        self.setLayout(layout)

        # Load Feedback
        self.load_feedback()
        self.background_image = QPixmap("C:/Users/KAVI/OneDrive/Documents/adminlog.jpg")
    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.rect()
        if not self.background_image.isNull():
            scaled_image = self.background_image.scaled(rect.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            painter.drawPixmap(rect.center() - scaled_image.rect().center(), scaled_image)

    def load_feedback(self):
        try:
            connection = sqlite3.connect('feedback.db')
            cursor = connection.cursor()
            # Select unseen feedback
            sql = '''SELECT staffname, feedback FROM Feedback WHERE seen=0'''
            cursor.execute(sql)
            rows = cursor.fetchall()

            if rows:
                # Prepare feedback text
                feedback_texts = [f'{row[0]}: {row[1]}' for row in rows]
                feedback_text = '\n'.join(feedback_texts)
                self.feedback_display.setText(feedback_text)

                # Mark feedback as seen
                update_sql = '''UPDATE Feedback SET seen=1 WHERE staffname=?'''
                cursor.executemany(update_sql, [(row[0],) for row in rows])

                # Commit and close the connection
                connection.commit()
            else:
                self.feedback_display.setText("No new feedback available.")
            
            connection.close()
        except sqlite3.Error as e:
            QMessageBox.critical(self, 'Database Error', f'An error occurred: {e}')
            print(f'An error occurred: {e}')  # Debugging purpose

class AddWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('ADD PAGE')
        self.resize(700,700)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(20)

        # Create a horizontal layout to centralize the buttons
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(40)
        layout.addLayout(button_layout)

        # Add Staff button with image and label
        self.staff_widget = QWidget()
        self.staff_layout = QVBoxLayout(self.staff_widget)
        self.staff_layout.setAlignment(Qt.AlignHCenter)
        self.add_staff_button = QPushButton()
        self.add_staff_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.add_staff_button.clicked.connect(self.add_staff)
        self.set_button_image(self.add_staff_button, "C:/Users/KAVI/Downloads/stafficon.png")  # Update with the correct path
        self.staff_label = QLabel("ADD STAFF")
        self.staff_label.setAlignment(Qt.AlignCenter)
        self.staff_label.setFont(QFont("Arial", 20, QFont.Bold))
        self.staff_label.setStyleSheet('color:white;')
        self.staff_layout.addWidget(self.add_staff_button)
        self.staff_layout.addWidget(self.staff_label)
        button_layout.addWidget(self.staff_widget)

        # Add Subject button with image and label
        self.subj_widget = QWidget()
        self.subj_layout = QVBoxLayout(self.subj_widget)
        self.subj_layout.setAlignment(Qt.AlignHCenter)
        self.add_subj_button = QPushButton()
        self.add_subj_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.add_subj_button.clicked.connect(self.add_subj)
        self.set_button_image(self.add_subj_button, "C:/Users/KAVI/Downloads/subjecticon.jpg")  # Update with the correct path
        self.subj_label = QLabel("ADD SUBJECT")
        self.subj_label.setAlignment(Qt.AlignCenter)
        self.subj_label.setFont(QFont("Arial", 20, QFont.Bold))
        self.subj_label.setStyleSheet('color:white;')
        self.subj_layout.addWidget(self.add_subj_button)
        self.subj_layout.addWidget(self.subj_label)
        button_layout.addWidget(self.subj_widget)

        self.setLayout(layout)

        # Set background image
        self.background_image = QPixmap("C:/Users/KAVI/Downloads/addwindow.jpeg")

    def set_button_image(self, button, image_path):
        button.setIcon(QIcon(image_path))
        button.setIconSize(QSize(200, 200))  # Set icon size to match button size
        button.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 100px; /* Half of the icon size */
                background-color: transparent;
                width: 200px; /* Button width */
                height: 200px; /* Button height */
                margin: 20px;
            }
            QPushButton::hover {
                background-color: rgba(255, 255, 255, 50);
            }
        """)    

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.rect()
        if not self.background_image.isNull():
            scaled_image = self.background_image.scaled(rect.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            painter.drawPixmap(rect.center() - scaled_image.rect().center(), scaled_image)
    def add_staff(self):
        self.add_newstaff = AdminCreateStaff()
        self.add_newstaff.show()

    def add_subj(self):
        self.add_newsubj = CreateSubjectWindow()
        self.add_newsubj.show()

class ForgotPasswordWindow(QWidget):
    otp_verified = pyqtSignal(str)  # Signal to emit when OTP is verified

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Forgot Password')
        self.resize(500,600)  # Explicitly set window size and position

        # Create layout
        layout = QVBoxLayout()

        # Add flexible space at the top
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Add email label and input
        self.email_label = QLabel('Email:')
        layout.addWidget(self.email_label)
        self.email_input = QLineEdit()
        layout.addWidget(self.email_input)

        # Add button to send OTP
        self.send_otp_button = QPushButton('Send OTP')
        layout.addWidget(self.send_otp_button)
        self.send_otp_button.clicked.connect(self.send_otp)

        # Add OTP label and input
        self.otp_label = QLabel('OTP:')
        layout.addWidget(self.otp_label)
        self.otp_input = QLineEdit()
        layout.addWidget(self.otp_input)

        # Add button to verify OTP
        self.verify_otp_button = QPushButton('Verify OTP')
        layout.addWidget(self.verify_otp_button)
        self.verify_otp_button.clicked.connect(self.verify_otp)

        # Add close button
        self.close_button = QPushButton('Close')
        layout.addWidget(self.close_button)
        self.close_button.clicked.connect(self.close)

        # Add flexible space at the bottom
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.setLayout(layout)

        # Set up timer for OTP timeout
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.otp_timeout)
        self.otp = None  # Initialize OTP as None

        # Apply styles
        self.apply_styles()

    def apply_styles(self):
        self.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #333;
            }
            QLineEdit {
                font-size: 14px;
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            QLineEdit:focus {
                border: 1px solid #007BFF;
                background-color: #E6F7FF;
            }
            QPushButton {
                font-size: 14px;
                padding: 5px;
                border: 1px solid #007BFF;
                border-radius: 5px;
                background-color: #007BFF;
                color: white;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
        """)

    def send_otp(self):
        self.email = self.email_input.text().strip()

        if not self.email:
            QMessageBox.warning(self, 'Incomplete Fields', 'Please enter your email.')
            return

        # Establish database connection
        conn1 = sqlite3.connect('staff.db')
        cursor1 = conn1.cursor()

        cursor1.execute('SELECT * FROM authen WHERE email=?', (self.email,))
        user = cursor1.fetchone()

        if user:
            self.otp = random.randint(100000, 999999)
            self.send_email(self.email, self.otp)
            self.timer.start(60000)  # Start timer for 60 seconds
            QMessageBox.information(self, 'OTP Sent', 'OTP has been sent to your email.')
        else:
            QMessageBox.warning(self, 'Invalid Email', 'No user exists with the given email.')

        cursor1.close()
        conn1.close()

    def send_email(self, to_email, otp):
        sender_email = 'amudhakavi05@gmail.com'
        sender_password = 'ikkstdqstpzjmqiw'

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, sender_password)

            subject = 'Your OTP Code'
            body = f'Your OTP code is {otp}. Use this to reset your password.'
            msg = f'Subject: {subject}\n\n{body}'

            server.sendmail(sender_email, to_email, msg)
            server.quit()
        except Exception as e:
            QMessageBox.warning(self, 'Email Error', f'Failed to send email: {str(e)}')

    def verify_otp(self):
        if not self.otp:
            QMessageBox.warning(self, 'Error', 'Please send OTP first.')
            return

        entered_otp = self.otp_input.text().strip()

        if entered_otp == str(self.otp):
            QMessageBox.information(self, 'OTP Verified', 'OTP verified successfully.')
            self.timer.stop()
            self.otp_verified.emit(self.email)  # Emit signal with email
        else:
            QMessageBox.warning(self, 'Invalid OTP', 'The OTP you entered is invalid.')

    def otp_timeout(self):
        self.timer.stop()
        QMessageBox.warning(self, 'Timeout', 'OTP verification timeout. Please request a new OTP.')
        self.otp = None

class SetNewPasswordWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Set New Password')
        self.resize(500,600)  # Explicitly set window size and position

        self.email = None

        # Create layout
        layout = QVBoxLayout()

        # Add flexible space at the top
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Add new password label and input
        self.new_password_label = QLabel('New Password:')
        layout.addWidget(self.new_password_label)
        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.new_password_input)

        # Add confirm password label and input
        self.confirm_password_label = QLabel('Confirm Password:')
        layout.addWidget(self.confirm_password_label)
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.confirm_password_input)

        # Add set password button
        self.set_password_button = QPushButton('Set Password')
        layout.addWidget(self.set_password_button)
        self.set_password_button.clicked.connect(self.set_password)

        # Add close button
        self.close_button = QPushButton('Close')
        layout.addWidget(self.close_button)
        self.close_button.clicked.connect(self.close)

        # Add flexible space at the bottom
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.setLayout(layout)

        # Apply styles
        self.apply_styles()

    def apply_styles(self):
        self.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #333;
            }
            QLineEdit {
                font-size: 14px;
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            QLineEdit:focus {
                border: 1px solid #007BFF;
                background-color: #E6F7FF;
            }
            QPushButton {
                font-size: 14px;
                padding: 5px;
                border: 1px solid #007BFF;
                border-radius: 5px;
                background-color: #007BFF;
                color: white;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
        """)

    def set_password(self):
        new_password = self.new_password_input.text().strip()
        confirm_password = self.confirm_password_input.text().strip()

        if not new_password or not confirm_password:
            QMessageBox.warning(self, 'Incomplete Fields', 'Please fill in all fields.')
            return

        if new_password != confirm_password:
            QMessageBox.warning(self, 'Password Mismatch', 'The passwords do not match.')
            return

        # Update the password in the database
        conn1 = sqlite3.connect('staff.db')
        cursor1 = conn1.cursor()

        cursor1.execute('UPDATE authen SET password=? WHERE email=?', (new_password, self.email))
        conn1.commit()

        cursor1.close()
        conn1.close()

        QMessageBox.information(self, 'Success', 'Password updated successfully.')
        self.close()

class ForgotPasswordMainWindow(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.resize(500,600) # Explicitly set window size and position
        self.setWindowTitle('Change Password')

        self.forgot_password_window = ForgotPasswordWindow()
        self.set_new_password_window = SetNewPasswordWindow()

        self.addWidget(self.forgot_password_window)
        self.addWidget(self.set_new_password_window)

        self.forgot_password_window.otp_verified.connect(self.switch_to_set_password)

        self.setCurrentIndex(0)

    def switch_to_set_password(self, email):
        self.set_new_password_window.email = email
        self.setCurrentIndex(1)
class AdminCreateStaff(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('CREATE NEW ACCOUNT')
        self.resize(700, 700)  # Enlarged window size
        self.initUI()
        self.timer = QTimer()
        self.timer.setSingleShot(True)  # Set to run only once
        self.timer.timeout.connect(self.verify_timeout)
        self.otp = None

    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Personal Details
        personal_group = QGroupBox("Personal Details")
        personal_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setMinimumSize(300, 30)  # Set minimum size for QLineEdit
        personal_layout.addRow(self.createStyledLabel('Name'), self.name_input)
        
        self.posting_combo = QComboBox()
        self.posting_combo.addItems(['Associate Professor', 'Assistant Professor', 'Lab Assistant', 'Professor'])
        self.posting_combo.setMinimumSize(300, 30)  # Set minimum size for QComboBox
        personal_layout.addRow(self.createStyledLabel("Posting"), self.posting_combo)
        
        self.department_combo = QComboBox()
        self.department_combo.addItems(['BME', 'CHEM', 'CIVIL', 'CSE', 'ECE', 'EEE', 'ENG', 'MECH', 'IT', 'PHY', 'TAM'])
        self.department_combo.setMinimumSize(300, 30)  # Set minimum size for QComboBox
        personal_layout.addRow(self.createStyledLabel("Department"), self.department_combo)
        
        main_layout.addWidget(personal_group)
        personal_group.setLayout(personal_layout)

        # Subject Details
        subject_group = QGroupBox("Subject Details")
        subject_layout = QFormLayout()
        
        self.subject_inputs = []
        for i in range(1, 5):
            subject_label = self.createStyledLabel(f"Subject {i}")
            subject_input = QLineEdit()
            subject_input.setMinimumSize(300, 30)  # Set minimum size for QLineEdit
            self.subject_inputs.append(subject_input)
            subject_layout.addRow(subject_label, subject_input)
        
        subject_group.setLayout(subject_layout)
        main_layout.addWidget(subject_group)

        # Email Verification
        email_group = QGroupBox("Email Verification")
        email_layout = QVBoxLayout()
        
        self.email_label = self.createStyledLabel('Email:')
        email_layout.addWidget(self.email_label)
        
        self.email_input_verification = QLineEdit()
        self.email_input_verification.setMinimumSize(300, 30)  # Set minimum size for QLineEdit
        email_layout.addWidget(self.email_input_verification)
        
        self.create_button = QPushButton('SEND OTP')
        self.create_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.create_button.clicked.connect(self.create_account)
        email_layout.addWidget(self.create_button)
        
        self.otp_label = self.createStyledLabel('OTP:')
        email_layout.addWidget(self.otp_label)
        
        self.otp_input = QLineEdit()
        self.otp_input.setMinimumSize(300, 30)  # Set minimum size for QLineEdit
        email_layout.addWidget(self.otp_input)
        
        self.verify_button = QPushButton('VERIFY OTP')
        self.verify_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.verify_button.clicked.connect(self.verify_otp)
        email_layout.addWidget(self.verify_button)
        
        email_group.setLayout(email_layout)
        main_layout.addWidget(email_group)

    def createStyledLabel(self, text):
        label = QLabel(text)
        label.setFont(QFont('Arial', 12))  # Set font size 
        return label

    def send_mail(self, receiver_email):
        if self.otp is None:  
            sender_email = 'amudhakavi05@gmail.com'  # Replace with your email
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, 'ikkstdqstpzjmqiw')  # Replace with your password

            self.otp = random.randint(100000, 999999)
            message = f'''Dear User,
            Your account creation is in process. To complete the registration process and verify your account, please use the following OTP: {self.otp}'''
            text = f'Subject: Account Verification OTP\n\n{message}'
            server.sendmail(sender_email, receiver_email, text)
            print("Email has been sent")
            server.quit()

    def verify_otp(self):
        if self.otp is None:
            QMessageBox.warning(self, 'Error', 'Please send OTP first.')
            return

        user_input_otp = self.otp_input.text()
        if user_input_otp == str(self.otp):
            self.print_values()  # Call method to print values or save to database
            self.close()  # Close the window after verification
        else:
            QMessageBox.warning(self, 'Verification Failed', 'Sorry! You have entered an incorrect OTP.')
            self.otp_input.clear()

    def verify_timeout(self):
        QMessageBox.warning(self, 'Verification Timeout', 'Time limit exceeded for OTP verification. Please try again.')
        self.close()  

    def create_account(self):
        email = self.email_input_verification.text()

        if not all([self.name_input.text(), self.email_input_verification.text(), self.posting_combo.currentText(), self.department_combo.currentText()]):
            QMessageBox.warning(self, 'Incomplete Fields', 'Please fill in all fields.')
            return

        for subject_input in self.subject_inputs:
            if not subject_input.text():
                QMessageBox.warning(self, 'Incomplete Fields', 'Please fill in all subject fields.')
                return

        if email == '':
            QMessageBox.warning(self, 'Incomplete Fields', 'Please enter your email.')
        else:
            self.send_mail(email)
            self.timer.start(60000)

    def print_values(self):
        name = self.name_input.text().upper() if self.name_input is not None else ""
        posting = self.posting_combo.currentText() 
        department = self.department_combo.currentText()
        subjects = [subject_input.text() for subject_input in self.subject_inputs]
        s='[0,0,0,0,0,0,0]'
        staff = (name[:3],name,10,s,s,s,s,s,*subjects,department)
        staff1=(department,name,self.email_input_verification.text(),'12345678')
        print(staff)
        try:
            conn = sqlite3.connect('staff.db')  # Connect to your database
            c = conn.cursor()
            c.execute("INSERT INTO staffn (initial,name,hours_per_week,MON,TUE,WED,THUR,FRI,subject1,subject2,subject3,subject4,dept) VALUES (?, ?, ?, ?, ?, ?, ?,?,?,?,?,?,?)", staff)
            conn.commit()
            c.execute("INSERT INTO authen (dept,staffname,email,password)VALUES(?,?,?,?)",staff1)
            conn.commit()
            print("INSERTED SUCCESSFULLY!")
        except sqlite3.Error as e:
            print("Error inserting into database:", e)
class CreateSubjectWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('ADD SUBJECT')
        self.resize(700, 700)
        # Remove the grey background
        # self.setStyleSheet("background-color: lightgrey;")

        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Create the form layout
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(15)

        # Adding fields
        self.subject_name = QLineEdit()
        self.sub_code = QLineEdit()
        self.sub_type = QComboBox()
        self.sub_type.addItems(['Select Type','T','TL','L'])

        self.department = QComboBox()
        self.department.addItems(['Select Department', 'BME', 'CHEM', 'CIVIL', 'CSE', 'ECE', 'EEE', 'ENG', 'MECH', 'IT', 'PHY', 'TAM'])

        self.semester = QComboBox()
        self.semester.addItems(['Select Semester', '1', '2', '3', '4', '5', '6', '7', '8'])

        self.hours = QComboBox()
        self.hours.addItems(['Select Hours', '1', '2', '3', '4', '5'])

        self.credits = QComboBox()
        self.credits.addItems(['Select Credits', '1', '2', '3', '4'])

        # Add styles to QLineEdit widgets
        line_edit_style = """
            QLineEdit {
                border: 2px solid #A9A9A9;
                border-radius: 5px;
                padding: 5px;
                background-color: #FFFFFF;
            }
            QLineEdit:focus {
                border: 2px solid #1E90FF;
            }
        """
        self.subject_name.setStyleSheet(line_edit_style)
        self.sub_code.setStyleSheet(line_edit_style)

        # Add styles to QComboBox widgets
        combo_box_style = """
            QComboBox {
                border: 2px solid #A9A9A9;
                border-radius: 5px;
                padding: 5px;
                background-color: #FFFFFF;
            }
            QComboBox:focus {
                border: 2px solid #1E90FF;
            }
            QComboBox::down-arrow {
                image: url("C:/Users/madhu/Downloads/arrow.png");  # Use a custom arrow image if desired
                width: 20px;
                height: 20px;
            }
            QComboBox::drop-down {
                border-left: 1px solid #A9A9A9;
            }
        """
        self.sub_type.setStyleSheet(combo_box_style)
        self.department.setStyleSheet(combo_box_style)
        self.semester.setStyleSheet(combo_box_style)
        self.hours.setStyleSheet(combo_box_style)
        self.credits.setStyleSheet(combo_box_style)

        # Adding widgets to the form layout
        form_layout.addRow(self.createStyledLabel('Subject Name'), self.subject_name)
        form_layout.addRow(self.createStyledLabel('Subject Code'), self.sub_code)
        form_layout.addRow(self.createStyledLabel('Subject Type'), self.sub_type)
        form_layout.addRow(self.createStyledLabel('Department'), self.department)
        form_layout.addRow(self.createStyledLabel('Semester'), self.semester)
        form_layout.addRow(self.createStyledLabel('Hours'), self.hours)
        form_layout.addRow(self.createStyledLabel('Credits'), self.credits)

        # Group box for the form
        form_group = QGroupBox("Subject Details")
        form_group.setFont(QFont('Arial', 14))
        form_group.setLayout(form_layout)

        # Adding form_group to main_layout
        main_layout.addWidget(form_group)

        # Add submit button with complex design
        self.submit_button = QPushButton('Submit')
        self.submit_button.setFont(QFont('Arial', 12))
        self.submit_button.setStyleSheet("""
            QPushButton {
                background-color: #1E90FF;
                color: white;
                border: 2px solid #1E90FF;
                border-radius: 10px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #63B8FF;
            }
            QPushButton:pressed {
                background-color: #104E8B;
            }
        """)
        self.submit_button.clicked.connect(self.createsub)
        main_layout.addWidget(self.submit_button)

    def createsub(self):
        # Check for empty fields
        if not self.subject_name.text() or \
           not self.sub_code.text() or \
           not self.sub_type.currentText()=='Select Type' or \
           self.department.currentText() == 'Select Department' or \
           self.semester.currentText() == 'Select Semester' or \
           self.hours.currentText() == 'Select Hours' or \
           self.credits.currentText() == 'Select Credits':
            QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
            return

        subject = (
            self.subject_name.text(),
            self.sub_code.text(),
            self.sub_type.currentText(),
            self.credits.currentText(),
            self.department.currentText(),
            self.semester.currentText(),
            self.hours.currentText()
        )

        self.add_sub(subject)

    def add_sub(self, subject):
        conn = sqlite3.connect('staff.db')
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM SUB WHERE subjectname = ?", (subject[0],))
        exists = cursor.fetchone()

        if exists:
            QMessageBox.warning(self, "Error", "SUBJECT ALREADY EXISTS")
        else:
            cursor.execute("INSERT INTO SUB (subjectname, subcode, subtype, credit, department, semester, hours) VALUES (?, ?, ?, ?, ?, ?, ?)", subject)
            conn.commit()
            QMessageBox.information(self, "Success", "Subject added successfully")

        conn.close()

    def createStyledLabel(self, text):
        label = QLabel(text)
        label.setFont(QFont('Arial', 12))
        return label
class GenerateTimeTable(QtWidgets.QMainWindow):
    def __init__(self):
        super(GenerateTimeTable, self).__init__()

        self.setWindowTitle('Timetable Generator')
        self.setFixedSize(500, 600)

        # Main layout
        self.mainWidget = QtWidgets.QWidget()
        self.setCentralWidget(self.mainWidget)
        self.mainLayout = QtWidgets.QVBoxLayout(self.mainWidget)

        # Title Label
        self.titleLabel = QtWidgets.QLabel('Timetable Generator')
        self.titleLabel.setFont(QtGui.QFont('Arial', 24, QtGui.QFont.Bold))
        self.titleLabel.setAlignment(Qt.AlignCenter)
        self.mainLayout.addWidget(self.titleLabel)

        # Input Frame
        self.inputFrame = QtWidgets.QFrame()
        self.inputFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.inputFrame.setStyleSheet("""
            QFrame {
                border: 1px solid #c0c0c0;
                padding: 20px;
                border-radius: 10px;
                background-color: #f8f8f8;
            }
        """)
        self.inputLayout = QtWidgets.QFormLayout(self.inputFrame)

        # Department
        self.departmentLabel = QtWidgets.QLabel('Department:')
        self.departmentInput = QtWidgets.QComboBox()
        self.departmentInput.addItems(["CSE", "ECE", "EEE", "MECH", "CIVIL"])
        self.inputLayout.addRow(self.departmentLabel, self.departmentInput)

        # Semester
        self.semesterLabel = QtWidgets.QLabel('Semester:')
        self.semesterInput = QtWidgets.QComboBox()
        self.semesterInput.addItems([str(i) for i in range(1, 11)])
        self.inputLayout.addRow(self.semesterLabel, self.semesterInput)

        # Section
        self.sectionLabel = QtWidgets.QLabel('Section:')
        self.sectionInput = QtWidgets.QLineEdit()
        self.inputLayout.addRow(self.sectionLabel, self.sectionInput)

        self.mainLayout.addWidget(self.inputFrame)

        # Generate Button
        self.generateButton = QtWidgets.QPushButton('Generate Timetable')
        self.generateButton.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                padding: 10px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.generateButton.clicked.connect(self.generate_timetable)
        self.mainLayout.addWidget(self.generateButton, alignment=Qt.AlignCenter)

        self.conn = sqlite3.connect('staff.db')
        self.cursor = self.conn.cursor()

    def staffdet(self, department, semester):
        self.cursor.execute("SELECT subjectname FROM SUB WHERE department = ? AND semester = ?;", (department, semester))
        subject = [row[0] for row in self.cursor.fetchall()]
        self.cursor.execute("SELECT subcode FROM SUB WHERE department = ? AND semester = ?;", (department, semester))
        subcode=[row[0] for row in self.cursor.fetchall()]
        staff_dict = {}
        for sub in subject:
            # Get staff names for each subject
            self.cursor.execute(
                "SELECT name FROM staffn WHERE subject1=? OR subject2=? OR subject3=? OR subject4=?", 
                (sub, sub, sub, sub,)
            )
            staff_names = [row[0] for row in self.cursor.fetchall()]
            staff_dict[sub] = staff_names
            all_staff_names = []
            for staff_list in staff_dict.values():
                all_staff_names.extend(staff_list)
            # Get initials for each staff name
        return  all_staff_names,subject, subcode
    def selectstaff(self, staff_names):
        self.cursor.execute("SELECT name, hours_per_week, MON, TUE, WED, THUR, FRI, subject1, subject2, subject3, subject4 FROM staffn")
        staff_data = self.cursor.fetchall()
        staff_dict = {}
        for n in staff_names:
            for row in staff_data:
                name, hours_per_week, mon, tue, wed, thur, fri, subject1, subject2, subject3, subject4 = row
                if n == row[0]:
                    staff_dict[name] = [name, hours_per_week, json.loads(mon), json.loads(tue), json.loads(wed), json.loads(thur), json.loads(fri), subject1, subject2, subject3, subject4]
        return staff_dict
    def selectsub(self, subjects):
        ln = {}
        r = self.cursor.execute("SELECT subjectname, subtype, hours, credit FROM SUB ")
        result = r.fetchall()
        for n in subjects:
            for row in result:
                if n == row[0]:
                    ln[n] = row
        return ln

    def lab_data(self, department):
        self.cursor.execute("SELECT SUBJECT, MON, TUE, WED, THUR, FRI FROM lab WHERE dept=?", (department,))
        rows = self.cursor.fetchall()
        lab_occupy = {}
        for row in rows:
            subject_name = row[0]
            lab_occupy[subject_name] = {
                'MON': json.loads(row[1]),
                'TUE': json.loads(row[2]),
                'WED': json.loads(row[3]),
                'THUR': json.loads(row[4]),
                'FRI': json.loads(row[5])
            }
        return lab_occupy

    def insert_table(self, time_table, section, semester, department):
        json_data = json.dumps(time_table)
        self.cursor.execute("INSERT INTO schedule_data (section, department, sem, data) VALUES (?, ?, ?, ?)", (section, department, semester, json_data,))
        self.conn.commit()

    def staff_table(self, staff):
        self.conn = sqlite3.connect('staff.db')
        self.cursor = self.conn.cursor()
        # Function to merge lists by replacing the existing class with the new class if it exists
        def merge_lists(existing_list, new_list):
            return [new if new != 0 else existing for existing, new in zip(existing_list, new_list)]

        # Retrieve all existing records
        self.cursor.execute("SELECT name, hours_per_week, MON, TUE, WED, THUR, FRI FROM staffn")
        existing_records = self.cursor.fetchall()

        # Process existing records into a dictionary for easier manipulation
        existing_records_dict = {row[0]: {
            'name': row[0],
            'hours_per_week': row[1],
            'MON': json.loads(row[2]),
            'TUE': json.loads(row[3]),
            'WED': json.loads(row[4]),
            'THUR': json.loads(row[5]),
            'FRI': json.loads(row[6])
        } for row in existing_records}

        # Process new staff data
        for key, value in staff.items():
            name = value[0]
            hours_per_week = value[1]
            mon = value[2]
            tue = value[3]
            wed = value[4]
            thur = value[5]
            fri = value[6]

            if name in existing_records_dict:
                existing_info = existing_records_dict[name]
                existing_info['MON'] = merge_lists(existing_info['MON'], mon)
                existing_info['TUE'] = merge_lists(existing_info['TUE'], tue)
                existing_info['WED'] = merge_lists(existing_info['WED'], wed)
                existing_info['THUR'] = merge_lists(existing_info['THUR'], thur)
                existing_info['FRI'] = merge_lists(existing_info['FRI'], fri)

                # Update the existing record in the database
                self.cursor.execute('''
                    UPDATE staffn
                    SET hours_per_week = ?,
                        MON = ?,
                        TUE = ?,
                        WED = ?,
                        THUR = ?,
                        FRI = ?
                    WHERE name = ?
                ''', (hours_per_week, json.dumps(existing_info['MON']), json.dumps(existing_info['TUE']), json.dumps(existing_info['WED']), json.dumps(existing_info['THUR']), json.dumps(existing_info['FRI']), name))
            else:
                # Insert new record if it does not exist (this part can be modified based on your logic)
                self.cursor.execute('''
                    INSERT INTO staffn (name, hours_per_week, MON, TUE, WED, THUR, FRI)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (name, hours_per_week, json.dumps(mon), json.dumps(tue), json.dumps(wed), json.dumps(thur), json.dumps(fri)))

        # Commit the transaction
        self.conn.commit()



    def assign_labs(self, lab, labs, days, time_table, subjects, labs_assigned, labs_assigned_per_day, department, section):
        rand_slot=0
        for subject, values in subjects.items():
            if 'L' in values[1]:
                while True:
                    lab_rand = random.randint(0, len(labs) - 1)
                    rand_day = random.randint(0, 4)

                    lab_name = labs[lab_rand]
                    day_name = days[rand_day]

                    if self.check_lab_slot(lab, lab_name, day_name, rand_slot) and labs_assigned_per_day[rand_day] == 0:
                        temp = department + ' ' + section
                        lab[lab_name][day_name][rand_slot] = [subject, temp]
                        labs_assigned.append((subject, lab_name))

                        start_slot = 1 if rand_slot == 0 else 4
                        end_slot = start_slot + 3

                        for i in range(start_slot, end_slot):
                            time_table[day_name][i] = [subject, 'lab']
                            rand_slot=(rand_slot+1)%2

                        labs_assigned_per_day[rand_day] = 1
                        break
        return lab

    def assign_special_activities(self, time_table, days):
        j = 0
        activities = ['PT', 'I Cell', 'Library', 'Mentor']
        for day in days:
            for period in range(len(time_table[day])):
                if time_table[day][period] == 0:
                    time_table[day][period] = activities[j]
                    j = (j + 1) % len(activities)
        return time_table

    def select_staff_for_subjects(self, subjects, staff):
        staffs = []
        for subject in subjects.keys():
            lst = []
            for staff_name, staff_info in staff.items():
                if subject in staff_info[7] or subject in staff_info[8] or subject in staff_info[9] or subject in staff_info[10]:
                    lst.append(staff_name)
            while True:
                dialog = QtWidgets.QInputDialog(self)
                dialog.setWindowTitle(f"Select Staff for {subject}")
                dialog.setLabelText(f"Available Staff for {subject}:")
                dialog.setComboBoxItems(lst)
                dialog.resize(400, 200)  # Increase the size of the dialog
                if dialog.exec() == QtWidgets.QDialog.Accepted:
                    select = dialog.textValue()
                    if select in lst and select not in [s[0] for s in staffs]:
                        staffs.append([select, subject, subjects[subject][2]])
                        staff[select][1] -= subjects[subject][2]
                        break
                else:
                    break
        return staffs

    def fill_timetable(self, time_table, staffs, staff, days, department, section):
        for staff_info in staffs:
            staff_name = staff_info[0]
            subject = staff_info[1]
            hours = staff_info[2]
            code=staff_info[3]
            initial=staff_info[4]

            # Calculate morning and afternoon hours
            morning_hours = hours * 2 // 3
            afternoon_hours = hours - morning_hours
            print(f"Assigning {subject} to {staff_name} - Morning Hours: {morning_hours}, Afternoon Hours: {afternoon_hours}")

            # Assign morning periods
            for _ in range(morning_hours):
                attempts = 0
                while attempts < 100:
                    rand_day_index = random.randint(0, 4)
                    rand_day = days[rand_day_index]
                    print(f"Trying to assign morning period for {subject} on {rand_day}")

                    if 0 in time_table[rand_day][:4]:
                        rand_period = time_table[rand_day][:4].index(0)
                        print(f"Assigned {subject} to {staff_name} on {rand_day} at period {rand_period}")
                        time_table[rand_day][rand_period] = [code, initial]
                        staff[staff_name][rand_day_index + 2][rand_period] = f"{department}-{section}"
                        staff_info[2] -= 1
                        break
                    attempts += 1

                if attempts == 100:
                    print(f"Failed to assign morning period for {subject} after 50 attempts")
                    return staff, time_table

            # Assign afternoon periods
            for _ in range(afternoon_hours):
                attempts = 0
                while attempts < 100:
                    rand_day_index = random.randint(0, 4)
                    rand_day = days[rand_day_index]
                    print(f"Trying to assign afternoon period for {subject} on {rand_day}")

                    if 0 in time_table[rand_day][4:]:
                        rand_period = time_table[rand_day][4:].index(0)
                        print(f"Assigned {subject} to {staff_name} on {rand_day} at period {rand_period + 4}")
                        time_table[rand_day][rand_period + 4] = [code, initial]
                        staff[staff_name][rand_day_index + 2][rand_period + 4] = f"{department}-{section}"
                        staff_info[2] -= 1
                        break
                    attempts += 1

                if attempts == 100:
                    print(f"Failed to assign afternoon period for {subject} after 50 attempts")
                    print(time_table)
                    return staff, time_table
        return staff,time_table

    
    def check_lab_slot(self, lab, lab_name, day_name, slot):
        return lab[lab_name][day_name][slot] == 0
    
    def insert_lab_table(self, lab):
        for key, value in lab.items():
            self.cursor.execute('INSERT OR REPLACE INTO labs_table (name, lab_value) VALUES (?, ?)', (key, json.dumps(value)))
            self.conn.commit()

    def generate_timetable(self):
        department = self.departmentInput.currentText()
        semester = int(self.semesterInput.currentText())
        section = self.sectionInput.text()

        try:
            staff_names, subject,subcode = self.staffdet(department, semester)
            staff = self.selectstaff(staff_names)
            subjects = self.selectsub(subject)
            staffs = self.select_staff_for_subjects(subjects, staff)

            print(staffs)
            print(staff)
            print(subcode)
            s=[]
            for x in staffs:
                s.append(x[0])
            print(s)
            initial = []

            for staff_name in s:
                self.cursor.execute(
                    "SELECT initial FROM staffn WHERE name=?", 
                    (staff_name,)
                )
                rows = self.cursor.fetchall()
                for row in rows:
                    initial.append(row[0])
            print(staff,staffs,initial)
            for i in range(len(staffs)):
                staffs[i].extend([subcode[i],initial[i]])
            print(staffs)
            #staffs=[['akisher', 'cp', 3], ['vishnu', 'unix', 3], ['kamesh', 'dsd', 3], ['ram', 'maths', 5], ['pravin', 'tamil', 1], ['paul', 'english', 3]]

            while True:
                lab = self.lab_data(department)
                labs = list(lab.keys())
                days = ['MON', 'TUE', 'WED', 'THUR', 'FRI']
                
                time_table = {
                    'MON': [0, 0, 0, 0, 0, 0, 0],
                    'TUE': [0, 0, 0, 0, 0, 0, 0],
                    'WED': [0, 0, 0, 0, 0, 0, 0],
                    'THUR': [0, 0, 0, 0, 0, 0, 0],
                    'FRI': [0, 0, 0, 0, 0, 0, 0],
                }
                # Clear staff timetable values
                for key in staff:
                    staff[key][2:] = [[0]*7 for _ in range(5)]

                lab = self.assign_labs(lab, labs, days, time_table, subjects, [], [0, 0, 0, 0, 0], department, section)
                staff, time_table = self.fill_timetable(time_table, staffs, staff, days, department, section)
                time_table = self.assign_special_activities(time_table, days)
                print(time_table)
                sub_list=[sub[1] for sub in staffs]
                print(time_table.values())
                print(sub_list)
                if self.check_timetable_conditions(time_table, staff,sub_list):
                    print(staff.values())
                    print(time_table)
                    self.insert_table(time_table, section, semester, department)
                    self.insert_lab_table(lab)
                    self.staff_table(staff)
                    QtWidgets.QMessageBox.information(self, "Timetable Generated", "The timetable has been generated and saved successfully.")
                    break
                else:
                    # Clear timetable values to 0
                    time_table = {day: [0, 0, 0, 0, 0, 0, 0] for day in days}
                    # Clear staff timetable values again in case they were modified
                    for key in staff:
                        staff[key][2:] = [[0]*7 for _ in range(5)]
        except Exception as e:
            print(f"An error occurred: {e}")

    def check_timetable_conditions(self, time_table, staff,sub_list):
        return self.check_consecutive(time_table) and self.check_more_than_three_classes(staff)

    def check_ratio(self, time_table,sub_list):
        for i in sub_list:
            mrng=0
            after=0
            for k in time_table.values():
                for j in range(0,7):
                    if k[j][0]==i:
                        if j in [1,2,3,4]:
                            mrng+=1
                        else:
                            after+=1
            if mrng==1 and after==0 or mrng==0 and after==1:
                continue
            elif mrng>1 and after==0 or mrng==0 and after>1:
                return False
            elif mrng/after==1 or after/mrng==1 or mrng/after==1.5 or after/mrng==1.5:
                continue
            else: 
                return False
        return True

    def check_consecutive(self, time_table):
        for day in time_table:
            for period in range(5):
                if time_table[day][period] != 0 and time_table[day][period + 1] != 0 and ((time_table[day][period][1] =='lab' and  time_table[day][period + 1][1]=='lab') or ((time_table[day][period][1] =='No Staff' and  time_table[day][period + 1][1]=='No Staff'))):
                    continue
                if time_table[day][period] != 0 and time_table[day][period + 1] != 0 and time_table[day][period][1] == time_table[day][period + 1][1]:
                    if time_table[day][period + 2] != 0 and time_table[day][period][1] == time_table[day][period + 2][1]:
                        return False
        return True

    def check_more_than_three_classes(self, staff):
        for staff_info in staff.values():
            for day in staff_info[2:7]:
                count = sum(1 for period in day if period != 0)
                if count > 3:
                    return False
        return True    
class UserLoginWindow(QWidget):
    login_successful = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle('USER LOGIN PAGE')
        self.background_image = QPixmap("C:/Users/KAVI/Downloads/userlogin.jpg")
        self.resize(500,600)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(20)

        # Add person icon at the top center
        icon_label = QLabel()
        icon_label.setPixmap(QPixmap("C:/Users/KAVI/Downloads/person.webp").scaled(100, 100, Qt.KeepAspectRatio))
        icon_layout = QHBoxLayout()
        icon_layout.addStretch()
        icon_layout.addWidget(icon_label)
        icon_layout.addStretch()
        layout.addLayout(icon_layout)

        welcome_label = QLabel("USER LOGIN")  
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("font-weight: bold; color: white; font-size: 32px;")
        layout.addWidget(welcome_label)

        self.username_label = QLabel('USERNAME:')
        self.username_label.setStyleSheet("font-weight: bold; color: white;")
        self.username_label.setFont(QFont("Times New Roman", 16, QFont.Bold))
        layout.addWidget(self.username_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('ENTER USERNAME HERE')
        self.username_input.setStyleSheet("QLineEdit { font-size: 16px; padding: 8px; border: 2px solid gray; border-radius: 8px; background-color: white; }")
        layout.addWidget(self.username_input)

        password_layout = QHBoxLayout()
        self.password_label = QLabel('PASSWORD:')
        self.password_label.setStyleSheet("font-weight: bold; color: white;")
        self.password_label.setFont(QFont("Times New Roman", 14, QFont.Bold))
        layout.addWidget(self.password_label)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('ENTER PASSWORD HERE')
        self.password_input.setStyleSheet("QLineEdit { font-size: 16px; padding: 8px; border: 2px solid gray; border-radius: 8px; background-color: white; }")
        self.password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(self.password_input)

        self.toggle_password_button = QPushButton()
        self.toggle_password_button.setIcon(QIcon("C:/Users/KAVI/Downloads/hide.jpg"))  # Replace with your hide icon path
        self.toggle_password_button.setIconSize(QSize(24, 24))
        self.toggle_password_button.setCheckable(True)
        self.toggle_password_button.clicked.connect(self.toggle_password_visibility)
        password_layout.addWidget(self.toggle_password_button)
        
        layout.addLayout(password_layout)

        self.login_button = QPushButton('LOGIN')
        self.login_button.setStyleSheet("QPushButton { background-color: rgba(0,0,50,1.0); color: white; font-weight: bold; font-size: 16px; padding: 8px; border-radius: 16px; } QPushButton:hover { background-color: #2ca02c; } QPushButton:pressed { background-color: #116611; }")
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)

        self.forgot_password_button = QPushButton('FORGOT PASSWORD')
        self.forgot_password_button.setStyleSheet("QPushButton { background-color: rgba(69, 0, 84, 1.0); color: white; font-weight: bold; font-size: 16px; padding: 8px; border-radius: 16px; } QPushButton:hover { background-color: #e60000; } QPushButton:pressed { background-color: #a80000; }")
        self.forgot_password_button.clicked.connect(self.forgot_password)
        layout.addWidget(self.forgot_password_button)

        self.setLayout(layout)

    def toggle_password_visibility(self):
        if self.password_input.echoMode() == QLineEdit.Password:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.toggle_password_button.setIcon(QIcon("C:/Users/KAVI/Downloads/showicon.jpeg"))  # Replace with your show icon path
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.toggle_password_button.setIcon(QIcon("C:/Users/KAVI/Downloads/hide.jpg"))
    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.rect()
        if not self.background_image.isNull():
            scaled_image = self.background_image.scaled(rect.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            painter.drawPixmap(rect.center() - scaled_image.rect().center(), scaled_image)
        super().paintEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjust_widgets()

    def adjust_widgets(self):
        widget_height = 40
        self.username_input.setFixedHeight(widget_height)
        self.password_input.setFixedHeight(widget_height)
        self.login_button.setFixedHeight(widget_height)
        self.forgot_password_button.setFixedHeight(widget_height)

    def forgot_password(self):
        self.forgot_password_window = ForgotPasswordMainWindow()
        self.forgot_password_window.show()

    def login(self):
        self.username = self.username_input.text()
        self.password = self.password_input.text()
        global user
        user=self.username

        cursor.execute("SELECT * FROM authen WHERE staffname = ? AND password = ?", (self.username, self.password))
        result = cursor.fetchone()
        if result:
            global user_dept
            user_dept = result[0]
            QMessageBox.information(self, 'Login Successful', 'You have logged in successfully.')
            self.login_successful.emit(self.username)
        else:
            QMessageBox.warning(self, 'Login Failed', 'Invalid username or password.')

class UserViewTimetable(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('USER VIEW TIMETABLE PAGE')
        self.resize(500,600)
        self.showMaximized()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(20)

        # Department Label
        self.department_label = QLabel(f'DEPARTMENT: {user_dept}')
        self.department_label.setStyleSheet("""
            font-weight: bold;
            color: white;
            font-size: 16px;
            background-color: #2E8B57;
            padding: 10px;
            border: 2px solid #4CAF50;
            border-radius: 5px;
        """)
        layout.addWidget(self.department_label)

        # Staff Name Label
        self.staff_label = QLabel(f'STAFF NAME: {user}')
        self.staff_label.setStyleSheet("""
            font-weight: bold;
            color: white;
            font-size: 16px;
            background-color: #2E8B57;
            padding: 10px;
            border: 2px solid #4CAF50;
            border-radius: 5px;
        """)
        layout.addWidget(self.staff_label)

        # Generate Timetable Button
        self.generate_button = QPushButton('Generate Timetable')
        self.generate_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                padding: 10px 20px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3e8e41;
            }
        """)
        self.generate_button.clicked.connect(self.generate_timetable)
        layout.addWidget(self.generate_button)
        
        # Timetable Display
        self.timetable_label = QLabel('TIMETABLE:')
        self.timetable_label.setStyleSheet("""
            font-weight: bold;
            color: white;
            font-size: 16px;
            background-color: #2E8B57;
            padding: 10px;
            border: 2px solid #4CAF50;
            border-radius: 5px;
        """)
        layout.addWidget(self.timetable_label)

        # Timetable Widget
        self.timetable_widget = TimetableWidget()
        layout.addWidget(self.timetable_widget)

        # Save as PDF Button
        self.save_pdf_button = QPushButton('Save Timetable as PDF')
        self.save_pdf_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                padding: 10px 20px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3e8e41;
            }
        """)
        self.save_pdf_button.clicked.connect(self.save_timetable_as_pdf)
        layout.addWidget(self.save_pdf_button)

        # Automatically generate timetable on initialization
        self.generate_timetable()

    
    def generate_timetable(self):
        conn = sqlite3.connect('staff.db')
        cursor = conn.cursor()

        # Staff name input
        staff_name = user
        name = staff_name.strip()  # Remove any leading/trailing whitespace
        #print(f"Searching for records with name: '{name}'")

        # Check if the table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='staffn'")
        table_exists = cursor.fetchone()
        conn.commit()
        if not table_exists:
            print("Table 'staffn' does not exist.")
        else:
            # Fetch records
            cursor.execute('SELECT * FROM staffn')
            rows = cursor.fetchall()
            print(f"Fetched {len(rows)} rows from the 'staffn' table.")
            
            found = False
            for row in rows:
                print(f"Checking row: {row}")
                if len(row) > 2:  # Ensure the row has enough columns
                    db_name = row[2].strip().lower()  # Case-insensitive and trimmed comparison
                    if db_name == name.lower():
                        #print(f"Found matching row: {row}")
                        found = True
                        break  # If we only need the first matching record, we can break here

            if not found:
                print(f"No matching records found for name: '{name}'")
            new_row=[]
            new_row.extend(row[4:9])
            print(new_row)
            converted_rows = [ast.literal_eval(row) for row in new_row]
            print(converted_rows)
            self.timetable_widget.populate_timetable(converted_rows)

        # Close the connection
        conn.close()

    def save_timetable_as_pdf(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Timetable as PDF", "", "PDF Files (.pdf);;All Files ()")
        if file_path:
            self.timetable_widget.save_table_as_pdf(file_path)

class UserMainWindow(QWidget):
    def __init__(self, username):
        super().__init__()
        self.setWindowTitle('USER PAGE')
        self.resize(500,600)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(20)

        button_width=300
        button_height=80

        self.view_button = QPushButton('VIEW YOUR TIMETABLE')
        self.view_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: black;
                font-weight: bold;
                border-radius: 10px ;
                width: %dpx;
                height: %dpx;
            }
            QPushButton:hover {
                background-color: red;
            }
            QPushButton:pressed {
                background-color: #006186;
            }
        """ % (button_width, button_height))
        self.view_button.setFont(QFont("Times New Roman", 16, QFont.Bold))
        self.view_button.clicked.connect(self.view)
        layout.addWidget(self.view_button)

        self.request_modify_button = QPushButton('REQUEST MODIFY')
        self.request_modify_button.setStyleSheet("""
            QPushButton {
                background-color: black;
                color: white;
                font-weight: bold;
                border-radius: 10px ;
                width: %dpx;
                height: %dpx;
            }
            QPushButton:hover {
                background-color: lightblue;
            }
            QPushButton:pressed {
                background-color: #006186;
            }
        """ % (button_width, button_height))
        self.request_modify_button.setFont(QFont("Times New Roman", 16, QFont.Bold))
        self.request_modify_button.clicked.connect(self.request_modify)
        layout.addWidget(self.request_modify_button)


        self.background_image = QPixmap("C:/Users/KAVI/OneDrive/Documents/adminmain.jpg")
    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.rect()
        if not self.background_image.isNull():
            scaled_image = self.background_image.scaled(rect.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            painter.drawPixmap(rect.center() - scaled_image.rect().center(), scaled_image)

    def view(self):
        self.view_user=UserViewTimetable()
        self.view_user.show()

    def request_modify(self):
        self.req = UserRequestModify(user)
        self.req.show()

class UserRequestModify(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.setWindowTitle('FEEDBACK PAGE')
        self.setFixedSize(500, 600)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setSpacing(20)

        # Spacer to push everything to the center vertically
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Label on top of the QTextEdit
        self.req_label = QLabel('CONFESS YOUR GRIEVANCES:')
        self.req_label.setFont(QFont('Times New Roman',10, QFont.Bold))
        self.req_label.setStyleSheet("font-weight: bold;color: white;")
        self.req_label.setAlignment(Qt.AlignLeft)
        main_layout.addWidget(self.req_label, 0, Qt.AlignLeft)

        # QTextEdit for multiline feedback
        self.req_input = QTextEdit()
        self.req_input.setFixedSize(400, 200)
        self.req_input.setStyleSheet("""
            QTextEdit {
                border: 2px solid #ccc;
                border-radius: 10px;
                padding: 10px;
                font-size: 16px;
            }
            QTextEdit:focus {
                border: 2px solid #008CBA;
                background-color: #f0f8ff;
            }
            QTextEdit:hover {
                border: 2px solid #008CBA;
            }
        """)
        main_layout.addWidget(self.req_input, 0, Qt.AlignCenter)

        # Submit button
        self.submit_button = QPushButton('SUBMIT FEEDBACK')
        self.submit_button.setFixedSize(200, 50)
        self.submit_button.setStyleSheet("""
            QPushButton {
                background-color: #008CBA;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #005f7a;
            }
            QPushButton:pressed {
                background-color: #003f4f;
            }
        """)
        self.submit_button.setFont(QFont('Times New Roman', 10, QFont.Bold))
        self.submit_button.clicked.connect(self.submit_feedback)
        main_layout.addWidget(self.submit_button, 0, Qt.AlignCenter)

        # Spacer to push everything to the center vertically
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.adjustSize()

        self.background_image = QPixmap("C:/Users/KAVI/Downloads/req.jpg")
    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.rect()
        if not self.background_image.isNull():
            scaled_image = self.background_image.scaled(rect.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            painter.drawPixmap(rect.center() - scaled_image.rect().center(), scaled_image)

    def submit_feedback(self):
        grievances = self.req_input.toPlainText()
        if grievances == '':
            QMessageBox.information(self, 'FEEDBACK PAGE', 'FIELD EMPTY!')
        else:
            conn1 = sqlite3.connect('feedback.db')
            cursor1 = conn1.cursor()
            sql = '''INSERT INTO Feedback (staffname, feedback) VALUES (?, ?)'''
            cursor1.execute(sql, (user+' - '+user_dept, grievances))
            print("Response Recorded!")
            conn1.commit()
            conn1.close()

class GenerateTimeTable(QtWidgets.QMainWindow):
    def __init__(self):
        super(GenerateTimeTable, self).__init__()

        self.setWindowTitle('Timetable Generator')
        self.setFixedSize(500, 600)

        # Main layout
        self.mainWidget = QtWidgets.QWidget()
        self.setCentralWidget(self.mainWidget)
        self.mainLayout = QtWidgets.QVBoxLayout(self.mainWidget)

        # Title Label
        self.titleLabel = QtWidgets.QLabel('Timetable Generator')
        self.titleLabel.setFont(QtGui.QFont('Arial', 24, QtGui.QFont.Bold))
        self.titleLabel.setAlignment(Qt.AlignCenter)
        self.mainLayout.addWidget(self.titleLabel)

        # Input Frame
        self.inputFrame = QtWidgets.QFrame()
        self.inputFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.inputFrame.setStyleSheet("""
            QFrame {
                border: 1px solid #c0c0c0;
                padding: 20px;
                border-radius: 10px;
                background-color: #f8f8f8;
            }
        """)
        self.inputLayout = QtWidgets.QFormLayout(self.inputFrame)

        # Department
        self.departmentLabel = QtWidgets.QLabel('Department:')
        self.departmentInput = QtWidgets.QComboBox()
        self.departmentInput.addItems(["CSE", "ECE", "EEE", "MECH", "CIVIL"])
        self.inputLayout.addRow(self.departmentLabel, self.departmentInput)

        # Semester
        self.semesterLabel = QtWidgets.QLabel('Semester:')
        self.semesterInput = QtWidgets.QComboBox()
        self.semesterInput.addItems([str(i) for i in range(1, 11)])
        self.inputLayout.addRow(self.semesterLabel, self.semesterInput)

        # Section
        self.sectionLabel = QtWidgets.QLabel('Section:')
        self.sectionInput = QtWidgets.QLineEdit()
        self.inputLayout.addRow(self.sectionLabel, self.sectionInput)

        self.mainLayout.addWidget(self.inputFrame)

        # Generate Button
        self.generateButton = QtWidgets.QPushButton('Generate Timetable')
        self.generateButton.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                padding: 10px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.generateButton.clicked.connect(self.generate_timetable)
        self.mainLayout.addWidget(self.generateButton, alignment=Qt.AlignCenter)

        self.conn = sqlite3.connect('staff.db')
        self.cursor = self.conn.cursor()

    def staffdet(self, department, semester):
        self.cursor.execute("SELECT subjectname FROM SUB WHERE department = ? AND semester = ?;", (department, semester))
        subject = [row[0] for row in self.cursor.fetchall()]
        self.cursor.execute("SELECT subcode FROM SUB WHERE department = ? AND semester = ?;", (department, semester))
        subcode=[row[0] for row in self.cursor.fetchall()]
        staff_dict = {}
        for sub in subject:
            # Get staff names for each subject
            self.cursor.execute(
                "SELECT name FROM staffn WHERE subject1=? OR subject2=? OR subject3=? OR subject4=?", 
                (sub, sub, sub, sub,)
            )
            staff_names = [row[0] for row in self.cursor.fetchall()]
            staff_dict[sub] = staff_names
            all_staff_names = []
            for staff_list in staff_dict.values():
                all_staff_names.extend(staff_list)
            # Get initials for each staff name
        return  all_staff_names,subject, subcode
    def selectstaff(self, staff_names):
        self.cursor.execute("SELECT name, hours_per_week, MON, TUE, WED, THUR, FRI, subject1, subject2, subject3, subject4 FROM staffn")
        staff_data = self.cursor.fetchall()
        staff_dict = {}
        for n in staff_names:
            for row in staff_data:
                name, hours_per_week, mon, tue, wed, thur, fri, subject1, subject2, subject3, subject4 = row
                if n == row[0]:
                    staff_dict[name] = [name, hours_per_week, json.loads(mon), json.loads(tue), json.loads(wed), json.loads(thur), json.loads(fri), subject1, subject2, subject3, subject4]
        return staff_dict
    def selectsub(self, subjects):
        ln = {}
        r = self.cursor.execute("SELECT subjectname, subtype, hours, credit FROM SUB ")
        result = r.fetchall()
        for n in subjects:
            for row in result:
                if n == row[0]:
                    ln[n] = row
        return ln

    def lab_data(self, department):
        self.cursor.execute("SELECT SUBJECT, MON, TUE, WED, THUR, FRI FROM lab WHERE dept=?", (department,))
        rows = self.cursor.fetchall()
        lab_occupy = {}
        for row in rows:
            subject_name = row[0]
            lab_occupy[subject_name] = {
                'MON': json.loads(row[1]),
                'TUE': json.loads(row[2]),
                'WED': json.loads(row[3]),
                'THUR': json.loads(row[4]),
                'FRI': json.loads(row[5])
            }
        return lab_occupy

    def insert_table(self, time_table, section, semester, department):
        json_data = json.dumps(time_table)
        self.cursor.execute("INSERT INTO schedule_data (section, department, sem, data) VALUES (?, ?, ?, ?)", (section, department, semester, json_data,))
        self.conn.commit()

    def staff_table(self, staff):
        self.conn = sqlite3.connect('staff.db')
        self.cursor = self.conn.cursor()
        # Function to merge lists by replacing the existing class with the new class if it exists
        def merge_lists(existing_list, new_list):
            return [new if new != 0 else existing for existing, new in zip(existing_list, new_list)]

        # Retrieve all existing records
        self.cursor.execute("SELECT name, hours_per_week, MON, TUE, WED, THUR, FRI FROM staffn")
        existing_records = self.cursor.fetchall()

        # Process existing records into a dictionary for easier manipulation
        existing_records_dict = {row[0]: {
            'name': row[0],
            'hours_per_week': row[1],
            'MON': json.loads(row[2]),
            'TUE': json.loads(row[3]),
            'WED': json.loads(row[4]),
            'THUR': json.loads(row[5]),
            'FRI': json.loads(row[6])
        } for row in existing_records}

        # Process new staff data
        for key, value in staff.items():
            name = value[0]
            hours_per_week = value[1]
            mon = value[2]
            tue = value[3]
            wed = value[4]
            thur = value[5]
            fri = value[6]

            if name in existing_records_dict:
                existing_info = existing_records_dict[name]
                existing_info['MON'] = merge_lists(existing_info['MON'], mon)
                existing_info['TUE'] = merge_lists(existing_info['TUE'], tue)
                existing_info['WED'] = merge_lists(existing_info['WED'], wed)
                existing_info['THUR'] = merge_lists(existing_info['THUR'], thur)
                existing_info['FRI'] = merge_lists(existing_info['FRI'], fri)

                # Update the existing record in the database
                self.cursor.execute('''
                    UPDATE staffn
                    SET hours_per_week = ?,
                        MON = ?,
                        TUE = ?,
                        WED = ?,
                        THUR = ?,
                        FRI = ?
                    WHERE name = ?
                ''', (hours_per_week, json.dumps(existing_info['MON']), json.dumps(existing_info['TUE']), json.dumps(existing_info['WED']), json.dumps(existing_info['THUR']), json.dumps(existing_info['FRI']), name))
            else:
                # Insert new record if it does not exist (this part can be modified based on your logic)
                self.cursor.execute('''
                    INSERT INTO staffn (name, hours_per_week, MON, TUE, WED, THUR, FRI)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (name, hours_per_week, json.dumps(mon), json.dumps(tue), json.dumps(wed), json.dumps(thur), json.dumps(fri)))

        # Commit the transaction
        self.conn.commit()



    def assign_labs(self, lab, labs, days, time_table, subjects, labs_assigned, labs_assigned_per_day, department, section):
        rand_slot=0
        for subject, values in subjects.items():
            if 'L' in values[1]:
                while True:
                    lab_rand = random.randint(0, len(labs) - 1)
                    rand_day = random.randint(0, 4)

                    lab_name = labs[lab_rand]
                    day_name = days[rand_day]

                    if self.check_lab_slot(lab, lab_name, day_name, rand_slot) and labs_assigned_per_day[rand_day] == 0:
                        temp = department + ' ' + section
                        lab[lab_name][day_name][rand_slot] = [subject, temp]
                        labs_assigned.append((subject, lab_name))

                        start_slot = 1 if rand_slot == 0 else 4
                        end_slot = start_slot + 3

                        for i in range(start_slot, end_slot):
                            time_table[day_name][i] = [subject, 'lab']
                            rand_slot=(rand_slot+1)%2

                        labs_assigned_per_day[rand_day] = 1
                        break
        return lab

    def assign_special_activities(self, time_table, days):
        j = 0
        activities = ['PT', 'I Cell', 'Library', 'Mentor']
        for day in days:
            for period in range(len(time_table[day])):
                if time_table[day][period] == 0:
                    time_table[day][period] = activities[j]
                    j = (j + 1) % len(activities)
        return time_table

    def select_staff_for_subjects(self, subjects, staff):
        staffs = []
        for subject in subjects.keys():
            lst = []
            for staff_name, staff_info in staff.items():
                if subject in staff_info[7] or subject in staff_info[8] or subject in staff_info[9] or subject in staff_info[10]:
                    lst.append(staff_name)
            while True:
                dialog = QtWidgets.QInputDialog(self)
                dialog.setWindowTitle(f"Select Staff for {subject}")
                dialog.setLabelText(f"Available Staff for {subject}:")
                dialog.setComboBoxItems(lst)
                dialog.resize(400, 200)  # Increase the size of the dialog
                if dialog.exec() == QtWidgets.QDialog.Accepted:
                    select = dialog.textValue()
                    if select in lst and select not in [s[0] for s in staffs]:
                        staffs.append([select, subject, subjects[subject][2]])
                        staff[select][1] -= subjects[subject][2]
                        break
                else:
                    break
        return staffs

    def fill_timetable(self, time_table, staffs, staff, days, department, section):
        for staff_info in staffs:
            staff_name = staff_info[0]
            subject = staff_info[1]
            hours = staff_info[2]
            code=staff_info[3]
            initial=staff_info[4]

            # Calculate morning and afternoon hours
            morning_hours = hours * 2 // 3
            afternoon_hours = hours - morning_hours
            print(f"Assigning {subject} to {staff_name} - Morning Hours: {morning_hours}, Afternoon Hours: {afternoon_hours}")

            # Assign morning periods
            for _ in range(morning_hours):
                attempts = 0
                while attempts < 100:
                    rand_day_index = random.randint(0, 4)
                    rand_day = days[rand_day_index]
                    print(f"Trying to assign morning period for {subject} on {rand_day}")

                    if 0 in time_table[rand_day][:4]:
                        rand_period = time_table[rand_day][:4].index(0)
                        print(f"Assigned {subject} to {staff_name} on {rand_day} at period {rand_period}")
                        time_table[rand_day][rand_period] = [code, initial]
                        staff[staff_name][rand_day_index + 2][rand_period] = f"{department}-{section}"
                        staff_info[2] -= 1
                        break
                    attempts += 1

                if attempts == 100:
                    print(f"Failed to assign morning period for {subject} after 50 attempts")
                    return staff, time_table

            # Assign afternoon periods
            for _ in range(afternoon_hours):
                attempts = 0
                while attempts < 100:
                    rand_day_index = random.randint(0, 4)
                    rand_day = days[rand_day_index]
                    print(f"Trying to assign afternoon period for {subject} on {rand_day}")

                    if 0 in time_table[rand_day][4:]:
                        rand_period = time_table[rand_day][4:].index(0)
                        print(f"Assigned {subject} to {staff_name} on {rand_day} at period {rand_period + 4}")
                        time_table[rand_day][rand_period + 4] = [code, initial]
                        staff[staff_name][rand_day_index + 2][rand_period + 4] = f"{department}-{section}"
                        staff_info[2] -= 1
                        break
                    attempts += 1

                if attempts == 100:
                    print(f"Failed to assign afternoon period for {subject} after 50 attempts")
                    print(time_table)
                    return staff, time_table
        return staff,time_table

    
    def check_lab_slot(self, lab, lab_name, day_name, slot):
        return lab[lab_name][day_name][slot] == 0
    
    def insert_lab_table(self, lab):
        for key, value in lab.items():
            self.cursor.execute('INSERT OR REPLACE INTO labs_table (name, lab_value) VALUES (?, ?)', (key, json.dumps(value)))
            self.conn.commit()

    def generate_timetable(self):
        department = self.departmentInput.currentText()
        semester = int(self.semesterInput.currentText())
        section = self.sectionInput.text()

        try:
            staff_names, subject,subcode = self.staffdet(department, semester)
            staff = self.selectstaff(staff_names)
            subjects = self.selectsub(subject)
            staffs = self.select_staff_for_subjects(subjects, staff)

            print(staffs)
            print(staff)
            print(subcode)
            s=[]
            for x in staffs:
                s.append(x[0])
            print(s)
            initial = []

            for staff_name in s:
                self.cursor.execute(
                    "SELECT initial FROM staffn WHERE name=?", 
                    (staff_name,)
                )
                rows = self.cursor.fetchall()
                for row in rows:
                    initial.append(row[0])
            print(staff,staffs,initial)
            for i in range(len(staffs)):
                staffs[i].extend([subcode[i],initial[i]])
            print(staffs)
            #staffs=[['akisher', 'cp', 3], ['vishnu', 'unix', 3], ['kamesh', 'dsd', 3], ['ram', 'maths', 5], ['pravin', 'tamil', 1], ['paul', 'english', 3]]

            while True:
                lab = self.lab_data(department)
                labs = list(lab.keys())
                days = ['MON', 'TUE', 'WED', 'THUR', 'FRI']
                
                time_table = {
                    'MON': [0, 0, 0, 0, 0, 0, 0],
                    'TUE': [0, 0, 0, 0, 0, 0, 0],
                    'WED': [0, 0, 0, 0, 0, 0, 0],
                    'THUR': [0, 0, 0, 0, 0, 0, 0],
                    'FRI': [0, 0, 0, 0, 0, 0, 0],
                }
                # Clear staff timetable values
                for key in staff:
                    staff[key][2:] = [[0]*7 for _ in range(5)]

                lab = self.assign_labs(lab, labs, days, time_table, subjects, [], [0, 0, 0, 0, 0], department, section)
                staff, time_table = self.fill_timetable(time_table, staffs, staff, days, department, section)
                time_table = self.assign_special_activities(time_table, days)
                print(time_table)
                sub_list=[sub[1] for sub in staffs]
                print(time_table.values())
                print(sub_list)
                if self.check_timetable_conditions(time_table, staff,sub_list):
                    print(staff.values())
                    print(time_table)
                    self.insert_table(time_table, section, semester, department)
                    self.insert_lab_table(lab)
                    self.staff_table(staff)
                    QtWidgets.QMessageBox.information(self, "Timetable Generated", "The timetable has been generated and saved successfully.")
                    break
                else:
                    # Clear timetable values to 0
                    time_table = {day: [0, 0, 0, 0, 0, 0, 0] for day in days}
                    # Clear staff timetable values again in case they were modified
                    for key in staff:
                        staff[key][2:] = [[0]*7 for _ in range(5)]
        except Exception as e:
            print(f"An error occurred: {e}")

    def check_timetable_conditions(self, time_table, staff,sub_list):
        return self.check_consecutive(time_table) and self.check_more_than_three_classes(staff)

    def check_ratio(self, time_table,sub_list):
        for i in sub_list:
            mrng=0
            after=0
            for k in time_table.values():
                for j in range(0,7):
                    if k[j][0]==i:
                        if j in [1,2,3,4]:
                            mrng+=1
                        else:
                            after+=1
            if mrng==1 and after==0 or mrng==0 and after==1:
                continue
            elif mrng>1 and after==0 or mrng==0 and after>1:
                return False
            elif mrng/after==1 or after/mrng==1 or mrng/after==1.5 or after/mrng==1.5:
                continue
            else: 
                return False
        return True

    def check_consecutive(self, time_table):
        for day in time_table:
            for period in range(5):
                if time_table[day][period] != 0 and time_table[day][period + 1] != 0 and ((time_table[day][period][1] =='lab' and  time_table[day][period + 1][1]=='lab') or ((time_table[day][period][1] =='No Staff' and  time_table[day][period + 1][1]=='No Staff'))):
                    continue
                if time_table[day][period] != 0 and time_table[day][period + 1] != 0 and time_table[day][period][1] == time_table[day][period + 1][1]:
                    if time_table[day][period + 2] != 0 and time_table[day][period][1] == time_table[day][period + 2][1]:
                        return False
        return True

    def check_more_than_three_classes(self, staff):
        for staff_info in staff.values():
            for day in staff_info[2:]:
                count = sum(1 for period in day if period != 0)
                if count > 3:
                    return False
        return True

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
