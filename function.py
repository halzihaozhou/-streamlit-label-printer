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


import streamlit.components.v1 as components
import json


def render_qz_html(base64_pdf: str, printer_name: str = "AM-243-BT"):
    base64_clean = base64_pdf.replace('\n', '')
    base64_pdf_js = json.dumps(base64_clean)

    html_code = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Print with QZ Tray</title>
        <script src="https://cdn.jsdelivr.net/npm/rsvp@4.8.5/dist/rsvp.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/qz-tray@2.1.0/qz-tray.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/js-sha256@0.9.0/build/sha256.min.js"></script>
    </head>
    <body>
        <h4>正在连接 QZ Tray...</h4>
        <button onclick="sendToPrinter()">🖨️ 打印标签</button>
        <script>
        const base64_pdf = {base64_pdf_js};

        // ✅ 正确 sha256 用法
        qz.security.setSignaturePromise(function(toSign) {{
            return Promise.resolve(sha256(toSign));
        }});

        window.onload = async function() {{
            if (typeof qz === 'undefined') {{
                alert("❌ QZ Tray JS 未加载，请检查网络或关闭广告插件");
                return;
            }}
            try {{
                await qz.websocket.connect();
                alert("✅ QZ Tray 已连接");
            }} catch (e) {{
                alert("⚠️ 无法连接 QZ Tray，请确保客户端已启动: " + e);
            }}
        }}

        async function sendToPrinter() {{
            console.log("✅ base64_pdf typeof:", typeof base64_pdf);
            console.log("✅ base64_pdf preview:", base64_pdf?.substring(0, 100));

            if (!qz.websocket.isActive()) {{
                alert("请先连接 QZ Tray");
                return;
            }}

            if (!base64_pdf || typeof base64_pdf !== 'string') {{
                alert("❌ base64_pdf 是空的或不是字符串！");
                return;
            }}

            try {{
                const config = qz.configs.create("{printer_name}", {{
                    copies: 1,
                    scaleContent: true,
                    rasterize: false,
                    altPrinting: false,
                    legacy: true  // ⛔ 强制跳过兼容性 split 检查
                }});
                await qz.print(config, [{{
                    type: 'pdf',
                    format: 'base64',
                    data: base64_pdf
                }}]);
                alert("✅ 打印成功！");
            }} catch (err) {{
                alert("打印失败: " + err);
                console.error(err);
            }}
        }}
        </script>
    </body>
    </html>
    '''

    components.html(html_code, height=400)


if "__name__" == "__main__":
    generate_barcode_pdf("123456789012", "Sample Description")
