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
# Lưu danh sách key đang hoạt động (Ai nhập trước người đó nhận)
active_keys = set() 

# 👉 Thay số 0 bằng ID Discord của bạn (Dùng lệnh !myid trong chat để lấy ID)
OWNER_ID = 1530913781515812925  

# 👉 THAY ĐỔI ĐƯỜNG LINK WEB SAU KHI DEPLOY LÊN RENDER VÀO ĐÂY:
CUSTOM_GET_KEY_URL = "http://localhost:5000" 

@bot.event
async def on_ready():
    print(f"Bot đã đăng nhập thành công: {bot.user}")
    
    for guild in bot.guilds:
        embed = discord.Embed(
            title="🟢 BOT ĐÃ KHỞI ĐỘNG THÀNH CÔNG!",
            description="Hệ thống xác thực Key VIP (NGHUYDIY-) không cần nhập ID đã sẵn sàng.",
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

# --- CẤU HÌNH WEB SERVER (FLASK) - KHÔNG CẦN NHẬP ID ---
app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Hệ Thống Get Key VIP - NGHUYDIY</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #0f172a; color: #fff; text-align: center; padding-top: 50px; }
        .container { background: #1e293b; padding: 30px; border-radius: 10px; display: inline-block; box-shadow: 0 4px 10px rgba(0,0,0,0.5); width: 400px; }
        button { background: #22c55e; color: white; border: none; padding: 12px 20px; font-size: 16px; border-radius: 5px; cursor: pointer; width: 95%; font-weight: bold; }
        button:hover { background: #16a34a; }
        .box { background: #334155; padding: 15px; margin-top: 15px; border-radius: 5px; word-break: break-all; text-align: left; }
        code { color: #facc15; font-family: monospace; font-size: 16px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>NHẬN KEY VIP DISCORD</h2>
        <p>Bấm nút bên dưới để tạo ngay Key VIP (Không cần nhập ID):</p>
        <form method="POST">
            <button type="submit">Tạo Key Ngay</button>
        </form>
        {% if key %}
            <div class="box">
                <p>🔑 Key của bạn (Dùng 1 lần): <br><code>{{ key }}</code></p>
                <p style="font-size: 13px; color: #cbd5e1; margin-top: 10px;">
                    👉 Vào Discord dùng lệnh:<br>
                    <code>!verify {{ key }}</code>
                </p>
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    generated_key = None
    if request.method == "POST":
        # Tạo chuỗi ngẫu nhiên không cần quan tâm ID người dùng
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
    embed.add_field(name="Lệnh Thành Viên", value="`!getkey` - Lấy link web tạo key NGHHUYDIY-\n`!verify <key>` - Kích hoạt nhận VIP (Ai nhanh người đó được)\n`!myid` - Lấy Discord ID của bạn", inline=False)
    embed.add_field(name="Lệnh Chủ Bot (Đặc Biệt)", value="`!tao_key` - Tạo key ngẫu nhiên trực tiếp trong chat (Chỉ chủ bot)\n`!vip @user` | `!unvip @user`\n`!clear` | `!kick` | `!timeout`\n`!sleep` | `!wakeup` | `!shutdown`", inline=False)
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
        await ctx.send("⛔ Bạn không có quyền sử dụng lệnh này! Chỉ chủ bot mới có thể tạo key.")
        return
    
    chars = string.ascii_uppercase + string.digits
    random_str = ''.join(random.choice(chars) for _ in range(8))
    key = f"NGHUYDIY-{random_str}"
    
    active_keys.add(key)
    
    try:
        await ctx.send(f"✅ Đã tạo key ngẫu nhiên thành công:\n🔑 Key: `{key}`\n*(Ai sử dụng lệnh `!verify` đầu tiên sẽ kích hoạt được)*")
    except Exception as e:
        print(f"Lỗi gửi tin nhắn tạo key: {e}")

@bot.command()
async def verify(ctx, user_key: str):
    if bot_is_sleeping: return
    
    if not user_key.startswith("NGHUYDIY-"):
        await ctx.send("❌ Key không hợp lệ! Key chuẩn hệ thống phải bắt đầu bằng tiền tố `NGHUYDIY-`.")
        return
    
    # Kiểm tra key có tồn tại trong hệ thống hay không
    if user_key in active_keys:
        role = discord.utils.get(ctx.guild.roles, name="VIP")
        if role:
            await ctx.author.add_roles(role)
            await ctx.send(f"🎉 Xác thực thành công! {ctx.author.mention} đã nhận được quyền `{role.name}`.")
            
            # XÓA VĨNH VIỄN KEY NGAY SAU KHI CÓ NGƯỜI KÍCH HOẠT ĐẦU TIÊN
            active_keys.remove(user_key)
        else:
            await ctx.send("❌ Lỗi: Server của bạn chưa tạo Role có tên chính xác là `VIP`.")
    else:
        await ctx.send("❌ Key không tồn tại hoặc đã có người khác nhanh tay kích hoạt trước đó rồi!")

# --- LỆNH CẤP VÀ GỠ VIP ---
@bot.command()
@commands.has_permissions(administrator=True)
async def vip(ctx, member: discord.Member):
    if bot_is_sleeping: return
    
    role = discord.utils.get(ctx.guild.roles, name="VIP")
    if role:
        await member.add_roles(role)
        await ctx.send(f"👑 Đã cấp quyền **VIP** thành công cho {member.mention}!")
    else:
        await ctx.send("❌ Lỗi: Server chưa tạo Role có tên là `VIP`.")

@vip.error
async def vip_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("⛔ Bạn không có quyền sử dụng lệnh này!")

@bot.command()
@commands.has_permissions(administrator=True)
async def unvip(ctx, member: discord.Member):
    if bot_is_sleeping: return
    
    role = discord.utils.get(ctx.guild.roles, name="VIP")
    if role and role in member.roles:
        await member.remove_roles(role)
        await ctx.send(f"❌ Đã gỡ quyền **VIP** của {member.mention}!")
    else:
        await ctx.send(f"⚠️ Thành viên {member.mention} không có role VIP hoặc server chưa tạo role này.")

@unvip.error
async def unvip_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("⛔ Bạn không có quyền sử dụng lệnh này!")

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

# --- LỆNH QUẢN TRỊ KHÁC ---
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
    await ctx.send(f"👢 Đã đá {member.mention}. Lý do: {reason}")

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
    await ctx.send("🛑 Tắt bot hoàn toàn...")
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
    
    bot.run("MTUzMjcyNDU2OTg3MjI3MzQzOQ.GdWHXc.WTC0j82OHBYpRTkJYJZEIVtXM_keN4l_cYI6JM")
