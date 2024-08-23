import svgwrite
import json
from HersheyFonts import HersheyFonts
import os

# Constants for return shipping information
RETURN_NAME = "Drawscape, Inc"
RETURN_ADDRESS = "10266 Truckee Airport Rd Suite C"
RETURN_CITY = "Truckee, CA 96161"

# Constants for dimensions (in mm)
LABEL_WIDTH = 292.1  # 11.5 inches in mm
LABEL_HEIGHT = 215.9  # 8.5 inches in mm
PADDING = 10  # 10mm padding

def create_shipping_label(json_file_path, output_path='shipping_label.svg'):
    print(f"Starting to create shipping label...")
    print(f"JSON file path: {json_file_path}")
    print(f"Output path: {output_path}")

    # Initialize Hershey Font
    thefont = HersheyFonts()
    thefont.load_default_font('futural')

    # Load shipping information from JSON file
    try:
        with open(json_file_path, 'r') as file:
            shipping_info = json.load(file)
    except FileNotFoundError:
        print(f"Error: JSON file not found at {json_file_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in file {json_file_path}")
        return None

    # Set variables for shipping information
    to_name = shipping_info.get('to_name', 'N/A')
    to_address = shipping_info.get('to_address', 'N/A')
    to_city = shipping_info.get('to_city', 'N/A')
    

    # Create a new SVG drawing (landscape orientation) with padding
    dwg = svgwrite.Drawing(output_path, size=(f'{LABEL_WIDTH}mm', f'{LABEL_HEIGHT}mm'), viewBox=f'0 0 {LABEL_WIDTH} {LABEL_HEIGHT}')

    # Add return address in top left corner, with padding
    scale_factor = .13
    line_spacing = 7 #millimieters
    
    for i, text in enumerate([RETURN_NAME, RETURN_ADDRESS, RETURN_CITY], start=1):
        y_offset = line_spacing * i
        add_hershey_text(dwg, thefont, text, PADDING, y_offset + PADDING, scale=scale_factor)

    # Add recipient address in the center of the document
    center_x = LABEL_WIDTH / 2
    center_y = LABEL_HEIGHT / 2
    scale_factor = .25
    line_spacing = 10  # millimeters

    for i, text in enumerate([to_name, to_address, to_city], start=1):
        y_offset = line_spacing * i
        text_bbox = get_text_bounding_box(text, thefont)
        text_width = text_bbox['width'] * scale_factor
        text_x = center_x - (text_width / 2)
        add_hershey_text(dwg, thefont, text, text_x, center_y + y_offset, scale=scale_factor)

    # Save the SVG file
    try:
        dwg.save()
        print(f"Successfully saved shipping label: {output_path}")
    except Exception as e:
        print(f"Error saving SVG file: {str(e)}")
        return None

    if os.path.exists(output_path):
        print(f"Verified: File exists at {output_path}")
        print(f"File size: {os.path.getsize(output_path)} bytes")
    else:
        print(f"Warning: File not found at {output_path}")

    return output_path

# Function to add Hershey Text
def add_hershey_text(dwg, thefont, text, x=0, y=0, scale=1):
    group = svgwrite.container.Group(transform=f'translate({x}, {y}) scale({scale})')
    for line in thefont.lines_for_text(text):
        path_data = "M" + " L".join(f"{x},{y}" for x, y in line)
        group.add(dwg.path(d=path_data, fill="none", stroke="black", stroke_width="1"))
    dwg.add(group)

def get_text_bounding_box(text, thefont):
    """
    Calculate the bounding box of a given text using the specified font.

    Args:
        text (str): The text to calculate the bounding box for.
        thefont (Font): The font object used to render the text.

    Returns:
        dict: A dictionary containing the bounding box information:
            - 'min_x': Minimum x-coordinate
            - 'max_x': Maximum x-coordinate
            - 'min_y': Minimum y-coordinate
            - 'max_y': Maximum y-coordinate
            - 'width': Width of the bounding box
            - 'height': Height of the bounding box
    """
    min_x, max_x = float('inf'), float('-inf')
    min_y, max_y = float('inf'), float('-inf')
    
    for line in thefont.lines_for_text(text):
        for x, y in line:
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)
    
    width = max_x - min_x
    height = max_y - min_y
    
    return {
        'min_x': min_x,
        'max_x': max_x,
        'min_y': min_y,
        'max_y': max_y,
        'width': width,
        'height': height
    }