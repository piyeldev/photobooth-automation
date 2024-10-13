import customtkinter as ctk
from PIL import Image, ImageTk
import os
import subprocess

# Function to open file picker using Zenity
def choose_image():
    try:
        # Use Zenity to open file picker
        file_path = subprocess.check_output(
            ['zenity', '--file-selection', '--file-filter=Images | *.png *.jpg *.jpeg *.bmp *.gif']
        ).decode('utf-8').strip()
        
        if file_path:
            # Load and display the image
            image = Image.open(file_path)
            image.thumbnail((300, 300))  # Resize the image to fit in the window
            img_display = ImageTk.PhotoImage(image)

            # Display the image in the label
            image_label.configure(image=img_display)
            image_label.image = img_display
            
            # Display the file path
            file_path_label.configure(text=os.path.basename(file_path))
    
    except subprocess.CalledProcessError:
        # Handle the case when user cancels the file dialog
        pass

# Initialize the application window
app = ctk.CTk()  
app.geometry("600x400")
app.title("Image Chooser")

# Create a button to choose an image
choose_button = ctk.CTkButton(app, text="Choose Image", command=choose_image)
choose_button.pack(pady=20)

# Label to display the image
image_label = ctk.CTkLabel(app)
image_label.pack(pady=10)

# Label to display the file path of the chosen image
file_path_label = ctk.CTkLabel(app, text="")
file_path_label.pack()

# Run the application
app.mainloop()
