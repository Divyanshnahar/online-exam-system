import unittest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest
import sys
import os
import hashlib
from unittest.mock import patch, MagicMock

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from login_page import LoginPage
from signup_page import SignupPage
from student_dashboard import StudentDashboard
from teacher_dashboard import TeacherDashboard
from admin_dashboard import AdminDashboard
from main import MainWindow

class TestDashboardFunctionality(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create QApplication instance
        cls.app = QApplication(sys.argv)

    def setUp(self):
        # Create main window instance
        self.main_window = MainWindow()
        self.login_page = LoginPage(self.main_window)
        self.signup_page = SignupPage(self.main_window)
        self.student_dashboard = StudentDashboard(self.main_window)
        self.teacher_dashboard = TeacherDashboard(self.main_window)
        self.admin_dashboard = AdminDashboard(self.main_window)

    def test_student_login(self):
        # Mock the database connection
        with patch('db_connection.create_connection') as mock_conn:
            # Setup mock response
            mock_supabase = MagicMock()
            mock_conn.return_value = mock_supabase
            
            # Mock successful login response
            mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
                {'username': 'divyansh', 'user_type': 'Student'}
            ]

            # Set test credentials
            self.login_page.username.setText('divyansh')
            self.login_page.password.setText('12345678')
            self.login_page.user_type_combo.setCurrentText('Student')

            # Trigger login
            self.login_page.login()

            # Verify user info was set
            self.assertEqual(self.main_window.current_user, 'divyansh')
            self.assertEqual(self.main_window.current_user_type, 'Student')

    def test_teacher_login(self):
        # Mock the database connection
        with patch('db_connection.create_connection') as mock_conn:
            # Setup mock response
            mock_supabase = MagicMock()
            mock_conn.return_value = mock_supabase
            
            # Mock successful login response
            mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
                {'username': 'divyanshteacher', 'user_type': 'Teacher'}
            ]

            # Set test credentials
            self.login_page.username.setText('divyanshteacher')
            self.login_page.password.setText('12345678')
            self.login_page.user_type_combo.setCurrentText('Teacher')

            # Trigger login
            self.login_page.login()

            # Verify user info was set
            self.assertEqual(self.main_window.current_user, 'divyanshteacher')
            self.assertEqual(self.main_window.current_user_type, 'Teacher')

    def test_admin_login(self):
        # Mock the database connection
        with patch('db_connection.create_connection') as mock_conn:
            # Setup mock response
            mock_supabase = MagicMock()
            mock_conn.return_value = mock_supabase
            
            # Mock successful login response
            mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
                {'username': 'divyanshadmin', 'user_type': 'Admin'}
            ]

            # Set test credentials
            self.login_page.username.setText('divyanshadmin')
            self.login_page.password.setText('12345678')
            self.login_page.user_type_combo.setCurrentText('Admin')

            # Trigger login
            self.login_page.login()

            # Verify user info was set
            self.assertEqual(self.main_window.current_user, 'divyanshadmin')
            self.assertEqual(self.main_window.current_user_type, 'Admin')

    def test_student_dashboard_buttons(self):
        # Set current user
        self.main_window.current_user = 'divyansh'
        self.main_window.current_user_type = 'Student'
        
        # Test exam list button
        exam_list_button = self.student_dashboard.findChild(QtWidgets.QPushButton, 'exam_list_button')
        if exam_list_button:
            QTest.mouseClick(exam_list_button, Qt.MouseButton.LeftButton)
            # Verify exam list was loaded
            self.assertTrue(hasattr(self.student_dashboard, 'exam_list'))

    def test_teacher_dashboard_buttons(self):
        # Set current user
        self.main_window.current_user = 'divyanshteacher'
        self.main_window.current_user_type = 'Teacher'
        
        # Test create exam button
        create_exam_button = self.teacher_dashboard.findChild(QtWidgets.QPushButton, 'create_exam_button')
        if create_exam_button:
            QTest.mouseClick(create_exam_button, Qt.MouseButton.LeftButton)
            # Verify exam creation form was loaded
            self.assertTrue(hasattr(self.teacher_dashboard, 'exam_creation_form'))

    def test_admin_dashboard_buttons(self):
        # Set current user
        self.main_window.current_user = 'divyanshadmin'
        self.main_window.current_user_type = 'Admin'
        
        # Test user management button
        user_management_button = self.admin_dashboard.findChild(QtWidgets.QPushButton, 'user_management_button')
        if user_management_button:
            QTest.mouseClick(user_management_button, Qt.MouseButton.LeftButton)
            # Verify user list was loaded
            self.assertTrue(hasattr(self.admin_dashboard, 'user_list'))

    @classmethod
    def tearDownClass(cls):
        # Clean up QApplication
        cls.app.quit()

if __name__ == '__main__':
    unittest.main() 