import cv2
import numpy as np
from PIL import Image
import os

def svglines(image_path):
    # Read the image
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    # Apply edge detection
    edges = cv2.Canny(img, 100, 200)
    
    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    
    # Get image dimensions
    height, width = img.shape
    
    # Start SVG content
    svg_content = f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">\n'
    
    # Add paths for each contour
    for contour in contours:
        if len(contour) > 1:
            svg_content += '  <path d="M'
            for point in contour:
                print(point)
                x, y = point[0]
                svg_content += f'{x},{y} '
            svg_content += 'Z" fill="none" stroke="black" />\n'
    
    # Close SVG content
    svg_content += '</svg>'
    
    # Generate output file path
    output_dir = os.path.dirname(image_path)
    output_filename = os.path.splitext(os.path.basename(image_path))[0] + "_svg.svg"
    output_path = os.path.join(output_dir, output_filename)
    
    # Save SVG content to file
    with open(output_path, 'w') as f:
        f.write(svg_content)
    
    print(f"SVG saved to {output_path}")
    
    return output_path