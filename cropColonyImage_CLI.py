import os
from PIL import Image, ImageDraw

def crop_circle_from_images(input_folder, output_folder):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.jpg', '.jpeg')):
            # Load the image
            input_image_path = os.path.join(input_folder, filename)
            image = Image.open(input_image_path)

            # Define the crop area
            crop_box = (0, 200, 2800, 3000)  # (left, upper, right, lower)
            cropped_image = image.crop(crop_box)

            # Create a mask for the circular area
            mask = Image.new('L', cropped_image.size, 0)  # Create a black mask
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, 2800, 2800), fill=255)  # Draw a white circle

            # Apply the mask to create transparency
            circular_image = Image.new('RGBA', cropped_image.size)
            circular_image.paste(cropped_image, (0, 0), mask)

            # Save the result with compression
            new_size = (1000, 1000)
            output_image_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}_circular.png")
            circular_image = circular_image.resize(new_size)
            circular_image.save(output_image_path, 'PNG', optimized=True)
            print(f"Processed {filename} and saved as {output_image_path}")

# Example usage with compression level set to 6
input_folder = '.'  # Replace with your input folder path
output_folder = 'output'  # Replace with your output folder path
crop_circle_from_images(input_folder, output_folder)