import streamlit.components.v1 as components
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import json


def generate_barcode_image(tracking_number: str, description: str) -> BytesIO:
    width, height = 400, 200
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 20)
    except Exception as e:
        print("Font load error:", e)
        font = ImageFont.load_default()

    draw.text((10, 30),
              f"Tracking #: {tracking_number}",
              font=font,
              fill='black')
    draw.text((10, 100), f"Desc: {description}", font=font, fill='black')

    buffer = BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer


def render_qz_image_html(base64_img: str, printer_name: str = "AM-243-BT"):
    base64_clean = base64_img.replace('\n', '')
    base64_img_js = json.dumps(base64_clean)  # 确保是合法 JS 字符串

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Print Image with QZ Tray</title>
        <script src="https://cdn.jsdelivr.net/npm/rsvp@4.8.5/dist/rsvp.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/qz-tray@2.1.0/qz-tray.js"></script>
    </head>
    <body>
        <h4>正在连接 QZ Tray...</h4>
        <button onclick="sendToPrinter()">🖨️ 打印图像</button>
        <script>
        const base64_img = {base64_img_js};

        qz.api.setPromiseType(function promise(resolver) {{
            return new RSVP.Promise(resolver);
        }});

        window.onerror = function(message, source, lineno, colno, error) {{
            console.warn("QZ Tray Error:", message);
            return true;
        }};

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
        }};

        async function sendToPrinter() {{
            console.log("🔍 打印机名: {printer_name}");
            if (!qz.websocket.isActive()) {{
                alert("请先连接 QZ Tray");
                return;
            }}

            if (!base64_img || typeof base64_img !== 'string') {{
                alert("❌ base64_img 是空的或不是字符串！");
                return;
            }}

            try {{
                const config = qz.configs.create("{printer_name}", {{
                    copies: 1,
                    rasterize: false,
                    altPrinting: false
                }});
                await qz.print(config, [{{
                    type: 'image',
                    format: 'base64',
                    data: base64_img
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
    """

    components.html(html_code, height=400)
