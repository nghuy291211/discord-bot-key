import os
import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import time

# Thư viện Google GenAI
from google import genai

# Khởi tạo Gemini Client
gemini_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# ================= CẤU HÌNH CHỦ BOT =================
# Thay số bên dưới bằng Discord User ID của bạn (ví dụ: 123456789012345678)
OWNER_ID = 1530913781515812925 
# ====================================================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print("Đã đồng bộ xong toàn bộ Slash Commands!")

client = MyBot()

# Lưu trữ dữ liệu rank tạm thời/vĩnh viễn: {guild_id: {user_id: {"rank": ten_rank, "expire_time": timestamp}}}
temporary_ranks = {}

@client.event
async def on_ready():
    print(f'Bot đã đăng nhập thành công với tên: {client.user}')

# ================= 1. LỆNH HELP (Tổng hợp đầy đủ nhóm lệnh) =================
@client.tree.command(name="help", description="Xem hướng dẫn sử dụng toàn bộ hệ thống bot")
async def help_command(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    
    embed = discord.Embed(title="📜 BẢNG HƯỚNG DẪN TOÀN BỘ HỆ THỐNG", color=discord.Color.blue())
    embed.add_field(name="🎵 1. Nhóm Lệnh Nhạc", value="`/play` - Phát âm thanh/video từ YouTube.", inline=False)
    embed.add_field(name="🔮 2. Nhóm Lệnh Giải Trí AI", value="`/8ball` - Trò chuyện và hỏi quả cầu thông minh.", inline=False)
    embed.add_field(name="ℹ️ 3. Nhóm Lệnh Thành Viên & Tiện Ích", value="`/serverinfo`, `/userinfo`, `/botinfo`, `/ping`", inline=False)
    embed.add_field(name="🛡️ 4. Nhóm Lệnh Quản Trị / Admin", value="`/kick`, `/ban`, `/unban`, `/timeout`, `/untimeout`, `/clear`, `/lock`, `/unlock`, `/slowmode`, `/poll`", inline=False)
    embed.add_field(name="👑 5. Nhóm Lệnh Độc Quyền Chủ Bot & Rank", value="`/set-rank`, `/owner-shutdown`, `/owner-broadcast`", inline=False)
    
    await interaction.followup.send(embed=embed)

# ================= 2. LỆNH PLAY (Phát nhạc - Chống timeout) =================
class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        import yt_dlp
        loop = loop or asyncio.get_event_loop()
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
        ytdl = yt_dlp.YoutubeDL(ytdl_format_options)
        
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            data = data['entries'][0]
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, executable="ffmpeg", options="-vn"), data=data)

@client.tree.command(name="play", description="[Phát nhạc] Phát âm thanh từ YouTube vào kênh thoại")
@app_commands.describe(search="Dán link YouTube hoặc tên bài hát")
async def play(interaction: discord.Interaction, search: str):
    if not interaction.user.voice:
        await interaction.response.send_message("⚠️ Bạn cần vào Kênh Thoại trước!", ephemeral=True)
        return

    await interaction.response.defer(thinking=True)
    voice_channel = interaction.user.voice.channel
    
    if not interaction.guild.voice_client:
        try:
            await voice_channel.connect()
        except Exception as e:
            await interaction.followup.send(f"❌ Không thể kết nối kênh thoại: {e}")
            return
    
    try:
        player = await YTDLSource.from_url(search, loop=client.loop, stream=True)
        interaction.guild.voice_client.play(player, after=lambda e: print(f'Lỗi: {e}') if e else None)
        await interaction.followup.send(f"▶️ Đang phát: **{player.title}**")
    except Exception as e:
        await interaction.followup.send(f"❌ Không thể phát: {e}")

# ================= 3. LỆNH 8BALL (AI Gemini) =================
@client.tree.command(name="8ball", description="[Giải trí AI] Trò chuyện thông minh cùng quả cầu kỳ diệu.")
@app_commands.describe(question="Điều bạn muốn hỏi hoặc tâm sự")
async def eight_ball(interaction: discord.Interaction, question: str):
    await interaction.response.defer(thinking=True)
    user_name = interaction.user.name
    
    try:
        prompt = f"""
        Bạn là một quả cầu 8-ball ma thuật nhưng có trí tuệ nhân tạo cực kỳ thông minh, sâu sắc và thân thiện. 
        Người dùng {user_name} đang hỏi bạn: "{question}"
        Hãy trả lời bằng tiếng Việt, ngắn gọn (dưới 3-4 câu), mang phong cách huyền bí nhưng rất thực tế, dí dỏm.
        """
        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        ai_reply = response.text if response.text else "Quả cầu đang mải suy ngẫm..."
        
        embed = discord.Embed(title="🔮 Quả Cầu Ma Thuật 8-ball (AI)", color=discord.Color.purple())
        embed.add_field(name=f"💬 Câu hỏi từ {user_name}:", value=question, inline=False)
        embed.add_field(name="✨ Phán quyết:", value=ai_reply, inline=False)
        await interaction.followup.send(embed=embed)
    except Exception as e:
        print(f"Lỗi Gemini API: {e}")
        await interaction.followup.send("🔮 Quả cầu hiện chưa kết nối được với vũ trụ, hãy kiểm tra lại khóa API!", ephemeral=True)

# ================= 4. NHÓM LỆNH THÀNH VIÊN & TIỆN ÍCH =================
@client.tree.command(name="ping", description="Kiểm tra độ trễ của bot")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! 🏓 Độ trễ: `{round(client.latency * 1000)}ms`", ephemeral=True)

@client.tree.command(name="serverinfo", description="Xem thông tin máy chủ")
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title=f"📊 Thông tin server: {guild.name}", color=discord.Color.gold())
    embed.add_field(name="Chủ sở hữu", value=guild.owner, inline=True)
    embed.add_field(name="Tổng thành viên", value=guild.member_count, inline=True)
    embed.add_field(name="Số kênh", value=len(guild.channels), inline=True)
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="botinfo", description="Xem thông tin về bot")
async def botinfo(interaction: discord.Interaction):
    embed = discord.Embed(title="🤖 Thông tin Bot", description="Bot quản lý, giải trí và phát nhạc tích hợp AI.", color=discord.Color.teal())
    embed.add_field(name="Nhà phát triển", value="Nguyễn Huy", inline=True)
    embed.add_field(name="Phiên bản", value="2.5 (AI Enabled)", inline=True)
    await interaction.response.send_message(embed=embed)

# ================= 5. NHÓM LỆNH QUẢN TRỊ / ADMIN =================
@client.tree.command(name="kick", description="Đuổi thành viên khỏi máy chủ")
@app_commands.describe(member="Thành viên cần kick", reason="Lý do")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "Không có lý do"):
    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message("❌ Bạn không có quyền sử dụng lệnh này!", ephemeral=True)
        return
    await member.kick(reason=reason)
    await interaction.response.send_message(f"👢 Đã đuổi **{member.name}** thành công. Lý do: {reason}")

@client.tree.command(name="ban", description="Cấm thành viên khỏi máy chủ")
@app_commands.describe(member="Thành viên cần ban", reason="Lý do")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "Không có lý do"):
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("❌ Bạn không có quyền sử dụng lệnh này!", ephemeral=True)
        return
    await member.ban(reason=reason)
    await interaction.response.send_message(f"🔨 Đã ban **{member.name}** thành công. Lý do: {reason}")

@client.tree.command(name="clear", description="Xóa tin nhắn nhanh trong kênh")
@app_commands.describe(amount="Số lượng tin nhắn muốn xóa (tối đa 100)")
async def clear(interaction: discord.Interaction, amount: int):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("❌ Bạn không có quyền quản lý tin nhắn!", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.followup.send(f"🧹 Đã xóa thành công {len(deleted)} tin nhắn!", ephemeral=True)

@client.tree.command(name="slowmode", description="Đặt chế độ chậm cho kênh chat")
@app_commands.describe(seconds="Số giây chậm (0 để tắt)")
async def slowmode(interaction: discord.Interaction, seconds: int):
    if not interaction.user.guild_permissions.manage_channels:
        await interaction.response.send_message("❌ Bạn không có quyền chỉnh sửa kênh!", ephemeral=True)
        return
    await interaction.channel.edit(slowmode_delay=seconds)
    await interaction.response.send_message(f"⏱️ Đã đặt slowmode của kênh thành **{seconds} giây**.")

@client.tree.command(name="poll", description="Tạo một cuộc khảo sát nhanh")
@app_commands.describe(question="Nội dung khảo sát")
async def poll(interaction: discord.Interaction, question: str):
    embed = discord.Embed(title="📊 Bảng Khảo Sát", description=question, color=discord.Color.orange())
    embed.set_footer(text=f"Khảo sát được tạo bởi {interaction.user.name}")
    await interaction.response.send_message(embed=embed)
    message = await interaction.original_response()
    await message.add_reaction("👍")
    await message.add_reaction("👎")

# ================= 6. LỆNH ĐỘC QUYỀN CHỦ BOT (Owner Commands) =================
@client.tree.command(name="owner-shutdown", description="[Độc quyền Chủ Bot] Tắt nguồn bot từ xa")
async def owner_shutdown(interaction: discord.Interaction):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ Lệnh này chỉ dành riêng cho Chủ Bot!", ephemeral=True)
        return
    await interaction.response.send_message("🔌 Đang tiến hành tắt nguồn bot...", ephemeral=True)
    await client.close()

@client.tree.command(name="owner-broadcast", description="[Độc quyền Chủ Bot] Gửi thông báo toàn hệ thống tới kênh hiện tại")
@app_commands.describe(message="Nội dung thông báo")
async def owner_broadcast(interaction: discord.Interaction, message: str):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ Lệnh này chỉ dành riêng cho Chủ Bot!", ephemeral=True)
        return
    embed = discord.Embed(title="📢 THÔNG BÁO TỪ HỆ THỐNG CHỦ BOT", description=message, color=discord.Color.red())
    await interaction.response.send_message("✅ Đã gửi thông báo!", ephemeral=True)
    await interaction.channel.send(embed=embed)

# ================= 7. LỆNH SET-RANK & USERINFO (Nâng cấp) =================
@client.tree.command(name="set-rank", description="Cấp rank (Vĩnh viễn nếu bỏ trống giây, hoặc theo số giây)")
@app_commands.describe(
    member="Thành viên nhận rank", 
    rank_name="Tên mức rank", 
    duration_seconds="Số giây hiệu lực (Bỏ trống = Vĩnh viễn)"
)
async def set_rank(interaction: discord.Interaction, member: discord.Member, rank_name: str, duration_seconds: int = None):
    # Cho phép Admin server HOẶC Chủ Bot thực hiện lệnh cấp rank
    if not interaction.user.guild_permissions.administrator and interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ Bạn cần quyền Administrator hoặc là Chủ Bot để dùng lệnh này!", ephemeral=True)
        return

    await interaction.response.defer(thinking=True)
    guild_id = interaction.guild.id
    
    if guild_id not in temporary_ranks:
        temporary_ranks[guild_id] = {}

    if duration_seconds is None:
        temporary_ranks[guild_id][member.id] = {
            "rank": rank_name,
            "expire_time": None
        }
        await interaction.followup.send(f"✅ Đã cấp rank **{rank_name}** cho {member.mention} **vĩnh viễn**!")
    else:
        expire_timestamp = time.time() + duration_seconds
        temporary_ranks[guild_id][member.id] = {
            "rank": rank_name,
            "expire_time": expire_timestamp
        }
        await interaction.followup.send(f"⏱️ Đã cấp rank **{rank_name}** cho {member.mention} trong vòng **{duration_seconds} giây**!")

@client.tree.command(name="userinfo", description="Xem thông tin chi tiết và thời hạn rank hiện tại")
@app_commands.describe(member="Thành viên cần kiểm tra (Bỏ trống để xem chính bạn)")
async def userinfo(interaction: discord.Interaction, member: discord.Member = None):
    await interaction.response.defer(thinking=True)
    target = member or interaction.user
    guild_id = interaction.guild.id
    
    rank_info = "Chưa có rank hệ thống"
    
    if guild_id in temporary_ranks and target.id in temporary_ranks[guild_id]:
        data = temporary_ranks[guild_id][target.id]
        rank_name = data["rank"]
        expire_time = data["expire_time"]
        
        if expire_time is None:
            rank_info = f"👑 {rank_name} (Vĩnh viễn)"
        else:
            remaining = int(expire_time - time.time())
            if remaining > 0:
                rank_info = f"⏳ {rank_name} (Còn lại: {remaining} giây)"
            else:
                rank_info = f"❌ {rank_name} (Đã hết hạn)"
                del temporary_ranks[guild_id][target.id]

    embed = discord.Embed(title=f"👤 Thông tin thành viên: {target.name}", color=discord.Color.green())
    embed.set_thumbnail(url=target.display_avatar.url)
    embed.add_field(name="Tên tài khoản", value=target.mention, inline=True)
    embed.add_field(name="Cấp bậc (Rank)", value=rank_info, inline=False)
    embed.add_field(name="Ngày tham gia Discord", value=target.joined_at.strftime("%d/%m/%Y"), inline=True)
    
    await interaction.followup.send(embed=embed)

# Chạy bot
client.run(os.environ.get("TOKEN"))
