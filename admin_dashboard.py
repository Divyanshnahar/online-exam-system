from PyQt6 import QtWidgets, QtCore
from styles import COMMON_STYLES

class AdminDashboard(QtWidgets.QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.initUI()

    def initUI(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header
        header = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel('Admin Dashboard', self)
        title.setStyleSheet(COMMON_STYLES['title_label'])
        header.addWidget(title)
        
        logout_btn = QtWidgets.QPushButton('Logout', self)
        logout_btn.setStyleSheet(COMMON_STYLES['secondary_button'])
        logout_btn.clicked.connect(self.logout)
        header.addStretch()
        header.addWidget(logout_btn)
        layout.addLayout(header)

        # Main Content
        content = QtWidgets.QHBoxLayout()
        
        # Left Panel - Navigation
        nav_panel = QtWidgets.QVBoxLayout()
        manage_users_btn = QtWidgets.QPushButton('Manage Users', self)
        manage_teachers_btn = QtWidgets.QPushButton('Manage Teachers', self)
        system_settings_btn = QtWidgets.QPushButton('System Settings', self)
        view_logs_btn = QtWidgets.QPushButton('View Logs', self)
        
        for btn in [manage_users_btn, manage_teachers_btn, system_settings_btn, view_logs_btn]:
            btn.setStyleSheet(COMMON_STYLES['primary_button'])
            nav_panel.addWidget(btn)
        
        nav_panel.addStretch()
        content.addLayout(nav_panel)
        
        # Right Panel - Content Area
        content_area = QtWidgets.QStackedWidget()
        content_area.setStyleSheet('background: white; border-radius: 10px;')
        content.addWidget(content_area)
        
        layout.addLayout(content)

    def logout(self):
        self.main_window.stackedWidget.setCurrentWidget(self.main_window.login_page)