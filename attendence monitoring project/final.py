import sys
import os
import sqlite3
import csv
import pandas as pd
import json
import traceback
import numpy as np
from PyQt6.QtWidgets import QStackedWidget, QProgressBar
import cv2
from datetime import datetime, timedelta
from insightface.app import FaceAnalysis
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QPushButton, QLabel, QLineEdit, QMessageBox, QTableWidget,
                            QTableWidgetItem, QFrame, QSplashScreen, QTabWidget, QScrollArea,
                            QGridLayout, QSpacerItem, QSizePolicy)
from PyQt6.QtGui import QFont, QPixmap, QIcon, QPalette, QColor, QBrush, QLinearGradient,QImage
from PyQt6.QtCore import Qt, QTimer, QSize, pyqtSignal, QThread
from PyQt6.QtWidgets import QHeaderView  
import bcrypt
from PyQt6.QtGui import QIntValidator
from PyQt6.QtWidgets import QFileDialog, QFormLayout
from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox, QTableWidget, QTableWidgetItem, 
    QHeaderView, QMessageBox, QHBoxLayout
)

from PyQt6.QtWidgets import QGroupBox
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QMessageBox, QTableWidget,
    QTableWidgetItem, QFrame, QSplashScreen, QTabWidget, QScrollArea,
    QGridLayout, QSpacerItem, QSizePolicy, QInputDialog, QDialog,
    QDialogButtonBox, QHeaderView, QFormLayout, QFileDialog
)

# Import existing attendance functions from your module
#from attendance_system import (start_camera, recognize_faces, reset_attendance_session, 
 #                             get_student_embeddings, restore_student_status)

# Set OpenCV to prefer DirectShow backend
#os.environ["OPENCV_VIDEOIO_PRIORITY_MSMF"] = "0"
#os.environ["OPENCV_VIDEOIO_PRIORITY_DSHOW"] = "1"

def hash_password(password):
    """Hash a password for storing"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed

def check_password(password, hashed):
    """Check if the provided password matches the hashed password"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed)
# Constants
DB_PATH = r"D:\miniproject\AutomaticAttendanceSystem\attendance1.db"
ATTENDANCE_DIR = "attendance"

# Ensure the attendance directory exists
os.makedirs(ATTENDANCE_DIR, exist_ok=True)

class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Set the layout for the splash screen
        layout = QVBoxLayout(self)

        # Create a label to display the GIF
        self.splash_label = QLabel(self)
        layout.addWidget(self.splash_label)

        # Load the GIF
        self.movie = QMovie("icons/splash.gif")  # Path to your GIF file
        self.splash_label.setMovie(self.movie)
        self.movie.start()

        # Set the window properties
        self.setWindowTitle("Splash Screen")
        self.setGeometry(100, 100, 800, 600)  # Adjust size as needed
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)  # Optional: for transparency
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)  # Optional: remove window frame

class AttendanceSystem(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        # Set window properties
        self.setWindowTitle("Attendease")
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowIcon(QIcon("icons/logo.jpg"))
        
        # Apply gradient background
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(6, 34, 71))      # Deep ocean blue (darker)
        gradient.setColorAt(0.5, QColor(12, 53, 106))  # Mid ocean blue
        gradient.setColorAt(1, QColor(0, 168, 204))  # Lighter ocean blue)   # Turquoise (light ocean)setColorAt(1, QColor(169, 175, 38))    # Light olive green
        
        palette = self.palette()
        palette.setBrush(QPalette.ColorRole.Window, QBrush(gradient))
        self.setPalette(palette)
        
        # Create central widget with stacked layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Create a stacked widget to switch between screens
        self.stacked_widget = QStackedWidget()
        
        # Main layout for central widget
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.addWidget(self.stacked_widget)
        
        # Create main menu screen
        self.main_menu_screen = QWidget()
        self.setup_main_menu()
        
        # Create the attendance marker screen
        self.attendance_marker_screen = AttendanceMarkerWidget()
        
        # Create student login screen (placeholder)
        self.student_login_screen = StudentLoginWindow()
        
        # Create teacher login screen
        self.teacher_login_screen = TeacherLoginWidget()

        # Create admin login screen
        self.admin_login_screen = AdminLoginWidget() 
        
        # Add all screens to the stacked widget
        self.stacked_widget.addWidget(self.main_menu_screen)
        self.stacked_widget.addWidget(self.attendance_marker_screen)
        self.stacked_widget.addWidget(self.student_login_screen)
        self.stacked_widget.addWidget(self.teacher_login_screen)
        self.stacked_widget.addWidget(self.admin_login_screen) 
        
        # Show main menu by default
        self.stacked_widget.setCurrentIndex(0)
        
        # Make window responsive
        self.setMinimumSize(800, 600)
    
    def setup_main_menu(self):
        # Main layout for the main menu screen
        main_layout = QVBoxLayout(self.main_menu_screen)
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setSpacing(30)
        
        # Logo and title section
        title_layout = QHBoxLayout()
        logo_label = QLabel()
        
        # Try to load logo if exists
        if os.path.exists("icons/attendance_icon.jpg"):
            logo_pixmap = QPixmap("icons/attendance_icon.jpg").scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio)
            logo_label.setPixmap(logo_pixmap)
        else:
            logo_label.setStyleSheet("font-size: 120px; color: white;")
            logo_label.setText("📊")
        
        title_layout.addWidget(logo_label)
        
        # Title and description
        title_desc_layout = QVBoxLayout()
        title_label = QLabel("ATTENDEASE : Attendance Management System")
        title_label.setFont(QFont("Garamond", 28, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white;")
        
        description_label = QLabel("Face the Future of Attendance")
        description_label.setFont(QFont("Palatino Linotype", 18))
        description_label.setStyleSheet("color: rgba(255, 255, 255, 0.8);")
        description_label.setAlignment(Qt.AlignmentFlag.AlignCenter) 

        title_desc_layout.addWidget(title_label)
        title_desc_layout.addWidget(description_label)
        title_desc_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addLayout(title_desc_layout)
        title_layout.addStretch()
        
        main_layout.addLayout(title_layout)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: rgba(255, 255, 255, 0.3);")
        main_layout.addWidget(separator)
        
        # Buttons section
        buttons_layout = QGridLayout()
        buttons_layout.setSpacing(30)
        
        # Button styles
        button_style = """
    QPushButton {
        background-color: rgba(255, 255, 255, 0.2);
        color: white;
        border-radius: 12px;
        font-size: 18px;
        font-weight: bold;
        padding: 15px 25px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        min-width: 120px;
    }
    
    QPushButton:hover {
        background-color: rgba(255, 255, 255, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.4);
    }
    
    QPushButton:pressed {
        background-color: rgba(255, 255, 255, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    QPushButton:disabled {
        background-color: rgba(255, 255, 255, 0.1);
        color: rgba(255, 255, 255, 0.5);
    }
"""
        
        # Mark Attendance Button
        mark_attendance_btn = QPushButton()
        pixmap = QPixmap("icons/mark_attendance.png")
        # Scale to fill while keeping aspect ratio (may crop edges)
        scaled_pixmap = pixmap.scaled(250, 250, 
                            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                            Qt.TransformationMode.SmoothTransformation)
        mark_attendance_btn.setIcon(QIcon(scaled_pixmap))
        mark_attendance_btn.setIconSize(QSize(200, 200))
        mark_attendance_btn.setStyleSheet(button_style)
        mark_attendance_btn.setMinimumHeight(150)

        mark_attendance_btn.clicked.connect(self.open_mark_attendance)
        
       # Student Login Button
        student_login_btn = QPushButton()
        student_pixmap = QPixmap("icons/student.png")
        scaled_student_pixmap = student_pixmap.scaled( 350, 350, 
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation
        )
        student_login_btn.setIcon(QIcon(scaled_student_pixmap))
        student_login_btn.setIconSize(QSize(200, 200))
        student_login_btn.setStyleSheet(button_style)
        student_login_btn.setMinimumHeight(150)
        student_login_btn.clicked.connect(self.open_student_login)
        
        # Teacher Login Button
        teacher_login_btn = QPushButton()
        teacher_pixmap = QPixmap("icons/teacher.png")
        scaled_teacher_pixmap = teacher_pixmap.scaled(350, 350, 
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation
        )
        teacher_login_btn.setIcon(QIcon(scaled_teacher_pixmap))
        teacher_login_btn.setIconSize(QSize(200, 200))
        teacher_login_btn.setStyleSheet(button_style)
        teacher_login_btn.setMinimumHeight(150)
        teacher_login_btn.clicked.connect(self.open_teacher_login)

         # New Admin Login Button
        admin_login_btn = QPushButton()
        admin_pixmap = QPixmap("icons/admin.png")
        scaled_admin_pixmap = admin_pixmap.scaled(350, 350, 
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation
        ) 
        admin_login_btn.setIcon(QIcon(scaled_admin_pixmap))
        admin_login_btn.setIconSize(QSize(200, 200))
        admin_login_btn.setStyleSheet(button_style)
        admin_login_btn.setMinimumHeight(150)
        admin_login_btn.clicked.connect(self.open_admin_login)
        
        # Add buttons to grid
        button1_layout = QVBoxLayout()
        button1_layout.addWidget(mark_attendance_btn)
        #button1_layout.addWidget(mark_attendance_label)
        
        button2_layout = QVBoxLayout()
        button2_layout.addWidget(student_login_btn)
        #button2_layout.addWidget(student_login_label)
        

        button3_layout = QVBoxLayout()
        button3_layout.addWidget(teacher_login_btn)
        #button3_layout.addWidget(teacher_login_label)

        button4_layout = QVBoxLayout()
        button4_layout.addWidget(admin_login_btn)
        #button4_layout.addWidget(admin_login_label)
        
        buttons_layout.addLayout(button1_layout, 0, 0)
        buttons_layout.addLayout(button2_layout, 0, 1)
        buttons_layout.addLayout(button3_layout, 1, 0)
        buttons_layout.addLayout(button4_layout, 1, 1)
        
        main_layout.addLayout(buttons_layout)
        
        # Footer
        footer_label = QLabel("© 2025 Attendance Management System | All Rights Reserved")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_label.setFont(QFont("Arial", 10))
        footer_label.setStyleSheet("color: rgba(255, 255, 255, 0.6);")
        main_layout.addStretch()
        main_layout.addWidget(footer_label)

    def open_mark_attendance(self):
        # Switch to the attendance marker screen
        self.stacked_widget.setCurrentIndex(1)
    
    def open_student_login(self):
        # Switch to the student login screen
        self.stacked_widget.setCurrentIndex(2)
    
    def open_teacher_login(self):
        # Switch to the teacher login screen
        self.stacked_widget.setCurrentIndex(3)

    def open_admin_login(self):
        # Switch to the admin login screen
        self.stacked_widget.setCurrentIndex(4) 


    def closeEvent(self, event):
            """Handle application close event"""
            if hasattr(self, 'attendance_marker_screen'):
                self.attendance_marker_screen.stop_camera()
            event.accept()


class AdminLoginWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()  # Make sure this is called

    
    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setSpacing(20)
        
        # Title
        title_label = QLabel("Admin Login")
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Login Form Layout
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)
        
        # Admin ID Input
        admin_id_layout = QHBoxLayout()
        admin_id_icon = QLabel()
        admin_id_icon.setPixmap(QIcon("icons/user.png").pixmap(30, 30))
        admin_id_icon.setFixedWidth(50)
        
        self.admin_id_input = QLineEdit()
        self.admin_id_input.setPlaceholderText("Admin ID")
        self.admin_id_input.setFont(QFont("Arial", 12))
        
        admin_id_layout.addWidget(admin_id_icon)
        admin_id_layout.addWidget(self.admin_id_input)
        form_layout.addLayout(admin_id_layout)
        
        # Password Input
        password_layout = QHBoxLayout()
        password_icon = QLabel()
        password_icon.setPixmap(QIcon("icons/lock.png").pixmap(30, 30))
        password_icon.setFixedWidth(50)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFont(QFont("Arial", 12))
        
        password_layout.addWidget(password_icon)
        password_layout.addWidget(self.password_input)
        form_layout.addLayout(password_layout)
        
        # Login Button
        login_btn = QPushButton("Login")
        login_btn.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        login_btn.clicked.connect(self.validate_login)
        form_layout.addWidget(login_btn)
        
        # Error Message Label
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: red;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(self.error_label)
        
        main_layout.addLayout(form_layout)
        main_layout.addStretch()
        
        # Back to Main Menu Button
        back_btn = QPushButton("Back to Main Menu")
        back_btn.clicked.connect(self.go_back_to_main_menu)
        main_layout.addWidget(back_btn)
    
    def hash_password(self, password):
        # Hash a password for storing
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed
    
    import sqlite3
    import bcrypt
    from PyQt5.QtWidgets import QMessageBox

    def validate_login(self):
     admin_id = self.admin_id_input.text()
     password = self.password_input.text()
    
     try:
         conn = sqlite3.connect(DB_PATH)
         cursor = conn.cursor()
        
         # Fetch admin details
         cursor.execute("SELECT * FROM admin WHERE admin_id = ?", (admin_id,))
         admin = cursor.fetchone()
        
         conn.close()
        
         if admin:
             stored_password = admin[2]  # Assuming password is in index 2
             
             # Check if stored_password is bytes or string
             if isinstance(stored_password, str):
                 stored_password = stored_password.encode('utf-8')
            
             # Bcrypt password verification
             if bcrypt.checkpw(password.encode('utf-8'), stored_password):
                 self.login_success(admin)
             else:
                 self.error_label.setText("Invalid Admin Credentials")
                 self.password_input.clear()
         else:
             self.error_label.setText("Admin ID not found")
    
     except sqlite3.Error as e:
          QMessageBox.critical(self, "Database Error", f"Error: {str(e)}")
     except Exception as e:
         QMessageBox.critical(self, "Login Error", f"Error during login: {str(e)}")

    def login_success(self, admin):
      """Handle successful login"""
      QMessageBox.information(self, "Login Successful", f"Welcome, {admin[1]}!")
    
      # Get the main window instance
      main_window = self.parent()
      while main_window is not None:
          if hasattr(main_window, 'stacked_widget'):
              break
          main_window = main_window.parent()
    
      if main_window is None:
          QMessageBox.critical(self, "Navigation Error", "Could not find main window")
          return
    
      # Navigate to admin dashboard
      main_window.stacked_widget.addWidget(AdminDashboardWidget())
      main_window.stacked_widget.setCurrentIndex(
          main_window.stacked_widget.count() - 1
      )
        
    def go_back_to_main_menu(self):
        """Safely navigate back to main menu by finding stacked_widget in parent chain"""
        current = self
        while current is not None:
            if hasattr(current, 'stacked_widget'):
                current.stacked_widget.setCurrentIndex(0)  # Main menu is index 0
                return
            current = current.parent()
        
        # Fallback if stacked_widget isn't found
        print("Error: Could not find stacked_widget in parent hierarchy")
        self.close()
    
    def keyPressEvent(self, event):
        # Allow login on Enter key press
        if event.key() in [Qt.Key.Key_Return, Qt.Key.Key_Enter]:
            self.validate_login()
        super().keyPressEvent(event)

# Add these imports at the top if not already present
from PyQt6.QtWidgets import QComboBox

class AdminDashboardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setSpacing(20)
        
        # Title
        title_label = QLabel("Admin Dashboard")
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Buttons Layout
        buttons_layout = QGridLayout()
        buttons_layout.setSpacing(15)
        
        # Student Management Button
        student_btn = QPushButton("Student Management")
        student_btn.setFont(QFont("Arial", 14))
        student_btn.clicked.connect(self.open_student_management)
        buttons_layout.addWidget(student_btn, 0, 0)
        
        # Teacher Management Button
        teacher_btn = QPushButton("Teacher Management")
        teacher_btn.setFont(QFont("Arial", 14))
        teacher_btn.clicked.connect(self.open_teacher_management)
        buttons_layout.addWidget(teacher_btn, 0, 1)
        
        # View All Students Button
        view_students_btn = QPushButton("View All Students")
        view_students_btn.setFont(QFont("Arial", 14))
        view_students_btn.clicked.connect(self.open_all_students_view)
        buttons_layout.addWidget(view_students_btn, 1, 0)
        
        # View All Teachers Button
        view_teachers_btn = QPushButton("View All Teachers")
        view_teachers_btn.setFont(QFont("Arial", 14))
        view_teachers_btn.clicked.connect(self.open_all_teachers_view)
        buttons_layout.addWidget(view_teachers_btn, 1, 1)
        
        # Edit Timetable Button
        timetable_btn = QPushButton("Edit Timetable")
        timetable_btn.setFont(QFont("Arial", 14))
        timetable_btn.clicked.connect(self.open_timetable_editor)
        buttons_layout.addWidget(timetable_btn, 2, 0, 1, 2)  # Span across two columns

        main_layout.addLayout(buttons_layout)
        main_layout.addStretch()
        
        # Back Button
        back_btn = QPushButton("Back")
        back_btn.clicked.connect(self.go_back)
        main_layout.addWidget(back_btn)
    
    

    def open_student_management(self):
        # Find the main window with stacked_widget by traversing parent hierarchy
        main_window = None
        parent = self.parent()
        while parent:
            if hasattr(parent, 'stacked_widget'):
                main_window = parent
                break
            parent = parent.parent()
        
        if main_window:
            # Create and add the student management widget
            student_widget = StudentManagementWidget()
            main_window.stacked_widget.addWidget(student_widget)
            main_window.stacked_widget.setCurrentIndex(
                main_window.stacked_widget.count() - 1
            )
        else:
            print("Error: Could not find main window with stacked_widget")
            # Fallback - create a new window if main window not found
            student_widget = StudentManagementWidget()
            student_widget.show()
    
    def open_teacher_management(self):
        # Find the main window with stacked_widget by traversing parent hierarchy
        main_window = None
        parent = self.parent()
        while parent:
            if hasattr(parent, 'stacked_widget'):
                main_window = parent
                break
            parent = parent.parent()
        
        if main_window:
            # Create and add the teacher management widget
            teacher_widget = TeacherManagementWidget()
            main_window.stacked_widget.addWidget(teacher_widget)
            main_window.stacked_widget.setCurrentIndex(
                main_window.stacked_widget.count() - 1
            )
        else:
            # Fallback if main window not found
            QMessageBox.critical(
                self, 
                "Navigation Error", 
                "Could not find main window with stacked widget"
            )
            # Alternatively, you could show the widget in a new window:
            # teacher_widget = TeacherManagementWidget()
            # teacher_widget.show()
    
    def open_all_students_view(self):
        # Try to find the main window or the object that has stacked_widget
        main_window = self.window()  # Gets the top-level window
        all_students_widget = AllStudentsWidget()
        
        # Check if main_window has stacked_widget
        if hasattr(main_window, 'stacked_widget'):
            main_window.stacked_widget.addWidget(all_students_widget)
            main_window.stacked_widget.setCurrentIndex(main_window.stacked_widget.count() - 1)
        else:
            print("Could not find stacked_widget in the parent hierarchy")
        

    def open_all_teachers_view(self):
        """Safely open the AllTeachersWidget by finding the main window"""
        # Method 1: Traverse parent hierarchy to find stacked_widget
        current = self
        while current is not None:
            if hasattr(current, 'stacked_widget'):
                all_teachers_widget = AllTeachersWidget()
                current.stacked_widget.addWidget(all_teachers_widget)
                current.stacked_widget.setCurrentIndex(current.stacked_widget.count() - 1)
                return
            current = current.parent()
    
    def open_timetable_editor(self):
        """Open the timetable editor widget"""
        # Find the main window with stacked_widget by traversing parent hierarchy
        main_window = None
        parent = self.parent()
        while parent:
            if hasattr(parent, 'stacked_widget'):
                main_window = parent
                break
            parent = parent.parent()
        
        if main_window:
            # Create and add the timetable editor widget
            timetable_widget = TimetableEditorWidget()
            main_window.stacked_widget.addWidget(timetable_widget)
            main_window.stacked_widget.setCurrentIndex(
                main_window.stacked_widget.count() - 1
            )

    def go_back(self):
        # Traverse up the parent hierarchy to find the main window
        parent = self.parent()
        while parent is not None:
            if hasattr(parent, 'stacked_widget'):
                # Found the main window with stacked widget
                parent.stacked_widget.setCurrentIndex(4)  # Go back to Admin Login (index 4)
                return
            parent = parent.parent()
        
        # Fallback: Close the current widget if main window not found
        self.close()

    

class TimetableEditorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.timetable_path = r"D:\miniproject\AutomaticAttendanceSystem\timetable\timetable.json"
        self.init_ui()
        self.load_timetable()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("Timetable Editor")
        title_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Tab widget for each day
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Save button
        save_btn = QPushButton("Save Timetable")
        save_btn.setFont(QFont("Arial", 14))
        save_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        save_btn.clicked.connect(self.save_timetable)
        button_layout.addWidget(save_btn)
        
        # Add Day button
        add_day_btn = QPushButton("Add Day")
        add_day_btn.setFont(QFont("Arial", 14))
        add_day_btn.setStyleSheet("background-color: #2196F3; color: white;")
        add_day_btn.clicked.connect(self.add_day)
        button_layout.addWidget(add_day_btn)
        
        # Back button
        back_btn = QPushButton("Back to Dashboard")
        back_btn.setFont(QFont("Arial", 14))
        back_btn.clicked.connect(self.go_back)
        button_layout.addWidget(back_btn)
        
        main_layout.addLayout(button_layout)
    
    def load_timetable(self):
        """Load the timetable from JSON file"""
        try:
            with open(self.timetable_path, 'r') as f:
                self.timetable = json.load(f)
                
            # Clear existing tabs
            self.tab_widget.clear()
            
            # Create a tab for each day
            for day in self.timetable:
                day_widget = QWidget()
                day_layout = QVBoxLayout(day_widget)
                
                # Scroll area for subjects
                scroll_area = QScrollArea()
                scroll_area.setWidgetResizable(True)
                
                # Container for subjects
                subjects_widget = QWidget()
                subjects_layout = QVBoxLayout(subjects_widget)
                
                # Add existing subjects
                day_data = self.timetable[day]
                # Handle both old and new format
                if isinstance(day_data, list):
                    subjects = day_data
                elif isinstance(day_data, dict) and "subjects" in day_data:
                    subjects = day_data["subjects"]
                else:
                    subjects = []
                    
                for subject_info in subjects:
                    subject_frame = self.create_subject_frame(day, subject_info)
                    subjects_layout.addWidget(subject_frame)
                
                # Add Subject button
                add_subject_btn = QPushButton("Add Subject")
                add_subject_btn.setFont(QFont("Arial", 12))
                add_subject_btn.setStyleSheet("background-color: #2196F3; color: white;")
                add_subject_btn.clicked.connect(lambda _, d=day: self.add_subject(d))
                subjects_layout.addWidget(add_subject_btn)
                subjects_layout.addStretch()
                
                # Add Intervals section if the day has intervals
                if isinstance(day_data, dict) and "intervals" in day_data:
                    intervals_group = QGroupBox("Intervals")
                    intervals_layout = QVBoxLayout(intervals_group)
                    
                    for interval in day_data["intervals"]:
                        interval_frame = self.create_interval_frame(day, interval)
                        intervals_layout.addWidget(interval_frame)
                    
                    # Add Interval button
                    add_interval_btn = QPushButton("Add Interval")
                    add_interval_btn.setFont(QFont("Arial", 12))
                    add_interval_btn.setStyleSheet("background-color: #9C27B0; color: white;")
                    add_interval_btn.clicked.connect(lambda _, d=day: self.add_interval(d))
                    intervals_layout.addWidget(add_interval_btn)
                    
                    subjects_layout.addWidget(intervals_group)
                
                scroll_area.setWidget(subjects_widget)
                day_layout.addWidget(scroll_area)
                
                self.tab_widget.addTab(day_widget, day)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load timetable: {str(e)}")
            # Initialize with default days if file doesn't exist
            self.timetable = {
                "Monday": {"subjects": [], "intervals": []},
                "Tuesday": {"subjects": [], "intervals": []},
                "Wednesday": {"subjects": [], "intervals": []},
                "Thursday": {"subjects": [], "intervals": []},
                "Friday": {"subjects": [], "intervals": []},
                "Saturday": {"subjects": [], "intervals": []},
                "Sunday": {"subjects": [], "intervals": []}
            }
            
            # Create tabs for default days
            self.load_timetable()
    
    def create_subject_frame(self, day, subject_info):
        """Create a frame for a subject with edit/delete controls"""
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setStyleSheet("QFrame { background-color: #f5f5f5; border-radius: 5px; padding: 5px; }")
        
        layout = QHBoxLayout(frame)
        
        # Subject fields
        form_layout = QFormLayout()
        
        # Subject name
        subject_name = QLineEdit(subject_info["subject"])
        subject_name.setFont(QFont("Arial", 12))
        form_layout.addRow("Subject:", subject_name)
        
        # Time
        time_edit = QLineEdit(subject_info["time"])
        time_edit.setFont(QFont("Arial", 12))
        time_edit.setPlaceholderText("HH:MM-HH:MM")
        form_layout.addRow("Time:", time_edit)
        
        # Teacher
        teacher_edit = QLineEdit(subject_info["teacher"])
        teacher_edit.setFont(QFont("Arial", 12))
        teacher_edit.setPlaceholderText("Teacher initials")
        form_layout.addRow("Teacher:", teacher_edit)
        
        layout.addLayout(form_layout)
        
        # Delete button
        delete_btn = QPushButton("Delete")
        delete_btn.setFont(QFont("Arial", 12))
        delete_btn.setStyleSheet("background-color: #f44336; color: white;")
        delete_btn.clicked.connect(lambda: self.delete_subject(day, frame))
        layout.addWidget(delete_btn)
        
        # Store references to the input fields
        frame.subject_name = subject_name
        frame.time_edit = time_edit
        frame.teacher_edit = teacher_edit
        frame.day = day
        frame.type = "subject"
        
        return frame
    
    def create_interval_frame(self, day, interval_info):
        """Create a frame for an interval with edit/delete controls"""
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setStyleSheet("QFrame { background-color: #e6e6ff; border-radius: 5px; padding: 5px; }")
        
        layout = QHBoxLayout(frame)
        
        # Interval fields
        form_layout = QFormLayout()
        
        # Interval name
        name_edit = QLineEdit(interval_info["name"])
        name_edit.setFont(QFont("Arial", 12))
        form_layout.addRow("Name:", name_edit)
        
        # Time
        time_edit = QLineEdit(interval_info["time"])
        time_edit.setFont(QFont("Arial", 12))
        time_edit.setPlaceholderText("HH:MM-HH:MM")
        form_layout.addRow("Time:", time_edit)
        
        layout.addLayout(form_layout)
        
        # Delete button
        delete_btn = QPushButton("Delete")
        delete_btn.setFont(QFont("Arial", 12))
        delete_btn.setStyleSheet("background-color: #f44336; color: white;")
        delete_btn.clicked.connect(lambda: self.delete_interval(day, frame))
        layout.addWidget(delete_btn)
        
        # Store references to the input fields
        frame.name_edit = name_edit
        frame.time_edit = time_edit
        frame.day = day
        frame.type = "interval"
        
        return frame
    
    def add_subject(self, day):
        """Add a new subject to the specified day"""
        # Find the tab for this day
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == day:
                # Get the scroll area's widget
                scroll_widget = self.tab_widget.widget(i)
                scroll_area = scroll_widget.findChild(QScrollArea)
                if scroll_area:
                    subjects_widget = scroll_area.widget()
                    subjects_layout = subjects_widget.layout()
                    
                    # Create a new subject frame with empty values
                    new_subject = {
                        "subject": "New Subject",
                        "time": "09:00-10:00",
                        "teacher": "TCH"
                    }
                    subject_frame = self.create_subject_frame(day, new_subject)
                    
                    # Insert before the Add Subject button
                    subjects_layout.insertWidget(subjects_layout.count() - 2, subject_frame)
                    
                    # Scroll to the new subject
                    scroll_area.verticalScrollBar().setValue(scroll_area.verticalScrollBar().maximum())
                    break
    
    def add_interval(self, day):
        """Add a new interval to the specified day"""
        # Find the tab for this day
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == day:
                # Get the scroll area's widget
                scroll_widget = self.tab_widget.widget(i)
                scroll_area = scroll_widget.findChild(QScrollArea)
                if scroll_area:
                    subjects_widget = scroll_area.widget()
                    # Find the intervals group box
                    intervals_group = subjects_widget.findChild(QGroupBox)
                    
                    if not intervals_group:
                        # Create new intervals group if it doesn't exist
                        intervals_group = QGroupBox("Intervals")
                        intervals_layout = QVBoxLayout(intervals_group)
                        
                        # Add Interval button
                        add_interval_btn = QPushButton("Add Interval")
                        add_interval_btn.setFont(QFont("Arial", 12))
                        add_interval_btn.setStyleSheet("background-color: #9C27B0; color: white;")
                        add_interval_btn.clicked.connect(lambda _, d=day: self.add_interval(d))
                        intervals_layout.addWidget(add_interval_btn)
                        
                        subjects_widget.layout().addWidget(intervals_group)
                    
                    intervals_layout = intervals_group.layout()
                    
                    # Create a new interval frame
                    new_interval = {
                        "name": "New Interval",
                        "time": "10:45-11:00"
                    }
                    interval_frame = self.create_interval_frame(day, new_interval)
                    
                    # Insert before the Add Interval button
                    intervals_layout.insertWidget(intervals_layout.count() - 1, interval_frame)
                    break
    
    def delete_subject(self, day, frame):
        """Delete a subject from the specified day"""
        reply = QMessageBox.question(
            self, 
            "Confirm Delete", 
            "Are you sure you want to delete this subject?", 
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Find the tab for this day
            for i in range(self.tab_widget.count()):
                if self.tab_widget.tabText(i) == day:
                    # Get the scroll area's widget
                    scroll_widget = self.tab_widget.widget(i)
                    scroll_area = scroll_widget.findChild(QScrollArea)
                    if scroll_area:
                        subjects_widget = scroll_area.widget()
                        subjects_layout = subjects_widget.layout()
                        
                        # Remove the frame
                        frame.setParent(None)
                        subjects_layout.removeWidget(frame)
                        frame.deleteLater()
                        break
    
    def delete_interval(self, day, frame):
        """Delete an interval from the specified day"""
        reply = QMessageBox.question(
            self, 
            "Confirm Delete", 
            "Are you sure you want to delete this interval?", 
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Find the tab for this day
            for i in range(self.tab_widget.count()):
                if self.tab_widget.tabText(i) == day:
                    # Get the intervals group
                    scroll_widget = self.tab_widget.widget(i)
                    scroll_area = scroll_widget.findChild(QScrollArea)
                    if scroll_area:
                        subjects_widget = scroll_area.widget()
                        intervals_group = subjects_widget.findChild(QGroupBox)
                        if intervals_group:
                            intervals_layout = intervals_group.layout()
                            
                            # Remove the frame
                            frame.setParent(None)
                            intervals_layout.removeWidget(frame)
                            frame.deleteLater()
                            break
    
    def add_day(self):
        """Add a new day to the timetable"""
        day_name, ok = QInputDialog.getText(self, "Add Day", "Enter day name:")
        if ok and day_name:
            if day_name not in self.timetable:
                self.timetable[day_name] = {"subjects": [], "intervals": []}
                
                # Create a new tab for this day
                day_widget = QWidget()
                day_layout = QVBoxLayout(day_widget)
                
                # Scroll area for subjects
                scroll_area = QScrollArea()
                scroll_area.setWidgetResizable(True)
                
                # Container for subjects
                subjects_widget = QWidget()
                subjects_layout = QVBoxLayout(subjects_widget)
                
                # Add Subject button
                add_subject_btn = QPushButton("Add Subject")
                add_subject_btn.setFont(QFont("Arial", 12))
                add_subject_btn.setStyleSheet("background-color: #2196F3; color: white;")
                add_subject_btn.clicked.connect(lambda _, d=day_name: self.add_subject(d))
                subjects_layout.addWidget(add_subject_btn)
                subjects_layout.addStretch()
                
                scroll_area.setWidget(subjects_widget)
                day_layout.addWidget(scroll_area)
                
                self.tab_widget.addTab(day_widget, day_name)
            else:
                QMessageBox.warning(self, "Warning", "This day already exists in the timetable.")
    
    def save_timetable(self):
        """Save the timetable back to the JSON file"""
        try:
            new_timetable = {}
            
            # Gather data from all tabs
            for i in range(self.tab_widget.count()):
                day = self.tab_widget.tabText(i)
                day_widget = self.tab_widget.widget(i)
                
                # Find all subject frames in this tab
                scroll_area = day_widget.findChild(QScrollArea)
                if scroll_area:
                    subjects_widget = scroll_area.widget()
                    
                    # Process subjects
                    subject_frames = []
                    for frame in subjects_widget.findChildren(QFrame):
                        if hasattr(frame, 'type') and frame.type == "subject":
                            subject_frames.append(frame)
                    
                    day_subjects = []
                    for frame in subject_frames:
                        subject_name = frame.subject_name.text()
                        time = frame.time_edit.text()
                        teacher = frame.teacher_edit.text()
                        
                        if subject_name and time and teacher:
                            day_subjects.append({
                                "subject": subject_name,
                                "time": time,
                                "teacher": teacher
                            })
                    
                    # Process intervals
                    intervals_group = subjects_widget.findChild(QGroupBox)
                    day_intervals = []
                    
                    if intervals_group:
                        interval_frames = []
                        for frame in intervals_group.findChildren(QFrame):
                            if hasattr(frame, 'type') and frame.type == "interval":
                                interval_frames.append(frame)
                        
                        for frame in interval_frames:
                            name = frame.name_edit.text()
                            time = frame.time_edit.text()
                            
                            if name and time:
                                day_intervals.append({
                                    "name": name,
                                    "time": time
                                })
                    
                    new_timetable[day] = {
                        "subjects": day_subjects,
                        "intervals": day_intervals
                    }
            
            # Save to file
            with open(self.timetable_path, 'w') as f:
                json.dump(new_timetable, f, indent=4)
            
            QMessageBox.information(self, "Success", "Timetable saved successfully!")
            self.timetable = new_timetable
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save timetable: {str(e)}")
    
    def go_back(self):
        """Navigate back to the admin dashboard"""
        # Find the main window in the parent hierarchy
        main_window = None
        parent = self.parent()
        while parent:
            if hasattr(parent, 'stacked_widget'):
                main_window = parent
                break
            parent = parent.parent()
        
        if main_window:
            # Go back to admin dashboard (index 5)
            main_window.stacked_widget.setCurrentIndex(5)

class StudentManagementWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = self._find_main_window()
        self.init_ui()
    
    def _find_main_window(self):
        """Helper method to find the main window with stacked_widget"""
        parent = self.parent()
        while parent:
            if hasattr(parent, 'stacked_widget'):
                return parent
            parent = parent.parent()
        return None
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("Student Management")
        title_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Tab widget for different management options
        tab_widget = QTabWidget()
        
        # Add Student Tab
        add_student_tab = QWidget()
        self.setup_add_student_tab(add_student_tab)
        tab_widget.addTab(add_student_tab, "Add New Student")
        
        # View/Edit Students Tab
        view_students_tab = QWidget()
        self.setup_view_students_tab(view_students_tab)
        tab_widget.addTab(view_students_tab, "View/Edit Students")
        
        main_layout.addWidget(tab_widget)
        
        # Back button
        back_btn = QPushButton("Back to Dashboard")
        back_btn.clicked.connect(self.go_back)
        main_layout.addWidget(back_btn)
    
    def setup_add_student_tab(self, tab):
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Roll Number
        self.roll_no_input = QLineEdit()
        self.roll_no_input.setPlaceholderText("Enter roll number")
        form_layout.addRow("Roll Number*:", self.roll_no_input)
        
        # Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter student name")
        form_layout.addRow("Name*:", self.name_input)
        
        # Age
        self.age_input = QLineEdit()
        self.age_input.setPlaceholderText("Enter age")
        self.age_input.setValidator(QIntValidator(1, 100))
        form_layout.addRow("Age:", self.age_input)
        
        # Gender
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["Male", "Female", "Other"])
        form_layout.addRow("Gender:", self.gender_combo)
        
        # Department
        self.dept_input = QLineEdit()
        self.dept_input.setPlaceholderText("Enter department")
        form_layout.addRow("Department:", self.dept_input)
        
        # Password
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password (min 8 characters)")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Password*:", self.password_input)
        
        # Confirm Password
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirm password")
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Confirm Password*:", self.confirm_password_input)
        
        # Image Upload
        self.image_path_label = QLabel("No image selected")
        self.image_path_label.setWordWrap(True)
        upload_btn = QPushButton("Upload Image")
        upload_btn.clicked.connect(self.upload_image)
        form_layout.addRow("Student Photo:", upload_btn)
        form_layout.addRow("", self.image_path_label)
        
        # Password requirements label
        password_req_label = QLabel("* Required fields | Password must be at least 8 characters")
        password_req_label.setStyleSheet("font-size: 10px; color: #666;")
        form_layout.addRow("", password_req_label)
        
        layout.addLayout(form_layout)
        
        # Add Student Button
        add_btn = QPushButton("Add Student")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        add_btn.clicked.connect(self.add_student)
        layout.addWidget(add_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Status label
        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        layout.addStretch()
    
    def setup_view_students_tab(self, tab):
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name or roll number...")
        self.search_input.textChanged.connect(self.filter_students)
        search_layout.addWidget(self.search_input)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_students)
        search_layout.addWidget(refresh_btn)
        layout.addLayout(search_layout)
        
        # Students table
        self.students_table = QTableWidget()
        self.students_table.setColumnCount(7)  # Roll No, Name, Age, Gender, Department, Image, Actions
        self.students_table.setHorizontalHeaderLabels(["Roll No", "Name", "Age", "Gender", "Department", "Has Photo", "Actions"])
        self.students_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.students_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        # Load initial data
        self.load_students()
        
        layout.addWidget(self.students_table)
    
    def upload_image(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp)")
        file_dialog.setViewMode(QFileDialog.ViewMode.Detail)
        
        if file_dialog.exec():
            file_names = file_dialog.selectedFiles()
            if file_names:
                self.image_path = file_names[0]
                self.image_path_label.setText(file_names[0])
    
    def load_students(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute("SELECT roll_no, name, age, gender, department, image FROM students ORDER BY roll_no")
            students = cursor.fetchall()
            
            conn.close()
            
            self.students_table.setRowCount(len(students))
            
            for row, (roll_no, name, age, gender, department, image) in enumerate(students):
                # Roll No
                self.students_table.setItem(row, 0, QTableWidgetItem(roll_no))
                
                # Name
                self.students_table.setItem(row, 1, QTableWidgetItem(name))
                
                # Age
                self.students_table.setItem(row, 2, QTableWidgetItem(str(age) if age else ""))
                
                # Gender
                self.students_table.setItem(row, 3, QTableWidgetItem(gender))
                
                # Department
                self.students_table.setItem(row, 4, QTableWidgetItem(department))
                
                # Has Photo
                has_photo = "Yes" if image else "No"
                self.students_table.setItem(row, 5, QTableWidgetItem(has_photo))
                
                # Action buttons
                btn_widget = QWidget()
                btn_layout = QHBoxLayout(btn_widget)
                
                edit_btn = QPushButton("Edit")
                edit_btn.setStyleSheet("background-color: #2196F3; color: white;")
                edit_btn.clicked.connect(lambda _, r=row: self.edit_student(r))
                
                delete_btn = QPushButton("Delete")
                delete_btn.setStyleSheet("background-color: #f44336; color: white;")
                delete_btn.clicked.connect(lambda _, r=row: self.delete_student(r))
                
                btn_layout.addWidget(edit_btn)
                btn_layout.addWidget(delete_btn)
                btn_layout.setContentsMargins(0, 0, 0, 0)
                
                self.students_table.setCellWidget(row, 6, btn_widget)
            
            self.students_table.resizeColumnsToContents()
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Error loading students: {str(e)}")
    
    def filter_students(self):
        search_text = self.search_input.text().lower()
        
        for row in range(self.students_table.rowCount()):
            match = False
            for col in range(6):  # Check all columns except Actions
                item = self.students_table.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            
            self.students_table.setRowHidden(row, not match)
    
    def edit_student(self, row):
        roll_no = self.students_table.item(row, 0).text()
        
        edit_dialog = EditStudentDialog(roll_no)
        if edit_dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_students()  # Refresh the table
    
    def delete_student(self, row):
        roll_no = self.students_table.item(row, 0).text()
        name = self.students_table.item(row, 1).text()
        
        reply = QMessageBox.question(
            self, 
            "Confirm Delete",
            f"Are you sure you want to delete student {name} (Roll No: {roll_no})?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                
                cursor.execute("DELETE FROM students WHERE roll_no = ?", (roll_no,))
                conn.commit()
                conn.close()
                
                self.load_students()  # Refresh the table
                
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", f"Error deleting student: {str(e)}")
    
    def add_student(self):
        # Get form data
        roll_no = self.roll_no_input.text().strip()
        name = self.name_input.text().strip()
        age = self.age_input.text().strip()
        gender = self.gender_combo.currentText()
        department = self.dept_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        
        # Validate inputs
        if not all([roll_no, name, password, confirm_password]):
            self.status_label.setText("Please fill in all required fields")
            self.status_label.setStyleSheet("color: red;")
            return
            
        if len(password) < 8:
            self.status_label.setText("Password must be at least 8 characters")
            self.status_label.setStyleSheet("color: red;")
            return
            
        if password != confirm_password:
            self.status_label.setText("Passwords do not match")
            self.status_label.setStyleSheet("color: red;")
            return
            
        try:
            # Process image if uploaded
            image_blob = None
            if hasattr(self, 'image_path'):
                with open(self.image_path, 'rb') as file:
                    image_blob = file.read()
            
            # Hash password
            hashed_password = hash_password(password)
            
            # Connect to database
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Insert student
            cursor.execute('''
                INSERT INTO students (roll_no, name, age, gender, department, image, password)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (roll_no, name, age if age else None, gender, department, image_blob, hashed_password))
            
            conn.commit()
            conn.close()
            
            # Clear form
            self.roll_no_input.clear()
            self.name_input.clear()
            self.age_input.clear()
            self.dept_input.clear()
            self.password_input.clear()
            self.confirm_password_input.clear()
            self.image_path_label.setText("No image selected")
            if hasattr(self, 'image_path'):
                delattr(self, 'image_path')
            
            # Show success message
            self.status_label.setText(f"Student {name} added successfully!")
            self.status_label.setStyleSheet("color: green;")
            
            # Refresh the view students tab if it exists
            if hasattr(self, 'students_table'):
                self.load_students()
            
        except sqlite3.IntegrityError:
            self.status_label.setText(f"Error: Roll number {roll_no} already exists")
            self.status_label.setStyleSheet("color: red;")
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
            self.status_label.setStyleSheet("color: red;")
    
    def go_back(self):
        # Find the main window in the parent hierarchy
        main_window = None
        parent = self.parent()
        while parent:
            if hasattr(parent, 'stacked_widget'):
                main_window = parent
                break
            parent = parent.parent()
        
        if main_window:
            # Go back to admin dashboard (index 5)
            main_window.stacked_widget.setCurrentIndex(5)
        else:
            # Fallback if main window not found
            print("Error: Could not find main window with stacked_widget")
            self.close()  # Close the current widget as fallback


class EditStudentDialog(QDialog):
    def __init__(self, roll_no, parent=None):
        super().__init__(parent)
        self.roll_no = roll_no
        self.setWindowTitle("Edit Student")
        self.setModal(True)
        self.init_ui()
        self.load_student_data()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Roll Number (read-only)
        self.roll_no_label = QLabel()
        form_layout.addRow("Roll Number:", self.roll_no_label)
        
        # Name
        self.name_input = QLineEdit()
        form_layout.addRow("Name:", self.name_input)
        
        # Age
        self.age_input = QLineEdit()
        self.age_input.setValidator(QIntValidator(1, 100))
        form_layout.addRow("Age:", self.age_input)
        
        # Gender
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["Male", "Female", "Other"])
        form_layout.addRow("Gender:", self.gender_combo)
        
        # Department
        self.dept_input = QLineEdit()
        form_layout.addRow("Department:", self.dept_input)
        
        # Password (optional change)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Leave blank to keep current password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("New Password:", self.password_input)
        
        # Confirm Password
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirm new password")
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Confirm Password:", self.confirm_password_input)
        
        # Image Upload
        self.image_path_label = QLabel("No image selected")
        self.image_path_label.setWordWrap(True)
        self.current_image = None
        
        upload_btn = QPushButton("Change Photo")
        upload_btn.clicked.connect(self.upload_image)
        form_layout.addRow("Student Photo:", upload_btn)
        form_layout.addRow("", self.image_path_label)
        
        layout.addLayout(form_layout)
        
        # Button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.save_changes)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Status label
        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
    
    def load_student_data(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute("SELECT name, age, gender, department, image FROM students WHERE roll_no = ?", (self.roll_no,))
            student = cursor.fetchone()
            
            conn.close()
            
            if student:
                name, age, gender, department, image = student
                self.roll_no_label.setText(self.roll_no)
                self.name_input.setText(name)
                self.age_input.setText(str(age) if age else "")
                self.gender_combo.setCurrentText(gender)
                self.dept_input.setText(department)
                
                if image:
                    self.current_image = image
                    self.image_path_label.setText("Current photo (click Change Photo to update)")
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Error loading student data: {str(e)}")
            self.reject()
    
    def upload_image(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp)")
        file_dialog.setViewMode(QFileDialog.ViewMode.Detail)
        
        if file_dialog.exec():
            file_names = file_dialog.selectedFiles()
            if file_names:
                self.image_path = file_names[0]
                self.image_path_label.setText(file_names[0])
    
    def save_changes(self):
        name = self.name_input.text().strip()
        age = self.age_input.text().strip()
        gender = self.gender_combo.currentText()
        department = self.dept_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        
        # Validate inputs
        if not name:
            self.status_label.setText("Name is required")
            self.status_label.setStyleSheet("color: red;")
            return
            
        if password and len(password) < 8:
            self.status_label.setText("Password must be at least 8 characters")
            self.status_label.setStyleSheet("color: red;")
            return
            
        if password and password != confirm_password:
            self.status_label.setText("Passwords do not match")
            self.status_label.setStyleSheet("color: red;")
            return
            
        try:
            # Process image if uploaded
            image_blob = self.current_image
            if hasattr(self, 'image_path'):
                with open(self.image_path, 'rb') as file:
                    image_blob = file.read()
            
            # Connect to database
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            if password:
                # Update with new password
                hashed_password = hash_password(password)
                cursor.execute('''
                    UPDATE students 
                    SET name = ?, age = ?, gender = ?, department = ?, image = ?, password = ?
                    WHERE roll_no = ?
                ''', (name, age if age else None, gender, department, image_blob, hashed_password, self.roll_no))
            else:
                # Update without changing password
                cursor.execute('''
                    UPDATE students 
                    SET name = ?, age = ?, gender = ?, department = ?, image = ?
                    WHERE roll_no = ?
                ''', (name, age if age else None, gender, department, image_blob, self.roll_no))
            
            conn.commit()
            conn.close()
            
            self.accept()
            
        except sqlite3.Error as e:
            self.status_label.setText(f"Error saving changes: {str(e)}")
            self.status_label.setStyleSheet("color: red;")

class TeacherManagementWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("Teacher Management")
        title_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Tab widget for different management options
        tab_widget = QTabWidget()
        
        # Add Teacher Tab
        add_teacher_tab = QWidget()
        self.setup_add_teacher_tab(add_teacher_tab)
        tab_widget.addTab(add_teacher_tab, "Add New Teacher")
        
        # View/Edit Teachers Tab
        view_teachers_tab = QWidget()
        self.setup_view_teachers_tab(view_teachers_tab)
        tab_widget.addTab(view_teachers_tab, "View/Edit Teachers")
        
        main_layout.addWidget(tab_widget)
        
        # Back button
        back_btn = QPushButton("Back to Dashboard")
        back_btn.clicked.connect(self.go_back)
        main_layout.addWidget(back_btn)
    
    def setup_add_teacher_tab(self, tab):
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Teacher ID
        self.teacher_id_input = QLineEdit()
        self.teacher_id_input.setPlaceholderText("Enter unique teacher ID")
        form_layout.addRow("Teacher ID*:", self.teacher_id_input)
        
        # Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter full name")
        form_layout.addRow("Name*:", self.name_input)
        
        # Subject
        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("Enter subject taught")
        form_layout.addRow("Subject*:", self.subject_input)
        
        # Password
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password (min 8 characters)")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Password*:", self.password_input)
        
        # Confirm Password
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Re-enter password")
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Confirm Password*:", self.confirm_password_input)
        
        # Password requirements label
        password_req_label = QLabel("* Required fields | Password must be at least 8 characters")
        password_req_label.setStyleSheet("font-size: 10px; color: #666;")
        form_layout.addRow("", password_req_label)
        
        layout.addLayout(form_layout)
        
        # Add Teacher Button
        add_btn = QPushButton("Add Teacher")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        add_btn.clicked.connect(self.add_teacher)
        layout.addWidget(add_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Status label
        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        layout.addStretch()
    
    def setup_view_teachers_tab(self, tab):
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name or ID...")
        self.search_input.textChanged.connect(self.filter_teachers)
        search_layout.addWidget(self.search_input)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_teachers)
        search_layout.addWidget(refresh_btn)
        layout.addLayout(search_layout)
        
        # Teachers table
        self.teachers_table = QTableWidget()
        self.teachers_table.setColumnCount(4)  # ID, Name, Subject, Actions
        self.teachers_table.setHorizontalHeaderLabels(["Teacher ID", "Name", "Subject", "Actions"])
        self.teachers_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.teachers_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        # Load initial data
        self.load_teachers()
        
        layout.addWidget(self.teachers_table)
        
    def load_teachers(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute("SELECT teacher_id, name, subject FROM teachers ORDER BY name")
            teachers = cursor.fetchall()
            
            conn.close()
            
            self.teachers_table.setRowCount(len(teachers))
            
            for row, (teacher_id, name, subject) in enumerate(teachers):
                # Teacher ID
                self.teachers_table.setItem(row, 0, QTableWidgetItem(teacher_id))
                
                # Name
                self.teachers_table.setItem(row, 1, QTableWidgetItem(name))
                
                # Subject
                self.teachers_table.setItem(row, 2, QTableWidgetItem(subject))
                
                # Action buttons
                btn_widget = QWidget()
                btn_layout = QHBoxLayout(btn_widget)
                
                edit_btn = QPushButton("Edit")
                edit_btn.setStyleSheet("background-color: #2196F3; color: white;")
                edit_btn.clicked.connect(lambda _, r=row: self.edit_teacher(r))
                
                delete_btn = QPushButton("Delete")
                delete_btn.setStyleSheet("background-color: #f44336; color: white;")
                delete_btn.clicked.connect(lambda _, r=row: self.delete_teacher(r))
                
                btn_layout.addWidget(edit_btn)
                btn_layout.addWidget(delete_btn)
                btn_layout.setContentsMargins(0, 0, 0, 0)
                
                self.teachers_table.setCellWidget(row, 3, btn_widget)
            
            self.teachers_table.resizeColumnsToContents()
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Error loading teachers: {str(e)}")
    
    def filter_teachers(self):
        search_text = self.search_input.text().lower()
        
        for row in range(self.teachers_table.rowCount()):
            match = False
            for col in range(3):  # Check ID, Name, Subject columns
                item = self.teachers_table.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            
            self.teachers_table.setRowHidden(row, not match)
    
    def edit_teacher(self, row):
        teacher_id = self.teachers_table.item(row, 0).text()
        
        # Find the main window in the parent hierarchy
        main_window = None
        parent = self.parent()
        while parent:
            if hasattr(parent, 'stacked_widget'):
                main_window = parent
                break
            parent = parent.parent()
        
        if main_window:
            # Create and show edit dialog
            edit_dialog = EditTeacherDialog(teacher_id)
            if edit_dialog.exec() == QDialog.DialogCode.Accepted:
                self.load_teachers()  # Refresh the table
    
    def delete_teacher(self, row):
        teacher_id = self.teachers_table.item(row, 0).text()
        name = self.teachers_table.item(row, 1).text()
        
        reply = QMessageBox.question(
            self, 
            "Confirm Delete",
            f"Are you sure you want to delete teacher {name} (ID: {teacher_id})?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                
                cursor.execute("DELETE FROM teachers WHERE teacher_id = ?", (teacher_id,))
                conn.commit()
                conn.close()
                
                self.load_teachers()  # Refresh the table
                
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", f"Error deleting teacher: {str(e)}")
    
    def add_teacher(self):
        # Get form data
        teacher_id = self.teacher_id_input.text().strip()
        name = self.name_input.text().strip()
        subject = self.subject_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        
        # Validate inputs
        if not all([teacher_id, name, subject, password, confirm_password]):
            self.status_label.setText("Please fill in all required fields")
            self.status_label.setStyleSheet("color: red;")
            return
            
        if len(password) < 8:
            self.status_label.setText("Password must be at least 8 characters")
            self.status_label.setStyleSheet("color: red;")
            return
            
        if password != confirm_password:
            self.status_label.setText("Passwords do not match")
            self.status_label.setStyleSheet("color: red;")
            return
            
        try:
            # Hash password
            hashed_password = hash_password(password)
            
            # Connect to database
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Insert teacher
            cursor.execute('''
                INSERT INTO teachers (teacher_id, name, subject, password)
                VALUES (?, ?, ?, ?)
            ''', (teacher_id, name, subject, hashed_password))
            
            conn.commit()
            conn.close()
            
            # Clear form
            self.teacher_id_input.clear()
            self.name_input.clear()
            self.subject_input.clear()
            self.password_input.clear()
            self.confirm_password_input.clear()
            
            # Show success message
            self.status_label.setText(f"Teacher {name} added successfully!")
            self.status_label.setStyleSheet("color: green;")
            
            # Refresh the view teachers tab if it exists
            if hasattr(self, 'teachers_table'):
                self.load_teachers()
            
        except sqlite3.IntegrityError:
            self.status_label.setText(f"Error: Teacher ID {teacher_id} already exists")
            self.status_label.setStyleSheet("color: red;")
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
            self.status_label.setStyleSheet("color: red;")
    
    def go_back(self):
        # Find the main window in the parent hierarchy
        main_window = None
        parent = self.parent()
        while parent:
            if hasattr(parent, 'stacked_widget'):
                main_window = parent
                break
            parent = parent.parent()
        
        if main_window:
            # Go back to admin dashboard (index 5)
            main_window.stacked_widget.setCurrentIndex(5)


class EditTeacherDialog(QDialog):
    def __init__(self, teacher_id, parent=None):
        super().__init__(parent)
        self.teacher_id = teacher_id
        self.setWindowTitle("Edit Teacher")
        self.setModal(True)
        self.init_ui()
        self.load_teacher_data()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Teacher ID (read-only)
        self.id_label = QLabel()
        form_layout.addRow("Teacher ID:", self.id_label)
        
        # Name
        self.name_input = QLineEdit()
        form_layout.addRow("Name:", self.name_input)
        
        # Subject
        self.subject_input = QLineEdit()
        form_layout.addRow("Subject:", self.subject_input)
        
        # Password (optional change)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Leave blank to keep current password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("New Password:", self.password_input)
        
        # Confirm Password
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirm new password")
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Confirm Password:", self.confirm_password_input)
        
        layout.addLayout(form_layout)
        
        # Button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.save_changes)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Status label
        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
    
    def load_teacher_data(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute("SELECT name, subject FROM teachers WHERE teacher_id = ?", (self.teacher_id,))
            teacher = cursor.fetchone()
            
            conn.close()
            
            if teacher:
                self.id_label.setText(self.teacher_id)
                self.name_input.setText(teacher[0])
                self.subject_input.setText(teacher[1])
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Error loading teacher data: {str(e)}")
            self.reject()
    
    def save_changes(self):
        name = self.name_input.text().strip()
        subject = self.subject_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        
        # Validate inputs
        if not all([name, subject]):
            self.status_label.setText("Name and subject are required")
            self.status_label.setStyleSheet("color: red;")
            return
            
        if password and len(password) < 8:
            self.status_label.setText("Password must be at least 8 characters")
            self.status_label.setStyleSheet("color: red;")
            return
            
        if password and password != confirm_password:
            self.status_label.setText("Passwords do not match")
            self.status_label.setStyleSheet("color: red;")
            return
            
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            if password:
                # Update with new password
                hashed_password = hash_password(password)
                cursor.execute('''
                    UPDATE teachers 
                    SET name = ?, subject = ?, password = ?
                    WHERE teacher_id = ?
                ''', (name, subject, hashed_password, self.teacher_id))
            else:
                # Update without changing password
                cursor.execute('''
                    UPDATE teachers 
                    SET name = ?, subject = ?
                    WHERE teacher_id = ?
                ''', (name, subject, self.teacher_id))
            
            conn.commit()
            conn.close()
            
            self.accept()
            
        except sqlite3.Error as e:
            self.status_label.setText(f"Error saving changes: {str(e)}")
            self.status_label.setStyleSheet("color: red;")

class AllTeachersWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("All Teachers")
        title_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Create table
        self.teachers_table = QTableWidget()
        self.teachers_table.setColumnCount(4)  # Teacher ID, Name, Subject, Actions
        self.teachers_table.setHorizontalHeaderLabels(["Teacher ID", "Name", "Subject", "Actions"])
        self.teachers_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.teachers_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        # Populate table
        self.populate_teachers()
        
        main_layout.addWidget(self.teachers_table)
        
        # Back button
        back_btn = QPushButton("Back to Dashboard")
        back_btn.clicked.connect(self.go_back)
        main_layout.addWidget(back_btn)
    
    def populate_teachers(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute("SELECT teacher_id, name, subject FROM teachers")
            teachers = cursor.fetchall()
            
            conn.close()
            
            self.teachers_table.setRowCount(len(teachers))
            
            for row, (teacher_id, name, subject) in enumerate(teachers):
                # Teacher ID
                self.teachers_table.setItem(row, 0, QTableWidgetItem(str(teacher_id)))
                # Name
                self.teachers_table.setItem(row, 1, QTableWidgetItem(name))
                # Subject
                self.teachers_table.setItem(row, 2, QTableWidgetItem(subject))
                
                # View Button
                view_btn = QPushButton("View Subject")
                view_btn.clicked.connect(lambda _, r=row: self.view_teacher_subject(r))
                self.teachers_table.setCellWidget(row, 3, view_btn)
        
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Error: {str(e)}")
    
    def view_teacher_subject(self, row):
        teacher_id = self.teachers_table.item(row, 0).text()
        subject = self.teachers_table.item(row, 2).text()
        
        # Find the main window in the parent hierarchy
        main_window = None
        parent = self.parent()
        while parent:
            if hasattr(parent, 'stacked_widget'):
                main_window = parent
                break
            parent = parent.parent()
        
        if main_window:
            # Create subject details window with admin flag
            subject_widget = SubjectDetailsWindow(teacher_id, subject, is_admin_view=True)
            main_window.stacked_widget.addWidget(subject_widget)
            main_window.stacked_widget.setCurrentIndex(
                main_window.stacked_widget.count() - 1
            )
    
    def go_back(self):
        """Navigate back to the teachers list by finding our position in the stack"""
        # Find the main window with stacked_widget
        main_window = None
        parent = self.parent()
        while parent:
            if hasattr(parent, 'stacked_widget'):
                main_window = parent
                break
            parent = parent.parent()
        
        if main_window:
            # Find our position in the stack
            for i in range(main_window.stacked_widget.count()):
                if main_window.stacked_widget.widget(i) == self:
                    # If we're not the first widget, go back one
                    if i > 0:
                        main_window.stacked_widget.setCurrentIndex(i-1)
                    else:
                        # Fallback to admin dashboard if we're at the bottom
                        main_window.stacked_widget.setCurrentIndex(5)
                    return
            
            # If we didn't find ourselves in the stack, go to admin dashboard
            main_window.stacked_widget.setCurrentIndex(5)

class AllStudentsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("All Students")
        title_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Create table
        self.students_table = QTableWidget()
        self.students_table.setColumnCount(3)
        self.students_table.setHorizontalHeaderLabels(["Roll No", "Name", "Actions"])
        self.students_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.students_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        # Populate table
        self.populate_students()
        
        main_layout.addWidget(self.students_table)
        
        # Back button
        back_btn = QPushButton("Back to Dashboard")
        back_btn.clicked.connect(self.go_back)
        main_layout.addWidget(back_btn)
    
    def populate_students(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute("SELECT roll_no, name FROM students ORDER BY roll_no")
            students = cursor.fetchall()
            
            conn.close()
            
            self.students_table.setRowCount(len(students))
            
            for row, (roll_no, name) in enumerate(students):
                self.students_table.setItem(row, 0, QTableWidgetItem(str(roll_no)))
                self.students_table.setItem(row, 1, QTableWidgetItem(name))
                
                view_btn = QPushButton("View Attendance")
                view_btn.clicked.connect(lambda _, r=row: self.view_student_attendance(r))
                self.students_table.setCellWidget(row, 2, view_btn)
        
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Error: {str(e)}")
    
    def view_student_attendance(self, row):
        roll_no = self.students_table.item(row, 0).text()
        name = self.students_table.item(row, 1).text()
        
        # Find the main window
        main_window = self._find_main_window()
        if main_window:
            # Remove any existing StudentAttendanceWidget from the stack
            self._clean_stack(main_window, StudentAttendanceWidget)
            
            # Add new attendance widget
            attendance_widget = StudentAttendanceWidget(roll_no, name)
            main_window.stacked_widget.addWidget(attendance_widget)
            main_window.stacked_widget.setCurrentIndex(
                main_window.stacked_widget.count() - 1
            )
    
    def _find_main_window(self):
        """Helper method to find the main window"""
        parent = self.parent()
        while parent:
            if hasattr(parent, 'stacked_widget'):
                return parent
            parent = parent.parent()
        return None
    
    def _clean_stack(self, main_window, widget_class):
        """Remove any existing widgets of specified type from the stack"""
        for i in reversed(range(main_window.stacked_widget.count())):
            widget = main_window.stacked_widget.widget(i)
            if isinstance(widget, widget_class):
                main_window.stacked_widget.removeWidget(widget)
                widget.deleteLater()
    
    def go_back(self):
        main_window = self._find_main_window()
        if main_window:
            main_window.stacked_widget.setCurrentIndex(5)  # Admin Dashboard index


class StudentAttendanceWidget(QWidget):
    def __init__(self, roll_no, name, parent=None):
        super().__init__(parent)
        self.roll_no = roll_no
        self.name = name
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel(f"Attendance for {self.name} (Roll No: {self.roll_no})")
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Create scroll area for attendance information
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        # Widget to hold attendance data
        attendance_widget = QWidget()
        attendance_layout = QVBoxLayout(attendance_widget)
        attendance_layout.setSpacing(15)
        
        # Get attendance data
        attendance_data = self.calculate_attendance(self.roll_no)
        
        if not attendance_data:
            no_data_label = QLabel("No attendance data found.")
            no_data_label.setFont(QFont("Arial", 14))
            no_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            attendance_layout.addWidget(no_data_label)
        else:
            # Display attendance for each subject
            for subject, data in attendance_data.items():
                subject_frame = QFrame()
                subject_frame.setStyleSheet("""
                    QFrame {
                        background-color: rgba(173, 216, 230, 0.3);
                        border-radius: 8px;
                        padding: 10px;
                    }
                """)
                
                subject_layout = QVBoxLayout(subject_frame)
                
                # Subject name
                subject_label = QLabel(subject)
                subject_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
                subject_layout.addWidget(subject_label)
                
                # Attendance details
                details_layout = QGridLayout()
                details_layout.setColumnStretch(0, 1)
                details_layout.setColumnStretch(1, 2)
                
                # Add attendance details
                row = 0
                for key, value in data.items():
                    if key != "percentage":
                        label = QLabel(f"{key}:")
                        label.setFont(QFont("Arial", 12))
                        
                        value_label = QLabel(str(value))
                        value_label.setFont(QFont("Arial", 12))
                        
                        details_layout.addWidget(label, row, 0)
                        details_layout.addWidget(value_label, row, 1)
                        row += 1
                
                subject_layout.addLayout(details_layout)
                
                # Progress bar for percentage
                percentage = data["percentage"]
                progress_bar = QProgressBar()
                progress_bar.setValue(int(percentage))
                progress_bar.setTextVisible(True)
                progress_bar.setFormat(f"{percentage:.1f}%")
                
                # Set color based on percentage
                if percentage >= 75:
                    color = "#4CAF50"  # Green
                elif percentage >= 60:
                    color = "#FFC107"  # Yellow
                else:
                    color = "#F44336"  # Red
                
                progress_bar.setStyleSheet(f"""
                    QProgressBar {{
                        background-color: rgba(255, 255, 255, 0.2);
                        color: black;
                        border-radius: 5px;
                        text-align: center;
                        height: 20px;
                    }}
                    
                    QProgressBar::chunk {{
                        background-color: {color};
                        border-radius: 5px;
                    }}
                """)
                
                subject_layout.addWidget(progress_bar)
                attendance_layout.addWidget(subject_frame)
        
        scroll_area.setWidget(attendance_widget)
        main_layout.addWidget(scroll_area)
        
        # Back button
        back_btn = QPushButton("Back to Students List")
        back_btn.clicked.connect(self.go_back)
        main_layout.addWidget(back_btn)
    
    def calculate_attendance(self, roll_no):
        attendance_data = {}
        
        try:
            csv_files = [
                f for f in os.listdir(ATTENDANCE_DIR) 
                if f.endswith('.csv') and f != 'late_comers.csv'
            ]
            
            for file in csv_files:
                subject = os.path.splitext(file)[0].capitalize()
                file_path = os.path.join(ATTENDANCE_DIR, file)
                
                df = pd.read_csv(
                    file_path, 
                    header=0, 
                    names=["Roll No", "Name", "Attendance", "Late", "Time_of_Entry", "Date", "Time_of_Exit", "Period_Time"]
                )
                
                student_data = df[df["Roll No"].astype(str) == str(roll_no)]
                
                if not student_data.empty:
                    total_days = len(student_data["Date"].unique())
                    days_present = len(student_data[student_data["Attendance"] == "Present"]["Date"].unique())
                    
                    percentage = (days_present / total_days) * 100 if total_days > 0 else 0
                    
                    attendance_data[subject] = {
                        "Total Days": total_days,
                        "Days Present": days_present,
                        "Days Absent": total_days - days_present,
                        "percentage": percentage
                    }
        
        except Exception as e:
            print(f"Error calculating attendance: {e}")
        
        return attendance_data
    
    def go_back(self):
        """Go back to students list by finding the AllStudentsWidget in the stack"""
        main_window = None
        parent = self.parent()
        while parent:
            if hasattr(parent, 'stacked_widget'):
                main_window = parent
                break
            parent = parent.parent()
        
        if main_window:
            # Find and show the AllStudentsWidget in the stack
            for i in range(main_window.stacked_widget.count()):
                widget = main_window.stacked_widget.widget(i)
                if isinstance(widget, AllStudentsWidget):
                    main_window.stacked_widget.setCurrentIndex(i)
                    return
            
            # If not found, go back to admin dashboard (index 5)
            main_window.stacked_widget.setCurrentIndex(5)




class TeacherLoginWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setSpacing(20)
        
        # Apply gradient background
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(0, 128, 128))
        gradient.setColorAt(1, QColor(32, 178, 170))
        
        palette = self.palette()
        palette.setBrush(QPalette.ColorRole.Window, QBrush(gradient))
        self.setPalette(palette)
        
        # Back button to return to main menu
        back_layout = QHBoxLayout()
        back_button = QPushButton("Back to Main Menu")
        back_button.setFont(QFont("Arial", 12))
        back_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)
        back_button.clicked.connect(self.back_to_main)
        back_layout.addWidget(back_button)
        back_layout.addStretch()
        main_layout.addLayout(back_layout)
        
        # Title
        title_label = QLabel("Teacher Login")
        title_label.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: rgba(255, 255, 255, 0.3);")
        main_layout.addWidget(separator)
        
        # Form layout
        form_layout = QGridLayout()
        form_layout.setSpacing(15)
        
        # Login ID
        login_id_label = QLabel("Login ID:")
        login_id_label.setFont(QFont("Arial", 14))
        login_id_label.setStyleSheet("color: white;")

        self.login_id_input = QLineEdit()
        self.login_id_input.setPlaceholderText("Enter your Teacher ID")
        self.login_id_input.setFont(QFont("Arial", 14))
        self.login_id_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.9);
                border-radius: 5px;
                padding: 10px;
                color: #333333; /* Dark gray for entered text */
            }
            QLineEdit::placeholder {
                color: #666666; /* Medium gray for placeholder */
            }
        """)
        
        # Password
        password_label = QLabel("Password:")
        password_label.setFont(QFont("Arial", 14))
        password_label.setStyleSheet("color: white;")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFont(QFont("Arial", 14))
        self.password_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.9);
                border-radius: 5px;
                padding: 10px;
                color: #333333; /* Dark gray for entered text */
            }
            QLineEdit::placeholder {
                color: #666666; /* Medium gray for placeholder */
            }
        """)

        # Add f
        
        # Add fields to form
        form_layout.addWidget(login_id_label, 0, 0)
        form_layout.addWidget(self.login_id_input, 0, 1)
        form_layout.addWidget(password_label, 1, 0)
        form_layout.addWidget(self.password_input, 1, 1)
        
        main_layout.addLayout(form_layout)
        main_layout.addSpacing(20)
        
        # Login button
        login_btn = QPushButton("Login")
        login_btn.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 8px;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #388E3C;
            }
        """)
        login_btn.clicked.connect(self.verify_login)
        main_layout.addWidget(login_btn)
        
        main_layout.addStretch()
    
    def back_to_main(self):
        """Returns to the main menu."""
        # Clear input fields
        self.login_id_input.clear()
        self.password_input.clear()
        
        # Try multiple approaches to find the main window
        parent = self.parent()
        while parent is not None:
            # Check if this is a main window with stacked widget
            if hasattr(parent, 'stacked_widget'):
                parent.stacked_widget.setCurrentIndex(0)  # Switch to main menu
                return
            
            # Check if this is a QMainWindow (common main window class)
            if isinstance(parent, QMainWindow):
                # If it has a central widget with stacked widget
                if hasattr(parent.centralWidget(), 'stacked_widget'):
                    parent.centralWidget().stacked_widget.setCurrentIndex(0)
                    return
            
            # Move up the parent hierarchy
            parent = parent.parent()
        
        # If we didn't find the main window, try closing this widget
        self.close()
        
        # Debug output (can be removed after testing)
        print("Could not find main window with stacked widget in parent hierarchy")
        print("Current parent chain:")
        p = self.parent()
        while p:
            print(f"- {p.__class__.__name__}")
            p = p.parent()
    
    def verify_login(self):
        teacher_id = self.login_id_input.text()
        password = self.password_input.text()
        
        # Check if fields are empty
        if not teacher_id or not password:
            QMessageBox.warning(self, "Login Error", "Please enter both Teacher ID and Password.")
            return
        
        # Connect to database
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Query teacher table
            cursor.execute("SELECT password, subject FROM teachers WHERE teacher_id = ?", (teacher_id,))
            teacher = cursor.fetchone()
            
            conn.close()
            
            # Verify credentials
            if teacher:
                stored_password = teacher[0]  # Hashed password from the database
                subject = teacher[1]  # Subject taught by the teacher
                
                # Verify the password
                if check_password(password, stored_password):
                    # Open subject details window
                    self.subject_window = SubjectDetailsWindow(teacher_id, subject)
                    self.subject_window.show()
                    
                    # Clear input fields
                    self.login_id_input.clear()
                    self.password_input.clear()
                    
                    # Return to main menu
                    self.back_to_main()
                else:
                    QMessageBox.warning(self, "Login Error", "Invalid Teacher ID or Password.")
            else:
                QMessageBox.warning(self, "Login Error", "Invalid Teacher ID or Password.")
                    
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Error connecting to database: {str(e)}")          
        
                

class SubjectDetailsWindow(QMainWindow):
    def __init__(self, teacher_id, subject, is_admin_view=False):
        super().__init__()
        self.teacher_id = teacher_id
        self.subject = subject
        self.is_admin_view = is_admin_view  # Flag to track admin access
        self.init_ui()
        self.load_attendance_data()
        
    def init_ui(self):
        self.setWindowTitle(f"Subject: {self.subject} - Teacher Dashboard")
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Header with teacher and subject info
        header_layout = QHBoxLayout()
        
        teacher_info = self.get_teacher_info()
        if teacher_info:
            header_text = f"📚 {teacher_info.get('name', 'Unknown')} | Subject: {self.subject}"
        else:
             header_text = f"📚 {self.subject}"
            
        header_label = QLabel(header_text)
        header_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header_label.setStyleSheet("""
        background: qlineargradient(
            x1:0, y1:0, x2:0, y2:1,
            stop:0 #0F172A,  /* Deep navy (almost black-blue) */
            stop:1 #1E40AF   /* Rich royal blue */
        );
        color: white;
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: bold;
        font-size: 18px;
        border: 1px solid rgba(255, 255, 255, 0.1);  /* Subtle white border */
    """)
        header_layout.addWidget(header_label)
        
        
        # Date selection
        date_layout = QHBoxLayout()
        date_label = QLabel("Date:")
        date_label.setFont(QFont("Arial", 14))
        
        self.date_input = QLineEdit()
        current_date = datetime.now().strftime("%Y-%m-%d")
        self.date_input.setText(current_date)
        self.date_input.setFont(QFont("Arial", 14))
        self.date_input.setFixedWidth(150)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setFont(QFont("Arial", 12))
        refresh_btn.clicked.connect(self.load_attendance_data)
        
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_input)
        date_layout.addWidget(refresh_btn)
        date_layout.addStretch()
        
        header_layout.addLayout(date_layout)
        main_layout.addLayout(header_layout)
        
        # Create a tab widget for different views
        tab_widget = QTabWidget()
        
        # Attendance Table Tab
        attendance_tab = QWidget()
        attendance_layout = QVBoxLayout(attendance_tab)
        
        # Create table for attendance data
        self.attendance_table = QTableWidget()
        self.attendance_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                gridline-color: #d3d3d3;
                selection-background-color: #3498db;
                selection-color: white;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 6px;
                font-weight: bold;
            }
        """)
        
        attendance_layout.addWidget(self.attendance_table)
        
        # Summary Tab
        summary_tab = QWidget()
        summary_layout = QVBoxLayout(summary_tab)
        
        self.summary_widget = QWidget()
        summary_content_layout = QVBoxLayout(self.summary_widget)
        
        # Attendance Statistics
        stats_label = QLabel("Attendance Statistics")
        stats_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        summary_content_layout.addWidget(stats_label)
        
        # Stats will be populated in load_attendance_data method
        self.stats_layout = QGridLayout()
        summary_content_layout.addLayout(self.stats_layout)
        
        # Add scroll area for summary tab
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.summary_widget)
        scroll_area.setWidgetResizable(True)
        summary_layout.addWidget(scroll_area)
        
        # Add tabs to tab widget
        tab_widget.addTab(attendance_tab, "Attendance Records")
        tab_widget.addTab(summary_tab, "Summary & Statistics")
        
        main_layout.addWidget(tab_widget)
        
        # Export button
        export_btn = QPushButton("Export to Excel")
        export_btn.setFont(QFont("Arial", 14))
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        export_btn.clicked.connect(self.export_to_excel)
        
        # Back button
        back_btn = QPushButton("Back to Home")
        back_btn.setFont(QFont("Arial", 14))
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #7f8c8d;
                color: white;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #95a5a6;
            }
        """)
        back_btn.clicked.connect(self.go_back)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(back_btn)
        button_layout.addStretch()
        button_layout.addWidget(export_btn)
        
        main_layout.addLayout(button_layout)
    
    def go_back(self):
        """Handle back navigation based on access path"""
        if self.is_admin_view:
            self._go_back_to_teachers_list()
        else:
            self.close()  # Maintain existing behavior for teacher login
    
    def _go_back_to_teachers_list(self):
        """Navigate back to AllTeachersWidget from admin view"""
        main_window = None
        parent = self.parent()
        while parent:
            if hasattr(parent, 'stacked_widget'):
                main_window = parent
                break
            parent = parent.parent()
        
        if main_window:
            # Find and show the AllTeachersWidget in the stack
            for i in range(main_window.stacked_widget.count()):
                widget = main_window.stacked_widget.widget(i)
                if isinstance(widget, AllTeachersWidget):
                    main_window.stacked_widget.setCurrentIndex(i)
                    # Remove this details window from stack
                    main_window.stacked_widget.removeWidget(self)
                    self.deleteLater()
                    return
            
            # Fallback to admin dashboard if teachers list not found
            main_window.stacked_widget.setCurrentIndex(5)
            main_window.stacked_widget.removeWidget(self)
            self.deleteLater()
    
    def get_teacher_info(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM teachers WHERE teacher_id = ?", (self.teacher_id,))
            teacher = cursor.fetchone()
            
            conn.close()
            
            if teacher:
                # Assuming teacher table has columns: teacher_id, name, subject, etc.
                return {
                    "teacher_id": teacher[0],
                    "name": teacher[1] if len(teacher) > 1 else "Unknown",
                    "subject": teacher[2] if len(teacher) > 2 else "Unknown"
                }
            return None
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Error fetching teacher info: {str(e)}")
            return None
    
    def load_attendance_data(self):
        selected_date = self.date_input.text().strip()
        subject_file = f"{ATTENDANCE_DIR}/{self.subject}.csv"
        
        if not os.path.exists(subject_file):
            QMessageBox.information(self, "No Data", f"No attendance data found for {self.subject}")
            return
        
        try:
            # Read with explicit encoding and clean data
            with open(subject_file, "r", encoding='utf-8-sig') as file:
                reader = csv.reader(file)
                all_rows = [[cell.strip() for cell in row] for row in reader if row]
                
                if not all_rows:
                    QMessageBox.information(self, "Empty File", "File is empty")
                    return
                    
                headers = all_rows[0]
                
                try:
                    date_index = headers.index("Date")
                except ValueError:
                    QMessageBox.warning(self, "Error", "Date column missing")
                    return

                # Filter rows for selected date
                filtered_rows = [row for row in all_rows[1:] 
                            if len(row) > date_index and row[date_index] == selected_date]

                print(f"Debug - Found {len(filtered_rows)} rows")
                if filtered_rows:
                    print(f"Sample row: {filtered_rows[0]}")

                # Reset table
                self.attendance_table.clearContents()
                self.attendance_table.setRowCount(0)
                self.attendance_table.setColumnCount(len(headers))
                self.attendance_table.setHorizontalHeaderLabels(headers)
                
                # Populate table with visual debugging
                self.attendance_table.setRowCount(len(filtered_rows))
                for row_idx, row in enumerate(filtered_rows):
                    for col_idx in range(len(headers)):
                        value = row[col_idx] if col_idx < len(row) else ""
                        item = QTableWidgetItem(value)
                        
                        # PyQt6 color syntax
                        item.setForeground(QColor(Qt.GlobalColor.black))
                        item.setBackground(QColor(Qt.GlobalColor.white))
                        
                        # Make text clearly visible
                        font = QFont()
                        font.setBold(True)
                        item.setFont(font)
                        
                        self.attendance_table.setItem(row_idx, col_idx, item)

                # Force UI update
                self.attendance_table.resizeColumnsToContents()
                self.attendance_table.setVisible(True)
                self.attendance_table.viewport().update()
                QApplication.processEvents()

                # Update statistics
                self.update_statistics(filtered_rows, headers)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load data: {str(e)}")
            traceback.print_exc()  # Use the imported traceback
    
    def update_statistics(self, rows, headers):
        # Clear existing stats
        for i in reversed(range(self.stats_layout.count())): 
            self.stats_layout.itemAt(i).widget().setParent(None)
        
        if not rows:
            no_data_label = QLabel("No attendance data for selected date")
            no_data_label.setFont(QFont("Arial", 14))
            self.stats_layout.addWidget(no_data_label, 0, 0)
            return
        
        # Calculate statistics
        total_students = len(rows)
        
        # Find indices for attendance and late status
        attendance_idx = headers.index("Attendance") if "Attendance" in headers else 2
        late_idx = headers.index("Late") if "Late" in headers else 3
        
        present_count = sum(1 for row in rows if row[attendance_idx] == "Present")
        absent_count = total_students - present_count
        late_count = sum(1 for row in rows if row[late_idx] == "Yes")
        
        attendance_percent = (present_count / total_students * 100) if total_students > 0 else 0
        
        # Create stat labels
        stats = [
            ("Total Students", str(total_students)),
            ("Present", str(present_count)),
            ("Absent", str(absent_count)),
            ("Late", str(late_count)),
            ("Attendance Rate", f"{attendance_percent:.1f}%")
        ]
        
        # Add stats to layout
        for idx, (label, value) in enumerate(stats):
            stat_label = QLabel(label + ":")
            stat_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            
            value_label = QLabel(value)
            value_label.setFont(QFont("Arial", 14))
            
            self.stats_layout.addWidget(stat_label, idx, 0)
            self.stats_layout.addWidget(value_label, idx, 1)
    
    def export_to_excel(self):
        # For a simple implementation, just copy the CSV to Excel format
        try:
            from openpyxl import Workbook
            
            selected_date = self.date_input.text()
            source_file = f"{ATTENDANCE_DIR}/{self.subject}.csv"
            target_file = f"{ATTENDANCE_DIR}/{self.subject}_{selected_date}.xlsx"
            
            # Create workbook and select active worksheet
            wb = Workbook()
            ws = wb.active
            ws.title = f"{self.subject} Attendance"
            
            # Read CSV and write to Excel
            with open(source_file, 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    ws.append(row)
            
            # Save the file
            wb.save(target_file)
            
            QMessageBox.information(self, "Export Successful", 
                                   f"Attendance data exported to {target_file}")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Error exporting data: {str(e)}")


class StudentLoginWindow(QWidget):
    def __init__(self, attendance_folder=r"D:\miniproject\AutomaticAttendanceSystem\attendance"):
        super().__init__()
        self.attendance_folder = attendance_folder
        self.current_student = None
        #self.parent_window = parent
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Student Login")
        self.setGeometry(300, 300, 600, 400)
        
        # Apply gradient background
        self.set_gradient_background()
        
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(50, 50, 50, 50)
        self.main_layout.setSpacing(20)
        
        # Show login form initially
        self.show_login_form()

        # Add back button at the top
        if self.parent:  # Only show back button if we have a parent window
            back_btn = QPushButton("← Back to Home")
            back_btn.setFont(QFont("Arial", 10))
            back_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: white;
                    border: none;
                    padding: 5px;
                    text-align: left;
                }
                QPushButton:hover {
                    color: #FFD700;
                }
            """)
            back_btn.clicked.connect(self.go_back_to_home)
            self.main_layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignLeft)
    
    def set_gradient_background(self):
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(70, 130, 180))  # SteelBlue
        gradient.setColorAt(1, QColor(100, 149, 237))  # CornflowerBlue
        
        palette = self.palette()
        palette.setBrush(QPalette.ColorRole.Window, QBrush(gradient))
        self.setPalette(palette)
    
    def show_login_form(self):
        # Clear existing widgets from layout
        self.clear_layout(self.main_layout)
        
        # Title
        title_label = QLabel("Student Login")
        title_label.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(title_label)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: rgba(255, 255, 255, 0.3);")
        self.main_layout.addWidget(separator)

        # Add back button at the top if we have a parent window
        if hasattr(self, 'parent') and self.parent():  # Check if parent exists
            back_btn = QPushButton("← Back to Home")
            back_btn.setFont(QFont("Arial", 10))
            back_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: white;
                    border: none;
                    padding: 5px;
                    text-align: left;
                }
                QPushButton:hover {
                    color: #FFD700;
                }
            """)
            back_btn.clicked.connect(self.go_back_to_home)
            self.main_layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        
        # Login form
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)
        
        # Roll number input
        roll_layout = QVBoxLayout()
        roll_label = QLabel("Roll Number:")
        roll_label.setFont(QFont("Arial", 12))
        roll_label.setStyleSheet("color: white;")
        self.roll_input = QLineEdit()
        self.roll_input.setPlaceholderText("Enter your roll number")
        self.roll_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QLineEdit:focus {
                background-color: rgba(255, 255, 255, 0.3);
                border: 1px solid white;
            }
        """)
        roll_layout.addWidget(roll_label)
        roll_layout.addWidget(self.roll_input)
        
        # Password input
        password_layout = QVBoxLayout()
        password_label = QLabel("Password:")
        password_label.setFont(QFont("Arial", 12))
        password_label.setStyleSheet("color: white;")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QLineEdit:focus {
                background-color: rgba(255, 255, 255, 0.3);
                border: 1px solid white;
            }
        """)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        
        # Add fields to form
        form_layout.addLayout(roll_layout)
        form_layout.addLayout(password_layout)
        
        # Login button
        login_btn = QPushButton("Login")
        login_btn.setFont(QFont("Arial", 14))
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                padding: 10px;
            }
             QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #388E3C;
            }
        """)
      

        login_btn.clicked.connect(self.handle_login)
        
        form_layout.addWidget(login_btn)
        self.main_layout.addLayout(form_layout)
        self.main_layout.addStretch()
    
    def handle_login(self):
        roll_no = self.roll_input.text().strip()
        password = self.password_input.text().strip()
        
        if not roll_no or not password:
            self.show_message("Error", "Please enter both roll number and password.")
            return
        
        # In a real application, you would verify against a database
        # For this example, we'll simulate authentication
        if self.authenticate_student(roll_no, password):
            self.current_student = roll_no
            self.show_attendance_dashboard()
        else:
            self.show_message("Login Failed", "Invalid roll number or password.")
    
    def authenticate_student(self, roll_no, password):
        try:
            # Connect to the database
            conn = sqlite3.connect(r'D:\miniproject\AutomaticAttendanceSystem\attendance1.db')
            cursor = conn.cursor()
            
            # Get the hashed password for this roll number
            cursor.execute("SELECT password FROM students WHERE roll_no = ?", (roll_no,))
            result = cursor.fetchone()
            
            if result:
                stored_password_hash = result[0]
                
                # Verify the password using bcrypt
                is_valid = bcrypt.checkpw(password.encode('utf-8'), stored_password_hash)
                
                conn.close()
                return is_valid
            else:
                conn.close()
                return False
                
        except Exception as e:
            print(f"Authentication error: {str(e)}")
            return False
    
    def show_attendance_dashboard(self):
        # Clear existing widgets from layout
        self.clear_layout(self.main_layout)

         # Add back button at the top if we have a parent window
        if hasattr(self, 'parent') and self.parent():  # Check if parent exists
            back_btn = QPushButton("← Back to Home")
            back_btn.setFont(QFont("Arial", 10))
            back_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: white;
                    border: none;
                    padding: 5px;
                    text-align: left;
                }
                QPushButton:hover {
                    color: #FFD700;
                }
            """)
            back_btn.clicked.connect(self.go_back_to_home)
            self.main_layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        
        # Title
        title_label = QLabel(f"Attendance Dashboard")
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(title_label)
        
        # Student info
        student_info = QLabel(f"Roll No: {self.current_student}")
        student_info.setFont(QFont("Arial", 14))
        student_info.setStyleSheet("color: white;")
        student_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(student_info)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: rgba(255, 255, 255, 0.3);")
        self.main_layout.addWidget(separator)
        
        # Create a scroll area for attendance information
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                border: none;
            }
        """)
        
        # Widget to hold attendance data
        attendance_widget = QWidget()
        attendance_layout = QVBoxLayout(attendance_widget)
        attendance_layout.setSpacing(15)
        
        # Get attendance data
        try:
            attendance_data = self.calculate_attendance(self.current_student)
            
            if not attendance_data:
                no_data_label = QLabel("No attendance data found.")
                no_data_label.setFont(QFont("Arial", 14))
                no_data_label.setStyleSheet("color: white;")
                no_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                attendance_layout.addWidget(no_data_label)
            else:
                # Display attendance for each subject
                for subject, data in attendance_data.items():
                    subject_frame = QFrame()
                    subject_frame.setStyleSheet("""
                        QFrame {
                            background-color: rgba(255, 255, 255, 0.15);
                            border-radius: 8px;
                            padding: 10px;
                        }
                    """)
                    
                    subject_layout = QVBoxLayout(subject_frame)
                    
                    # Subject name
                    subject_label = QLabel(subject)
                    subject_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
                    subject_label.setStyleSheet("color: white;")
                    subject_layout.addWidget(subject_label)
                    
                    # Attendance details
                    details_layout = QGridLayout()
                    details_layout.setColumnStretch(0, 1)
                    details_layout.setColumnStretch(1, 2)
                    
                    # Add attendance details
                    row = 0
                    for key, value in data.items():
                        if key != "percentage":
                            label = QLabel(f"{key}:")
                            label.setFont(QFont("Arial", 12))
                            label.setStyleSheet("color: rgba(255, 255, 255, 0.8);")
                            
                            value_label = QLabel(str(value))
                            value_label.setFont(QFont("Arial", 12))
                            value_label.setStyleSheet("color: white;")
                            
                            details_layout.addWidget(label, row, 0)
                            details_layout.addWidget(value_label, row, 1)
                            row += 1
                    
                    subject_layout.addLayout(details_layout)
                    
                    # Progress bar for percentage
                    percentage = data["percentage"]
                    progress_bar = QProgressBar()
                    progress_bar.setValue(int(percentage))
                    progress_bar.setTextVisible(True)
                    progress_bar.setFormat(f"{percentage:.1f}%")
                    progress_bar.setStyleSheet(self.get_progress_bar_style(percentage))
                    subject_layout.addWidget(progress_bar)
                    
                    attendance_layout.addWidget(subject_frame)
        
        except Exception as e:
            error_label = QLabel(f"Error loading attendance data: {str(e)}")
            error_label.setFont(QFont("Arial", 12))
            error_label.setStyleSheet("color: white;")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            attendance_layout.addWidget(error_label)
        
        scroll_area.setWidget(attendance_widget)
        self.main_layout.addWidget(scroll_area)
        
        
        # Logout button
        logout_btn = QPushButton("Logout")
        logout_btn.setFont(QFont("Arial", 16))
        logout_btn.setStyleSheet("""
        QPushButton {
            background-color: rgba(255, 138, 128, 0.25);  /* Soft coral red with transparency */
            color: red;
            border-radius: 5px;
            padding: 10px;
            border: none;
        }
        QPushButton:hover {
            background-color: #ef5350;  /* Lighter red */
        }
        QPushButton:pressed {
            background-color: #c62828;  /* Darker red */
        }
    """)
        
        logout_btn.clicked.connect(self.show_login_form)
        self.main_layout.addWidget(logout_btn)
    
    def calculate_attendance(self, roll_no):
        attendance_data = {}
        
        try:
            print(f"Looking for attendance data for roll number: {roll_no}")
            print(f"Attendance folder path: {self.attendance_folder}")
            
            # Check if directory exists
            if not os.path.exists(self.attendance_folder):
                print(f"ERROR: Directory does not exist: {self.attendance_folder}")
                return {}
            
            # Get all CSV files EXCEPT late_comers.csv
            try:
                csv_files = [
                    f for f in os.listdir(self.attendance_folder) 
                    if f.endswith('.csv') and f != 'late_comers.csv'  # Skip this file
                ]
                print(f"Found CSV files (excluding late_comers.csv): {csv_files}")
                
                if not csv_files:
                    print("No CSV files found in the directory")
                    return {}
                    
                for file in csv_files:
                    # Extract subject name from filename (assuming filename format is subject.csv)
                    subject = os.path.splitext(file)[0].capitalize()
                    
                    # Full path to the CSV file
                    file_path = os.path.join(self.attendance_folder, file)
                    
                    try:
                        # Read CSV file (expecting 8 columns)
                        df = pd.read_csv(
                            file_path, 
                            header=0, 
                            names=["Roll No", "Name", "Attendance", "Late", "Time_of_Entry", "Date", "Time_of_Exit", "Period_Time"]
                        )
                        
                        # Filter data for the current student
                        student_data = df[df["Roll No"].astype(str) == str(roll_no)]
                        
                        if not student_data.empty:
                            # Count total days (unique dates)
                            total_days = len(student_data["Date"].unique())
                            
                            # Count days present
                            days_present = len(student_data[student_data["Attendance"] == "Present"]["Date"].unique())
                            
                            # Calculate percentage
                            if total_days > 0:
                                percentage = (days_present / total_days) * 100
                            else:
                                percentage = 0
                            
                            # Store data
                            attendance_data[subject] = {
                                "Total Days": total_days,
                                "Days Present": days_present,
                                "Days Absent": total_days - days_present,
                                "percentage": percentage
                            }
                        else:
                            print(f"No attendance data found for roll number {roll_no} in subject {subject}")
                            
                    except Exception as e:
                        print(f"Error processing file {file}: {str(e)}")
                        continue  # Skip to next file if there's an error
            
            except Exception as e:
                print(f"ERROR: Cannot list directory contents: {str(e)}")
                return {}
            
        except Exception as e:
            print(f"Error calculating attendance: {str(e)}")
            return {}
        
        return attendance_data
    
    def get_progress_bar_style(self, percentage):
        # Define color based on attendance percentage
        if percentage >= 75:
            color = "#4CAF50"  # Green
        elif percentage >= 60:
            color = "#FFC107"  # Yellow
        else:
            color = "#F44336"  # Red
        
        return f"""
            QProgressBar {{
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border-radius: 5px;
                text-align: center;
                height: 20px;
            }}
            
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 5px;
            }}
        """
    
    def clear_layout(self, layout):
        if layout is None:
            return
        
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            
            if widget is not None:
                widget.deleteLater()
            else:
                child_layout = item.layout()
                if child_layout is not None:
                    self.clear_layout(child_layout)
    
    def show_message(self, title, message):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()


    def go_back_to_home(self):
        """Returns to the main menu."""
        # Stop camera if running
        if hasattr(self, 'is_running') and self.is_running:
            self.stop_camera()
            
        # Try to find the main window through the parent hierarchy
        parent = self.parent()
        while parent is not None:
            if hasattr(parent, 'stacked_widget'):
                # Found the main window with stacked widget
                parent.stacked_widget.setCurrentIndex(0)
                return
            if hasattr(parent, 'go_to_home'):
                parent.go_to_home()
                return
            parent = parent.parent()

class AttendanceMarkerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Back button to return to main menu
        back_layout = QHBoxLayout()
        back_button = QPushButton("Back to Main Menu")
        back_button.setFont(QFont("Arial", 12))
        back_button.setStyleSheet("""
            QPushButton {
                background-color: #2c3e50;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
        """)
        back_button.clicked.connect(self.back_to_home)
        back_layout.addWidget(back_button)
        back_layout.addStretch()
        main_layout.addLayout(back_layout)
        
        # Header
        header_label = QLabel("Mark Attendance")
        header_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        header_label.setStyleSheet("color: white")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header_label)
        
        # Camera feed and controls
        camera_section = QHBoxLayout()
        
        # Camera feed placeholder
        self.camera_feed = QLabel("Camera Feed Will Appear Here")
        self.camera_feed.setFont(QFont("Arial", 14))
        self.camera_feed.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_feed.setStyleSheet("""
            background-color: #2c3e50;
            color: white;
            border-radius: 10px;
            padding: 20px;
        """)
        self.camera_feed.setMinimumSize(500, 300)
        camera_section.addWidget(self.camera_feed)
        
        # Controls
        controls_layout = QVBoxLayout()
        
        # Start button
        start_btn = QPushButton("Start Entry camera")
        start_btn.setFont(QFont("Arial", 14))
        start_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        start_btn.clicked.connect(lambda: self.start_camera("entry"))
        controls_layout.addWidget(start_btn)
        
        # Stop button
        exit_btn = QPushButton("Start Exit camera")
        exit_btn.setFont(QFont("Arial", 14))
        exit_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        exit_btn.clicked.connect(lambda: self.start_camera("exit"))
        controls_layout.addWidget(exit_btn)
        
        # Stop Camera button
        stop_camera_btn = QPushButton("Stop Camera")
        stop_camera_btn.setFont(QFont("Arial", 14))
        stop_camera_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        stop_camera_btn.clicked.connect(self.stop_camera)
        controls_layout.addWidget(stop_camera_btn)
        
        # Reset button
        reset_btn = QPushButton("Reset Session")
        reset_btn.setFont(QFont("Arial", 14))
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        reset_btn.clicked.connect(self.reset_session)
        controls_layout.addWidget(reset_btn)
        
        camera_section.addLayout(controls_layout)
        main_layout.addLayout(camera_section)
        
        # Attendance log
        log_label = QLabel("Attendance Log:")
        log_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        main_layout.addWidget(log_label)
        
        self.log_table = QTableWidget(0, 7)  # 7 columns: roll_no, name, attendance, late, date, time_in, time_out
        self.log_table.setHorizontalHeaderLabels(["Roll No", "Name", "Attendance", "Late", "Date", "Time In", "Time Out"])
        self.log_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                gridline-color: #d3d3d3;
                color: black;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 5px;
                font-weight: bold;
            }
        """)
        self.log_table.horizontalHeader().setStretchLastSection(True)
        self.log_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        main_layout.addWidget(self.log_table)
        
        # Status bar
        self.status_label = QLabel("Ready")
        self.status_label.setFont(QFont("Arial", 12))
        self.status_label.setStyleSheet("color: #2c3e50;")
        main_layout.addWidget(self.status_label)
        
        # Initialize camera variables
        self.camera_thread = None
        self.is_running = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_camera_feed)
        self.capture = None
        self.camera_mode = None
    
    def back_to_home(self):
        """Returns to the main menu."""
        # Stop camera if running
        if hasattr(self, 'is_running') and self.is_running:
            self.stop_camera()
            
        # Try to find the main window through the parent hierarchy
        parent = self.parent()
        while parent is not None:
            if hasattr(parent, 'stacked_widget'):
                # Found the main window with stacked widget
                parent.stacked_widget.setCurrentIndex(0)
                return
            if hasattr(parent, 'go_to_home'):
                parent.go_to_home()
                return
            parent = parent.parent()
        
    def start_camera(self, mode):
        """Starts the webcam and displays the feed in the GUI."""
        # Stop any existing camera feed
        if self.is_running:
            self.stop_camera()
        
        self.camera_mode = mode
        
        # More robust camera initialization
        try:
            # Try multiple camera indices
            camera_indices = [0, 1, 2, -1]
            self.capture = None
            
            for index in camera_indices:
                cap = cv2.VideoCapture(index)
                if cap.isOpened():
                    self.capture = cap
                    break
            
            if self.capture is None:
                # No camera found
                self.status_label.setText("Error: No camera found")
                print("DEBUG: No camera could be opened")
                return
            
            # Explicitly set camera properties
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            # Test if we can actually read a frame
            ret, frame = self.capture.read()
            if not ret:
                print("DEBUG: Cannot read frame from camera")
                self.status_label.setText("Error: Cannot read camera frame")
                self.capture.release()
                return
            
            # Create and start camera thread
            self.camera_thread = CameraThread(mode)
            self.camera_thread.log_update.connect(self.handle_student_detection)
            self.camera_thread.start()

            self.is_running = True
            self.status_label.setText(f"Camera started in {mode} mode")
            self.timer.start(30)  # Update every 30ms (approx. 33 fps)
        
        except Exception as e:
            print(f"DEBUG: Camera initialization error: {e}")
            self.status_label.setText(f"Camera Error: {str(e)}")
            if self.capture:
                self.capture.release()
    
    def update_camera_feed(self):
        """Updates the camera feed in the GUI."""
        if not self.is_running:
            return
            
        ret, frame = self.capture.read()
        if not ret:
            self.status_label.setText("Error: Could not read frame")
            self.stop_camera()
            return
        
        # Process the frame based on the mode
        if self.camera_mode == "entry":
            processed_frame, recognized_students = self.process_for_entry(frame)
        else:  # exit mode
            processed_frame, recognized_students = self.process_for_exit(frame)
        
        # Update log if students were recognized
        if recognized_students:
            for student in recognized_students:
                # Pass the entire student dictionary instead of creating a list
                self.update_log(student)
        
        # Convert the frame to a format Qt can display
        if processed_frame is not None:  # Add this check
            h, w, ch = processed_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(processed_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888).rgbSwapped()
            pixmap = QPixmap.fromImage(qt_image)
            
            # Scale the pixmap to fit the label while maintaining aspect ratio
            pixmap = pixmap.scaled(self.camera_feed.width(), self.camera_feed.height(), 
                                Qt.AspectRatioMode.KeepAspectRatio)
            
            # Display the image
            self.camera_feed.setPixmap(pixmap)
    
    def process_for_entry(self, frame):
        """Process the frame for entry mode and return processed frame and recognized students"""
        try:
            # Get student embeddings
            student_embeddings = get_student_embeddings()
            if not student_embeddings:
                return frame, []  # Return original frame and empty list
                
            # Process frame and recognize faces
            processed_frame, recognized_students = recognize_faces(frame, mode="entry")
            return processed_frame, recognized_students
        except Exception as e:
            print(f"Error in process_for_entry: {e}")
            return frame, []  # Return original frame and empty list on error
    
    def process_for_exit(self, frame):
        """Process the frame for exit mode and return processed frame and recognized students"""
        try:
            # Get student embeddings
            student_embeddings = get_student_embeddings()
            if not student_embeddings:
                return frame, []  # Return original frame and empty list
                
            # Process frame and recognize faces
            processed_frame, recognized_students = recognize_faces(frame, mode="exit")
            return processed_frame, recognized_students
        except Exception as e:
            print(f"Error in process_for_exit: {e}")
            return frame, []  # Return original frame and empty list on error

    
    def stop_camera(self):
        """Properly stops the camera feed and releases resources"""
        if not self.is_running:
            return
            
        # Stop the timer first
        self.timer.stop()
        
        # Stop the camera thread if running
        if self.camera_thread and self.camera_thread.isRunning():
            self.camera_thread.stop()
            self.camera_thread.wait()
            self.camera_thread = None
        
        # Release the camera capture
        if self.capture and self.capture.isOpened():
            try:
                # Set camera properties to minimize power usage
                self.capture.set(cv2.CAP_PROP_AUTOFOCUS, 0)
                self.capture.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
                self.capture.release()
            except Exception as e:
                print(f"Error releasing camera: {e}")
            finally:
                self.capture = None
        
        # Reset the camera feed display
        self.camera_feed.clear()
        self.camera_feed.setText("Camera Feed Will Appear Here")
        self.status_label.setText("Camera stopped")
        self.is_running = False
        
    def reset_session(self):
        # Stop camera if running
        if self.is_running:
            self.stop_camera()
            
        # Reset the attendance session
        try:
            # Assuming this function exists elsewhere in your codebase
            reset_attendance_session()
            self.status_label.setText("Session reset successfully")
            self.log_table.setRowCount(0)  # Clear the table
        except NameError:
            # If the function isn't defined, show a message
            self.status_label.setText("Reset function not implemented yet")
        except Exception as e:
            QMessageBox.critical(self, "Reset Error", f"Error resetting session: {str(e)}")
            
    def update_log(self, student_data=None):
        """Updates the attendance log with properly formatted columns"""
        try:
            if not os.path.exists(ATTENDANCE_DIR):
                print(f"Attendance directory not found: {ATTENDANCE_DIR}")
                return
                
            current_date = datetime.now().strftime("%Y-%m-%d")
            records_to_display = []
            
            if student_data and isinstance(student_data, dict):
                # Create properly ordered record from student data
                record = [
                    student_data.get('roll_no', ''),
                    student_data.get('name', ''),
                    student_data.get('attendance', 'Present'),
                    'Yes' if student_data.get('late', False) else 'No',
                    student_data.get('time_of_entry', ''),
                    current_date,
                    student_data.get('time_of_exit', ''),
                    student_data.get('subject', 'Unknown'),  # Subject in column 7
                    student_data.get('period_time', '')      # Period time in column 8
                ]
                records_to_display.append(record)
                
                # Check for other entries from CSV files
                subject_files = [f for f in os.listdir(ATTENDANCE_DIR) 
                            if f.endswith('.csv') and f != 'late_comers.csv']
                
                for subject_file in subject_files:
                    file_path = os.path.join(ATTENDANCE_DIR, subject_file)
                    try:
                        with open(file_path, 'r') as f:
                            reader = csv.reader(f)
                            headers = next(reader, None)
                            
                            for row in reader:
                                if len(row) >= 7 and row[5] == current_date:
                                    # Ensure proper column order: subject comes from filename, period time from row[7]
                                    subject = os.path.splitext(subject_file)[0]
                                    period_time = row[7] if len(row) > 7 else ''
                                    
                                    # Reconstruct record with correct column order
                                    fixed_record = [
                                        row[0],  # Roll No
                                        row[1],  # Name
                                        row[2],  # Attendance
                                        row[3],  # Late
                                        row[4],  # Time In
                                        row[5],  # Date
                                        row[6] if len(row) > 6 else '',  # Time Out
                                        subject,  # Subject (from filename)
                                        period_time  # Period Time (from row[7])
                                    ]
                                    records_to_display.append(fixed_record)
                    except Exception as e:
                        print(f"Error reading {subject_file}: {str(e)}")
                        continue

            # Sort records by time (newest first)
            records_to_display.sort(key=lambda x: x[4], reverse=True)
            
            # Update the table
            self.log_table.clearContents()
            self.log_table.setRowCount(len(records_to_display))
            
            # Set headers
            headers = ["Roll No", "Name", "Attendance", "Late", "Time In", "Date", "Time Out", "Subject", "Period Time"]
            self.log_table.setColumnCount(len(headers))
            self.log_table.setHorizontalHeaderLabels(headers)
            
            # Populate table with properly ordered columns
            for row_idx, record in enumerate(records_to_display):
                for col_idx in range(len(headers)):
                    value = record[col_idx] if col_idx < len(record) else ""
                    item = QTableWidgetItem(value)
                    
                    # Highlight if it's the newly detected student
                    should_highlight = (row_idx == 0 and student_data is not None)
                    self._format_log_item(item, col_idx, record, should_highlight)
                    self.log_table.setItem(row_idx, col_idx, item)
            
            self.log_table.resizeColumnsToContents()
            
        except Exception as e:
            print(f"Error updating log: {str(e)}")
            traceback.print_exc()


    def _format_log_item(self, item, col_idx, record, highlight=False):
        """Helper method to format log items consistently"""
        item.setFont(QFont("Arial", 10))
        
        # Highlight newly detected students
        if highlight:
            item.setBackground(QColor(173, 216, 230))  # Light blue
        
        # Color code attendance status
        if col_idx == 2:  # Attendance column
            if record[2] == "Present":
                item.setForeground(QColor(0, 128, 0))  # Green
            else:
                item.setForeground(QColor(255, 0, 0))  # Red
        
        # Color code late status
        if col_idx == 3 and record[3] == "Yes":  # Late column
            item.setForeground(QColor(255, 165, 0))  # Orange


    def handle_student_detection(self, student_data):
        """
        Handles newly detected students by:
        1. Updating the attendance records
        2. Refreshing the log display
        3. Highlighting the new entry
        """
        # First update the CSV files through mark_attendance
        current_day = datetime.now().strftime("%A")
        mark_attendance(
            student_data['roll_no'],
            student_data['name'],
            current_day,
            self.camera_mode
        )
        
        # Then refresh the log display
        self.update_log(student_data)
        

class CameraThread(QThread):
    frame_update = pyqtSignal(object)
    log_update = pyqtSignal(dict)
    status_update = pyqtSignal(str)
    
    def __init__(self, mode):
        super().__init__()
        self.mode = mode
        self.running = False
        self.cap = None
        
    def run(self):
        self.running = True
        try:
            # Get student embeddings
            student_embeddings = get_student_embeddings()
            
            if not student_embeddings:
                self.status_update.emit("No student embeddings found")
                return
                
            # Initialize camera with proper settings
            self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Use DirectShow backend
            if not self.cap.isOpened():
                self.status_update.emit("Failed to start camera")
                return
                
            # Set camera properties to reduce power usage
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            # Restore student status if system was restarted
            restore_student_status()
            
            while self.running:
                ret, frame = self.cap.read()
                if not ret:
                    break
                
                # Process frame and recognize faces
                processed_frame, recognized_students = recognize_faces(frame, self.mode)
                
                # Convert frame for display
                rgb_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_frame.shape
                bytes_per_line = ch * w
                qt_img = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                
                # Emit signals
                self.frame_update.emit(qt_img)
                
                # Handle recognized students
                for student in recognized_students:
                    # Add current time and date
                    student['time_of_entry'] = datetime.now().strftime("%H:%M:%S")
                    student['date'] = datetime.now().strftime("%Y-%m-%d")
                    self.log_update.emit(student)
                
                # Small delay to prevent CPU overload
                QThread.msleep(50)
                
        except Exception as e:
            self.status_update.emit(f"Error in camera thread: {str(e)}")
        finally:
            self.cleanup_camera()
                
    def cleanup_camera(self):
        """Properly clean up camera resources"""
        if self.cap and self.cap.isOpened():
            try:
                # Reset camera properties before release
                self.cap.set(cv2.CAP_PROP_SETTINGS, 1)
                self.cap.release()
            except Exception as e:
                print(f"Error cleaning up camera: {e}")
            finally:
                self.cap = None
                
    def stop(self):
        """Safe stop of the thread"""
        self.running = False
        self.cleanup_camera()
        self.wait()
                
    

# Backend components for the attendance system
class AttendanceSystemBackend:
    DB_PATH = r"D:\miniproject\AutomaticAttendanceSystem\attendance1.db"
TIMETABLE_PATH = r"D:\miniproject\AutomaticAttendanceSystem\timetable\timetable.json"
LATE_THRESHOLD_MINUTES = 5
RECOGNITION_THRESHOLD = 0.4  # Adjust for accuracy



# Load timetable from JSON
with open(TIMETABLE_PATH, "r") as f:
    timetable = json.load(f)

# Initialize InsightFace model
face_app = FaceAnalysis(name="buffalo_l", providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
face_app.prepare(ctx_id=0, det_size=(640, 640))

# Track student entry/exit status
student_status = {}

def get_current_subject(day, time_now):
    """Finds all current subjects based on time and day."""
    if day not in timetable:
        return []
        
    current_subjects = []
    for subject_info in timetable[day].get("subjects", []):
        start_time, end_time = subject_info["time"].split("-")
        if start_time <= time_now <= end_time:
            current_subjects.append(subject_info)
    return current_subjects

def is_interval_time(day, time_now):
    """Check if current time falls within any interval period for the day."""
    if day not in timetable:
        return False
        
    for interval in timetable[day].get("intervals", []):
        start, end = interval["time"].split("-")
        if start <= time_now <= end:
            return True
    return False

def get_first_subject_start_time(day):
    """Gets the start time of the first subject of the day."""
    if day in timetable and "subjects" in timetable[day] and timetable[day]["subjects"]:
        return timetable[day]["subjects"][0]["time"].split("-")[0]
    return None

def is_before_late_threshold(subject_info, current_time):
    """Checks if the current time is before the late threshold for a subject."""
    start_time = subject_info["time"].split("-")[0]
    start_dt = datetime.strptime(start_time, "%H:%M")
    current_dt = datetime.strptime(current_time, "%H:%M")
    threshold_dt = start_dt + timedelta(minutes=LATE_THRESHOLD_MINUTES)
    return current_dt <= threshold_dt

def get_completed_subjects(day, time_now):
    """Returns a list of subjects that have already been completed for the day."""
    completed_subjects = []
    if day in timetable and "subjects" in timetable[day]:
        for subject_info in timetable[day]["subjects"]:
            start_time, end_time = subject_info["time"].split("-")
            if time_now > end_time:
                completed_subjects.append(subject_info)
    return completed_subjects

# In the fetch_student_status function, modify how you're checking for dates
def fetch_student_status(roll_no, date):
    """Fetches the attendance status of a student from all subject CSV files for a given date."""
    student_status = {}
    day = datetime.strptime(date, "%Y-%m-%d").strftime("%A")
    
    # Get the subjects list from the timetable dictionary
    subjects_list = timetable.get(day, {}).get("subjects", [])
    
    for subject_info in subjects_list:
        subject = subject_info["subject"]
        subject_file = f"attendance/{subject}.csv"
        
        if os.path.exists(subject_file):
            with open(subject_file, "r") as file:
                reader = csv.reader(file)
                headers = next(reader, None)  # Skip header row
                if not headers:
                    continue
                    
                for row in reader:
                    # Debug print to see what's being read
                    print(f"Reading row for {subject}: {row}")
                    
                    # Skip empty or malformed rows
                    if not row or len(row) < 6:
                        print(f"Skipping malformed row in {subject_file}: {row}")
                        continue
                    
                    # Check if the row matches the student and date - ensuring string comparison
                    if row[0] == str(roll_no) and row[5].strip() == date.strip():
                        student_status[subject] = {
                            "Attendance": row[2],
                            "Late": row[3],
                            "Time_of_Entry": row[4],
                            "Time_of_Exit": row[6] if len(row) > 6 else None,
                            "Period_Time": row[7] if len(row) > 7 else None
                        }
                        print(f"Found attendance record for {subject}: {student_status[subject]}")
    
    return student_status


def mark_attendance(roll_no, name, day, status):
    """
    Marks attendance based on face detection at entry/exit cameras, with special handling for interval times.
    
    Parameters:
    roll_no (str): Student roll number
    name (str): Student name
    day (str): Current day of the week
    status (str): 'entry' or 'exit' depending on which camera detected the face
    """
    time_now = datetime.now().strftime("%H:%M")
    date = datetime.now().strftime("%Y-%m-%d")
    current_subjects = get_current_subject(day, time_now)
    is_interval = is_interval_time(day, time_now)

    # Initialize attendance directory
    os.makedirs("attendance", exist_ok=True)
    
    # Get student's current status from CSV files if they exist
    student_attendance = fetch_student_status(roll_no, date)
    
    # Debug print
    print(f"Current time: {time_now}, Day: {day}")
    print(f"Current subjects: {[s['subject'] for s in current_subjects]}")
    print(f"Student attendance records: {student_attendance}")
    
    # Special handling for interval times
    if is_interval:
        print(f"Interval time detected ({time_now}). Processing with interval rules.")
        
        # For entry during interval - mark present for all future subjects without late penalties
        if status == "entry":
            # First mark absent for all past subjects
            for subject_info in timetable[day]["subjects"]:
                subject = subject_info["subject"]
                subject_end_time = subject_info["time"].split("-")[1]
                
                # If this subject ends before current time, it's a past subject
                if subject_end_time <= time_now:
                    subject_file = f"attendance/{subject}.csv"
                    mark_subject_attendance(
                        subject_file, 
                        roll_no, 
                        name, 
                        "Absent", 
                        "No",  # Late = No for past subjects during interval
                        None, 
                        None, 
                        date,
                        subject_info["time"]
                    )
            
            # Then mark present for all future subjects
            for subject_info in timetable[day]["subjects"]:
                subject = subject_info["subject"]
                subject_start_time = subject_info["time"].split("-")[0]
                
                # If this subject starts after current time, it's a future subject
                if subject_start_time > time_now:
                    subject_file = f"attendance/{subject}.csv"
                    mark_subject_attendance(
                        subject_file, 
                        roll_no, 
                        name, 
                        "Present", 
                        "No",  # Never late during intervals
                        time_now, 
                        None, 
                        date,
                        subject_info["time"]
                    )
            print(f"Interval entry: Marked future subjects as Present and past subjects as Absent for {name} ({roll_no})")
        
        # For exit during interval - mark absent for all future subjects (existing behavior remains same)
        elif status == "exit":
            for subject_info in timetable[day]["subjects"]:
                subject = subject_info["subject"]
                subject_start_time = subject_info["time"].split("-")[0]
                
                # If this subject starts after current time, it's a future subject
                if subject_start_time > time_now:
                    subject_file = f"attendance/{subject}.csv"
                    mark_subject_attendance(
                        subject_file, 
                        roll_no, 
                        name, 
                        "Absent", 
                        "No", 
                        None, 
                        time_now, 
                        date,
                        subject_info["time"]
                    )
            print(f"Interval exit: Marked future subjects as Absent for {name} ({roll_no})")
        
        return
    
    # Case: No class is scheduled at the current time
    if not current_subjects:
        print(f"No class is scheduled at this time ({time_now}). No attendance marked for {name} ({roll_no}).")
        return
    
    # ENTRY DETECTION CASES
    if status == "entry":
        # Get first subject start time for early arrival check
        first_subject_time = get_first_subject_start_time(day)
        first_subject_dt = datetime.strptime(first_subject_time, "%H:%M")
        threshold_dt = first_subject_dt + timedelta(minutes=LATE_THRESHOLD_MINUTES)
        current_dt = datetime.strptime(time_now, "%H:%M")
        
        # Case 2: Early arrival - mark present for all subjects
        if current_dt <= threshold_dt:
            for subject_info in timetable[day]:
                subject = subject_info["subject"]
                subject_file = f"attendance/{subject}.csv"
                mark_subject_attendance(
                    subject_file, 
                    roll_no, 
                    name, 
                    "Present", 
                    "No", 
                    time_now, 
                    None, 
                    date,
                    subject_info["time"]
                )
            print(f"Full-day attendance marked for {name} ({roll_no}).")
        
        # Case 3: Enter between classes
        else:
            # Mark absent for all previous subjects
            for subject_info in timetable[day]["subjects"]:  # Access the "subjects" list directly
                subject = subject_info["subject"]
                subject_time = subject_info["time"]
                subject_end_time = subject_time.split("-")[1]
                    
                # If this subject ends before current time, it's a past subject
                if subject_end_time <= time_now:
                    subject_file = f"attendance/{subject}.csv"
                    mark_subject_attendance(
                        subject_file, 
                        roll_no, 
                        name, 
                        "Absent", 
                        "No", 
                        None, 
                        None, 
                        date,
                        subject_time
                    )
            
            # Handle current class
            for current_subject_info in current_subjects:
                current_subject = current_subject_info["subject"]
                subject_file = f"attendance/{current_subject}.csv"
                
                # Check if the student is late for current class
                is_late = not is_before_late_threshold(current_subject_info, time_now)
                
                if is_late:
                    # Case 3a: Late for current class
                    mark_subject_attendance(
                        subject_file, 
                        roll_no, 
                        name, 
                        "Absent", 
                        "Yes", 
                        time_now, 
                        None, 
                        date,
                        current_subject_info["time"]
                    )
                    
                    # Record late entry
                    late_file = "attendance/late_comers.csv"
                    mark_late_entry(
                        late_file, 
                        roll_no, 
                        name, 
                        time_now, 
                        current_subject
                    )
                    
                    print(f"Late attendance marked for {name} ({roll_no}). Marked as Absent for current class.")
                
                else:
                    # Case 3b: Not late for current class
                    mark_subject_attendance(
                        subject_file, 
                        roll_no, 
                        name, 
                        "Present", 
                        "No", 
                        time_now, 
                        None, 
                        date,
                        current_subject_info["time"]
                    )
                    
                    print(f"Present attendance marked for {name} ({roll_no}) for current class.")
            
            # Mark present for all upcoming classes
            for subject_info in timetable[day]["subjects"]:  # Access the "subjects" list directly
                subject = subject_info["subject"]
                subject_start_time = subject_info["time"].split("-")[0]
                
                # If this subject starts after current time, it's an upcoming subject
                if subject_start_time > time_now:
                    subject_file = f"attendance/{subject}.csv"
                    mark_subject_attendance(
                        subject_file, 
                        roll_no, 
                        name, 
                        "Present", 
                        "No", 
                        time_now, 
                        None, 
                        date,
                        subject_info["time"]
                    )
            
            print(f"Upcoming subjects marked as Present for {name} ({roll_no}).")
    
        # ENTRY DETECTION CASES
    if status == "entry":
        # Get first subject start time for early arrival check
        first_subject_time = get_first_subject_start_time(day)
        first_subject_dt = datetime.strptime(first_subject_time, "%H:%M")
        threshold_dt = first_subject_dt + timedelta(minutes=LATE_THRESHOLD_MINUTES)
        current_dt = datetime.strptime(time_now, "%H:%M")
        
        # Case 2: Early arrival - mark present for all subjects
        if current_dt <= threshold_dt:
            for subject_info in timetable[day]["subjects"]:
                subject = subject_info["subject"]
                subject_file = f"attendance/{subject}.csv"
                mark_subject_attendance(
                    subject_file, 
                    roll_no, 
                    name, 
                    "Present", 
                    "No", 
                    time_now, 
                    None, 
                    date,
                    subject_info["time"]
                )
            print(f"Full-day attendance marked for {name} ({roll_no}).")
        
        # Case 3: Enter between classes
        else:
            # Mark absent for all previous subjects
            for subject_info in timetable[day]["subjects"]:
                subject = subject_info["subject"]
                subject_time = subject_info["time"]
                subject_end_time = subject_time.split("-")[1]
                    
                # If this subject ends before current time, it's a past subject
                if subject_end_time <= time_now:
                    subject_file = f"attendance/{subject}.csv"
                    mark_subject_attendance(
                        subject_file, 
                        roll_no, 
                        name, 
                        "Absent", 
                        "No", 
                        None, 
                        None, 
                        date,
                        subject_time
                    )
            
            # Handle current class
            for current_subject_info in current_subjects:
                current_subject = current_subject_info["subject"]
                subject_file = f"attendance/{current_subject}.csv"
                
                # Check if the student is late for current class
                is_late = not is_before_late_threshold(current_subject_info, time_now)
                
                if is_late:
                    # Case 3a: Late for current class
                    mark_subject_attendance(
                        subject_file, 
                        roll_no, 
                        name, 
                        "Absent", 
                        "Yes", 
                        time_now, 
                        None, 
                        date,
                        current_subject_info["time"]
                    )
                    
                    # Record late entry
                    late_file = "attendance/late_comers.csv"
                    mark_late_entry(
                        late_file, 
                        roll_no, 
                        name, 
                        time_now, 
                        current_subject
                    )
                    
                    print(f"Late attendance marked for {name} ({roll_no}). Marked as Absent for current class.")
                
                else:
                    # Case 3b: Not late for current class
                    mark_subject_attendance(
                        subject_file, 
                        roll_no, 
                        name, 
                        "Present", 
                        "No", 
                        time_now, 
                        None, 
                        date,
                        current_subject_info["time"]
                    )
                    
                    print(f"Present attendance marked for {name} ({roll_no}) for current class.")
            
            # Mark present for all upcoming classes
            for subject_info in timetable[day]["subjects"]:
                subject = subject_info["subject"]
                subject_start_time = subject_info["time"].split("-")[0]
                
                # If this subject starts after current time, it's an upcoming subject
                if subject_start_time > time_now:
                    subject_file = f"attendance/{subject}.csv"
                    mark_subject_attendance(
                        subject_file, 
                        roll_no, 
                        name, 
                        "Present", 
                        "No", 
                        time_now, 
                        None, 
                        date,
                        subject_info["time"]
                    )
            
            print(f"Upcoming subjects marked as Present for {name} ({roll_no}).")
    
        # EXIT DETECTION CASES
    elif status == "exit":
        print(f"Processing exit for {name} ({roll_no}) at {time_now}")
        
        if not current_subjects:
            print(f"No subject currently in session. Exit not processed for {name} ({roll_no}).")
            return
        
        # Case 4: Exit during class
        for current_subject_info in current_subjects:
            current_subject = current_subject_info["subject"]
            subject_file = f"attendance/{current_subject}.csv"
            
            print(f"Checking subject for exit: {current_subject}")
            
            # Check if attendance record exists for the current subject
            attendance_record = None
            if current_subject in student_attendance:
                attendance_record = student_attendance[current_subject]
                print(f"Found attendance record for {current_subject}: {attendance_record}")
            else:
                # If no record found but exit is detected, create a basic record
                print(f"No attendance record found for {current_subject} but exit detected.")
                # For subjects with no entry record, we can't properly update, so continue
                continue
            
            # Process exit based on available record
            if attendance_record:
                # Make sure we have time_of_entry, default to current time if missing
                time_of_entry = attendance_record.get("Time_of_Entry", time_now)
                is_late = attendance_record.get("Late", "No")
                
                end_time = current_subject_info["time"].split("-")[1]
                
                if time_now < end_time:
                    # Case 4a: Exit before end of period
                    print(f"Student exiting before end of class {current_subject} (ends at {end_time})")
                    mark_subject_attendance(
                        subject_file, 
                        roll_no, 
                        name, 
                        "Absent", 
                        is_late, 
                        time_of_entry, 
                        time_now, 
                        date,
                        current_subject_info["time"]
                    )
                    
                    # Mark "Absent" for remaining subjects
                    for subject_info in timetable[day]["subjects"]:
                        subject = subject_info["subject"]
                        subject_start_time = subject_info["time"].split("-")[0]
                        subject_end_time = subject_info["time"].split("-")[1]
                        
                        # If this subject starts after current time or is currently ongoing but not the one we just processed
                        if (subject_start_time > time_now) or (subject_start_time <= time_now and subject_end_time >= time_now and subject != current_subject):
                            subject_file = f"attendance/{subject}.csv"
                            mark_subject_attendance(
                                subject_file, 
                                roll_no, 
                                name, 
                                "Absent", 
                                "No", 
                                None, 
                                time_now, 
                                date,
                                subject_info["time"]
                            )
                    
                    print(f"Exit detected for {name} ({roll_no}). Marked as Absent for current and remaining subjects.")
                
                else:
                    # Case 4b: Exit after end of period
                    print(f"Student exiting after end of class {current_subject} (ended at {end_time})")
                    mark_subject_attendance(
                        subject_file, 
                        roll_no, 
                        name, 
                        "Present", 
                        is_late, 
                        time_of_entry, 
                        time_now, 
                        date,
                        current_subject_info["time"]
                    )
                    
                    # Mark "Absent" for upcoming subjects
                    for subject_info in timetable[day]["subjects"]:
                        subject = subject_info["subject"]
                        subject_start_time = subject_info["time"].split("-")[0]
                        
                        # If this subject starts after current time, it's an upcoming subject
                        if subject_start_time > time_now:
                            subject_file = f"attendance/{subject}.csv"
                            mark_subject_attendance(
                                subject_file, 
                                roll_no, 
                                name, 
                                "Absent", 
                                "No", 
                                None, 
                                time_now, 
                                date,
                                subject_info["time"]
                            )
                    
                    print(f"Exit detected for {name} ({roll_no}) after class end. Present status maintained for current class, marked as Absent for upcoming subjects.")

        # After processing exit for all current subjects, update student status globally
        student_status[roll_no] = "outside"
        print(f"Updated global status for {name} ({roll_no}) to 'outside'")


def delete_attendance_entry(file_path, roll_no, date):
    """
    Ensures there is only one attendance entry per student per period time.
    If multiple entries exist, keeps only the most recent one based on available timestamps.
    """
    if not os.path.exists(file_path):
        return
    
    # Read all rows from the CSV file
    rows = []
    with open(file_path, "r") as file:
        reader = csv.reader(file)
        rows = list(reader)
    
    # Dictionary to store the latest entry for each student and period combination
    latest_entries = {}
    filtered_rows = []
    header_row = None
    
    for i, row in enumerate(rows):
        # Save header row
        if i == 0 or row[0] == "Roll No":
            header_row = row
            continue
        
        # Skip malformed rows
        if len(row) < 8:
            continue
        
        # Create a unique key for each student and period combination
        student_roll = row[0]
        entry_date = row[5]
        period_time = row[7]
        key = f"{student_roll}_{entry_date}_{period_time}"
        
        # Get timestamps from the row
        entry_time = row[4] if row[4] else ""
        exit_time = row[6] if row[6] else ""
        
        # Determine the most recent timestamp
        timestamp = exit_time if exit_time > entry_time else entry_time
        
        # Check if we already have an entry for this key
        if key in latest_entries:
            current_timestamp = latest_entries[key][1]
            # Keep the entry with the most recent timestamp
            if timestamp > current_timestamp:
                latest_entries[key] = (row, timestamp)
        else:
            # First entry for this key
            latest_entries[key] = (row, timestamp)
    
    # Start with the header row
    filtered_rows.append(header_row)
    
    # Add only the latest entry for each student and period combination
    for key, (row, _) in latest_entries.items():
        filtered_rows.append(row)
    
    # Write back filtered rows
    with open(file_path, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(filtered_rows)

def mark_subject_attendance(file_path, roll_no, name, attendance, late, time_of_entry, time_of_exit, date, period_time=None):
    """Marks attendance for a specific subject in its CSV file with extended parameters."""
    file_exists = os.path.exists(file_path)
    
    with open(file_path, "a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            # Write the header if the file is new
            header = ["Roll No", "Name", "Attendance", "Late", "Time_of_Entry", "Date", "Time_of_Exit", "Period_Time"]
            writer.writerow(header)
        
        row = [roll_no, name, attendance, late, time_of_entry, date, time_of_exit, period_time]
        writer.writerow(row)
    
    # Clean up duplicate entries - this will ensure only one entry per student per period
    delete_attendance_entry(file_path, roll_no, date)

def mark_late_entry(file_path, roll_no, name, time_of_entry, subject):
    """Marks a late entry in the late_comers.csv file with simplified structure."""
    file_exists = os.path.exists(file_path)
    date = datetime.now().strftime("%Y-%m-%d")
    
    with open(file_path, "a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            # Write the header if the file is new - simplified structure
            header = ["Roll No", "Name", "Time_of_Entry", "Subject"]
            writer.writerow(header)
        
        row = [roll_no, name, time_of_entry, subject]
        writer.writerow(row)

def reset_attendance_session():
    """Resets the attendance session."""
    global student_status
    student_status.clear()
    print("Attendance session reset.")



def get_student_embeddings():
    """Fetch roll_no, name, and extract face embeddings from the image column."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT roll_no, name, image FROM students")

    students = {}
    for roll_no, name, image_data in cursor.fetchall():
        if image_data:
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is not None:
                faces = face_app.get(img)
                if faces:
                    students[roll_no] = (name, faces[0].normed_embedding)

    conn.close()
    return students

def restore_student_status():
    """Restore student status based on the CSV files when the system restarts."""
    global student_status
    date = datetime.now().strftime("%Y-%m-%d")
    
    # Get all student IDs from the database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT roll_no FROM students")
    students = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    # For each student, check their status in the CSV files
    for roll_no in students:
        student_records = fetch_student_status(roll_no, date)
        
        # Check the latest status
        inside = False
        for subject, record in student_records.items():
            if "_late" not in subject and record["Attendance"] == "Present" and not record["Time_of_Exit"]:
                inside = True
                break
        
        # Update student status
        if inside:
            student_status[roll_no] = "inside"
        else:
            student_status[roll_no] = "outside"
    
    print(f"Restored status for {len(student_status)} students.")

def recognize_faces(frame, mode="entry"):
    """
    Recognizes faces in frame and updates attendance, handling interval times.
    
    Args:
        frame: Input video frame
        mode: "entry" or "exit" camera mode
    
    Returns:
        tuple: (processed_frame, list_of_recognized_students)
    """
    try:
        # Initialize
        faces = face_app.get(frame)
        current_day = datetime.now().strftime("%A")
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H:%M:%S")
        current_time_short = datetime.now().strftime("%H:%M")
        stored_embeddings = get_student_embeddings()
        recognized_students = []
        
        # Get current schedule information
        current_subjects = get_current_subject(current_day, current_time_short)
        is_interval = is_interval_time(current_day, current_time_short)
        subject_name = current_subjects[0]['subject'] if current_subjects else "Unknown"
        subject_time = current_subjects[0]['time'] if current_subjects else ""

        # Process each face
        for face in faces:
            # Face matching
            best_match = (None, None, -1)  # (roll_no, name, similarity)
            face_embedding = np.array(face.normed_embedding)
            
            for roll_no, (name, stored_embedding) in stored_embeddings.items():
                similarity = np.dot(face_embedding, stored_embedding)
                if similarity > best_match[2]:
                    best_match = (roll_no, name, similarity)

            # Recognition threshold check
            if best_match[2] > RECOGNITION_THRESHOLD:
                roll_no, name, similarity = best_match
                
                # Prepare attendance record
                attendance_record = {
                    'roll_no': roll_no,
                    'name': name,
                    'attendance': 'Present',
                    'late': False,  # Updated in mark_attendance()
                    'date': current_date,
                    'time_of_entry': current_time,
                    'time_of_exit': '',
                    'subject': subject_name,
                    'period_time': subject_time,
                    'is_interval': is_interval,
                    'similarity_score': float(similarity)
                }

                # Entry camera logic
                if mode == "entry":
                    if roll_no not in student_status or student_status[roll_no] == "outside":
                        student_status[roll_no] = "inside"
                        mark_attendance(roll_no, name, current_day, "entry")
                        recognized_students.append(attendance_record)
                
                # Exit camera logic
                elif mode == "exit":
                    if roll_no in student_status and student_status[roll_no] == "inside":
                        student_status[roll_no] = "outside"
                        attendance_record['time_of_exit'] = current_time
                        mark_attendance(roll_no, name, current_day, "exit")
                        recognized_students.append(attendance_record)

                # Draw face annotations
                x, y, w, h = face.bbox.astype(int)
                cv2.rectangle(frame, (x, y), (w, h), (0, 255, 0), 2)
                cv2.putText(frame, name, (x, y - 10), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        return frame, recognized_students

    except Exception as e:
        print(f"Face recognition error: {str(e)}")
        traceback.print_exc()
        return frame, []

    
# Entry point
from PyQt6.QtGui import QMovie
from PyQt6.QtCore import Qt, QSize

# ... (other imports remain the same)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Create and show the splash screen
    splash = SplashScreen()
    splash.show()

    # Create the main application window
    main_window = AttendanceSystem()

    # Set a timer to close the splash screen and show the main window
    QTimer.singleShot(3000, lambda: (splash.close(), main_window.show()))  # 3000 ms = 3 seconds

    sys.exit(app.exec())