from PIL import Image, ExifTags
import os
import random

file_list = []
full_file_path_list = []

def correct_image_orientation(image_path):
    # Open the image
    img = Image.open(image_path)

    # Check if the image has EXIF data
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = img._getexif()

        # Apply the correct orientation
        if exif is not None:
            orientation = exif.get(orientation, 1)
            if orientation == 3:
                img = img.rotate(180, expand=True)
            elif orientation == 6:
                img = img.rotate(270, expand=True)
            elif orientation == 8:
                img = img.rotate(90, expand=True)
    except (AttributeError, KeyError, IndexError):
        # If no EXIF data or orientation information, skip the correction
        print("err")
        pass

    return img

dir_path = []
def files():
    for entry in os.listdir(dir_path):
        full_path = os.path.join(dir_path, entry)
        if os.path.isfile(full_path):
            full_file_path_list.append(full_path)
            file_list.append(entry) 
files()

landscape_overlay = Image.open("../assets/landscape_frame.png")
portrait_overlay = Image.open("../assets/portrait_frame.png")

def processImage(file_list):
    for item in file_list:
        image = correct_image_orientation(item)
        filename = os.path.splitext(os.path.basename(item))[0]
        if (image.height > image.width):
            withOverlay(image, name=filename, overlay=portrait_overlay)
            print("0")
        else:
            withOverlay(image, name=filename, overlay=landscape_overlay)
            print("1")

def withOverlay(image, name, overlay):
    _overlay = overlay.resize(image.size)
    image.paste(_overlay, (0, 0), _overlay)
    image.save(f'../outputs/{name}-framed.png')


def photostrip():


def photoframe():

processImage(full_file_path_list)