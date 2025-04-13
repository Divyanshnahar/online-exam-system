from PyQt6 import QtWidgets
from supabase_connection import create_connection

class StudentManagement(QtWidgets.QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.initUI()

    def initUI(self):
        layout = QtWidgets.QVBoxLayout(self)

        try:
            supabase = create_connection()
            response = supabase.table('users') \
                .select('username') \
                .eq('user_type', 'Student') \
                .execute()

            if not response.data:
                layout.addWidget(QtWidgets.QLabel("No students found."))
                return

            for student in response.data:
                layout.addWidget(QtWidgets.QLabel(student['username']))

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))