from PyQt6 import QtWidgets, QtCore, QtGui
from supabase_connection import create_connection
from PyQt6.QtCore import QDateTime

class ExamManagement(QtWidgets.QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.initUI()

    def initUI(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel("Exam Management")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: black;")
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)
        
        # Description
        description = QtWidgets.QLabel("Manage your exams and view their schedules and status.")
        description.setStyleSheet("font-size: 14px; color: #555; margin-bottom: 20px;")
        layout.addWidget(description)
        
        # Refresh button
        refresh_btn = QtWidgets.QPushButton("Refresh Exams")
        refresh_btn.setStyleSheet('''
            QPushButton {
                background-color: #6C63FF;
                border-radius: 5px;
                color: white;
                padding: 8px 15px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #5A52D5;
            }
        ''')
        refresh_btn.clicked.connect(self.load_exams)
        layout.addWidget(refresh_btn)
        
        # Exams container
        self.exams_container = QtWidgets.QWidget()
        self.exams_layout = QtWidgets.QVBoxLayout(self.exams_container)
        
        # Scroll area for exams
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.exams_container)
        scroll_area.setStyleSheet('''
            QScrollArea {
                border: none;
                background-color: white;
            }
        ''')
        layout.addWidget(scroll_area)
        
        # Load exams
        self.load_exams()

    def load_exams(self):
        # Clear existing exams
        while self.exams_layout.count():
            item = self.exams_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        try:
            supabase = create_connection()
            exams_response = supabase.table('exams') \
                .select('id, name, status, exam_date, start_time, end_time, violation_limit') \
                .eq('teacher_username', self.main_window.current_user) \
                .execute()

            data = exams_response.data
            if not data:
                no_exams_label = QtWidgets.QLabel("No exams created yet.")
                no_exams_label.setStyleSheet("color: #555; font-size: 16px; padding: 20px;")
                self.exams_layout.addWidget(no_exams_label)
                return

            for exam in data:
                self.create_exam_card(exam)

        except Exception as e:
            error_label = QtWidgets.QLabel(f"Error loading exams: {str(e)}")
            error_label.setStyleSheet("color: red;")
            self.exams_layout.addWidget(error_label)
    
    def create_exam_card(self, exam):
        # Create card container
        card = QtWidgets.QWidget()
        card.setStyleSheet('''
            QWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                margin-bottom: 15px;
            }
        ''')
        card_layout = QtWidgets.QVBoxLayout(card)
        
        # Exam header with name and status
        header = QtWidgets.QHBoxLayout()
        
        # Exam name
        name_label = QtWidgets.QLabel(exam['name'])
        name_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        header.addWidget(name_label)
        
        header.addStretch()
        
        # Status badge
        status = exam['status']
        status_label = QtWidgets.QLabel(status.capitalize())
        
        # Style based on status
        if status == 'active':
            status_color = "#28a745"  # Green
        elif status == 'scheduled':
            status_color = "#ffc107"  # Yellow
        elif status == 'completed':
            status_color = "#6c757d"  # Gray
        else:
            status_color = "#dc3545"  # Red
            
        status_label.setStyleSheet(f'''
            background-color: {status_color};
            color: white;
            border-radius: 10px;
            padding: 3px 10px;
            font-size: 12px;
            font-weight: bold;
        ''')
        header.addWidget(status_label)
        
        card_layout.addLayout(header)
        
        # Exam details
        details_layout = QtWidgets.QFormLayout()
        details_layout.setVerticalSpacing(8)
        details_layout.setHorizontalSpacing(15)
        
        # Format date and time
        exam_date = exam.get('exam_date', 'Not scheduled')
        start_time = exam.get('start_time', '')
        end_time = exam.get('end_time', '')
        
        # Create labels with styled text
        date_label = QtWidgets.QLabel("Date:")
        date_label.setStyleSheet("color: #555; font-weight: bold;")
        date_value = QtWidgets.QLabel(exam_date)
        date_value.setStyleSheet("color: #333;")
        
        time_label = QtWidgets.QLabel("Time:")
        time_label.setStyleSheet("color: #555; font-weight: bold;")
        time_value = QtWidgets.QLabel(f"{start_time} - {end_time}")
        time_value.setStyleSheet("color: #333;")
        
        violation_label = QtWidgets.QLabel("Violation Limit:")
        violation_label.setStyleSheet("color: #555; font-weight: bold;")
        violation_value = QtWidgets.QLabel(str(exam.get('violation_limit', 3)))
        violation_value.setStyleSheet("color: #333;")
        
        details_layout.addRow(date_label, date_value)
        details_layout.addRow(time_label, time_value)
        details_layout.addRow(violation_label, violation_value)
        
        card_layout.addLayout(details_layout)
        
        # Actions
        actions_layout = QtWidgets.QHBoxLayout()
        
        # View Results button
        view_results_btn = QtWidgets.QPushButton("View Results")
        view_results_btn.setStyleSheet('''
            QPushButton {
                background-color: #6C63FF;
                border-radius: 5px;
                color: white;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #5A52D5;
            }
        ''')
        view_results_btn.clicked.connect(lambda: self.view_exam_results(exam['id']))
        
        # Edit button
        edit_btn = QtWidgets.QPushButton("Edit")
        edit_btn.setStyleSheet('''
            QPushButton {
                background-color: white;
                border: 1px solid #6C63FF;
                border-radius: 5px;
                color: #6C63FF;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #f0f0ff;
            }
        ''')
        edit_btn.clicked.connect(lambda: self.edit_exam(exam['id']))
        
        actions_layout.addWidget(view_results_btn)
        actions_layout.addWidget(edit_btn)
        
        card_layout.addLayout(actions_layout)
        
        # Add card to container
        self.exams_layout.addWidget(card)
    
    def view_exam_results(self, exam_id):
        # Placeholder for viewing exam results
        try:
            supabase = create_connection()
            results_response = supabase.table('exam_results') \
                .select('student_username, score, max_score, submission_time, violation_termination') \
                .eq('exam_id', exam_id) \
                .execute()
                
            results = results_response.data
            
            # Create a dialog to display results
            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle("Exam Results")
            dialog.setMinimumWidth(600)
            dialog.setMinimumHeight(400)
            
            dialog_layout = QtWidgets.QVBoxLayout(dialog)
            
            # Results table
            table = QtWidgets.QTableWidget()
            table.setColumnCount(5)
            table.setHorizontalHeaderLabels(["Student", "Score", "Submission Time", "Violations", "Status"])
            table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
            
            if not results:
                dialog_layout.addWidget(QtWidgets.QLabel("No results available for this exam."))
            else:
                table.setRowCount(len(results))
                
                for i, result in enumerate(results):
                    # Student username
                    table.setItem(i, 0, QtWidgets.QTableWidgetItem(result['student_username']))
                    
                    # Score
                    score_text = f"{result['score']}/{result['max_score']}"
                    table.setItem(i, 1, QtWidgets.QTableWidgetItem(score_text))
                    
                    # Submission time
                    table.setItem(i, 2, QtWidgets.QTableWidgetItem(result['submission_time']))
                    
                    # Violations
                    violation_status = "Terminated" if result.get('violation_termination', False) else "None"
                    table.setItem(i, 3, QtWidgets.QTableWidgetItem(violation_status))
                    
                    # Status
                    status = "Failed" if result['score'] < result['max_score'] / 2 else "Passed"
                    status_item = QtWidgets.QTableWidgetItem(status)
                    status_item.setForeground(QtGui.QColor("#dc3545" if status == "Failed" else "#28a745"))
                    table.setItem(i, 4, status_item)
                
                dialog_layout.addWidget(table)
            
            # Close button
            close_btn = QtWidgets.QPushButton("Close")
            close_btn.clicked.connect(dialog.accept)
            dialog_layout.addWidget(close_btn)
            
            dialog.exec()
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load exam results: {str(e)}")
    
    def edit_exam(self, exam_id):
        try:
            # Get exam details
            supabase = create_connection()
            exam_response = supabase.table('exams') \
                .select('*') \
                .eq('id', exam_id) \
                .execute()
                
            exam = exam_response.data[0] if exam_response.data else None
            
            if not exam:
                QtWidgets.QMessageBox.warning(self, "Error", "Exam not found")
                return
                
            # Create edit dialog
            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle(f"Edit Exam: {exam['name']}")
            dialog.setMinimumWidth(400)
            
            dialog_layout = QtWidgets.QVBoxLayout(dialog)
            
            # Form layout
            form_layout = QtWidgets.QFormLayout()
            
            # Violation limit
            violation_limit = QtWidgets.QSpinBox()
            violation_limit.setMinimum(1)
            violation_limit.setMaximum(10)
            violation_limit.setValue(exam.get('violation_limit', 3))
            form_layout.addRow("Violation Limit:", violation_limit)
            
            dialog_layout.addLayout(form_layout)
            
            # Buttons
            buttons_layout = QtWidgets.QHBoxLayout()
            
            save_btn = QtWidgets.QPushButton("Save Changes")
            save_btn.clicked.connect(lambda: self.save_exam_changes(exam_id, violation_limit.value(), dialog))
            
            cancel_btn = QtWidgets.QPushButton("Cancel")
            cancel_btn.clicked.connect(dialog.reject)
            
            buttons_layout.addWidget(save_btn)
            buttons_layout.addWidget(cancel_btn)
            
            dialog_layout.addLayout(buttons_layout)
            
            dialog.exec()
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load exam details: {str(e)}")
    
    def save_exam_changes(self, exam_id, violation_limit, dialog):
        try:
            supabase = create_connection()
            supabase.table('exams') \
                .update({'violation_limit': violation_limit}) \
                .eq('id', exam_id) \
                .execute()
                
            QtWidgets.QMessageBox.information(dialog, "Success", "Exam updated successfully")
            dialog.accept()
            
            # Refresh the exam list
            self.load_exams()
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(dialog, "Error", f"Failed to update exam: {str(e)}")