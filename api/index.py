from flask import Flask, request, Response
from flask_cors import CORS
import edge_tts
import asyncio

app = Flask(__name__)
CORS(app)

# 纯异步逻辑，不直接暴露给路由
async def _do_tts(text, voice):
    communicate = edge_tts.Communicate(text, voice)
    audio_content = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_content += chunk["data"]
    return audio_content

@app.route('/api/tts')
def tts():  # 注意：这里去掉了 async 关键字
    text = request.args.get('text', 'hello')
    voice = request.args.get('voice', 'zh-CN-XiaoxiaoNeural')
    
    try:
        # 强制在同步 Flask 线程中开启新的事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        data = loop.run_until_complete(_do_tts(text, voice))
        loop.close()
        
        return Response(data, mimetype='audio/mpeg')
    except Exception as e:
        return f"Error: {str(e)}", 500

# 确保没有任何 handler 函数或 app = app
