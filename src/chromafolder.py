import os
import argparse
import subprocess
from PIL import Image


def validate_arguments(folder_path, color_hex):
    if not os.path.exists(folder_path):
        print(f"Error: Folder '{folder_path}' not found.")
        return False

    if not color_hex.startswith("#"):
        print(f"Error: '{color_hex}' must start with a '#' character.")
        return False
    if not all(c in "0123456789ABCDEFabcdef" for c in color_hex[1:]):
        print(f"Error: '{color_hex}' contains invalid characters. Use only digits and A-F.")
        return False
    
    return True

def get_template_icon_path():
    try:
        system_theme = subprocess.check_output(['defaults', 'read', '-g', 'AppleInterfaceStyle'], stderr=subprocess.DEVNULL).strip()
    except subprocess.CalledProcessError:
        # The AppleInterfaceStyle does not exist when the system theme is Light
        system_theme = 'Light'
    
    if (system_theme == 'Dark'):
        return 'assets/GrayFolderIcon.BigSur.dark.icns'
    else:
        return 'assets/GrayFolderIcon.BigSur.icns'
    
    
def generate_icon_with_color(image_path, hex_color):
    # Convert hex color to RGB
    rgb_color = tuple(int(hex_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

    # Open image file
    icon = Image.open(image_path)
    icon = icon.convert('RGBA')

    # Convert the image data to a list of lists
    pixels = list(icon.getdata())
    width, height = icon.size
    pixels = [pixels[i * width:(i + 1) * width] for i in range(height)]

    # Average pixel value of the template icon
    avg_pixel_rgb_color = (175, 175, 175)

    for i in range(height):
        for j in range(width):
            pixel = pixels[i][j]
            # Adjust the RGB values
            rgb = [p - b + c for p, b, c in zip(pixel, avg_pixel_rgb_color, rgb_color)]
            # Ensure RGB values are within 0-255
            rgb = [max(0, min(255, int(c))) for c in rgb]
            pixels[i][j] = (*rgb, pixel[3])

    # Create a new image with the adjusted pixels
    new_icon = Image.new('RGBA', icon.size)
    new_icon.putdata([pixel for row in pixels for pixel in row])

    # Save the new icon
    path_to_new_icon = 'temp.icns'
    new_icon.save(path_to_new_icon)

    return path_to_new_icon

def set_icon(icns_path, target_path):
    # Adapted from Lucas Garron's reccomendations:
    # - https://github.com/mklement0/fileicon/blob/9c41a44fac462f66a1194e223aa26e4c3b9b5ae3/bin/fileicon#L268-L276
    # - https://github.com/mklement0/fileicon/issues/32#issuecomment-1074124748
    # - https://apple.stackexchange.com/a/161984

    osa_command = ['osascript', 'scripts/set_icon.applescript', icns_path, target_path]
    subprocess.run(osa_command)


def main():
    parser = argparse.ArgumentParser(description="Change the color of a folder icon on macOS by providing a hexadecimal color value.")
    parser.add_argument("folder_path", help="Target folder path.")
    parser.add_argument("color_hex", help="Hexadecimal color code for the icon, beginning with '#'.")

    args = parser.parse_args()

    if validate_arguments(args.folder_path, args.color_hex):
        template_icon_path = get_template_icon_path()
        new_icon_path = generate_icon_with_color(template_icon_path, args.color_hex)
        set_icon(new_icon_path, args.folder_path)
        os.remove(new_icon_path)

if __name__ == "__main__":
    main()
