from customtkinter import *
from PIL import Image, ImageTk
import utilities

set_appearance_mode("System")  # Modes: system (default), light, dark
set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

app = CTk()
app.title("AutoPrinter")  # create CTk window like you do with the Tk window
app.geometry("1024x668")

def button_function():
    print("button pressed")

empty = CTkLabel(app, text="", padx=25)
empty.grid(row=0, column=0, rowspan=12)

# ========= heading 
heading = CTkLabel(app, text="AutoPrinter", fg_color="transparent", font=("Cantarell", 32, "bold"), pady=10, anchor="w")
heading.grid(row=0, column=3, sticky="w")

img_lbl = CTkLabel(app, text="", fg_color="transparent", padx=5, pady=5)
img_lbl.grid(row=1, column=3)

def testImage(path: str):
    test_image = Image.open(path)
    new_test_image_size = tuple(i/3 for i in test_image.size)
    # ===== preview image
    preview_image = CTkImage(dark_image=test_image, size=new_test_image_size)
    img_lbl.configure(image=preview_image)
    img_lbl.image = preview_image 
    

testImage("../assets/frame_un.png")
# ==== choosing frame ===
choosing_frame = CTkFrame(app, fg_color="transparent")
choosing_frame.grid(row=1, column=4, sticky="n")
#===space between preview and choosing frame
space = CTkLabel(choosing_frame, text="", padx=20)
space.grid(row=0, column=0, rowspan=3)
selected_folder = ""



#====== frame label
frame_label = CTkLabel(choosing_frame, text="Frame", font=("Cantarell", 24, "bold"), fg_color="transparent")
frame_label.grid(row=3, column=1, sticky="sw")


def frame_chooser_handler(choice):
    if choice == "PhotoCard":
        testImage("../assets/frame_un.png")

    elif choice == "PhotoStrip":
        testImage("../assets/photostrip.png")


# ===== frame_chooser drop down menu
options = ["PhotoCard", "PhotoStrip"]
dropdown = CTkOptionMenu(choosing_frame, values=options, command=frame_chooser_handler)
dropdown.grid(row=4, column=1, padx=4)

last_seen_files = set()
def monitor_folder():
    if selected_folder:  # Ensure folder is selected
        global last_seen_files
        current_files = set(os.listdir(selected_folder))  # Get current list of files in folder
        new_files = current_files - last_seen_files  # Find new files
        image_files = [f for f in new_files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]  # Check if new files are images
        
        if image_files:
            # If new image files are found, get the first image's full path
            new_image_path = os.path.join(selected_folder, image_files[0])
            print(f"New image file detected: {new_image_path}")
            # partially for the photocard
            utilities.overlay_images(new_image_path)
        
        last_seen_files = current_files  # Update last seen files
        
    app.after(2000, monitor_folder)  # Check every 2000 ms (2 seconds)


monitor_folder()
app.mainloop()