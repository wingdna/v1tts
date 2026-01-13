from flask import Flask, request, Response
from flask_cors import CORS
import edge_tts
import asyncio

# 必须叫 app，且直接暴露在最外层
app = Flask(__name__)
CORS(app)

async def _generate(text, voice):
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
        return "Missing text parameter", 400

    try:
        # 使用全新的事件循环来运行异步合成任务
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        audio_content = loop.run_until_complete(_generate(text, voice))
        loop.close()
        
        return Response(
            audio_content,
            mimetype='audio/mpeg'
        )
    except Exception as e:
        return f"Error: {str(e)}", 500

# 注意：这里千万不要写 def handler(request) 或者 app = app
