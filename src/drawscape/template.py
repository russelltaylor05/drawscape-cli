import os

def template():
    # Set SVG dimensions in mm
    svg_width_mm = 210
    svg_height_mm = 297

    # Calculate inset rectangle dimensions
    inset = 8
    rect_width_mm = svg_width_mm - (2 * inset)
    rect_height_mm = svg_height_mm - (2 * inset)

    # Start SVG content with dimensions in mm
    svg_content = f'<svg width="{svg_width_mm}mm" height="{svg_height_mm}mm" xmlns="http://www.w3.org/2000/svg">\n'
    
    # Add a 1pt border rectangle inset 10mm from the edges
    svg_content += f'  <rect x="{inset}mm" y="{inset}mm" width="{rect_width_mm}mm" height="{rect_height_mm}mm" fill="none" stroke="black" stroke-width="1pt" />\n'
    
    # Close SVG content
    svg_content += '</svg>'
    
    # Generate output file path
    output_dir = os.getcwd()  # Current working directory
    output_filename = "template_210x297mm_inset.svg"
    output_path = os.path.join(output_dir, output_filename)
    
    # Save SVG content to file
    with open(output_path, 'w') as f:
        f.write(svg_content)
    
    print(f"SVG template with inset border saved to {output_path}")
    
    return output_path