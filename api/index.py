from flask import Flask, request, Response
from flask_cors import CORS
import edge_tts
import asyncio
import io

app = Flask(__name__)
CORS(app) # 开启跨域，允许你的前端页面访问

async def generate_audio(text, voice):
    communicate = edge_tts.Communicate(text, voice)
    # 使用流式传输
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            yield chunk["data"]

@app.route('/api/tts')
async def tts():
    text = request.args.get('text')
    voice = request.args.get('voice', 'zh-CN-XiaoxiaoNeural')
    
    if not text:
        return "Error: Missing 'text' parameter", 400

    # 返回音频流，浏览器会自动识别并播放
    return Response(
        generate_audio(text, voice),
        mimetype='audio/mpeg',
        headers={
            "Content-Disposition": "inline",
            "Cache-Control": "no-cache"
        }
    )

# Vercel 要求的入口
def handler(request):
    return app(request)