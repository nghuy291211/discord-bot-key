import discord
from discord.ext import commands
import random
import string
from datetime import timedelta
import threading
import os
from flask import Flask, render_template_string, request

# --- CẤU HÌNH DISCORD BOT ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

bot_is_sleeping = False
active_keys = set() 

OWNER_ID = 000000000000000000  # Thay ID của bạn vào đây
CUSTOM_GET_KEY_URL = "http://localhost:5000" 

@bot.event
async def on_ready():
    print(f"Bot đã đăng nhập thành công: {bot.user}")

# --- CẤU HÌNH WEB SERVER (FLASK) ---
app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Get Key VIP - NGHUYDIY</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #0f172a; color: #fff; text-align: center; padding-top: 80px; }
        .container { background: #1e293b; padding: 40px; border-radius: 12px; display: inline-block; box-shadow: 0 4px 15px rgba(0,0,0,0.6); width: 420px; }
        .key-box { background: #334155; padding: 20px; border-radius: 8px; cursor: pointer; border: 2px dashed #38bdf8; margin-top: 15px; transition: 0.2s; }
        .key-box:hover { background: #475569; }
        code { color: #facc15; font-size: 26px; font-weight: bold; font-family: monospace; display: block; margin-top: 5px; }
    </style>
</head>
<body>
    <div class="container" id="box">
        <h2>NHẬN KEY VIP</h2>
        <p style="color: #38bdf8; font-weight: bold;">Bấm vào ô dưới để sao chép key:</p>
        
        <div class="key-box" onclick="copyKey('{{ key }}')">
            <span style="font-size: 13px; color: #cbd5e1;">BẤM ĐỂ COPY</span>
            <code>{{ key }}</code>
        </div>
    </div>

    <script>
        function copyKey(text) {
            navigator.clipboard.writeText(text).then(function() {
                // Thử đóng tab, nếu trình duyệt chặn sẽ tự động reset về giao diện thông báo thành công
                window.close();
                document.getElementById("box").innerHTML = `
                    <h2 style='color:#22c55e;'>Đã copy Key thành công!</h2>
                    <p style='color:#cbd5e1;'>Bạn có thể tắt tab này hoặc lấy link mới từ Discord.</p>
                `;
            }, function(err) {
                alert('Không thể tự copy, vui lòng sao chép thủ công!');
            });
        }
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    chars = string.ascii_uppercase + string.digits
    random_str = ''.join(random.choice(chars) for _ in range(8))
    key = f"NGHUYDIY-{random_str}"
    active_keys.add(key)
    return render_template_string(HTML_TEMPLATE, key=key)

def run_web():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# --- CÁC LỆNH BOT ---

@bot.command(name="getkey")
async def getkey(ctx):
    if bot_is_sleeping: return
    await ctx.send(f"🔗 {ctx.author.mention}, lấy key tại đây:\n{CUSTOM_GET_KEY_URL}")

@bot.command()
async def verify(ctx, user_key: str):
    if bot_is_sleeping: return
    
    if user_key in active_keys:
        role = discord.utils.get(ctx.guild.roles, name="VIP")
        if role:
            await ctx.author.add_roles(role)
            await ctx.send(f"🎉 {ctx.author.mention} đã xác thực thành công quyền `{role.name}`!")
            active_keys.remove(user_key)
        else:
            await ctx.send("❌ Server chưa tạo Role tên là `VIP`.")
    else:
        await ctx.send("❌ Key không hợp lệ hoặc đã được sử dụng!")

@bot.command()
@commands.has_permissions(administrator=True)
async def sleep(ctx):
    global bot_is_sleeping
    bot_is_sleeping = True
    await ctx.send("💤 Bot đã ngủ!")

@bot.command()
@commands.has_permissions(administrator=True)
async def wakeup(ctx):
    global bot_is_sleeping
    bot_is_sleeping = False
    await ctx.send("☀️ Bot đã thức dậy!")

# --- KHỞI CHẠY ---
if __name__ == "__main__":
    web_thread = threading.Thread(target=run_web)
    web_thread.daemon = True
    web_thread.start()
    
    bot.run("YOUR_BOT_TOKEN")
