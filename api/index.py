from flask import Flask, request, Response
from flask_cors import CORS
import edge_tts
import asyncio

app = Flask(__name__)
CORS(app)

async def get_audio_data(text, voice):
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
        # 使用 asyncio.run 确保在同步 Flask 中运行异步任务
        loop = asyncio.new_loop()
        asyncio.set_event_loop(loop)
        audio_content = loop.run_until_complete(get_audio_data(text, voice))
        loop.close()
        
        return Response(
            audio_content,
            mimetype='audio/mpeg',
            headers={"Content-Disposition": "inline"}
        )
    except Exception as e:
        return f"Internal Error: {str(e)}", 500

# 必须显式导出 app
app = app
