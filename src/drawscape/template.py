import os
import json
from HersheyFonts import HersheyFonts

# Constants
SVG_WIDTH = 210
SVG_HEIGHT = 297
INSET = 8
BORDER_WIDTH = SVG_WIDTH - (2 * INSET)
BORDER_HEIGHT = SVG_HEIGHT - (2 * INSET)
LEGEND_X = INSET + 5
LEGEND_Y = INSET + 5
CELL_HEIGHT = 8
GRID_SPACING = 10
TITLE_SCALE = 0.3
SUBTITLE_SCALE = 0.2
RIGHT_MARGIN = 15
SUBTITLE_RIGHT_MARGIN = 15

# Stroke width constants
BORDER_STROKE_WIDTH = "0.5"
GRID_STROKE_WIDTH = "0.5"
LEGEND_STROKE_WIDTH = "0.5"
TEXT_STROKE_WIDTH = "0.6"
TITLE_STROKE_WIDTH = "0.5"

def template(json_file_path, include_grid=False):
    
    # Load data from JSON file
    with open(json_file_path, 'r') as f:
        data = json.load(f)

    # Load SVG data from the file specified in the JSON
    svg_file_path = data.get('SVG', '')
    if svg_file_path:
        # Expand the ~ to the user's home directory if present
        svg_file_path = os.path.expanduser(svg_file_path)
        
        if os.path.exists(svg_file_path):
            with open(svg_file_path, 'r') as svg_file:
                svg_data = svg_file.read()
            # Remove enclosing XML and svg tags
            svg_data = svg_data.split('<svg', 1)[-1]
            svg_data = svg_data.rsplit('</svg>', 1)[0]
            
            # Remove metadata
            start_index = svg_data.find('<metadata')
            end_index = svg_data.find('</metadata>') + len('</metadata>')
            if start_index != -1 and end_index != -1:
                svg_data = svg_data[:start_index] + svg_data[end_index:]
            
            # Strip leading/trailing whitespace
            svg_data = svg_data.strip()
        else:
            print(f"Warning: SVG file not found at {svg_file_path}")
            svg_data = None
    else:
        print("Warning: No SVG file path specified in the JSON data")
        svg_data = None
    
    # Extract title, subtitle, and specifications from JSON data
    title_text = data.get('title', '')
    subtitle_text = data.get('subtitle', '')
    sailboat_specs = [{'name': spec['label'], 'detail': spec['detail']} for spec in data.get('specifications', [])]

    thefont = HersheyFonts()
    thefont.load_default_font('futural')

    # Start SVG content with XML declaration and dimensions with viewBox
    svg_content = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
    svg_content += f'<svg width="{SVG_WIDTH}mm" height="{SVG_HEIGHT}mm" viewBox="0 0 {SVG_WIDTH} {SVG_HEIGHT}" xmlns="http://www.w3.org/2000/svg">\n'
    
    # Add a group for border elements
    svg_content += '  <g id="borders">\n'
    
    # Add a 1pt Border rectangle inset 8 from the edges using a path element
    svg_content += f'    <path d="M {INSET} {INSET} H {INSET + BORDER_WIDTH} V {INSET + BORDER_HEIGHT} H {INSET} Z" fill="none" stroke="black" stroke-width="{BORDER_STROKE_WIDTH}" id="Border" />\n'
    svg_content += f'    <path d="M {INSET} {INSET} V {INSET + BORDER_HEIGHT} H {INSET + BORDER_WIDTH} V {INSET} Z" fill="none" stroke="black" stroke-width="{BORDER_STROKE_WIDTH}" id="ReversedBorder" />\n'
    
    # Close the group for border elements
    svg_content += '  </g>\n'
    
    # Add grid pattern inside the border if include_grid is True
    if include_grid:
        for x in range(INSET, INSET + BORDER_WIDTH, GRID_SPACING):
            svg_content += f'  <line x1="{x}" y1="{INSET}" x2="{x}" y2="{INSET + BORDER_HEIGHT}" stroke="lightgray" stroke-width="{GRID_STROKE_WIDTH}" />\n'
        for y in range(INSET, INSET + BORDER_HEIGHT, GRID_SPACING):
            svg_content += f'  <line x1="{INSET}" y1="{y}" x2="{INSET + BORDER_WIDTH}" y2="{y}" stroke="lightgray" stroke-width="{GRID_STROKE_WIDTH}" />\n'
    
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
    legend_height = len(sailboat_specs) * CELL_HEIGHT  # Adjusted for dynamic number of rows

    # Add 2 column legend outline with labels
    svg_content += f'  <g id="legend" fill="none" stroke="black" stroke-width="{LEGEND_STROKE_WIDTH}">\n'
    svg_content += f'    <rect id="legend-border" x="{LEGEND_X}" y="{LEGEND_Y}" width="{legend_width}" height="{legend_height}" />\n'
    
    # Add vertical line for columns
    svg_content += f'    <line id="legend-column-divider" x1="{LEGEND_X + name_column_width}" y1="{LEGEND_Y}" x2="{LEGEND_X + name_column_width}" y2="{LEGEND_Y + legend_height}" />\n'
    
    # Add horizontal lines for rows and text for specifications
    for i, spec in enumerate(sailboat_specs):
        y = LEGEND_Y + i * CELL_HEIGHT
        svg_content += f'    <line id="legend-row-divider-{i}" x1="{LEGEND_X}" y1="{y + CELL_HEIGHT}" x2="{LEGEND_X + legend_width}" y2="{y + CELL_HEIGHT}" />\n'
        text_y = y + (CELL_HEIGHT / 2)  # Vertically center the text
        
        svg_content += f'    <g id="legend-label-{i}-name" transform="translate({LEGEND_X + 2}, {text_y}) scale(0.1)">\n'
        for line in thefont.lines_for_text(spec["name"]):
            path_data = "M" + " L".join(f"{x},{y}" for x, y in line)
            svg_content += f'      <path d="{path_data}" fill="none" stroke="black" stroke-width="{TEXT_STROKE_WIDTH}" />\n'
        svg_content += '    </g>\n'
        
        svg_content += f'    <g id="legend-label-{i}-detail" transform="translate({LEGEND_X + name_column_width + 2}, {text_y}) scale(0.1)">\n'
        for line in thefont.lines_for_text(spec["detail"]):
            path_data = "M" + " L".join(f"{x},{y}" for x, y in line)
            svg_content += f'      <path d="{path_data}" fill="none" stroke="black" stroke-width="{TEXT_STROKE_WIDTH}" />\n'
        svg_content += '    </g>\n'

    svg_content += '  </g>\n'
    

    # Calculate bounding box of the text
    min_x, max_x = float('inf'), float('-inf')
    min_y, max_y = float('inf'), float('-inf')
    for line in thefont.lines_for_text(title_text):
        for x, y in line:
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)
    
    text_width = max_x - min_x
    text_height = max_y - min_y

    print(text_width, text_height)
    
    # Calculate translation to right-align
    translate_x = SVG_WIDTH - (text_width * TITLE_SCALE) - RIGHT_MARGIN
        
    # Add title text using HersheyFonts in top right corner of the outside border rectangle
    svg_content += f'  <g id="title" transform="translate({translate_x}, {text_height - 3}) scale({TITLE_SCALE})">\n'
    for line in thefont.lines_for_text(title_text):
        path_data = "M" + " L".join(f"{x},{y}" for x, y in line)
        svg_content += f'    <path d="{path_data}" fill="none" stroke="black" stroke-width="{TITLE_STROKE_WIDTH}" />\n'
    svg_content += '  </g>\n'
    
    # Calculate bounding box of the subtitle text
    min_x, max_x = float('inf'), float('-inf')
    min_y, max_y = float('inf'), float('-inf')
    for line in thefont.lines_for_text(subtitle_text):
        for x, y in line:
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)
    
    subtitle_width = max_x - min_x
    subtitle_height = max_y - min_y

    # Calculate translation to right-align subtitle
    subtitle_translate_x = SVG_WIDTH - (subtitle_width * SUBTITLE_SCALE) - SUBTITLE_RIGHT_MARGIN
    subtitle_translate_y = text_height + 9  # Adjust vertical spacing as needed
    
    # Add subtitle text using HersheyFonts below the title
    svg_content += f'  <g id="subtitle" transform="translate({subtitle_translate_x}, {subtitle_translate_y}) scale({SUBTITLE_SCALE})">\n'
    for line in thefont.lines_for_text(subtitle_text):
        path_data = "M" + " L".join(f"{x},{y}" for x, y in line)
        svg_content += f'    <path d="{path_data}" fill="none" stroke="black" stroke-width="{TITLE_STROKE_WIDTH}" />\n'
    svg_content += '  </g>\n'

    # Calculate the center of the document
    center_x = SVG_WIDTH / 2
    center_y = SVG_HEIGHT / 2

    # Add the SVG content to the middle of the document
    if svg_data:
        svg_content += f'  <g id="inserted_svg" transform="translate({center_x}, {center_y})">\n'
        svg_content += '<style>#inserted_svg svg { max-width: 100mm; max-height: 100mm; }</style>\n'
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
    
    return output_path