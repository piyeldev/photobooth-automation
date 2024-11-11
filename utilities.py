from PIL import Image
import os
from datetime import datetime
import subprocess

photocard_frame = Image.open("../assets/frame_un.png")
def frame_image_upc(image_path: str):
    Image.open(image_path)


def overlay_image_photocard(background_path):
    filename = os.path.splitext(os.path.basename(background_path))[0]
    # Open the background and frame images
    background = Image.open(background_path)
    frame = photocard_frame
    
    # Get sizes
    frame_width, frame_height = frame.size
    bg_width, bg_height = background.size
    
    # Calculate the new width maintaining aspect ratio, resize background height to frame height
    new_bg_height = frame_height
    aspect_ratio = bg_width / bg_height
    new_bg_width = int(aspect_ratio * new_bg_height)
    
    # Resize background image with proportional width and new height
    background_resized = background.resize((new_bg_width, new_bg_height), Image.LANCZOS)
    
    # Create a blank canvas with frame size to place the resized background and frame
    result_image = Image.new("RGBA", (frame_width, frame_height), (0, 0, 0, 0))  # Transparent background

    # Center the resized background within the frame
    if new_bg_width > frame_width:
        # If resized background is wider, crop it
        left_padding = (new_bg_width - frame_width) // 2
        background_cropped = background_resized.crop((left_padding, 0, left_padding + frame_width, new_bg_height))
        result_image.paste(background_cropped, (0, 0))  # Paste centered in the result
    else:
        # If resized background is narrower, center it
        offset_x = (frame_width - new_bg_width) // 2
        result_image.paste(background_resized, (offset_x, 0))  # Paste centered in the result
    
    # Paste the frame on top of the resized background
    result_image.paste(frame, (0, 0), frame)  # Assuming the frame has transparency (RGBA)

    
    # Save the result
    overlayed_img_path = f"out/framed/{filename}-framed-{current_date_time()}.png"
    result_image.save(overlayed_img_path)
    return overlayed_img_path
    # save_image_for_printing("out/out.png")

def photostrip_processor(image_paths: list):
    # Load the photostrip frame (with transparency)
    photostrip = Image.open("../assets/photostrip.png").convert("RGBA")

    # Open the three images to place behind the photostrip
    photo1 = Image.open(image_paths[0]).convert("RGBA")
    photo2 = Image.open(image_paths[1]).convert("RGBA")
    photo3 = Image.open(image_paths[2]).convert("RGBA")

    # Resize the photos to fit within the photostrip's boxes
    # (Adjust the sizes below based on the actual white areas of your photostrip)
    size = tuple(s-80 for s in photo1.size)
    photo1 = photo1.resize(size)  
    photo2 = photo2.resize(size)  
    photo3 = photo3.resize(size)  

    # Create a background to paste the photos onto
    # Make it the same size as the photostrip
    background = Image.new("RGBA", photostrip.size, (255, 255, 255, 0))

    # Paste the photos into their respective positions
    # Adjust the coordinates (x, y) based on the white box areas in the photostrip
    background.paste(photo1, (20, 103))  # Top box
    background.paste(photo2, (20, 568))  # Middle box
    background.paste(photo3, (20, 1031))  # Bottom box

    # Overlay the photostrip on top of the photos
    final_image = Image.alpha_composite(background, photostrip)

    # Save or display the final image
    save_path = f"out/photostripped/photostrip-{current_date_time()}.png"
    final_image.save(save_path)

    return save_path

def save_image_for_printing(image_path, size_in_inches=(4, 5), dpi=300):
    # Open the image
    image = Image.open(image_path)
    
    # Convert inches to pixels
    width_in_pixels = int(size_in_inches[0] * dpi)
    height_in_pixels = int(size_in_inches[1] * dpi)
    
    # Resize the image to the target size for printing
    image_resized = image.resize((height_in_pixels, width_in_pixels), Image.LANCZOS)
    
    # Save the resized image
    image_resized.save("out/out-pdf-img.png")
    convert_image_to_pdf("out/out-pdf-img.png")


def current_date_time():
    current_time = datetime.now()
    formatted_time = current_time.strftime("%y%m%d-%H%M%S")

    return formatted_time
def convert_image_to_pdf(image_path, name_as_prefix):
    # Open the image
    print("i'm runnin", name_as_prefix)
    image = Image.open(image_path)
    
    if image.mode != 'RGB':
        image = image.convert('RGB')
    # Convert and save as PDF
    path = f"out/pdf/{name_as_prefix if name_as_prefix else ""}-{get_filename_from_path(image_path)}.pdf"
    image.save(path, "PDF", resolution=300)

    return os.path.join(os.getcwd(), path)

def get_filename_from_path(path):
    return os.path.splitext(os.path.basename(path))[0]

def xdg_open(path: str):
    subprocess.run(["xdg-open", path])
    
