import discord
from discord import app_commands

# --- CẤU HÌNH TRỰC TIẾP (KHÔNG DÙNG ENV) ---
TOKEN = "TOKEN"  # Dán Token bot Discord của bạn vào đây

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

class UltimateBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        print("[BOT] Đã đồng bộ thành công toàn bộ hệ thống lệnh nâng cao.")

client = UltimateBot()

@client.event
async def on_ready():
    print(f"[BOT] Đã đăng nhập: {client.user} (ID: {client.user.id})")
    await client.change_presence(activity=discord.Game(name="/help | Quản lý Server Toàn Diện"))


# ==========================================================
# HỆ THỐNG TỰ ĐỘNG: GÁN ROLE CHỨC VỤ & CHÀO MỪNG KHI JOIN
# ==========================================================
@client.event
async def on_member_join(member: discord.Member):
    guild = member.guild
    
    # 1. Tự động kiểm tra và gán role "Thành Viên" mặc định
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

    # 2. Gửi tin nhắn chào mừng
    channel = discord.utils.get(guild.text_channels, name="welcome") or discord.utils.get(guild.text_channels, name="chao-mung")
    if channel:
        embed = discord.Embed(
            title="🎉 Chào mừng bạn đến với Server!",
            description=f"Xin chào {member.mention}, rất vui được đón tiếp bạn đến với **{guild.name}**!",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Thành viên thứ: {guild.member_count}")
        await channel.send(embed=embed)


# ==========================================================
# 🟢 1. NHÓM LỆNH THÀNH VIÊN & TIỆN ÍCH (USER COMMANDS)
# ==========================================================

@client.tree.command(name="help", description="[Thành viên] Hiển thị bảng trợ giúp và phân loại danh sách lệnh của bot.")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📖 HỆ THỐNG TRỢ GIÚP - BOT QUẢN LÝ TỐI CAO",
        description="Danh sách toàn bộ các tính năng và lệnh được phân loại chi tiết:",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="🟢 1. Nhóm Lệnh Thành Viên (User Commands)",
        value="• `/help` - Hiển thị bảng hướng dẫn này\n• `/serverinfo` - Xem thông tin chi tiết máy chủ\n• `/userinfo` - Xem thông tin tài khoản cá nhân/người khác\n• `/botinfo` - Xem thông tin về con bot\n• `/ping` - Kiểm tra độ trễ (latency)",
        inline=False
    )
    embed.add_field(
        name="🟡 2. Nhóm Lệnh Quản Trị / Admin (Moderation & Management)",
        value="• `/kick` - Đuổi thành viên\n• `/ban` / `/unban` - Cấm / Gỡ cấm thành viên\n• `/timeout` / `/untimeout` - Cô lập / Gỡ cô lập thành viên\n• `/clear` - Xóa hàng loạt tin nhắn (1-100)\n• `/lock` / `/unlock` - Khóa / Mở khóa kênh chat\n• `/slowmode` - Đặt chế độ chậm cho kênh\n• `/nickname` - Đổi biệt danh\n• `/poll` - Tạo bảng khảo sát nhanh\n• `/channel-create` / `/channel-delete` - Quản lý kênh\n• `/check-user` - Kiểm tra ID và quyền hạn của thành viên",
        inline=False
    )
    embed.add_field(
        name="🔴 3. Nhóm Lệnh Chủ Bot & Phân Chia Chức Vụ (Owner Only)",
        value="• `/set-rank` - **[ĐỘC QUYỀN CHỦ BOT]** Phân chia/Gán chức vụ Role (`Owner`, `Admin`, `Thành Viên`)\n• `/owner-broadcast` - Gửi thông báo toàn hệ thống\n• `/owner-shutdown` - Tắt nguồn bot từ xa",
        inline=False
    )
    embed.set_footer(text="Sử dụng dấu gạch chéo (/) để chạy các lệnh tương tác trực quan.")
    await interaction.response.send_message(embed=embed, ephemeral=True)

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

@client.tree.command(name="botinfo", description="[Thành viên] Xem thông tin về hệ thống bot quản lý.")
async def botinfo(interaction: discord.Interaction):
    embed = discord.Embed(title="🤖 Thông Tin Bot Quản Lý", description="Hệ thống bot quản lý server toàn diện tích hợp bảo mật chủ bot đa tài khoản.", color=discord.Color.teal())
    embed.add_field(name="Trạng thái", value="🟢 Hoạt động 24/7", inline=True)
    embed.add_field(name="Thư viện", value="Discord.py", inline=True)
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="ping", description="[Thành viên] Kiểm tra độ trễ phản hồi của bot.")
async def ping(interaction: discord.Interaction):
    latency = round(client.latency * 1000)
    await interaction.response.send_message(f"Pong! Độ trễ phản hồi của bot là: `{latency}ms`", ephemeral=True)


# ==========================================================
# 🟡 2. NHÓM LỆNH QUẢN TRỊ / ADMIN (MODERATION & MANAGEMENT)
# ==========================================================

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

@client.tree.command(name="channel-create", description="[Admin] Tạo một kênh văn bản mới trong server.")
@app_commands.describe(name="Tên kênh mới")
@app_commands.checks.has_permissions(manage_channels=True)
async def channel_create(interaction: discord.Interaction, name: str):
    guild = interaction.guild
    await guild.create_text_channel(name=name)
    await interaction.response.send_message(f"📁 Đã tạo thành công kênh văn bản: **#{name}**", ephemeral=True)

@client.tree.command(name="channel-delete", description="[Admin] Xóa kênh văn bản hiện tại.")
@app_commands.checks.has_permissions(manage_channels=True)
async def channel_delete(interaction: discord.Interaction):
    channel = interaction.channel
    await interaction.response.send_message(f"🗑️ Đang tiến hành xóa kênh **{channel.name}**...", ephemeral=True)
    await channel.delete()

@client.tree.command(name="check-user", description="[Admin] Kiểm tra ID, ngày tạo và các quyền hạn cốt lõi của một thành viên.")
@app_commands.describe(user="Thành viên cần kiểm tra")
@app_commands.checks.has_permissions(manage_roles=True)
async def check_user(interaction: discord.Interaction, user: discord.Member):
    # Lọc lấy các quyền quan trọng đang được bật của thành viên
    permissions = user.guild_permissions
    active_perms = []
    if permissions.administrator:
        active_perms.append("Administrator (Quản trị tối cao)")
    if permissions.manage_guild:
        active_perms.append("Manage Server (Quản lý Server)")
    if permissions.manage_roles:
        active_perms.append("Manage Roles (Quản lý Role)")
    if permissions.kick_members:
        active_perms.append("Kick Members (Đuổi thành viên)")
    if permissions.ban_members:
        active_perms.append("Ban Members (Cấm thành viên)")
    if permissions.manage_messages:
        active_perms.append("Manage Messages (Quản lý tin nhắn)")
    
    perm_text = ", ".join(active_perms) if active_perms else "Thành viên thông thường (Không có quyền đặc biệt)"

    embed = discord.Embed(title=f"🔍 Kiểm Tra ID & Quyền Hạn: {user}", color=discord.Color.dark_blue())
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.add_field(name="ID Tài khoản", value=f"`{user.id}`", inline=False)
    embed.add_field(name="Là Chủ Bot?", value="✅ Có (Thuộc danh sách 5 Owner tối cao)" if is_owner(user.id) else "❌ Không", inline=False)
    embed.add_field(name="Các quyền hạn cốt lõi", value=perm_text, inline=False)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)


# ==========================================================
# 🔴 3. NHÓM LỆNH CHỦ BOT & PHÂN CHIA CHỨC VỤ (OWNER ONLY)
# ==========================================================

@client.tree.command(name="set-rank", description="[CHỦ BOT ĐỘC QUYỀN] Phân chia chức vụ thông qua Role tương ứng.")
@app_commands.describe(
    user="Thành viên cần phân chia chức vụ",
    rank="Chọn chức vụ: Owner (Chủ Bot), Admin (Quản Lí), Thành Viên (Thành Viên)"
)
@app_commands.choices(rank=[
    app_commands.Choice(name="Owner (Chủ Bot)", value="Owner"),
    app_commands.Choice(name="Admin (Quản Lí)", value="Admin"),
    app_commands.Choice(name="Thành Viên (Thành Viên)", value="Thành Viên")
])
async def set_rank(interaction: discord.Interaction, user: discord.Member, rank: str):
    # Kiểm tra bảo mật: Chỉ 5 Chủ Bot mới được dùng lệnh này
    if not is_owner(interaction.user.id):
        await interaction.response.send_message("⛔ Lệnh này chỉ dành riêng cho **5 Chủ Bot tối cao** mới có quyền phân chia chức vụ!", ephemeral=True)
        return

    guild = interaction.guild
    role_name = rank  # "Owner", "Admin", hoặc "Thành Viên"
    
    # Tìm hoặc tự động tạo role tương ứng trong Server nếu chưa có
    role = discord.utils.get(guild.roles, name=role_name)
    if not role:
        color_map = {
            "Owner": discord.Color.red(),
            "Admin": discord.Color.gold(),
            "Thành Viên": discord.Color.green()
        }
        try:
            role = await guild.create_role(name=role_name, color=color_map.get(role_name, discord.Color.default()), reason="Tự động tạo role chức vụ hệ thống")
        except Exception as e:
            await interaction.response.send_message(f"❌ Không thể tạo role mới do thiếu quyền hệ thống: {e}", ephemeral=True)
            return

    try:
        # Gán role chức vụ cho thành viên
        await user.add_roles(role)
        await interaction.response.send_message(f"👑 [HỆ THỐNG CHỦ BOT]: Đã phân chia thành công chức vụ **{role_name}** cho thành viên **{user.mention}** thông qua Role!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Lỗi khi gán role chức vụ: {e}", ephemeral=True)

@client.tree.command(name="owner-broadcast", description="[CHỦ BOT] Gửi thông báo hệ thống toàn cầu bằng Embed đỏ.")
@app_commands.describe(message="Nội dung thông báo tối cao")
async def owner_broadcast(interaction: discord.Interaction, message: str):
    if not is_owner(interaction.user.id):
        await interaction.response.send_message("⛔ Lệnh này chỉ dành riêng cho **5 Chủ Bot tối cao**!", ephemeral=True)
        return
    
    embed = discord.Embed(title="🚨 THÔNG BÁO TỪ HỆ THỐNG CHỦ BOT", description=message, color=discord.Color.red())
    embed.set_footer(text=f"Phát hành bởi: {interaction.user}", icon_url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="owner-shutdown", description="[CHỦ BOT] Tắt nguồn bot khẩn cấp từ xa.")
async def owner_shutdown(interaction: discord.Interaction):
    if not is_owner(interaction.user.id):
        await interaction.response.send_message("⛔ Lệnh này chỉ dành riêng cho **5 Chủ Bot tối cao**!", ephemeral=True)
        return
    
    await interaction.response.send_message("🛑 Bot đang tiến hành ngắt kết nối và tắt nguồn hệ thống...")
    await client.close()


# Xử lý lỗi thiếu quyền hạn hệ thống
@client.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("❌ Bạn không có đủ quyền hạn (`Permissions`) để thực hiện hành động này!", ephemeral=True)
    else:
        print(f"Lỗi: {error}")

# Khởi chạy Bot
client.run(TOKEN)
