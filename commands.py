from discord.ext import commands
import discord
import collections
import datetime
import time
import pprint
import sys
from random import randint
# import pymorphy2
import json
import requests
from asyncpg.exceptions import UniqueViolationError
import mcstatus
from socket import timeout as socket_timeout
from database import PostgresController
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import asyncio
import os


def find_color(ctx):
    """Ищет цвет отрисовки бота. Если это цвет по умолчанию или мы находимся в ЛС, вернет "greyple", цвет Дискорда."""

    try:
        if ctx.guild.me.color == discord.Color.default():
            color = discord.Color.greyple()
        else:
            color = ctx.guild.me.color
    except AttributeError:  # Если это ЛС
        color = discord.Color.greyple()
    return color


class Commands(commands.Cog):
    """Команды для бота пингера"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def пинг(self, ctx, ip):
        """Пинг сервера и показ его основной информации"""
        print(f'{ctx.author.name} использовал команду "{ctx.message.content}"')
        embed = discord.Embed(
            title=f'Пингую {ip}...',
            description=f"Подождите немного, я вас упомяну когда закончу",
            color=discord.Color.orange())
        await ctx.send(embed=embed)
        response = requests.get(f"https://api.mcsrvstat.us/2/{ip}")
        result = json.loads(response.text)
        server = mcstatus.MinecraftServer.lookup(ip)
        try:
            status = server.status()
            online = True
        except socket_timeout: online = False
        if online:
            embed = discord.Embed(
                title=f'Результаты пинга {server.host}',
                description=f"Цифровое айпи: {result['ip']}:{str(server.port)}\n**Онлайн**",
                color=discord.Color.green())

            embed.set_thumbnail(url=f'https://api.mcsrvstat.us/icon/{ip}')
            embed.add_field(name="Версия сервера", value=result['version'])
            embed.add_field(name="Используемое ПО", value=status.version.name)
            embed.add_field(name="Онлайн", value=f"{status.players.online}/{status.players.max}")
            embed.add_field(name="Мотд", value=f"{result['motd']['clean'][0]}\n{result['motd']['clean'][1]}")
            embed.set_footer(text=f'Для получения ссылки на редактирование МОТД, напишите "мотд {ip}"')

            await ctx.send(ctx.author.mention, embed=embed)
        else:
            embed = discord.Embed(
                title=f'Результаты пинга {ip}',
                description=f"\n\n**Офлайн**",
                color=discord.Color.red())

            embed.add_field(name="Не удалось пингануть сервер",
                            value='Возможно вы указали неверный айпи, или сервер сейчас выключен')
            await ctx.send(ctx.author.mention, embed=embed)

    @commands.command()
    async def мотд(self, ctx, ip):
        """Показывает мотд и ссылку на редактирование сервера"""
        print(f'{ctx.author.name} использовал команду "{ctx.message.content}"')
        embed = discord.Embed(
            title=f'Получаю данные сервера {ip}...',
            description=f"Подождите немного, я вас упомяну когда закончу",
            color=discord.Color.orange())
        await ctx.send(embed=embed)
        server = mcstatus.MinecraftServer.lookup(ip)
        try:
            status = server.status()
            online = True
        except socket_timeout: online = False
        if online:
            motd = f"{status.raw['description']['text']}"
            motd1 = motd.replace(' ', '+')
            motdURL = motd1.replace('\n', '%0A')
            embed = discord.Embed(
                title=f'Подробное мотд сервера {ip}',
                description=f"Эта команда дает возможность скопировать мотд и вставить на свой сервер",
                color=discord.Color.green())

            embed.set_thumbnail(url=f'https://api.mcsrvstat.us/icon/{ip}')
            embed.add_field(name="Мотд", value=f"{status.description}")
            embed.add_field(name="Ссылка на редактирование", value="https://mctools.org/motd-creator?text=" + motdURL)
            await ctx.send(ctx.author.mention, embed=embed)
        else:
            embed = discord.Embed(
                title=f'Подробное мотд сервера {ip}',
                description=f"Эта команда дает возможность скопировать мотд и вставить на свой сервер",
                color=discord.Color.red())

            embed.add_field(name="Не удалось получить данные с сервера",
                            value='Возможно вы указали неверный айпи, или сервер сейчас выключен')
            await ctx.send(ctx.author.mention, embed=embed)

    @commands.command()
    async def стата(self, ctx, server):  # TODO Добавить график и прочую красоту
        """Статистика сервера"""
        print(f'{ctx.author.name} использовал команду "{ctx.message.content}"')
        embed = discord.Embed(
            title=f'Получаю данные сервера {server}...',
            description=f"Подождите немного, я вас упомяну когда закончу",
            color=discord.Color.orange())
        await ctx.send(embed=embed)
        pg_controller = await PostgresController.get_instance()
        ip_from_alias = await pg_controller.get_ip_alias(server)
        if len(ip_from_alias) != 0:
            server = str(ip_from_alias[0]['numip'])[0:-3] + ':' + str(ip_from_alias[0]['port'])
        response = requests.get(f"https://api.mcsrvstat.us/2/{server}")
        result = json.loads(response.text)
        mcserver = mcstatus.MinecraftServer.lookup(server)
        try:
            status = mcserver.status()
            online = True
        except socket_timeout: online = False
        database_server = await pg_controller.get_server(result['ip'], mcserver.port)
        if online and len(database_server) != 0:
            if database_server[0]['alias'] != None:
                server = database_server[0]['alias']
            embed = discord.Embed(
                title=f'Статистика сервера {server}',
                description=f"Цифровое айпи: {result['ip']}:{str(mcserver.port)}\n**Онлайн**",
                color=discord.Color.green())

            online_yest = await pg_controller.get_ping_yest(result['ip'], mcserver.port)
            if len(online_yest) == 0: online_yest = 'Нету информации'
            else: online_yest = str(online_yest[0]['players'])

            embed.set_thumbnail(url=f"https://api.mcsrvstat.us/icon/{result['ip']}:{str(mcserver.port)}")
            embed.add_field(name="Текущий онлайн", value=str(status.players.online)+'/'+str(status.players.max))
            embed.add_field(name="Онлайн сутки назад в это же время", value=online_yest)
            embed.add_field(name="Рекорд онлайна за всё время", value=str(database_server[0]['record']))
            embed.set_footer(text=f'Для большей информации о сервере напишите "пинг {server}"')

            pings = await pg_controller.get_pings(result['ip'], mcserver.port)
            fig, ax = plt.subplots()
            arrOnline = []
            arrTime = []
            date = datetime.datetime.now().strftime("%Y-%m-%d ")
            for ping in pings:
                arrOnline.append(int(ping['players']))
                strTime = date + str(ping['time'])
                arrTime.append(datetime.datetime.strptime(strTime, '%Y-%m-%d %H:%M:%S'))
            myFmt = mdates.DateFormatter('%H:%M')
            ax.xaxis.set_major_formatter(myFmt)
            ax.hist(arrTime, arrOnline)

            plt.xlabel('Время')
            plt.ylabel('Онлайн')
            plt.title('Статистика')

            fileName = result['ip']+'_'+str(mcserver.port)+'.png'
            try: fig.savefig('./grafics/'+fileName)
            except FileNotFoundError: 
                os.mkdir('./grafics/')
                fig.savefig('./grafics/'+fileName)
            file = discord.File('./grafics/'+fileName, filename=fileName)
            embed.set_image(url='attachment://'+fileName)

            await ctx.send(ctx.author.mention, embed=embed, file=file)

            await asyncio.sleep(60)
            try: os.remove('./grafics/'+fileName)
            except FileNotFoundError: pass
        else:
            embed = discord.Embed(
                title=f'Статистика сервера {server}',
                description="**Офлайн**",
                color=discord.Color.red())

            embed.add_field(name="Не удалось получить статистику сервера",
                            value='Возможно вы указали неверный айпи/алиас, или сервер еще не добавлен')
            await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def добавить(self, ctx, server):
        """Добавление сервера в бота"""
        print(f'{ctx.author.name} использовал команду "{ctx.message.content}"')
        response = requests.get(f"https://api.mcsrvstat.us/2/{server}")
        result = json.loads(response.text)
        mcserver = mcstatus.MinecraftServer.lookup(server)
        try:
            mcserver.status()
            online = True
        except socket_timeout: online = False
        pg_controller = await PostgresController.get_instance()
        if online:
            try: await pg_controller.add_server(result['ip'], result['port'])
            except UniqueViolationError: # сервер уже добавлен
                embed = discord.Embed(
                    title=f'Не удалось добавить сервер {server}',
                    description="**Онлайн**",
                    color=discord.Color.red())

                embed.add_field(name="Не удалось добавить сервер",
                                value='Сервер уже добавлен')
                await ctx.send(ctx.author.mention, embed=embed)
                return

            embed = discord.Embed(
                title=f'Добавил сервер {server}',
                description=f"Цифровое айпи: {result['ip']}:{str(result['port'])}\n**Онлайн**",
                color=discord.Color.green())

            embed.set_thumbnail(url=f'https://api.mcsrvstat.us/icon/{server}')
            embed.add_field(name="Сервер успешно добавлен",
                            value='Напишите "помощь" для получения большей информации о серверах')
            embed.set_footer(text=f'Теперь вы можете использовать "стата {server}" или "алиас (алиас) {server}"')

            await ctx.send(ctx.author.mention, embed=embed)
        else:
            embed = discord.Embed(
                title=f'Не удалось добавить сервер {server}',
                description="**Офлайн**",
                color=discord.Color.red())

            embed.add_field(name="Не удалось добавить сервер",
                            value='Возможно вы указали неверный айпи, или сервер сейчас выключен')
            await ctx.send(ctx.author.mention, embed=embed)

    @commands.command()
    async def help(self, ctx):
        """Это команда помощи!"""

        cmds = sorted([c for c in self.bot.commands if not c.hidden], key=lambda c: c.name)

        embed = discord.Embed(
            title="Команда помощи",
            description="Я пингую сервер каждые 5 минут, и показываю его статистику! "
                        "Я довольно простой бот в использовании. Мой префикс это буквально ничего, "
                        "вам не нужно ставить префикс перед командами."
                        f"\n\nВот короткий список моих команд:", color=find_color(ctx))
        embed.set_footer(text="Примечание: Нет, я не пингую сервера перед тем как вы меня добавите")
        for c in cmds:
            embed.add_field(name=c.name, value=c.help, inline=False)

        await ctx.send(embed=embed)

    @commands.command(aliases=["info"])
    async def about(self, ctx):
        """Немного базовой информации про меня"""

        embed = discord.Embed(
            title=str(self.bot.user), description=self.bot.app_info.description +
                                                  f"\n\n**ID**: {self.bot.app_info.id}", color=find_color(ctx))

        embed.set_thumbnail(url=self.bot.app_info.icon_url)
        embed.add_field(name="Владелец", value=self.bot.app_info.owner)
        embed.add_field(name="Количество серверов", value=len(self.bot.guilds))
        embed.add_field(name="Количество пользователей", value=len(self.bot.users))
        embed.add_field(
            name="Язык программирования",
            value=f"Python {sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}")
        embed.add_field(
            name="Библиотека", value="[discord.py](https://github.com/Rapptz/discord.py)")
        embed.add_field(
            name="Лицензия",
            value="[CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/)")
        embed.add_field(
            name="Открытый код", value="https://github.com/PerchunPak/sunshinedsbot", inline=False)
        embed.set_footer(
            text="Примечание: Оригинальный автор не Perchun_Pak#9236, а NinjaSnail1080#8581")

        await ctx.send(embed=embed)

    @commands.command()
    async def count(self, ctx, user: discord.User = None):
        """Узнайте, сколько раз пользователь сказал "ладно"
        Формат: `count <@пинг пользователя>`
        Если вы не указываете пинг, я укажу **вашу** статистику
        """
        if user is None:
            user = ctx.author
        if user == self.bot.user:
            return await ctx.send(
                """@MATUKITE has said the N-word **1,070,855 times**,
__1,070,801 of which had a hard-R__

They've said the N-word __23,737 times__ since they were last investigated
            """)
        if user.bot:
            return await ctx.send(
                "Я не считаю " + '"ладно-слова"' + ", сказанные ботами. Представляете, насколько это было бы странно?")

        try:
            count = self.bot.lwords[user.id]
        except:
            return await ctx.send(f"{user.mention} еще ни разу не говорил " + '"ладно"' + ". Странный чел")

        if count["total"]:
            # morph = pymorphy2.MorphAnalyzer()
            # word = morph.parse('раз')[0]
            # raz = word.inflect(word.tag.grammemes, ({'gent'}))
            # print(raz)
            msg = f"{user.mention} сказал ладно **{count['total']:,} раз{'а' if count['total'] == 2 or count['total'] == 3 or count['total'] == 4 else ''}**"
            if "last_time" in count:
                since_last = count["total"] - count["last_time"]
                if since_last:
                    msg += (f".\n\nТак же {user.mention} сказал ладно __{since_last:,} "
                            f"раз{'а' if since_last == 2 or since_last == 3 or since_last == 4 else 'а'}__ "
                            "с прошлой проверки")
            await ctx.send(msg)
            self.bot.lwords[user.id]["last_time"] = self.bot.lwords[user.id]["total"]
        else:
            await ctx.send(f"{user.mention} еще ни разу не говорил " + '"ладно"' + ". Странный чел")

    @count.error
    async def count_error(self, ctx, exc):
        if isinstance(exc, commands.BadArgument):
            return await ctx.send(exc)

    @commands.command()
    async def invite(self, ctx):
        """Скидывает ссылку чтобы Вы могли пригласить бота на свой сервер"""

        await ctx.send("Это моя пригласительная ссылка чтобы Вы могли считать " + '"ладно"' + " тоже:\n"
                                                                                              f"https://discordapp.com/oauth2/authorize?client_id={self.bot.app_info.id}"
                                                                                              "&scope=bot&permissions=8")

    @commands.command()
    async def stats(self, ctx):
        """Показывает мою статистику"""

        await ctx.channel.trigger_typing()

        uptime = datetime.datetime.utcnow() - self.bot.started_at

        # * This code was copied from my other bot, MAT
        y = int(uptime.total_seconds()) // 31557600  # * Number of seconds in 356.25 days
        mo = int(uptime.total_seconds()) // 2592000 % 12  # * Number of seconds in 30 days
        d = int(uptime.total_seconds()) // 86400 % 30  # * Number of seconds in 1 day
        h = int(uptime.total_seconds()) // 3600 % 24  # * Number of seconds in 1 hour
        mi = int(uptime.total_seconds()) // 60 % 60  # * etc.
        se = int(uptime.total_seconds()) % 60

        frmtd_uptime = []
        if y != 0:
            frmtd_uptime.append(f"{y}г")
        if mo != 0:
            frmtd_uptime.append(f"{mo}мес")
        if d != 0:
            frmtd_uptime.append(f"{d}дн")
        if h != 0:
            frmtd_uptime.append(f"{h}ч")
        if mi != 0:
            frmtd_uptime.append(f"{mi}м")
        if se != 0:
            frmtd_uptime.append(f"{se}с")

        allUsers = f"{len(self.bot.lwords):,}"
        for _ in range(1): randomInt = randint(0, 100)
        embed = discord.Embed(
            description=f"ID: {self.bot.user.id}",
            timestamp=datetime.datetime.utcnow(),
            color=find_color(ctx))
        embed.add_field(name="Количество серверов", value=f"{len(self.bot.guilds):,} серверов")
        embed.add_field(name="Количество пользовотелей", value=f"{len(self.bot.users):,} уникальных пользователей")
        embed.add_field(
            name="Количество каналов",
            value=f"{len(list(self.bot.get_all_channels()) + self.bot.private_channels):,} "
                  "каналов")
        embed.add_field(
            name="Использование памяти",
            value=f"{round(self.bot.process.memory_info().rss / 1000000, 2)} МБ")
        embed.add_field(name="Пинг", value=f"{round(self.bot.latency * 1000, 2)}мс")
        embed.add_field(name="Аптайм", value=" ".join(frmtd_uptime) + " после прошлого рестарта")
        embed.add_field(
            name="Количество пользователей кто произнес " + '"ладно"',
            value=str(int(allUsers) - 1),
            inline=False)
        embed.add_field(
            name="Всего слов насчитано",
            value=f"{self.bot.lwords[0]['total']:,} ",
            inline=False)
        embed.set_author(name="Статистика", icon_url=self.bot.user.avatar_url)
        embed.set_footer(text="Эти статистические данные верны на: " + str(randomInt) + "%")

        await ctx.send(embed=embed)

    @commands.command(aliases=["leaderboard", "high"])
    @commands.guild_only()
    async def top(self, ctx, param: str = None):
        """Показывает таблицу лидеров по произношению слова "ладно" на этом сервере. Используйте `top global` чтобы посмотреть таблицу лидеров всех серверов
        Примечание: Если пользователь сказал "ладно" на другом сервере, на котором я тоже есть, они будут приняты во внимание.
        """
        await ctx.channel.trigger_typing()

        def create_leaderboard():
            leaderboard = {}
            if param == "global":
                for u, n in self.bot.lwords.items():
                    if self.bot.get_user(u):
                        leaderboard.update({self.bot.get_user(u): n["total"]})
                leaderboard = dict(collections.Counter(leaderboard).most_common(10))
            else:
                for m in ctx.guild.members:
                    if m.id in self.bot.lwords and not m.bot:
                        if self.bot.lwords[m.id]["total"]:
                            leaderboard.update({m: self.bot.lwords[m.id]["total"]})
                leaderboard = dict(collections.Counter(leaderboard).most_common(10))
            return leaderboard

        leaderboard = await self.bot.loop.run_in_executor(None, create_leaderboard)
        if not len(leaderboard):
            return await ctx.send("На этом сервере еще никто не сказал " + '"ладно"')

        description = "\n"
        counter = 1
        for m, c in leaderboard.items():
            description += (f"**{counter}.** {m if param == 'global' else m.mention} - __{c:,} "
                            f"раз{'а' if c == 2 or c == 3 or c == 4 else ''}__\n")
            counter += 1

        description = description.replace("**1.**", ":first_place:").replace("**2.**", ":second_place:").replace(
            "**3.**", ":third_place:")

        embed = discord.Embed(description=description, color=find_color(ctx),
                              timestamp=datetime.datetime.utcnow())
        if param == "global":
            embed.set_author(
                name=f"Топ за все время")
        else:
            embed.set_author(
                name=f"Топ сервера {ctx.guild.name}", icon_url=ctx.guild.icon_url)

        for _ in range(1): randomInt = randint(0, 100)
        embed.set_footer(
            text="Эти списки верны на: " + str(randomInt) + "%", icon_url=self.bot.user.avatar_url)

        await ctx.send(embed=embed)

    @top.error
    async def top_error(self, ctx, exc):
        if isinstance(exc, commands.NoPrivateMessage):
            return await ctx.send(exc)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def edit(self, ctx, user_id: int, total: int, last_time: int = None):
        """Отредактируйте запись пользователя в ДБ или добавьте новую"""
        totalBefore = self.bot.lwords[user_id]['total']
        if total < totalBefore:
            self.bot.lwords[0]["total"] -= (totalBefore - (self.bot.lwords[user_id]['total']))
            if last_time:
                self.bot.lwords[user_id] = {"id": user_id, "total": total, "last_time": last_time}
            else:
                self.bot.lwords[user_id] = {"id": user_id, "total": total}
        elif total > totalBefore:
            self.bot.lwords[0]["total"] += (int(self.bot.lwords[user_id]['total']) - totalBefore)
            if last_time:
                self.bot.lwords[user_id] = {"id": user_id, "total": total, "last_time": last_time}
            else:
                self.bot.lwords[user_id] = {"id": user_id, "total": total}
        else:
            await ctx.send("Неизвестная ошибка")
        await ctx.send("Готово")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def pop(self, ctx, user_id: int):
        """Удалите пользователя с ДБ"""
        self.bot.lwords[0]["total"] -= int(self.bot.lwords[user_id]['total'])
        try:
            self.bot.lwords.pop(user_id)
            await ctx.send("Готово")
        except KeyError as e:
            await ctx.send(f"Ошибка: ```{e}```")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def execute(self, ctx, *, query):
        """Выполнить запрос в базе данных"""

        try:
            with ctx.channel.typing():
                async with self.bot.pool.acquire() as conn:
                    result = await conn.execute(query)
            await ctx.send(f"Запрос выполнен:```{result}```")
        except Exception as e:
            await ctx.send(f"Ошибка:```{e}```")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def fetch(self, ctx, *, query):
        """Выполнить поиск в базе данных"""

        try:
            with ctx.channel.typing():
                async with self.bot.pool.acquire() as conn:
                    result = await conn.fetch(query)

            fmtd_result = pprint.pformat([dict(i) for i in result])
            await ctx.send(f"Поиск выполнен:```{fmtd_result}```")
        except Exception as e:
            await ctx.send(f"Ошибка:```{e}```")

    @commands.command(aliases=["resetstatus"], hidden=True)
    @commands.is_owner()
    async def restartstatus(self, ctx):
        await self.bot.change_presence(status=discord.Status.online, activity=discord.Activity(
            name=f'кто сколько раз сказал "ладно"', type=discord.ActivityType.competing))

        await ctx.send("Статус был сброшен")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def setstatus(self, ctx, status):
        """Изменить статус бота"""

        if status.startswith("on"):
            await self.bot.change_presence(status=discord.Status.online)
        elif status.startswith("id"):
            await self.bot.change_presence(status=discord.Status.idle)
        elif status.startswith("d"):
            await self.bot.change_presence(status=discord.Status.dnd)
        elif status.startswith("off") or status.startswith("in"):
            await self.bot.change_presence(status=discord.Status.invisible)
        else:
            await ctx.send("Недействительный статус")

        await ctx.send("Поставить новый статус")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def updatedb(self, ctx):
        temp = await ctx.send("Обновление вручную... Это может занять несколько минут... Подождите...")
        with ctx.channel.typing():
            start = time.perf_counter()
            async with self.bot.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO lwords
                    (id)
                    VALUES {}
                    ON CONFLICT
                        DO NOTHING
                ;""".format(", ".join([f"({u})" for u in self.bot.lwords])))

                for data in self.bot.lwords.copy().values():
                    await conn.execute("""
                        UPDATE lwords
                        SET total = {}
                        WHERE id = {}
                    ;""".format(data["total"], data["id"]))

        delta = time.perf_counter() - start
        mi = int(delta) // 60
        sec = int(delta) % 60
        ms = round(delta * 1000 % 1000)
        await temp.delete()
        await ctx.send(f"Завершено обновление базы данных ({mi}м {sec}с {ms}мс)")


def setup(bot):
    bot.add_cog(Commands(bot))
