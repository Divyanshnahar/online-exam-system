from PyQt6 import QtCore, QtWidgets, QtGui
import hashlib
from db_connection import create_connection
from styles import COMMON_STYLES

class LoginPage(QtWidgets.QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.initUI()

    def initUI(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(40, 20, 40, 20)
        layout.setSpacing(15)

        # Center content
        center_widget = QtWidgets.QWidget()
        center_layout = QtWidgets.QVBoxLayout(center_widget)
        center_layout.setContentsMargins(0, 40, 0, 40)
        center_layout.setSpacing(15)

        # Logo display
        logo_container = QtWidgets.QWidget()
        logo_layout = QtWidgets.QVBoxLayout(logo_container)
        logo_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        
        # Use the logo from main window if available
        if hasattr(self.main_window, 'logo_pixmap') and not self.main_window.logo_pixmap.isNull():
            logo_label = QtWidgets.QLabel()
            logo_label.setPixmap(self.main_window.logo_pixmap.scaled(
                300, 150, 
                QtCore.Qt.AspectRatioMode.KeepAspectRatio, 
                QtCore.Qt.TransformationMode.SmoothTransformation
            ))
            logo_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            logo_layout.addWidget(logo_label)
        else:
            # Fallback to text logo
            logo_label = QtWidgets.QLabel('Proctor Prime', self)
            logo_label.setStyleSheet('''
                font-size: 32px;
                color: #6C63FF;
                font-weight: bold;
                font-family: 'Script', cursive;
            ''')
            logo_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            logo_layout.addWidget(logo_label)
        
        center_layout.addWidget(logo_container)

        # Welcome text
        welcome_label = QtWidgets.QLabel('Welcome Back', self)
        welcome_label.setStyleSheet(COMMON_STYLES['title_label'])
        welcome_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(welcome_label)

        # User type selection
        type_label = QtWidgets.QLabel('Login As', self)
        type_label.setStyleSheet(COMMON_STYLES['field_label'])
        center_layout.addWidget(type_label)

        self.user_type_combo = QtWidgets.QComboBox(self)
        self.user_type_combo.addItems(['Student', 'Teacher', 'Admin'])
        self.user_type_combo.setStyleSheet(COMMON_STYLES['input_field'])
        center_layout.addWidget(self.user_type_combo)

        # Username field
        username_label = QtWidgets.QLabel('Username', self)
        username_label.setStyleSheet(COMMON_STYLES['field_label'])
        center_layout.addWidget(username_label)

        self.username = QtWidgets.QLineEdit(self)
        self.username.setPlaceholderText('Enter your username')
        self.username.setStyleSheet(COMMON_STYLES['input_field'])
        center_layout.addWidget(self.username)

        # Password field with forgot link
        password_header = QtWidgets.QHBoxLayout()
        password_label = QtWidgets.QLabel('Password', self)
        password_label.setStyleSheet(COMMON_STYLES['field_label'])
        forgot_link = QtWidgets.QLabel('<a href="#" style="' + COMMON_STYLES['link_text'] + '">Forgot?</a>', self)
        forgot_link.setOpenExternalLinks(False)
        password_header.addWidget(password_label)
        password_header.addStretch()
        password_header.addWidget(forgot_link)
        center_layout.addLayout(password_header)

        self.password = QtWidgets.QLineEdit(self)
        self.password.setPlaceholderText('Enter your password')
        self.password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.password.setStyleSheet(COMMON_STYLES['input_field'])
        center_layout.addWidget(self.password)

        # Login button
        self.login_button = QtWidgets.QPushButton('Login', self)
        self.login_button.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.login_button.clicked.connect(self.login)
        self.login_button.setStyleSheet(COMMON_STYLES['primary_button'])
        center_layout.addWidget(self.login_button)

        # Sign up link
        signup_text = QtWidgets.QLabel(
            'Don\'t have an account? <a href="#" style="color: #6C63FF; text-decoration: none;">, Sign up</a>', self)
        signup_text.setStyleSheet('color: #333333; font-size: 14px;')
        signup_text.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        signup_text.setOpenExternalLinks(False)  # This ensures internal handling
        signup_text.linkActivated.connect(self.go_to_signup)
        center_layout.addWidget(signup_text)

        # Add the centered content to main layout
        layout.addStretch()
        layout.addWidget(center_widget)
        layout.addStretch()

        self.setStyleSheet(COMMON_STYLES['window_background'])

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def login(self):
        username = self.username.text()
        password = self.password.text()
        user_type = self.user_type_combo.currentText()
        hashed_password = self.hash_password(password)

        try:
            supabase = create_connection()
            if not supabase:
                raise Exception("Failed to connect to Supabase")
                
            # Query the users table to find a matching user
            response = supabase.table('users') \
                .select('*') \
                .eq('username', username) \
                .eq('password', hashed_password) \
                .eq('user_type', user_type) \
                .execute()
                
            # Check if we got any results back
            if response.data and len(response.data) > 0:
                # Store user info in main window
                self.main_window.current_user = username
                self.main_window.current_user_type = user_type
                
                msg = QtWidgets.QMessageBox()
                msg.setStyleSheet(COMMON_STYLES['message_box'])
                msg.setWindowTitle("Success")
                msg.setText("Login successful!")
                msg.setIcon(QtWidgets.QMessageBox.Icon.Information)
                msg.exec()
                
                if user_type == 'Teacher':
                    self.main_window.teacher_dashboard.username = username  # Set username in teacher dashboard
                    self.main_window.stackedWidget.setCurrentWidget(self.main_window.teacher_dashboard)
                elif user_type == 'Student':
                    self.main_window.stackedWidget.setCurrentWidget(self.main_window.student_dashboard)
                elif user_type == 'Admin':
                    self.main_window.stackedWidget.setCurrentWidget(self.main_window.admin_dashboard)
            else:
                msg = QtWidgets.QMessageBox()
                msg.setStyleSheet(COMMON_STYLES['message_box'])
                msg.setWindowTitle("Error")
                msg.setText("Invalid username or password!")
                msg.setIcon(QtWidgets.QMessageBox.Icon.Warning)
                msg.exec()
        except Exception as e:
            msg = QtWidgets.QMessageBox()
            msg.setStyleSheet(COMMON_STYLES['message_box'])
            msg.setWindowTitle("Error")
            msg.setText(f"Login error: {str(e)}")
            msg.setIcon(QtWidgets.QMessageBox.Icon.Critical)
            msg.exec()

    def go_to_signup(self):
        self.main_window.stackedWidget.setCurrentWidget(self.main_window.signup_page)
