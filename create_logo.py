import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPainter, QPixmap, QFont, QColor, QPen, QBrush
from PyQt6.QtCore import Qt, QRect

def create_logo():
    # Create application instance (required for Qt operations)
    app = QApplication([])
    
    # Create a transparent pixmap
    pixmap = QPixmap(800, 400)
    pixmap.fill(QColor(255, 255, 220))  # Light yellow background
    
    # Create painter
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # Draw icon
    painter.setPen(QPen(QColor("#FFD700"), 8))  # Gold color
    painter.setBrush(QBrush(QColor("#FFD700")))
    
    # Draw computer/monitor icon
    painter.drawRect(250, 100, 150, 100)  # Monitor
    painter.drawRect(230, 100, 190, 10)   # Monitor top
    painter.drawRect(290, 200, 70, 20)    # Monitor stand
    painter.drawRect(270, 220, 110, 10)   # Monitor base
    
    # Draw person icon
    painter.drawEllipse(200, 150, 50, 50)  # Head
    painter.drawLine(225, 200, 225, 250)   # Body
    painter.drawLine(225, 220, 200, 240)   # Left arm
    painter.drawLine(225, 220, 250, 240)   # Right arm
    
    # Draw text
    font = QFont("Script", 72, QFont.Weight.Bold)
    painter.setFont(font)
    painter.setPen(QColor("#000000"))
    
    # Draw "Proctor Prime" text
    painter.drawText(QRect(400, 100, 350, 200), Qt.AlignmentFlag.AlignCenter, "Proctor\nPrime")
    
    # End painting
    painter.end()
    
    # Ensure assets directory exists
    os.makedirs("assets", exist_ok=True)
    
    # Save the pixmap
    pixmap.save("assets/logo.png")
    print("Logo created successfully at assets/logo.png")

if __name__ == "__main__":
    create_logo()
