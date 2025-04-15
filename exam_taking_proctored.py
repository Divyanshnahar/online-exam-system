from PyQt6 import QtWidgets, QtCore, QtGui
from exam_taking import ExamTaking
import logging
import threading
import time
import datetime

# Initialize global variable
GAZE_DETECTION_AVAILABLE = False

# Import gaze detection with error handling
try:
    from gaze_detection import GazeDetection
    import cv2
    import numpy as np
    import os
    
    # Verify OpenCV Haar cascade files exist
    face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    eye_cascade_path = cv2.data.haarcascades + 'haarcascade_eye.xml'
    
    if not os.path.exists(face_cascade_path) or not os.path.exists(eye_cascade_path):
        logging.error(f"Required OpenCV Haar cascade files not found")
        GAZE_DETECTION_AVAILABLE = False
    else:
        GAZE_DETECTION_AVAILABLE = True
        
except ImportError as e:
    logging.error(f"Failed to import gaze detection modules: {e}")
    GAZE_DETECTION_AVAILABLE = False

class ProctoredExamTaking(QtWidgets.QWidget):
    # Signal for gaze status updates
    gaze_status_signal = QtCore.pyqtSignal(dict)
    
    def __init__(self, main_window, exam_id):
        global GAZE_DETECTION_AVAILABLE
        super().__init__()
        self.main_window = main_window
        self.exam_id = exam_id
        self.is_fullscreen = False
        self.violations_count = 0
        self.MAX_VIOLATIONS = 3
        self.last_violation_time = 0
        self.VIOLATION_COOLDOWN = 10  # seconds between violation counts
        
        try:
            # Initialize gaze detection if available
            if GAZE_DETECTION_AVAILABLE:
                try:
                    self.gaze_detector = GazeDetection(timeout_seconds=15)  # 15 seconds of looking away is a violation
                    self.camera_thread = None
                    self.is_camera_running = False
                    
                    # Connect the gaze status signal to the update function
                    self.gaze_status_signal.connect(self.update_gaze_status)
                    logging.info("Gaze detection initialized successfully")
                except Exception as init_error:
                    logging.error(f"Failed to initialize gaze detection: {init_error}")
                    GAZE_DETECTION_AVAILABLE = False
                    # Show warning about gaze detection initialization failure
                    QtWidgets.QMessageBox.warning(
                        self, 
                        "Proctoring Not Available",
                        f"The exam proctoring system failed to initialize: {init_error}\n\n"
                        "Your exam will continue without proctoring.",
                        QtWidgets.QMessageBox.StandardButton.Ok
                    )
            
            if not GAZE_DETECTION_AVAILABLE:
                # Show a warning that proctoring is not available
                QtWidgets.QMessageBox.warning(
                    self, 
                    "Proctoring Not Available",
                    "The exam proctoring system could not be initialized due to missing dependencies.\n\n"
                    "Your exam will continue without proctoring.",
                    QtWidgets.QMessageBox.StandardButton.Ok
                )
            
            self.initUI()
        except Exception as e:
            logging.error(f"Error initializing proctored exam: {e}")
            raise
        
    def initUI(self):
        try:
            # Main layout
            self.main_layout = QtWidgets.QVBoxLayout(self)
            self.main_layout.setContentsMargins(0, 0, 0, 0)
            self.main_layout.setSpacing(0)
            
            # Container for all content
            self.content_widget = QtWidgets.QWidget()
            self.content_layout = QtWidgets.QVBoxLayout(self.content_widget)
            
            global GAZE_DETECTION_AVAILABLE
            if GAZE_DETECTION_AVAILABLE:
                # Status bar for proctoring information
                self.status_bar = QtWidgets.QWidget()
                self.status_bar.setStyleSheet('''
                    QWidget {
                        background-color: #333;
                        color: white;
                        padding: 5px;
                    }
                    QLabel {
                        color: white;
                    }
                ''')
                status_layout = QtWidgets.QHBoxLayout(self.status_bar)
                status_layout.setContentsMargins(10, 5, 10, 5)
                
                # Camera preview
                self.camera_preview = QtWidgets.QLabel("Camera initializing...")
                self.camera_preview.setFixedSize(120, 90)
                self.camera_preview.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.camera_preview.setStyleSheet("border: 1px solid #666; background-color: #222;")
                status_layout.addWidget(self.camera_preview)
                
                # Status information
                status_info = QtWidgets.QVBoxLayout()
                
                self.status_label = QtWidgets.QLabel("Status: Initializing...")
                self.status_label.setStyleSheet("font-weight: bold;")
                status_info.addWidget(self.status_label)
                
                self.gaze_status_text = QtWidgets.QLabel("Please look at the camera")
                self.gaze_status_text.setStyleSheet("font-size: 14px; color: #00FF00;")
                status_info.addWidget(self.gaze_status_text)
                
                # Add violation counter
                self.violations_label = QtWidgets.QLabel(f"Violations: 0/{self.MAX_VIOLATIONS}")
                self.violations_label.setStyleSheet("font-weight: bold; color: white;")
                status_info.addWidget(self.violations_label)
                
                # Add violation timer
                self.violation_timer_label = QtWidgets.QLabel("Violation timer: 0s")
                self.violation_timer_label.setStyleSheet("color: white;")
                status_info.addWidget(self.violation_timer_label)
                
                status_layout.addLayout(status_info)
                status_layout.addStretch()
                
                # Add fullscreen warning
                self.fullscreen_warning = QtWidgets.QLabel("⚠️ Stay in fullscreen mode")
                self.fullscreen_warning.setStyleSheet("color: orange; font-weight: bold;")
                self.fullscreen_warning.hide()  # Hidden by default
                status_layout.addWidget(self.fullscreen_warning)
                
                # Add status bar to main layout
                self.content_layout.addWidget(self.status_bar)
            
            # Create a container for the exam content
            self.exam_container = QtWidgets.QWidget()
            self.exam_layout = QtWidgets.QVBoxLayout(self.exam_container)
            self.exam_layout.setContentsMargins(0, 0, 0, 0)
            
            # Create the standard exam taking widget and embed it
            self.exam_widget = ExamTaking(self.main_window, self.exam_id)
            
            # Override the submit_exam method to ensure we clean up resources
            original_submit = self.exam_widget.submit_exam
            def submit_exam_wrapper(*args, **kwargs):
                global GAZE_DETECTION_AVAILABLE
                if GAZE_DETECTION_AVAILABLE:
                    self.stop_camera()
                    self.exit_fullscreen()
                return original_submit(*args, **kwargs)
                
            self.exam_widget.submit_exam = submit_exam_wrapper
            
            self.exam_layout.addWidget(self.exam_widget)
            self.content_layout.addWidget(self.exam_container)
            
            self.main_layout.addWidget(self.content_widget)
            
            if GAZE_DETECTION_AVAILABLE:
                # Set up a timer to check if we're still in fullscreen
                self.fullscreen_timer = QtCore.QTimer(self)
                self.fullscreen_timer.timeout.connect(self.check_fullscreen)
                self.fullscreen_timer.start(1000)  # Check every second
        except Exception as e:
            logging.error(f"Error in initUI: {e}")
            raise
    
    def showEvent(self, event):
        """Called when the widget is shown"""
        super().showEvent(event)
        # Start in fullscreen and enable camera if available
        global GAZE_DETECTION_AVAILABLE
        if GAZE_DETECTION_AVAILABLE:
            QtCore.QTimer.singleShot(500, self.enter_fullscreen)
            QtCore.QTimer.singleShot(1000, self.start_camera)
    
    def hideEvent(self, event):
        """Called when the widget is hidden"""
        global GAZE_DETECTION_AVAILABLE
        if GAZE_DETECTION_AVAILABLE:
            self.stop_camera()
            self.exit_fullscreen()
        super().hideEvent(event)
    
    def enter_fullscreen(self):
        """Enter fullscreen mode"""
        if not self.is_fullscreen:
            self.main_window.showFullScreen()
            self.is_fullscreen = True
    
    def exit_fullscreen(self):
        """Exit fullscreen mode"""
        if self.is_fullscreen:
            self.main_window.showNormal()
            self.is_fullscreen = False
    
    def check_fullscreen(self):
        """Check if we're still in fullscreen mode"""
        if self.is_fullscreen and not self.main_window.isFullScreen():
            # User exited fullscreen, count as violation
            self.record_violation("Exited fullscreen mode")
            # Try to go back to fullscreen
            self.enter_fullscreen()
    
    def start_camera(self):
        """Start the camera thread for gaze detection"""
        global GAZE_DETECTION_AVAILABLE
        if not GAZE_DETECTION_AVAILABLE:
            return
        
        if not self.is_camera_running:
            self.is_camera_running = True
            self.camera_thread = threading.Thread(target=self.camera_worker)
            self.camera_thread.daemon = True
            self.camera_thread.start()
    
    def stop_camera(self):
        """Stop the camera thread"""
        global GAZE_DETECTION_AVAILABLE
        if not GAZE_DETECTION_AVAILABLE:
            return
            
        self.is_camera_running = False
        if self.camera_thread:
            self.camera_thread.join(timeout=1.0)
            self.camera_thread = None
    
    def camera_worker(self):
        """Worker function that runs in a separate thread to process camera frames"""
        global GAZE_DETECTION_AVAILABLE
        if not GAZE_DETECTION_AVAILABLE:
            return
            
        try:
            # Initialize camera
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                logging.error("Failed to open camera")
                self.gaze_status_signal.emit({
                    "status": "Camera not available", 
                    "is_error": True,
                    "is_camera_clear": False,
                    "is_face_detected": False,
                    "is_facing_camera": False,
                    "is_timeout": False
                })
                return
                
            try:
                while self.is_camera_running:
                    # Read frame
                    ret, frame = cap.read()
                    if not ret:
                        logging.error("Failed to capture frame")
                        continue
                    
                    # Process frame with gaze detection
                    result = self.gaze_detector.process_frame(frame)
                    
                    # Emit the status to the main thread
                    self.gaze_status_signal.emit(result)
                    
                    # Update the camera preview
                    self.update_camera_preview(frame)
                    
                    # Check if we need to record a violation
                    if result["is_timeout"]:
                        self.record_violation("Looking away for too long")
                    
                    # Sleep for a bit to reduce CPU usage
                    time.sleep(0.1)
                    
            finally:
                # Make sure we release the camera
                cap.release()
        except Exception as e:
            logging.error(f"Camera worker error: {e}")
            self.gaze_status_signal.emit({
                "status": f"Camera error: {str(e)}", 
                "is_error": True,
                "is_camera_clear": False,
                "is_face_detected": False,
                "is_facing_camera": False,
                "is_timeout": False
            })
    
    def update_camera_preview(self, frame):
        """Update the camera preview with the current frame"""
        try:
            # Convert the OpenCV BGR image to RGB for Qt
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Resize the frame to fit the preview
            preview_width = self.camera_preview.width()
            preview_height = self.camera_preview.height()
            resized_frame = cv2.resize(rgb_frame, (preview_width, preview_height))
            
            # Convert to QImage
            h, w, c = resized_frame.shape
            bytes_per_line = c * w
            q_img = QtGui.QImage(resized_frame.data, w, h, bytes_per_line, QtGui.QImage.Format.Format_RGB888)
            
            # Convert to QPixmap and set to label
            pixmap = QtGui.QPixmap.fromImage(q_img)
            
            # Use signal to update UI in main thread
            QtCore.QMetaObject.invokeMethod(
                self, 
                "set_camera_preview", 
                QtCore.Qt.ConnectionType.QueuedConnection,
                QtCore.Q_ARG(QtGui.QPixmap, pixmap)
            )
        except Exception as e:
            logging.error(f"Error updating camera preview: {e}")
    
    @QtCore.pyqtSlot(QtGui.QPixmap)
    def set_camera_preview(self, pixmap):
        """Set the camera preview pixmap (called in main thread)"""
        self.camera_preview.setPixmap(pixmap)
        self.camera_preview.setScaledContents(True)
    
    def update_gaze_status(self, result):
        """Update the UI with the current gaze status (called in main thread)"""
        global GAZE_DETECTION_AVAILABLE
        if not GAZE_DETECTION_AVAILABLE:
            return
            
        # Update the status label
        status_text = result["status"]
        status_color = "red"
        
        if result["is_facing_camera"] and result["is_camera_clear"] and result["is_face_detected"]:
            status_text = "Properly facing camera"
            status_color = "green"
        
        self.status_label.setText(f"Status: {status_text}")
        self.status_label.setStyleSheet(f"color: {status_color};")
        
        # Update violation timer if applicable
        if "violation_duration" in result:
            violation_seconds = int(result["violation_duration"])
            self.violation_timer_label.setText(f"Violation timer: {violation_seconds}s")
            
            # Change color based on how close to violation threshold
            if violation_seconds > 7:  # Close to the 10s threshold
                self.violation_timer_label.setStyleSheet("color: red; font-weight: bold;")
            elif violation_seconds > 5:
                self.violation_timer_label.setStyleSheet("color: orange; font-weight: bold;")
            elif violation_seconds > 0:
                self.violation_timer_label.setStyleSheet("color: yellow;")
            else:
                self.violation_timer_label.setStyleSheet("color: white;")
        
        # Check for violations
        if result.get("violation_triggered", False):
            violation_type = result.get("violation_type", "unknown")
            reason = ""
            
            if violation_type == "unclear_camera":
                reason = "Camera image is not clear"
            elif violation_type == "face_not_detected":
                reason = "Face not detected"
            elif violation_type == "not_facing_camera":
                reason = "Not facing camera directly"
            else:
                reason = "Unknown violation"
                
            self.record_violation(reason)
        
        # Check for timeout
        if result["is_timeout"]:
            # This is a long-term timeout (e.g., not facing camera for 60 seconds)
            # We may want to handle this differently than the 10-second violations
            pass
    
    def record_violation(self, reason):
        """Record a proctoring violation"""
        global GAZE_DETECTION_AVAILABLE
        if not GAZE_DETECTION_AVAILABLE:
            return
            
        current_time = time.time()
        
        # Check if we're still in cooldown period
        if current_time - self.last_violation_time < self.VIOLATION_COOLDOWN:
            return
            
        # Record the violation
        self.violations_count += 1
        self.last_violation_time = current_time
        
        # Update violation counter in UI
        self.violations_label.setText(f"Violations: {self.violations_count}/{self.MAX_VIOLATIONS}")
        if self.violations_count >= self.MAX_VIOLATIONS - 1:  # Warning color when close to max
            self.violations_label.setStyleSheet("color: orange; font-weight: bold;")
        if self.violations_count >= self.MAX_VIOLATIONS:
            self.violations_label.setStyleSheet("color: red; font-weight: bold;")
            
        # Log the violation
        logging.warning(f"Proctoring violation recorded: {reason}. Count: {self.violations_count}/{self.MAX_VIOLATIONS}")
        
        if self.violations_count >= self.MAX_VIOLATIONS:
            self.handle_max_violations()
        else:
            # Show a warning
            self.show_violation_warning(reason)
    
    def show_violation_warning(self, reason):
        """Show a warning about a proctoring violation"""
        global GAZE_DETECTION_AVAILABLE
        if not GAZE_DETECTION_AVAILABLE:
            return
            
        # Create a warning message box
        msg = QtWidgets.QMessageBox(self)
        msg.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        msg.setWindowTitle("Proctoring Violation")
        msg.setText(f"Proctoring violation detected: {reason}")
        msg.setInformativeText(f"You have {self.violations_count} out of {self.MAX_VIOLATIONS} allowed violations.\n\nIf you reach {self.MAX_VIOLATIONS} violations, your exam will be terminated automatically and you will receive a score of zero.")
        msg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
        msg.setStyleSheet("color: black;")  # Ensure text is visible
        
        # Show the message box
        msg.exec()
    
    def handle_max_violations(self):
        """Handle reaching the maximum number of violations"""
        global GAZE_DETECTION_AVAILABLE
        if not GAZE_DETECTION_AVAILABLE:
            return
            
        # Stop the camera
        self.stop_camera()
        
        # Show a message box
        msg = QtWidgets.QMessageBox(self)
        msg.setIcon(QtWidgets.QMessageBox.Icon.Critical)
        msg.setWindowTitle("Exam Terminated")
        msg.setText("Maximum proctoring violations reached")
        msg.setInformativeText("Your exam has been terminated due to too many proctoring violations. You will receive a score of zero for this exam.")
        msg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
        msg.setStyleSheet("color: black;")  # Ensure text is visible
        
        # Show the message box
        msg.exec()
        
        # Submit a zero score for the exam
        self.submit_zero_score()
        
        # Return to the dashboard
        from student_dashboard import StudentDashboard
        dashboard = StudentDashboard(self.main_window)
        self.main_window.stackedWidget.addWidget(dashboard)
        self.main_window.stackedWidget.setCurrentWidget(dashboard)
    
    def submit_zero_score(self):
        """Submit a score of zero for the exam due to proctoring violations"""
        try:
            from supabase_connection import create_connection
            supabase = create_connection()
            
            # Get the current user
            student_username = self.main_window.current_user
            
            # Submit a zero score using the existing schema
            response = supabase.table('exam_results').insert({
                'exam_id': self.exam_id,
                'student_username': student_username,
                'score': 0,
                'completed_at': datetime.datetime.now().isoformat()
            }).execute()
            
            logging.info(f"Submitted zero score for {student_username} due to proctoring violations")
            
        except Exception as e:
            logging.error(f"Failed to submit zero score: {e}")
            # Show error message
            msg = QtWidgets.QMessageBox(self)
            msg.setIcon(QtWidgets.QMessageBox.Icon.Critical)
            msg.setWindowTitle("Error")
            msg.setText("Failed to submit exam result")
            msg.setInformativeText(f"Error: {str(e)}")
            msg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
            msg.setStyleSheet("color: black;")  # Ensure text is visible
            msg.exec()