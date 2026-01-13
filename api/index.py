from flask import Flask, request, Response
from flask_cors import CORS
import edge_tts
import asyncio

# 1. 必须命名为 app，且不能被包含在 if __name__ == "__main__": 之外
app = Flask(__name__)
CORS(app)

# 异步逻辑保持独立
async def get_audio(text, voice):
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
        # 在同步 Flask 中运行异步 edge-tts
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        audio_content = new_loop.run_until_complete(get_audio(text, voice))
        new_loop.close()
        
        return Response(
            audio_content,
            mimetype='audio/mpeg',
            headers={"Content-Disposition": "inline"}
        )
    except Exception as e:
        return f"Runtime Error: {str(e)}", 500

# 2. 严禁添加 def handler() 函数，直接让 app 暴露在最外层
