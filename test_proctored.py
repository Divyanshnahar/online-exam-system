import sys
import traceback

print("Python version:", sys.version)
print("Python path:", sys.path)

try:
    print("Attempting to import ProctoredExamTaking...")
    
    # First try absolute import
    try:
        import exam_taking_proctored
        print("Successfully imported exam_taking_proctored module")
        print("Module contents:", dir(exam_taking_proctored))
        
        ProctoredExamTaking = exam_taking_proctored.ProctoredExamTaking
        print("Successfully retrieved ProctoredExamTaking class")
    except ImportError as e:
        print(f"Absolute import failed: {e}")
        
        # If absolute import fails, try relative import
        try:
            from exam_taking_proctored import ProctoredExamTaking
            print("Successfully imported ProctoredExamTaking using relative import")
        except ImportError as e:
            print(f"Relative import also failed: {e}")
            raise
    
    print("Checking if dependencies are available...")
    try:
        from gaze_detection import GazeDetection
        print("GazeDetection import successful")
        import cv2
        print("OpenCV import successful")
        import numpy as np
        print("NumPy import successful")
        import mediapipe as mp
        print("MediaPipe import successful")
        print("All dependencies are available")
    except ImportError as e:
        print(f"Warning: Some dependencies are missing: {e}")
        
    # Simple empty mock classes to test instantiation
    class MockMainWindow:
        def __init__(self):
            self.fullscreen = False
            
        def showFullScreen(self):
            self.fullscreen = True
            print("Mock main window entered fullscreen mode")
            
        def showNormal(self):
            self.fullscreen = False
            print("Mock main window exited fullscreen mode")
            
        def isFullScreen(self):
            return self.fullscreen
    
    # Try to instantiate the class
    print("Attempting to instantiate ProctoredExamTaking...")
    mock_window = MockMainWindow()
    
    # We won't actually create the instance since it requires a proper QApplication
    # But we can print the class info
    print(f"ProctoredExamTaking class: {ProctoredExamTaking}")
    print("Class initialization requirements:", ProctoredExamTaking.__init__.__code__.co_varnames)
    
    print("Test completed successfully")
    
except Exception as e:
    print(f"Error: {e}")
    print("Traceback:")
    traceback.print_exc() 