import customtkinter as ctk

# Set up the main application window
app = ctk.CTk()
app.geometry("300x200")

# Create a CTkProgressBar and pack it in the window
progress_bar = ctk.CTkProgressBar(app, width=200)
progress_bar.pack(pady=20)

# Set an initial value for the progress bar (range is from 0 to 1)
progress_bar.set(0.0)  # Sets progress to 50%

# Function to update progress
def update_progress():
    progress_bar.set(progress_bar.get() + 0.1)  # Increase progress by 10%

# Create a button to update the progress bar
update_button = ctk.CTkButton(app, text="Update Progress", command=update_progress)
update_button.pack(pady=20)

# Run the application
app.mainloop()
