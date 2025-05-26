import streamlit.components.v1 as components
import json
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont


def generate_barcode_image(tracking_number: str, description: str) -> BytesIO:
    width, height = 400, 200
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 20)
    except Exception:
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


def render_qz_image_html(base64_img: str):
    base64_clean = base64_img.replace('\n', '')
    base64_img_js = json.dumps(base64_clean)

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Print with QZ Tray</title>
        <script src="https://cdn.jsdelivr.net/npm/rsvp@4.8.5/dist/rsvp.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/qz-tray@2.1.0/qz-tray.js"></script>
    </head>
    <body>
        <h4>选择打印机并打印图像：</h4>
        <select id="printerSelect">
            <option>🔄 加载中...</option>
        </select>
        <br><br>
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

                // 加载打印机列表
                const printers = await qz.printers.find();
                const select = document.getElementById("printerSelect");
                select.innerHTML = "";
                printers.forEach(name => {{
                    const option = document.createElement("option");
                    option.textContent = name;
                    select.appendChild(option);
                }});
            }} catch (e) {{
                alert("⚠️ 无法连接 QZ Tray: " + e);
            }}
        }};

        async function sendToPrinter() {{
            const printerName = document.getElementById("printerSelect").value;

            if (!qz.websocket.isActive()) {{
                alert("请先连接 QZ Tray");
                return;
            }}

            if (!base64_img || typeof base64_img !== 'string') {{
                alert("❌ base64_img 是空的或不是字符串！");
                return;
            }}

            try {{
                const config = qz.configs.create(printerName, {{
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

    components.html(html_code, height=450)
