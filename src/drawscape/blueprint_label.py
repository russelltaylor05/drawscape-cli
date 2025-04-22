import os
import json
from HersheyFonts import HersheyFonts
import xml.etree.ElementTree as ET
import re
from datetime import datetime
from nextdraw import NextDraw   # Import the module


# Paper sizes in millimeters (width, height)
PAPER_SIZES = {
    'a3': (297, 420),
    'a4': (210, 297),
    'letter': (216, 279),
    'tabloid': (279.4, 431.8)
}


def blueprint_label(json_file_path, svg_file_path):

    # Load data from JSON file
    with open(json_file_path, 'r') as f:
        data = json.load(f)

    # Determine which function to use based on size
    svg_content = container(data, svg_file_path)
    
    # Generate output file path
    output_dir = os.getcwd()  # Current working directory
    
    # Create the new output filename
    output_filename = "label.svg"
    output_path = os.path.join(output_dir, output_filename)
    
    # Save SVG content to file
    with open(output_path, 'w') as f:
        f.write(svg_content)
    
    print(f"SVG template with Border, legend, title, subtitle saved to {output_path}")
    
    return output_path


def container(json_data, svg_file_path):
    
    thefont = HersheyFonts()
    thefont.load_default_font('futural')

    # Default to tabloid size if no size specified
    
    size = 'tabloid'

    if size in PAPER_SIZES:
        DOCUMENT_WIDTH, DOCUMENT_HEIGHT = PAPER_SIZES[size]
    else:
        print("Cannot find the specified paper size. Defaulting to tabloid size.")
        DOCUMENT_WIDTH, DOCUMENT_HEIGHT = PAPER_SIZES['tabloid']

    if size in ['a3', 'tabloid']:
        # Constants for A3 and Tabloid
        BORDER_INSET = 12
        INTERNAL_PADDING = 8
        
        LEGEND_CELL_HEIGHT = 8
        LEGEND_PADDING = 10
        LEGEND_TEXT_SCALE_FACTOR = 0.13
        
    else:
        # Constants for A4 and Letter
        BORDER_INSET = 8
        INTERNAL_PADDING = 6
        
        LEGEND_CELL_HEIGHT = 6
        LEGEND_PADDING = 8
        LEGEND_TEXT_SCALE_FACTOR = 0.1
        

    #Stroke Widths
    TEXT_STROKE_WIDTH = "0.9"
    LEGEND_STROKE_WIDTH = "0.6"
    
    #Legend Dimensions
    LEGEND_START_X = BORDER_INSET + INTERNAL_PADDING
    LEGEND_START_Y = BORDER_INSET + INTERNAL_PADDING
        

    # Hard code legend details with today's date as the first element

    today_date = datetime.now().strftime("%Y-%m-%d")

    title_text = json_data.get('title', '').upper()
    subtitle_text = json_data.get('subtitle', '')
    combined_title = f"{title_text} - {subtitle_text}" if subtitle_text else title_text
    print(combined_title)

    # Load the SVG file and extract the time estimate
    nd1 = NextDraw()
    nd1.plot_setup(svg_file_path)
    nd1.options.preview = True
    nd1.options.report_time = True
    nd1.options.model = 9 ## https://bantam.tools/nd_py/#model
    nd1.options.pen_rate_lower = 10
    nd1.options.pen_rate_upper = 10
    nd1.options.speed_pendown = 30
    nd1.options.speed_penup = 50
    nd1.plot_run()

    time_estimate_seconds = nd1.time_estimate
    hours, remainder = divmod(time_estimate_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours > 0:
        time_estimate = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
    else:
        time_estimate = f"{int(minutes)}m {int(seconds)}s"

    # Convert pen travel distance from meters to feet
    distance_pendown_m = nd1.distance_pendown
    distance_pendown_ft = distance_pendown_m * 3.28084

    legend_details = [
        {'name': 'Date', 'detail': today_date},
        {'name': 'Project', 'detail': combined_title},
        {'name': 'Draw Time', 'detail': f"{time_estimate}"},
        {'name': 'Pen Travel Distance', 'detail': f"{distance_pendown_ft:.1f} ft / {distance_pendown_m:.1f} m"},
        {'name': 'Designed By', 'detail': 'Drawscape Inc.'},
        {'name': 'Website', 'detail': 'https://drawscape.io'},
    ]
    

    # Start SVG content with XML declaration and dimensions with viewBox
    svg_content = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
    svg_content += f'<svg width="{DOCUMENT_WIDTH}mm" height="{DOCUMENT_HEIGHT}mm" viewBox="0 0 {DOCUMENT_WIDTH} {DOCUMENT_HEIGHT}" xmlns="http://www.w3.org/2000/svg">\n'
        
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
    svg_content += f'    <title>Legend</title>\n'
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

    # Close the SVG tag
    svg_content += '</svg>\n'

    

    return svg_content