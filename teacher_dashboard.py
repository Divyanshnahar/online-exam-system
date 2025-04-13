from PyQt6 import QtWidgets, QtCore
from styles import COMMON_STYLES
from exam_creation import ExamCreation

class TeacherDashboard(QtWidgets.QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.initUI()

    def handle_action(self, action):
        if action == 'Create Exam':
            try:
                if hasattr(self.main_window, 'current_user') and self.main_window.current_user:
                    exam_page = ExamCreation(self.main_window, self.main_window.current_user)
                    self.main_window.stackedWidget.addWidget(exam_page)
                    self.main_window.stackedWidget.setCurrentWidget(exam_page)
                else:
                    msg = QtWidgets.QMessageBox()
                    msg.setWindowTitle("Error")
                    msg.setText("Session error. Please login again.")
                    msg.setIcon(QtWidgets.QMessageBox.Icon.Warning)
                    msg.exec()
            except Exception as e:
                msg = QtWidgets.QMessageBox()
                msg.setWindowTitle("Error")
                msg.setText(f"Error creating exam page: {str(e)}")
                msg.setIcon(QtWidgets.QMessageBox.Icon.Critical)
                msg.exec()

    def initUI(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Header with welcome and logout
        header = QtWidgets.QHBoxLayout()
        welcome_label = QtWidgets.QLabel(f'Welcome, {self.main_window.current_user}!', self)
        welcome_label.setStyleSheet('font-size: 24px; font-weight: bold; color: #333333;')
        header.addWidget(welcome_label)
        
        logout_btn = QtWidgets.QPushButton('Logout', self)
        logout_btn.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        logout_btn.setStyleSheet('''
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
        logout_btn.clicked.connect(self.logout)
        header.addStretch()
        header.addWidget(logout_btn)
        main_layout.addLayout(header)

        # Content area
        content_widget = QtWidgets.QWidget()
        content_widget.setStyleSheet('background-color: white; border-radius: 10px;')
        content_layout = QtWidgets.QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)

        # Quick Actions Section
        quick_actions_label = QtWidgets.QLabel('Quick Actions', self)
        quick_actions_label.setStyleSheet('font-size: 18px; font-weight: bold; color: #333333;')
        content_layout.addWidget(quick_actions_label)

        # Action buttons grid
        actions_grid = QtWidgets.QGridLayout()
        actions_grid.setSpacing(15)

        actions = [
            ('Create Exam', 'Create new exam'),
            ('View Exams', 'Manage existing exams'),
            ('View Results', 'Check student results'),
            ('Manage Students', 'View and manage students')
        ]

        for i, (title, description) in enumerate(actions):
            action_widget = QtWidgets.QWidget()
            action_widget.setStyleSheet('''
                QWidget {
                    background-color: #F8F9FA;
                    border-radius: 8px;
                }
                QWidget:hover {
                    background-color: #E9ECEF;
                }
            ''')
            action_widget.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)

            action_layout = QtWidgets.QVBoxLayout(action_widget)
            action_layout.setContentsMargins(20, 15, 20, 15)

            title_label = QtWidgets.QLabel(title)
            title_label.setStyleSheet('font-size: 16px; color: #6C63FF; font-weight: bold;')

            desc_label = QtWidgets.QLabel(description)
            desc_label.setStyleSheet('color: #666666;')

            action_layout.addWidget(title_label)
            action_layout.addWidget(desc_label)

            if title == 'Create Exam':
                action_widget.mouseReleaseEvent = lambda _, t=title: self.handle_action(t)

            row = i // 2
            col = i % 2
            actions_grid.addWidget(action_widget, row, col)

        content_layout.addLayout(actions_grid)
        main_layout.addWidget(content_widget)
        main_layout.addStretch()

    def logout(self):
        self.main_window.current_user = None
        self.main_window.current_user_type = None
        self.main_window.stackedWidget.setCurrentWidget(self.main_window.login_page)