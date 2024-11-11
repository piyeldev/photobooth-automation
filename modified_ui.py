
import customtkinter as ctk
from logic import APLogic
from PIL import Image, ImageTk
from camera_module import Camera
from tkinter import messagebox
import cv2
import os
import utilities
import shutil

class APUI:
    def __init__(self, root):
        self.root = root
        self.available_cameras = Camera.list_cameras()
        if not self.available_cameras:
            messagebox.showerror("Error", "No cameras found.")
            root.destroy()
            return
        
        self.selected_camera = ctk.StringVar()
        self.selected_camera.set(str(self.available_cameras[0]))
        self.camera = Camera(int(self.selected_camera.get()))
        self.camera.start()

        self.print_img_path = ""
        self.last_print_path = ""
        self.current_pdf_path = ""
        
        # Initialize GUI components
        heading = ctk.CTkLabel(root, text="Auto Printer", fg_color="transparent", font=("Cantarell", 32, "bold"))
        heading.grid(row=0, column=0, columnspan=2, padx=20, sticky="w")
        self.delete_last_photos_init()
        self.preview_cam()
        
        # Custom filename entry field below the Take Picture button
        self.custom_filename_var = ctk.StringVar()
        self.custom_filename_entry = ctk.CTkEntry(root, textvariable=self.custom_filename_var, placeholder_text="Enter custom filename")
        self.custom_filename_entry.grid(row=3, column=0, padx=10, pady=(5, 20))  # Position it below the Take Picture button

        self.selected_choice = "PhotoCard"
        self.photostrip_imgs_paths = []
        self.photostrip_image_widgets = []
        self.photostrip_imgs_paths_count = len(self.photostrip_imgs_paths)

        self.frame_choose_and_preview()
        self.last_seen_files = set()
        self.photostrip_buttons()
        self.update_frame()

    # Modify the 'print_img' method to use the custom filename when saving the PDF
    def print_img(self):
        print_path = self.print_img_path
        if os.path.isfile(print_path):
            # Use the custom filename if provided; otherwise, use a default name
            custom_filename = self.custom_filename_var.get().strip()
            if not custom_filename:
                custom_filename = "output"  # Default name if no custom name is entered
            custom_filename = custom_filename + ".pdf"  # Append .pdf extension
            
            if not os.path.isfile(self.current_pdf_path) or print_path != self.last_print_path:
                self.current_pdf_path = utilities.convert_image_to_pdf(print_path, custom_filename)
                
            utilities.xdg_open(self.current_pdf_path)
        else:
            messagebox.showerror("Invalid File Path/No File Path", "Check code pls")
        self.last_print_path = print_path

    # Existing preview and other functions here...

    # Modify the 'take_picture' method if needed

if __name__ == "__main__":
    root = ctk.CTk()
    root.title("Auto Printer")
    root.geometry("1024x768")

    ui = APUI(root)
    root.protocol("WM_DELETE_WINDOW", ui.on_closing)
    root.mainloop()
