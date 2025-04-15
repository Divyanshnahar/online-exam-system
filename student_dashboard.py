from PyQt6 import QtCore, QtWidgets
from styles import COMMON_STYLES
from supabase_connection import create_connection
from exam_taking import ExamTaking
from exam_disclaimer import ExamDisclaimerPage
import datetime
import logging

class StudentDashboard(QtWidgets.QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.initUI()

    def initUI(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(40, 20, 40, 20)
        layout.setSpacing(20)

        # Header section
        header_widget = QtWidgets.QWidget()
        header_layout = QtWidgets.QHBoxLayout(header_widget)
        
        title_label = QtWidgets.QLabel('Student Dashboard', self)
        title_label.setStyleSheet(COMMON_STYLES['title_label'])
        
        logout_btn = QtWidgets.QPushButton('Logout', self)
        logout_btn.setStyleSheet(COMMON_STYLES['secondary_button'])
        logout_btn.clicked.connect(self.logout)
        logout_btn.setFixedWidth(100)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(logout_btn)
        layout.addWidget(header_widget)

        # Welcome message
        welcome_label = QtWidgets.QLabel('Welcome back, Student!', self)
        welcome_label.setStyleSheet('font-size: 18px; color: #666;')
        layout.addWidget(welcome_label)

        # Main actions
        actions_widget = QtWidgets.QWidget()
        actions_layout = QtWidgets.QGridLayout(actions_widget)
        actions_layout.setSpacing(15)

        actions = [
            ('Take Exams', 'Take available exams', self.show_exams),
            ('My Results', 'View your exam results', self.show_results),
            ('Profile', 'Update your information', self.show_profile),
            ('Resources', 'Access study materials', self.show_resources)
        ]

        for i, (title, desc, action) in enumerate(actions):
            card = self.create_action_card(title, desc)
            if action:
                card.mouseReleaseEvent = lambda event, act=action: act()
            actions_layout.addWidget(card, i // 2, i % 2)

        layout.addWidget(actions_widget)
        layout.addStretch()
        self.setStyleSheet(COMMON_STYLES['window_background'])

    def create_action_card(self, title, description):
        card = QtWidgets.QWidget()
        card.setStyleSheet('''
            QWidget {
                background: white;
                border-radius: 10px;
                padding: 15px;
            }
            QWidget:hover {
                background: #F5F5FF;
            }
        ''')
        card_layout = QtWidgets.QVBoxLayout(card)
        
        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet('font-size: 16px; font-weight: bold; color: #333;')
        
        desc_label = QtWidgets.QLabel(description)
        desc_label.setStyleSheet('color: #666; font-size: 13px;')
        
        card_layout.addWidget(title_label)
        card_layout.addWidget(desc_label)
        
        return card

    def logout(self):
        self.main_window.stackedWidget.setCurrentWidget(self.main_window.login_page)

    def show_exams(self):
        # Create a new widget to display exams
        self.exams_widget = QtWidgets.QWidget()
        exams_layout = QtWidgets.QVBoxLayout(self.exams_widget)
        
        # Add header with back and reload buttons
        header = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel('Available Exams')
        title.setStyleSheet(COMMON_STYLES['title_label'])
        
        buttons_layout = QtWidgets.QHBoxLayout()
        
        reload_btn = QtWidgets.QPushButton('🔄 Reload')
        reload_btn.setStyleSheet(COMMON_STYLES['secondary_button'])
        reload_btn.clicked.connect(self.reload_exams)
        reload_btn.setToolTip("Refresh the list of available exams")
        
        back_btn = QtWidgets.QPushButton('Back to Dashboard')
        back_btn.setStyleSheet(COMMON_STYLES['secondary_button'])
        back_btn.clicked.connect(lambda: self.main_window.stackedWidget.setCurrentWidget(self))
        
        buttons_layout.addWidget(reload_btn)
        buttons_layout.addWidget(back_btn)
        
        header.addWidget(title)
        header.addStretch()
        header.addLayout(buttons_layout)
        exams_layout.addLayout(header)
        
        # Add a container widget for the exam list that can be updated
        self.exams_container = QtWidgets.QWidget()
        self.exams_container_layout = QtWidgets.QVBoxLayout(self.exams_container)
        exams_layout.addWidget(self.exams_container)
        
        # Load exams initially
        self.load_exams()
        
        exams_layout.addStretch()
        self.main_window.stackedWidget.addWidget(self.exams_widget)
        self.main_window.stackedWidget.setCurrentWidget(self.exams_widget)
    
    def reload_exams(self):
        # Clear the current exams
        self.clear_exams_container()
        
        # Show loading indicator
        loading_label = QtWidgets.QLabel("Loading exams...")
        loading_label.setStyleSheet("font-size: 14px; color: #666; margin: 10px;")
        loading_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.exams_container_layout.addWidget(loading_label)
        
        # Use a short timer to allow the UI to update before loading exams
        QtCore.QTimer.singleShot(100, self.load_exams)
    
    def clear_exams_container(self):
        # Clear all widgets from the exams container
        while self.exams_container_layout.count():
            item = self.exams_container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def load_exams(self):
        # Clear any existing content
        self.clear_exams_container()
        
        # Get current date and time
        current_date = datetime.date.today().isoformat()  # Convert to ISO format for Supabase
        current_time = datetime.datetime.now().time().strftime('%H:%M:%S')  # Format time for comparison
        
        # Fetch exams from the database that are active and scheduled for today
        try:
            supabase = create_connection()
            if not supabase:
                raise Exception("Failed to connect to Supabase")
            
            # Query for exams that are:
            # 1. Active
            # 2. Scheduled for today
            # 3. Not attempted by the current student
            
            # First get all exams for today
            exams_response = supabase.table('exams') \
                .select('id, name, duration, start_time, end_time') \
                .eq('status', 'active') \
                .eq('exam_date', current_date) \
                .execute()
                
            if not exams_response.data:
                no_exams_label = QtWidgets.QLabel("No exams scheduled for today.")
                no_exams_label.setStyleSheet("font-size: 16px; color: #666; margin: 20px;")
                no_exams_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.exams_container_layout.addWidget(no_exams_label)
                return
                
            # Now check which ones the student hasn't taken yet
            available_exams = []
            for exam in exams_response.data:
                # Check if student already attempted this exam
                result_response = supabase.table('exam_results') \
                    .select('id') \
                    .eq('exam_id', exam['id']) \
                    .eq('student_username', self.main_window.current_user) \
                    .execute()
                    
                if not result_response.data:  # No results found, exam is available
                    available_exams.append(exam)
            
            if not available_exams:
                no_exams_label = QtWidgets.QLabel("No exams available for you today.")
                no_exams_label.setStyleSheet("font-size: 16px; color: #666; margin: 20px;")
                no_exams_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.exams_container_layout.addWidget(no_exams_label)
                return
                
            # Section headers
            available_now_label = QtWidgets.QLabel("Available Now")
            available_now_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #6C63FF; margin-top: 10px;")
            
            upcoming_label = QtWidgets.QLabel("Upcoming Today")
            upcoming_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #6C63FF; margin-top: 20px;")
            
            expired_label = QtWidgets.QLabel("Expired")
            expired_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #6C63FF; margin-top: 20px;")
            
            # Group exams by availability
            available_now = []
            upcoming = []
            expired = []
            
            for exam in available_exams:
                # Convert times for comparison
                start_time_str = exam['start_time']
                end_time_str = exam['end_time']
                
                # Parse time strings
                start_time = datetime.datetime.strptime(start_time_str, '%H:%M:%S').time()
                end_time = datetime.datetime.strptime(end_time_str, '%H:%M:%S').time()
                
                # Get current time
                current_time_obj = datetime.datetime.now().time()
                
                # Check if exam is currently available
                if start_time <= current_time_obj and end_time >= current_time_obj:
                    available_now.append((exam['id'], exam['name'], exam['duration'], start_time, end_time))
                elif start_time > current_time_obj:
                    upcoming.append((exam['id'], exam['name'], exam['duration'], start_time, end_time))
                else:  # end_time < current_time
                    expired.append((exam['id'], exam['name'], exam['duration'], start_time, end_time))
            
            # Create scrollable area
            scroll_area = QtWidgets.QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_content = QtWidgets.QWidget()
            scroll_layout = QtWidgets.QVBoxLayout(scroll_content)
            scroll_layout.setSpacing(10)
            
            # Display available now exams
            if available_now:
                scroll_layout.addWidget(available_now_label)
                
                for exam_id, name, duration, start_time, end_time in available_now:
                    exam_card = self.create_exam_card(exam_id, name, duration, start_time, end_time, True)
                    scroll_layout.addWidget(exam_card)
            
            # Display upcoming exams
            if upcoming:
                scroll_layout.addWidget(upcoming_label)
                
                for exam_id, name, duration, start_time, end_time in upcoming:
                    exam_card = self.create_exam_card(exam_id, name, duration, start_time, end_time, False)
                    scroll_layout.addWidget(exam_card)
            
            # Display expired exams
            if expired:
                scroll_layout.addWidget(expired_label)
                
                for exam_id, name, duration, start_time, end_time in expired:
                    exam_card = self.create_exam_card(exam_id, name, duration, start_time, end_time, False, True)
                    scroll_layout.addWidget(exam_card)
            
            scroll_area.setWidget(scroll_content)
            self.exams_container_layout.addWidget(scroll_area)
            
            # Add a refresh note
            refresh_note = QtWidgets.QLabel("Last refreshed: " + datetime.datetime.now().strftime("%H:%M:%S"))
            refresh_note.setStyleSheet("color: #999; font-size: 12px; font-style: italic;")
            refresh_note.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
            self.exams_container_layout.addWidget(refresh_note)
    
        except Exception as e:
            msg = QtWidgets.QMessageBox()
            msg.setStyleSheet(COMMON_STYLES['message_box'])
            msg.setWindowTitle("Error")
            msg.setText(str(e))
            msg.setIcon(QtWidgets.QMessageBox.Icon.Critical)
            msg.exec()
            
    def create_exam_card(self, exam_id, name, duration, start_time, end_time, is_available, is_expired=False):
        exam_card = QtWidgets.QWidget()
        
        # Style based on availability
        if is_available:
            # Available now - highlighted style
            exam_card.setStyleSheet("""
                QWidget {
                    background-color: #F0F8FF;
                    border-radius: 10px;
                    padding: 15px;
                    margin: 5px;
                    border: 2px solid #6C63FF;
                }
            """)
            status_text = "AVAILABLE NOW"
            status_color = "#4CAF50"  # Green
        elif is_expired:
            # Expired - faded style
            exam_card.setStyleSheet("""
                QWidget {
                    background-color: #F5F5F5;
                    border-radius: 10px;
                    padding: 15px;
                    margin: 5px;
                    border: 1px solid #E0E0E0;
                    opacity: 0.7;
                }
            """)
            status_text = "EXPIRED"
            status_color = "#999999"  # Gray
        else:
            # Upcoming - normal style
            exam_card.setStyleSheet("""
                QWidget {
                    background-color: white;
                    border-radius: 10px;
                    padding: 15px;
                    margin: 5px;
                    border: 1px solid #E0E0E0;
                }
            """)
            status_text = "UPCOMING"
            status_color = "#FF9800"  # Orange
            
        # Only make available exams clickable
        if is_available:
            exam_card.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
            exam_card.mouseReleaseEvent = lambda event, eid=exam_id: self.take_exam(eid)
        
        card_layout = QtWidgets.QVBoxLayout(exam_card)
        
        # Header with name and status
        header_layout = QtWidgets.QHBoxLayout()
        
        name_label = QtWidgets.QLabel(name)
        name_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        
        status_label = QtWidgets.QLabel(status_text)
        status_label.setStyleSheet(f"color: {status_color}; font-weight: bold; font-size: 12px;")
        
        header_layout.addWidget(name_label)
        header_layout.addStretch()
        header_layout.addWidget(status_label)
        
        card_layout.addLayout(header_layout)
        
        # Format duration correctly based on its type - always treat as seconds
        try:
            # Convert to integer seconds if it's not already
            duration_seconds = int(duration)
            
            # Calculate hours, minutes, seconds
            hours = duration_seconds // 3600
            minutes = (duration_seconds % 3600) // 60
            seconds = duration_seconds % 60
            
            # Format the duration text
            if hours > 0:
                duration_text = f"Duration: {hours}h {minutes}m {seconds}s"
            elif minutes > 0:
                duration_text = f"Duration: {minutes}m {seconds}s"
            else:
                duration_text = f"Duration: {seconds}s"
        except:
            # Fallback in case of errors
            duration_text = f"Duration: {duration} seconds"
            
        duration_label = QtWidgets.QLabel(duration_text)
        duration_label.setStyleSheet("color: #666; font-size: 14px;")
        
        # Time information layout
        time_layout = QtWidgets.QHBoxLayout()
        
        # Add start and end time information
        start_time_label = QtWidgets.QLabel(f"Starts: {start_time.strftime('%H:%M')}")
        start_time_label.setStyleSheet("color: #666; font-size: 14px;")
        
        end_time_label = QtWidgets.QLabel(f"Ends: {end_time.strftime('%H:%M')}")
        end_time_label.setStyleSheet("color: #666; font-size: 14px;")
        
        time_layout.addWidget(start_time_label)
        time_layout.addStretch()
        time_layout.addWidget(end_time_label)
        
        card_layout.addWidget(duration_label)
        card_layout.addLayout(time_layout)
        
        # Add instruction text
        if is_available:
            instruction = QtWidgets.QLabel("Click to take this exam")
            instruction.setStyleSheet("color: #6C63FF; font-size: 13px; font-style: italic; margin-top: 5px;")
            card_layout.addWidget(instruction)
        elif not is_expired:
            # Calculate and display time until exam starts
            now = datetime.datetime.now().time()
            start_dt = datetime.datetime.combine(datetime.date.today(), start_time)
            now_dt = datetime.datetime.combine(datetime.date.today(), now)
            time_until = start_dt - now_dt
            
            minutes_until = int(time_until.total_seconds() / 60)
            hours_until = minutes_until // 60
            mins_remaining = minutes_until % 60
            
            if hours_until > 0:
                time_text = f"Available in {hours_until}h {mins_remaining}m"
            else:
                time_text = f"Available in {mins_remaining}m"
                
            countdown = QtWidgets.QLabel(time_text)
            countdown.setStyleSheet("color: #FF9800; font-size: 13px; font-weight: bold; margin-top: 5px;")
            card_layout.addWidget(countdown)
            
        return exam_card

    def take_exam(self, exam_id):
        # Navigate to the disclaimer page first instead of directly to exam taking
        disclaimer_page = ExamDisclaimerPage(self.main_window, exam_id)
        self.main_window.stackedWidget.addWidget(disclaimer_page)
        self.main_window.stackedWidget.setCurrentWidget(disclaimer_page)

    def show_results(self):
        # Create a new widget to display results
        self.results_widget = QtWidgets.QWidget()
        results_layout = QtWidgets.QVBoxLayout(self.results_widget)

        # Add header with back button
        header = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel('My Results')
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

        # Load results initially
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

            # Fetch exam results for the current student
            results_response = supabase.table('exam_results') \
                .select('exam_id, score, completed_at') \
                .eq('student_username', self.main_window.current_user) \
                .execute()

            if not results_response.data:
                no_results_label = QtWidgets.QLabel("No results available.")
                no_results_label.setStyleSheet("font-size: 16px; color: #666; margin: 20px;")
                no_results_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.results_container_layout.addWidget(no_results_label)
                return

            # Create section headers
            completed_label = QtWidgets.QLabel("Completed Exams")
            completed_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #6C63FF; margin-top: 10px;")
            
            in_progress_label = QtWidgets.QLabel("In-Progress Exams")
            in_progress_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #FF9800; margin-top: 20px;")
            
            # Group results by status
            completed_exams = []
            in_progress_exams = []
            
            for result in results_response.data:
                exam_id = result['exam_id']
                score = result['score']
                completed_at = result['completed_at']
                
                # Fetch exam date and name from exams table
                exam_data = supabase.table('exams') \
                    .select('exam_date, name') \
                    .eq('id', exam_id) \
                    .single() \
                    .execute()
                
                exam_date = exam_data.data['exam_date'] if exam_data.data and 'exam_date' in exam_data.data else "Unknown"
                exam_name = exam_data.data['name'] if exam_data.data and 'name' in exam_data.data else f"Exam #{exam_id}"

                # Count total number of questions for the exam
                questions_data = supabase.table('questions') \
                    .select('id') \
                    .eq('exam_id', exam_id) \
                    .execute()
                total_marks = len(questions_data.data) if questions_data.data else 0
                
                # Log information for debugging
                logging.debug(f"Exam result: id={exam_id}, name={exam_name}, score={score}/{total_marks}, completed={completed_at}")
                
                # Look at completed_at timestamp to determine if exam is completed
                if completed_at:
                    # For a more accurate check, we could add additional logic here
                    # such as comparing with end time of the exam
                    completed_exams.append((exam_id, exam_name, score, total_marks, exam_date, completed_at))
                else:
                    in_progress_exams.append((exam_id, exam_name, score, total_marks, exam_date))
        
            # Add container for scrollable content
            scroll_area = QtWidgets.QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_content = QtWidgets.QWidget()
            scroll_layout = QtWidgets.QVBoxLayout(scroll_content)
            scroll_layout.setSpacing(10)
            
            # Display completed exams
            if completed_exams:
                scroll_layout.addWidget(completed_label)
                
                for exam_id, exam_name, score, total_marks, exam_date, completed_at in completed_exams:
                    result_card = self.create_result_card(exam_id, exam_name, score, total_marks, exam_date, True, completed_at)
                    scroll_layout.addWidget(result_card)
            
            # Display in-progress exams
            if in_progress_exams:
                scroll_layout.addWidget(in_progress_label)
                
                for exam_id, exam_name, score, total_marks, exam_date in in_progress_exams:
                    result_card = self.create_result_card(exam_id, exam_name, score, total_marks, exam_date, False)
                    scroll_layout.addWidget(result_card)
            
            if not (completed_exams or in_progress_exams):
                no_results_label = QtWidgets.QLabel("No results available.")
                no_results_label.setStyleSheet("font-size: 16px; color: #666; margin: 20px;")
                no_results_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                scroll_layout.addWidget(no_results_label)
            
            scroll_area.setWidget(scroll_content)
            self.results_container_layout.addWidget(scroll_area)

        except Exception as e:
            logging.error(f"Error loading results: {e}")
            msg = QtWidgets.QMessageBox()
            msg.setStyleSheet(COMMON_STYLES['message_box'])
            msg.setWindowTitle("Error")
            msg.setText(str(e))
            msg.setIcon(QtWidgets.QMessageBox.Icon.Critical)
            msg.exec()

    def create_result_card(self, exam_id, exam_name, score, total_marks, exam_date, is_completed, completed_at=None):
        result_card = QtWidgets.QWidget()
        
        # Style based on completion status
        if is_completed:
            result_card.setStyleSheet('''
                QWidget {
                    background: #F0F8FF;
                    border-radius: 10px;
                    padding: 15px;
                    margin: 5px;
                    border: 1px solid #6C63FF;
                }
            ''')
            status_text = "COMPLETED"
            status_color = "#4CAF50"  # Green
        else:
            result_card.setStyleSheet('''
                QWidget {
                    background: #FFF8E1;
                    border-radius: 10px;
                    padding: 15px;
                    margin: 5px;
                    border: 1px solid #FF9800;
                }
            ''')
            status_text = "IN PROGRESS"
            status_color = "#FF9800"  # Orange
        
        card_layout = QtWidgets.QVBoxLayout(result_card)
        
        # Header with name and status
        header_layout = QtWidgets.QHBoxLayout()
        
        name_label = QtWidgets.QLabel(exam_name)
        name_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
        
        status_label = QtWidgets.QLabel(status_text)
        status_label.setStyleSheet(f"color: {status_color}; font-weight: bold; font-size: 12px;")
        
        header_layout.addWidget(name_label)
        header_layout.addStretch()
        header_layout.addWidget(status_label)
        
        card_layout.addLayout(header_layout)
        
        # Score and date info
        score_label = QtWidgets.QLabel(f"Score: {score}/{total_marks}")
        score_label.setStyleSheet("font-size: 14px; color: #666;")
        
        date_label = QtWidgets.QLabel(f"Exam Date: {exam_date}")
        date_label.setStyleSheet("font-size: 14px; color: #666;")
        
        card_layout.addWidget(score_label)
        card_layout.addWidget(date_label)
        
        # Add completion time if available
        if completed_at:
            try:
                # Convert ISO format to readable format
                completed_datetime = datetime.datetime.fromisoformat(completed_at)
                formatted_time = completed_datetime.strftime("%Y-%m-%d %H:%M:%S")
                completed_label = QtWidgets.QLabel(f"Completed: {formatted_time}")
                completed_label.setStyleSheet("font-size: 14px; color: #666; font-style: italic;")
                card_layout.addWidget(completed_label)
            except:
                # In case of formatting errors
                pass
        
        return result_card

    def show_profile(self):
        # Create a new widget to display profile information
        self.profile_widget = QtWidgets.QWidget()
        profile_layout = QtWidgets.QVBoxLayout(self.profile_widget)

        # Add header with back button
        header = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel('My Profile')
        title.setStyleSheet(COMMON_STYLES['title_label'])

        back_btn = QtWidgets.QPushButton('Back to Dashboard')
        back_btn.setStyleSheet(COMMON_STYLES['secondary_button'])
        back_btn.clicked.connect(lambda: self.main_window.stackedWidget.setCurrentWidget(self))

        header.addWidget(title)
        header.addStretch()
        header.addWidget(back_btn)
        profile_layout.addLayout(header)

        # Add a container widget for the profile details
        self.profile_container = QtWidgets.QWidget()
        self.profile_container_layout = QtWidgets.QVBoxLayout(self.profile_container)
        profile_layout.addWidget(self.profile_container)

        # Load profile information
        self.load_profile()

        profile_layout.addStretch()
        self.main_window.stackedWidget.addWidget(self.profile_widget)
        self.main_window.stackedWidget.setCurrentWidget(self.profile_widget)

    def load_profile(self):
        # Clear any existing content
        while self.profile_container_layout.count():
            item = self.profile_container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        try:
            supabase = create_connection()
            if not supabase:
                raise Exception("Failed to connect to Supabase")

            # Fetch profile information for the current user
            profile_response = supabase.table('users') \
                .select('username, user_type') \
                .eq('username', self.main_window.current_user) \
                .single() \
                .execute()

            if not profile_response.data:
                no_profile_label = QtWidgets.QLabel("Profile information not available.")
                no_profile_label.setStyleSheet("font-size: 16px; color: #666; margin: 20px;")
                no_profile_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.profile_container_layout.addWidget(no_profile_label)
                return

            profile_data = profile_response.data

            username_label = QtWidgets.QLabel(f"Username: {profile_data['username']}")
            username_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #333;")

            user_type_label = QtWidgets.QLabel(f"User Type: {profile_data['user_type']}")
            user_type_label.setStyleSheet("font-size: 14px; color: #666;")

            self.profile_container_layout.addWidget(username_label)
            self.profile_container_layout.addWidget(user_type_label)

        except Exception as e:
            msg = QtWidgets.QMessageBox()
            msg.setStyleSheet(COMMON_STYLES['message_box'])
            msg.setWindowTitle("Error")
            msg.setText(str(e))
            msg.setIcon(QtWidgets.QMessageBox.Icon.Critical)
            msg.exec()

    def show_resources(self):
        # Create a new widget to display resources
        self.resources_widget = QtWidgets.QWidget()
        resources_layout = QtWidgets.QVBoxLayout(self.resources_widget)

        # Add header with back button
        header = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel('Study Resources')
        title.setStyleSheet(COMMON_STYLES['title_label'])

        back_btn = QtWidgets.QPushButton('Back to Dashboard')
        back_btn.setStyleSheet(COMMON_STYLES['secondary_button'])
        back_btn.clicked.connect(lambda: self.main_window.stackedWidget.setCurrentWidget(self))

        header.addWidget(title)
        header.addStretch()
        header.addWidget(back_btn)
        resources_layout.addLayout(header)

        # Add a container widget for the resources list
        self.resources_container = QtWidgets.QWidget()
        self.resources_container_layout = QtWidgets.QVBoxLayout(self.resources_container)
        resources_layout.addWidget(self.resources_container)

        # Load resources
        self.load_resources()

        resources_layout.addStretch()
        self.main_window.stackedWidget.addWidget(self.resources_widget)
        self.main_window.stackedWidget.setCurrentWidget(self.resources_widget)

    def load_resources(self):
        # Clear any existing content
        while self.resources_container_layout.count():
            item = self.resources_container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        try:
            supabase = create_connection()
            if not supabase:
                raise Exception("Failed to connect to Supabase")

            # Fetch resources from the database
            resources_response = supabase.table('resources') \
                .select('title, description, link') \
                .execute()

            if not resources_response.data:
                no_resources_label = QtWidgets.QLabel("No resources available.")
                no_resources_label.setStyleSheet("font-size: 16px; color: #666; margin: 20px;")
                no_resources_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.resources_container_layout.addWidget(no_resources_label)
                return

            # Display each resource
            for resource in resources_response.data:
                resource_card = QtWidgets.QWidget()
                resource_card.setStyleSheet('''
                    QWidget {
                        background: white;
                        border-radius: 10px;
                        padding: 15px;
                        margin: 5px;
                        border: 1px solid #E0E0E0;
                    }
                ''')
                card_layout = QtWidgets.QVBoxLayout(resource_card)

                title_label = QtWidgets.QLabel(resource['title'])
                title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #333;")

                description_label = QtWidgets.QLabel(resource['description'])
                description_label.setStyleSheet("font-size: 13px; color: #666;")

                link_btn = QtWidgets.QPushButton('Open Resource')
                link_btn.setStyleSheet(COMMON_STYLES['primary_button'])
                link_btn.clicked.connect(lambda _, url=resource['link']: QtCore.QDesktopServices.openUrl(QtCore.QUrl(url)))

                card_layout.addWidget(title_label)
                card_layout.addWidget(description_label)
                card_layout.addWidget(link_btn)

                self.resources_container_layout.addWidget(resource_card)

        except Exception as e:
            msg = QtWidgets.QMessageBox()
            msg.setStyleSheet(COMMON_STYLES['message_box'])
            msg.setWindowTitle("Error")
            msg.setText(str(e))
            msg.setIcon(QtWidgets.QMessageBox.Icon.Critical)
            msg.exec()

