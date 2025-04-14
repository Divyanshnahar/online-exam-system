from PyQt6 import QtWidgets, QtCore, QtGui
from styles import COMMON_STYLES

class ExamDisclaimerPage(QtWidgets.QWidget):
    def __init__(self, main_window, exam_id):
        super().__init__()
        self.main_window = main_window
        self.exam_id = exam_id
        self.initUI()
        
    def initUI(self):
        # Main layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(20)
        
        # Header
        header_label = QtWidgets.QLabel("Exam Proctoring Disclaimer")
        header_label.setStyleSheet('''
            font-size: 24px;
            font-weight: bold;
            color: #6C63FF;
        ''')
        layout.addWidget(header_label)
        
        # Warning icon and text
        warning_widget = QtWidgets.QWidget()
        warning_layout = QtWidgets.QHBoxLayout(warning_widget)
        
        warning_icon = QtWidgets.QLabel("⚠️")
        warning_icon.setStyleSheet("font-size: 32px;")
        warning_layout.addWidget(warning_icon)
        
        warning_text = QtWidgets.QLabel("This exam is proctored with AI gaze detection technology")
        warning_text.setStyleSheet('''
            font-size: 18px;
            font-weight: bold;
            color: #FF6C63;
        ''')
        warning_layout.addWidget(warning_text)
        warning_layout.addStretch()
        
        layout.addWidget(warning_widget)
        
        # Disclaimer content
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet('''
            QScrollArea {
                border: 1px solid #E0E0E0;
                border-radius: 5px;
                background-color: white;
            }
        ''')
        
        disclaimer_content = QtWidgets.QWidget()
        disclaimer_layout = QtWidgets.QVBoxLayout(disclaimer_content)
        
        rules_header = QtWidgets.QLabel("Exam Rules and Requirements:")
        rules_header.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 10px;color: black;")
        disclaimer_layout.addWidget(rules_header)
        
        requirements = [
            "Your webcam must be enabled during the entire exam.",
            "Your face must be clearly visible and well-lit.",
            "You must face the camera directly while taking the exam.",
            "Looking away from the screen for extended periods will be flagged.",
            "The system will monitor your gaze direction during the entire exam.",
            "Multiple violations may result in automatic exam termination.",
            "The exam will be in fullscreen mode and cannot be minimized.",
            "Attempting to exit fullscreen may be considered a violation."
        ]
        
        for i, req in enumerate(requirements):
            req_label = QtWidgets.QLabel(f"{i+1}. {req}")
            req_label.setWordWrap(True)
            req_label.setStyleSheet("font-size: 14px; margin: 5px 0px;color: black;")
            disclaimer_layout.addWidget(req_label)
        
        privacy_header = QtWidgets.QLabel("Privacy Information:")
        privacy_header.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 15px;color: black;")
        disclaimer_layout.addWidget(privacy_header)
        
        privacy_text = QtWidgets.QLabel(
            "Camera data is processed locally on your device for gaze detection. "
            "No video or images are stored or transmitted to external servers. "
            "Only proctoring alerts and test results will be recorded in the system."
        )
        privacy_text.setWordWrap(True)
        privacy_text.setStyleSheet("font-size: 14px; margin: 5px 0px;color: black;")
        disclaimer_layout.addWidget(privacy_text)
        
        disclaimer_layout.addStretch()
        scroll_area.setWidget(disclaimer_content)
        layout.addWidget(scroll_area)
        
        # Checkbox for agreement
        self.agreement_checkbox = QtWidgets.QCheckBox("I understand and agree to the proctoring requirements")
        self.agreement_checkbox.setStyleSheet("font-size: 14px; margin-top: 10px;color: black;")
        self.agreement_checkbox.stateChanged.connect(self.toggle_continue_button)
        layout.addWidget(self.agreement_checkbox)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        
        back_button = QtWidgets.QPushButton("Back")
        back_button.setStyleSheet(COMMON_STYLES['secondary_button'])
        back_button.clicked.connect(self.go_back)
        
        self.continue_button = QtWidgets.QPushButton("Continue to Exam")
        self.continue_button.setStyleSheet(COMMON_STYLES['primary_button'])
        self.continue_button.clicked.connect(self.continue_to_exam)
        self.continue_button.setEnabled(False)
        
        button_layout.addWidget(back_button)
        button_layout.addStretch()
        button_layout.addWidget(self.continue_button)
        
        layout.addLayout(button_layout)
        
    def toggle_continue_button(self):
        self.continue_button.setEnabled(self.agreement_checkbox.isChecked())
        
    def go_back(self):
        # Navigate back to student dashboard
        self.main_window.stackedWidget.setCurrentWidget(self.main_window.student_dashboard)
        
    def continue_to_exam(self):
        try:
            # Import here to avoid circular import
            print("Attempting to import ProctoredExamTaking...")
            
            import exam_taking_proctored
            ProctoredExamTaking = exam_taking_proctored.ProctoredExamTaking
            print("Successfully imported ProctoredExamTaking")
            
            # Check if gaze detection is available
            print(f"Gaze detection available: {exam_taking_proctored.GAZE_DETECTION_AVAILABLE}")
            
            if not exam_taking_proctored.GAZE_DETECTION_AVAILABLE:
                # Show a warning that proctoring is not available
                QtWidgets.QMessageBox.warning(
                    self, 
                    "Proctoring Not Available",
                    "The exam proctoring system could not be initialized due to missing or incompatible dependencies.\n\n"
                    "Your exam will continue without proctoring.",
                    QtWidgets.QMessageBox.StandardButton.Ok
                )
            
            # Create proctored exam page
            print(f"Creating ProctoredExamTaking instance with exam_id: {self.exam_id}")
            exam_taking_widget = ProctoredExamTaking(self.main_window, self.exam_id)
            print("Successfully created ProctoredExamTaking instance")
            
            # Add widget to stacked widget
            print("Adding widget to stacked widget...")
            self.main_window.stackedWidget.addWidget(exam_taking_widget)
            
            # Switch to the exam taking widget
            print("Switching to exam taking widget...")
            self.main_window.stackedWidget.setCurrentWidget(exam_taking_widget)
            print("Successfully navigated to exam")
            
        except ImportError as e:
            # Specific handling for import errors
            import traceback
            error_details = traceback.format_exc()
            print(f"Import Error: {str(e)}")
            print(f"Traceback: {error_details}")
            
            msg = QtWidgets.QMessageBox(self)
            msg.setWindowTitle("Module Import Error")
            msg.setText("Failed to import exam proctoring module")
            msg.setInformativeText("Your exam will continue without proctoring.")
            msg.setDetailedText(f"Error: {str(e)}\n\nTraceback: {error_details}")
            msg.setIcon(QtWidgets.QMessageBox.Icon.Warning)
            msg.exec()
            
            # Fallback to standard exam taking without proctoring
            print("Falling back to standard exam taking")
            from exam_taking import ExamTaking
            exam_taking_widget = ExamTaking(self.main_window, self.exam_id)
            self.main_window.stackedWidget.addWidget(exam_taking_widget)
            self.main_window.stackedWidget.setCurrentWidget(exam_taking_widget)
            
        except Exception as e:
            # General exception handling
            import traceback
            error_details = traceback.format_exc()
            print(f"General Error: {str(e)}")
            print(f"Traceback: {error_details}")
            
            msg = QtWidgets.QMessageBox(self)
            msg.setWindowTitle("Error Starting Exam")
            msg.setText("Failed to start the exam")
            msg.setInformativeText(f"Error: {str(e)}")
            msg.setDetailedText(error_details)
            msg.setIcon(QtWidgets.QMessageBox.Icon.Critical)
            msg.exec()
            
            # Fallback to standard exam taking without proctoring
            try:
                print("Attempting fallback to standard exam taking")
                from exam_taking import ExamTaking
                exam_taking_widget = ExamTaking(self.main_window, self.exam_id)
                self.main_window.stackedWidget.addWidget(exam_taking_widget)
                self.main_window.stackedWidget.setCurrentWidget(exam_taking_widget)
                print("Successfully switched to non-proctored exam")
            except Exception as fallback_error:
                print(f"Fallback also failed: {fallback_error}")
                # If even the fallback fails, show another error message
                error_msg = QtWidgets.QMessageBox(self)
                error_msg.setWindowTitle("Critical Error")
                error_msg.setText("Failed to start the exam in any mode")
                error_msg.setIcon(QtWidgets.QMessageBox.Icon.Critical)
                error_msg.exec() 