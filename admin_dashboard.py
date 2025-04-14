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
        # system_settings_btn = QtWidgets.QPushButton('System Settings', self)
        # view_logs_btn = QtWidgets.QPushButton('View Logs', self)
        
        # Connect button actions
        manage_users_btn.clicked.connect(self.manage_users)
        manage_teachers_btn.clicked.connect(self.manage_teachers)
        
        for btn in [manage_users_btn, manage_teachers_btn]:
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
        
    def manage_users(self):
        # Create a new widget to display all users
        self.users_widget = QtWidgets.QWidget()
        users_layout = QtWidgets.QVBoxLayout(self.users_widget)
        
        # Add header with back button
        header = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel('Manage Users')
        title.setStyleSheet(COMMON_STYLES['title_label'])
        
        back_btn = QtWidgets.QPushButton('Back to Dashboard')
        back_btn.setStyleSheet(COMMON_STYLES['secondary_button'])
        back_btn.clicked.connect(lambda: self.main_window.stackedWidget.setCurrentWidget(self))
        
        header.addWidget(title)
        header.addStretch()
        header.addWidget(back_btn)
        users_layout.addLayout(header)
        
        # Add a container widget for the users list
        self.users_container = QtWidgets.QWidget()
        self.users_container_layout = QtWidgets.QVBoxLayout(self.users_container)
        users_layout.addWidget(self.users_container)
        
        # Load users
        self.load_users()
        
        users_layout.addStretch()
        self.main_window.stackedWidget.addWidget(self.users_widget)
        self.main_window.stackedWidget.setCurrentWidget(self.users_widget)
    
    def load_users(self):
        # Clear any existing content
        while self.users_container_layout.count():
            item = self.users_container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        try:
            from supabase_connection import create_connection
            supabase = create_connection()
            if not supabase:
                raise Exception("Failed to connect to Supabase")
            
            # Fetch all users
            response = supabase.table('users') \
                .select('username, user_type') \
                .execute()
            
            data = response.data
            if not data:
                no_users_label = QtWidgets.QLabel("No users found in the system.")
                no_users_label.setStyleSheet("font-size: 16px; color: #666; margin: 20px;")
                no_users_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.users_container_layout.addWidget(no_users_label)
                return
            
            # Add search and filter options
            filter_layout = QtWidgets.QHBoxLayout()
            search_box = QtWidgets.QLineEdit()
            search_box.setPlaceholderText("Search users...")
            search_box.setStyleSheet("padding: 8px; border: 1px solid #ccc; border-radius: 4px;")
            
            user_type_filter = QtWidgets.QComboBox()
            user_type_filter.addItems(["All Types", "Student", "Teacher", "Admin"])
            user_type_filter.setStyleSheet("padding: 8px; border: 1px solid #ccc; border-radius: 4px;")
            
            filter_layout.addWidget(search_box)
            filter_layout.addWidget(user_type_filter)
            self.users_container_layout.addLayout(filter_layout)
            
            # Create a scroll area for the users
            scroll_area = QtWidgets.QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_widget = QtWidgets.QWidget()
            scroll_layout = QtWidgets.QVBoxLayout(scroll_widget)
            scroll_layout.setSpacing(10)
            
            for user in data:
                user_card = QtWidgets.QWidget()
                user_card.setStyleSheet('''
                    QWidget {
                        background: white;
                        border-radius: 10px;
                        padding: 15px;
                        margin: 5px;
                        border: 1px solid #E0E0E0;
                    }
                    QWidget:hover {
                        background: #F5F5F5;
                    }
                ''')
                card_layout = QtWidgets.QHBoxLayout(user_card)
                
                # User info
                info_layout = QtWidgets.QVBoxLayout()
                username_label = QtWidgets.QLabel(f"Username: {user['username']}")
                username_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
                
                user_type_label = QtWidgets.QLabel(f"Type: {user['user_type']}")
                user_type_label.setStyleSheet("font-size: 14px; color: #666;")
                
                info_layout.addWidget(username_label)
                info_layout.addWidget(user_type_label)
                
                # Action buttons
                buttons_layout = QtWidgets.QHBoxLayout()
                edit_btn = QtWidgets.QPushButton("Edit")
                edit_btn.setStyleSheet(COMMON_STYLES['secondary_button'])
                
                delete_btn = QtWidgets.QPushButton("Delete")
                delete_btn.setStyleSheet('''
                    QPushButton {
                        background-color: #FF5252;
                        color: white;
                        border: none;
                        padding: 5px 10px;
                        border-radius: 4px;
                    }
                    QPushButton:hover {
                        background-color: #FF0000;
                    }
                ''')
                
                buttons_layout.addWidget(edit_btn)
                buttons_layout.addWidget(delete_btn)
                
                card_layout.addLayout(info_layout)
                card_layout.addStretch()
                card_layout.addLayout(buttons_layout)
                
                scroll_layout.addWidget(user_card)
            
            # Add a "Create New User" button at the bottom
            create_user_btn = QtWidgets.QPushButton("+ Create New User")
            create_user_btn.setStyleSheet(COMMON_STYLES['primary_button'])
            create_user_btn.setMinimumHeight(40)
            scroll_layout.addWidget(create_user_btn)
            
            scroll_area.setWidget(scroll_widget)
            self.users_container_layout.addWidget(scroll_area)
            
        except Exception as e:
            error_label = QtWidgets.QLabel(f"Failed to fetch users: {str(e)}")
            error_label.setStyleSheet("font-size: 14px; color: red; margin: 20px;")
            self.users_container_layout.addWidget(error_label)
    
    def manage_teachers(self):
        # Create a new widget to display teachers
        self.teachers_widget = QtWidgets.QWidget()
        teachers_layout = QtWidgets.QVBoxLayout(self.teachers_widget)
        
        # Add header with back button
        header = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel('Manage Teachers')
        title.setStyleSheet(COMMON_STYLES['title_label'])
        
        back_btn = QtWidgets.QPushButton('Back to Dashboard')
        back_btn.setStyleSheet(COMMON_STYLES['secondary_button'])
        back_btn.clicked.connect(lambda: self.main_window.stackedWidget.setCurrentWidget(self))
        
        header.addWidget(title)
        header.addStretch()
        header.addWidget(back_btn)
        teachers_layout.addLayout(header)
        
        # Add a container widget for the teachers list
        self.teachers_container = QtWidgets.QWidget()
        self.teachers_container_layout = QtWidgets.QVBoxLayout(self.teachers_container)
        teachers_layout.addWidget(self.teachers_container)
        
        # Load teachers
        self.load_teachers()
        
        teachers_layout.addStretch()
        self.main_window.stackedWidget.addWidget(self.teachers_widget)
        self.main_window.stackedWidget.setCurrentWidget(self.teachers_widget)
    
    def load_teachers(self):
        # Clear any existing content
        while self.teachers_container_layout.count():
            item = self.teachers_container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        try:
            from supabase_connection import create_connection
            supabase = create_connection()
            if not supabase:
                raise Exception("Failed to connect to Supabase")
            
            # Fetch only teachers
            response = supabase.table('users') \
                .select('username') \
                .eq('user_type', 'Teacher') \
                .execute()
            
            data = response.data
            if not data:
                no_teachers_label = QtWidgets.QLabel("No teachers found in the system.")
                no_teachers_label.setStyleSheet("font-size: 16px; color: #666; margin: 20px;")
                no_teachers_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.teachers_container_layout.addWidget(no_teachers_label)
                return
            
            # Add search
            search_layout = QtWidgets.QHBoxLayout()
            search_box = QtWidgets.QLineEdit()
            search_box.setPlaceholderText("Search teachers...")
            search_box.setStyleSheet("padding: 8px; border: 1px solid #ccc; border-radius: 4px;")
            
            search_layout.addWidget(search_box)
            self.teachers_container_layout.addLayout(search_layout)
            
            # Stats section
            stats_widget = QtWidgets.QWidget()
            stats_widget.setStyleSheet("background: #F8F9FA; border-radius: 8px; padding: 15px; margin-top: 10px;")
            stats_layout = QtWidgets.QHBoxLayout(stats_widget)
            
            total_teachers = len(data)
            active_exams = 0  # Would need additional query to get real data
            
            teachers_count = QtWidgets.QLabel(f"Total Teachers: {total_teachers}")
            teachers_count.setStyleSheet("font-size: 14px; font-weight: bold;")
            
            exams_count = QtWidgets.QLabel(f"Active Exams: {active_exams}")
            exams_count.setStyleSheet("font-size: 14px; font-weight: bold;")
            
            stats_layout.addWidget(teachers_count)
            stats_layout.addStretch()
            stats_layout.addWidget(exams_count)
            
            self.teachers_container_layout.addWidget(stats_widget)
            
            # Create a scroll area for the teachers
            scroll_area = QtWidgets.QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_widget = QtWidgets.QWidget()
            scroll_layout = QtWidgets.QVBoxLayout(scroll_widget)
            scroll_layout.setSpacing(10)
            
            for teacher in data:
                teacher_card = QtWidgets.QWidget()
                teacher_card.setStyleSheet('''
                    QWidget {
                        background: white;
                        border-radius: 10px;
                        padding: 15px;
                        margin: 5px;
                        border: 1px solid #E0E0E0;
                    }
                    QWidget:hover {
                        background: #F5F5F5;
                    }
                ''')
                card_layout = QtWidgets.QHBoxLayout(teacher_card)
                
                # Teacher info
                info_layout = QtWidgets.QVBoxLayout()
                username_label = QtWidgets.QLabel(f"Username: {teacher['username']}")
                username_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
                
                info_layout.addWidget(username_label)
                
                # Action buttons
                buttons_layout = QtWidgets.QHBoxLayout()
                view_exams_btn = QtWidgets.QPushButton("View Exams")
                view_exams_btn.setStyleSheet(COMMON_STYLES['secondary_button'])
                
                remove_btn = QtWidgets.QPushButton("Remove")
                remove_btn.setStyleSheet('''
                    QPushButton {
                        background-color: #FF5252;
                        color: white;
                        border: none;
                        padding: 5px 10px;
                        border-radius: 4px;
                    }
                    QPushButton:hover {
                        background-color: #FF0000;
                    }
                ''')
                
                buttons_layout.addWidget(view_exams_btn)
                buttons_layout.addWidget(remove_btn)
                
                card_layout.addLayout(info_layout)
                card_layout.addStretch()
                card_layout.addLayout(buttons_layout)
                
                scroll_layout.addWidget(teacher_card)
            
            # Add "Add Teacher" button at the bottom
            add_teacher_btn = QtWidgets.QPushButton("+ Add New Teacher")
            add_teacher_btn.setStyleSheet(COMMON_STYLES['primary_button'])
            add_teacher_btn.setMinimumHeight(40)
            scroll_layout.addWidget(add_teacher_btn)
            
            scroll_area.setWidget(scroll_widget)
            self.teachers_container_layout.addWidget(scroll_area)
            
        except Exception as e:
            error_label = QtWidgets.QLabel(f"Failed to fetch teachers: {str(e)}")
            error_label.setStyleSheet("font-size: 14px; color: red; margin: 20px;")
            self.teachers_container_layout.addWidget(error_label)