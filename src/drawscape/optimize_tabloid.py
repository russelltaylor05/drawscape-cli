import os
import subprocess
import xml.etree.ElementTree as ET
from .blueprint import PAPER_SIZES

def optimize_tabloid(input_svg_path):
    """
    Optimize an SVG file specifically for tabloid paper size.
    
    Args:
        input_svg_path (str): Path to the input SVG file
        
    Returns:
        str: Path to the optimized SVG file
    """
    print(f"Optimizing SVG file for tabloid size: {input_svg_path}")

    # Get tabloid dimensions
    DOCUMENT_WIDTH, DOCUMENT_HEIGHT = PAPER_SIZES['tabloid']
    
    # Generate output file path
    output_dir = os.path.dirname(input_svg_path)
    output_filename = os.path.splitext(os.path.basename(input_svg_path))[0] + "_tabloid_optimized.svg"
    output_path = os.path.join(output_dir, output_filename)

    # Construct the vpype command with tabloid-specific optimizations
    vpype_command = [
        "vpype",
        "read",
        input_svg_path,
        "linemerge",  # Merge lines that are close to each other
        "linesimplify",  # Simplify complex paths
        "linesort",   # Sort lines to minimize pen travel
        "scaleto",   # Scale to fit within tabloid dimensions
        f"{DOCUMENT_WIDTH}mm",
        f"{DOCUMENT_HEIGHT}mm",
        "layout",    # Center the drawing
        "--fit-to-margins",
        "2cm",      # Add 2cm margins
        "tabloid",  # Specify tabloid layout
        "write",    # Write the output
        "--page-size",
        "tabloid",  # Specify tabloid page size
        "--center", # Center the drawing
        output_path
    ]

    print(vpype_command)

    # Execute the vpype command
    try:
        subprocess.run(vpype_command, check=True, capture_output=True, text=True)
        print(f"Optimized SVG saved to {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error optimizing SVG: {e}")
        print(f"Command output: {e.output}")
        return None

    return output_path 