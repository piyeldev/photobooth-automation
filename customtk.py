import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import cv2
from camera_module import Camera

# Initialize CustomTkinter appearance
ctk.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue"

class CustomTkCameraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CustomTkinter Camera App")
        self.root.geometry("800x600")
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
        # Camera Selection Dropdown
        camera_label = ctk.CTkLabel(self.root, text="Select Camera:")
        camera_label.pack(pady=(10, 0))

        self.camera_menu = ctk.CTkComboBox(
            master=self.root,
            values=[str(cam) for cam in self.available_cameras],
            variable=self.selected_camera,
            command=self.change_camera,
            width=100
        )
        self.camera_menu.pack(pady=(0, 20))

        # Video Display Canvas
        self.canvas = ctk.CTkCanvas(self.root, width=640, height=480)
        self.canvas.pack(pady=(0, 20))

        # Take Picture Button
        self.btn_snapshot = ctk.CTkButton(
            master=self.root,
            text="Take Picture",
            command=self.take_picture
        )
        self.btn_snapshot.pack(pady=(0, 10))

    def change_camera(self, selection):
        try:
            new_camera_index = int(selection)
            self.camera.change_camera(new_camera_index)
        except ValueError:
            messagebox.showerror("Invalid Selection", "Please select a valid camera index.")

    def update_frame(self):
        frame = self.camera.get_frame()
        if frame is not None:
            # Convert the frame to RGB and then to PIL Image
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img = img.resize((640, 480), Image.LANCZOS)
            imgtk = ImageTk.PhotoImage(image=img)

            # Update the canvas image
            self.canvas.create_image(0, 0, anchor=ctk.NW, image=imgtk)
            self.canvas.imgtk = imgtk  # Prevent garbage collection

        # Schedule the next frame update
        self.root.after(10, self.update_frame)

    def take_picture(self):
        if not os.path.exists('photos'):
            os.makedirs('photos')
        filename = f'photos/photo_{len(os.listdir("photos"))}.png'
        success = self.camera.take_picture(filename)
        if success:
            messagebox.showinfo("Picture Taken", f"Saved {filename}")
        else:
            messagebox.showerror("Error", "Failed to take picture.")

    def on_closing(self):
        self.camera.stop()
        self.root.destroy()

if __name__ == "__main__":
    root = ctk.CTk()
    app = CustomTkCameraApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
