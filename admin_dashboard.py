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
        
        logout_btn = QtWidgets.QPushButton('Logout', self)
        logout_btn.setStyleSheet(COMMON_STYLES['secondary_button'])
        logout_btn.clicked.connect(self.logout)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(logout_btn)
        layout.addLayout(header)

        # Main Content
        content = QtWidgets.QHBoxLayout()
        
        # Left Panel - Navigation
        nav_panel = QtWidgets.QVBoxLayout()
        manage_students_btn = QtWidgets.QPushButton('Manage Students', self)
        manage_teachers_btn = QtWidgets.QPushButton('Manage Teachers', self)
        # system_settings_btn = QtWidgets.QPushButton('System Settings', self)
        # view_logs_btn = QtWidgets.QPushButton('View Logs', self)
        
        # Connect button actions
        manage_students_btn.clicked.connect(self.manage_students)
        manage_teachers_btn.clicked.connect(self.manage_teachers)
        
        for btn in [manage_students_btn, manage_teachers_btn]:
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
        
    def manage_students(self):
        # Create a new widget to display all students
        self.students_widget = QtWidgets.QWidget()
        students_layout = QtWidgets.QVBoxLayout(self.students_widget)
        
        # Add header with back button
        header = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel('Manage Students')
        title.setStyleSheet(COMMON_STYLES['title_label'])
        
        back_btn = QtWidgets.QPushButton('Back to Dashboard')
        back_btn.setStyleSheet(COMMON_STYLES['secondary_button'])
        back_btn.clicked.connect(lambda: self.main_window.stackedWidget.setCurrentWidget(self))
        
        header.addWidget(title)
        header.addStretch()
        header.addWidget(back_btn)
        students_layout.addLayout(header)
        
        # Add a container widget for the students list
        self.students_container = QtWidgets.QWidget()
        self.students_container_layout = QtWidgets.QVBoxLayout(self.students_container)
        students_layout.addWidget(self.students_container)
        
        # Load students
        self.load_students()
        
        students_layout.addStretch()
        self.main_window.stackedWidget.addWidget(self.students_widget)
        self.main_window.stackedWidget.setCurrentWidget(self.students_widget)
    
    def load_students(self):
        # Clear any existing content
        while self.students_container_layout.count():
            item = self.students_container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        try:
            from supabase_connection import create_connection
            supabase = create_connection()
            if not supabase:
                raise Exception("Failed to connect to Supabase")
            
            # Fetch all students
            response = supabase.table('users') \
                .select('username') \
                .eq('user_type', 'Student') \
                .execute()
            
            data = response.data
            if not data:
                no_students_label = QtWidgets.QLabel("No students found in the system.")
                no_students_label.setStyleSheet("font-size: 16px; color: #666; margin: 20px;")
                no_students_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.students_container_layout.addWidget(no_students_label)
                return
            
            # Add search
            search_layout = QtWidgets.QHBoxLayout()
            search_box = QtWidgets.QLineEdit()
            search_box.setPlaceholderText("Search students...")
            search_box.setStyleSheet("padding: 8px; border: 1px solid #ccc; border-radius: 4px;")
            search_box.textChanged.connect(lambda text: self.filter_students(text, data))
            
            search_layout.addWidget(search_box)
            self.students_container_layout.addLayout(search_layout)
            
            # Stats section
            stats_widget = QtWidgets.QWidget()
            stats_widget.setStyleSheet("background: #F8F9FA; border-radius: 8px; padding: 15px; margin-top: 10px;")
            stats_layout = QtWidgets.QHBoxLayout(stats_widget)
            
            total_students = len(data)
            
            students_count = QtWidgets.QLabel(f"Total Students: {total_students}")
            students_count.setStyleSheet("font-size: 14px; font-weight: bold;")
            
            stats_layout.addWidget(students_count)
            stats_layout.addStretch()
            
            self.students_container_layout.addWidget(stats_widget)
            
            # Create a scroll area for the students
            scroll_area = QtWidgets.QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_widget = QtWidgets.QWidget()
            scroll_layout = QtWidgets.QVBoxLayout(scroll_widget)
            scroll_layout.setSpacing(10)
            
            # Store the scroll layout and data for filtering
            self.students_scroll_layout = scroll_layout
            self.students_data = data
            
            self.display_students(data, scroll_layout)
            
            scroll_area.setWidget(scroll_widget)
            self.students_container_layout.addWidget(scroll_area)
            
        except Exception as e:
            error_label = QtWidgets.QLabel(f"Failed to fetch students: {str(e)}")
            error_label.setStyleSheet("font-size: 14px; color: red; margin: 20px;")
            self.students_container_layout.addWidget(error_label)
    
    def display_students(self, students_data, layout):
        """Display the student cards in the layout"""
        # Clear the layout first
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        for student in students_data:
            student_card = QtWidgets.QWidget()
            student_card.setStyleSheet('''
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
            card_layout = QtWidgets.QHBoxLayout(student_card)
            
            # Student info
            info_layout = QtWidgets.QVBoxLayout()
            username_label = QtWidgets.QLabel(f"Username: {student['username']}")
            username_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
            info_layout.addWidget(username_label)
            
            # Action buttons
            buttons_layout = QtWidgets.QHBoxLayout()
            
            edit_btn = QtWidgets.QPushButton("Edit")
            edit_btn.setStyleSheet(COMMON_STYLES['secondary_button'])
            edit_btn.clicked.connect(lambda checked, s=student: self.edit_student(s))
            
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
            remove_btn.clicked.connect(lambda checked, s=student: self.remove_student(s))
            
            buttons_layout.addWidget(edit_btn)
            buttons_layout.addWidget(remove_btn)
            
            card_layout.addLayout(info_layout)
            card_layout.addStretch()
            card_layout.addLayout(buttons_layout)
            
            layout.addWidget(student_card)
        
        # Add "Add Student" button at the bottom
        add_student_btn = QtWidgets.QPushButton("+ Add New Student")
        add_student_btn.setStyleSheet(COMMON_STYLES['primary_button'])
        add_student_btn.setMinimumHeight(40)
        add_student_btn.clicked.connect(self.add_new_student)
        layout.addWidget(add_student_btn)
    
    def filter_students(self, search_text, students_data):
        """Filter students based on search text"""
        if not search_text:
            # If search text is empty, show all students
            self.display_students(students_data, self.students_scroll_layout)
            return
        
        # Filter students based on search text
        filtered_students = []
        search_text = search_text.lower()
        
        for student in students_data:
            if search_text in student['username'].lower():
                filtered_students.append(student)
        
        # Display filtered students
        self.display_students(filtered_students, self.students_scroll_layout)
    
    def add_new_student(self):
        """Add a new student to the system"""
        # Create a dialog for adding a new student
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Add New Student")
        dialog.setMinimumWidth(400)
        dialog.setStyleSheet("background-color: white; color: black;")
        
        layout = QtWidgets.QVBoxLayout(dialog)
        
        # Form fields
        form_layout = QtWidgets.QFormLayout()
        
        username_input = QtWidgets.QLineEdit()
        username_input.setPlaceholderText("Enter username")
        username_input.setStyleSheet("padding: 8px; border: 1px solid #ccc; border-radius: 4px;")
        
        password_input = QtWidgets.QLineEdit()
        password_input.setPlaceholderText("Enter password")
        password_input.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        password_input.setStyleSheet("padding: 8px; border: 1px solid #ccc; border-radius: 4px;")
        
        form_layout.addRow("Username:", username_input)
        form_layout.addRow("Password:", password_input)
        
        layout.addLayout(form_layout)
        
        # Error message label
        error_label = QtWidgets.QLabel("")
        error_label.setStyleSheet("color: red; margin-top: 10px;")
        error_label.setVisible(False)
        layout.addWidget(error_label)
        
        # Buttons
        buttons_layout = QtWidgets.QHBoxLayout()
        
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.setStyleSheet(COMMON_STYLES['secondary_button'])
        cancel_btn.clicked.connect(dialog.reject)
        
        save_btn = QtWidgets.QPushButton("Save")
        save_btn.setStyleSheet(COMMON_STYLES['primary_button'])
        
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(save_btn)
        
        layout.addLayout(buttons_layout)
        
        # Handle save button click
        def save_student():
            username = username_input.text().strip()
            password = password_input.text().strip()
            
            # Validate inputs
            if not username or not password:
                error_label.setText("Username and password are required")
                error_label.setVisible(True)
                return
            
            if len(password) < 8:
                error_label.setText("Password must be at least 8 characters")
                error_label.setVisible(True)
                return
            
            try:
                from supabase_connection import create_connection
                import hashlib
                
                supabase = create_connection()
                
                # Check if username already exists
                response = supabase.table('users').select('username').eq('username', username).execute()
                if response.data:
                    error_label.setText("Username already exists")
                    error_label.setVisible(True)
                    return
                
                # Hash the password
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                
                # Create new student
                new_student = {
                    'username': username,
                    'password': hashed_password,
                    'user_type': 'Student'
                }
                
                response = supabase.table('users').insert(new_student).execute()
                
                # Reload students
                self.load_students()
                
                # Close dialog
                dialog.accept()
                
            except Exception as e:
                error_label.setText(f"Error: {str(e)}")
                error_label.setVisible(True)
        
        save_btn.clicked.connect(save_student)
        
        # Show dialog
        dialog.exec()
    
    def edit_student(self, student):
        """Edit an existing student"""
        # Create a dialog for editing a student
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle(f"Edit Student: {student['username']}")
        dialog.setMinimumWidth(400)
        dialog.setStyleSheet("background-color: white; color: black;")
        
        layout = QtWidgets.QVBoxLayout(dialog)
        
        # Form fields
        form_layout = QtWidgets.QFormLayout()
        
        username_input = QtWidgets.QLineEdit(student['username'])
        username_input.setReadOnly(True)  # Username cannot be changed
        username_input.setStyleSheet("padding: 8px; border: 1px solid #ccc; border-radius: 4px; background-color: #f0f0f0;")
        
        password_input = QtWidgets.QLineEdit()
        password_input.setPlaceholderText("Enter new password (leave blank to keep current)")
        password_input.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        password_input.setStyleSheet("padding: 8px; border: 1px solid #ccc; border-radius: 4px;")
        
        form_layout.addRow("Username:", username_input)
        form_layout.addRow("New Password:", password_input)
        
        layout.addLayout(form_layout)
        
        # Error message label
        error_label = QtWidgets.QLabel("")
        error_label.setStyleSheet("color: red; margin-top: 10px;")
        error_label.setVisible(False)
        layout.addWidget(error_label)
        
        # Buttons
        buttons_layout = QtWidgets.QHBoxLayout()
        
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.setStyleSheet(COMMON_STYLES['secondary_button'])
        cancel_btn.clicked.connect(dialog.reject)
        
        save_btn = QtWidgets.QPushButton("Save")
        save_btn.setStyleSheet(COMMON_STYLES['primary_button'])
        
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(save_btn)
        
        layout.addLayout(buttons_layout)
        
        # Handle save button click
        def save_student_changes():
            password = password_input.text().strip()
            
            # Validate password if provided
            if password and len(password) < 8:
                error_label.setText("Password must be at least 8 characters")
                error_label.setVisible(True)
                return
            
            try:
                from supabase_connection import create_connection
                import hashlib
                
                supabase = create_connection()
                
                # Only update if password is provided
                if password:
                    # Hash the password
                    hashed_password = hashlib.sha256(password.encode()).hexdigest()
                    
                    # Update student's password
                    response = supabase.table('users').update({'password': hashed_password}).eq('username', student['username']).execute()
                    
                    # Reload students
                    self.load_students()
                    
                    # Close dialog
                    dialog.accept()
                else:
                    error_label.setText("No changes to save")
                    error_label.setVisible(True)
                
            except Exception as e:
                error_label.setText(f"Error: {str(e)}")
                error_label.setVisible(True)
        
        save_btn.clicked.connect(save_student_changes)
        
        # Show dialog
        dialog.exec()
    
    def remove_student(self, student):
        """Remove a student from the system"""
        # Confirm deletion
        confirm = QtWidgets.QMessageBox(self)
        confirm.setWindowTitle("Confirm Deletion")
        confirm.setText(f"Are you sure you want to remove student '{student['username']}'?")
        confirm.setInformativeText("This action cannot be undone.")
        confirm.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        confirm.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
        confirm.setDefaultButton(QtWidgets.QMessageBox.StandardButton.No)
        confirm.setStyleSheet("color: black;")  # Ensure text is visible
        
        if confirm.exec() == QtWidgets.QMessageBox.StandardButton.Yes:
            try:
                from supabase_connection import create_connection
                
                supabase = create_connection()
                
                # Delete student
                response = supabase.table('users').delete().eq('username', student['username']).execute()
                
                # Reload students
                self.load_students()
                
            except Exception as e:
                error = QtWidgets.QMessageBox(self)
                error.setWindowTitle("Error")
                error.setText(f"Failed to remove student: {str(e)}")
                error.setIcon(QtWidgets.QMessageBox.Icon.Critical)
                error.setStyleSheet("color: black;")  # Ensure text is visible
                error.exec()
    
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
            search_box.textChanged.connect(lambda text: self.filter_teachers(text, data))
            
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
            
            # Store the scroll layout and data for filtering
            self.teachers_scroll_layout = scroll_layout
            self.teachers_data = data
            
            self.display_teachers(data, scroll_layout)
            
            scroll_area.setWidget(scroll_widget)
            self.teachers_container_layout.addWidget(scroll_area)
            
        except Exception as e:
            error_label = QtWidgets.QLabel(f"Failed to fetch teachers: {str(e)}")
            error_label.setStyleSheet("font-size: 14px; color: red; margin: 20px;")
            self.teachers_container_layout.addWidget(error_label)
    
    def display_teachers(self, teachers_data, layout):
        """Display the teacher cards in the layout"""
        # Clear the layout first
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        for teacher in teachers_data:
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
            
            edit_btn = QtWidgets.QPushButton("Edit")
            edit_btn.setStyleSheet(COMMON_STYLES['secondary_button'])
            edit_btn.clicked.connect(lambda checked, t=teacher: self.edit_teacher(t))
            
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
            remove_btn.clicked.connect(lambda checked, t=teacher: self.remove_teacher(t))
            
            buttons_layout.addWidget(edit_btn)
            buttons_layout.addWidget(remove_btn)
            
            card_layout.addLayout(info_layout)
            card_layout.addStretch()
            card_layout.addLayout(buttons_layout)
            
            layout.addWidget(teacher_card)
        
        # Add "Add Teacher" button at the bottom
        add_teacher_btn = QtWidgets.QPushButton("+ Add New Teacher")
        add_teacher_btn.setStyleSheet(COMMON_STYLES['primary_button'])
        add_teacher_btn.setMinimumHeight(40)
        add_teacher_btn.clicked.connect(self.add_new_teacher)
        layout.addWidget(add_teacher_btn)
    
    def filter_teachers(self, search_text, teachers_data):
        """Filter teachers based on search text"""
        if not search_text:
            # If search text is empty, show all teachers
            self.display_teachers(teachers_data, self.teachers_scroll_layout)
            return
        
        # Filter teachers based on search text
        filtered_teachers = []
        search_text = search_text.lower()
        
        for teacher in teachers_data:
            if search_text in teacher['username'].lower():
                filtered_teachers.append(teacher)
        
        # Display filtered teachers
        self.display_teachers(filtered_teachers, self.teachers_scroll_layout)
    
    def add_new_teacher(self):
        """Add a new teacher to the system"""
        # Create a dialog for adding a new teacher
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Add New Teacher")
        dialog.setMinimumWidth(400)
        dialog.setStyleSheet("background-color: white; color: black;")
        
        layout = QtWidgets.QVBoxLayout(dialog)
        
        # Form fields
        form_layout = QtWidgets.QFormLayout()
        
        username_input = QtWidgets.QLineEdit()
        username_input.setPlaceholderText("Enter username")
        username_input.setStyleSheet("padding: 8px; border: 1px solid #ccc; border-radius: 4px;")
        
        password_input = QtWidgets.QLineEdit()
        password_input.setPlaceholderText("Enter password")
        password_input.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        password_input.setStyleSheet("padding: 8px; border: 1px solid #ccc; border-radius: 4px;")
        
        form_layout.addRow("Username:", username_input)
        form_layout.addRow("Password:", password_input)
        
        layout.addLayout(form_layout)
        
        # Error message label
        error_label = QtWidgets.QLabel("")
        error_label.setStyleSheet("color: red; margin-top: 10px;")
        error_label.setVisible(False)
        layout.addWidget(error_label)
        
        # Buttons
        buttons_layout = QtWidgets.QHBoxLayout()
        
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.setStyleSheet(COMMON_STYLES['secondary_button'])
        cancel_btn.clicked.connect(dialog.reject)
        
        save_btn = QtWidgets.QPushButton("Save")
        save_btn.setStyleSheet(COMMON_STYLES['primary_button'])
        
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(save_btn)
        
        layout.addLayout(buttons_layout)
        
        # Handle save button click
        def save_teacher():
            username = username_input.text().strip()
            password = password_input.text().strip()
            
            # Validate inputs
            if not username or not password:
                error_label.setText("Username and password are required")
                error_label.setVisible(True)
                return
            
            if len(password) < 8:
                error_label.setText("Password must be at least 8 characters")
                error_label.setVisible(True)
                return
            
            try:
                from supabase_connection import create_connection
                import hashlib
                
                supabase = create_connection()
                
                # Check if username already exists
                response = supabase.table('users').select('username').eq('username', username).execute()
                if response.data:
                    error_label.setText("Username already exists")
                    error_label.setVisible(True)
                    return
                
                # Hash the password
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                
                # Create new teacher
                new_teacher = {
                    'username': username,
                    'password': hashed_password,
                    'user_type': 'Teacher'
                }
                
                response = supabase.table('users').insert(new_teacher).execute()
                
                # Reload teachers
                self.load_teachers()
                
                # Close dialog
                dialog.accept()
                
            except Exception as e:
                error_label.setText(f"Error: {str(e)}")
                error_label.setVisible(True)
        
        save_btn.clicked.connect(save_teacher)
        
        # Show dialog
        dialog.exec()
    
    def edit_teacher(self, teacher):
        """Edit an existing teacher"""
        # Create a dialog for editing a teacher
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle(f"Edit Teacher: {teacher['username']}")
        dialog.setMinimumWidth(400)
        dialog.setStyleSheet("background-color: white; color: black;")
        
        layout = QtWidgets.QVBoxLayout(dialog)
        
        # Form fields
        form_layout = QtWidgets.QFormLayout()
        
        username_input = QtWidgets.QLineEdit(teacher['username'])
        username_input.setReadOnly(True)  # Username cannot be changed
        username_input.setStyleSheet("padding: 8px; border: 1px solid #ccc; border-radius: 4px; background-color: #f0f0f0;")
        
        password_input = QtWidgets.QLineEdit()
        password_input.setPlaceholderText("Enter new password (leave blank to keep current)")
        password_input.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        password_input.setStyleSheet("padding: 8px; border: 1px solid #ccc; border-radius: 4px;")
        
        form_layout.addRow("Username:", username_input)
        form_layout.addRow("New Password:", password_input)
        
        layout.addLayout(form_layout)
        
        # Error message label
        error_label = QtWidgets.QLabel("")
        error_label.setStyleSheet("color: red; margin-top: 10px;")
        error_label.setVisible(False)
        layout.addWidget(error_label)
        
        # Buttons
        buttons_layout = QtWidgets.QHBoxLayout()
        
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.setStyleSheet(COMMON_STYLES['secondary_button'])
        cancel_btn.clicked.connect(dialog.reject)
        
        save_btn = QtWidgets.QPushButton("Save")
        save_btn.setStyleSheet(COMMON_STYLES['primary_button'])
        
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(save_btn)
        
        layout.addLayout(buttons_layout)
        
        # Handle save button click
        def save_teacher_changes():
            password = password_input.text().strip()
            
            # Validate password if provided
            if password and len(password) < 8:
                error_label.setText("Password must be at least 8 characters")
                error_label.setVisible(True)
                return
            
            try:
                from supabase_connection import create_connection
                import hashlib
                
                supabase = create_connection()
                
                # Only update if password is provided
                if password:
                    # Hash the password
                    hashed_password = hashlib.sha256(password.encode()).hexdigest()
                    
                    # Update teacher's password
                    response = supabase.table('users').update({'password': hashed_password}).eq('username', teacher['username']).execute()
                    
                    # Reload teachers
                    self.load_teachers()
                    
                    # Close dialog
                    dialog.accept()
                else:
                    error_label.setText("No changes to save")
                    error_label.setVisible(True)
                
            except Exception as e:
                error_label.setText(f"Error: {str(e)}")
                error_label.setVisible(True)
        
        save_btn.clicked.connect(save_teacher_changes)
        
        # Show dialog
        dialog.exec()
    
    def remove_teacher(self, teacher):
        """Remove a teacher from the system"""
        # Confirm deletion
        confirm = QtWidgets.QMessageBox(self)
        confirm.setWindowTitle("Confirm Deletion")
        confirm.setText(f"Are you sure you want to remove teacher '{teacher['username']}'?")
        confirm.setInformativeText("This action cannot be undone.")
        confirm.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        confirm.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
        confirm.setDefaultButton(QtWidgets.QMessageBox.StandardButton.No)
        confirm.setStyleSheet("color: black;")  # Ensure text is visible
        
        if confirm.exec() == QtWidgets.QMessageBox.StandardButton.Yes:
            try:
                from supabase_connection import create_connection
                
                supabase = create_connection()
                
                # Delete teacher
                response = supabase.table('users').delete().eq('username', teacher['username']).execute()
                
                # Reload teachers
                self.load_teachers()
                
            except Exception as e:
                error = QtWidgets.QMessageBox(self)
                error.setWindowTitle("Error")
                error.setText(f"Failed to remove teacher: {str(e)}")
                error.setIcon(QtWidgets.QMessageBox.Icon.Critical)
                error.setStyleSheet("color: black;")  # Ensure text is visible
                error.exec()