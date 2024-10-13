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
        self.logic = APLogic()

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

        heading = ctk.CTkLabel(root, text="Auto Printer", fg_color="transparent", font=("Cantarell", 32, "bold"))
        heading.grid(row=0, column=0, columnspan=2, padx=20, sticky="w")
        self.delete_last_photos_init()
        self.preview_cam()
        self.selected_choice = "PhotoCard"
        self.frame_choose_and_preview()
        self.last_seen_files = set()
        # self.watch_folder("photos/")
        self.update_frame()

    def delete_last_photos_init(self):
        folder = os.path.join(os.getcwd(), "photos/")
        for file_name in os.listdir(folder):
            file_path = os.path.join(folder, file_name)
            # Check if it's a file and delete it
            if os.path.isfile(file_path):
                os.remove(file_path)

    def preview_cam(self):
        # select camera label
        preview_frame = ctk.CTkFrame(
            master=root,
            fg_color="transparent", 
            border_color="black",
            border_width=2
        )
        preview_frame.grid(row=1, column=0, pady=10, padx=10)
        camera_label = ctk.CTkLabel(preview_frame, text="Select Camera: ")
        camera_label.grid(row=0, column=0, padx=10, pady=10)


        self.camera_menu = ctk.CTkComboBox(
            master=preview_frame,
            values=[str(cam) for cam in self.available_cameras],
            variable=self.selected_camera,
            command=self.change_camera,
            width=100
        )
        self.camera_menu.grid(column=1, row=0)

        # camera canvas
        self.canvas =ctk.CTkCanvas(preview_frame, width=640, height=480)
        self.canvas.grid(row=1, column=0, columnspan=2, padx=10)

        # take picture button
        self.btn_snapshot = ctk.CTkButton(
            master=preview_frame,
            text="Take Picture",
            command=self.take_picture
        )
        self.btn_snapshot.grid(row=2, column=0, columnspan=2)

    def frame_choose_and_preview(self):
        self.chooser_frame = ctk.CTkFrame(
            master=root,
            fg_color="transparent"
        )
        self.chooser_frame.grid(row=1, column=1, sticky="n")

        #====== frame label
        frame_label = ctk.CTkLabel(self.chooser_frame, text="Frame", font=("Cantarell", 24, "bold"), fg_color="transparent")
        frame_label.grid(row=0, column=0, sticky="w", pady=10)


        
        # ===== frame_chooser drop down menu
        self.options = ["PhotoCard", "PhotoStrip"]
        dropdown = ctk.CTkOptionMenu(self.chooser_frame, values=self.options, command=self.frame_chooser_handler)
        dropdown.grid(row=1, column=0, sticky="w")

        # frame_preview is not ""
        self.img_lbl = ctk.CTkLabel(self.chooser_frame, text="", fg_color="transparent")
        self.img_lbl.grid(row=2, column=0, pady=10)

        # print button
        self.print_btn = ctk.CTkButton(
            master=self.chooser_frame,
            text="Print",
            command=self.print_img
        )
            
    
    
    def print_img(self):
        print_path = self.print_img_path
        if os.path.isfile(print_path) and not os.path.isfile(self.current_pdf_path) and print_path is not self.last_print_path:
            self.current_pdf_path = utilities.convert_image_to_pdf(print_path)
            utilities.xdg_open(self.current_pdf_path)
        elif os.path.isfile(print_path) and os.path.isfile(self.current_pdf_path) and print_path is not self.last_print_path:
            self.current_pdf_path = utilities.convert_image_to_pdf(print_path)
            utilities.xdg_open(self.current_pdf_path)
        elif os.path.isfile(print_path) and os.path.isfile(self.current_pdf_path) and print_path is self.last_print_path:
            utilities.xdg_open(self.current_pdf_path)
        else:
            messagebox.showerror("Invalid File Path/No File Path", "Check code pls")
        self.last_print_path = print_path
        
    def image_prev(self, path: str):
        test_image = Image.open(path)
        new_test_image_size = tuple(i/3 for i in test_image.size)
        # ===== preview image
        preview_image = ctk.CTkImage(dark_image=test_image, size=new_test_image_size)
        self.img_lbl.configure(image=preview_image)
        self.img_lbl.image = preview_image 

    def frame_chooser_handler(self, choice):
        self.selected_choice = choice
        if choice == "PhotoCard":
            self.image_prev("../assets/frame_un.png")

        elif choice == "PhotoStrip":
            self.image_prev("../assets/photostrip.png")

    def watch_folder(self, selected_folder):
        current_files = set(os.listdir(selected_folder))
        new_files = current_files - self.last_seen_files 
        image_files = [f for f in new_files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

        if image_files:
            # If new image files are found, get the first image's full path
            new_image_path = os.path.join(selected_folder, image_files[0])
            
            if self.selected_choice == "PhotoCard":
                self.overlay_photocard(new_image_path)
        
        self.last_seen_files = current_files

    def overlay_photocard(self, new_image_path):
        overlayed_image, overlayed_img_path = utilities.overlay_image_photocard(new_image_path)
        img = ctk.CTkImage(dark_image=overlayed_image, size=tuple(i/3 for i in overlayed_image.size))
        self.img_lbl.configure(image=img)
        self.img_lbl.image = img

        # set print path for print ready
        self.print_img_path = overlayed_img_path

        # display print button
        self.print_btn.grid(row=3, column=0, columnspan=2)
    def change_camera(self, selection):
        try:
            new_camera_index = int(selection)
            self.camera.change_camera(new_camera_index)
        except ValueError:
            messagebox.showerror("Invalid Selection", "Please select a valid camera index.")

    def update_frame(self):
        frame = self.camera.get_frame()
        if frame is not None:
            frame = cv2.flip(frame, 1)
            # Convert the frame to RGB and then to PIL Image
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img = img.resize((640, 480), Image.LANCZOS)
            imgtk = ImageTk.PhotoImage(image=img)

            # Update the canvas image
            self.canvas.create_image(0, 0, anchor=ctk.NW, image=imgtk)
            self.canvas.imgtk = imgtk  # Prevent garbage collection

        # Schedule the next frame update
        root.after(10, self.update_frame)

    def take_picture(self):
        if not os.path.exists('photos'):
            os.makedirs('photos')
        filename = f'photos/photo_{len(os.listdir("photos"))}.png'
        success = self.camera.take_picture(filename)
        if success:
            self.watch_folder("photos/")
            # messagebox.showinfo("Picture Taken", f"Saved {filename}")
        else:
            messagebox.showerror("Error", "Failed to take picture.")


    def on_closing(self):
        self.camera.stop()
        root.destroy()

if __name__ == "__main__":
    root = ctk.CTk()
    root.title("Auto Printer")

    ui = APUI(root)
    root.protocol("WM_DELETE_WINDOW", ui.on_closing)
    root.mainloop()