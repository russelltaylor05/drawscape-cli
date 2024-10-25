import xml.etree.ElementTree as ET
import re
import copy

def split_svg(svg_file_path):
    try:
        # Parse the SVG file
        tree = ET.parse(svg_file_path)
        root = tree.getroot()

        # Get viewBox and calculate middle point
        viewBox = root.get('viewBox')
        if not viewBox:
            raise ValueError("ViewBox is required for this operation")
        min_x, min_y, width, height = map(float, viewBox.split())
        mid_y = min_y + height / 2

        print(f"ViewBox: {viewBox}")
        print(f"Middle Y: {mid_y}")

        # Create new SVG roots for upper and lower halves
        upper_root = ET.Element('svg', root.attrib)
        lower_root = ET.Element('svg', root.attrib)

        # Function to extract y-coordinate from path data
        def extract_y_from_path(d):
            match = re.search(r'[Mm]\s*[-+]?[0-9]*\.?[0-9]+\s+([-+]?[0-9]*\.?[0-9]+)', d)
            return float(match.group(1)) if match else None

        # Function to determine y-coordinate of an element
        def get_y_coordinate(elem):
            if 'y' in elem.attrib:
                return float(elem.attrib['y'])
            elif elem.tag.endswith('path'):
                return extract_y_from_path(elem.get('d', ''))
            elif 'transform' in elem.attrib:
                transform = elem.get('transform')
                if 'translate' in transform:
                    match = re.search(r'translate\([^,]+,\s*([-+]?[0-9]*\.?[0-9]+)', transform)
                    if match:
                        return float(match.group(1))
            return None

        # Iterate through all elements and add to appropriate SVG
        for elem in root:
            y = get_y_coordinate(elem)
            if y is not None:
                if y < mid_y:
                    upper_root.append(copy.deepcopy(elem))
                else:
                    lower_root.append(copy.deepcopy(elem))
            else:
                # If y-coordinate can't be determined, add to both
                upper_root.append(copy.deepcopy(elem))
                lower_root.append(copy.deepcopy(elem))

        # Write the new SVG files
        base_name = svg_file_path.rsplit('.', 1)[0]
        upper_path = f"{base_name}_upper.svg"
        lower_path = f"{base_name}_lower.svg"

        ET.ElementTree(upper_root).write(upper_path, encoding="unicode", xml_declaration=True)
        ET.ElementTree(lower_root).write(lower_path, encoding="unicode", xml_declaration=True)

        print(f"Upper half saved to: {upper_path}")
        print(f"Lower half saved to: {lower_path}")

    except ET.ParseError:
        print(f"Error: Unable to parse the SVG file at {svg_file_path}")
    except FileNotFoundError:
        print(f"Error: File not found at {svg_file_path}")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")