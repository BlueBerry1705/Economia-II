import os
import discord
import asyncio
import datetime
import random
from faker import Faker
from unidecode import unidecode

import Economia
from Utils import *
from Commands import *
from Mapa import *

from discord_easy_commands import EasyBot

intents = discord.Intents.all()
bot = EasyBot(intents = intents)

current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

user_id = None
g = 696380553515106380
chat_mafia = 1138030632467964037
chat_empresario = 1138030671089111091
chat_dirigente = 1138030751108038706
chat_general1 = 1138030792979795988
chat_general2 = 1138030893856981012

game = Economia()


game.load_data()

CargarMapa()

ajedrez = Ajedrez()

ajedrez.load_data()

#comandos de economia
@bot.event
async def on_message(message):
  if message.author.bot:
    return
  
  #**ECONOMIA**
  if message.author not in game.eliminados:  
    if message.channel.id == chat_general1 or message.channel.id == chat_general2 or message.channel.id == chat_dirigente or message.channel.id == chat_empresario or message.channel.id == chat_mafia:
      if has_role(message.author, "Economia"):
        if obtener_rol_usuario(message.author) is None:      
          if message.content == '+start' or message.content.startswith('+start '):
            await event_command(message)
          else:
            await message.channel.send(embed=discord.Embed(title='Espera!', description=f'{message.author.mention}, vemos que aún no has seleccionado equipo!\n Para disfrutar de la Economía 2, usa el comando +start en el chat global y selecciona tu equipo!', color=discord.Color.red()))

        if message.content == '+help' or message.content.startswith('+help '):
          await help(message)

      if has_role(message.author, 'Moderador') or has_role(message.author, 'Mini pendejos con poder'):
        if message.content == '+add-money' or message.content.startswith('+add-money '):
          await addmoney_command(game, message)

        elif message.content == '+remove-money' or message.content.startswith('+remove-money '):
          await remove_command(game, message)

        elif message.content == '+reset' or message.content.startswith('+reset '):
          await reset_command(game, message)
        
        elif message.content == '+actualizar' or message.content.startswith('+actualizar '):
          #await actualizar_indices(message, game)
          game.save_data()
          await message.channel.send(embed=discord.Embed(title='Actualizado!', description='Todos los datos han sido actualizados!', color=discord.Color.green()))
        
        elif message.content == '+autoroles' or message.content.startswith('+autoroles '):
          await autoroles(game, message)

      if obtener_rol_usuario(message.author) is not None:    
        if message.content == '+give' or message.content.startswith('+give '):
          await transfer_command(game, message)

        elif message.content == '+bal' or message.content.startswith('+bal '):
          await balance_command(game, message)    
          
        elif message.content == '+dep' or message.content.startswith('+dep '):
          await deposit_command(game, message)

        elif message.content == '+ret' or message.content.startswith('+ret '):
          await retire_command(game,message)
        
        elif message.content == '+shop' or message.content.startswith('+shop '):
          await shop(game, message)

        elif message.content == '+buy' or message.content.startswith('+buy '):
          await buy(game, message)

        elif message.content == '+inv' or message.content.startswith('+inv '):
          await inventario(game, message)

        elif message.content == '+list' or message.content.startswith('+list '):
          await lista(message)

        elif message.content == '+top' or message.content.startswith('+top '):
          await mostrar_top(message, game)

        elif message.content == '+reclutar' or message.content.startswith('+reclutar '):
          await reclutar(message, game, bot)

        elif message.content == '+caballeria' or message.content.startswith('+caballeria '):
          await mostrar_soldados(message, game)

        elif message.content == '+resaltar' or message.content.startswith('+resaltar '):
          await construccion_mapa(message)
          
        elif message.content == '+rob' or message.content.startswith('+rob '):
          await robar(message, game)
        
        elif message.content == '+jackpot' or message.content.startswith('+jackpot '):
          await jackpot(message, game)
        
        elif message.content == '+caballos' or message.content.startswith('+caballos '):
          await carrera_caballos(message, game)
        if message.channel.id != chat_general1 and message.channel.id != chat_general2:
          if message.content == '+mapa' or message.content.startswith('+mapa '):
            await MostrarMapa(message)
            
          elif message.content == '+collect' or message.content.startswith('+collect '):
            await collect(message, game, bot)

          elif message.content == '+use' or message.content.startswith('+use '):
            await Usar(message, game, bot)
            
          elif message.content == '+construcciones' or message.content.startswith('+construcciones '):
            await mostrar_construcciones(message, game)
        
        if message.content == '+ruleta' or message.content.startswith('+ruleta '):
          await ruleta(game, message, bot)

        elif message.content == '+ppt' or message.content.startswith('+ppt '):
          await ppt(game, message)  
        
        if has_role(message.author, 'Alcalde') is False:
          if message.content == '+añadir-defensa' or message.content.startswith('+añadir-defensa '):
            await añadir_defensa(message, game)

          elif message.content == '+quitar-defensa' or message.content.startswith('+quitar-defensa '):
            await quitar_defensa(message, game)
            
          elif message.content == '+traslado' or message.content.startswith('+traslado '):
            await intercambiar(message, game)
            
          elif message.content == '+ejercito' or message.content.startswith('+ejercito '):
            await ejercito(message, game)
        
        if message.content == '+work' or message.content.startswith('+work '):
          await slut_work(message, game)

        if message.content == '+slut' or message.content.startswith('+slut '):
          await slut_work(message, game)
          
        if has_role(message.author, 'Empresario') and message.channel.id == chat_empresario:
          #if message.content == '!accionismo' or   message.content.startswith('!accionismo'):
            #await Accionismo(message, bot, game)

          if message.content == '+gremio' or message.content.startswith('+gremio '):
            await Gremios(message, bot, game)

          elif message.content == '+tabla' or message.content.startswith('+tabla '):
            await mostrar_investigaciones(message, game)

          elif message.content == '+mostrar-gremios' or message.content.startswith('+mostrar-gremios '):
            await mostrar_gremios(message, game)

          elif message.content == '+mejorar' or message.content.startswith('+mejorar '):
            await comprar_tabla(message, game)
          
          elif message.content == '+añadir-redada' or message.content.startswith('+añadir-redada '):
            await añadir_redada(message, game)

        if (has_role(message.author, 'Dirigente') or has_role(message.author, 'Alcalde')) and message.channel.id == chat_dirigente:
          if has_role(message.author, 'Alcalde') is False:
            if message.content == '+redada' or message.content.startswith('+redada '):
              await Redada(message, bot, game)
              
            if message.content == '+añadir-redada' or message.content.startswith('+añadir-redada '):
              await añadir_redada(message, game)

          else:
            if message.content == '+impuestos' or message.content.startswith('+impuestos '):
              await asignar_impuestos(message, game, bot)   

          if message.content == '+ejercito-redada' or message.content.startswith('+ejercito-redada '):
            await mostrar_redada(message, game)  

        if has_role(message.author, 'Mafia'):
          if message.content == '+combate' or message.content.startswith('+combate '):
            await combate(message, game, bot)
          if message.channel.id == chat_mafia:
            if message.content == '+rendirse' or message.content.startswith('+rendirse '):
              await incorporazione(message, game, bot)

            elif message.content == '+secuestrar' or message.content.startswith('+secuestrar '):
              await secuestrar(message, game)

    game.save_data()

  else:
    await message.channel.send(embed=discord.Embed(title='Eliminado!', description=f'Lo sentimos mucho {message.author.mention}, pero estás eliminado de la partida.\n Espera a la próxima partida para volver a jugar!', color=discord.Color.red()))

  if message.author.guild_permissions.administrator:
    if message.content == '+partida' or message.content.startswith('+partida '):
      await gestionar_puntos(ajedrez, message)
  
  if message.content == '+ajedrez' or message.content.startswith('+ajedrez '):
    await top_ajedrez(ajedrez, message)
  
  elif message.content == '+puntos' or message.content.startswith('+puntos '):
    await mostrar_puntuacion(ajedrez, message)
  
  ajedrez.save_data()

    
    
  
    
@bot.event
async def on_disconnect():
    game.save_data()

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name='Economy Game'))
    print('Bot is ready!')

    #bot.loop.create_task(auto_add_money())
    bot.loop.create_task(paquete(1138879046382526495))

async def auto_add_money():
  while True:
    await asyncio.sleep(10)
    
    current_time = datetime.datetime.now().strftime('%H:%M')
    g = 696380553515106380
    if current_time == '20:05':
      guild = bot.get_guild(g)
      for member in guild.members:
          if has_role(member, 'Alcalde'):
            alcalde = member
            break

      for miembro in guild.members:
        construcciones = game.show_user_construcciones(miembro.id)
        tiene1 = False
        tiene2 = False
        
        if construcciones:
          embed = discord.Embed(title='Ganancias', description='Aquí están tus ganancias del dia de hoy!', color=discord.Color.blue())
          for c in construcciones:
            construccion = c.copy()
            if 'ganancias' in construccion:
              ultimos_valores = {}
              if game.gremios:
                for g in game.gremios:
                  if miembro.id in g['miembros']:
                    for investigacion, desbloqueos in g['desbloqueados'].items():
                      valores_no_vacios = [valor for valor in desbloqueos if valor != []]
                      if valores_no_vacios:
                        ultimo_valor = valores_no_vacios[-1]
                        ultimos_valores[investigacion] = ultimo_valor
                    break

              print(ultimos_valores)
              if 'Ganancias' in ultimos_valores:
                construccion['ganancias'] = c['ganancias'] * (1 + 100 / ultimos_valores['Ganancias'])  

              if 'Mantenimiento' in ultimos_valores:
                construccion['mantenimiento'] = c['mantenimiento'] * (1 - 100 / ultimos_valores['Mantenimiento'])       

              nombre = construccion['nombre']
              
              if 'impuestos' in construccion:
                if 'Sobornos' in ultimos_valores:
                  construccion['impuestos'] = c['impuestos'] * (1 - 100 / ultimos_valores['Sobornos'])
                
                tiene1 = True
                amountAlcalde = construccion['ganancias'] * construccion['impuestos']
                game.add_money(alcalde.id, amountAlcalde, 'bank')
                await alcalde.send(f'El usuario {miembro} te ha dado su parte de las ganancias en {nombre}!')
              
              if 'mafia' in construccion:
                tiene2 = True
                amountMafia = construccion['ganancias'] * 0.2
                game.add_money(construccion['mafia'].id, amountMafia, 'bank')
                await construccion['mafia'].send(f'El usuario {miembro} te ha dado su parte de las ganancias en {nombre}!')
              
              if tiene1 and tiene2:
                amountUser = construccion['ganancias'] * (1 - 0.2 - construccion['impuestos'])
                game.add_money(miembro, amountUser, 'bank')
                embed.add_field(name=f'{nombre}', value=f'Ganancias obtenidas: {amountUser}')

              elif tiene1:
                amountUser = construccion['ganancias'] * (1 - construccion['impuestos'])
                game.add_money(miembro, amountUser, 'bank')
                embed.add_field(name=f'{nombre}', value=f'Ganancias obtenidas: {amountUser}')
              
              elif tiene2:
                amountUser = construccion['ganancias'] * 0.8
                game.add_money(miembro, amountUser, 'bank')
                embed.add_field(name=f'{nombre}', value=f'Ganancias obtenidas: {amountUser}')
              
              else:
                amountUser = construccion['ganancias']
                game.add_money(miembro, amountUser, 'bank')
                embed.add_field(name=f'{nombre}', value=f'Ganancias obtenidas: {amountUser}')
              
              if game.balances[miembro]['bank'] > 0:
                game.remove_money(miembro, construccion['mantenimiento'], 'bank')
              else:
                game.remove_money(miembro, construccion['mantenimiento'], 'wallet')

          embed.set_footer(text=f'{current_date}')
          await member.send(embed=embed)

      game.save_data()
      await asyncio.sleep(60)


      

@bot.event
async def on_raw_reaction_add(payload):
  global user_id
  guild = bot.get_guild(payload.guild_id)
  user = guild.get_member(payload.user_id)
  channel = bot.get_channel(payload.channel_id)
  message = await channel.fetch_message(payload.message_id)

  if user.bot:
    return

  if message.author == bot.user:
    emojis = ['💼', '🧐']
    roles = [
      discord.utils.get(guild.roles, name='Empresario'),
      discord.utils.get(guild.roles, name='Mafia')
    ] 
    if user_id is not None and payload.user_id == user_id:
      for i in range(len(roles)):
        if str(payload.emoji) == emojis[i]:
          for role in roles:
            if role in user.roles:
              await user.remove_roles(role)
            await user.add_roles(roles[i])
            await user.add_roles(discord.utils.get(guild.roles, name='Economia'))
          
          break
            
      await message.delete()
      embed = discord.Embed(title='Muchas gracias!', description=f'Has sido asignado correctamente con el rol {roles[i].name}!')
      embed.add_field(name='\u200b', value='Ahora podrás ver el chat de tu rol dentro de la categoria de Economia en el servidor!', inline=False)
      embed.add_field(name='\u200b', value='Mucha suerte!', inline=False)
      embed.set_footer(text=f'{current_date}')
      
      await user.send(embed=embed)



async def event_command(message):
  global user_id
  emojis = ['💼', '🧐']
  roles = [
    discord.utils.get(message.guild.roles, name='Empresario'),
    discord.utils.get(message.guild.roles, name='Mafia')
  ] 

  embed = discord.Embed(title='Bienvenido!', description='Vemos que eres nuevo por aquí! Dejame que te explique brevemente de que va esto...', color=discord.Color.purple())
  embed.add_field(name='\u200b', value='Este es el nuevo juego de la economia del servidor! En el participan 3 tipos de roles...', inline=False)

  for i in range(len(roles)):
    embed.add_field(name='Emoji', value=emojis[i], inline=True)
    embed.add_field(name='Rol', value=roles[i].mention, inline=True)
    embed.add_field(name='\u200b', value='\u200b', inline=False)

  embed.add_field(name='\u200b', value='Por normativas del juego, solo podrás escoger entre los 2 primeros roles.', inline=False)
  embed.add_field(name='\u200b', value='Reacciona a los emojis para conseguir uno de los dos roles!', inline=False)
  embed.set_footer(text=f'{current_date}')
  
  msj = await message.channel.send(embed=embed)
  
  for emoji in emojis:
    await msj.add_reaction(emoji)
    
  user_id = message.author.id

async def paquete(c):
  while True:
    channel = bot.get_channel(c) 
    await asyncio.sleep(random.randint(600, 1200)) ## 1800, 3600
    g = 696380553515106380
    if random.randint(0 , 1) == 0:
      probabilidades = [0.35, 0.60, 0.05]
    
      valores = [1, 2, 3]
    
      tipo = random.choices(valores, weights=probabilidades)[0]
      
      if tipo == 1:
        numero = random.randint(1, 9)
        amount = random.randint(500, 1000)
        await channel.send(f"¡Un paquete ha sido soltado! El numero está entre el 1 y 9")
      
      if tipo == 2:
        numero = random.randint(1, 99)
        amount = random.randint(1000, 10000)
        await channel.send(f"¡Un paquete ha sido soltado! El numero está entre el 1 y 99")
        
      if tipo == 3:
        numero = random.randint(1, 999)
        amount = random.randint(10000, 20000)
        await channel.send(f"¡Un paquete ha sido soltado! El numero está entre el 1 y 999")
        
      def check(m):
        if m.content.isdigit() and int(m.content) > 0:
          return m.author != bot.user
        
      while True:    
        try:
            message = await bot.wait_for("message", check=check, timeout=180)
            response = int(message.content)
            autor = message.author
            if numero - int(response) > 25:
              await channel.send("frio, frio...")
            elif numero - int(response) < -25:
              await channel.send("frio, frio...")
            elif int(response) != numero:
              await channel.send("caliente, caliente...")
            if numero == int(response):
              game.add_money(autor.id, amount, 'bank')
              await channel.send(embed=discord.Embed(title='Felicidades!', description=f'el usuario {autor} ha acertado el número! Aquí tienes el premio de {amount} 💸', color=discord.Color.green()))
              break
        except asyncio.TimeoutError:
          await channel.send(embed=discord.Embed(
              title='Failed!',
              description=f"Se agotó el tiempo de espera. El numero era {numero}!!",
              color=discord.Color.red()))
          break
    else:
      fake = Faker('es_ES')
      
      acento = fake.first_name()
      nombre = unidecode(acento)

      letras_reveladas = [False] * len(nombre)

      mensaje = await channel.send('Paquete!')

      print(nombre, acento)
      adivinado = False
      cantidad_true = 0
      while not adivinado and cantidad_true != len(letras_reveladas):
        indice = 0
        while letras_reveladas[indice] == True:
          indice = random.randint(0, len(nombre) - 1)

        letras_reveladas[indice] = True
        
        nombre_oculto = ''.join(['?' if not revelada else letra for letra, revelada in zip(nombre, letras_reveladas)])

        print(nombre, letras_reveladas)


        embed = discord.Embed(title='Adivinanza', description=f'¡Hola! ¿A que no adivinas mi nombre?', color=discord.Color.blurple())
        embed.add_field(name='Mi nombre es:', value=nombre_oculto, inline=False)

        embed.set_thumbnail(url = 'https://cdn-icons-png.flaticon.com/512/1828/1828413.png')
        
        await mensaje.edit(embed=embed)
        
        cantidad_true = letras_reveladas.count(True)

        for i in range(15):
          try:
            mensaje_usuario = await bot.wait_for('message', timeout=2, check=lambda m: m.channel == mensaje.channel)
            author = mensaje_usuario.author
            if unidecode(mensaje_usuario.content.lower()) == nombre.lower():
              author = mensaje_usuario.author
              recompensa = random.randint(1000, 2000 * (len(letras_reveladas) - cantidad_true)) * 3
              await channel.send(f'{author.mention}. Ese SI es mi nombre. Aquí tienes {recompensa} 💸!')
              adivinado = True
              break
            else:
              await channel.send(f'{author.mention}. Ese NO es mi nombre. ¡Sigue intentando!')
              
          except asyncio.TimeoutError:
            continue
      
      if adivinado:
        game.add_money(author.id, recompensa, 'bank')
        
            





bot.run('MTExMTcwMjU1NTEzNTg1Njc2MA.GrG3Yd.WD5LCtREIOrxkhfMbX5H1EAi1oRPalzqiRaJOQ')