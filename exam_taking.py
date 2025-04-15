from PyQt6 import QtWidgets, QtCore
from supabase_connection import create_connection
import logging
import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class ExamTaking(QtWidgets.QWidget):
    def __init__(self, main_window, exam_id):
        super().__init__()
        self.main_window = main_window
        self.exam_id = exam_id
        self.current_question_index = 0
        self.questions = []
        self.answers = {}
        self.exam_duration = 0  # Duration in minutes
        self.remaining_time = 0  # Remaining time in seconds
        
        # Initialize timer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.timer.setInterval(1000)  # 1 second interval
        
        self.initUI()

    def initUI(self):
        self.setStyleSheet("background-color: white;")
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(40, 40, 40, 40)
        self.main_layout.setSpacing(20)

        # Title for the exam with timer
        title_timer_layout = QtWidgets.QHBoxLayout()
        
        self.title_label = QtWidgets.QLabel("Exam Questions")
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #6C63FF;")
        title_timer_layout.addWidget(self.title_label)
        
        title_timer_layout.addStretch()
        
        self.timer_label = QtWidgets.QLabel()
        self.timer_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #FF6C63;")
        title_timer_layout.addWidget(self.timer_label)
        
        self.main_layout.addLayout(title_timer_layout)

        # Question and options layout
        self.question_layout = QtWidgets.QVBoxLayout()
        self.question_layout.setSpacing(15)
        
        # Create a scroll area to ensure all content is visible
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet('''
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        ''')
        
        scroll_content = QtWidgets.QWidget()
        scroll_content.setLayout(self.question_layout)
        scroll_area.setWidget(scroll_content)
        
        self.main_layout.addWidget(scroll_area, 1)  # Add stretch factor to take available space

        # Navigation buttons
        self.nav_layout = QtWidgets.QHBoxLayout()
        self.nav_layout.setContentsMargins(10, 20, 10, 10)  # Add more top margin
        self.nav_layout.setSpacing(15)  # Increase spacing between buttons
        
        self.prev_button = QtWidgets.QPushButton('Previous')
        self.prev_button.setStyleSheet('''
            QPushButton {
                background-color: white;
                border: 1px solid #6C63FF;
                border-radius: 5px;
                color: #6C63FF;
                padding: 10px 20px;
                font-size: 14px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #6C63FF;
                color: white;
            }
        ''')
        self.prev_button.clicked.connect(self.prev_question)
        
        self.next_button = QtWidgets.QPushButton('Next')
        self.next_button.setStyleSheet('''
            QPushButton {
                background-color: white;
                border: 1px solid #6C63FF;
                border-radius: 5px;
                color: #6C63FF;
                padding: 10px 20px;
                font-size: 14px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #6C63FF;
                color: white;
            }
        ''')
        self.next_button.clicked.connect(self.next_question)
        
        self.submit_button = QtWidgets.QPushButton('Submit')
        self.submit_button.setStyleSheet('''
            QPushButton {
                background-color: #6C63FF;
                border: none;
                border-radius: 5px;
                color: white;
                padding: 10px 20px;
                font-size: 14px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #5952cc;
            }
        ''')
        self.submit_button.clicked.connect(self.submit_exam)

        # Add spacers to better distribute buttons
        self.nav_layout.addStretch(1)
        self.nav_layout.addWidget(self.prev_button)
        self.nav_layout.addStretch(1)
        self.nav_layout.addWidget(self.next_button)
        self.nav_layout.addStretch(1)
        self.nav_layout.addWidget(self.submit_button)
        self.nav_layout.addStretch(1)

        self.main_layout.addLayout(self.nav_layout)

        # Progress indicator
        self.progress_label = QtWidgets.QLabel()
        self.progress_label.setStyleSheet("color: #666; font-size: 14px; margin-top: 10px; margin-bottom: 10px;")
        self.progress_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)  # Center the progress text
        self.main_layout.addWidget(self.progress_label)

        # Fetch exam details including duration
        self.fetch_exam_details()

        # Fetch questions from the database
        self.fetch_questions()

        # Display the first question
        if self.questions:
            self.display_question(self.current_question_index)

    def fetch_exam_details(self):
        try:
            supabase = create_connection()
            if not supabase:
                raise Exception("Failed to connect to Supabase")
                
            # Get exam details
            response = supabase.table('exams') \
                .select('name, duration') \
                .eq('id', self.exam_id) \
                .execute()
                
            if response.data:
                exam = response.data[0]
                exam_name = exam['name']
                duration = exam['duration']
                
                self.title_label.setText(exam_name)
                self.exam_duration = duration
                
                # Fix duration handling - always treat duration as seconds
                # Convert to proper time format for display
                self.remaining_time = int(duration)  # Always use seconds
                hours = int(self.remaining_time // 3600)
                minutes = int((self.remaining_time % 3600) // 60)
                seconds = int(self.remaining_time % 60)
                
                if hours > 0:
                    logging.debug(f"Exam duration set to {hours}h {minutes}m {seconds}s")
                else:
                    logging.debug(f"Exam duration set to {minutes}m {seconds}s")
                
                self.update_timer_display()
                
                # Start the timer
                self.timer.start()
                logging.debug("Exam timer started")
            else:
                logging.warning(f"Exam with ID {self.exam_id} not found")
        except Exception as e:
            logging.error(f"Error fetching exam details: {e}")
            msg = QtWidgets.QMessageBox()
            msg.setWindowTitle("Error")
            msg.setText(f"Error fetching exam details: {str(e)}")
            msg.setIcon(QtWidgets.QMessageBox.Icon.Critical)
            msg.exec()

    def update_timer(self):
        if self.remaining_time > 0:
            self.remaining_time -= 1
            self.update_timer_display()
        else:
            self.timer.stop()
            msg = QtWidgets.QMessageBox()
            msg.setWindowTitle("Time's Up")
            msg.setText("Your time is up! The exam will be submitted automatically.")
            msg.setIcon(QtWidgets.QMessageBox.Icon.Warning)
            msg.exec()
            self.submit_exam()

    def update_timer_display(self):
        minutes = self.remaining_time // 60
        seconds = self.remaining_time % 60
        self.timer_label.setText(f"Time Left: {minutes:02d}:{seconds:02d}")
        
        # Change color to red when less than 5 minutes remaining
        if minutes < 5:
            self.timer_label.setStyleSheet("font-size: 18px; font-weight: bold; color: red;")
        else:
            self.timer_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #FF6C63;")

    def fetch_questions(self):
        try:
            supabase = create_connection()
            if not supabase:
                raise Exception("Failed to connect to Supabase")
                
            # Get questions for this exam
            response = supabase.table('questions') \
                .select('id, question_text, option1, option2, option3, option4') \
                .eq('exam_id', self.exam_id) \
                .order('id') \
                .execute()
                
            # Log details about questions to help debug duplication issues
            logging.debug(f"Raw question data: {response.data}")
            
            # Convert the response data to the expected format
            self.questions = [(q['id'], q['question_text'], q['option1'], q['option2'], q['option3'], q['option4']) 
                              for q in response.data]
                              
            logging.debug(f"Fetched {len(self.questions)} questions")
            
            # Alert if there are more questions than expected
            if len(self.questions) > 1:
                logging.warning(f"Multiple questions found for exam ID {self.exam_id}. This might indicate duplicate entries.")
                
        except Exception as e:
            logging.error(f"Error fetching questions: {e}")
            msg = QtWidgets.QMessageBox()
            msg.setWindowTitle("Error")
            msg.setText(f"Error fetching questions: {str(e)}")
            msg.setIcon(QtWidgets.QMessageBox.Icon.Critical)
            msg.exec()

    def display_question(self, index):
        logging.debug(f"Displaying question at index: {index}")
        if 0 <= index < len(self.questions):
            question_id, question_text, option1, option2, option3, option4 = self.questions[index]

            # Clear existing question widgets
            while self.question_layout.count():
                child = self.question_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

            # Display question
            question_container = QtWidgets.QWidget()
            question_container.setStyleSheet("background-color: #F5F5FF; border-radius: 10px; padding: 15px; margin-bottom: 15px;")
            question_container_layout = QtWidgets.QVBoxLayout(question_container)
            
            question_num_label = QtWidgets.QLabel(f"Question {index + 1}:")
            question_num_label.setStyleSheet('font-size: 16px; font-weight: bold; color: #6C63FF;')
            question_container_layout.addWidget(question_num_label)
            
            question_label = QtWidgets.QLabel(question_text)
            question_label.setStyleSheet('font-size: 18px; font-weight: bold; color: #333; margin-top: 5px;')
            question_label.setWordWrap(True)
            question_container_layout.addWidget(question_label)
            
            self.question_layout.addWidget(question_container)

            # Display options
            options_container = QtWidgets.QWidget()
            options_container.setStyleSheet("background-color: white; border: 1px solid #E0E0E0; border-radius: 10px; padding: 15px; margin-bottom: 15px;")
            options_layout = QtWidgets.QVBoxLayout(options_container)
            options_layout.setSpacing(15)  # Increase spacing between options
            
            options_title = QtWidgets.QLabel("Select an answer:")
            options_title.setStyleSheet('font-size: 14px; color: #666; margin-bottom: 10px;')
            options_layout.addWidget(options_title)
            
            self.option_buttons = []
            options = [option1, option2, option3, option4]
            option_labels = ['A', 'B', 'C', 'D']
            
            option_group = QtWidgets.QButtonGroup(self)
            
            for i, option in enumerate(options):
                if option:  # Ensure option is not None or empty
                    option_layout = QtWidgets.QHBoxLayout()
                    option_layout.setContentsMargins(5, 5, 5, 5)  # Add padding around options
                    
                    radio_button = QtWidgets.QRadioButton()
                    radio_button.setStyleSheet('''
                        QRadioButton {
                            font-size: 16px;
                            color: #333;
                            spacing: 10px;
                        }
                        QRadioButton::indicator {
                            width: 20px;
                            height: 20px;
                        }
                    ''')
                    
                    # Add to button group for mutually exclusive selection
                    option_group.addButton(radio_button, i)
                    
                    # Check if this answer was previously selected
                    if question_id in self.answers and self.answers[question_id] == i:
                        radio_button.setChecked(True)
                    
                    # Connect to save answer when selected
                    radio_button.toggled.connect(lambda checked, q_id=question_id, opt_idx=i: 
                                              self.save_answer(q_id, opt_idx) if checked else None)
                    
                    option_label = QtWidgets.QLabel(f"{option_labels[i]}. {option}")
                    option_label.setStyleSheet('font-size: 16px; color: #333;')
                    option_label.setWordWrap(True)
                    
                    option_layout.addWidget(radio_button)
                    option_layout.addWidget(option_label)
                    option_layout.addStretch()
                    
                    options_layout.addLayout(option_layout)
                    self.option_buttons.append(radio_button)
            
            self.question_layout.addWidget(options_container)
            
            # Update progress label
            self.progress_label.setText(f"Question {index + 1} of {len(self.questions)}")
        else:
            logging.warning(f"Invalid question index: {index}")

    def save_answer(self, question_id, option_index):
        self.answers[question_id] = option_index
        logging.debug(f"Saved answer for question {question_id}: option {option_index}")
        
        # Update exam_results in real-time
        try:
            supabase = create_connection()
            if not supabase:
                raise Exception("Failed to connect to Supabase")
            
            # Get the correct answer to check if this response is correct
            response = supabase.table('questions') \
                .select('correct_answer, option1, option2, option3, option4') \
                .eq('id', question_id) \
                .execute()
            
            if response.data:
                question = response.data[0]
                correct_answer = question['correct_answer']
                options = [question['option1'], question['option2'], question['option3'], question['option4']]
                selected_option = options[option_index]
                
                # Fixed correct answer comparison logic - compare with the actual option text
                # The correct_answer field stores the text, like "Option X", but we need to match with actual content
                
                # Convert from "Option X" format to index
                option_index_map = {"Option 1": 0, "Option 2": 1, "Option 3": 2, "Option 4": 3}
                if correct_answer in option_index_map:
                    correct_index = option_index_map[correct_answer]
                    correct_option_text = options[correct_index]
                    is_correct = (selected_option == correct_option_text)
                else:
                    # Fallback to direct match (if correct_answer is stored as the actual text)
                    is_correct = (selected_option == correct_answer)
                
                # Log comparison details to help debug
                logging.debug(f"Answer comparison: selected='{selected_option}', correct='{correct_answer}', is_correct={is_correct}")
                
                # Check if this student has already answered this question
                existing_answer = supabase.table('student_answers') \
                    .select('id') \
                    .eq('exam_id', self.exam_id) \
                    .eq('question_id', question_id) \
                    .eq('student_username', self.main_window.current_user) \
                    .execute()
                
                if existing_answer.data:
                    # Update existing answer
                    supabase.table('student_answers') \
                        .update({
                            'selected_answer': selected_option,
                            'is_correct': is_correct
                        }) \
                        .eq('id', existing_answer.data[0]['id']) \
                        .execute()
                else:
                    # Create new answer
                    supabase.table('student_answers').insert({
                        'exam_id': self.exam_id,
                        'question_id': question_id,
                        'student_username': self.main_window.current_user,
                        'selected_answer': selected_option,
                        'is_correct': is_correct
                    }).execute()
                
                # Count all correct answers so far to update the score
                correct_count_response = supabase.table('student_answers') \
                    .select('id') \
                    .eq('exam_id', self.exam_id) \
                    .eq('student_username', self.main_window.current_user) \
                    .eq('is_correct', True) \
                    .execute()
                
                correct_count = len(correct_count_response.data)
                
                # Check if there's an existing exam result
                result_response = supabase.table('exam_results') \
                    .select('id') \
                    .eq('exam_id', self.exam_id) \
                    .eq('student_username', self.main_window.current_user) \
                    .execute()
                
                if result_response.data:
                    # Update existing result with current score
                    supabase.table('exam_results') \
                        .update({'score': correct_count}) \
                        .eq('id', result_response.data[0]['id']) \
                        .execute()
                else:
                    # Create new result entry with initial score
                    supabase.table('exam_results').insert({
                        'exam_id': self.exam_id,
                        'student_username': self.main_window.current_user,
                        'score': correct_count
                        # Don't set completed_at until the exam is fully submitted
                    }).execute()
        except Exception as e:
            logging.error(f"Error updating exam result in real-time: {e}")
            # Don't show error to user to avoid interrupting the exam experience

    def prev_question(self):
        if self.current_question_index > 0:
            self.current_question_index -= 1
            self.display_question(self.current_question_index)

    def next_question(self):
        if self.current_question_index < len(self.questions) - 1:
            self.current_question_index += 1
            self.display_question(self.current_question_index)

    def submit_exam(self):
        try:
            # Get current score from the database
            supabase = create_connection()
            if not supabase:
                raise Exception("Failed to connect to Supabase")
            
            # Process any unanswered questions and ensure accurate score calculation
            total_questions = len(self.questions)
            correct_count = 0
            
            # Check all questions and answers
            for question_id, _, _, _, _, _ in self.questions:
                if question_id in self.answers:
                    # Get the correct answer
                    response = supabase.table('questions') \
                        .select('correct_answer, option1, option2, option3, option4') \
                        .eq('id', question_id) \
                        .execute()
                    
                    if response.data:
                        question = response.data[0]
                        correct_answer = question['correct_answer']
                        options = [question['option1'], question['option2'], question['option3'], question['option4']]
                        selected_option = options[self.answers[question_id]]
                        
                        # Fixed correct answer comparison logic
                        option_index_map = {"Option 1": 0, "Option 2": 1, "Option 3": 2, "Option 4": 3}
                        if correct_answer in option_index_map:
                            correct_index = option_index_map[correct_answer]
                            correct_option_text = options[correct_index]
                            is_correct = (selected_option == correct_option_text)
                        else:
                            # Fallback to direct match (if correct_answer is stored as the actual text)
                            is_correct = (selected_option == correct_answer)
                        
                        if is_correct:
                            correct_count += 1
                        
                        # Log comparison details to help debug
                        logging.debug(f"Submit check: selected='{selected_option}', correct='{correct_answer}', is_correct={is_correct}")
                        
                        # Ensure student's answer is saved
                        # Check if this answer already exists
                        existing_answer = supabase.table('student_answers') \
                            .select('id') \
                            .eq('exam_id', self.exam_id) \
                            .eq('question_id', question_id) \
                            .eq('student_username', self.main_window.current_user) \
                            .execute()
                        
                        if not existing_answer.data:
                            # Save only if not already saved
                            supabase.table('student_answers').insert({
                                'exam_id': self.exam_id,
                                'question_id': question_id,
                                'student_username': self.main_window.current_user,
                                'selected_answer': selected_option,
                                'is_correct': is_correct
                            }).execute()
            
            # Get existing result or create a new one
            result_response = supabase.table('exam_results') \
                .select('id') \
                .eq('exam_id', self.exam_id) \
                .eq('student_username', self.main_window.current_user) \
                .execute()
            
            if result_response.data:
                # Update existing result with accurate score
                result_id = result_response.data[0]['id']
                supabase.table('exam_results') \
                    .update({
                        'score': correct_count,
                        'completed_at': datetime.datetime.now().isoformat()
                    }) \
                    .eq('id', result_id) \
                    .execute()
            else:
                # Create a new result entry
                supabase.table('exam_results').insert({
                    'exam_id': self.exam_id,
                    'student_username': self.main_window.current_user,
                    'score': correct_count,
                    'completed_at': datetime.datetime.now().isoformat()
                }).execute()
            
            # Show result with additional info about where to view results
            msg = QtWidgets.QMessageBox()
            msg.setWindowTitle("Exam Completed")
            msg.setText(
                f"Exam submitted successfully!\n\n"
                f"Your score: {correct_count}/{total_questions}\n"
                f"Correct answers: {correct_count}/{total_questions}\n\n"
                f"You can view your full results by going to 'My Results' on the dashboard."
            )
            msg.setIcon(QtWidgets.QMessageBox.Icon.Information)
            msg.exec()
            
            # Navigate back to the student dashboard
            self.main_window.stackedWidget.setCurrentWidget(self.main_window.student_dashboard)
            
        except Exception as e:
            logging.error(f"Error submitting exam: {e}")
            msg = QtWidgets.QMessageBox()
            msg.setWindowTitle("Error")
            msg.setText(f"Error submitting exam: {str(e)}")
            msg.setIcon(QtWidgets.QMessageBox.Icon.Critical)
            msg.exec() 