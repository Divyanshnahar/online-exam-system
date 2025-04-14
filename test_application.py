import time
import os
import sys
import subprocess
from pywinauto.application import Application
from pywinauto.keyboard import send_keys
from pywinauto import Desktop
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename='test_results.log',
                    filemode='w')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

class OnlineExamSystemTest:
    def __init__(self):
        self.app = None
        self.main_window = None
        # Updated credentials as provided
        self.student_username = "divyansh"
        self.teacher_username = "divyanshteacher"
        self.admin_username = "divyanshadmin"
        self.password = "12345678"  # Same password for all users

    def start_application(self):
        """Start the Online Exam System application"""
        try:
            # Start the application as a subprocess
            logging.info("Starting the application...")
            app_path = os.path.join(os.getcwd(), "main.py")
            self.process = subprocess.Popen([sys.executable, app_path])
            
            # Give the application time to start up
            logging.info("Waiting for application to start...")
            time.sleep(10)  # Increased wait time to 10 seconds
            
            # Try to connect to the application using a more flexible approach
            desktop = Desktop(backend="uia")
            # Look for any window that might be our application
            all_windows = desktop.windows()
            
            for window in all_windows:
                window_text = window.window_text()
                logging.info(f"Found window: {window_text}")
                
                # Try to identify our application window
                if "Online" in window_text or "Exam" in window_text or "System" in window_text:
                    self.main_window = window
                    logging.info(f"Connected to application window: {window_text}")
                    return True
            
            # If we get here, we couldn't find the application window
            logging.error("Could not find application window")
            return False
            
        except Exception as e:
            logging.error(f"Failed to start application: {str(e)}")
            return False

    def close_application(self):
        """Close the application"""
        try:
            if self.process:
                self.process.terminate()
                logging.info("Application closed")
            return True
        except Exception as e:
            logging.error(f"Failed to close application: {e}")
            return False

    def test_login(self, username, password, user_type="Student"):
        """Test the login functionality"""
        try:
            logging.info(f"Testing login with username: {username}, user_type: {user_type}")
            
            # Wait for the login page to fully load
            time.sleep(2)
            
            # First, print all controls to help with debugging
            logging.info("Available controls on the page:")
            for control in self.main_window.descendants():
                try:
                    control_text = control.window_text()
                    control_class = control.element_info.control_type
                    if control_text:
                        logging.info(f"Control: {control_class} - '{control_text}'")
                except Exception:
                    pass
            
            # Find the user type selection (dropdown/combobox)
            try:
                # Look for dropdown/combobox elements
                combo_boxes = self.main_window.descendants(control_type="ComboBox")
                if combo_boxes:
                    user_type_combo = combo_boxes[0]
                    logging.info(f"Found user type combo box: {user_type_combo.window_text()}")
                    user_type_combo.select(user_type)
                    logging.info(f"Selected user type: {user_type}")
                else:
                    # Try to find by text labels
                    for control in self.main_window.descendants():
                        if control.window_text() == "Student" or control.window_text() == "Teacher" or control.window_text() == "Admin":
                            control.click_input()
                            logging.info(f"Clicked on user type: {control.window_text()}")
                            break
            except Exception as e:
                logging.warning(f"Error selecting user type: {str(e)}")
            
            # Find the username and password fields
            try:
                # Look for edit boxes
                edit_boxes = self.main_window.descendants(control_type="Edit")
                
                # Enter username
                if len(edit_boxes) >= 1:
                    username_field = edit_boxes[0]
                    username_field.set_text(username)
                    logging.info(f"Entered username: {username}")
                    
                    # Enter password
                    if len(edit_boxes) >= 2:
                        password_field = edit_boxes[1]
                        password_field.set_text(password)
                        logging.info("Entered password")
                    else:
                        logging.warning("Password field not found")
                else:
                    logging.warning("Username field not found")
            except Exception as e:
                logging.warning(f"Error entering credentials: {str(e)}")
            
            # Find and click the login button
            try:
                # Look for buttons with "Login" text
                login_buttons = []
                for control in self.main_window.descendants():
                    if control.element_info.control_type == "Button" and "login" in control.window_text().lower():
                        login_buttons.append(control)
                
                if login_buttons:
                    login_button = login_buttons[0]
                    logging.info(f"Found login button: {login_button.window_text()}")
                    login_button.click_input()
                    logging.info("Clicked login button")
                else:
                    # Try to find by position or other attributes
                    buttons = self.main_window.descendants(control_type="Button")
                    if buttons:
                        # Assume the main button is the login button
                        login_button = buttons[0]
                        logging.info(f"Using first button as login: {login_button.window_text()}")
                        login_button.click_input()
                        logging.info("Clicked possible login button")
                    else:
                        logging.warning("No login button found")
                        return False
            except Exception as e:
                logging.warning(f"Error clicking login button: {str(e)}")
                return False
            
            # Wait for login to process
            time.sleep(5)
            
            # Check if login was successful
            # This is a simple check - we just look for any change in the UI
            # that might indicate we've moved to a dashboard
            try:
                # Check for dashboard elements or success messages
                dashboard_found = False
                for control in self.main_window.descendants():
                    control_text = control.window_text()
                    if "dashboard" in control_text.lower() or "welcome" in control_text.lower():
                        logging.info(f"Found dashboard element: {control_text}")
                        dashboard_found = True
                        break
                
                if dashboard_found:
                    logging.info(f"Login successful for {user_type}")
                    return True
                else:
                    # Check for error messages
                    error_found = False
                    for control in self.main_window.descendants():
                        control_text = control.window_text()
                        if "error" in control_text.lower() or "invalid" in control_text.lower() or "failed" in control_text.lower():
                            logging.warning(f"Login error message: {control_text}")
                            error_found = True
                            break
                    
                    if error_found:
                        logging.warning("Login failed - error message found")
                    else:
                        logging.warning("Login result unclear - no dashboard or error message found")
                    
                    return False
            except Exception as e:
                logging.warning(f"Error checking login result: {str(e)}")
                return False
                
        except Exception as e:
            logging.error(f"Error during login test: {str(e)}")
            return False

    def test_signup(self, username, password, user_type="Student"):
        """Test the signup functionality"""
        try:
            logging.info(f"Testing signup with username: {username}, user_type: {user_type}")
            
            # Go to signup page
            signup_link = self.main_window.child_window(title="Sign up", control_type="Hyperlink")
            signup_link.click()
            time.sleep(1)
            
            # Select user type
            user_type_combo = self.main_window.child_window(auto_id="user_type_combo")
            user_type_combo.select(user_type)
            
            # Enter username
            username_field = self.main_window.child_window(title="Username", control_type="Edit")
            username_field.set_text(username)
            
            # Enter password
            password_field = self.main_window.child_window(title="Password", control_type="Edit")
            password_field.set_text(password)
            
            # Confirm password
            confirm_password_field = self.main_window.child_window(title="Confirm Password", control_type="Edit")
            confirm_password_field.set_text(password)
            
            # Click signup button
            signup_button = self.main_window.child_window(title="Create Account", control_type="Button")
            signup_button.click()
            
            # Wait for confirmation or error
            time.sleep(2)
            
            # Check if signup was successful
            try:
                success_dialog = Desktop(backend="uia").window(title="Success")
                if success_dialog.exists():
                    success_text = success_dialog.window_text()
                    logging.info(f"Signup successful: {success_text}")
                    # Close the success dialog
                    success_dialog.child_window(title="OK", control_type="Button").click()
                    return True
            except Exception:
                # Check if error message appeared
                try:
                    error_dialog = Desktop(backend="uia").window(title="Error")
                    if error_dialog.exists():
                        error_text = error_dialog.window_text()
                        logging.warning(f"Signup failed with error: {error_text}")
                        # Close the error dialog
                        error_dialog.child_window(title="OK", control_type="Button").click()
                        return False
                except Exception:
                    pass
                
                logging.warning("Signup result unclear - no confirmation dialog found")
                return False
                
        except Exception as e:
            logging.error(f"Error during signup test: {e}")
            return False

    def test_student_dashboard(self):
        """Test student dashboard functionality"""
        try:
            logging.info("Testing student dashboard functionality")
            
            # Check if we're on the student dashboard
            dashboard_title = self.main_window.child_window(title="Student Dashboard", control_type="Text")
            if not dashboard_title.exists():
                logging.warning("Not on student dashboard")
                return False
                
            # Test clicking on "Take Exams" card
            take_exams_card = self.main_window.child_window(title="Take Exams", control_type="Text")
            if take_exams_card.exists():
                take_exams_card.click()
                time.sleep(1)
                
                # Check if we're on the exams page
                exams_title = self.main_window.child_window(title="Available Exams", control_type="Text")
                if exams_title.exists():
                    logging.info("Successfully navigated to Available Exams page")
                    
                    # Go back to dashboard
                    back_button = self.main_window.child_window(title="Back to Dashboard", control_type="Button")
                    back_button.click()
                    time.sleep(1)
                else:
                    logging.warning("Failed to navigate to Available Exams page")
            else:
                logging.warning("Take Exams card not found")
                
            # Test clicking on "My Results" card
            my_results_card = self.main_window.child_window(title="My Results", control_type="Text")
            if my_results_card.exists():
                my_results_card.click()
                time.sleep(1)
                
                # Check if we're on the results page
                results_title = self.main_window.child_window(title="My Exam Results", control_type="Text")
                if results_title.exists():
                    logging.info("Successfully navigated to My Exam Results page")
                    
                    # Go back to dashboard
                    back_button = self.main_window.child_window(title="Back to Dashboard", control_type="Button")
                    back_button.click()
                    time.sleep(1)
                else:
                    logging.warning("Failed to navigate to My Exam Results page")
            else:
                logging.warning("My Results card not found")
                
            # Test logout
            logout_button = self.main_window.child_window(title="Logout", control_type="Button")
            if logout_button.exists():
                logout_button.click()
                time.sleep(1)
                
                # Check if we're back on the login page
                login_button = self.main_window.child_window(title="Login", control_type="Button")
                if login_button.exists():
                    logging.info("Successfully logged out")
                    return True
                else:
                    logging.warning("Failed to logout properly")
                    return False
            else:
                logging.warning("Logout button not found")
                return False
                
        except Exception as e:
            logging.error(f"Error during student dashboard test: {e}")
            return False

    def test_teacher_dashboard(self):
        """Test teacher dashboard functionality"""
        try:
            logging.info("Testing teacher dashboard functionality")
            
            # Check if we're on the teacher dashboard
            dashboard_title = self.main_window.child_window(title="Teacher Dashboard", control_type="Text")
            if not dashboard_title.exists():
                logging.warning("Not on teacher dashboard")
                return False
                
            # Test clicking on "Create Exam" card
            create_exam_card = self.main_window.child_window(title="Create Exam", control_type="Text")
            if create_exam_card.exists():
                create_exam_card.click()
                time.sleep(1)
                
                # Check if we're on the exam creation page
                create_title = self.main_window.child_window(title="Create New Exam", control_type="Text")
                if create_title.exists():
                    logging.info("Successfully navigated to Create New Exam page")
                    
                    # Go back to dashboard
                    back_button = self.main_window.child_window(title="Back to Dashboard", control_type="Button")
                    back_button.click()
                    time.sleep(1)
                else:
                    logging.warning("Failed to navigate to Create New Exam page")
            else:
                logging.warning("Create Exam card not found")
                
            # Test clicking on "View Exams" card
            view_exams_card = self.main_window.child_window(title="View Exams", control_type="Text")
            if view_exams_card.exists():
                view_exams_card.click()
                time.sleep(1)
                
                # Check if we're on the view exams page
                exams_title = self.main_window.child_window(title="Your Exams", control_type="Text")
                if exams_title.exists():
                    logging.info("Successfully navigated to Your Exams page")
                    
                    # Go back to dashboard
                    back_button = self.main_window.child_window(title="Back to Dashboard", control_type="Button")
                    back_button.click()
                    time.sleep(1)
                else:
                    logging.warning("Failed to navigate to Your Exams page")
            else:
                logging.warning("View Exams card not found")
                
            # Test logout
            logout_button = self.main_window.child_window(title="Logout", control_type="Button")
            if logout_button.exists():
                logout_button.click()
                time.sleep(1)
                
                # Check if we're back on the login page
                login_button = self.main_window.child_window(title="Login", control_type="Button")
                if login_button.exists():
                    logging.info("Successfully logged out")
                    return True
                else:
                    logging.warning("Failed to logout properly")
                    return False
            else:
                logging.warning("Logout button not found")
                return False
                
        except Exception as e:
            logging.error(f"Error during teacher dashboard test: {e}")
            return False

    def run_all_tests(self):
        """Run all tests in sequence"""
        try:
            logging.info("=== Starting Online Exam System Tests ===")
            
            # Start the application
            if not self.start_application():
                logging.error("Failed to start application. Aborting tests.")
                return False
                
            time.sleep(2)  # Wait for application to fully load
            
            # Test signup with a new user
            new_username = f"testuser_{int(time.time())}"
            signup_success = self.test_signup(new_username, self.password, "Student")
            
            # Test login with existing credentials
            login_success = self.test_login(self.student_username, self.password, "Student")
            
            if login_success:
                # Test student dashboard functionality
                dashboard_success = self.test_student_dashboard()
            
            # Test login as teacher
            teacher_login = self.test_login(self.teacher_username, self.password, "Teacher")
            
            if teacher_login:
                # Test teacher dashboard functionality
                teacher_dashboard_success = self.test_teacher_dashboard()
            
            # Close the application
            self.close_application()
            
            logging.info("=== All tests completed ===")
            return True
            
        except Exception as e:
            logging.error(f"Error during test execution: {e}")
            self.close_application()
            return False


if __name__ == "__main__":
    # Run the tests
    test = OnlineExamSystemTest()
    
    # Simplified test flow - just focus on starting the app and basic login
    try:
        logging.info("=== Starting Online Exam System Tests ===")
        
        # Start the application
        if test.start_application():
            logging.info("Application started successfully")
            
            # Wait for application to fully load
            time.sleep(5)
            
            # Print window information to help with debugging
            if test.main_window:
                logging.info(f"Main window title: {test.main_window.window_text()}")
                logging.info("Main window controls:")
                for control in test.main_window.descendants():
                    try:
                        control_text = control.window_text()
                        control_class = control.element_info.control_type
                        if control_text:
                            logging.info(f"- {control_class}: '{control_text}'")
                    except Exception:
                        pass
                
                # Try to log in as student
                logging.info(f"Attempting to log in as student: {test.student_username}")
                test.test_login(test.student_username, test.password, "Student")
            else:
                logging.error("Main window not found")
        else:
            logging.error("Failed to start application")
            
        # Close the application
        test.close_application()
        logging.info("=== Tests completed ===")
        
    except Exception as e:
        logging.error(f"Error during test execution: {str(e)}")
        # Make sure to close the application
        test.close_application()
