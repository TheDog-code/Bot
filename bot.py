"""
Ryu Discord Bot - Bot completo de moderação com interações divertidas
Desenvolvido com discord.py
"""

import discord
from discord.ext import commands
from discord import ui
import aiosqlite
import os
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv
import google.generativeai as genai
import re

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GEMINI_KEY = os.getenv('GEMINI_API_KEY')

if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None


# ==================== HELP MENU ====================
class HelpSelect(ui.Select):
    def __init__(self, bot):
        options = [
            discord.SelectOption(label="👮 Moderação", description="Ban, Kick, Mute, Logs", emoji="🛡️"),
            discord.SelectOption(label="🤖 AutoMod", description="Filtro de palavras, spam", emoji="⚙️"),
            discord.SelectOption(label="🎭 Cargos", description="Painel, AutoRole", emoji="🧢"),
            discord.SelectOption(label="🎫 Tickets", description="Sistema de atendimento", emoji="📩"),
            discord.SelectOption(label="🎮 Interações", description="Reações, caixas, curtidas", emoji="🎪"),
            discord.SelectOption(label="🧠 IA", description="Chat com Gemini", emoji="💡"),
        ]
        super().__init__(placeholder="Selecione uma categoria...", min_values=1, max_values=1, options=options)
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        categoria = self.values[0]
        embed = discord.Embed(title=f"Comandos de {categoria}", color=discord.Color.blue())
        
        prefix = self.bot.prefix_cache.get(interaction.guild.id, '!')

        if "Moderação" in categoria:
            embed.add_field(name=f"`{prefix}ban @user [motivo]`", value="Bane um usuário.", inline=False)
            embed.add_field(name=f"`{prefix}kick @user [motivo]`", value="Expulsa um usuário.", inline=False)
            embed.add_field(name=f"`{prefix}mute @user 10m [motivo]`", value="Silencia por tempo (m/h/d).", inline=False)
            embed.add_field(name=f"`{prefix}softban @user`", value="Ban + unban automático (limpa msgs).", inline=False)
            embed.add_field(name=f"`{prefix}warn @user [motivo]`", value="Avisa um usuário.", inline=False)
            embed.add_field(name=f"`{prefix}warns @user`", value="Ver avisos de um usuário.", inline=False)
            embed.add_field(name=f"`{prefix}purge [qtd]`", value="Limpa mensagens do chat.", inline=False)
            embed.add_field(name=f"`{prefix}setlogs #canal`", value="Define onde os logs aparecem.", inline=False)
        
        elif "AutoMod" in categoria:
            embed.add_field(name=f"`{prefix}addfilter palavra`", value="Adiciona palavra ao filtro.", inline=False)
            embed.add_field(name=f"`{prefix}removefilter palavra`", value="Remove palavra do filtro.", inline=False)
            embed.add_field(name=f"`{prefix}listfilter`", value="Lista palavras filtradas.", inline=False)
            embed.add_field(name=f"`{prefix}slow [segundos]`", value="Ativa modo lento no canal.", inline=False)
            embed.add_field(name=f"`{prefix}slowoff`", value="Desativa modo lento.", inline=False)
            embed.add_field(name=f"`{prefix}antispam on/off`", value="Ativa/desativa anti-spam.", inline=False)

        elif "Cargos" in categoria:
            embed.add_field(name=f"`{prefix}painel_cargos`", value="Cria botões para pegar cargos.", inline=False)
            embed.add_field(name=f"`{prefix}setautorole @cargo`", value="Define cargo automático ao entrar.", inline=False)
            embed.add_field(name=f"`{prefix}addrole @user @cargo`", value="Adiciona cargo manualmente.", inline=False)
            embed.add_field(name=f"`{prefix}removerole @user @cargo`", value="Remove cargo de um usuário.", inline=False)

        elif "Tickets" in categoria:
            embed.add_field(name=f"`{prefix}setup_ticket`", value="Cria o painel de atendimento.", inline=False)
            embed.add_field(name=f"`{prefix}fechar`", value="Fecha um ticket aberto.", inline=False)

        elif "Interações" in categoria:
            embed.add_field(name=f"`{prefix}box [texto]`", value="Coloca texto em uma caixa ASCII.", inline=False)
            embed.add_field(name=f"`{prefix}curtir`", value="Reage com 👍 em mensagens aleatoriamente.", inline=False)
            embed.add_field(name="Mensagens com MAIÚSCULA", value="Bot reage com 🔥 automaticamente.", inline=False)

        elif "IA" in categoria:
            embed.add_field(name=f"`{prefix}pergunte [pergunta]`", value="Responde com Gemini AI.", inline=False)

        await interaction.response.edit_message(embed=embed)


# ==================== SYSTEM COG ====================
class SystemCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ajuda(self, ctx):
        """Exibe o menu interativo de comandos"""
        view = ui.View()
        view.add_item(HelpSelect(self.bot))
        embed = discord.Embed(title="📚 Central de Ajuda", description="Selecione uma categoria abaixo:", color=discord.Color.gold())
        await ctx.send(embed=embed, view=view)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setprefix(self, ctx, novo_prefixo: str):
        """Muda o prefixo do bot"""
        async with aiosqlite.connect(self.bot.db_name) as db:
            await db.execute('INSERT OR REPLACE INTO settings (guild_id, prefix) VALUES (?, ?)', 
                             (str(ctx.guild.id), novo_prefixo))
            await db.commit()
        self.bot.prefix_cache[ctx.guild.id] = novo_prefixo
        await ctx.send(f"✅ Prefixo alterado para `{novo_prefixo}`")


# ==================== MODERATION COG ====================
class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def log_action(self, guild, title, description, color):
        async with aiosqlite.connect(self.bot.db_name) as db:
            cursor = await db.execute('SELECT log_channel_id FROM settings WHERE guild_id = ?', (str(guild.id),))
            result = await cursor.fetchone()
        if result and result[0]:
            channel = guild.get_channel(int(result[0]))
            if channel:
                embed = discord.Embed(title=title, description=description, color=color, timestamp=datetime.now())
                try:
                    await channel.send(embed=embed)
                except:
                    pass

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setlogs(self, ctx, channel: discord.TextChannel):
        """Define o canal de logs"""
        async with aiosqlite.connect(self.bot.db_name) as db:
            await db.execute('INSERT OR REPLACE INTO settings (guild_id, log_channel_id) VALUES (?, ?)', 
                             (str(ctx.guild.id), str(channel.id)))
            await db.commit()
        await ctx.send(f"📝 Logs definidos em {channel.mention}")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, motivo="Sem motivo"):
        """Bane um usuário"""
        try:
            await member.ban(reason=motivo)
            embed = discord.Embed(title="🔨 Banimento", description=f"**Alvo:** {member}\n**Motivo:** {motivo}", color=discord.Color.red())
            await ctx.send(embed=embed)
            await self.log_action(ctx.guild, "🔨 Banimento", f"Alvo: {member}\nMod: {ctx.author}\nMotivo: {motivo}", discord.Color.red())
        except Exception as e:
            await ctx.send(f"❌ Erro ao banir: {e}")

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, motivo="Sem motivo"):
        """Expulsa um usuário"""
        try:
            await member.kick(reason=motivo)
            embed = discord.Embed(title="👢 Expulsão", description=f"**Alvo:** {member}\n**Motivo:** {motivo}", color=discord.Color.orange())
            await ctx.send(embed=embed)
            await self.log_action(ctx.guild, "👢 Expulsão", f"Alvo: {member}\nMod: {ctx.author}\nMotivo: {motivo}", discord.Color.orange())
        except Exception as e:
            await ctx.send(f"❌ Erro ao expulsar: {e}")

    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def mute(self, ctx, member: discord.Member, time: str, *, motivo="Sem motivo"):
        """Silencia um usuário por tempo (10m, 1h, 1d)"""
        try:
            unit = time[-1]
            try:
                val = int(time[:-1])
            except:
                return await ctx.send("❌ Use formato: 10m, 1h, 1d", ephemeral=True)
            
            delta = None
            if unit == 'm': delta = timedelta(minutes=val)
            elif unit == 'h': delta = timedelta(hours=val)
            elif unit == 'd': delta = timedelta(days=val)
            else: return await ctx.send("❌ Unidades: m, h, d", ephemeral=True)

            await member.timeout(delta, reason=motivo)
            embed = discord.Embed(title="🤐 Silenciado", description=f"**Alvo:** {member}\n**Tempo:** {time}\n**Motivo:** {motivo}", color=discord.Color.dark_grey())
            await ctx.send(embed=embed)
            await self.log_action(ctx.guild, "🤐 Silenciado", f"Alvo: {member}\nTempo: {time}\nMod: {ctx.author}\nMotivo: {motivo}", discord.Color.dark_grey())
        except Exception as e:
            await ctx.send(f"❌ Erro ao silenciar: {e}")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def softban(self, ctx, member: discord.Member, *, motivo="Sem motivo"):
        """Ban + unban automático (limpa mensagens)"""
        try:
            await member.ban(reason=motivo)
            await asyncio.sleep(1)
            await ctx.guild.unban(member)
            embed = discord.Embed(title="⚠️ Soft Ban", description=f"**Alvo:** {member}\n**Motivo:** {motivo}\n*Mensagens limpas*", color=discord.Color.yellow())
            await ctx.send(embed=embed)
            await self.log_action(ctx.guild, "⚠️ Soft Ban", f"Alvo: {member}\nMod: {ctx.author}\nMotivo: {motivo}", discord.Color.yellow())
        except Exception as e:
            await ctx.send(f"❌ Erro ao fazer soft ban: {e}")

    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def warn(self, ctx, member: discord.Member, *, motivo="Sem motivo"):
        """Avisa um usuário"""
        try:
            async with aiosqlite.connect(self.bot.db_name) as db:
                await db.execute('INSERT INTO warns (user_id, guild_id, reason, admin_id) VALUES (?, ?, ?, ?)',
                                (str(member.id), str(ctx.guild.id), motivo, str(ctx.author.id)))
                await db.commit()
            embed = discord.Embed(title="⚠️ Aviso", description=f"**Alvo:** {member}\n**Motivo:** {motivo}", color=discord.Color.yellow())
            await ctx.send(embed=embed)
            await self.log_action(ctx.guild, "⚠️ Aviso", f"Alvo: {member}\nMod: {ctx.author}\nMotivo: {motivo}", discord.Color.yellow())
        except Exception as e:
            await ctx.send(f"❌ Erro ao avisar: {e}")

    @commands.command()
    async def warns(self, ctx, member: discord.Member):
        """Ver avisos de um usuário"""
        try:
            async with aiosqlite.connect(self.bot.db_name) as db:
                cursor = await db.execute('SELECT reason, admin_id FROM warns WHERE user_id = ? AND guild_id = ?',
                                        (str(member.id), str(ctx.guild.id)))
                warns_list = await cursor.fetchall()
            
            if not warns_list:
                return await ctx.send(f"✅ {member} não tem avisos!")
            
            embed = discord.Embed(title=f"⚠️ Avisos de {member}", color=discord.Color.yellow())
            for i, (reason, admin_id) in enumerate(warns_list, 1):
                embed.add_field(name=f"Aviso #{i}", value=f"Motivo: {reason}", inline=False)
            
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Erro: {e}")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int):
        """Limpa mensagens do canal"""
        if amount > 100:
            amount = 100
        try:
            deleted = await ctx.channel.purge(limit=amount)
            await ctx.send(f"🧹 {len(deleted)} mensagens apagadas.", delete_after=5)
        except Exception as e:
            await ctx.send(f"❌ Erro: {e}")


# ==================== AUTOMOD COG ====================
class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.spam_tracker = {}  # {user_id: [timestamp, timestamp, ...]}

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def addfilter(self, ctx, *, palavra):
        """Adiciona palavra ao filtro"""
        try:
            async with aiosqlite.connect(self.bot.db_name) as db:
                await db.execute('INSERT INTO filter_words (guild_id, word) VALUES (?, ?)',
                                (str(ctx.guild.id), palavra.lower()))
                await db.commit()
            await ctx.send(f"✅ Palavra '{palavra}' adicionada ao filtro!")
        except Exception as e:
            await ctx.send(f"❌ Erro: {e}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def removefilter(self, ctx, *, palavra):
        """Remove palavra do filtro"""
        try:
            async with aiosqlite.connect(self.bot.db_name) as db:
                await db.execute('DELETE FROM filter_words WHERE guild_id = ? AND word = ?',
                                (str(ctx.guild.id), palavra.lower()))
                await db.commit()
            await ctx.send(f"✅ Palavra '{palavra}' removida do filtro!")
        except Exception as e:
            await ctx.send(f"❌ Erro: {e}")

    @commands.command()
    async def listfilter(self, ctx):
        """Lista palavras filtradas"""
        try:
            async with aiosqlite.connect(self.bot.db_name) as db:
                cursor = await db.execute('SELECT word FROM filter_words WHERE guild_id = ?',
                                        (str(ctx.guild.id),))
                words = await cursor.fetchall()
            
            if not words:
                return await ctx.send("Nenhuma palavra filtrada!")
            
            embed = discord.Embed(title="🚫 Palavras Filtradas", color=discord.Color.red())
            word_list = ", ".join([w[0] for w in words])
            embed.description = word_list
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Erro: {e}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def slow(self, ctx, segundos: int = 5):
        """Ativa modo lento no canal"""
        try:
            await ctx.channel.edit(slowmode_delay=segundos)
            await ctx.send(f"🐢 Modo lento ativado: {segundos}s entre mensagens")
        except Exception as e:
            await ctx.send(f"❌ Erro: {e}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def slowoff(self, ctx):
        """Desativa modo lento"""
        try:
            await ctx.channel.edit(slowmode_delay=0)
            await ctx.send("⚡ Modo lento desativado!")
        except Exception as e:
            await ctx.send(f"❌ Erro: {e}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def antispam(self, ctx, status: str):
        """Ativa/desativa anti-spam"""
        if status.lower() == "on":
            async with aiosqlite.connect(self.bot.db_name) as db:
                await db.execute('INSERT OR REPLACE INTO settings (guild_id, antispam) VALUES (?, ?)',
                                (str(ctx.guild.id), 1))
                await db.commit()
            await ctx.send("✅ Anti-spam ativado!")
        elif status.lower() == "off":
            async with aiosqlite.connect(self.bot.db_name) as db:
                await db.execute('INSERT OR REPLACE INTO settings (guild_id, antispam) VALUES (?, ?)',
                                (str(ctx.guild.id), 0))
                await db.commit()
            await ctx.send("❌ Anti-spam desativado!")
        else:
            await ctx.send("Use: `!antispam on` ou `!antispam off`")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        # Filtro de palavras
        async with aiosqlite.connect(self.bot.db_name) as db:
            cursor = await db.execute('SELECT word FROM filter_words WHERE guild_id = ?',
                                    (str(message.guild.id),))
            words = await cursor.fetchall()
        
        if words:
            msg_lower = message.content.lower()
            for (word,) in words:
                if word in msg_lower:
                    try:
                        await message.delete()
                        await message.channel.send(f"⚠️ {message.author.mention} sua mensagem foi removida (contém palavra filtrada)!", delete_after=5)
                    except:
                        pass
                    return

        # Anti-spam
        async with aiosqlite.connect(self.bot.db_name) as db:
            cursor = await db.execute('SELECT antispam FROM settings WHERE guild_id = ?',
                                    (str(message.guild.id),))
            result = await cursor.fetchone()
        
        if result and result[0]:
            user_id = message.author.id
            now = datetime.now().timestamp()
            
            if user_id not in self.spam_tracker:
                self.spam_tracker[user_id] = []
            
            self.spam_tracker[user_id] = [t for t in self.spam_tracker[user_id] if now - t < 5]
            self.spam_tracker[user_id].append(now)
            
            if len(self.spam_tracker[user_id]) > 5:
                try:
                    await message.delete()
                    await message.channel.send(f"⚠️ {message.author.mention} você está enviando mensagens muito rápido!", delete_after=5)
                except:
                    pass


# ==================== ROLE MANAGER COG ====================
class RoleManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def painel_cargos(self, ctx):
        """Cria botões com cargos"""
        roles = ctx.guild.roles[-4:-1]
        if not roles:
            return await ctx.send("❌ Sem cargos suficientes.")

        view = ui.View(timeout=None)
        for role in roles:
            button = ui.Button(label=role.name, style=discord.ButtonStyle.primary, custom_id=f"role_{role.id}")
            
            async def cb(interaction, r=role):
                if r in interaction.user.roles:
                    await interaction.user.remove_roles(r)
                    await interaction.response.send_message(f"❌ Removido: {r.name}", ephemeral=True)
                else:
                    await interaction.user.add_roles(r)
                    await interaction.response.send_message(f"✅ Adicionado: {r.name}", ephemeral=True)
            
            button.callback = cb
            view.add_item(button)
        
        await ctx.send("🎭 **Escolha seus Cargos:**", view=view)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setautorole(self, ctx, role: discord.Role):
        """Define cargo automático ao entrar"""
        async with aiosqlite.connect(self.bot.db_name) as db:
            await db.execute('INSERT OR REPLACE INTO settings (guild_id, autorole_id) VALUES (?, ?)',
                            (str(ctx.guild.id), str(role.id)))
            await db.commit()
        await ctx.send(f"🆕 AutoRole definido: {role.name}")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def addrole(self, ctx, member: discord.Member, role: discord.Role):
        """Adiciona cargo a um usuário"""
        if ctx.author.top_role <= role:
            return await ctx.send("❌ Você não pode dar um cargo maior que o seu.")
        try:
            await member.add_roles(role)
            await ctx.send(f"✅ Cargo {role.name} dado a {member.name}")
        except Exception as e:
            await ctx.send(f"❌ Erro: {e}")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def removerole(self, ctx, member: discord.Member, role: discord.Role):
        """Remove cargo de um usuário"""
        try:
            await member.remove_roles(role)
            await ctx.send(f"✅ Cargo {role.name} removido de {member.name}")
        except Exception as e:
            await ctx.send(f"❌ Erro: {e}")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Adiciona cargo automático ao entrar"""
        async with aiosqlite.connect(self.bot.db_name) as db:
            cursor = await db.execute('SELECT autorole_id FROM settings WHERE guild_id = ?',
                                    (str(member.guild.id),))
            res = await cursor.fetchone()
        if res and res[0]:
            role = member.guild.get_role(int(res[0]))
            if role:
                try:
                    await member.add_roles(role)
                except:
                    pass


# ==================== TICKET SYSTEM COG ====================
class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setup_ticket(self, ctx):
        """Cria o painel de tickets"""
        view = ui.View(timeout=None)
        btn = ui.Button(label="Abrir Ticket", style=discord.ButtonStyle.success, emoji="📩")
        
        async def cb(interaction):
            cat = discord.utils.get(interaction.guild.categories, name="Tickets")
            if not cat:
                cat = await interaction.guild.create_category("Tickets")
            
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True),
                interaction.guild.me: discord.PermissionOverwrite(read_messages=True)
            }
            ch = await interaction.guild.create_text_channel(f"ticket-{interaction.user.name}", category=cat, overwrites=overwrites)
            await interaction.response.send_message(f"✅ Ticket criado: {ch.mention}", ephemeral=True)
            await ch.send(f"{interaction.user.mention} Como podemos ajudar? Digite `!fechar` para encerrar.")
        
        btn.callback = cb
        view.add_item(btn)
        embed = discord.Embed(title="Central de Suporte", description="Clique abaixo para abrir um ticket.", color=discord.Color.green())
        await ctx.send(embed=embed, view=view)

    @commands.command(name="fechar")
    async def fechar_tkt(self, ctx):
        """Fecha um ticket"""
        if "ticket-" in ctx.channel.name:
            await ctx.send("🔒 Fechando em 3 segundos...")
            await asyncio.sleep(3)
            try:
                await ctx.channel.delete()
            except:
                pass


# ==================== INTERACTIONS COG ====================
class Interactions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def box(self, ctx, *, texto):
        """Coloca texto em uma caixa ASCII"""
        lines = texto.split('\n')
        max_len = max(len(line) for line in lines) if lines else 0
        
        box = "```\n"
        box += "┌" + "─" * (max_len + 2) + "┐\n"
        for line in lines:
            box += f"│ {line.ljust(max_len)} │\n"
        box += "└" + "─" * (max_len + 2) + "┘\n"
        box += "```"
        
        await ctx.send(box)

    @commands.command()
    async def curtir(self, ctx):
        """Reage com 👍 em uma mensagem aleatória"""
        try:
            async for message in ctx.channel.history(limit=50):
                if not message.author.bot and message != ctx.message:
                    await message.add_reaction("👍")
                    await ctx.send(f"👍 Curtida adicionada em mensagem de {message.author.name}!", delete_after=3)
                    return
        except Exception as e:
            await ctx.send(f"❌ Erro: {e}")

    @commands.Cog.listener()
    async def on_message(self, message):
        """Reage com 🔥 em mensagens com MAIÚSCULA"""
        if message.author.bot:
            return
        
        # Verifica se tem letras e se a maioria é maiúscula
        letters = [c for c in message.content if c.isalpha()]
        if letters and len([c for c in letters if c.isupper()]) / len(letters) > 0.7:
            try:
                await message.add_reaction("🔥")
            except:
                pass


# ==================== AI COG ====================
class AIFeatures(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def pergunte(self, ctx, *, q):
        """Pergunta algo para a IA"""
        if not model:
            return await ctx.send("❌ IA não configurada no .env")
        
        async with ctx.typing():
            try:
                res = await asyncio.to_thread(model.generate_content, q)
                text = res.text[:2000]
                embed = discord.Embed(title="🧠 Resposta da IA", description=text, color=discord.Color.teal())
                await ctx.send(embed=embed)
            except Exception as e:
                await ctx.send(f"❌ Erro na IA: {e}")


# ==================== GET PREFIX ====================
async def get_prefix(bot, message):
    if not message.guild:
        return '!'
    if message.guild.id in bot.prefix_cache:
        return bot.prefix_cache[message.guild.id]
    
    async with aiosqlite.connect(bot.db_name) as db:
        cursor = await db.execute('SELECT prefix FROM settings WHERE guild_id = ?', (str(message.guild.id),))
        result = await cursor.fetchone()
    
    prefix = result[0] if result else '!'
    bot.prefix_cache[message.guild.id] = prefix
    return prefix


# ==================== MAIN BOT CLASS ====================
class RyuBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix=get_prefix, intents=intents, help_command=None)
        self.db_name = 'Ryu_bot.db'
        self.prefix_cache = {}

    async def setup_hook(self):
        await self.init_db()
        await self.add_cog(SystemCog(self))
        await self.add_cog(Moderation(self))
        await self.add_cog(AutoMod(self))
        await self.add_cog(RoleManager(self))
        await self.add_cog(TicketSystem(self))
        await self.add_cog(Interactions(self))
        if model:
            await self.add_cog(AIFeatures(self))
        print(f"✅ Bot logado como {self.user}")

    async def init_db(self):
        """Inicializa banco de dados"""
        async with aiosqlite.connect(self.db_name) as db:
            # Settings
            await db.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    guild_id TEXT PRIMARY KEY,
                    log_channel_id TEXT,
                    autorole_id TEXT,
                    prefix TEXT DEFAULT '!',
                    antispam INTEGER DEFAULT 0
                )
            ''')
            
            # Warns
            await db.execute('''
                CREATE TABLE IF NOT EXISTS warns (
                    id INTEGER PRIMARY KEY,
                    user_id TEXT,
                    guild_id TEXT,
                    reason TEXT,
                    admin_id TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Filter words
            await db.execute('''
                CREATE TABLE IF NOT EXISTS filter_words (
                    id INTEGER PRIMARY KEY,
                    guild_id TEXT,
                    word TEXT
                )
            ''')
            
            await db.commit()


# ==================== RUN BOT ====================
if __name__ == "__main__":
    bot = RyuBot()
    bot.run(TOKEN)
