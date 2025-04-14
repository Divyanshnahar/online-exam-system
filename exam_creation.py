from PyQt6 import QtWidgets, QtCore, QtGui
from db_connection import create_connection
from PyQt6.QtCore import QDate, QTime

class ExamCreation(QtWidgets.QWidget):
    def __init__(self, main_window, teacher_username):
        super().__init__()
        self.main_window = main_window
        self.teacher_username = teacher_username
        self.exam_id = None
        self.questions = []
        self.current_question = 1
        self.total_questions = 0
        self.initUI()

    def initUI(self):
        # Main layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel("Create New Exam")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: black;")
        header.addWidget(title)
        
        back_btn = QtWidgets.QPushButton("Back to Dashboard")
        back_btn.setStyleSheet('''
            QPushButton {
                background-color: white;
                border: 1px solid #6C63FF;
                border-radius: 5px;
                color: #6C63FF;
                padding: 8px 15px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #6C63FF;
                color: white;
            }
        ''')
        back_btn.clicked.connect(self.go_back)
        header.addStretch()
        header.addWidget(back_btn)
        main_layout.addLayout(header)
        
        # Content area with stacked widget
        self.content_stack = QtWidgets.QStackedWidget()
        
        # First page - Exam details
        self.setup_page = QtWidgets.QWidget()
        setup_layout = QtWidgets.QVBoxLayout(self.setup_page)
        
        # Exam Details Section
        details_group = QtWidgets.QGroupBox("Exam Details")
        details_group.setStyleSheet('''
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 1px solid #ddd;
                border-radius: 5px;
                margin-top: 15px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #6C63FF;
            }
        ''')
        details_layout = QtWidgets.QFormLayout(details_group)
        details_layout.setVerticalSpacing(15)
        
        self.exam_name = QtWidgets.QLineEdit()
        self.exam_name.setStyleSheet('''
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background: white;
                font-size: 14px;
                color: black;
            }
            QLineEdit:focus {
                border: 1px solid #6C63FF;
            }
        ''')
        self.exam_name.setPlaceholderText("Enter exam name")
        
        self.question_count = QtWidgets.QSpinBox()
        self.question_count.setStyleSheet('''
            QSpinBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background: white;
                font-size: 14px;
                color: black;
            }
        ''')
        self.question_count.setMinimum(1)
        self.question_count.setMaximum(50)
        self.question_count.setValue(5)
        
        # Create labels with black color
        exam_name_label = QtWidgets.QLabel("Exam Name:")
        exam_name_label.setStyleSheet("color: black;")
        duration_label = QtWidgets.QLabel("Duration:")
        duration_label.setStyleSheet("color: black;")
        questions_label = QtWidgets.QLabel("Number of Questions:")
        questions_label.setStyleSheet("color: black;")
        
        details_layout.addRow(exam_name_label, self.exam_name)
        details_layout.addRow(questions_label, self.question_count)
        
        # Scheduling Section
        schedule_group = QtWidgets.QGroupBox("Exam Schedule")
        schedule_group.setStyleSheet('''
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 1px solid #ddd;
                border-radius: 5px;
                margin-top: 15px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #6C63FF;
            }
        ''')
        schedule_layout = QtWidgets.QFormLayout(schedule_group)
        schedule_layout.setVerticalSpacing(15)
        
        date_label = QtWidgets.QLabel("Exam Date:")
        date_label.setStyleSheet("color: black;")
        start_time_label = QtWidgets.QLabel("Start Time:")
        start_time_label.setStyleSheet("color: black;")
        end_time_label = QtWidgets.QLabel("End Time:")
        end_time_label.setStyleSheet("color: black;")
        
        # Add date and time pickers
        self.exam_date = QtWidgets.QDateEdit()
        self.exam_date.setStyleSheet('''
            QDateEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background: white;
                font-size: 14px;
                color: black;
            }
            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 25px;
                border-left: 1px solid #ddd;
                background: #f5f5f5;
            }
        ''')
        self.exam_date.setCalendarPopup(True)
        self.exam_date.setDisplayFormat("dd-MM-yyyy")
        self.exam_date.setDate(QDate.currentDate())
        
        # Start Time with better styling and clock icon
        self.start_time = QtWidgets.QTimeEdit()
        self.start_time.setStyleSheet('''
            QTimeEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background: white;
                font-size: 14px;
                color: black;
            }
            QTimeEdit::up-button, QTimeEdit::down-button {
                width: 16px;
                border-left: 1px solid #ddd;
                background: #f5f5f5;
            }
            QTimeEdit QAbstractItemView {
                color: black;
                background-color: white;
                selection-background-color: #6C63FF;
                selection-color: white;
            }
            QTimeEdit QSpinBox {
                color: black;
                background-color: white;
            }
            QTimeEdit::drop-down {
                background-color: #f5f5f5;
                width: 30px;
            }
        ''')
        self.start_time.setDisplayFormat("hh:mm:ss AP")
        self.start_time.setTime(QTime.currentTime())
        self.start_time.timeChanged.connect(self.update_end_time)
        
        start_time_layout = QtWidgets.QHBoxLayout()
        start_time_layout.addWidget(self.start_time)
        start_time_btn = QtWidgets.QPushButton()
        # Use a built-in character instead of a theme icon which might not be available
        start_time_btn.setText("🕒")
        start_time_btn.setStyleSheet('''
            QPushButton {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 8px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        ''')
        start_time_btn.setMaximumWidth(40)
        start_time_btn.setToolTip("Select Time")
        
        # Create time selection dialog for start time
        def show_start_time_dialog():
            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle("Select Start Time")
            dialog.setStyleSheet("background-color: white; color: black;")
            dialog_layout = QtWidgets.QVBoxLayout(dialog)
            
            time_picker = QtWidgets.QTimeEdit()
            time_picker.setStyleSheet('''
                QTimeEdit {
                    padding: 12px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    background: white;
                    font-size: 18px;
                    color: black;
                }
                QTimeEdit::up-button, QTimeEdit::down-button {
                    width: 20px;
                    height: 20px;
                    border-left: 1px solid #ddd;
                    background: #f5f5f5;
                    subcontrol-origin: border;
                    subcontrol-position: top right;
                    color: black;
                    border: 1px solid #ccc;
                }
                QTimeEdit::up-button {
                    subcontrol-position: top right;
                }
                QTimeEdit::down-button {
                    subcontrol-position: bottom right;
                }
                QTimeEdit::up-arrow {
                    width: 10px;
                    height: 10px;
                    image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNiIgaGVpZ2h0PSIxNiIgZmlsbD0iY3VycmVudENvbG9yIiBjbGFzcz0iYmkgYmktY2hldnJvbi11cCIgdmlld0JveD0iMCAwIDE2IDE2Ij48cGF0aCBmaWxsLXJ1bGU9ImV2ZW5vZGQiIGQ9Ik03LjY0NiAxLjE0NmEuNS41IDAgMCAxIC43MDggMGw2IDZhLjUuNSAwIDAgMS0uNzA4LjcwOEw4IDIuMjA3IDIuMzU0IDcuODU0YS41LjUgMCAxIDEtLjcwOC0uNzA4bDYtNnoiLz48L3N2Zz4=);
                }
                QTimeEdit::down-arrow {
                    width: 10px;
                    height: 10px;
                    image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNiIgaGVpZ2h0PSIxNiIgZmlsbD0iY3VycmVudENvbG9yIiBjbGFzcz0iYmkgYmktY2hldnJvbi1kb3duIiB2aWV3Qm94PSIwIDAgMTYgMTYiPjxwYXRoIGZpbGwtcnVsZT0iZXZlbm9kZCIgZD0iTTEuNjQ2IDQuNjQ2YS41LjUgMCAwIDEgLjcwOCAwTDggMTAuMjkzbDUuNjQ2LTUuNjQ3YS41LjUgMCAwIDEgLjcwOC43MDhsLTYgNmEuNS41IDAgMCAxLS43MDggMGwtNi02YS41LjUgMCAwIDEgMC0uNzA4eiIvPjwvc3ZnPg==);
                }
                /* Fix for dropdown elements */
                QTimeEdit QAbstractItemView {
                    color: black;
                    background-color: white;
                    selection-background-color: #6C63FF;
                    selection-color: white;
                }
                /* Fix for spinbox elements */
                QTimeEdit QSpinBox {
                    color: black;
                    background-color: white;
                }
                /* Fix for AM/PM selector */
                QTimeEdit::drop-down {
                    background-color: #f5f5f5;
                    width: 30px;
                }
                /* Fix for all widgets inside the time edit */
                QTimeEdit QWidget {
                    color: black;
                }
                /* Fix for selected time */
                QTimeEdit QWidget:item:selected {
                    color: white;
                    background-color: #6C63FF;
                }
            ''')
            time_picker.setDisplayFormat("hh:mm:ss AP")
            time_picker.setTime(self.start_time.time())
            
            # Make the time picker larger and more prominent
            time_picker.setMinimumHeight(60)
            dialog_layout.addWidget(time_picker)
            
            # Add custom hour selector
            hour_label = QtWidgets.QLabel("Hour:")
            hour_label.setStyleSheet("color: black; font-size: 14px; margin-top: 10px;")
            dialog_layout.addWidget(hour_label)
            
            hour_buttons = QtWidgets.QGridLayout()
            for i in range(12):
                hour = i + 1
                hour_btn = QtWidgets.QPushButton(str(hour))
                hour_btn.setFixedSize(40, 40)
                hour_btn.setStyleSheet('''
                    QPushButton {
                        background-color: #f0f0f0;
                        color: black;
                        border: 1px solid #ddd;
                        border-radius: 4px;
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background-color: #e0e0e0;
                    }
                    QPushButton:pressed {
                        background-color: #6C63FF;
                        color: white;
                    }
                ''')
                # Use a lambda with default argument to capture the current value of hour
                hour_btn.clicked.connect(lambda checked, h=hour: set_hour(h))
                hour_buttons.addWidget(hour_btn, i // 6, i % 6)
            
            dialog_layout.addLayout(hour_buttons)
            
            # Add custom minute selector
            minute_label = QtWidgets.QLabel("Minute:")
            minute_label.setStyleSheet("color: black; font-size: 14px; margin-top: 10px;")
            dialog_layout.addWidget(minute_label)
            
            minute_buttons = QtWidgets.QGridLayout()
            minutes = [0, 15, 30, 45]
            for i, minute in enumerate(minutes):
                minute_btn = QtWidgets.QPushButton(f"{minute:02d}")
                minute_btn.setFixedSize(60, 40)
                minute_btn.setStyleSheet('''
                    QPushButton {
                        background-color: #f0f0f0;
                        color: black;
                        border: 1px solid #ddd;
                        border-radius: 4px;
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background-color: #e0e0e0;
                    }
                    QPushButton:pressed {
                        background-color: #6C63FF;
                        color: white;
                    }
                ''')
                # Use a lambda with default argument to capture the current value of minute
                minute_btn.clicked.connect(lambda checked, m=minute: set_minute(m))
                minute_buttons.addWidget(minute_btn, 0, i)
            
            dialog_layout.addLayout(minute_buttons)
            
            # Add AM/PM selector buttons for easier selection
            am_pm_layout = QtWidgets.QHBoxLayout()
            am_btn = QtWidgets.QPushButton("AM")
            pm_btn = QtWidgets.QPushButton("PM")
            
            for btn in [am_btn, pm_btn]:
                btn.setMinimumHeight(40)
                btn.setStyleSheet('''
                    QPushButton {
                        background-color: #f0f0f0;
                        color: black;
                        border: 1px solid #ddd;
                        border-radius: 4px;
                        padding: 8px;
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background-color: #e0e0e0;
                    }
                    QPushButton:pressed {
                        background-color: #6C63FF;
                        color: white;
                    }
                ''')
            
            am_btn.clicked.connect(lambda: set_am_pm(True))
            pm_btn.clicked.connect(lambda: set_am_pm(False))
            
            am_pm_layout.addWidget(am_btn)
            am_pm_layout.addWidget(pm_btn)
            dialog_layout.addLayout(am_pm_layout)
            
            # Helper functions to set time
            def set_hour(hour):
                current_time = time_picker.time()
                is_pm = current_time.hour() >= 12
                new_hour = hour if not is_pm else hour + 12
                if new_hour == 24:  # Handle 12 PM case
                    new_hour = 12
                new_time = QtCore.QTime(new_hour, current_time.minute(), current_time.second())
                time_picker.setTime(new_time)
            
            def set_minute(minute):
                current_time = time_picker.time()
                new_time = QtCore.QTime(current_time.hour(), minute, current_time.second())
                time_picker.setTime(new_time)
            
            def set_am_pm(is_am):
                current_time = time_picker.time()
                hour = current_time.hour()
                if is_am and hour >= 12:
                    hour -= 12
                elif not is_am and hour < 12:
                    hour += 12
                new_time = QtCore.QTime(hour, current_time.minute(), current_time.second())
                time_picker.setTime(new_time)
            
            # Add OK/Cancel buttons
            buttons = QtWidgets.QDialogButtonBox(
                QtWidgets.QDialogButtonBox.StandardButton.Ok | 
                QtWidgets.QDialogButtonBox.StandardButton.Cancel
            )
            buttons.accepted.connect(lambda: [self.start_time.setTime(time_picker.time()), dialog.accept()])
            buttons.rejected.connect(dialog.reject)
            buttons.setStyleSheet('''
                QPushButton {
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-size: 14px;
                }
                QPushButton[text="OK"] {
                    background-color: #6C63FF;
                    color: white;
                    border: none;
                }
                QPushButton[text="Cancel"] {
                    background-color: white;
                    color: black;
                    border: 1px solid #ddd;
                }
                QPushButton:hover {
                    opacity: 0.8;
                }
            ''')
            
            dialog_layout.addWidget(buttons)
            
            dialog.exec()
        
        start_time_btn.clicked.connect(show_start_time_dialog)
        start_time_layout.addWidget(start_time_btn)
        
        # End Time with better styling and clock icon
        self.end_time = QtWidgets.QTimeEdit()
        self.end_time.setStyleSheet('''
            QTimeEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background: white;
                font-size: 14px;
                color: black;
            }
            QTimeEdit::up-button, QTimeEdit::down-button {
                width: 16px;
                border-left: 1px solid #ddd;
                background: #f5f5f5;
            }
            QTimeEdit QAbstractItemView {
                color: black;
                background-color: white;
                selection-background-color: #6C63FF;
                selection-color: white;
            }
            QTimeEdit QSpinBox {
                color: black;
                background-color: white;
            }
            QTimeEdit::drop-down {
                background-color: #f5f5f5;
                width: 30px;
            }
        ''')
        self.end_time.setDisplayFormat("hh:mm:ss AP")
        self.end_time.setTime(QTime.currentTime().addSecs(3600))  # Default to 1 hour later
        
        end_time_layout = QtWidgets.QHBoxLayout()
        end_time_layout.addWidget(self.end_time)
        end_time_btn = QtWidgets.QPushButton()
        # Use a built-in character instead of a theme icon which might not be available
        end_time_btn.setText("🕒")
        end_time_btn.setStyleSheet('''
            QPushButton {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 8px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        ''')
        end_time_btn.setMaximumWidth(40)
        end_time_btn.setToolTip("Select Time")
        
        # Create time selection dialog for end time
        def show_end_time_dialog():
            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle("Select End Time")
            dialog.setStyleSheet("background-color: white; color: black;")
            dialog_layout = QtWidgets.QVBoxLayout(dialog)
            
            time_picker = QtWidgets.QTimeEdit()
            time_picker.setStyleSheet('''
                QTimeEdit {
                    padding: 12px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    background: white;
                    font-size: 18px;
                    color: black;
                }
                QTimeEdit::up-button, QTimeEdit::down-button {
                    width: 20px;
                    height: 20px;
                    border-left: 1px solid #ddd;
                    background: #f5f5f5;
                    subcontrol-origin: border;
                    subcontrol-position: top right;
                    color: black;
                    border: 1px solid #ccc;
                }
                QTimeEdit::up-button {
                    subcontrol-position: top right;
                }
                QTimeEdit::down-button {
                    subcontrol-position: bottom right;
                }
                QTimeEdit::up-arrow {
                    width: 10px;
                    height: 10px;
                    image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNiIgaGVpZ2h0PSIxNiIgZmlsbD0iY3VycmVudENvbG9yIiBjbGFzcz0iYmkgYmktY2hldnJvbi11cCIgdmlld0JveD0iMCAwIDE2IDE2Ij48cGF0aCBmaWxsLXJ1bGU9ImV2ZW5vZGQiIGQ9Ik03LjY0NiAxLjE0NmEuNS41IDAgMCAxIC43MDggMGw2IDZhLjUuNSAwIDAgMS0uNzA4LjcwOEw4IDIuMjA3IDIuMzU0IDcuODU0YS41LjUgMCAxIDEtLjcwOC0uNzA4bDYtNnoiLz48L3N2Zz4=);
                }
                QTimeEdit::down-arrow {
                    width: 10px;
                    height: 10px;
                    image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNiIgaGVpZ2h0PSIxNiIgZmlsbD0iY3VycmVudENvbG9yIiBjbGFzcz0iYmkgYmktY2hldnJvbi1kb3duIiB2aWV3Qm94PSIwIDAgMTYgMTYiPjxwYXRoIGZpbGwtcnVsZT0iZXZlbm9kZCIgZD0iTTEuNjQ2IDQuNjQ2YS41LjUgMCAwIDEgLjcwOCAwTDggMTAuMjkzbDUuNjQ2LTUuNjQ3YS41LjUgMCAwIDEgLjcwOC43MDhsLTYgNmEuNS41IDAgMCAxLS43MDggMGwtNi02YS41LjUgMCAwIDEgMC0uNzA4eiIvPjwvc3ZnPg==);
                }
                /* Fix for dropdown elements */
                QTimeEdit QAbstractItemView {
                    color: black;
                    background-color: white;
                    selection-background-color: #6C63FF;
                    selection-color: white;
                }
                /* Fix for spinbox elements */
                QTimeEdit QSpinBox {
                    color: black;
                    background-color: white;
                }
                /* Fix for AM/PM selector */
                QTimeEdit::drop-down {
                    background-color: #f5f5f5;
                    width: 30px;
                }
                /* Fix for all widgets inside the time edit */
                QTimeEdit QWidget {
                    color: black;
                }
                /* Fix for selected time */
                QTimeEdit QWidget:item:selected {
                    color: white;
                    background-color: #6C63FF;
                }
            ''')
            time_picker.setDisplayFormat("hh:mm:ss AP")
            time_picker.setTime(self.end_time.time())
            
            # Make the time picker larger and more prominent
            time_picker.setMinimumHeight(60)
            dialog_layout.addWidget(time_picker)
            
            # Add custom hour selector
            hour_label = QtWidgets.QLabel("Hour:")
            hour_label.setStyleSheet("color: black; font-size: 14px; margin-top: 10px;")
            dialog_layout.addWidget(hour_label)
            
            hour_buttons = QtWidgets.QGridLayout()
            for i in range(12):
                hour = i + 1
                hour_btn = QtWidgets.QPushButton(str(hour))
                hour_btn.setFixedSize(40, 40)
                hour_btn.setStyleSheet('''
                    QPushButton {
                        background-color: #f0f0f0;
                        color: black;
                        border: 1px solid #ddd;
                        border-radius: 4px;
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background-color: #e0e0e0;
                    }
                    QPushButton:pressed {
                        background-color: #6C63FF;
                        color: white;
                    }
                ''')
                # Use a lambda with default argument to capture the current value of hour
                hour_btn.clicked.connect(lambda checked, h=hour: set_hour(h))
                hour_buttons.addWidget(hour_btn, i // 6, i % 6)
            
            dialog_layout.addLayout(hour_buttons)
            
            # Add custom minute selector
            minute_label = QtWidgets.QLabel("Minute:")
            minute_label.setStyleSheet("color: black; font-size: 14px; margin-top: 10px;")
            dialog_layout.addWidget(minute_label)
            
            minute_buttons = QtWidgets.QGridLayout()
            minutes = [0, 15, 30, 45]
            for i, minute in enumerate(minutes):
                minute_btn = QtWidgets.QPushButton(f"{minute:02d}")
                minute_btn.setFixedSize(60, 40)
                minute_btn.setStyleSheet('''
                    QPushButton {
                        background-color: #f0f0f0;
                        color: black;
                        border: 1px solid #ddd;
                        border-radius: 4px;
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background-color: #e0e0e0;
                    }
                    QPushButton:pressed {
                        background-color: #6C63FF;
                        color: white;
                    }
                ''')
                # Use a lambda with default argument to capture the current value of minute
                minute_btn.clicked.connect(lambda checked, m=minute: set_minute(m))
                minute_buttons.addWidget(minute_btn, 0, i)
            
            dialog_layout.addLayout(minute_buttons)
            
            # Add AM/PM selector buttons for easier selection
            am_pm_layout = QtWidgets.QHBoxLayout()
            am_btn = QtWidgets.QPushButton("AM")
            pm_btn = QtWidgets.QPushButton("PM")
            
            for btn in [am_btn, pm_btn]:
                btn.setMinimumHeight(40)
                btn.setStyleSheet('''
                    QPushButton {
                        background-color: #f0f0f0;
                        color: black;
                        border: 1px solid #ddd;
                        border-radius: 4px;
                        padding: 8px;
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background-color: #e0e0e0;
                    }
                    QPushButton:pressed {
                        background-color: #6C63FF;
                        color: white;
                    }
                ''')
            
            am_btn.clicked.connect(lambda: set_am_pm(True))
            pm_btn.clicked.connect(lambda: set_am_pm(False))
            
            am_pm_layout.addWidget(am_btn)
            am_pm_layout.addWidget(pm_btn)
            dialog_layout.addLayout(am_pm_layout)
            
            # Helper functions to set time
            def set_hour(hour):
                current_time = time_picker.time()
                is_pm = current_time.hour() >= 12
                new_hour = hour if not is_pm else hour + 12
                if new_hour == 24:  # Handle 12 PM case
                    new_hour = 12
                new_time = QtCore.QTime(new_hour, current_time.minute(), current_time.second())
                time_picker.setTime(new_time)
            
            def set_minute(minute):
                current_time = time_picker.time()
                new_time = QtCore.QTime(current_time.hour(), minute, current_time.second())
                time_picker.setTime(new_time)
            
            def set_am_pm(is_am):
                current_time = time_picker.time()
                hour = current_time.hour()
                if is_am and hour >= 12:
                    hour -= 12
                elif not is_am and hour < 12:
                    hour += 12
                new_time = QtCore.QTime(hour, current_time.minute(), current_time.second())
                time_picker.setTime(new_time)
            
            # Add OK/Cancel buttons
            buttons = QtWidgets.QDialogButtonBox(
                QtWidgets.QDialogButtonBox.StandardButton.Ok | 
                QtWidgets.QDialogButtonBox.StandardButton.Cancel
            )
            buttons.accepted.connect(lambda: [self.end_time.setTime(time_picker.time()), dialog.accept()])
            buttons.rejected.connect(dialog.reject)
            buttons.setStyleSheet('''
                QPushButton {
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-size: 14px;
                }
                QPushButton[text="OK"] {
                    background-color: #6C63FF;
                    color: white;
                    border: none;
                }
                QPushButton[text="Cancel"] {
                    background-color: white;
                    color: black;
                    border: 1px solid #ddd;
                }
                QPushButton:hover {
                    opacity: 0.8;
                }
            ''')
            
            dialog_layout.addWidget(buttons)
            
            dialog.exec()
        
        end_time_btn.clicked.connect(show_end_time_dialog)
        end_time_layout.addWidget(end_time_btn)
        
        # Add calendar button with improved popup handling
        date_layout = QtWidgets.QHBoxLayout()
        date_layout.addWidget(self.exam_date)
        calendar_btn = QtWidgets.QPushButton()
        # Use a built-in character instead of a theme icon which might not be available
        calendar_btn.setText("📅")
        calendar_btn.setStyleSheet('''
            QPushButton {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 8px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        ''')
        calendar_btn.setMaximumWidth(40)
        calendar_btn.setToolTip("Open Calendar")
        
        # Create a proper calendar popup
        def show_calendar():
            # Create a dialog to ensure the calendar is fully visible
            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle("Select Date")
            dialog.setStyleSheet("background-color: white; color: black;")
            dialog_layout = QtWidgets.QVBoxLayout(dialog)
            
            calendar = QtWidgets.QCalendarWidget()
            calendar.setSelectedDate(self.exam_date.date())
            calendar.setMinimumSize(500, 400)  # Make calendar larger
            calendar.setGridVisible(True)  # Show grid lines for better visibility
            calendar.setFirstDayOfWeek(QtCore.Qt.DayOfWeek.Monday)
            calendar.setHorizontalHeaderFormat(QtWidgets.QCalendarWidget.HorizontalHeaderFormat.LongDayNames)
            calendar.setVerticalHeaderFormat(QtWidgets.QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
            calendar.setNavigationBarVisible(True)
            calendar.setStyleSheet('''
                QCalendarWidget {
                    background-color: white;
                    min-width: 500px;
                    min-height: 400px;
                }
                QCalendarWidget QToolButton {
                    color: #6C63FF;
                    background-color: white;
                    font-size: 16px;
                    min-width: 80px;
                    padding: 5px;
                }
                QCalendarWidget QMenu {
                    width: 150px;
                    left: 20px;
                    font-size: 14px;
                    color: black;
                    background-color: white;
                }
                QCalendarWidget QSpinBox {
                    font-size: 14px;
                    width: 60px;
                    color: black;
                    background-color: white;
                }
                QCalendarWidget QAbstractItemView:enabled {
                    font-size: 14px;
                    color: black;
                    background-color: white;
                    selection-background-color: #6C63FF;
                    selection-color: white;
                }
                QCalendarWidget QWidget#qt_calendar_navigationbar {
                    background-color: #f8f8f8;
                    padding: 4px;
                    min-height: 40px;
                }
                QCalendarWidget QWidget#qt_calendar_prevmonth, 
                QCalendarWidget QWidget#qt_calendar_nextmonth {
                    qproperty-icon: none;
                    min-width: 40px;
                    font-size: 18px;
                    color: #6C63FF;
                }
                QCalendarWidget QWidget#qt_calendar_prevmonth {
                    qproperty-text: "<";
                }
                QCalendarWidget QWidget#qt_calendar_nextmonth {
                    qproperty-text: ">";
                }
                QCalendarWidget QWidget#qt_calendar_yearbutton, 
                QCalendarWidget QWidget#qt_calendar_monthbutton {
                    font-size: 16px;
                    font-weight: bold;
                    color: #333;
                    padding: 5px 10px;
                }
                QCalendarWidget QTableView {
                    alternate-background-color: #f5f5f5;
                    color: black;
                }
                /* Fix for weekday headers */
                QCalendarWidget QTableView QHeaderView {
                    color: black;
                }
                /* Fix for day numbers */
                QCalendarWidget QTableView QTableCornerButton::section {
                    color: black;
                    background-color: white;
                }
                /* Fix for selected date */
                QCalendarWidget QTableView:item:selected {
                    color: white;
                    background-color: #6C63FF;
                }
                /* Fix for today's date */
                QCalendarWidget QTableView:item:hover {
                    background-color: #e0e0ff;
                }
                /* Fix for dates in other months */
                QCalendarWidget QTableView:disabled {
                    color: #aaa;
                }
            ''')
            
            dialog_layout.addWidget(calendar)
            
            buttons = QtWidgets.QDialogButtonBox(
                QtWidgets.QDialogButtonBox.StandardButton.Ok | 
                QtWidgets.QDialogButtonBox.StandardButton.Cancel
            )
            buttons.accepted.connect(lambda: [self.exam_date.setDate(calendar.selectedDate()), dialog.accept()])
            buttons.rejected.connect(dialog.reject)
            buttons.setStyleSheet('''
                QPushButton {
                    padding: 8px 16px;
                    font-size: 14px;
                    border-radius: 4px;
                    min-width: 80px;
                }
                QPushButton[text="OK"] {
                    background-color: #6C63FF;
                    color: white;
                    border: none;
                }
                QPushButton[text="Cancel"] {
                    background-color: white;
                    color: black;
                    border: 1px solid #ccc;
                }
                QPushButton[text="OK"]:hover {
                    background-color: #5952cc;
                }
                QPushButton[text="Cancel"]:hover {
                    background-color: #f0f0f0;
                }
            ''')
            dialog_layout.addWidget(buttons)
            
            dialog.setMinimumSize(550, 500)
            dialog.exec()
        
        calendar_btn.clicked.connect(show_calendar)
        date_layout.addWidget(calendar_btn)
        
        # Duration selection with hours, minutes, and seconds
        duration_layout = QtWidgets.QHBoxLayout()
        
        self.duration_hours = QtWidgets.QSpinBox()
        self.duration_hours.setStyleSheet('''
            QSpinBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background: white;
                font-size: 14px;
                color: black;
            }
        ''')
        self.duration_hours.setMinimum(0)
        self.duration_hours.setMaximum(5)
        self.duration_hours.setValue(1)
        self.duration_hours.setSuffix(" hrs")
        self.duration_hours.valueChanged.connect(self.update_end_time)
        
        self.duration_minutes = QtWidgets.QSpinBox()
        self.duration_minutes.setStyleSheet('''
            QSpinBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background: white;
                font-size: 14px;
                color: black;
            }
        ''')
        self.duration_minutes.setMinimum(0)
        self.duration_minutes.setMaximum(59)
        self.duration_minutes.setValue(0)
        self.duration_minutes.setSuffix(" mins")
        self.duration_minutes.valueChanged.connect(self.update_end_time)
        
        self.duration_seconds = QtWidgets.QSpinBox()
        self.duration_seconds.setStyleSheet('''
            QSpinBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background: white;
                font-size: 14px;
                color: black;
            }
        ''')
        self.duration_seconds.setMinimum(0)
        self.duration_seconds.setMaximum(59)
        self.duration_seconds.setValue(0)
        self.duration_seconds.setSuffix(" secs")
        self.duration_seconds.valueChanged.connect(self.update_end_time)
        
        duration_layout.addWidget(self.duration_hours)
        duration_layout.addWidget(self.duration_minutes)
        duration_layout.addWidget(self.duration_seconds)
        
        schedule_info = QtWidgets.QLabel("Note: Students can only take the exam during this scheduled time window.")
        schedule_info.setStyleSheet("color: #666; font-style: italic; font-size: 12px;")
        
        schedule_layout.addRow(date_label, date_layout)
        schedule_layout.addRow(duration_label, duration_layout)
        schedule_layout.addRow(start_time_label, start_time_layout)
        schedule_layout.addRow(end_time_label, end_time_layout)
        schedule_layout.addRow("", schedule_info)
        
        setup_layout.addWidget(details_group)
        setup_layout.addWidget(schedule_group)
        setup_layout.addStretch()
        
        start_btn = QtWidgets.QPushButton("Start Adding Questions")
        start_btn.setStyleSheet('''
            QPushButton {
                background-color: #6C63FF;
                border: none;
                border-radius: 5px;
                color: white;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #5952cc;
            }
        ''')
        start_btn.clicked.connect(self.start_questions)
        setup_layout.addWidget(start_btn)
        
        # Question page
        self.question_page = QtWidgets.QWidget()
        question_layout = QtWidgets.QVBoxLayout(self.question_page)
        
        self.progress_label = QtWidgets.QLabel("Question 1 of 5")
        self.progress_label.setStyleSheet("font-size: 16px; margin-bottom: 10px;")
        question_layout.addWidget(self.progress_label)
        
        self.question_input = QtWidgets.QTextEdit()
        self.question_input.setStyleSheet('''
            QTextEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background: white;
                font-size: 14px;
                color: black;
            }
        ''')
        self.question_input.setPlaceholderText("Enter question text")
        self.question_input.setMinimumHeight(100)
        question_layout.addWidget(self.question_input)
        
        options_layout = QtWidgets.QVBoxLayout()
        options_layout.setSpacing(10)
        
        option_style = '''
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background: white;
                font-size: 14px;
                color: black;
            }
        '''
        
        self.option1 = QtWidgets.QLineEdit()
        self.option2 = QtWidgets.QLineEdit()
        self.option3 = QtWidgets.QLineEdit()
        self.option4 = QtWidgets.QLineEdit()
        
        for i, option in enumerate([self.option1, self.option2, self.option3, self.option4], 1):
            option.setStyleSheet(option_style)
            option.setPlaceholderText(f"Option {i}")
            options_layout.addWidget(option)
            
        question_layout.addLayout(options_layout)
        
        self.correct_answer = QtWidgets.QComboBox()
        self.correct_answer.setStyleSheet('''
            QComboBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background: white;
                font-size: 14px;
                color: black;
            }
            QComboBox QAbstractItemView {
                color: black;
            }
        ''')
        self.correct_answer.addItems(["Select correct answer", "Option 1", "Option 2", "Option 3", "Option 4"])
        question_layout.addWidget(self.correct_answer)
        
        buttons_layout = QtWidgets.QHBoxLayout()
        next_btn = QtWidgets.QPushButton("Next Question")
        next_btn.setStyleSheet('''
            QPushButton {
                background-color: #6C63FF;
                border: none;
                border-radius: 5px;
                color: white;
                padding: 8px 15px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #5952cc;
            }
        ''')
        next_btn.clicked.connect(self.next_question)
        
        self.finish_btn = QtWidgets.QPushButton("Finish Exam")  # Changed to self to access it later
        self.finish_btn.setStyleSheet('''
            QPushButton {
                background-color: white;
                border: 1px solid #6C63FF;
                border-radius: 5px;
                color: #6C63FF;
                padding: 8px 15px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #6C63FF;
                color: white;
            }
        ''')
        self.finish_btn.clicked.connect(self.finish_exam)
        self.finish_btn.hide()  # Hide initially
        
        buttons_layout.addWidget(next_btn)
        buttons_layout.addWidget(self.finish_btn)
        question_layout.addStretch()
        question_layout.addLayout(buttons_layout)
        
        # Add pages to stack
        self.content_stack.addWidget(self.setup_page)
        self.content_stack.addWidget(self.question_page)
        main_layout.addWidget(self.content_stack)

    def update_end_time(self):
        # Update end time to be at least the duration after start time
        start = self.start_time.time()
        
        # Calculate duration in seconds (hours + minutes + seconds)
        duration_secs = (self.duration_hours.value() * 3600) + (self.duration_minutes.value() * 60) + self.duration_seconds.value()
        
        # Convert to seconds since midnight
        start_secs = start.hour() * 3600 + start.minute() * 60 + start.second()
        end_secs = start_secs + duration_secs
        
        # Create new time
        hours = end_secs // 3600
        minutes = (end_secs % 3600) // 60
        seconds = end_secs % 60
        
        # Handle day overflow (cap at 23:59:59)
        if hours >= 24:
            hours = 23
            minutes = 59
            seconds = 59
            
        end_time = QTime(hours, minutes, seconds)
        self.end_time.setTime(end_time)

    def start_questions(self):
        exam_name = self.exam_name.text().strip()
        
        if not exam_name:
            self.show_error("Please enter an exam name")
            return
            
        # Validate start and end times
        start_time = self.start_time.time()
        end_time = self.end_time.time()
        if end_time <= start_time:
            self.show_error("End time must be after start time")
            return
            
        self.total_questions = self.question_count.value()
        self.current_question = 1
        self.update_progress_label()
        
        # If there's only one question, show the finish button right away
        if self.total_questions == 1:
            self.finish_btn.show()
        
        # Calculate total duration in seconds instead of decimal minutes
        total_duration_seconds = (self.duration_hours.value() * 3600) + (self.duration_minutes.value() * 60) + self.duration_seconds.value()
        
        try:
            # Connect to Supabase
            supabase = create_connection()
            if not supabase:
                raise Exception("Failed to connect to Supabase")
                
            # Convert date and times to format Supabase expects
            exam_date = self.exam_date.date().toPyDate().isoformat()
            start_time_str = self.start_time.time().toPyTime().strftime('%H:%M:%S')
            end_time_str = self.end_time.time().toPyTime().strftime('%H:%M:%S')
            
            # Insert the new exam - using seconds for duration
            response = supabase.table('exams').insert({
                'name': exam_name,
                'teacher_username': self.teacher_username,
                'duration': total_duration_seconds,
                'status': 'draft',
                'created_at': 'now()', # Use Supabase's now() function
                'exam_date': exam_date,
                'start_time': start_time_str,
                'end_time': end_time_str
            }).execute()
            
            # Get the exam ID from the response
            if response.data and len(response.data) > 0:
                self.exam_id = response.data[0]['id']
                self.content_stack.setCurrentWidget(self.question_page)
            else:
                raise Exception("Failed to get exam ID after creation")
                
        except Exception as e:
            self.show_error(f"Error creating exam: {str(e)}")

    def update_progress_label(self):
        self.progress_label.setText(f"Question {self.current_question} of {self.total_questions}")
        self.progress_label.setStyleSheet("font-size: 16px; margin-bottom: 10px; color: black;")

    def next_question(self):
        if self.save_question():
            if self.current_question < self.total_questions:
                self.current_question += 1
                self.update_progress_label()
                self.clear_fields()
            if self.current_question == self.total_questions:
                self.finish_btn.show()  # Show finish button on last question

    def save_question(self):
        question_text = self.question_input.toPlainText().strip()
        option1 = self.option1.text().strip()
        option2 = self.option2.text().strip()
        option3 = self.option3.text().strip()
        option4 = self.option4.text().strip()
        correct_answer = self.correct_answer.currentText()

        if not question_text:
            self.show_error("Question cannot be empty")
            return False

        if not all([option1, option2, option3, option4]):
            self.show_error("All options must be filled")
            return False

        if correct_answer == "Select correct answer":
            self.show_error("Please select the correct answer")
            return False

        try:
            # Connect to Supabase
            supabase = create_connection()
            if not supabase:
                raise Exception("Failed to connect to Supabase")
                
            # Insert the question
            supabase.table('questions').insert({
                'exam_id': self.exam_id,
                'question_text': question_text,
                'option1': option1,
                'option2': option2,
                'option3': option3,
                'option4': option4,
                'correct_answer': correct_answer
            }).execute()
            
            return True
        except Exception as e:
            self.show_error(f"Error saving question: {str(e)}")
            return False

    def finish_exam(self):
        if self.save_question():
            try:
                # Connect to Supabase
                supabase = create_connection()
                if not supabase:
                    raise Exception("Failed to connect to Supabase")
                    
                # Update the exam status
                supabase.table('exams') \
                    .update({'status': 'active'}) \
                    .eq('id', self.exam_id) \
                    .execute()
                
                msg = QtWidgets.QMessageBox()
                msg.setWindowTitle("Success")
                msg.setText("Exam created and scheduled successfully!")
                msg.setInformativeText(f"Exam Date: {self.exam_date.date().toString('yyyy-MM-dd')}\nTime: {self.start_time.time().toString('hh:mm:ss')} - {self.end_time.time().toString('hh:mm:ss')}")
                msg.setIcon(QtWidgets.QMessageBox.Icon.Information)
                msg.exec()
                
                self.go_back()
            except Exception as e:
                self.show_error(f"Error finalizing exam: {str(e)}")

    def clear_fields(self):
        self.question_input.clear()
        self.option1.clear()
        self.option2.clear()
        self.option3.clear()
        self.option4.clear()
        self.correct_answer.setCurrentIndex(0)

    def go_back(self):
        self.main_window.stackedWidget.setCurrentWidget(self.main_window.teacher_dashboard)

    def show_error(self, message):
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle("Error")
        msg.setText(message)
        msg.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        msg.exec()