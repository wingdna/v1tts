from flask import Flask, request, Response
from flask_cors import CORS
import edge_tts
import asyncio

# 必须命名为 app，这是 Vercel 识别 Flask 的默认变量名
app = Flask(__name__)
CORS(app)

async def generate_audio_data(text, voice):
    communicate = edge_tts.Communicate(text, voice)
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    return audio_data

@app.route('/api/tts')
def tts():
    text = request.args.get('text')
    voice = request.args.get('voice', 'zh-CN-XiaoxiaoNeural')
    
    if not text:
        return "Error: Missing text parameter", 400

    try:
        # 在同步路由中手动管理事件循环，防止 Vercel 运行时冲突
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        audio_content = loop.run_until_complete(generate_audio_data(text, voice))
        loop.close()
        
        return Response(
            audio_content,
            mimetype='audio/mpeg',
            headers={"Content-Disposition": "inline"}
        )
    except Exception as e:
        return f"Service Error: {str(e)}", 500
