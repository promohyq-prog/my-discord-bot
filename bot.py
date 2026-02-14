import discord
from discord.ext import commands
from discord.ui import View, Button
import asyncio

WELCOME_CHANNEL_ID = 1469318139660599307
TICKET_CATEGORY_ID = 1471232410329813002
SUPPORT_ROLE_ID = 1471220377974735123
GARANT_ROLE_ID = 1471220456185925724
KZT_CATEGORY_ID = 1472157532926640240

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# ================= ВХОД =================

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    embed = discord.Embed(
        title="👋 Добро пожаловать!",
        description=f"{member.mention}, рады видеть тебя на сервере!",
        color=0x5865F2
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    await channel.send(embed=embed)

# ================= ЗАКРЫТИЕ =================

class CloseTicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒", style=discord.ButtonStyle.red)
    async def close_ticket(self, interaction: discord.Interaction, button: Button):
        await interaction.channel.delete()

    @discord.ui.button(label="✏", style=discord.ButtonStyle.gray)
    async def close_with_reason(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("Напиши причину закрытия:", ephemeral=True)

        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel

        try:
            msg = await bot.wait_for("message", check=check, timeout=120)

            forum = bot.get_channel(LOG_FORUM_ID)

            if forum and isinstance(forum, discord.ForumChannel):
                embed = discord.Embed(
                    title="Закрытый тикет",
                    description=f"Пользователь: {interaction.user}\nТикет: {interaction.channel.name}\nПричина: {msg.content}",
                    color=0xED4245
                )

                await forum.create_thread(
                    name=f"Тикет {interaction.user}",
                    content="Тикет закрыт с причиной.",
                    embed=embed
                )

            await interaction.channel.delete()

        except asyncio.TimeoutError:
            await interaction.followup.send("Время вышло.", ephemeral=True)

# ================= ОБЫЧНЫЙ ТИКЕТ =================

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📩 Создать тикет", style=discord.ButtonStyle.primary)
    async def create_ticket(self, interaction: discord.Interaction, button: Button):

        guild = interaction.guild
        support_role = guild.get_role(SUPPORT_ROLE_ID)
        category = guild.get_channel(TICKET_CATEGORY_ID)

        for ch in category.channels:
            if ch.name == f"ticket-{interaction.user.name}".lower():
                await interaction.response.send_message("У тебя уже есть тикет.", ephemeral=True)
                return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            support_role: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }

        channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=category,
            overwrites=overwrites
        )

        embed = discord.Embed(
            title="Привет 👋",
            description="Опиши подробно свою проблему или вопрос. В скором времени тебе ответят. В конце разговора не забудь закрыть тикет нажав на 🔒.",
            color=0x2B2D31
        )

        await channel.send(
            content=f"{interaction.user.mention} {support_role.mention}",
            embed=embed,
            view=CloseTicketView()
        )

        await interaction.response.send_message("Тикет создан.", ephemeral=True)

# ================= KZT ТИКЕТ =================
class TicketViewKZT(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="💳 Открыть тикет (KZT)", style=discord.ButtonStyle.success)
    async def create_ticket_kzt(self, interaction: discord.Interaction, button: Button):

        guild = interaction.guild
        garant_role = guild.get_role(GARANT_ROLE_ID)
        category = guild.get_channel(KZT_CATEGORY_ID)

        if category is None:
            await interaction.response.send_message("Категория KZT не найдена.", ephemeral=True)
            return

        for ch in category.channels:
            if ch.name == f"ticketkzt-{interaction.user.name}".lower():
                await interaction.response.send_message("У тебя уже есть тикет.", ephemeral=True)
                return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            garant_role: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }

        channel = await guild.create_text_channel(
            name=f"ticketkzt-{interaction.user.name}",
            category=category,
            overwrites=overwrites
        )

        embed = discord.Embed(
            title="Привет 👋",
            description="Опиши подробно что ты хочешь купить и с какой валюты (Тенге). Тут так же можно купить донат через киви если на сайте недоступна оплата. В скором времени тебе ответят. В конце разговора не забудь закрыть тикет нажав на 🔒.",
            color=0x2B2D31
        )

        await channel.send(
            content=f"{interaction.user.mention} {garant_role.mention}",
            embed=embed,
            view=CloseTicketView()
        )

        await interaction.response.send_message("Тикет создан.", ephemeral=True)


# ================= ПАНЕЛИ =================

@bot.command()
@commands.has_permissions(administrator=True)
async def ticketpanel(ctx):
    embed = discord.Embed(
        title="📨 Поддержка",
        description="Создайте тикет что бы задать вопрос или описать свою проблему. На ваш вопрос может ответить как саппорт, так и владелец проекта.",
        color=0x5865F2
    )
    await ctx.send(embed=embed, view=TicketView())

@bot.command()
@commands.has_permissions(administrator=True)
async def ticketpanelkzt(ctx):
    embed = discord.Embed(
        title="💳 Донат / KZT",
        description="Не пришел донат? Создайте тикет что бы решить эту проблему.",
        color=0x57F287
    )
    await ctx.send(embed=embed, view=TicketViewKZT())

# ================= READY =================

@bot.event
async def on_ready():
    print(f"Бот запущен как {bot.user}")
    bot.add_view(TicketView())
    bot.add_view(TicketViewKZT())
    bot.add_view(CloseTicketView())

import os

bot.run(os.getenv("TOKEN"))
