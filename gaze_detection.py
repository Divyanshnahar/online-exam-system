import cv2
import numpy as np
import time
import logging
import os

class GazeDetection:
    def __init__(self, timeout_seconds=60):
        """
        Initialize the gaze detection system using OpenCV
        
        Args:
            timeout_seconds (int): Number of seconds before triggering a timeout alert
        """
        try:
            # Initialize OpenCV face and eye cascade classifiers
            face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            eye_cascade_path = cv2.data.haarcascades + 'haarcascade_eye.xml'
            
            # Verify that the cascade files exist
            if not os.path.exists(face_cascade_path):
                raise FileNotFoundError(f"Face cascade file not found: {face_cascade_path}")
            if not os.path.exists(eye_cascade_path):
                raise FileNotFoundError(f"Eye cascade file not found: {eye_cascade_path}")
            
            # Load the cascades
            self.face_cascade = cv2.CascadeClassifier(face_cascade_path)
            self.eye_cascade = cv2.CascadeClassifier(eye_cascade_path)
            
            logging.info("OpenCV face and eye detectors initialized successfully")
            
            # State variables
            self.last_facing_camera_time = time.time()
            self.warning_shown = False
            self.is_camera_clear = True
            self.is_face_detected = False
            self.is_facing_camera = False
            
            # Violation tracking
            self.violation_start_time = None
            self.violation_duration = 0
            self.violation_threshold = 10  # 10 seconds threshold for violations
            
            # Constants
            self.GAZE_TIMEOUT = timeout_seconds
        except Exception as e:
            logging.error(f"Failed to initialize OpenCV detectors: {e}")
            raise
    
    def check_image_quality(self, frame):
        """
        Check if the camera image is clear
        
        Args:
            frame: OpenCV image frame
            
        Returns:
            bool: True if image is clear enough
        """
        # Convert to grayscale for analysis
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Calculate image clarity - Laplacian variance method
        clarity = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Check if image is too dark
        brightness = np.mean(gray)
        
        # Return True if image is clear enough
        return clarity > 100 and brightness > 30
    
    def detect_face_and_gaze(self, frame):
        """
        Detect face and determine if user is facing the camera using OpenCV
        
        Args:
            frame: OpenCV image frame
            
        Returns:
            frame: Processed frame with annotations (optional)
        """
        # Reset detection flags
        self.is_face_detected = False
        self.is_facing_camera = False
        
        try:
            # Convert frame to grayscale for detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            if len(faces) > 0:
                self.is_face_detected = True
                
                # Get the largest face (assuming it's the user)
                largest_face = max(faces, key=lambda face: face[2] * face[3])
                x, y, w, h = largest_face
                
                # Draw face rectangle (for debugging)
                # cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                
                # Extract face region and detect eyes
                roi_gray = gray[y:y+h, x:x+w]
                roi_color = frame[y:y+h, x:x+w]
                
                eyes = self.eye_cascade.detectMultiScale(
                    roi_gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(20, 20)
                )
                
                # Check if both eyes are detected
                if len(eyes) >= 2:
                    # Sort eyes by x-position
                    eyes = sorted(eyes, key=lambda e: e[0])
                    
                    # Draw eye rectangles (for debugging)
                    # for (ex, ey, ew, eh) in eyes:
                    #     cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)
                    
                    # If we have at least two eyes and they're roughly at the same height,
                    # consider the user to be facing the camera
                    if len(eyes) >= 2:
                        eye1_y = eyes[0][1] + eyes[0][3]/2
                        eye2_y = eyes[1][1] + eyes[1][3]/2
                        
                        # If eyes are roughly at the same height (within 10% of face height)
                        if abs(eye1_y - eye2_y) < 0.1 * h:
                            self.is_facing_camera = True
            
            return frame
        except Exception as e:
            logging.error(f"Error in face/eye detection: {e}")
            return frame
    
    def process_frame(self, frame):
        """
        Process a frame and check gaze status
        
        Args:
            frame: OpenCV image frame
            
        Returns:
            dict: Status information
        """
        # Check if camera image is clear
        self.is_camera_clear = self.check_image_quality(frame)
        
        # Detect face and gaze
        processed_frame = self.detect_face_and_gaze(frame)
        
        # Update status and check timeout
        current_time = time.time()
        status = ""
        is_timeout = False
        violation_triggered = False
        
        # Check for violations (camera not clear, face not detected, not facing camera)
        if not self.is_camera_clear:
            status = "Camera image is not clear"
            violation_type = "unclear_camera"
        elif not self.is_face_detected:
            status = "Face not detected"
            violation_type = "face_not_detected"
            # Reset timer when face is not detected
            self.last_facing_camera_time = current_time
        elif not self.is_facing_camera:
            status = "Not facing camera directly"
            violation_type = "not_facing_camera"
            
            # Check if we've exceeded the timeout
            if current_time - self.last_facing_camera_time > self.GAZE_TIMEOUT and not self.warning_shown:
                is_timeout = True
                self.warning_shown = True
        else:
            # User is facing camera
            status = "Properly facing camera"
            self.last_facing_camera_time = current_time
            self.warning_shown = False
            # Reset violation tracking when everything is fine
            self.violation_start_time = None
            self.violation_duration = 0
            return {
                "frame": processed_frame,
                "status": status,
                "is_timeout": is_timeout,
                "is_camera_clear": self.is_camera_clear,
                "is_face_detected": self.is_face_detected,
                "is_facing_camera": self.is_facing_camera,
                "violation_triggered": False,
                "violation_type": None,
                "violation_duration": 0
            }
        
        # Track violation duration
        if self.violation_start_time is None:
            self.violation_start_time = current_time
        
        self.violation_duration = current_time - self.violation_start_time
        
        # Check if violation duration exceeds threshold
        if self.violation_duration >= self.violation_threshold:
            violation_triggered = True
            # Reset for next violation
            self.violation_start_time = None
            self.violation_duration = 0
        
        return {
            "frame": processed_frame,
            "status": status,
            "is_timeout": is_timeout,
            "is_camera_clear": self.is_camera_clear,
            "is_face_detected": self.is_face_detected,
            "is_facing_camera": self.is_facing_camera,
            "violation_triggered": violation_triggered,
            "violation_type": violation_type,
            "violation_duration": self.violation_duration
        }

    def reset(self):
        """Reset the gaze detection state"""
        self.last_facing_camera_time = time.time()
        self.warning_shown = False
        self.violation_start_time = None
        self.violation_duration = 0

# Example usage with OpenCV window
def main():
    # Check for required libraries
    try:
        import cv2
        import numpy as np
    except ImportError as e:
        print(f"Error: Missing required library: {e}")
        print("Please install required libraries with:")
        print("pip install opencv-python numpy")
        return
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera")
        return
    
    # Initialize gaze detection
    gaze_detector = GazeDetection(timeout_seconds=10)
    
    print("Press 'q' to quit")
    
    while True:
        # Read frame
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture image")
            break
        
        # Process frame
        result = gaze_detector.process_frame(frame)
        
        # Display status on frame
        cv2.putText(
            result["frame"],
            f"Status: {result['status']}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2
        )
        
        # Show the frame
        cv2.imshow('Gaze Detection with OpenCV', result["frame"])
        
        # Check for timeout
        if result["is_timeout"]:
            print("WARNING: You have not been facing the camera for too long.")
        
        # Check for key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Release resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()