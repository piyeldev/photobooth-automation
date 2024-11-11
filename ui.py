import customtkinter as ctk
from logic import APLogic
from PIL import Image, ImageTk
from camera_module import Camera
from tkinter import messagebox
import cv2
import os
import utilities
import gdrive
import qrcode
import threading

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

        self.upload_choice = ctk.StringVar(master=self.root, value="yes")
        self.upload_choice_state_printing = ""

        self.frame_choose_and_preview()
        self.frame_choose_to_upload_to_gdrive()
        self.last_seen_files = set()
        self.photostrip_buttons()
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

        # camera canvas
        self.canvas =ctk.CTkCanvas(preview_frame, width=640, height=480)
        self.canvas.grid(row=1, column=0, columnspan=2, padx=10)

        # take picture button
        self.btn_snapshot = ctk.CTkButton(
            master=preview_frame,
            text="Take Picture",
            command=self.threaded_take_picture
        )
        self.btn_snapshot.grid(row=2, column=0, columnspan=2)


    def checkbox_event(self):
        print(f'state: {self.upload_choice.get()}')


    def frame_choose_to_upload_to_gdrive(self):
        self.upload_choice_frame = ctk.CTkFrame(
            master=self.chooser_frame,
            fg_color="transparent"
        )

        self.checkbox = ctk.CTkCheckBox(
            master=self.upload_choice_frame,
            text="Include Soft Copy",
            command=self.checkbox_event,
            variable=self.upload_choice,
            onvalue="yes",
            offvalue="no"
        )
        
        self.label_of_field = ctk.CTkLabel(
            master=self.upload_choice_frame,
            text="Name: "
        )
        self.name_field = ctk.CTkTextbox(
            master=self.upload_choice_frame,
            height=30,
            activate_scrollbars=False,
        )
        self.name_field.bind("<Return>", self.disable_newline)
        self.upload_progressbar = ctk.CTkProgressBar(
            master=self.upload_choice_frame,
            width=200,
        )

        self.status_message = ctk.CTkLabel(
            master=self.upload_choice_frame
        )
        # self.upload_choice_frame.grid(row=2, column=0, pady=10)
        self.checkbox.grid(row=0, column=0)
        self.name_field.grid(row=1, column=1)
        self.label_of_field.grid(row=1, column=0)

    def disable_newline(self, event):
        return "break"

    def frame_choose_and_preview(self):
        self.chooser_frame = ctk.CTkFrame(
            master=self.root,
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

        # loading bar
        self.loading_bar = ctk.CTkProgressBar(self.root, mode="indeterminate", width=200)
        # frame_preview is not ""
        self.img_lbl = ctk.CTkLabel(self.chooser_frame, text="", fg_color="transparent")
        self.img_lbl.grid(row=2, column=0, pady=10)

        # print button photocard
        self.print_btn = ctk.CTkButton(
            master=self.chooser_frame,
            text="Prepare for Printing",
            command=self.threaded_print_img
        )
        
        self.chooser_frame.grid_rowconfigure(2, weight=1)
        self.chooser_frame.grid_columnconfigure(1, weight=1)
        self.photostrip_images_preview_frame = ctk.CTkFrame(
            master=self.chooser_frame,
            fg_color="transparent"
        )

    def threaded_print_img(self):
        self.print_btn.configure(state="disabled")
        threading.Thread(target=self.print_img, args=(), daemon=True).start()

    def print_img(self):
        print_path = self.print_img_path

        name_val = self.name_field.get("0.0", "end").strip() if self.name_field.get("0.0", "end").strip() and not self.name_field.get("0.0", "end").strip() == "" else self.photostrip_name_field.get("0.0", "end").strip()
        print("empty" if name_val == "" else name_val)
        print_path_qr = print_path
        if os.path.isfile(print_path):
            if not os.path.isfile(self.current_pdf_path) or print_path != self.last_print_path:
                if self.upload_choice.get() == "yes":
                    print_path_qr = self.upload_and_overlay_qr(print_path)
                    self.upload_choice_state_printing = "yes"
                self.current_pdf_path = utilities.convert_image_to_pdf(print_path_qr, name_val)
            elif os.path.isfile(self.current_pdf_path) and print_path == self.last_print_path and self.upload_choice.get() != self.upload_choice_state_printing:
                if (self.upload_choice.get() == "yes"):
                    potential_filename = f"out/framed/withQRCodes/wqr-{os.path.splitext(os.path.basename(print_path))[0]}.pdf"
                    # check if a the print_path with the prefix wqr- exists in the directory out/framed/withQRCodes
                    if (os.path.isfile(potential_filename)):
                        utilities.xdg_open(potential_filename)
                    else:
                        print_path_qr = self.upload_and_overlay_qr(print_path)
                        self.current_pdf_path = utilities.convert_image_to_pdf(print_path_qr, name_val)
                    self.upload_choice_state_printing = "yes"
                else:
                    potential_filename = f"out/framed/withQRCodes/{os.path.splitext(os.path.basename(print_path))[0]}.pdf"
                    
                    if (os.path.isfile(potential_filename)):
                        utilities.xdg_open(potential_filename)
                    else:
                        self.current_pdf_path = utilities.convert_image_to_pdf(print_path_qr, name_val)
                    self.upload_choice_state_printing = "no"

                    
            utilities.xdg_open(self.current_pdf_path)
        else:
            messagebox.showerror("Invalid File Path/No File Path", "Check code pls")
        self.last_print_path = print_path

        self.root.after(0, lambda: self.print_btn.configure(state='normal'))

    # TODO: Upload to Gdrive => Make qr based on uploaded img link
    def upload_and_overlay_qr(self, img_path):
        self.upload_progressbar.grid(row=0, column=1, padx=20)
        self.status_message.grid(row=0, column=2, padx=10)
        self.upload_progressbar.set(0.1)

        self.status_message.configure(text="Uploading to Google Drive")
        gdrive_link = gdrive.upload_photo(img_path)
        self.upload_progressbar.set(0.3)

        self.status_message.configure(text="Finished uploading to Google Drive")
        img_name = os.path.splitext(os.path.basename(img_path))[0]
        qr_code = qrcode.make(gdrive_link)
        qr_code_path = f"out/qrcodes/{img_name}.png"
        qr_code.save(qr_code_path)

        self.upload_progressbar.set(0.6)
        self.status_message.configure(text="QR Code generating")
        img = Image.open(img_path)
        qr_code_img = Image.open(qr_code_path)

        qr_size = (212, 212)
        if (self.selected_choice == "PhotoCard"):
            position = (1250,100)
            qr_code_img = qr_code_img.resize(qr_size)
            self.upload_progressbar.set(0.9)
            self.status_message.configure(text="Attaching QR Code")
            img.paste(qr_code_img, position, qr_code_img if qr_code_img.mode == 'RGBA' else None)
            
            image_path = f"out/framed/withQRCodes/wqr-{img_name}.png"
            img.save(image_path)
            self.upload_progressbar.set(1)
            self.status_message.configure(text="Finished configuring!")
            self.upload_progressbar.grid_forget()
            self.status_message.grid_forget()
            return image_path

        else:
            # selected_choice=PhotoStrip
            self.upload_progressbar.grid_forget()
            self.status_message.grid_forget()
            position = (340,1560)
            qr_code_img = qr_code_img.resize(qr_size)
            img.paste(qr_code_img, position, qr_code_img if qr_code_img.mode == 'RGBA' else None)

            image_path = f"out/framed/withQRCodes/wqr-{img_name}.png"
            img.save(image_path)

            
            return image_path



        


    def image_prev(self, path: str):
        try:
            test_image = Image.open(path)
            new_test_image_size = tuple(i/3 for i in test_image.size)
            # ===== preview image
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
            self.photostrip_buttons_frame.grid_forget()
            self.photostrip_name_field.delete("0.0", "end")


        elif choice == "PhotoStrip":
            self.image_prev("../assets/photostrip.png")
            self.photostrip_images_preview_frame.grid(row=2, column=1, sticky="ne", padx=10)
            self.photostrip_buttons_frame.grid(row=2, column=2, sticky="n")

            self.name_field.delete("0.0", "end")
            


    def watch_folder(self, selected_folder):
        current_files = set(os.listdir(selected_folder))
        new_files = current_files - self.last_seen_files 
        image_files = [f for f in new_files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

        if image_files:
            # If new image filses are found, get the first image's full path
            new_image_path = os.path.join(selected_folder, image_files[0])
            
            if self.selected_choice == "PhotoCard":
                self.overlay_photocard(new_image_path)
            elif self.selected_choice == "PhotoStrip":
                self.photostrip_process(new_image_path)
        self.last_seen_files = current_files

    def overlay_photocard(self, new_image_path):
        overlayed_img_path = utilities.overlay_image_photocard(new_image_path)
        self.image_prev(overlayed_img_path)

        # set print path for print ready
        self.print_img_path = overlayed_img_path

        # display print button
        self.print_btn.grid(row=3, column=0, columnspan=2)
        self.upload_choice_frame.grid(row=4, column=0, columnspan=2, pady=10, sticky="sw")

    def preview_images_for_photostrip(self):
        # Clear existing widgets from the frame before previewing new images
        for widget in self.photostrip_images_preview_frame.winfo_children():
            widget.destroy()  # Remove any existing image widgets

        self.photostrip_image_widgets.clear()  # Clear the widget list

        for index, image in enumerate(self.photostrip_imgs_paths):
            pil_img = Image.open(image)
            img = ctk.CTkImage(dark_image=pil_img, size=tuple(e/4 for e in pil_img.size))

            img_label = ctk.CTkLabel(
                self.photostrip_images_preview_frame,
                text="",
                image=img
            )
            img_label.grid(row=index, column=0, pady=25, sticky="n")
            self.photostrip_image_widgets.append(img_label)


        
    def photostrip_process(self, img_path):
        if self.photostrip_imgs_paths_count < 3:
            self.photostrip_imgs_paths.append(img_path)
            self.photostrip_imgs_paths_count = len(self.photostrip_imgs_paths)
            self.preview_images_for_photostrip()
            print(f"Added image. Current count: {self.photostrip_imgs_paths_count}")

            self.update_buttons_visibility()  # Update button visibility
        else:
            messagebox.showinfo("Photo Count Error", "Please clear the images before proceeding.")

        
    def threaded_process_photostrip(self):
        self.process_btn_photostrip.configure(state="disabled")
        self.photostrip_progress_bar.grid(row=4, column=0, pady=10)
        threading.Thread(target=self.process_photostrip, args=(), daemon=True).start()

    def process_photostrip(self):
        self.photostrip_progress_bar.set(0.1)
        photostrip = utilities.photostrip_processor(self.photostrip_imgs_paths)
        self.photostrip_progress_bar.set(0.4)
        self.image_prev(photostrip)
        self.photostrip_progress_bar.set(0.6)
        self.print_img_path = photostrip
        self.photostrip_progress_bar.set(0.8)
        self.print_img()
        self.photostrip_progress_bar.set(1)
        self.photostrip_progress_bar.grid_forget()

        self.root.after(0, lambda: self.process_btn_photostrip.configure(state="normal"))
        
    def photostrip_buttons(self):
        print("yes it is")
        self.photostrip_buttons_frame = ctk.CTkFrame(
            master=self.chooser_frame,
            fg_color="transparent"
        )
        self.clear_last_img_btn = ctk.CTkButton(
            master=self.photostrip_buttons_frame,
            text="Clear Last Image",
            command=self.remove_last_image

        )
        self.clear_all_img_btn = ctk.CTkButton(
            master=self.photostrip_buttons_frame,
            text="Clear All Images",
            command=self.clear_all_images
        )
        self.process_btn_photostrip = ctk.CTkButton(
            master=self.photostrip_buttons_frame,
            text="Process Photostrip",
            command=self.threaded_process_photostrip
        )

        self.photostrip_progress_bar = ctk.CTkProgressBar(
            master=self.photostrip_buttons_frame,
            width=100
        )

        self.photostrip_checkbox = ctk.CTkCheckBox(
            master=self.photostrip_buttons_frame,
            text="Include Soft Copy",
            command=self.checkbox_event,
            variable=self.upload_choice,
            onvalue="yes",
            offvalue="no"
        )

        self.photostrip_name_field = ctk.CTkTextbox(
            master=self.photostrip_buttons_frame,
            height=30,
            activate_scrollbars=False
        )
        self.photostrip_name_field.bind("<Return>", self.disable_newline)
        

         # Initially hide buttons
        self.clear_last_img_btn.grid_remove()
        self.clear_all_img_btn.grid_remove()
        self.process_btn_photostrip.grid_remove()

    def clear_all_images(self):
        self.photostrip_imgs_paths.clear()
        self.photostrip_imgs_paths_count = 0
        self.preview_images_for_photostrip()
        self.update_buttons_visibility()
    def child_widgets_in_specific_row_of(self, frame: ctk.CTkFrame):
        widgets_in_row = []
        # Iterate over all child widgets of the frame
        for widget in frame.winfo_children():
            # Check if the widget is managed by the grid system
            if widget.winfo_manager() == 'grid':
                grid_info = widget.grid_info()  # Get the widget's grid info
                if grid_info['row'] == 0:  # If the widget is in the specified row
                    widgets_in_row.append(widget)
        return widgets_in_row

    def remove_last_image(self):
        if self.photostrip_imgs_paths_count > 0:
            first_count_of_widgets = self.photostrip_imgs_paths_count
            print(f"Initial count of images: {first_count_of_widgets}")

            # Remove the last image path
            self.photostrip_imgs_paths.pop()
            self.photostrip_imgs_paths_count = len(self.photostrip_imgs_paths)
            print(f"Updated count of images after removal: {self.photostrip_imgs_paths_count}")

            # Check if there are widgets to destroy
            if self.photostrip_image_widgets:
                # Destroy the last widget
                last_widget = self.photostrip_image_widgets.pop()  # Get and remove the last widget from the list
                last_widget.destroy()  # Destroy the last widget
                print(f"Destroyed widget: {last_widget}")

            # Update the visibility of buttons based on remaining images
            self.update_buttons_visibility()

        else:
            print("No images to remove.")
    def update_buttons_visibility(self):
        print(f"Updating button visibility. Image count: {self.photostrip_imgs_paths_count}")
        # Clear Last Image Button
        if self.photostrip_imgs_paths_count >= 1:
            print("yes 1 button")
            self.clear_last_img_btn.grid(row=0, column=0, padx=10, pady=10)
        else:
            self.clear_last_img_btn.grid_forget()

        # Clear All Images Button
        if self.photostrip_imgs_paths_count >= 2:
            print("yes 2 buttons")
            self.clear_all_img_btn.grid(row=1, column=0, padx=10, pady=10)
        else:
            self.clear_all_img_btn.grid_forget()

        if self.photostrip_imgs_paths_count == 3:
            print("yes third button")
          
            self.process_btn_photostrip.grid(row=2, column=0, columnspan=2)
            self.photostrip_checkbox.grid(row=3, column=0, pady=10)
            self.photostrip_name_field.grid(row=5, column=0, pady=10)
        else:
            self.process_btn_photostrip.grid_forget()

        
        
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
        self.root.after(10, self.update_frame)

    def threaded_take_picture(self):
        self.btn_snapshot.configure(state="disabled")
        threading.Thread(target=self.take_picture, args=(), daemon=True).start()

    def take_picture(self):
        self.loading_bar.grid(row=3, column=0, padx=10)
        self.loading_bar.start()
        if not os.path.exists('photos'):
            os.makedirs('photos')
        filename = f'photos/photo_{len(os.listdir("photos"))}.png'
        success = self.camera.take_picture(filename)
        if success:
            self.watch_folder("photos/")
        else:
            messagebox.showerror("Error", "Failed to take picture.")
        
        self.loading_bar.stop()
        self.loading_bar.grid_forget()
        self.root.after(0, lambda: self.btn_snapshot.configure(state='normal'))
        self.checkbox.select()
        self.upload_choice_state_printing = "no"


    def on_closing(self):
        self.camera.stop()
        root.destroy()
    
    def on_resize(self, event):
        new_width = event.width

if __name__ == "__main__":
    root = ctk.CTk()
    root.title("Auto Printer")
    root.geometry("1024x768")


    ui = APUI(root)
    root.protocol("WM_DELETE_WINDOW", ui.on_closing)
    root.mainloop()