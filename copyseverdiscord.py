import discord
from discord.ext import commands

# รับ input จากผู้ใช้
TOKEN = input("TOKEN: ")
SOURCE_GUILD_ID = int(input("GUILD ID SERVER: "))
TARGET_GUILD_ID = int(input("GUILD ID SERVER YOU: "))

# กำหนด intents
intents = discord.Intents.default()
intents.guilds = True
intents.messages = True

# สร้าง client
client = commands.Bot(command_prefix="!", intents=intents, self_bot=True)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

    # ดึงข้อมูลเซิร์ฟเวอร์ต้นทาง
    source_guild = client.get_guild(SOURCE_GUILD_ID)
    target_guild = client.get_guild(TARGET_GUILD_ID)

    if not source_guild:
        print("ไม่พบเซิร์ฟเวอร์ต้นทาง!")
        await client.close()
        return

    if not target_guild:
        print("ไม่พบเซิร์ฟเวอร์ปลายทาง!")
        await client.close()
        return

    # ลบทุกช่องและหมวดหมู่ในเซิร์ฟเวอร์ปลายทาง
    for channel in target_guild.channels:
        try:
            await channel.delete()
            print(f"Deleted channel: {channel.name}")
        except discord.NotFound:
            print(f"Channel {channel.name} not found.")
        except discord.Forbidden:
            print(f"Permission denied to delete channel: {channel.name}.")
        except discord.HTTPException as e:
            print(f"Failed to delete channel {channel.name}: {e}")

    for category in target_guild.categories:
        try:
            await category.delete()
            print(f"Deleted category: {category.name}")
        except discord.NotFound:
            print(f"Category {category.name} not found.")
        except discord.Forbidden:
            print(f"Permission denied to delete category: {category.name}.")
        except discord.HTTPException as e:
            print(f"Failed to delete category {category.name}: {e}")

    # ลบทุกบทบาทในเซิร์ฟเวอร์ปลายทาง ยกเว้น @everyone
    for role in target_guild.roles:
        if role.name != "@everyone":
            try:
                await role.delete()
                print(f"Deleted role: {role.name}")
            except discord.NotFound:
                print(f"Role {role.name} not found.")
            except discord.Forbidden:
                print(f"Permission denied to delete role: {role.name}.")
            except discord.HTTPException as e:
                print(f"Failed to delete role {role.name}: {e}")

    # Copy ชื่อหมวดหมู่
    for category in source_guild.categories:
        new_category = await target_guild.create_category(name=category.name, overwrites=category.overwrites)
        print(f"Created category: {new_category.name}")

    # Copy ชื่อช่องในหมวดหมู่
    for channel in source_guild.channels:
        if isinstance(channel, discord.TextChannel):
            category = discord.utils.get(target_guild.categories, name=channel.category.name) if channel.category else None
            await target_guild.create_text_channel(name=channel.name, category=category)
            print(f"Created text channel: {channel.name}")
        elif isinstance(channel, discord.VoiceChannel):
            category = discord.utils.get(target_guild.categories, name=channel.category.name) if channel.category else None
            await target_guild.create_voice_channel(name=channel.name, category=category)
            print(f"Created voice channel: {channel.name}")

    # Copy roles
    for role in source_guild.roles:
        if role.name != "@everyone":  # Skip @everyone role
            await target_guild.create_role(name=role.name, permissions=role.permissions, colour=role.colour)
            print(f"Created role: {role.name}")

    print("การก็อปเสร็จสิ้น!")
    await client.close()

client.run(TOKEN, bot=False)  # ใช้ token ของผู้ใช้
