from flask import Flask, request, Response
from flask_cors import CORS
import edge_tts
import asyncio

app = Flask(__name__)
CORS(app)

async def run_tts(text, voice):
    communicate = edge_tts.Communicate(text, voice)
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    return audio_data

@app.route('/api/tts')
def tts():
    text = request.args.get('text', 'hello')
    voice = request.args.get('voice', 'zh-CN-XiaoxiaoNeural')
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        # 这里是同步等待异步完成
        audio_content = loop.run_until_complete(run_tts(text, voice))
        loop.close()
        
        return Response(audio_content, mimetype='audio/mpeg')
    except Exception as e:
        return f"Error: {str(e)}", 500
