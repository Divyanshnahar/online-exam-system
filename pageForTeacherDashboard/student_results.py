from PyQt6 import QtWidgets
from supabase_connection import create_connection

class StudentResults(QtWidgets.QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.initUI()

    def initUI(self):
        layout = QtWidgets.QVBoxLayout(self)

        try:
            supabase = create_connection()
            exams_resp = supabase.table('exams') \
                .select('id, name') \
                .eq('teacher_username', self.main_window.current_user) \
                .execute()

            exam_ids = [e['id'] for e in exams_resp.data]
            exam_names = {e['id']: e['name'] for e in exams_resp.data}

            results_resp = supabase.table('exam_results') \
                .select('exam_id, student_username, score, total_marks') \
                .in_('exam_id', exam_ids) \
                .execute()

            if not results_resp.data:
                layout.addWidget(QtWidgets.QLabel("No student results available."))
                return

            for result in results_resp.data:
                name = exam_names.get(result['exam_id'], 'Unknown')
                label = QtWidgets.QLabel(f"{result['student_username']} - {name}: {result['score']} / {result['total_marks']}")
                layout.addWidget(label)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))