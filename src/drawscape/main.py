#!/usr/bin/env python3

import sys
import os
import requests
from PIL import Image
from dotenv import load_dotenv
import argparse

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
    parser.add_argument('action', choices=['removebg', 'trim'], help='Action to perform')
    parser.add_argument('--image', required=True, help='Path to the image file')

    args = parser.parse_args()

    image_path = args.image

    try:
        if args.action == 'removebg':
            remove_background(image_path)
        elif args.action == 'trim':
            trim(image_path)
            
    except TypeError as e:
        print(f"Error: {e}. Please provide a valid input file path.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()