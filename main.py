from PyQt6 import QtWidgets, QtCore
from signup_page import SignupPage
from login_page import LoginPage
from student_dashboard import StudentDashboard
from teacher_dashboard import TeacherDashboard
from admin_dashboard import AdminDashboard
from styles import COMMON_STYLES
from exam_creation import ExamCreation


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Online Examination System")
        
        # Get the screen dimensions
        screen = QtWidgets.QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        self.setGeometry(0, 0, screen_geometry.width(), screen_geometry.height())
        self.setStyleSheet(COMMON_STYLES['window_background'])

        self.stackedWidget = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stackedWidget)

        # Store current user info
        self.current_user = None
        self.current_user_type = None

        self.signup_page = SignupPage(self)
        self.login_page = LoginPage(self)
        self.student_dashboard = StudentDashboard(self)
        self.teacher_dashboard = TeacherDashboard(self)
        self.admin_dashboard = AdminDashboard(self)

        self.stackedWidget.addWidget(self.signup_page)
        self.stackedWidget.addWidget(self.login_page)
        self.stackedWidget.addWidget(self.student_dashboard)
        self.stackedWidget.addWidget(self.teacher_dashboard)
        self.stackedWidget.addWidget(self.admin_dashboard)
    

        self.stackedWidget.setCurrentWidget(self.login_page)

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec()

