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
    
    for guild in bot.guilds:
        embed = discord.Embed(
            title="🟢 BOT ĐÃ KHỞI ĐỘNG THÀNH CÔNG!",
            description="Hệ thống xác thực Key VIP (NGHUYDIY-) dạng một lần đã sẵn sàng.",
            color=discord.Color.green()
        )
        embed.add_field(name="Lệnh cơ bản", value="Dùng `!help` hoặc `!getkey` để bắt đầu.", inline=False)
        
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                try:
                    await channel.send(embed=embed)
                except Exception as e:
                    print(f"Không thể gửi tin nhắn vào kênh {channel.name}: {e}")

# --- TÍNH NĂNG CHÀO MỪNG THÀNH VIÊN MỚI ---
@bot.event
async def on_member_join(member):
    if bot_is_sleeping:
        return
    
    target_channel = discord.utils.get(member.guild.text_channels, name="chao-mung")
    if not target_channel:
        target_channel = discord.utils.get(member.guild.text_channels, name="welcome")
    
    if not target_channel:
        for c in member.guild.text_channels:
            if c.permissions_for(member.guild.me).send_messages:
                target_channel = c
                break

    if target_channel:
        embed = discord.Embed(
            title="🎉 CHÀO MỪNG THÀNH VIÊN MỚI! 🎉",
            description=f"Xin chào {member.mention} đã đến với server **{member.guild.name}**!",
            color=discord.Color.gold()
        )
        embed.add_field(
            name="📌 Hướng dẫn nhanh:",
            value="• Gõ `!getkey` để lấy link tạo key dạng `NGHUYDIY-...` nhận quyền VIP.\n• Đọc kỹ nội quy để tránh bị phạt nhé!",
            inline=False
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Tổng thành viên hiện tại: {member.guild.member_count}")
        
        try:
            await target_channel.send(embed=embed)
        except Exception as e:
            print(f"Không thể gửi tin nhắn chào mừng: {e}")

# --- CẤU HÌNH WEB SERVER (FLASK) ---
app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Hệ Thống Get Key VIP - NGHUYDIY</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #0f172a; color: #fff; text-align: center; padding-top: 80px; }
        .container { background: #1e293b; padding: 40px; border-radius: 12px; display: inline-block; box-shadow: 0 4px 15px rgba(0,0,0,0.6); width: 420px; }
        button { background: #22c55e; color: white; border: none; padding: 14px 24px; font-size: 18px; border-radius: 6px; cursor: pointer; width: 100%; font-weight: bold; }
        button:hover { background: #16a34a; }
        .key-box { background: #334155; padding: 20px; border-radius: 8px; cursor: pointer; border: 2px dashed #38bdf8; margin-top: 10px; transition: 0.2s; }
        .key-box:hover { background: #475569; }
        code { color: #facc15; font-size: 26px; font-weight: bold; font-family: monospace; display: block; margin-top: 5px; }
        .toast { position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); background: #22c55e; color: white; padding: 10px 20px; border-radius: 5px; font-weight: bold; display: none; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
    </style>
</head>
<body>
    <div class="container">
        <h2>NHẬN KEY VIP DISCORD</h2>
        
        {% if not key %}
            <p>Bấm nút bên dưới để khởi tạo Key của bạn:</p>
            <form method="POST" id="keyForm">
                <button type="submit" id="createBtn">Tạo Key Ngay</button>
            </form>
        {% else %}
            <p style="color: #38bdf8; font-weight: bold;">🔑 Nhấn vào ô bên dưới để sao chép & tự đóng trang:</p>
            <div class="key-box" onclick="copyAndClose('{{ key }}')">
                <span style="font-size: 14px; color: #cbd5e1;">BẤM ĐỂ SAO CHÉP</span>
                <code>{{ key }}</code>
            </div>
            <p style="font-size: 12px; color: #94a3b8; margin-top: 15px;">(Sau khi sao chép, trang web sẽ tự động đóng lại)</p>
            
            <script>
                // Lưu trạng thái vào trình duyệt để chống F5 hoặc cố tình truy cập lại trang kết quả
                if (localStorage.getItem("key_claimed")) {
                    window.location.href = "/";
                } else {
                    localStorage.setItem("key_claimed", "true");
                }

                function copyAndClose(text) {
                    navigator.clipboard.writeText(text).then(function() {
                        let toast = document.getElementById("toast");
                        toast.style.display = "block";
                        setTimeout(function() {
                            window.close();
                            // Phòng trường hợp trình duyệt chặn window.close() tự động
                            document.body.innerHTML = "<h2 style='color:#22c55e; margin-top:100px;'>Đã sao chép Key thành công! Bạn có thể tắt tab này.</h2>";
                        }, 800);
                    }, function(err) {
                        alert('Không thể tự sao chép, vui lòng copy thủ công!');
                    });
                }
            </script>
        {% endif %}
    </div>

    <div id="toast" class="toast">Đã sao chép Key thành công! Đang đóng trang...</div>

    <script>
        // Xóa bộ nhớ chống F5 nếu người dùng quay lại trang chủ lấy lượt mới
        if (window.location.pathname === "/" && !window.location.search) {
            // Có thể giữ hoặc reset tùy ý, ở đây cho phép tạo mới nếu vào lại từ đầu
        }
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    generated_key = None
    if request.method == "POST":
        chars = string.ascii_uppercase + string.digits
        random_str = ''.join(random.choice(chars) for _ in range(8))
        key = f"NGHUYDIY-{random_str}"
        
        active_keys.add(key)
        generated_key = key
            
    return render_template_string(HTML_TEMPLATE, key=generated_key)

def run_web():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# --- CÁC LỆNH CỦA BOT ---

@bot.command(name="myid")
async def myid(ctx):
    if bot_is_sleeping: return
    await ctx.send(f"🆔 ID Discord của bạn là: `{ctx.author.id}` (Hãy copy dãy số này dán vào biến `OWNER_ID` trong code Python).")

@bot.command(name="help")
async def help_command(ctx):
    if bot_is_sleeping: return
    embed = discord.Embed(title="🤖 HỆ THỐNG LỆNH", color=discord.Color.green())
    embed.add_field(name="Lệnh Thành Viên", value="`!getkey` - Lấy link web tạo key NGHHUYDIY-\n`!verify <key>` - Kích hoạt nhận VIP\n`!myid` - Lấy Discord ID", inline=False)
    embed.add_field(name="Lệnh Chủ Bot", value="`!tao_key` - Tạo key trực tiếp trong chat\n`!vip @user` | `!unvip @user`\n`!clear` | `!kick` | `!timeout`\n`!sleep` | `!wakeup` | `!shutdown`", inline=False)
    await ctx.send(embed=embed)

@bot.command(name="getkey")
async def getkey(ctx):
    if bot_is_sleeping:
        await ctx.send("💤 Bot đang ngủ!")
        return
    await ctx.send(f"🔗 {ctx.author.mention}, hãy truy cập đường dẫn sau để lấy key bảo mật của bạn:\n{CUSTOM_GET_KEY_URL}")

@bot.command(name="tao_key")
async def tao_key(ctx):
    if bot_is_sleeping: return
    
    if ctx.author.id != OWNER_ID:
        await ctx.send("⛔ Bạn không có quyền sử dụng lệnh này!")
        return
    
    chars = string.ascii_uppercase + string.digits
    random_str = ''.join(random.choice(chars) for _ in range(8))
    key = f"NGHUYDIY-{random_str}"
    
    active_keys.add(key)
    
    try:
        await ctx.send(f"✅ Đã tạo key ngẫu nhiên thành công:\n🔑 Key: `{key}`")
    except Exception as e:
        print(f"Lỗi gửi tin nhắn tạo key: {e}")

@bot.command()
async def verify(ctx, user_key: str):
    if bot_is_sleeping: return
    
    if not user_key.startswith("NGHUYDIY-"):
        await ctx.send("❌ Key không hợp lệ! Key phải bắt đầu bằng `NGHUYDIY-`.")
        return
    
    if user_key in active_keys:
        role = discord.utils.get(ctx.guild.roles, name="VIP")
        if role:
            await ctx.author.add_roles(role)
            await ctx.send(f"🎉 Xác thực thành công! {ctx.author.mention} đã nhận được quyền `{role.name}`.")
            active_keys.remove(user_key)
        else:
            await ctx.send("❌ Lỗi: Server chưa tạo Role có tên chính xác là `VIP`.")
    else:
        await ctx.send("❌ Key không tồn tại hoặc đã được sử dụng trước đó!")

# --- CÁC LỆNH QUẢN TRỊ KHÁC ---
@bot.command()
@commands.has_permissions(administrator=True)
async def vip(ctx, member: discord.Member):
    if bot_is_sleeping: return
    role = discord.utils.get(ctx.guild.roles, name="VIP")
    if role:
        await member.add_roles(role)
        await ctx.send(f"👑 Đã cấp quyền **VIP** cho {member.mention}!")
    else:
        await ctx.send("❌ Server chưa tạo Role `VIP`.")

@bot.command()
@commands.has_permissions(administrator=True)
async def unvip(ctx, member: discord.Member):
    if bot_is_sleeping: return
    role = discord.utils.get(ctx.guild.roles, name="VIP")
    if role and role in member.roles:
        await member.remove_roles(role)
        await ctx.send(f"❌ Đã gỡ quyền **VIP** của {member.mention}!")
    else:
        await ctx.send(f"⚠️ Thành viên không có role VIP.")

@bot.command()
async def serverinfo(ctx):
    if bot_is_sleeping: return
    guild = ctx.guild
    embed = discord.Embed(title=f"Thông tin Server: {guild.name}", color=discord.Color.blue())
    embed.add_field(name="Chủ sở hữu", value=guild.owner, inline=True)
    embed.add_field(name="Tổng thành viên", value=guild.member_count, inline=True)
    await ctx.send(embed=embed)

@bot.command()
async def coinflip(ctx):
    if bot_is_sleeping: return
    result = random.choice(["Mặt Ngửa (Heads)", "Mặt Sấp (Tails)"])
    await ctx.send(f"🪙 Kết quả tung đồng xu: **{result}**")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    if bot_is_sleeping: return
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 Đã xóa {amount} tin nhắn!", delete_after=3)

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="Không có lý do"):
    if bot_is_sleeping: return
    await member.kick(reason=reason)
    await ctx.send(f"👢 Đã đá {member.mention}.")

@bot.command()
async def timeout(ctx, member: discord.Member, minutes: int, *, reason="Không có lý do"):
    if bot_is_sleeping: return
    await member.timeout(timedelta(minutes=minutes), reason=reason)
    await ctx.send(f"🔇 Đã khóa chat {member.mention} trong {minutes} phút.")

@bot.command()
@commands.has_permissions(administrator=True)
async def sleep(ctx):
    global bot_is_sleeping
    bot_is_sleeping = True
    await ctx.send("💤 Bot đã đi ngủ!")

@bot.command()
@commands.has_permissions(administrator=True)
async def wakeup(ctx):
    global bot_is_sleeping
    bot_is_sleeping = False
    await ctx.send("☀️ Bot đã thức dậy!")

@bot.command()
@commands.has_permissions(administrator=True)
async def shutdown(ctx):
    await ctx.send("🛑 Tắt bot...")
    await bot.close()

# --- BỘ LỌC LINK LẠ ---
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if bot_is_sleeping:
        if message.content.startswith("!wakeup"):
            await bot.process_commands(message)
        return

    if "http://" in message.content or "https://" in message.content or "www." in message.content:
        allowed_domains = ["discord.gg", "youtube.com"]
        
        is_admin_or_vip = message.author.guild_permissions.administrator
        if not is_admin_or_vip:
            vip_role = discord.utils.get(message.guild.roles, name="VIP")
            if vip_role and vip_role in message.author.roles:
                is_admin_or_vip = True

        if not is_admin_or_vip and not any(domain in message.content for domain in allowed_domains):
            try:
                await message.delete()
                await message.channel.send(f"⚠️ {message.author.mention}, bạn không được phép gửi link lạ trong server này!")
                return
            except discord.Forbidden:
                pass

    await bot.process_commands(message)

# --- KHỞI CHẠY ĐỒNG THỜI WEB VÀ BOT ---
if __name__ == "__main__":
    web_thread = threading.Thread(target=run_web)
    web_thread.daemon = True
    web_thread.start()
    
    bot.run("YOUR_BOT_TOKEN")
