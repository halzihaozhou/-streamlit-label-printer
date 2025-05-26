import streamlit as st
from barcode.codex import Code128
from barcode.writer import ImageWriter
from PIL import Image, ImageDraw, ImageFont
import io


def generate_barcode_pdf(label, description, dpi=300):
    # Calculate dimensions for 2.25 x 1.25 inches at the given DPI
    label_width_inch = 2
    label_height_inch = 1
    width_px = int(label_width_inch * dpi)
    height_px = int(label_height_inch * dpi)

    # Generate the barcode
    options = {
        "module_width": 0.2,
        "module_height": 5,
        "font_size": 4,
        "text_distance": 2
    }
    barcode = Code128(label, writer=ImageWriter())
    barcode_buffer = io.BytesIO()
    barcode.write(barcode_buffer, options=options)
    barcode_buffer.seek(0)

    # Load the barcode image
    barcode_image = Image.open(barcode_buffer)

    # Resize the barcode image to fit within the specified width while maintaining aspect ratio
    barcode_width, barcode_height = barcode_image.size
    scale_factor = width_px / barcode_width
    barcode_image = barcode_image.resize(
        (width_px, int(barcode_height * scale_factor)), Image.LANCZOS)

    # Create the final image with the correct label size
    final_image = Image.new('RGB', (width_px, height_px), 'white')

    # Paste the barcode image onto the final image, centered vertically
    barcode_y = (height_px - barcode_image.height) // 2
    final_image.paste(barcode_image, (0, barcode_y))

    # Prepare to draw the label and description
    draw = ImageDraw.Draw(final_image)

    # Load a Unicode font
    font_path = "DejaVuSans-Bold.ttf"  # Ensure this path is correct
    try:
        font = ImageFont.truetype(font_path, int(10 * scale_factor))
    except IOError:
        st.error(f"Font file not found: {font_path}")
        return None

    # Draw the description
    description_y = barcode_y + barcode_image.height + 2
    draw.text((10, description_y), description, font=font, fill="black")

    # Save the final image to a buffer
    output_buffer = io.BytesIO()
    pdf_image = final_image.convert("RGB")
    pdf_image.save(output_buffer, format="PDF", resolution=dpi)
    output_buffer.seek(0)

    return output_buffer

if "__name__" == "__main__":
    generate_barcode_pdf("123456789012", "Sample Description")
