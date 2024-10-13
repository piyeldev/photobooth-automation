import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import cv2
from camera_module import Camera

# Initialize CustomTkinter appearance
ctk.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue"

class CustomPrinter:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Printer")
        self.root.geometry("1024x668")
        self.root.resizable(False, False)

        # Initialize Camera
        self.available_cameras = Camera.list_cameras()
        if not self.available_cameras:
            messagebox.showerror("Error", "No cameras found.")
            self.root.destroy()
            return

        self.selected_camera = ctk.StringVar()
        self.selected_camera.set(str(self.available_cameras[0]))
        self.camera = Camera(int(self.selected_camera.get()))
        self.camera.start()

        # Create UI Components
        self.create_widgets()

        # Start the frame update loop
        self.update_frame()

    def create_widgets(self):
        # ========= heading 
        heading = ctk.CTkLabel(self.root, text="AutoPrinter", fg_color="transparent", font=("Cantarell", 32, "bold"), pady=10, pady=20, padx=10)
        heading.grid(row=0, column=3, sticky="s")
