from PyQt6 import QtWidgets, QtCore
from supabase_connection import create_connection

class ExamManagement(QtWidgets.QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.initUI()

    def initUI(self):
        layout = QtWidgets.QVBoxLayout(self)

        try:
            supabase = create_connection()
            exams_response = supabase.table('exams') \
                .select('id, name, status, exam_date') \
                .eq('teacher_username', self.main_window.current_user) \
                .execute()

            data = exams_response.data
            if not data:
                layout.addWidget(QtWidgets.QLabel("No exams created yet."))
                return

            for exam in data:
                card = QtWidgets.QLabel(f"{exam['name']} | {exam['status']} | {exam['exam_date']}")
                layout.addWidget(card)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))