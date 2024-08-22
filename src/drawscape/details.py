import os
import xml.etree.ElementTree as ET
import re

def parse_svg_file(svg_file_path):
    """
    Parse an SVG file and extract its details.

    Args:
        svg_file_path (str): Path to the SVG file.

    Returns:
        dict: A dictionary containing the SVG details:
            - 'width': Width of the SVG
            - 'height': Height of the SVG
            - 'viewBox': ViewBox of the SVG
            - 'bounding_box': Bounding box of the SVG content
            - 'content': SVG content as a string (excluding outer <svg> tag)
    """
    if not svg_file_path:
        print("Error: No SVG file path specified")
        return None

    svg_file_path = os.path.expanduser(svg_file_path)
    
    if not os.path.exists(svg_file_path):
        print(f"Error: SVG file not found at {svg_file_path}")
        return None

    try:
        tree = ET.parse(svg_file_path)
        root = tree.getroot()

        # Remove the default namespace if present
        ns = re.match(r'\{.*\}', root.tag)
        if ns:
            ns = ns.group(0)
            for elem in root.iter():
                elem.tag = elem.tag.replace(ns, '')

        # Extract width and height
        width = root.get('width', '0')
        height = root.get('height', '0')

        # Convert width and height to float, removing any units
        width_value = float(re.sub(r'[^0-9.]', '', width))
        height_value = float(re.sub(r'[^0-9.]', '', height))

        # Convert all units to mm
        if 'cm' in width.lower():
            width_value *= 10  # Convert cm to mm
        elif 'in' in width.lower():
            width_value *= 25.4  # Convert inches to mm
        elif 'px' in width.lower():
            width_value /= 3.7795275591  # Convert pixels to mm (96 DPI)

        if 'cm' in height.lower():
            height_value *= 10  # Convert cm to mm
        elif 'in' in height.lower():
            height_value *= 25.4  # Convert inches to mm
        elif 'px' in height.lower():
            height_value /= 3.7795275591  # Convert pixels to mm (96 DPI)

        # Round to 2 decimal places for practical use
        width_value = round(width_value, 2)
        height_value = round(height_value, 2)

        # Extract viewBox
        viewBox = root.get('viewBox')

        # Calculate bounding box
        bounding_box = calculate_bounding_box(root)

        # Get SVG content (excluding outer <svg> tag)
        svg_content = ''.join(ET.tostring(child, encoding='unicode') for child in root)

        return {
            'width': width_value,
            'height': height_value,
            'viewBox': viewBox,
            'bounding_box': bounding_box,
            'content': svg_content.strip()
        }

    except ET.ParseError as e:
        print(f"Error parsing SVG file: {e}")
        return None

def calculate_bounding_box(root):
    """
    Calculate the bounding box of all elements in the SVG.

    Args:
        root (Element): The root element of the SVG.

    Returns:
        dict: A dictionary containing the bounding box information:
            - 'min_x': Minimum x-coordinate
            - 'min_y': Minimum y-coordinate
            - 'max_x': Maximum x-coordinate
            - 'max_y': Maximum y-coordinate
    """
    min_x, min_y = float('inf'), float('inf')
    max_x, max_y = float('-inf'), float('-inf')

    for elem in root.iter():
        if 'x' in elem.attrib and 'y' in elem.attrib:
            x = float(elem.attrib['x'])
            y = float(elem.attrib['y'])
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x)
            max_y = max(max_y, y)
        elif 'points' in elem.attrib:
            points = elem.attrib['points'].split()
            for point in points:
                x, y = map(float, point.split(','))
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
        elif 'd' in elem.attrib:
            # For path elements, we'd need a more complex parsing of the 'd' attribute
            # This is a simplified approach that may not be accurate for all paths
            commands = re.findall(r'([MmLlHhVvCcSsQqTtAaZz])', elem.attrib['d'])
            coords = re.findall(r'(-?\d+\.?\d*)', elem.attrib['d'])
            coords = list(map(float, coords))
            for i in range(0, len(coords), 2):
                if i+1 < len(coords):
                    x, y = coords[i], coords[i+1]
                    min_x = min(min_x, x)
                    min_y = min(min_y, y)
                    max_x = max(max_x, x)
                    max_y = max(max_y, y)

    return {
        'min_x': min_x,
        'min_y': min_y,
        'max_x': max_x,
        'max_y': max_y
    }

# Example usage
if __name__ == "__main__":
    svg_file_path = "path/to/your/svg/file.svg"
    svg_details = parse_svg_file(svg_file_path)
    if svg_details:
        print("SVG Details:")
        print(f"Width: {svg_details['width']}")
        print(f"Height: {svg_details['height']}")
        print(f"ViewBox: {svg_details['viewBox']}")
        print(f"Bounding Box: {svg_details['bounding_box']}")
        print(f"Content length: {len(svg_details['content'])} characters")