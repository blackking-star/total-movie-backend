import os
import asyncio

# Fix for Python event loop issue with Pyrogram
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

from quart import Quart, jsonify, request
from quart_cors import cors
from pyrogram import Client

app = Quart(__name__)
app = cors(app, allow_origin="*")

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

bot = Client(
    "total_movie_stream_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.route('/')
async def home():
    return jsonify({"status": "Server is running smoothly!"})

@app.route('/stream/<string:channel>/<int:msg_id>', methods=['GET'])
async def stream_video(channel, msg_id):
    try:
        if not bot.is_connected:
            await bot.start()
        
        message = await bot.get_messages(channel, msg_id)
        if not message or not message.video:
            return jsonify({"error": "Video file not found in channel"}), 404
            
        video = message.video
        file_size = video.file_size
        
        async def generate():
            async for chunk in bot.stream_media(message):
                yield chunk

        headers = {
            'Content-Type': video.mime_type or 'video/mp4',
            'Accept-Ranges': 'bytes',
            'Content-Length': str(file_size),
            'Access-Control-Allow-Origin': '*'
        }
        
        return await generate(), 200, headers
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
