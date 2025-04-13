from PyQt6 import QtWidgets, QtCore
from styles import COMMON_STYLES
from exam_creation import ExamCreation
from supabase_connection import create_connection
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

            def make_handler(t):
                def handler(_):
                    if t == 'Create Exam':
                        self.handle_action(t)
                    elif t == 'View Exams':
                        self.manage_existing_exam()
                    elif t == 'View Results':
                        self.check_student_result()
                    elif t == 'Manage Students':
                        self.view_student()
                return handler

            action_widget.mouseReleaseEvent = make_handler(title)


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
    
    def manage_existing_exam(self):
        # Create a new widget to display existing exams
        self.exams_widget = QtWidgets.QWidget()
        exams_layout = QtWidgets.QVBoxLayout(self.exams_widget)
        
        # Add header with back button
        header = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel('Your Exams')
        title.setStyleSheet(COMMON_STYLES['title_label'])
        
        back_btn = QtWidgets.QPushButton('Back to Dashboard')
        back_btn.setStyleSheet(COMMON_STYLES['secondary_button'])
        back_btn.clicked.connect(lambda: self.main_window.stackedWidget.setCurrentWidget(self))
        
        header.addWidget(title)
        header.addStretch()
        header.addWidget(back_btn)
        exams_layout.addLayout(header)
        
        # Add a container widget for the exams list
        self.exams_container = QtWidgets.QWidget()
        self.exams_container_layout = QtWidgets.QVBoxLayout(self.exams_container)
        exams_layout.addWidget(self.exams_container)
        
        # Load exams
        self.load_exams()
        
        exams_layout.addStretch()
        self.main_window.stackedWidget.addWidget(self.exams_widget)
        self.main_window.stackedWidget.setCurrentWidget(self.exams_widget)
    
    def load_exams(self):
        # Clear any existing content
        while self.exams_container_layout.count():
            item = self.exams_container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        try:
            supabase = create_connection()
            if not supabase:
                raise Exception("Failed to connect to Supabase")
            
            response = supabase.table('exams') \
                .select('id, name, status, exam_date, start_time, end_time') \
                .eq('teacher_username', self.main_window.current_user) \
                .execute()
            
            data = response.data
            if not data:
                no_exams_label = QtWidgets.QLabel("You haven't created any exams yet.")
                no_exams_label.setStyleSheet("font-size: 16px; color: #666; margin: 20px;")
                no_exams_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.exams_container_layout.addWidget(no_exams_label)
                return
            
            # Create a scroll area for the exams
            scroll_area = QtWidgets.QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_widget = QtWidgets.QWidget()
            scroll_layout = QtWidgets.QVBoxLayout(scroll_widget)
            scroll_layout.setSpacing(10)
            
            for exam in data:
                exam_card = QtWidgets.QWidget()
                exam_card.setStyleSheet('''
                    QWidget {
                        background: white;
                        border-radius: 10px;
                        padding: 15px;
                        margin: 5px;
                        border: 1px solid #E0E0E0;
                    }
                ''')
                card_layout = QtWidgets.QVBoxLayout(exam_card)
                
                name_label = QtWidgets.QLabel(f"Name: {exam['name']}")
                name_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
                
                id_label = QtWidgets.QLabel(f"ID: {exam['id']}")
                id_label.setStyleSheet("font-size: 14px; color: #666;")
                
                status_label = QtWidgets.QLabel(f"Status: {exam['status']}")
                status_label.setStyleSheet("font-size: 14px; color: #666;")
                
                date_label = QtWidgets.QLabel(f"Date: {exam['exam_date']}")
                date_label.setStyleSheet("font-size: 14px; color: #666;")
                
                time_label = QtWidgets.QLabel(f"Time: {exam['start_time']} - {exam['end_time']}")
                time_label.setStyleSheet("font-size: 14px; color: #666;")
                
                card_layout.addWidget(name_label)
                card_layout.addWidget(id_label)
                card_layout.addWidget(status_label)
                card_layout.addWidget(date_label)
                card_layout.addWidget(time_label)
                
                scroll_layout.addWidget(exam_card)
            
            scroll_area.setWidget(scroll_widget)
            self.exams_container_layout.addWidget(scroll_area)
            
        except Exception as e:
            error_label = QtWidgets.QLabel(f"Failed to fetch exams: {str(e)}")
            error_label.setStyleSheet("font-size: 14px; color: red; margin: 20px;")
            self.exams_container_layout.addWidget(error_label)

    def check_student_result(self):
        # Create a new widget to display results
        self.results_widget = QtWidgets.QWidget()
        results_layout = QtWidgets.QVBoxLayout(self.results_widget)
        
        # Add header with back button
        header = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel('Student Results')
        title.setStyleSheet(COMMON_STYLES['title_label'])
        
        back_btn = QtWidgets.QPushButton('Back to Dashboard')
        back_btn.setStyleSheet(COMMON_STYLES['secondary_button'])
        back_btn.clicked.connect(lambda: self.main_window.stackedWidget.setCurrentWidget(self))
        
        header.addWidget(title)
        header.addStretch()
        header.addWidget(back_btn)
        results_layout.addLayout(header)
        
        # Add a container widget for the results list
        self.results_container = QtWidgets.QWidget()
        self.results_container_layout = QtWidgets.QVBoxLayout(self.results_container)
        results_layout.addWidget(self.results_container)
        
        # Load results
        self.load_results()
        
        results_layout.addStretch()
        self.main_window.stackedWidget.addWidget(self.results_widget)
        self.main_window.stackedWidget.setCurrentWidget(self.results_widget)
    
    def load_results(self):
        # Clear any existing content
        while self.results_container_layout.count():
            item = self.results_container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        try:
            supabase = create_connection()
            if not supabase:
                raise Exception("Failed to connect to Supabase")
            
            # Step 1: Get exams created by the teacher
            exams_response = supabase.table('exams') \
                .select('id, name') \
                .eq('teacher_username', self.main_window.current_user) \
                .execute()
            
            exam_ids = [e['id'] for e in exams_response.data]
            exam_names = {e['id']: e['name'] for e in exams_response.data}
            
            if not exam_ids:
                no_exams_label = QtWidgets.QLabel("You haven't created any exams yet.")
                no_exams_label.setStyleSheet("font-size: 16px; color: #666; margin: 20px;")
                no_exams_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.results_container_layout.addWidget(no_exams_label)
                return
            
            # Step 2: Fetch results for those exams
            results_response = supabase.table('exam_results') \
                .select('exam_id, student_username, score') \
                .in_('exam_id', exam_ids) \
                .execute()
            
            if not results_response.data:
                no_results_label = QtWidgets.QLabel("No students have submitted results yet.")
                no_results_label.setStyleSheet("font-size: 16px; color: #666; margin: 20px;")
                no_results_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.results_container_layout.addWidget(no_results_label)
                return
            
            # Create a scroll area for the results
            scroll_area = QtWidgets.QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_widget = QtWidgets.QWidget()
            scroll_layout = QtWidgets.QVBoxLayout(scroll_widget)
            scroll_layout.setSpacing(10)
            
            for result in results_response.data:
                exam_name = exam_names.get(result['exam_id'], 'Unknown')
                result_card = QtWidgets.QWidget()
                result_card.setStyleSheet('''
                    QWidget {
                        background: white;
                        border-radius: 10px;
                        padding: 15px;
                        margin: 5px;
                        border: 1px solid #E0E0E0;
                    }
                ''')
                card_layout = QtWidgets.QVBoxLayout(result_card)
                
                exam_label = QtWidgets.QLabel(f"Exam: {exam_name}")
                exam_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
                
                student_label = QtWidgets.QLabel(f"Student: {result['student_username']}")
                student_label.setStyleSheet("font-size: 14px; color: #666;")
                
                score_label = QtWidgets.QLabel(f"Score: {result['score']}")
                score_label.setStyleSheet("font-size: 14px; color: #666;")
                
                card_layout.addWidget(exam_label)
                card_layout.addWidget(student_label)
                card_layout.addWidget(score_label)
                
                scroll_layout.addWidget(result_card)
            
            scroll_area.setWidget(scroll_widget)
            self.results_container_layout.addWidget(scroll_area)
            
        except Exception as e:
            error_label = QtWidgets.QLabel(f"Failed to fetch results: {str(e)}")
            error_label.setStyleSheet("font-size: 14px; color: red; margin: 20px;")
            self.results_container_layout.addWidget(error_label)

    def view_student(self):
        # Create a new widget to display students
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
            supabase = create_connection()
            if not supabase:
                raise Exception("Failed to connect to Supabase")
            
            response = supabase.table('users') \
                .select('username') \
                .eq('user_type', 'Student') \
                .execute()
            
            if not response.data:
                no_students_label = QtWidgets.QLabel("No students found in the system.")
                no_students_label.setStyleSheet("font-size: 16px; color: #666; margin: 20px;")
                no_students_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.students_container_layout.addWidget(no_students_label)
                return
            
            # Create a scroll area for the students
            scroll_area = QtWidgets.QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_widget = QtWidgets.QWidget()
            scroll_layout = QtWidgets.QVBoxLayout(scroll_widget)
            scroll_layout.setSpacing(10)
            
            for user in response.data:
                student_card = QtWidgets.QWidget()
                student_card.setStyleSheet('''
                    QWidget {
                        background: white;
                        border-radius: 10px;
                        padding: 15px;
                        margin: 5px;
                        border: 1px solid #E0E0E0;
                    }
                ''')
                card_layout = QtWidgets.QVBoxLayout(student_card)
                
                username_label = QtWidgets.QLabel(f"Username: {user['username']}")
                username_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
                
                card_layout.addWidget(username_label)
                scroll_layout.addWidget(student_card)
            
            scroll_area.setWidget(scroll_widget)
            self.students_container_layout.addWidget(scroll_area)
            
        except Exception as e:
            error_label = QtWidgets.QLabel(f"Failed to fetch students: {str(e)}")
            error_label.setStyleSheet("font-size: 14px; color: red; margin: 20px;")
            self.students_container_layout.addWidget(error_label)