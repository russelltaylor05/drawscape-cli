import os
import xml.etree.ElementTree as ET

def convert_svg(input_svg_path):
    print(f"Converting SVG file: {input_svg_path}")

    # Parse the SVG file
    tree = ET.parse(input_svg_path)
    root = tree.getroot()

    # Function to convert pixels to mm (assuming 96 DPI)
    def px_to_mm(px):
        return float(px) * 0.26458333

    # Handle SVG element manually
    if 'viewBox' in root.attrib:
        viewBox = root.attrib['viewBox'].split()
        viewBox = [f"{px_to_mm(float(val)):.3f}" for val in viewBox]
        root.attrib['viewBox'] = ' '.join(viewBox)

    for attr in ['width', 'height']:
        if attr in root.attrib:
            root.attrib[attr] = f"{px_to_mm(float(root.attrib[attr].rstrip('px'))):.3f}mm"

    # Preserve enable-background attribute if present
    if 'enable-background' in root.attrib:
        enable_background = root.attrib['enable-background'].split()
        if len(enable_background) > 1:
            enable_background = ['new'] + [f"{px_to_mm(float(val)):.3f}" for val in enable_background[1:]]
            root.attrib['enable-background'] = ' '.join(enable_background)

    # Convert all coordinate and size values for child elements
    for elem in root.iter():
        if elem != root:  # Skip the root SVG element
            for attr in ['x', 'y', 'x1', 'y1', 'x2', 'y2', 'cx', 'cy', 'r', 'rx', 'ry', 'width', 'height']:
                if attr in elem.attrib:
                    elem.attrib[attr] = f"{px_to_mm(float(elem.attrib[attr])):.3f}"
            
            # Convert stroke-width
            if 'stroke-width' in elem.attrib:
                elem.attrib['stroke-width'] = f"{px_to_mm(float(elem.attrib['stroke-width'])):.3f}"

            # Convert path data
            if elem.tag.endswith('path') and 'd' in elem.attrib:
                d = elem.attrib['d']
                new_d = []
                for cmd in d.split():
                    try:
                        new_d.append(f"{px_to_mm(float(cmd)):.3f}")
                    except ValueError:
                        new_d.append(cmd)
                elem.attrib['d'] = ' '.join(new_d)

            # Convert polygon and polyline points
            if elem.tag.endswith(('polygon', 'polyline')) and 'points' in elem.attrib:
                points = elem.attrib['points'].split()
                new_points = []
                for point in points:
                    x, y = point.split(',')
                    new_points.append(f"{px_to_mm(float(x)):.3f},{px_to_mm(float(y)):.3f}")
                elem.attrib['points'] = ' '.join(new_points)

    # Generate output file path
    output_dir = os.path.dirname(input_svg_path)
    output_filename = os.path.splitext(os.path.basename(input_svg_path))[0] + "_converted.svg"
    output_path = os.path.join(output_dir, output_filename)

    # Write the modified SVG to the output file
    tree.write(output_path, encoding='utf-8', xml_declaration=True)

    print(f"Converted SVG saved to {output_path}")
    return output_path