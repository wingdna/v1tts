from flask import Flask, request, Response
from flask_cors import CORS
import edge_tts
import asyncio

app = Flask(__name__)
CORS(app)

# 将异步合成逻辑独立出来
async def text_to_speech_logic(text, voice):
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
        # 核心修复：在同步 Flask 路由中启动一个全新的事件循环
        loop = asyncio.new_loop()
        asyncio.set_event_loop(loop)
        audio_content = loop.run_until_complete(text_to_speech_logic(text, voice))
        loop.close()
        
        return Response(
            audio_content,
            mimetype='audio/mpeg',
            headers={
                "Content-Disposition": "inline",
                "Content-Length": str(len(audio_content))
            }
        )
    except Exception as e:
        return f"TTS Error: {str(e)}", 500

# 这一行对 Vercel 识别入口至关重要
app = app
