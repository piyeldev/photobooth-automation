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
        
        heading = ctk.CTkLabel(root, text="Auto Printer", fg_color="transparent", font=("Cantarell", 32, "bold"))
        heading.grid(row=0, column=0, columnspan=2, padx=20, sticky="w")
        self.delete_last_photos_init()
        self.preview_cam()
        self.selected_choice = "PhotoCard"
        self.photostrip_imgs_paths = []
        self.photostrip_image_widgets = []
        self.photostrip_imgs_paths_count = len(self.photostrip_imgs_paths)

        self.frame_choose_and_preview()
        self.last_seen_files = set()
        self.photostrip_buttons()
        self.update_frame()

    def delete_last_photos_init(self):
        folder = os.path.join(os.getcwd(), "photos/")
        if os.path.exists(folder):
            for file_name in os.listdir(folder):
                file_path = os.path.join(folder, file_name)
                if os.path.isfile(file_path):
                    os.remove(file_path)

    def preview_cam(self):
        preview_frame = ctk.CTkFrame(
            master=self.root,
            fg_color="transparent", 
            border_color="black",
            border_width=2
        )
        preview_frame.grid(row=1, column=0, pady=10, padx=10, sticky="n")

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

        self.canvas = ctk.CTkCanvas(preview_frame, width=640, height=480)
        self.canvas.grid(row=1, column=0, columnspan=2, padx=10)

        self.btn_snapshot = ctk.CTkButton(
            master=preview_frame,
            text="Take Picture",
            command=self.take_picture
        )
        self.btn_snapshot.grid(row=2, column=0, columnspan=2)

    def frame_choose_and_preview(self):
        self.chooser_frame = ctk.CTkFrame(
            master=self.root,
            fg_color="transparent"
        )
        self.chooser_frame.grid(row=1, column=1, sticky="n")

        frame_label = ctk.CTkLabel(self.chooser_frame, text="Frame", font=("Cantarell", 24, "bold"), fg_color="transparent")
        frame_label.grid(row=0, column=0, sticky="w", pady=10)

        self.options = ["PhotoCard", "PhotoStrip"]
        dropdown = ctk.CTkOptionMenu(self.chooser_frame, values=self.options, command=self.frame_chooser_handler)
        dropdown.grid(row=1, column=0, sticky="w")

        self.img_lbl = ctk.CTkLabel(self.chooser_frame, text="", fg_color="transparent")
        self.img_lbl.grid(row=2, column=0, pady=10)

        self.print_btn = ctk.CTkButton(
            master=self.chooser_frame,
            text="Print",
            command=self.print_img
        )
        
        self.chooser_frame.grid_rowconfigure(2, weight=1)
        self.chooser_frame.grid_columnconfigure(1, weight=1)
        self.photostrip_images_preview_frame = ctk.CTkFrame(
            master=self.chooser_frame,
            fg_color="transparent"
        )

    def print_img(self):
        print_path = self.print_img_path
        if os.path.isfile(print_path):
            if not os.path.isfile(self.current_pdf_path) or print_path != self.last_print_path:
                self.current_pdf_path = utilities.convert_image_to_pdf(print_path)
                
            utilities.xdg_open(self.current_pdf_path)
        else:
            messagebox.showerror("Invalid File Path/No File Path", "Check code pls")
        self.last_print_path = print_path
        
    def image_prev(self, path: str):
        try:
            test_image = Image.open(path)
            new_test_image_size = tuple(int(i/3) for i in test_image.size)
            preview_image = ctk.CTkImage(dark_image=test_image, size=new_test_image_size)
            self.img_lbl.configure(image=preview_image)
            self.img_lbl.image = preview_image 
        except Exception as e:
            messagebox.showerror("Image Preview Error", f"Failed to load image: {e}")

    def frame_chooser_handler(self, choice):
        self.selected_choice = choice
        if choice == "PhotoCard":
            self.image_prev("../assets/frame_un.png")
            self.photostrip_images_preview_frame.grid_forget()
        elif choice == "PhotoStrip":
            self.image_prev("../assets/photostrip.png")
            self.photostrip_images_preview_frame.grid(row=2, column=1, sticky="n")
            self.photostrip_buttons_frame.grid(row=3, column=0, sticky="n")

    def watch_folder(self, selected_folder):
        current_files = set(os.listdir(selected_folder))
        new_files = current_files - self.last_seen_files 
        image_files = [f for f in new_files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

        if image_files:
            new_image_path = os.path.join(selected_folder, image_files[0])
            
            if self.selected_choice == "PhotoCard":
                self.overlay_photocard(new_image_path)
            elif self.selected_choice == "PhotoStrip":
                self.photostrip_process(new_image_path)
        self.last_seen_files = current_files

    def overlay_photocard(self, new_image_path):
        overlayed_img_path = utilities.overlay_image_photocard(new_image_path)
        self.image_prev(overlayed_img_path)
        self.print_img_path = overlayed_img_path
        self.print_btn.grid(row=3, column=0, columnspan=2)

    def preview_images_for_photostrip(self):
        for widget in self.photostrip_images_preview_frame.winfo_children():
            widget.destroy()
        self.photostrip_image_widgets.clear()

        for index, image in enumerate(self.photostrip_imgs_paths):
            try:
                pil_img = Image.open(image)
                img = ctk.CTkImage(dark_image=pil_img, size=tuple(int(e/4) for e in pil_img.size))

                img_label = ctk.CTkLabel(
                    self.photostrip_images_preview_frame,
                    text="",
                    image=img
                )
                img_label.grid(row=index, column=0, pady=25, sticky="n")
                self.photostrip_image_widgets.append(img_label)
            except Exception as e:
                print(f"Failed to load image {image}: {e}")

    def photostrip_process(self, img_path):
        if self.photostrip_imgs_paths_count < 3:
            self.photostrip_imgs_paths.append(img_path)
            self.photostrip_imgs_paths_count = len(self.photostrip_imgs_paths)
            self.preview_images_for_photostrip()
            print(f"Added image. Current count: {self.photostrip_imgs_paths_count}")
            self.update_buttons_visibility()
        else:
            messagebox.showinfo("Photo Count Error", "Please clear the images before proceeding.")

    def process_photostrip(self):
        photostrip = utilities.photostrip_processor(self.photostrip_imgs_paths)
        self.image_prev(photostrip)
        self.print_img_path = photostrip
        self.print_img()
        
    def photostrip_buttons(self):
        # Changed master to chooser_frame to avoid being a child of a potentially hidden frame
        self.photostrip_buttons_frame = ctk.CTkFrame(
            master=self.chooser_frame,  # Changed from photostrip_images_preview_frame
            fg_color="transparent"
        )
        self.photostrip_buttons_frame.grid(row=3, column=0, sticky="n")

        # Clear Last Image Button
        self.clear_last_img_btn = ctk.CTkButton(
            master=self.photostrip_buttons_frame,
            text="Clear Last Image",
            command=self.remove_last_image
        )
        self.clear_last_img_btn.grid(row=0, column=0, padx=10, sticky="nw", pady=10)
        self.clear_last_img_btn.grid_remove()  # Hide initially

        # Clear All Images Button
        self.clear_all_img_btn = ctk.CTkButton(
            master=self.photostrip_buttons_frame,
            text="Clear All Images",
            command=self.clear_all_images
        )
        self.clear_all_img_btn.grid(row=0, column=1, padx=10, sticky="nw", pady=10)
        self.clear_all_img_btn.grid_remove()  # Hide initially

        # Process Photostrip Button
        self.process_btn_photostrip = ctk.CTkButton(
            master=self.photostrip_buttons_frame,
            text="Process Photostrip",
            command=self.process_photostrip
        )
        self.process_btn_photostrip.grid(row=1, column=0, columnspan=2, pady=10)
        self.process_btn_photostrip.grid_remove()  # Hide initially

    def clear_all_images(self):
        self.photostrip_imgs_paths.clear()
        self.photostrip_imgs_paths_count = 0
        self.preview_images_for_photostrip()
        self.update_buttons_visibility()

    def remove_last_image(self):
        if self.photostrip_imgs_paths_count > 0:
            self.photostrip_imgs_paths.pop()
            self.photostrip_imgs_paths_count = len(self.photostrip_imgs_paths)
            if self.photostrip_image_widgets:
                last_widget = self.photostrip_image_widgets.pop()
                last_widget.destroy()
            self.update_buttons_visibility()
        else:
            print("No images to remove.")

    def update_buttons_visibility(self):
        # Debugging statements
        print(f"Updating button visibility. Image count: {self.photostrip_imgs_paths_count}")

        # Show or hide Clear Last Image Button
        if self.photostrip_imgs_paths_count >= 1:
            self.clear_last_img_btn.grid()
        else:
            self.clear_last_img_btn.grid_remove()

        # Show or hide Clear All Images Button
        if self.photostrip_imgs_paths_count >= 2:
            self.clear_all_img_btn.grid()
        else:
            self.clear_all_img_btn.grid_remove()

        # Show or hide Process Photostrip Button
        if self.photostrip_imgs_paths_count == 3:
            self.process_btn_photostrip.grid()
        else:
            self.process_btn_photostrip.grid_remove()

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
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img = img.resize((640, 480), Image.LANCZOS)
            imgtk = ImageTk.PhotoImage(image=img)

            self.canvas.create_image(0, 0, anchor=ctk.NW, image=imgtk)
            self.canvas.imgtk = imgtk  # Prevent garbage collection

        self.root.after(10, self.update_frame)

    def take_picture(self):
        if not os.path.exists('photos'):
            os.makedirs('photos')
        filename = f'photos/photo_{len(os.listdir("photos"))}.png'
        success = self.camera.take_picture(filename)
        if success:
            self.watch_folder("photos/")
        else:
            messagebox.showerror("Error", "Failed to take picture.")

    def on_closing(self):
        self.camera.stop()
        self.root.destroy()
    
    def on_resize(self, event):
        new_width = event.width

if __name__ == "__main__":
    root = ctk.CTk()
    root.title("Auto Printer")
    root.geometry("1024x768")

    ui = APUI(root)
    root.protocol("WM_DELETE_WINDOW", ui.on_closing)
    root.mainloop()
