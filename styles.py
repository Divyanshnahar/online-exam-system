COMMON_STYLES = {
    'window_background': 'background-color: #F8F8F8;',
    
    'input_field': '''
        QLineEdit, QComboBox {
            padding: 12px;
            border: 1px solid #E0E0E0;
            border-radius: 5px;
            background: white;
            font-size: 14px;
            color: #333333;
        }
        QComboBox QAbstractItemView {
            background-color: white;
            color: #333333;
            selection-background-color: #6C63FF;
            selection-color: white;
        }
        QComboBox::drop-down {
            border: none;
        }
    ''',
    
    'primary_button': '''
        QPushButton {
            padding: 12px;
            background: #6C63FF;
            border: none;
            border-radius: 5px;
            color: white;
            font-weight: bold;
            font-size: 14px;
            margin: 10px 0;
        }
        QPushButton:hover {
            background: #5952cc;
        }
    ''',
    
    'secondary_button': '''
        QPushButton {
            padding: 12px;
            background: #FFFFFF;
            border: 1px solid #6C63FF;
            border-radius: 5px;
            color: #6C63FF;
            font-weight: bold;
            font-size: 14px;
            margin: 10px 0;
        }
        QPushButton:hover {
            background: #F0F0FF;
        }
    ''',
    
    'title_label': '''
        font-size: 28px;
        font-weight: bold;
        color: #333333;
        margin: 20px 0;
    ''',
    
    'field_label': '''
        color: #555;
        font-size: 14px;
        margin-bottom: 5px;
    ''',
    
    'link_text': '''
        color: #6C63FF;
        text-decoration: none;
        font-size: 14px;
    ''',
    
    'message_box': '''
        QMessageBox {
            background-color: white;
        }
        QMessageBox QLabel {
            color: #333333;
            font-size: 14px;
        }
        QMessageBox QPushButton {
            padding: 6px 14px;
            background: #6C63FF;
            border: none;
            border-radius: 4px;
            color: white;
            font-weight: bold;
            min-width: 80px;
        }
        QMessageBox QPushButton:hover {
            background: #5952cc;
        }
        QMessageBox QLabel#qt_msgbox_label {
            color: #333333;
            font-size: 14px;
            min-width: 300px;
        }
    ''',
}