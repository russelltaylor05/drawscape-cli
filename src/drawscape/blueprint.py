import os
import json
from HersheyFonts import HersheyFonts
import xml.etree.ElementTree as ET
import re



# Paper sizes in millimeters (width, height)
PAPER_SIZES = {
    'a3': (297, 420),
    'a4': (210, 297),
    'letter': (216, 279),
    'tabloid': (279.4, 431.8)
}


def blueprint(json_file_path, size, orientation='portrait'):

    # Load data from JSON file
    with open(json_file_path, 'r') as f:
        data = json.load(f)

    # Determine which function to use based on size
    svg_content = container(size, data, orientation)
    
    # Generate output file path
    output_dir = os.getcwd()  # Current working directory
    
    # Create the new output filename
    output_filename = "blueprint.svg"
    output_path = os.path.join(output_dir, output_filename)
    
    # Save SVG content to file
    with open(output_path, 'w') as f:
        f.write(svg_content)
    
    print(f"SVG template with Border, legend, title, subtitle saved to {output_path}")
    
    return output_path


def container(size, json_data, orientation):
    
    thefont = HersheyFonts()
    thefont.load_default_font('futural')

    if size in PAPER_SIZES:
        DOCUMENT_WIDTH, DOCUMENT_HEIGHT = PAPER_SIZES[size]
    else:
        print("Cannot find the specified paper size. Defaulting to A4 size.")
        DOCUMENT_WIDTH, DOCUMENT_HEIGHT = PAPER_SIZES['a4']

    # Swap document width and height if orientation is landscape
    if orientation.lower() == 'landscape':
        DOCUMENT_WIDTH, DOCUMENT_HEIGHT = DOCUMENT_HEIGHT, DOCUMENT_WIDTH

    if size in ['a3', 'tabloid']:
        # Constants for A3 and Tabloid
        BORDER_INSET = 10
        INTERNAL_PADDING = 8
        
        LEGEND_CELL_HEIGHT = 8
        LEGEND_PADDING = 10
        LEGEND_TEXT_SCALE_FACTOR = 0.13

        # Titles
        TITLE_SCALE_FACTOR = 0.5
        SUBTITLE_SCALE_FACTOR = 0.35
        
    else:
        # Constants for A4 and Letter
        BORDER_INSET = 8
        INTERNAL_PADDING = 6
        
        LEGEND_CELL_HEIGHT = 6
        LEGEND_PADDING = 8
        LEGEND_TEXT_SCALE_FACTOR = 0.1

        # Titles
        TITLE_SCALE_FACTOR = 0.3
        SUBTITLE_SCALE_FACTOR = 0.2
        

    TITLE_RIGHT_MARGIN = BORDER_INSET + INTERNAL_PADDING + 1
    SUBTITLE_RIGHT_MARGIN = BORDER_INSET + INTERNAL_PADDING + 1

    #Stroke Widths
    TITLE_STROKE_WIDTH = "0.75"
    TEXT_STROKE_WIDTH = "0.9"
    BORDER_STROKE_WIDTH = "0.8"
    LEGEND_STROKE_WIDTH = "0.6"

    #Border Dimensions
    BORDER_WIDTH = DOCUMENT_WIDTH - (2 * BORDER_INSET)
    BORDER_HEIGHT = DOCUMENT_HEIGHT - (2 * BORDER_INSET)
    
    #Legend Dimensions
    LEGEND_START_X = BORDER_INSET + INTERNAL_PADDING
    LEGEND_START_Y = BORDER_INSET + INTERNAL_PADDING
        

    # Extract title, subtitle, and specifications from JSON data
    title_text = json_data.get('title', '').upper()
    subtitle_text = json_data.get('subtitle', '')
    legend_details = [{'name': spec['label'], 'detail': spec['detail']} for spec in json_data.get('specifications', [])]
    
    # Start SVG content with XML declaration and dimensions with viewBox
    svg_content = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
    svg_content += f'<svg width="{DOCUMENT_WIDTH}mm" height="{DOCUMENT_HEIGHT}mm" viewBox="0 0 {DOCUMENT_WIDTH} {DOCUMENT_HEIGHT}" xmlns="http://www.w3.org/2000/svg">\n'
    
    # Add a group for border elements
    svg_content += '  <g id="borders">\n'
    
    # Add a 1pt Border rectangle from the edges using a path element
    svg_content += f'    <path d="M {BORDER_INSET} {BORDER_INSET} H {BORDER_INSET + BORDER_WIDTH} V {BORDER_INSET + BORDER_HEIGHT} H {BORDER_INSET} Z" fill="none" stroke="black" stroke-width="{BORDER_STROKE_WIDTH}" id="Border" />\n'
    svg_content += f'    <path d="M {BORDER_INSET} {BORDER_INSET} V {BORDER_INSET + BORDER_HEIGHT} H {BORDER_INSET + BORDER_WIDTH} V {BORDER_INSET} Z" fill="none" stroke="black" stroke-width="{BORDER_STROKE_WIDTH}" id="ReversedBorder" />\n'
    
    # Close the group for border elements
    svg_content += '  </g>\n'
    
    # Calculate the width of the widest label name and label detail
    max_name_width = float('-inf')
    max_detail_width = float('-inf')
    for spec in legend_details:
        # Calculate bounding box for name
        min_x, max_x = float('inf'), float('-inf')
        for line in thefont.lines_for_text(spec["name"]):
            for x, y in line:
                min_x = min(min_x, x)
                max_x = max(max_x, x)
        name_width = max_x - min_x
        max_name_width = max(max_name_width, name_width)

        # Calculate bounding box for detail
        min_x, max_x = float('inf'), float('-inf')
        for line in thefont.lines_for_text(spec["detail"]):
            for x, y in line:
                min_x = min(min_x, x)
                max_x = max(max_x, x)
        detail_width = max_x - min_x
        max_detail_width = max(max_detail_width, detail_width)

    # Calculate the legend width based on the widest text with increased padding
    name_column_width = max_name_width * LEGEND_TEXT_SCALE_FACTOR + LEGEND_PADDING  # Scale factor 0.1, plus 8 for padding
    detail_column_width = max_detail_width * LEGEND_TEXT_SCALE_FACTOR + LEGEND_PADDING  # Scale factor 0.1, plus 8 for padding
    legend_width = name_column_width + detail_column_width

    # Recalculate legend dimensions
    legend_height = len(legend_details) * LEGEND_CELL_HEIGHT  # Adjusted for dynamic number of rows

    # Add 2 column legend outline with labels
    svg_content += f'  <g id="legend" fill="none" stroke="black" stroke-width="{LEGEND_STROKE_WIDTH}">\n'
    svg_content += f'    <rect id="legend-border" x="{LEGEND_START_X}" y="{LEGEND_START_Y}" width="{legend_width}" height="{legend_height}" />\n'
    
    # Add vertical line for columns
    svg_content += f'    <line id="legend-column-divider" x1="{LEGEND_START_X + name_column_width}" y1="{LEGEND_START_Y}" x2="{LEGEND_START_X + name_column_width}" y2="{LEGEND_START_Y + legend_height}" />\n'
    
    # Add horizontal lines for rows and text for specifications
    for i, spec in enumerate(legend_details):
        y = LEGEND_START_Y + i * LEGEND_CELL_HEIGHT
        svg_content += f'    <line id="legend-row-divider-{i}" x1="{LEGEND_START_X}" y1="{y + LEGEND_CELL_HEIGHT}" x2="{LEGEND_START_X + legend_width}" y2="{y + LEGEND_CELL_HEIGHT}" />\n'
        text_y = y + (LEGEND_CELL_HEIGHT / 2)  # Vertically center the text
        
        svg_content += f'    <g id="legend-label-{i}-name" transform="translate({LEGEND_START_X + 2}, {text_y}) scale({LEGEND_TEXT_SCALE_FACTOR})">\n'
        for line in thefont.lines_for_text(spec["name"]):
            path_data = "M" + " L".join(f"{x},{y}" for x, y in line)
            svg_content += f'      <path d="{path_data}" fill="none" stroke="black" stroke-width="{TEXT_STROKE_WIDTH}" />\n'
        svg_content += '    </g>\n'
        
        svg_content += f'    <g id="legend-label-{i}-detail" transform="translate({LEGEND_START_X + name_column_width + 2}, {text_y}) scale({LEGEND_TEXT_SCALE_FACTOR})">\n'
        for line in thefont.lines_for_text(spec["detail"]):
            path_data = "M" + " L".join(f"{x},{y}" for x, y in line)
            svg_content += f'      <path d="{path_data}" fill="none" stroke="black" stroke-width="{TEXT_STROKE_WIDTH}" />\n'
        svg_content += '    </g>\n'

    svg_content += '  </g>\n'

    
    # baseline letter heigh calculations
    heightcalc = get_text_bounding_box("R", thefont) # letters belwo the line (y, g, etc) mess up the calc when using lowercase. We are currenlty forcing uppercase.
    title_height = heightcalc['height']

    """
    Title
    """
    title_box = get_text_bounding_box(title_text, thefont)
    title_width = title_box['width']

    title_translate_x = DOCUMENT_WIDTH - (title_width * TITLE_SCALE_FACTOR) - TITLE_RIGHT_MARGIN
    title_translate_y =  ((title_height / 2) * TITLE_SCALE_FACTOR) + BORDER_INSET + INTERNAL_PADDING
    svg_content += f'  <g id="title" transform="translate({title_translate_x}, {title_translate_y}) scale({TITLE_SCALE_FACTOR})">\n'
    for line in thefont.lines_for_text(title_text):
        title_path_data = "M" + " L".join(f"{x},{y}" for x, y in line)
        svg_content += f'    <path d="{title_path_data}" fill="none" stroke="black" stroke-width="{TITLE_STROKE_WIDTH}" />\n'
    svg_content += '  </g>\n'
    
    """
    Sub Title
    """
    subtitle_box = get_text_bounding_box(subtitle_text, thefont)    
    subtitle_width = subtitle_box['width']
    subtitle_translate_x = DOCUMENT_WIDTH - (subtitle_width * SUBTITLE_SCALE_FACTOR) - SUBTITLE_RIGHT_MARGIN
    subtitle_translate_y = ((title_height / 2) * SUBTITLE_SCALE_FACTOR) + (title_height * TITLE_SCALE_FACTOR) + BORDER_INSET + INTERNAL_PADDING + INTERNAL_PADDING
    svg_content += f'  <g id="subtitle" transform="translate({subtitle_translate_x}, {subtitle_translate_y}) scale({SUBTITLE_SCALE_FACTOR})">\n'
    for line in thefont.lines_for_text(subtitle_text):
        path_data = "M" + " L".join(f"{x},{y}" for x, y in line)
        svg_content += f'    <path d="{path_data}" fill="none" stroke="black" stroke-width="{TITLE_STROKE_WIDTH}" />\n'
    svg_content += '  </g>\n'


    # Close the SVG tag
    svg_content += '</svg>\n'

    return svg_content


# This function loads SVG data from a file and returns the SVG content as a string,
# along with the width, height, and units of the SVG.

def load_svg_data(svg_file_path):
    if not svg_file_path:
        print("Warning: No SVG file path specified")
        return None, None, None, None

    svg_file_path = os.path.expanduser(svg_file_path)
    
    if not os.path.exists(svg_file_path):
        print(f"Warning: SVG file not found at {svg_file_path}")
        return None, None, None, None

    try:
        with open(svg_file_path, 'r') as file:
            svg_content = file.read()

        # Parse the SVG content
        root = ET.fromstring(svg_content)

        # Get width and height
        width = root.get('width', '0')
        height = root.get('height', '0')

        # Extract numeric values and units
        width_match = re.match(r'(\d+(\.\d+)?)\s*(\w*)', width)
        height_match = re.match(r'(\d+(\.\d+)?)\s*(\w*)', height)

        if width_match and height_match:
            width_value = float(width_match.group(1))
            height_value = float(height_match.group(1))
            units = width_match.group(3) or height_match.group(3) or 'px'
        else:
            print(f"Warning: Unable to parse width ({width}) or height ({height})")
            return None, None, None, None

        # Remove containing <xml> tags and <svg> tags
        svg_content = re.sub(r'<\?xml.*?\?>', '', svg_content)
        svg_content = re.sub(r'<svg.*?>', '', svg_content)
        svg_content = re.sub(r'</svg>', '', svg_content)

        print(width_value, height_value, units)

        return svg_content.strip(), width_value, height_value, units

    except Exception as e:
        print(f"Error reading SVG file: {e}")
        return None, None, None, None



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