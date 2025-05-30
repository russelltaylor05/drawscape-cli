#!/usr/bin/env python3

import os
import requests
from PIL import Image
from dotenv import load_dotenv
import argparse

from .svg_utils import svglines
from .blueprint import blueprint
from .blueprint_label import blueprint_label
from .optimize import optimize_svg
from .optimize_tabloid import optimize_tabloid
from .details import parse_svg_file
from .convert import convert_svg
from .shipping import create_shipping_label
from .split import split_svg

load_dotenv()

# not needed right now since the removebg had an api option for thi
def trim(image_path):
    img = Image.open(image_path)
    img = img.convert("RGBA")
    # Get the bounding box of the non-transparent area using the alpha channel
    bbox = img.getbbox()
    if (bbox):
        trimmed_img = img.crop(bbox)
        output_path = os.path.splitext(image_path)[0] + "_trimmed.png"
        trimmed_img.save(output_path)
        print(f"Image saved to {output_path}")
    else:
        print("No non-transparent area found.")


def remove_background(image_path):
    output_path = os.path.splitext(image_path)[0] + "_removebg.png"
    response = requests.post(
        'https://api.remove.bg/v1.0/removebg',
        files={'image_file': open(image_path, 'rb')},
        data={'size': 'auto', 'crop': 'true'},
        headers={'X-Api-Key': os.getenv('REMOVEBG_KEY')},
    )
    if response.status_code == requests.codes.ok:
        with open(output_path, 'wb') as out:
            out.write(response.content)
        print(f"Image saved to {output_path}")
    else:
        print("Error:", response.status_code, response.text)
    return output_path

def main():
    parser = argparse.ArgumentParser(description='Image processing tool')
    parser.add_argument('action', choices=['removebg', 'trim', 'svglines', 'blueprint', 'blueprint-label', 'optimize', 'optimize-tabloid', 'svgdetails', 'convert', 'shipping', 'vase', 'split'], help='Action to perform')
    parser.add_argument('--image', help='Path to the image file')
    parser.add_argument('--json', help='Path to the JSON file for blueprint or shipping action')
    parser.add_argument('--svg', help='Path to the SVG file for blueprint-label action')
    parser.add_argument('--output', help='Output path for shipping label')
    parser.add_argument('--size', choices=['a4', 'a3', 'letter', 'tabloid'], help='Size for blueprint action (optional)')
    parser.add_argument('--orientation', choices=['portrait', 'landscape'], default='portrait', help='Orientation for blueprint action (optional)')

    args = parser.parse_args()

    try:
        if args.action == 'removebg':
            if not args.image:
                raise ValueError("--image argument is required for removebg action")
            remove_background(args.image)
        elif args.action == 'trim':
            if not args.image:
                raise ValueError("--image argument is required for trim action")
            trim(args.image)
        elif args.action == 'svglines':
            if not args.image:
                raise ValueError("--image argument is required for svglines action")
            svglines(args.image)
        elif args.action == 'blueprint':
            if not args.json:
                raise ValueError("--json argument is required for blueprint action")
            blueprint(args.json, args.size, args.orientation)
        elif args.action == 'blueprint-label':
            if not args.json:
                raise ValueError("--json argument is required for blueprint-label action")
            blueprint_label(args.json, args.svg)
        elif args.action == 'optimize':
            if not args.image:
                raise ValueError("--image argument is required for optimize action")
            optimize_svg(args.image)
        elif args.action == 'optimize-tabloid':
            if not args.image:
                raise ValueError("--image argument is required for optimize-tabloid action")
            optimize_tabloid(args.image)
        elif args.action == 'svgdetails':
            if not args.image:
                raise ValueError("--image argument is required for svgdetails action")
            details = parse_svg_file(args.image)
            if details:
                print("SVG Details:")
                print(f"Width: {details['width']}")
                print(f"Height: {details['height']}")
                print(f"ViewBox: {details['viewBox']}")
                print(f"Bounding Box: {details['bounding_box']}")
                print(f"Content length: {len(details['content'])} characters")
            else:
                print("Failed to parse SVG file.")
        elif args.action == 'convert':
            if not args.image:
                raise ValueError("--image argument is required for convert action")
            convert_svg(args.image)
        elif args.action == 'shipping':
            if not args.json:
                raise ValueError("--json argument is required for shipping action")
            output_path = args.output if args.output else 'shipping_label.svg'
            create_shipping_label(args.json, output_path)
        elif args.action == 'vase':
            print_vase()
        elif args.action == 'split':
            if not args.image:
                raise ValueError("--image argument is required for split action")
            split_svg(args.image)
            
    except TypeError as e:
        print(f"Error: {e}. Please provide a valid input file path.")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()