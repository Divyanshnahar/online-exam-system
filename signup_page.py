from PyQt6 import QtCore, QtWidgets, QtGui
import hashlib
from db_connection import create_connection
from styles import COMMON_STYLES

class SignupPage(QtWidgets.QWidget):
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

        # Title
        title_label = QtWidgets.QLabel('Create Account', self)
        title_label.setStyleSheet(COMMON_STYLES['title_label'])
        title_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(title_label)

        # User type selection
        type_label = QtWidgets.QLabel('Register As', self)
        type_label.setStyleSheet(COMMON_STYLES['field_label'])
        center_layout.addWidget(type_label)

        self.user_type_combo = QtWidgets.QComboBox(self)
        self.user_type_combo.addItems(['Student', 'Teacher'])  # Removed 'Admin' from options
        self.user_type_combo.setStyleSheet(COMMON_STYLES['input_field'])
        center_layout.addWidget(self.user_type_combo)

        # Input fields
        fields = [
            ('Username', 'Enter username', False),
            ('Password', 'Enter password', True),
            ('Confirm Password', 'Confirm your password', True)
        ]

        self.inputs = {}
        for label_text, placeholder, is_password in fields:
            label = QtWidgets.QLabel(label_text, self)
            label.setStyleSheet(COMMON_STYLES['field_label'])
            center_layout.addWidget(label)

            input_field = QtWidgets.QLineEdit(self)
            input_field.setPlaceholderText(placeholder)
            input_field.setStyleSheet(COMMON_STYLES['input_field'])
            if is_password:
                input_field.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
            center_layout.addWidget(input_field)
            self.inputs[label_text] = input_field

        # Sign up button
        self.signup_button = QtWidgets.QPushButton('Create Account', self)
        self.signup_button.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.signup_button.clicked.connect(self.signup)
        self.signup_button.setStyleSheet(COMMON_STYLES['primary_button'])
        center_layout.addWidget(self.signup_button)

        # Login link
        login_text = QtWidgets.QLabel(
            'Already have an account? <a href="#" style="color: #6C63FF; text-decoration: none;">, Login</a>', self)
        login_text.setStyleSheet('color: #333333; font-size: 14px;')
        login_text.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        login_text.setOpenExternalLinks(False)
        login_text.linkActivated.connect(self.go_to_login)
        center_layout.addWidget(login_text)

        # Add the centered content to main layout
        layout.addStretch()
        layout.addWidget(center_widget)
        layout.addStretch()

        self.setStyleSheet(COMMON_STYLES['window_background'])

    def signup(self):
        username = self.inputs['Username'].text()
        password = self.inputs['Password'].text()
        confirm_password = self.inputs['Confirm Password'].text()
        user_type = self.user_type_combo.currentText()

        # Validate inputs first
        if not all([username, password, confirm_password]):
            msg = QtWidgets.QMessageBox()
            msg.setStyleSheet(COMMON_STYLES['message_box'])
            msg.setWindowTitle("Error")
            msg.setText("Please fill in all fields!")
            msg.setIcon(QtWidgets.QMessageBox.Icon.Warning)
            msg.exec()
            return

        if password != confirm_password:
            msg = QtWidgets.QMessageBox()
            msg.setStyleSheet(COMMON_STYLES['message_box'])
            msg.setWindowTitle("Error")
            msg.setText("Passwords do not match!")
            msg.setIcon(QtWidgets.QMessageBox.Icon.Warning)
            msg.exec()
            return

        # If validation passes, proceed with database operation
        try:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            # Connect to Supabase
            supabase = create_connection()
            if not supabase:
                raise Exception("Failed to connect to Supabase")
                
            # Check if username already exists
            check_response = supabase.table('users') \
                .select('username') \
                .eq('username', username) \
                .execute()
                
            if check_response.data and len(check_response.data) > 0:
                msg = QtWidgets.QMessageBox()
                msg.setStyleSheet(COMMON_STYLES['message_box'])
                msg.setWindowTitle("Error")
                msg.setText("Username already exists. Please choose another username.")
                msg.setIcon(QtWidgets.QMessageBox.Icon.Warning)
                msg.exec()
                return
                
            # Insert the new user
            supabase.table('users').insert({
                'username': username,
                'password': hashed_password,
                'user_type': user_type
            }).execute()

            msg = QtWidgets.QMessageBox()
            msg.setStyleSheet(COMMON_STYLES['message_box'])
            msg.setWindowTitle("Success")
            msg.setText("Account created successfully!")
            msg.setIcon(QtWidgets.QMessageBox.Icon.Information)
            msg.exec()
            
            self.go_to_login()
            
        except Exception as e:
            msg = QtWidgets.QMessageBox()
            msg.setStyleSheet(COMMON_STYLES['message_box'])
            msg.setWindowTitle("Error")
            msg.setText(f"Signup error: {str(e)}")
            msg.setIcon(QtWidgets.QMessageBox.Icon.Critical)
            msg.exec()

    def go_to_login(self):
        self.main_window.stackedWidget.setCurrentWidget(self.main_window.login_page)
