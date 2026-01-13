import asyncio
from flask import Flask, request, Response
from flask_cors import CORS
import edge_tts

# 必须叫 app，且不要添加任何 handler 函数
app = Flask(__name__)
CORS(app)

async def generate(text, voice):
    communicate = edge_tts.Communicate(text, voice)
    data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            data += chunk["data"]
    return data

@app.route('/api/tts')
def tts():
    text = request.args.get('text', 'hello')
    voice = request.args.get('voice', 'zh-CN-XiaoxiaoNeural')
    
    # 强制在同步环境运行异步任务
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        audio_content = loop.run_until_complete(generate(text, voice))
        return Response(audio_content, mimetype='audio/mpeg')
    finally:
        loop.close()

# 严禁在下方添加 app = app 或任何 if __name__ == "__main__"
