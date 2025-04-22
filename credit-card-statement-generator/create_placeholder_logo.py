from PIL import Image, ImageDraw

# Create a blank image with white background
img = Image.new('RGB', (200, 100), 'white')
draw = ImageDraw.Draw(img)

# Save as logo.png in static/images
img.save('static/images/logo.png')