import os
import discord
from discord import app_commands
from dotenv import load_dotenv

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

# Khởi tạo Intents
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True
intents.moderation = True

class AdvancedBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        print("[BOT] Đã đồng bộ thành công toàn bộ lệnh phân quyền.")

client = AdvancedBot()

@client.event
async def on_ready():
    print(f"[BOT] Đã đăng nhập: {client.user} (ID: {client.user.id})")
    await client.change_presence(activity=discord.Game(name="Gõ !help hoặc dùng Slash commands"))

# --- HỆ THỐNG SỰ KIỆN TỰ ĐỘNG & LỆNH !HELP ---
@client.event
async def on_member_join(member: discord.Member):
    role = discord.utils.get(member.guild.roles, name="Thành Viên") or discord.utils.get(member.guild.roles, name="Member")
    if role:
        try:
            await member.add_roles(role)
        except:
            pass

    channel = discord.utils.get(member.guild.text_channels, name="welcome") or discord.utils.get(member.guild.text_channels, name="chao-mung")
    if channel:
        embed = discord.Embed(
            title="🎉 Chào mừng bạn đến với Server!",
            description=f"Xin chào {member.mention}, rất vui được đón tiếp bạn đến với **{member.guild.name}**!",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Thành viên thứ: {member.guild.member_count}")
        await channel.send(embed=embed)

@client.event
async def on_message(message):
    if message.author.bot:
        return

    # Bảng trợ giúp phân định rõ từng nhóm lệnh
    if message.content.startswith('!help'):
        embed = discord.Embed(
            title="📖 HỆ THỐNG TRỢ GIÚP - PHÂN LOẠI LỆNH",
            description="Dưới đây là danh sách toàn bộ các lệnh được chia theo phân quyền:",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="🟢 1. Nhóm Lệnh Thành Viên (User Commands)",
            value="• `/serverinfo` - Xem thông tin chi tiết máy chủ\n• `/userinfo` - Xem thông tin tài khoản cá nhân hoặc người khác",
            inline=False
        )
        embed.add_field(
            name="🟡 2. Nhóm Lệnh Quản Trị / Admin (Admin Commands)",
            value="• `/kick` - Đuổi thành viên khỏi server\n• `/ban` - Cấm vĩnh viễn thành viên\n• `/unban` - Gỡ ban bằng ID\n• `/timeout` - Cô lập (mute) thành viên\n• `/untimeout` - Gỡ cô lập thành viên\n• `/clear` - Xóa hàng loạt tin nhắn (1-100)\n• `/lock` / `/unlock` - Khóa/mở khóa kênh chat\n• `/slowmode` - Chỉnh thời gian chậm của kênh\n• `/role-add` / `/role-remove` - Cấp/gỡ vai trò\n• `/nickname` - Đổi biệt danh thành viên\n• `/poll` - Tạo bảng khảo sát",
            inline=False
        )
        embed.add_field(
            name="🔴 3. Nhóm Lệnh Chủ Bot (Bot Owner Commands - 5 IDs)",
            value="• `/owner-broadcast` - Gửi thông báo hệ thống tối cao\n• `/owner-shutdown` - Tắt nguồn bot từ xa khẩn cấp",
            inline=False
        )
        embed.set_footer(text="Sử dụng dấu gạch chéo (/) để chạy các lệnh tương tác.")
        await message.channel.send(embed=embed)


# ==========================================
# 🟢 1. NHÓM LỆNH THÀNH VIÊN (USER COMMANDS)
# ==========================================

@client.tree.command(name="serverinfo", description="[Thành viên] Xem thông tin tổng quan chi tiết của máy chủ.")
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title=f"📊 Thông tin Server: {guild.name}", color=discord.Color.blue())
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name="👑 Chủ sở hữu", value=f"<@{guild.owner_id}>", inline=True)
    embed.add_field(name="👥 Tổng thành viên", value=str(guild.member_count), inline=True)
    embed.add_field(name="💬 Kênh", value=str(len(guild.channels)), inline=True)
    embed.add_field(name="🎭 Số lượng Roles", value=str(len(guild.roles)), inline=True)
    embed.add_field(name="📅 Ngày tạo", value=f"<t:{int(guild.created_at.timestamp())}:R>", inline=True)
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="userinfo", description="[Thành viên] Xem thông tin chi tiết tài khoản của bạn hoặc người khác.")
@app_commands.describe(user="Thành viên cần xem (để trống sẽ lấy thông tin chính bạn)")
async def userinfo(interaction: discord.Interaction, user: discord.Member = None):
    target = user or interaction.user
    embed = discord.Embed(title=f"👤 Thông tin: {target}", color=discord.Color.gold())
    embed.set_thumbnail(url=target.display_avatar.url)
    embed.add_field(name="🆔 ID", value=target.id, inline=True)
    embed.add_field(name="📅 Tạo tài khoản", value=f"<t:{int(target.created_at.timestamp())}:R>", inline=True)
    embed.add_field(name="📥 Vào Server", value=f"<t:{int(target.joined_at.timestamp())}:R>", inline=True)
    roles = [role.mention for role in target.roles if role != interaction.guild.default_role]
    embed.add_field(name=f"🎭 Vai trò ({len(roles)})", value=" ".join(roles) if roles else "Không có", inline=False)
    await interaction.response.send_message(embed=embed)


# =======================================================
# 🟡 2. NHÓM LỆNH QUẢN TRỊ / ROLE ADMIN (ADMIN COMMANDS)
# =======================================================

@client.tree.command(name="kick", description="[Admin] Đuổi một thành viên khỏi server.")
@app_commands.describe(user="Thành viên cần đuổi", reason="Lý do")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, user: discord.Member, reason: str = "Không có lý do"):
    await user.kick(reason=reason)
    await interaction.response.send_message(f"✅ Đã kick thành công **{user}**. Lý do: {reason}", ephemeral=True)

@client.tree.command(name="ban", description="[Admin] Cấm vĩnh viễn một thành viên truy cập server.")
@app_commands.describe(user="Thành viên cần ban", reason="Lý do")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, user: discord.Member, reason: str = "Không có lý do"):
    await user.ban(reason=reason)
    await interaction.response.send_message(f"🔨 Đã ban thành công **{user}**. Lý do: {reason}", ephemeral=True)

@client.tree.command(name="unban", description="[Admin] Gỡ lệnh ban cho người dùng thông qua Discord ID.")
@app_commands.describe(user_id="Discord ID của người cần gỡ ban", reason="Lý do")
@app_commands.checks.has_permissions(ban_members=True)
async def unban(interaction: discord.Interaction, user_id: str, reason: str = "Không có lý do"):
    try:
        user = await client.fetch_user(int(user_id))
        await interaction.guild.unban(user, reason=reason)
        await interaction.response.send_message(f"🔓 Đã gỡ ban thành công cho **{user.tag}**.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Không tìm thấy user hoặc lỗi: {e}", ephemeral=True)

@client.tree.command(name="timeout", description="[Admin] Cô lập (mute) thành viên trong số phút nhất định.")
@app_commands.describe(user="Thành viên", minutes="Số phút", reason="Lý do")
@app_commands.checks.has_permissions(moderate_members=True)
async def timeout(interaction: discord.Interaction, user: discord.Member, minutes: int, reason: str = "Không có lý do"):
    duration = discord.utils.utcnow() + discord.timedelta(minutes=minutes)
    await user.timeout(duration, reason=reason)
    await interaction.response.send_message(f"🔇 Đã timeout **{user}** trong {minutes} phút. Lý do: {reason}", ephemeral=True)

@client.tree.command(name="untimeout", description="[Admin] Gỡ trạng thái cô lập cho thành viên.")
@app_commands.describe(user="Thành viên")
@app_commands.checks.has_permissions(moderate_members=True)
async def untimeout(interaction: discord.Interaction, user: discord.Member):
    await user.timeout(None, reason="Gỡ timeout bởi admin")
    await interaction.response.send_message(f"🔊 Đã gỡ timeout cho **{user}**.", ephemeral=True)

@client.tree.command(name="clear", description="[Admin] Xóa hàng loạt tin nhắn trong kênh (1 đến 100 tin).")
@app_commands.describe(amount="Số lượng tin nhắn cần xóa")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: int):
    if amount < 1 or amount > 100:
        await interaction.response.send_message("⚠️ Vui lòng nhập số lượng từ 1 đến 100.", ephemeral=True)
        return
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(f"🧹 Đã xóa thành công {len(deleted)} tin nhắn.", ephemeral=True)

@client.tree.command(name="lock", description="[Admin] Khóa kênh hiện tại, ngăn thành viên gửi tin nhắn.")
@app_commands.checks.has_permissions(manage_channels=True)
async def lock(interaction: discord.Interaction):
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
    await interaction.response.send_message("🔒 Đã khóa kênh này thành công.")

@client.tree.command(name="unlock", description="[Admin] Mở khóa kênh hiện tại cho phép chat.")
@app_commands.checks.has_permissions(manage_channels=True)
async def unlock(interaction: discord.Interaction):
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=True)
    await interaction.response.send_message("🔓 Đã mở khóa kênh này thành công.")

@client.tree.command(name="slowmode", description="[Admin] Đặt chế độ chậm (slowmode) cho kênh.")
@app_commands.describe(seconds="Số giây chờ (0 để tắt)")
@app_commands.checks.has_permissions(manage_channels=True)
async def slowmode(interaction: discord.Interaction, seconds: int):
    await interaction.channel.edit(slowmode_delay=seconds)
    if seconds == 0:
        await interaction.response.send_message("⏱️ Đã tắt chế độ slowmode.")
    else:
        await interaction.response.send_message(f"⏱️ Đã đặt slowmode thành {seconds} giây.")

@client.tree.command(name="role-add", description="[Admin] Cấp một vai trò cho thành viên.")
@app_commands.describe(user="Thành viên", role="Vai trò cần cấp")
@app_commands.checks.has_permissions(manage_roles=True)
async def role_add(interaction: discord.Interaction, user: discord.Member, role: discord.Role):
    await user.add_roles(role)
    await interaction.response.send_message(f"✅ Đã cấp vai trò **{role.name}** cho **{user}**.", ephemeral=True)

@client.tree.command(name="role-remove", description="[Admin] Gỡ một vai trò của thành viên.")
@app_commands.describe(user="Thành viên", role="Vai trò cần gỡ")
@app_commands.checks.has_permissions(manage_roles=True)
async def role_remove(interaction: discord.Interaction, user: discord.Member, role: discord.Role):
    await user.remove_roles(role)
    await interaction.response.send_message(f"❌ Đã gỡ vai trò **{role.name}** khỏi **{user}**.", ephemeral=True)

@client.tree.command(name="nickname", description="[Admin] Thay đổi biệt danh của thành viên.")
@app_commands.describe(user="Thành viên", new_name="Biệt danh mới (để trống để xóa)")
@app_commands.checks.has_permissions(manage_nicknames=True)
async def nickname(interaction: discord.Interaction, user: discord.Member, new_name: str = None):
    await user.edit(nick=new_name)
    await interaction.response.send_message(f"✏️ Đã cập nhật biệt danh cho **{user}**.", ephemeral=True)

@client.tree.command(name="poll", description="[Admin] Tạo bảng khảo sát ý kiến nhanh kèm reaction.")
@app_commands.describe(question="Nội dung câu hỏi")
@app_commands.checks.has_permissions(manage_messages=True)
async def poll(interaction: discord.Interaction, question: str):
    embed = discord.Embed(title="📊 Bảng Khảo Sát Nhanh", description=question, color=discord.Color.purple())
    embed.set_footer(text=f"Tạo bởi {interaction.user}")
    await interaction.response.send_message(embed=embed)
    message = await interaction.original_response()
    await message.add_reaction("👍")
    await message.add_reaction("👎")


# ==========================================
# 🔴 3. NHÓM LỆNH CHỦ BOT (OWNER COMMANDS)
# ==========================================

@client.tree.command(name="owner-broadcast", description="[Chủ Bot] Gửi thông báo hệ thống toàn cầu bằng Embed đỏ.")
@app_commands.describe(message="Nội dung thông báo tối cao")
async def owner_broadcast(interaction: discord.Interaction, message: str):
    if not is_owner(interaction.user.id):
        await interaction.response.send_message("⛔ Lệnh này chỉ dành riêng cho **5 Chủ Bot tối cao**!", ephemeral=True)
        return
    
    embed = discord.Embed(title="🚨 THÔNG BÁO TỪ HỆ THỐNG CHỦ BOT", description=message, color=discord.Color.red())
    embed.set_footer(text=f"Phát hành bởi: {interaction.user}", icon_url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="owner-shutdown", description="[Chủ Bot] Tắt nguồn bot khẩn cấp từ xa.")
async def owner_shutdown(interaction: discord.Interaction):
    if not is_owner(interaction.user.id):
        await interaction.response.send_message("⛔ Lệnh này chỉ dành riêng cho **5 Chủ Bot tối cao**!", ephemeral=True)
        return
    
    await interaction.response.send_message("🛑 Bot đang tiến hành ngắt kết nối và tắt nguồn hệ thống...")
    await client.close()


# Xử lý lỗi thiếu quyền hạn
@client.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("❌ Bạn không có đủ quyền hạn (`Permissions`) để sử dụng lệnh này!", ephemeral=True)
    else:
        print(f"Lỗi: {error}")

# Khởi chạy Bot
client.run(TOKEN)
