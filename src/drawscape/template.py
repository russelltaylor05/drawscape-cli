import os
import json
from HersheyFonts import HersheyFonts
import xml.etree.ElementTree as ET
import re

# Constants (all measurements in millimeters unless otherwise specified)

# Document
DOCUMENT_WIDTH = 210
DOCUMENT_HEIGHT = 297

# Border
BORDER_INSET = 8
BORDER_WIDTH = DOCUMENT_WIDTH - (2 * BORDER_INSET)
BORDER_HEIGHT = DOCUMENT_HEIGHT - (2 * BORDER_INSET)
BORDER_STROKE_WIDTH = "0.6"

# Legend
LEGEND_START_X = BORDER_INSET + 5
LEGEND_START_Y = BORDER_INSET + 5
LEGEND_CELL_HEIGHT = 6
LEGEND_STROKE_WIDTH = "0.4"

# Titles
TITLE_SCALE_FACTOR = 0.3
SUBTITLE_SCALE_FACTOR = 0.2
TITLE_RIGHT_MARGIN = 15
SUBTITLE_RIGHT_MARGIN = 15
TITLE_STROKE_WIDTH = "0.5"

# Text
TEXT_STROKE_WIDTH = "0.6"


def template(json_file_path):
    
    # Load data from JSON file
    with open(json_file_path, 'r') as f:
        data = json.load(f)

    # Load SVG data from the file specified in the JSON
    svg_file_path = data.get('SVG', '')
    svg_data, svg_width, svg_height, svg_units = load_svg_data(svg_file_path)

    print(svg_width, svg_height, svg_units)
    
    # Extract title, subtitle, and specifications from JSON data
    title_text = data.get('title', '')
    subtitle_text = data.get('subtitle', '')
    sailboat_specs = [{'name': spec['label'], 'detail': spec['detail']} for spec in data.get('specifications', [])]

    thefont = HersheyFonts()
    thefont.load_default_font('futural')

    # Start SVG content with XML declaration and dimensions with viewBox
    svg_content = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
    svg_content += f'<svg width="{DOCUMENT_WIDTH}mm" height="{DOCUMENT_HEIGHT}mm" viewBox="0 0 {DOCUMENT_WIDTH} {DOCUMENT_HEIGHT}" xmlns="http://www.w3.org/2000/svg">\n'
    
    # Add a group for border elements
    svg_content += '  <g id="borders">\n'
    
    # Add a 1pt Border rectangle inset 8 from the edges using a path element
    svg_content += f'    <path d="M {BORDER_INSET} {BORDER_INSET} H {BORDER_INSET + BORDER_WIDTH} V {BORDER_INSET + BORDER_HEIGHT} H {BORDER_INSET} Z" fill="none" stroke="black" stroke-width="{BORDER_STROKE_WIDTH}" id="Border" />\n'
    svg_content += f'    <path d="M {BORDER_INSET} {BORDER_INSET} V {BORDER_INSET + BORDER_HEIGHT} H {BORDER_INSET + BORDER_WIDTH} V {BORDER_INSET} Z" fill="none" stroke="black" stroke-width="{BORDER_STROKE_WIDTH}" id="ReversedBorder" />\n'
    
    # Close the group for border elements
    svg_content += '  </g>\n'
    
    # Calculate the width of the widest label name and label detail
    max_name_width = float('-inf')
    max_detail_width = float('-inf')
    for spec in sailboat_specs:
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
    name_column_width = max_name_width * 0.1 + 8  # Scale factor 0.1, plus 8 for padding
    detail_column_width = max_detail_width * 0.1 + 8  # Scale factor 0.1, plus 8 for padding
    legend_width = name_column_width + detail_column_width

    # Recalculate legend dimensions
    legend_height = len(sailboat_specs) * LEGEND_CELL_HEIGHT  # Adjusted for dynamic number of rows

    # Add 2 column legend outline with labels
    svg_content += f'  <g id="legend" fill="none" stroke="black" stroke-width="{LEGEND_STROKE_WIDTH}">\n'
    svg_content += f'    <rect id="legend-border" x="{LEGEND_START_X}" y="{LEGEND_START_Y}" width="{legend_width}" height="{legend_height}" />\n'
    
    # Add vertical line for columns
    svg_content += f'    <line id="legend-column-divider" x1="{LEGEND_START_X + name_column_width}" y1="{LEGEND_START_Y}" x2="{LEGEND_START_X + name_column_width}" y2="{LEGEND_START_Y + legend_height}" />\n'
    
    # Add horizontal lines for rows and text for specifications
    for i, spec in enumerate(sailboat_specs):
        y = LEGEND_START_Y + i * LEGEND_CELL_HEIGHT
        svg_content += f'    <line id="legend-row-divider-{i}" x1="{LEGEND_START_X}" y1="{y + LEGEND_CELL_HEIGHT}" x2="{LEGEND_START_X + legend_width}" y2="{y + LEGEND_CELL_HEIGHT}" />\n'
        text_y = y + (LEGEND_CELL_HEIGHT / 2)  # Vertically center the text
        
        svg_content += f'    <g id="legend-label-{i}-name" transform="translate({LEGEND_START_X + 2}, {text_y}) scale(0.1)">\n'
        for line in thefont.lines_for_text(spec["name"]):
            path_data = "M" + " L".join(f"{x},{y}" for x, y in line)
            svg_content += f'      <path d="{path_data}" fill="none" stroke="black" stroke-width="{TEXT_STROKE_WIDTH}" />\n'
        svg_content += '    </g>\n'
        
        svg_content += f'    <g id="legend-label-{i}-detail" transform="translate({LEGEND_START_X + name_column_width + 2}, {text_y}) scale(0.1)">\n'
        for line in thefont.lines_for_text(spec["detail"]):
            path_data = "M" + " L".join(f"{x},{y}" for x, y in line)
            svg_content += f'      <path d="{path_data}" fill="none" stroke="black" stroke-width="{TEXT_STROKE_WIDTH}" />\n'
        svg_content += '    </g>\n'

    svg_content += '  </g>\n'
    
    """
    Title
    """
    title_bbox = get_text_bounding_box(title_text, thefont)
    title_width = title_bbox['width']
    title_height = title_bbox['height']
    title_translate_x = DOCUMENT_WIDTH - (title_width * TITLE_SCALE_FACTOR) - TITLE_RIGHT_MARGIN
    svg_content += f'  <g id="title" transform="translate({title_translate_x}, {title_height - 3}) scale({TITLE_SCALE_FACTOR})">\n'
    for line in thefont.lines_for_text(title_text):
        title_path_data = "M" + " L".join(f"{x},{y}" for x, y in line)
        svg_content += f'    <path d="{title_path_data}" fill="none" stroke="black" stroke-width="{TITLE_STROKE_WIDTH}" />\n'
    svg_content += '  </g>\n'
    
    """
    Sub Title
    """
    subtitle_bbox = get_text_bounding_box(subtitle_text, thefont)    
    subtitle_width = subtitle_bbox['width']
    subtitle_translate_x = DOCUMENT_WIDTH - (subtitle_width * SUBTITLE_SCALE_FACTOR) - SUBTITLE_RIGHT_MARGIN
    subtitle_translate_y = title_height + 9 
    svg_content += f'  <g id="subtitle" transform="translate({subtitle_translate_x}, {subtitle_translate_y}) scale({SUBTITLE_SCALE_FACTOR})">\n'
    for line in thefont.lines_for_text(subtitle_text):
        path_data = "M" + " L".join(f"{x},{y}" for x, y in line)
        svg_content += f'    <path d="{path_data}" fill="none" stroke="black" stroke-width="{TITLE_STROKE_WIDTH}" />\n'
    svg_content += '  </g>\n'

    # Calculate the center of the document
    center_x = DOCUMENT_WIDTH / 2
    center_y = DOCUMENT_HEIGHT / 2
    
    # Calculate the scale factor to fit the SVG content inside the document
    scale_x = (BORDER_WIDTH - 10) / svg_width  # 10mm margin
    scale_y = (BORDER_HEIGHT - 10) / svg_height  # 10mm margin
    scale_factor = min(scale_x, scale_y)

    # Calculate the position to center the SVG content
    translate_x = center_x - (svg_width * scale_factor / 2)
    translate_y = center_y - (svg_height * scale_factor / 2)

    # Add the SVG content to the middle of the document
    if svg_data:
        svg_content += f'  <g id="inserted_svg">\n'
        svg_content += svg_data
        svg_content += '  </g>\n'

    # Close the SVG tag
    svg_content += '</svg>\n'
    
    # Generate output file path
    output_dir = os.getcwd()  # Current working directory
    # Extract the filename from the SVG path
    svg_filename = os.path.basename(svg_file_path)
    # Remove the extension
    svg_filename_without_ext = os.path.splitext(svg_filename)[0]
    # Create the new output filename
    output_filename = f"{svg_filename_without_ext}_template.svg"
    output_path = os.path.join(output_dir, output_filename)
    
    # Save SVG content to file
    with open(output_path, 'w') as f:
        f.write(svg_content)
    
    print(f"SVG template with Border, legend, title, subtitle saved to {output_path}")
    
    return output_path, svg_units




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