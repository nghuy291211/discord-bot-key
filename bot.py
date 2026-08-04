import os
import random
import asyncio
import discord
from discord import app_commands
from dotenv import load_dotenv
import yt_dlp

# Tải biến môi trường
load_dotenv()
TOKEN = os.getenv("TOKEN")

# --- DANH SÁCH 5 ID CHỦ BOT TỐI CAO ---
OWNER_IDS = [
    1530913781515812925,  # Thay bằng ID chủ bot 1
    234567890123456789,  # Thay bằng ID chủ bot 2
    345678901234567890,  # Thay bằng ID chủ bot 3
    456789012345678901,  # Thay bằng ID chủ bot 4
    567890123456789012   # Thay bằng ID chủ bot 5
]

def is_owner(user_id: int) -> bool:
    return user_id in OWNER_IDS

# Cấu hình yt-dlp để phát video/âm thanh
ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            data = data['entries'][0]
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

# Khởi tạo Intents
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True
intents.moderation = True
intents.voice_states = True

class UltimateBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        print("[BOT] Đã đồng bộ thành công toàn bộ hệ thống lệnh mở rộng.")

client = UltimateBot()

@client.event
async def on_ready():
    print(f"[BOT] Đã đăng nhập: {client.user} (ID: {client.user.id})")
    await client.change_presence(activity=discord.Game(name="/help | Giải trí & Quản lý Toàn Diện"))


# ==========================================================
# HỆ THỐNG TỰ ĐỘNG KHI JOIN SERVER
# ==========================================================
@client.event
async def on_member_join(member: discord.Member):
    guild = member.guild
    member_role = discord.utils.get(guild.roles, name="Thành Viên")
    if not member_role:
        try:
            member_role = await guild.create_role(name="Thành Viên", color=discord.Color.green(), reason="Tự động tạo role Thành Viên")
        except:
            pass
    if member_role:
        try:
            await member.add_roles(member_role)
        except:
            pass

    channel = discord.utils.get(guild.text_channels, name="welcome") or discord.utils.get(guild.text_channels, name="chao-mung")
    if channel:
        embed = discord.Embed(
            title="🎉 Chào mừng bạn đến với Server!",
            description=f"Xin chào {member.mention}, chúc bạn có những trải nghiệm tuyệt vời tại **{guild.name}**!",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Thành viên thứ: {guild.member_count}")
        await channel.send(embed=embed)


# ==========================================================
# 📖 HỆ THỐNG LỆNH TRỢ GIÚP (/help)
# ==========================================================
@client.tree.command(name="help", description="Hiển thị toàn bộ danh sách lệnh quản lý, giải trí và phát nhạc.")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🌟 HỆ THỐNG TRỢ GIÚP - BOT QUẢN LÝ & GIẢI TRÍ TỐI CAO",
        description="Dưới đây là phân loại toàn bộ tính năng của hệ thống:",
        color=discord.Color.blurple()
    )
    embed.add_field(
        name="🎮 1. Nhóm Lệnh Giải Trí & Mini-Games",
        value="• `/roll` - Tung xúc xắc ngẫu nhiên (1-6)\n• `/coinflip` - Tung đồng xu (Sấp / Ngửa)\n• `/8ball` - Hỏi đáp tiên tri ma thuật\n• `/rps` - Chơi oẳn tù tì với bot",
        inline=False
    )
    embed.add_field(
        name="🎵 2. Nhóm Lệnh Phát Nhạc / Video (Voice)",
        value="• `/play` - Phát nhạc hoặc âm thanh video từ từ khóa/link YouTube\n• `/stop` - Dừng phát và ngắt kết nối bot khỏi kênh thoại",
        inline=False
    )
    embed.add_field(
        name="🟢 3. Nhóm Lệnh Thành Viên & Tiện Ích",
        value="• `/serverinfo` - Xem thông tin máy chủ\n• `/userinfo` - Xem thông tin tài khoản\n• `/botinfo` - Xem thông tin bot\n• `/ping` - Kiểm tra độ trễ mạng",
        inline=False
    )
    embed.add_field(
        name="🟡 4. Nhóm Lệnh Quản Trị / Admin",
        value="• `/kick`, `/ban`, `/unban`, `/timeout`, `/untimeout` - Kiểm soát thành viên\n• `/clear` - Xóa tin nhắn nhanh\n• `/lock` / `/unlock` - Khóa/Mở khóa kênh\n• `/slowmode`, `/nickname`, `/poll`, `/channel-create`, `/check-user`",
        inline=False
    )
    embed.add_field(
        name="🔴 5. Nhóm Lệnh Độc Quyền Chủ Bot",
        value="• `/set-rank` - Phân chia chức vụ Role (`Owner`, `Admin`, `Thành Viên`)\n• `/owner-broadcast` - Gửi thông báo toàn hệ thống\n• `/owner-shutdown` - Tắt nguồn bot",
        inline=False
    )
    embed.set_footer(text="Sử dụng dấu gạch chéo (/) để trải nghiệm.")
    await interaction.response.send_message(embed=embed, ephemeral=True)


# ==========================================================
# 🎮 1. NHÓM LỆNH GIẢI TRÍ & MINI-GAMES (ENTERTAINMENT)
# ==========================================================

@client.tree.command(name="roll", description="[Giải trí] Tung xúc xắc ngẫu nhiên từ 1 đến 6.")
async def roll(interaction: discord.Interaction):
    result = random.randint(1, 6)
    embed = discord.Embed(title="🎲 Trò Chơi Xúc Xắc", description=f"Kết quả tung xúc xắc của bạn là: **{result} 🎯**", color=discord.Color.orange())
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="coinflip", description="[Giải trí] Tung đồng xu chọn Sấp hay Ngửa.")
async def coinflip(interaction: discord.Interaction):
    result = random.choice(["Sấp (Heads)", "Ngửa (Tails)"])
    embed = discord.Embed(title="🪙 Tung Đồng Xu", description=f"Kết quả đồng xu gọi tên: **{result}**", color=discord.Color.gold())
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="8ball", description="[Giải trí] Đặt câu hỏi và để quả cầu ma thuật 8-ball giải đáp.")
@app_commands.describe(question="Câu hỏi của bạn")
async def eight_ball(interaction: discord.Interaction, question: str):
    answers = [
        "Chắc chắn là vậy rồi! ✅", "Có thể lắm chứ. 👍", "Không thể nào đoán trước được. 🔮",
        "Tuyệt đối không! ❌", "Hỏi lại vào lúc khác nhé. ⏰", "Triển vọng rất sáng sủa! ✨", "Không có cửa đâu bạn trẻ. 💀"
    ]
    embed = discord.Embed(title="🎱 Quả Cầu Ma Thuật", color=discord.Color.purple())
    embed.add_field(name="Câu hỏi:", value=question, inline=False)
    embed.add_field(name="Phán quyết:", value=random.choice(answers), inline=False)
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="rps", description="[Giải trí] Chơi oẳn tù tì (Kéo, Búa, Bao) với bot.")
@app_commands.describe(choice="Lựa chọn của bạn")
@app_commands.choices(choice=[
    app_commands.Choice(name="Búa (Rock)", value="búa"),
    app_commands.Choice(name="Kéo (Scissors)", value="kéo"),
    app_commands.Choice(name="Bao (Paper)", value="bao")
])
async def rps(interaction: discord.Interaction, choice: str):
    bot_choice = random.choice(["búa", "kéo", "bao"])
    user_choice = choice.lower()
    
    if user_choice == bot_choice:
        result = "🤝 Hòa nhau mất rồi!"
    elif (user_choice == "búa" and bot_choice == "kéo") or \
         (user_choice == "kéo" and bot_choice == "bao") or \
         (user_choice == "bao" and bot_choice == "búa"):
        result = "🎉 Chúc mừng! Bạn đã chiến thắng bot!"
    else:
        result = "🤖 Tiếc quá, bot đã chiến thắng bạn rồi!"
        
    embed = discord.Embed(title="✂️ Oẳn Tù Tì", color=discord.Color.magenta())
    embed.add_field(name="Bạn chọn", value=user_choice.capitalize(), inline=True)
    embed.add_field(name="Bot chọn", value=bot_choice.capitalize(), inline=True)
    embed.add_field(name="Kết quả", value=result, inline=False)
    await interaction.response.send_message(embed=embed)


# ==========================================================
# 🎵 2. NHÓM LỆNH PHÁT NHẠC / VIDEO (MUSIC / VOICE)
# ==========================================================

@client.tree.command(name="play", description="[Phát nhạc/Video] Dán link YouTube hoặc nhập tên bài hát để phát trong voice.")
@app_commands.describe(search="Dán link YouTube (URL) hoặc nhập tên bài hát")
async def play(interaction: discord.Interaction, search: str):
    if not interaction.user.voice:
        await interaction.response.send_message("⚠️ Bạn cần phải tham gia vào một Kênh Thoại (Voice Channel) trước!", ephemeral=True)
        return

    # PHẢI GỌI DEFER NGAY LẬP TỨC ĐỂ TRÁNH LỖI TIMEOUT 3 GIÂY CỦA DISCORD
    await interaction.response.defer(thinking=True)
    
    voice_channel = interaction.user.voice.channel
    
    if not interaction.guild.voice_client:
        try:
            await voice_channel.connect()
        except Exception as e:
            await interaction.followup.send(f"❌ Không thể kết nối vào kênh thoại: {e}")
            return
    
    try:
        player = await YTDLSource.from_url(search, loop=client.loop, stream=True)
        interaction.guild.voice_client.play(player, after=lambda e: print(f'Lỗi âm thanh: {e}') if e else None)
        await interaction.followup.send(f"▶️ Đang phát: **{player.title}**")
    except Exception as e:
        await interaction.followup.send(f"❌ Không thể phát video từ liên kết này: {e}")

@client.tree.command(name="stop", description="[Phát nhạc] Dừng phát nhạc và đuổi bot ra khỏi kênh thoại.")
async def stop(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("⏹️ Đã dừng phát nhạc và rời khỏi kênh thoại.")
    else:
        await interaction.response.send_message("⚠️ Bot hiện không ở trong kênh thoại nào cả.", ephemeral=True)


# ==========================================================
# 🟢 3. NHÓM LỆNH THÀNH VIÊN & TIỆN ÍCH
# ==========================================================

@client.tree.command(name="serverinfo", description="[Thành viên] Xem thông tin tổng quan chi tiết của máy chủ.")
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title=f"📊 Thông tin Server: {guild.name}", color=discord.Color.blue())
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name="👑 Chủ sở hữu", value=f"<@{guild.owner_id}>", inline=True)
    embed.add_field(name="👥 Tổng thành viên", value=str(guild.member_count), inline=True)
    embed.add_field(name="💬 Kênh", value=str(len(guild.channels)), inline=True)
    embed.add_field(name="📅 Ngày tạo", value=f"<t:{int(guild.created_at.timestamp())}:R>", inline=True)
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="userinfo", description="[Thành viên] Xem thông tin chi tiết tài khoản cá nhân hoặc người khác.")
@app_commands.describe(user="Thành viên cần xem")
async def userinfo(interaction: discord.Interaction, user: discord.Member = None):
    target = user or interaction.user
    embed = discord.Embed(title=f"👤 Thông tin: {target}", color=discord.Color.gold())
    embed.set_thumbnail(url=target.display_avatar.url)
    embed.add_field(name="🆔 ID", value=target.id, inline=True)
    embed.add_field(name="📅 Tạo tài khoản", value=f"<t:{int(target.created_at.timestamp())}:R>", inline=True)
    roles = [role.mention for role in target.roles if role != interaction.guild.default_role]
    embed.add_field(name=f"🎭 Vai trò ({len(roles)})", value=" ".join(roles) if roles else "Không có", inline=False)
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="botinfo", description="[Thành viên] Xem thông tin về hệ thống bot.")
async def botinfo(interaction: discord.Interaction):
    embed = discord.Embed(title="🤖 Thông Tin Bot Quản Lý & Giải Trí", description="Hệ thống đa năng tích hợp công nghệ xử lý âm thanh/video tiên tiến.", color=discord.Color.teal())
    embed.add_field(name="Trạng thái", value="🟢 Hoạt động ổn định 24/7", inline=True)
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="ping", description="[Thành viên] Kiểm tra độ trễ phản hồi của bot.")
async def ping(interaction: discord.Interaction):
    latency = round(client.latency * 1000)
    await interaction.response.send_message(f"Pong! Độ trễ phản hồi: `{latency}ms`", ephemeral=True)


# ==========================================================
# 🟡 4. NHÓM LỆNH QUẢN TRỊ / ADMIN
# ==========================================================

@client.tree.command(name="kick", description="[Admin] Đuổi thành viên khỏi server.")
@app_commands.describe(user="Thành viên", reason="Lý do")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, user: discord.Member, reason: str = "Không có lý do"):
    await user.kick(reason=reason)
    await interaction.response.send_message(f"✅ Đã kick **{user}**. Lý do: {reason}", ephemeral=True)

@client.tree.command(name="ban", description="[Admin] Cấm vĩnh viễn thành viên.")
@app_commands.describe(user="Thành viên", reason="Lý do")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, user: discord.Member, reason: str = "Không có lý do"):
    await user.ban(reason=reason)
    await interaction.response.send_message(f"🔨 Đã ban **{user}**. Lý do: {reason}", ephemeral=True)

@client.tree.command(name="unban", description="[Admin] Gỡ cấm thành viên qua ID.")
@app_commands.describe(user_id="Discord ID", reason="Lý do")
@app_commands.checks.has_permissions(ban_members=True)
async def unban(interaction: discord.Interaction, user_id: str, reason: str = "Không có lý do"):
    try:
        user = await client.fetch_user(int(user_id))
        await interaction.guild.unban(user, reason=reason)
        await interaction.response.send_message(f"🔓 Đã gỡ ban cho **{user.tag}**.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Lỗi: {e}", ephemeral=True)

@client.tree.command(name="timeout", description="[Admin] Mute thành viên trong khoảng phút.")
@app_commands.describe(user="Thành viên", minutes="Số phút", reason="Lý do")
@app_commands.checks.has_permissions(moderate_members=True)
async def timeout(interaction: discord.Interaction, user: discord.Member, minutes: int, reason: str = "Không có lý do"):
    duration = discord.utils.utcnow() + discord.timedelta(minutes=minutes)
    await user.timeout(duration, reason=reason)
    await interaction.response.send_message(f"🔇 Đã timeout **{user}** trong {minutes} phút.", ephemeral=True)

@client.tree.command(name="untimeout", description="[Admin] Gỡ timeout cho thành viên.")
@app_commands.checks.has_permissions(moderate_members=True)
async def untimeout(interaction: discord.Interaction, user: discord.Member):
    await user.timeout(None, reason="Gỡ timeout")
    await interaction.response.send_message(f"🔊 Đã gỡ timeout cho **{user}**.", ephemeral=True)

@client.tree.command(name="clear", description="[Admin] Xóa hàng loạt tin nhắn (1-100).")
@app_commands.describe(amount="Số lượng")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: int):
    if amount < 1 or amount > 100:
        await interaction.response.send_message("⚠️ Nhập số lượng từ 1 đến 100.", ephemeral=True)
        return
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(f"🧹 Đã xóa {len(deleted)} tin nhắn.", ephemeral=True)

@client.tree.command(name="lock", description="[Admin] Khóa kênh chat hiện tại.")
@app_commands.checks.has_permissions(manage_channels=True)
async def lock(interaction: discord.Interaction):
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
    await interaction.response.send_message("🔒 Đã khóa kênh này.")

@client.tree.command(name="unlock", description="[Admin] Mở khóa kênh chat hiện tại.")
@app_commands.checks.has_permissions(manage_channels=True)
async def unlock(interaction: discord.Interaction):
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=True)
    await interaction.response.send_message("🔓 Đã mở khóa kênh này.")

@client.tree.command(name="slowmode", description="[Admin] Bật slowmode cho kênh.")
@app_commands.checks.has_permissions(manage_channels=True)
async def slowmode(interaction: discord.Interaction, seconds: int):
    await interaction.channel.edit(slowmode_delay=seconds)
    await interaction.response.send_message(f"⏱️ Đã đặt slowmode thành {seconds} giây.")

@client.tree.command(name="nickname", description="[Admin] Đổi biệt danh thành viên.")
@app_commands.checks.has_permissions(manage_nicknames=True)
async def nickname(interaction: discord.Interaction, user: discord.Member, new_name: str = None):
    await user.edit(nick=new_name)
    await interaction.response.send_message(f"✏️ Đã đổi biệt danh cho **{user}**.", ephemeral=True)

@client.tree.command(name="poll", description="[Admin] Tạo bảng khảo sát kèm vote 👍 👎.")
@app_commands.checks.has_permissions(manage_messages=True)
async def poll(interaction: discord.Interaction, question: str):
    embed = discord.Embed(title="📊 Khảo Sát Nhanh", description=question, color=discord.Color.purple())
    await interaction.response.send_message(embed=embed)
    msg = await interaction.original_response()
    await msg.add_reaction("👍")
    await msg.add_reaction("👎")

@client.tree.command(name="channel-create", description="[Admin] Tạo kênh chat mới.")
@app_commands.checks.has_permissions(manage_channels=True)
async def channel_create(interaction: discord.Interaction, name: str):
    await interaction.guild.create_text_channel(name=name)
    await interaction.response.send_message(f"📁 Đã tạo kênh **#{name}**.", ephemeral=True)

@client.tree.command(name="check-user", description="[Admin] Kiểm tra ID và quyền của thành viên.")
@app_commands.checks.has_permissions(manage_roles=True)
async def check_user(interaction: discord.Interaction, user: discord.Member):
    embed = discord.Embed(title=f"🔍 Kiểm Tra User: {user}", color=discord.Color.dark_blue())
    embed.add_field(name="ID", value=f"`{user.id}`", inline=False)
    embed.add_field(name="Là Chủ Bot?", value="✅ Có" if is_owner(user.id) else "❌ Không", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)


# ==========================================================
# 🔴 5. NHÓM LỆNH CHỦ BOT & PHÂN CHIA CHỨC VỤ (OWNER ONLY)
# ==========================================================

@client.tree.command(name="set-rank", description="[CHỦ BOT ĐỘC QUYỀN] Phân chia chức vụ Role (Owner, Admin, Thành Viên).")
@app_commands.choices(rank=[
    app_commands.Choice(name="Owner (Chủ Bot)", value="Owner"),
    app_commands.Choice(name="Admin (Quản Lí)", value="Admin"),
    app_commands.Choice(name="Thành Viên (Thành Viên)", value="Thành Viên")
])
async def set_rank(interaction: discord.Interaction, user: discord.Member, rank: str):
    if not is_owner(interaction.user.id):
        await interaction.response.send_message("⛔ Lệnh này chỉ dành riêng cho **5 Chủ Bot tối cao**!", ephemeral=True)
        return

    guild = interaction.guild
    role = discord.utils.get(guild.roles, name=rank)
    if not role:
        color_map = {"Owner": discord.Color.red(), "Admin": discord.Color.gold(), "Thành Viên": discord.Color.green()}
        try:
            role = await guild.create_role(name=rank, color=color_map.get(rank, discord.Color.default()))
        except Exception as e:
            await interaction.response.send_message(f"❌ Lỗi tạo role: {e}", ephemeral=True)
            return

    try:
        await user.add_roles(role)
        await interaction.response.send_message(f"👑 Đã gán chức vụ **{rank}** cho **{user.mention}** thành công!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Lỗi gán role: {e}", ephemeral=True)

@client.tree.command(name="owner-broadcast", description="[CHỦ BOT] Gửi thông báo toàn hệ thống.")
async def owner_broadcast(interaction: discord.Interaction, message: str):
    if not is_owner(interaction.user.id):
        await interaction.response.send_message("⛔ Lệnh này chỉ dành riêng cho **5 Chủ Bot tối cao**!", ephemeral=True)
        return
    embed = discord.Embed(title="🚨 THÔNG BÁO TỪ HỆ THỐNG CHỦ BOT", description=message, color=discord.Color.red())
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="owner-shutdown", description="[CHỦ BOT] Tắt nguồn bot từ xa.")
async def owner_shutdown(interaction: discord.Interaction):
    if not is_owner(interaction.user.id):
        await interaction.response.send_message("⛔ Lệnh này chỉ dành riêng cho **5 Chủ Bot tối cao**!", ephemeral=True)
        return
    await interaction.response.send_message("🛑 Đang tiến hành tắt nguồn bot...")
    await client.close()

# Khởi chạy Bot
client.run(TOKEN)
