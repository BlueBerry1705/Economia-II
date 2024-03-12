import os
from typing import Optional
import discord
import asyncio
import datetime
import random
from itertools import zip_longest
from tabulate import tabulate
from PIL import Image, ImageDraw, ImageOps
from discord.ui import Button, View, Select
from discord.ext import commands
import math
import re
import copy
import io

from Economia import *
from Utils import *
from Mapa import DibujarMapa, MostrarMapa

from discord_easy_commands import EasyBot


g = 696380553515106380

emoji_id = 1137838279409016962



async def reset_command(game, message):
  current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  
  if len(message.mentions) >= 1:
    user = message.mentions[0]
  else:
    user = 'all'
  type = message.content.split(' ')[2]
  
  if game.reset(user, type, message) is not False:
    embed = discord.Embed(
      title='Restarted!',
      description=
      f'👏 Se ha reseteado correctamente!',
      color=discord.Color.yellow())
    embed.set_footer(text=f'{current_date}')
  else:
    embed = discord.Embed(
      title='Restart Failed!',
      description='Wrong input. Try !reset (user) (balance/inventario)',
      color=discord.Color.red())

  await message.channel.send(embed=embed)


async def remove_command(game, message):
  current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  #if not has_mod_role(message.author):
  #await message.channel.send('❌ No tienes permisos para usar este comando.')
  #return
  if len(message.mentions) == 0:
    embed = discord.Embed(title='Error',
                          description='❌ Debes mencionar a un usuario.',
                          color=discord.Color.red())
    embed.set_footer(text=f'{current_date}')
    await message.channel.send(embed=embed)
    return

  member = message.mentions[0]
  amount = int(message.content.split(' ')[1])
  if game.remove_money(member.id, amount, message.content.split(' ')[2]):
    game.save_data()
    embed = discord.Embed(
      title='Remover Dinero',
      description=
      f'✅ Se han removido {amount} monedas a {member.display_name}.',
      color=discord.Color.green())
    embed.set_footer(text=f'{current_date}')
  else:
    embed = discord.Embed(
      title='Error',
      description='❌ No tienes suficiente cantidad de dinero!.',
      color=discord.Color.red())

    embed.set_footer(text=f'{current_date}')

  await message.channel.send(embed=embed)


async def balance_command(game, message):
  current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  emoji = discord.utils.get(message.guild.emojis, id=emoji_id)
  member = message.author
  if len(message.mentions) > 0:
    member = message.mentions[0]

  balances = game.get_balance(member.id)
  wallet_balance = balances['wallet']
  bank_balance = balances['bank']

  embed = discord.Embed(title=f'Saldo de {member.display_name}',
                        color=discord.Color.blue())
  if member.avatar:
    embed.set_thumbnail(url=member.avatar.url)
  embed.add_field(name='Bolsillo',
                  value=f'{emoji} {wallet_balance} monedas',
                  inline=False)
  embed.add_field(name='Banco',
                  value=f'{emoji} {bank_balance} monedas',
                  inline=False)

  embed.set_footer(text=f'{current_date}')

  await message.channel.send(embed=embed)


async def transfer_command(game, message):
  current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  emoji = discord.utils.get(message.guild.emojis, id=emoji_id)
  args = message.content.split(' ')
  member = message.author
  recipient = message.mentions[0]
  balance = game.get_balance(member.id)
  amount = args[2]
  
  if amount == 'all':
    amount = balance.get('bank', 0)
  if int(amount) <= 0:
    embed = discord.Embed(
      title='Transferencia',
      description='❌ No puedes transferir en negativo.',
      color=discord.Color.red())
    embed.set_footer(text=f'{current_date}')
    await message.channel.send(embed=embed)
    return 0
  
  if game.transfer_money(member.id, recipient.id, int(amount)):
    embed = discord.Embed(
      title='Transferencia',
      description=f'💸 Se transfirieron {amount} {emoji} a {recipient.name}.',
      color=discord.Color.green())
  else:
    embed = discord.Embed(
      title='Transferencia',
      description='❌ No tienes suficiente dinero en tu banco para transferir.',
      color=discord.Color.red())

  embed.set_footer(text=f'{current_date}')

  await message.channel.send(embed=embed)


async def addmoney_command(game, message):
  current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  emoji = discord.utils.get(message.guild.emojis, id=emoji_id)

  if len(message.mentions) == 0:
    await message.channel.send(
      embed=discord.Embed(title='Failed',
                          value='❌ Debes mencionar a un usuario.',
                          color=discord.Color.red()))
    return

  member = message.mentions[0]
  amount = int(message.content.split(' ')[1])

  if amount > 0:
    game.add_money(member.id, amount, message.content.split(' ')[2])
    game.save_data()

    embed = discord.Embed(
      title='Añadir Dinero',
      description=f'{emoji} Se han añadido {amount} monedas a {member.display_name}!',
      color=discord.Color.green())
    embed.set_footer(text=f'{current_date}')
    await message.channel.send(embed=embed)


async def deposit_command(game, message):
  current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  emoji = discord.utils.get(message.guild.emojis, id=emoji_id)
  member = message.author
  amount = message.content.split(' ')[1]
  balance = game.get_balance(member.id)

  if amount == 'all':
    amount = balance.get('wallet', 0)
  amount = int(amount)
  if amount > 0 and balance.get('wallet', 0) >= amount:
    game.add_money(member.id, amount, 'bank')
    game.remove_money(member.id, amount, 'wallet')

    embed = discord.Embed(
      title='Depósito',
      description=
      f'{emoji} Se han depositado {amount} {emoji} a {member.display_name}!',
      color=discord.Color.green())

    embed.set_footer(text=f'{current_date}')

    await message.channel.send(embed=embed)


async def retire_command(game, message):
  current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  emoji = discord.utils.get(message.guild.emojis, id=emoji_id)
  member = message.author
  amount = message.content.split(' ')[1]
  balance = game.get_balance(member.id)

  if amount == 'all':
    amount = balance.get('bank', 0)

  amount = int(amount)
  if amount > 0 and balance.get('bank', 0) >= amount:
    game.add_money(member.id, amount, 'wallet')
    game.remove_money(member.id, amount, 'bank')

    embed = discord.Embed(
      title='Retirado!',
      description=
      f'{emoji} Se han retirado {amount} {emoji} a {member.display_name}!',
      color=discord.Color.green())

    embed.set_footer(text=f'{current_date}')

    await message.channel.send(embed=embed)

class PaginationView(discord.ui.View):
  def __init__(self, data):
    super().__init__()
    self.current_page = 1
    self.sep = 5
    self.data = data
  
  async def send(self, ctx):
    self.message = await ctx.channel.send(view=self)
    await self.update_message(self.data[:self.sep])
  
  async def update_message(self, data):
    self.update_buttons()
    await self.message.edit(embed=self.create_embed(data), view=self)
  
  def update_buttons(self):
    if self.current_page == 1:
      self.first_page_button.disabled = True
      self.prev_button.disabled = True
      self.first_page_button.style = discord.ButtonStyle.gray
      self.prev_button.style = discord.ButtonStyle.gray
    else:
      self.first_page_button.disabled = False
      self.prev_button.disabled = False
      self.first_page_button.style = discord.ButtonStyle.green
      self.prev_button.style = discord.ButtonStyle.primary
    
    if self.current_page == int(len(self.data) / self.sep) + 1:
      self.last_page_button.disabled = True
      self.next_button.disabled = True
      self.last_page_button.style = discord.ButtonStyle.gray
      self.next_button.style = discord.ButtonStyle.gray
    else:
      self.last_page_button.disabled = False
      self.next_button.disabled = False
      self.last_page_button.style = discord.ButtonStyle.green
      self.next_button.style = discord.ButtonStyle.primary

  @discord.ui.button(label="|<", style=discord.ButtonStyle.primary)
  async def first_page_button(self, interaction:discord.Interaction, button: discord.ui.Button):
    await interaction.response.defer()
    self.current_page = 1
    until_item = self.current_page * self.sep
    await self.update_message(self.data[:until_item])

  @discord.ui.button(label="<", style=discord.ButtonStyle.primary)
  async def prev_button(self, interaction:discord.Interaction, button: discord.ui.Button):
    await interaction.response.defer()
    self.current_page -= 1
    until_item = self.current_page * self.sep
    from_item = until_item - self.sep
    await self.update_message(self.data[from_item:until_item])
  
  @discord.ui.button(label=">", style=discord.ButtonStyle.primary)
  async def next_button(self, interaction:discord.Interaction, button: discord.ui.Button):
    await interaction.response.defer()
    self.current_page += 1
    until_item = self.current_page * self.sep
    from_item = until_item - self.sep
    await self.update_message(self.data[from_item:until_item])
  
  @discord.ui.button(label=">|", style=discord.ButtonStyle.primary)
  async def last_page_button(self, interaction:discord.Interaction, button: discord.ui.Button):
    await interaction.response.defer()
    self.current_page = int(len(self.data) / self.sep) + 1
    until_item = self.current_page * self.sep
    from_item = until_item - self.sep
    await self.update_message(self.data[from_item:])

class ShopPaginationView(PaginationView):
  def __init__(self, data, url, emoji):
    super().__init__(data)
    self.url = url
    self.emoji = emoji

  def create_embed(self, data):
    current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    embed = discord.Embed(title='Tienda', description='Bienvenido a la tienda!', color=discord.Color.blue())
    embed.set_thumbnail(url=self.url)
  
    if data is not None:
      for objeto in data:
        id = objeto['id']
        nombre = objeto['nombre']
        precio = objeto['precio']
        ganancias = objeto['ganancias']
        mantenimiento = objeto['mantenimiento']
        
        embed.add_field(name=f'ID: {id} - Nombre: {nombre}', value=f"Precio: {precio} {self.emoji},  Ganancias: {ganancias} {self.emoji},  Mantenimiento: {mantenimiento} {self.emoji}", inline=False)

        if 'requisitos' in objeto:
          embed.add_field(name='\u200b', value='**__REQUISITOS__**', inline=False)
          requisitos = objeto['requisitos']
          for r in requisitos:
            nombre_requisito = r['nombre']
            cantidad = r['cantidad']
            embed.add_field(name=f'Nombre: {nombre_requisito}', value=f'Cantidad: {cantidad}', inline=True)

    embed.set_footer(text=f'{current_date}')
    
    return embed

async def shop(game, message):
  emoji = discord.utils.get(message.guild.emojis, id=emoji_id)
  roles = ["Empresario", "Dirigente", "Mafia", "Alcalde"]
  author = message.author

  for rol in roles:
    if discord.utils.get(message.guild.roles, name=rol) in author.roles:
      if rol == 'Alcalde':
        rol = 'Dirigente'
        
      tienda = game.show_shop(rol)

      if obtener_rol_usuario(author) == 'Mafia':
        url = 'https://i2.wp.com/johnothecoder.uk/wp-content/uploads/sites/11/2018/12/Mafia-Online-Avatar-600x600.jpg?ssl=1'
      elif obtener_rol_usuario(author) == 'Empresario':
        url = 'https://images.vexels.com/media/users/3/129616/isolated/preview/fb517f8913bd99cd48ef00facb4a67c0-silueta-de-avatar-de-empresario.png'
      else:
        url = 'https://cdn.icon-icons.com/icons2/3082/PNG/512/police_policeman_avatar_man_people_icon_191330.png'
        
      pagination_view = ShopPaginationView(tienda, url, emoji)
      await pagination_view.send(message)

async def buy(game, message):
  current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  emoji = discord.utils.get(message.guild.emojis, id=emoji_id)
  author = message.author
  objeto = int(message.content.split(' ')[1])
  cantidad = int(message.content.split(' ')[2])
  roles = ["Empresario", "Dirigente", "Mafia", "Alcalde"]

  for rol in roles:
    if discord.utils.get(message.guild.roles, name=rol) in author.roles:
      if rol == 'Alcalde':
        rol = 'Dirigente'
      
      mensaje = game.buy_object(author, rol, objeto, cantidad, emoji)

      embed = discord.Embed(title='Compra',
                            description=mensaje,
                            color=discord.Color.blue())
      break

  embed.set_footer(text=f'{current_date}')

  await message.channel.send(embed=embed)

class InventoryPaginationView(PaginationView):
  def __init__(self, data, user):
    super().__init__(data)
    self.user = user
    
  def create_embed(self, data):
    current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    embed = discord.Embed(title='Inventario', description=f'Este es el inventario de {self.user}:', color=discord.Color.blue())
    if self.user.avatar:
      embed.set_thumbnail(url=self.user.avatar.url)
    if data is not None:
      for objeto in data:
        nombre = objeto['nombre']
        id = objeto['id']
        cantidad = objeto.get('cantidad', 1)
        embed.add_field(name=f'{nombre} - ID: {id}',
                        value=f'Descripcion del objeto - Cantidad: {cantidad}',
                        inline=False)
    else:
      embed.add_field(name='\u200b',
                      value='No tiene ningún objeto en el inventario!!')

    embed.set_footer(text=f'{current_date}')
    
    return embed
  
async def inventario(game, message):
  usuario = message.author
  if len(message.mentions) > 0:
    usuario = message.mentions[0]
  items = game.show_user_items(usuario.id)

  if items is not None:
    pagination_view = InventoryPaginationView(items, usuario)
    await pagination_view.send(message)
  else:
    await message.channel.send(embed=discord.Embed(title='Inventario', description=f'El usuario {usuario} no tiene ningún objeto en el inventario!!', color=discord.Color.blue()))

class EjercitoPaginationView(PaginationView):
  def __init__(self, data, user, emoji):
    super().__init__(data)
    self.user = user
    self.emoji = emoji

  def create_embed(self, data):
    current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    embed = discord.Embed(title='Ejercito', description=f'Este es el ejercito de {self.user}:', color=discord.Color.blue())
    if self.user.avatar:
      embed.set_thumbnail(url=self.user.avatar.url)
    print(data)
    if data is not None:
      for objeto in data:
        if objeto['id'] <= 3:
          id = objeto['id']
          nombre = objeto['nombre']
          precio = objeto['precio']
          mantenimiento = objeto['mantenimiento']
          ataque = objeto['ataque']
          defensa = objeto['defensa']
          vida = objeto['vida']
          cantidad = objeto['cantidad']
          embed.add_field(name=nombre, value=f"ID: {id} - Precio: {precio} {self.emoji},  Mantenimiento: {mantenimiento} {self.emoji}, Ataque: {ataque} ⚔️, Defensa: {defensa} 🛡️, Vida: {vida} ❤️, Cantidad: {cantidad}", inline=False)
        else:
          id = objeto['id']
          nombre = objeto['nombre']
          cantidad = objeto['cantidad']
          embed.add_field(name='Capofamiglia', value=f'ID: {id} - Nombre: {nombre}, Cantidad: {cantidad}', inline=False)
    else:
      embed.add_field(name='\u200b',
                      value='No tiene ningún soldado en el inventario!!')

    embed.set_footer(text=f'{current_date}')
    
    return embed

async def ejercito(message, game):
  emoji = discord.utils.get(message.guild.emojis, id=emoji_id)
  usuario = message.author
  if len(message.mentions) > 0:
    usuario = message.mentions[0]
  items = game.show_user_ejercito(usuario.id)

  if items is not None:
    pagination_view = EjercitoPaginationView(items, usuario, emoji)
    await pagination_view.send(message)
  else:
    await message.channel.send(embed=discord.Embed(title='Ejercito', description=f'El usuario {usuario} no tiene ningún soldado en el cuartel!!', color=discord.Color.blue()))

class HelpPaginationView(PaginationView):
  def __init__(self, data, user, avatar):
    super().__init__(data)
    self.user = user
    self.avatar = avatar
    
  def create_embed(self, data):
    current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    embed = discord.Embed(title='Lista de comandos Economia II:', description='Este es un listado de comandos para el uso de la economía II.', color=discord.Color.blue())
    
    embed.set_thumbnail(url=self.avatar)

    for objeto in data:
      name = objeto['name']
      value = objeto['value']

      embed.add_field(name=name, value=value, inline=False)
        

    embed.set_footer(text=f'{current_date}')
    
    return embed
  
async def help(message):
  usuario = message.author
  help_mafia = [
    {
      'name': '+help', 'value': 'Muestra una lista de los comandos disponibles para cada rol'
    },
    {
      'name': '+start', 'value': 'En caso de no tener el rol de Economia aún, podrás usar este comando para empezar a formar parte de ella!!'
    },
    {
      'name': '+dep {amount/all}', 'value': 'Deposita una cantidad en concreto o todo el dinero de tu cartera al banco'
    },
    {
      'name': '+ret {amount/all}', 'value': 'Retira una cantidad en concreto o todo el dinero de tu banco a la cartera'
    },
    {
      'name': '+bal {usuario}', 'value': 'Muestra el balance del usuario mencionado'
    },
    {
      'name': '+shop', 'value': 'Muestra la tienda de tu rol predeterminado'
    },
    {
      'name': '+buy {ID producto} {cantidad}', 'value': 'Compra el objeto asignado con ese ID en la tienda de tu rol'
    },
    {
      'name': '+inv {usuario}', 'value': 'Muestra el inventario y la caballeria reclutada del usuario mencionado'
    },
    {
      'name': '+jackpot {apuesta} {dificultad (1, 2, 3)}', 'value': 'Apuesta tu dinero en un juego de azar!!'
    },
    {
      'name': '+caballos', 'value': 'Apuesta tu dinero en una carrera de caballos!!'
    },
    {
      'name': '+ruleta', 'value': 'Apuesta tu dinero en la ruleta del casino!!'
    },
    {
      'name': '+ppt {apuesta}', 'value': 'El clásico piedra, papel o tijera. Apuesta tu dinero y invita a un contrincante!'
    },
    {
      'name': '+give {usuario} {amount/all}', 'value': 'Transfiere una cantidad o todo tu dinero depositado en el banco a un usuario'
    },
    {
      'name': '+mapa', 'value': 'Muestra el mapa del juego actualizado hasta el momento'
    },
    {
      'name': '+reset {usuario} {balance/inventario/ejercito}', 'value': 'Resetea el inventario, balance o el ejercito de un usuario en especifico'
    },
    {
      'name': '+use {ID edificio} {posX} {posY}', 'value': 'Añade un edificio por cada posicion de 10 en 10 en el mapa original'
    },
    {
      'name': '+top', 'value': 'Muestra el top actualizado de las personas con mas dinero total'
    },
    {
      'name': '+list', 'value': 'Muestra los jugadores de esta economia con sus roles respectivos'
    },
    {
      'name': '+collect', 'value': 'Cobra todas las ganancias de tus construcciones cada 24h!'
    },
    {
      'name': '+caballeria', 'value': 'Muestra la caballeria disponible de sus roles respectivos'
    },
    {
      'name': '+reclutar {ID caballeria} {cantidad}', 'value': 'Recluta la cantidad de caballeria solicitada'
    },
    {
      'name': '+construcciones {usuario}', 'value': 'Muestra las construcciones de un usuario, con sus ganancias y mantenimiento junto su ID de construccion'
    },
    {
      'name': '+añadir-defensa {ID solado} {cantidad} {ID construccion}', 'value': 'Añade una cantidad de un soldado en concreto a un edificio'
    },
    {
      'name': '+quitar-defensa {ID solado} {cantidad} {ID construccion}', 'value': 'Quita una cantidad de un soldado en concreto a un edificio'
    },
    {
      'name': '+resaltar {ID construccion} {usuario}', 'value': 'Resalta una construccion en especifico de un usuario en el mapa del juego'
    },
    {
      'name': '+rob {usuario}', 'value': 'Roba un porcentaje de dinero en la cartera de un usuario en específico'
    },
    {
      'name': '+traslado {ID soldado} {cantidad} {usuario}', 'value': 'Traslada una cantidad de un soldado en concreto al usuario mencionado' 
    },
    {
      'name': '+ejercito {usuario}', 'value': 'Muestra el ejercito de un usuario en concreto'
    },
    {
      'name': '+work', 'value': 'Consigue dinero trabajando un poquito'
    },
    {
      'name': '+slut', 'value': 'Consigue dinero robando. CUIDADO porque puedes perder dinero!'
    },
    {
      'name': '+combate {ID construccion} {usuario} {ID soldado 1} {cantidad soldado 1} {ID soldado 2} {cantidad soldado 2} ... {ID soldado N} {cantidad soldado N}', 'value': 'Lucha contra el usuario mencionado con el ID y cantidad de la caballeria que quiera mandar', 'rol': 'Mafia'
    },
    {
      'name': '+rendirse {usuario}', 'value': 'Ríndete ante una mafia para poder formar parte de su capofamiglia. Siendo un capofamiglia puedes MORIR para SIEMPRE!!!', 'rol': 'Mafia'
    },
    {
      'name': '+secuestrar {ID soldado 1} {cantidad soldado 1} {ID soldado 2} {cantidad soldado 2} ... {ID soldado N} {cantidad soldado N}', 'value': 'Manda un ejercito en busca de esclavos! Durante las 12h de búsqueda, tu ejercito mandado estará ausente!', 'rol': 'Mafia'
    }
  ]
  help_empresario = [
    {
      'name': '+help', 'value': 'Muestra una lista de los comandos disponibles para cada rol'
    },
    {
      'name': '+start', 'value': 'En caso de no tener el rol de Economia aún, podrás usar este comando para empezar a formar parte de ella!!'
    },
    {
      'name': '+dep {amount/all}', 'value': 'Deposita una cantidad en concreto o todo el dinero de tu cartera al banco'
    },
    {
      'name': '+ret {amount/all}', 'value': 'Retira una cantidad en concreto o todo el dinero de tu banco a la cartera'
    },
    {
      'name': '+bal {usuario}', 'value': 'Muestra el balance del usuario mencionado'
    },
    {
      'name': '+shop', 'value': 'Muestra la tienda de tu rol predeterminado'
    },
    {
      'name': '+buy {ID producto} {cantidad}', 'value': 'Compra el objeto asignado con ese ID en la tienda de tu rol'
    },
    {
      'name': '+inv {usuario}', 'value': 'Muestra el inventario y la caballeria reclutada del usuario mencionado'
    },
    {
      'name': '+jackpot {apuesta} {dificultad (1, 2, 3)}', 'value': 'Apuesta tu dinero en un juego de azar!!'
    },
    {
      'name': '+caballos', 'value': 'Apuesta tu dinero en una carrera de caballos!!'
    },
    {
      'name': '+ruleta', 'value': 'Apuesta tu dinero en la ruleta del casino!!'
    },
    {
      'name': '+ppt {apuesta}', 'value': 'El clásico piedra, papel o tijera. Apuesta tu dinero y invita a un contrincante!'
    },
    {
      'name': '+give {usuario} {amount/all}', 'value': 'Transfiere una cantidad o todo tu dinero depositado en el banco a un usuario'
    },
    {
      'name': '+mapa', 'value': 'Muestra el mapa del juego actualizado hasta el momento'
    },
    {
      'name': '+reset {usuario} {balance/inventario/ejercito}', 'value': 'Resetea el inventario, balance o el ejercito de un usuario en especifico'
    },
    {
      'name': '+use {ID edificio} {posX} {posY}', 'value': 'Añade un edificio por cada posicion de 10 en 10 en el mapa original'
    },
    {
      'name': '+top', 'value': 'Muestra el top actualizado de las personas con mas dinero total'
    },
    {
      'name': '+list', 'value': 'Muestra los jugadores de esta economia con sus roles respectivos'
    },
    {
      'name': '+collect', 'value': 'Cobra todas las ganancias de tus construcciones cada 24h!'
    },
    {
      'name': '+caballeria', 'value': 'Muestra la caballeria disponible de sus roles respectivos'
    },
    {
      'name': '+reclutar {ID caballeria} {cantidad}', 'value': 'Recluta la cantidad de caballeria solicitada'
    },
    {
      'name': '+construcciones {usuario}', 'value': 'Muestra las construcciones de un usuario, con sus ganancias y mantenimiento junto su ID de construccion'
    },
    {
      'name': '+añadir-defensa {ID solado} {cantidad} {ID construccion}', 'value': 'Añade una cantidad de un soldado en concreto a un edificio'
    },
    {
      'name': '+quitar-defensa {ID solado} {cantidad} {ID construccion}', 'value': 'Quita una cantidad de un soldado en concreto a un edificio'
    },
    {
      'name': '+resaltar {ID construccion} {usuario}', 'value': 'Resalta una construccion en especifico de un usuario en el mapa del juego'
    },
    {
      'name': '+rob {usuario}', 'value': 'Roba un porcentaje de dinero en la cartera de un usuario en específico'
    },
    {
      'name': '+traslado {ID soldado} {cantidad} {usuario}', 'value': 'Traslada una cantidad de un soldado en concreto al usuario mencionado' 
    },
    {
      'name': '+ejercito {usuario}', 'value': 'Muestra el ejercito de un usuario en concreto'
    },
    {
      'name': '+work', 'value': 'Consigue dinero trabajando un poquito'
    },
    {
      'name': '+slut', 'value': 'Consigue dinero robando. CUIDADO porque puedes perder dinero!'
    },
    {
      'name': '+gremio {usuario1} {usuario2} {apodo} {avatar} (opcional)', 'value': 'Formar gremio con un máximo de 3 miembros (contándote a tí mismo) con tal de poder optar a algunas ventajas (se pueden hacer gremios de 2 y 3 personas solo)', 'rol': 'Empresario'
    },
    {
      'name': '+tabla {ID gremio} {ID investigación}', 'value': 'Muestra la tabla de progreso de una investigación en concreta (de las 4 existentes) de un gremio en concreto', 'rol': 'Empresario'
    },
    {
      'name': '+mostrar-gremios', 'value': 'Muestra todos los gremios formados con sus porcentajes desbloqueados de cada investigación en el momento', 'rol': 'Empresario'
    },
    {
      'name': '+mejorar {ID investigación}', 'value': 'Compra el siguiente % a desbloquear de una investigación en concreto', 'rol': 'Empresario'
    },
    {
      'name': '+añadir-redada {ID soldado} {cantidad}', 'value': 'Añade una cantidad de soldados en específico al ejercito de redadas. NO se puede sacar soldados del ejercito!', 'no': 'Mafia'
    }
  ]

  help_dirigente = [
    {
      'name': '+help', 'value': 'Muestra una lista de los comandos disponibles para cada rol'
    },
    {
      'name': '+start', 'value': 'En caso de no tener el rol de Economia aún, podrás usar este comando para empezar a formar parte de ella!!'
    },
    {
      'name': '+dep {amount/all}', 'value': 'Deposita una cantidad en concreto o todo el dinero de tu cartera al banco'
    },
    {
      'name': '+ret {amount/all}', 'value': 'Retira una cantidad en concreto o todo el dinero de tu banco a la cartera'
    },
    {
      'name': '+bal {usuario}', 'value': 'Muestra el balance del usuario mencionado'
    },
    {
      'name': '+shop', 'value': 'Muestra la tienda de tu rol predeterminado'
    },
    {
      'name': '+buy {ID producto} {cantidad}', 'value': 'Compra el objeto asignado con ese ID en la tienda de tu rol'
    },
    {
      'name': '+inv {usuario}', 'value': 'Muestra el inventario y la caballeria reclutada del usuario mencionado'
    },
    {
      'name': '+jackpot {apuesta} {dificultad (1, 2, 3)}', 'value': 'Apuesta tu dinero en un juego de azar!!'
    },
    {
      'name': '+caballos', 'value': 'Apuesta tu dinero en una carrera de caballos!!'
    },
    {
      'name': '+ruleta', 'value': 'Apuesta tu dinero en la ruleta del casino!!'
    },
    {
      'name': '+ppt {apuesta}', 'value': 'El clásico piedra, papel o tijera. Apuesta tu dinero y invita a un contrincante!'
    },
    {
      'name': '+give {usuario} {amount/all}', 'value': 'Transfiere una cantidad o todo tu dinero depositado en el banco a un usuario'
    },
    {
      'name': '+mapa', 'value': 'Muestra el mapa del juego actualizado hasta el momento'
    },
    {
      'name': '+reset {usuario} {balance/inventario/ejercito}', 'value': 'Resetea el inventario, balance o el ejercito de un usuario en especifico'
    },
    {
      'name': '+use {ID edificio} {posX} {posY}', 'value': 'Añade un edificio por cada posicion de 10 en 10 en el mapa original'
    },
    {
      'name': '+top', 'value': 'Muestra el top actualizado de las personas con mas dinero total'
    },
    {
      'name': '+list', 'value': 'Muestra los jugadores de esta economia con sus roles respectivos'
    },
    {
      'name': '+collect', 'value': 'Cobra todas las ganancias de tus construcciones cada 24h!'
    },
    {
      'name': '+caballeria', 'value': 'Muestra la caballeria disponible de sus roles respectivos'
    },
    {
      'name': '+reclutar {ID caballeria} {cantidad}', 'value': 'Recluta la cantidad de caballeria solicitada'
    },
    {
      'name': '+construcciones {usuario}', 'value': 'Muestra las construcciones de un usuario, con sus ganancias y mantenimiento junto su ID de construccion'
    },
    {
      'name': '+añadir-defensa {ID solado} {cantidad} {ID construccion}', 'value': 'Añade una cantidad de un soldado en concreto a un edificio'
    },
    {
      'name': '+quitar-defensa {ID solado} {cantidad} {ID construccion}', 'value': 'Quita una cantidad de un soldado en concreto a un edificio'
    },
    {
      'name': '+resaltar {ID construccion} {usuario}', 'value': 'Resalta una construccion en especifico de un usuario en el mapa del juego'
    },
    {
      'name': '+rob {usuario}', 'value': 'Roba un porcentaje de dinero en la cartera de un usuario en específico'
    },
    {
      'name': '+traslado {ID soldado} {cantidad} {usuario}', 'value': 'Traslada una cantidad de un soldado en concreto al usuario mencionado' 
    },
    {
      'name': '+ejercito {usuario}', 'value': 'Muestra el ejercito de un usuario en concreto'
    },
    {
      'name': '+work', 'value': 'Consigue dinero trabajando un poquito'
    },
    {
      'name': '+slut', 'value': 'Consigue dinero robando. CUIDADO porque puedes perder dinero!'
    },
    {
      'name': '+redada {normal/grande/territorial} {posX} {posY}', 'value': 'Revela todas las construcciones de la mafia dentro del rango de busqueda de cada tipo empezando en una posición en específico del mapa. Una vez revelado, se decide a que construcción atacar con el ejercito de redadas', 'rol': 'Jefe de Policía'
    },
    {
      'name': '+impuestos {porcentaje}', 'value': 'Actualiza el porcentaje de impuestos que se asigna a los edificios construidos en la ciudad', 'rol': 'Alcalde' 
    },
    {
      'name': '+añadir-redada {ID soldado} {cantidad}', 'value': 'Añade una cantidad de soldados en específico al ejercito de redadas. NO se puede sacar soldados del ejercito!', 'no': 'Mafia'
    },
    {
      'name': '+ejercito-redada', 'value': 'Muestra el ejercito de redadas', 'rol': 'Dirigente'
    }
  ]
  help_moderador = [
    {
      'name': '+help', 'value': 'Muestra una lista de los comandos disponibles para cada rol'
    },
    {
      'name': '+start', 'value': 'En caso de no tener el rol de Economia aún, podrás usar este comando para empezar a formar parte de ella!!'
    },
    {
      'name': '+dep {amount/all}', 'value': 'Deposita una cantidad en concreto o todo el dinero de tu cartera al banco'
    },
    {
      'name': '+ret {amount/all}', 'value': 'Retira una cantidad en concreto o todo el dinero de tu banco a la cartera'
    },
    {
      'name': '+bal {usuario}', 'value': 'Muestra el balance del usuario mencionado'
    },
    {
      'name': '+shop', 'value': 'Muestra la tienda de tu rol predeterminado'
    },
    {
      'name': '+buy {ID producto} {cantidad}', 'value': 'Compra el objeto asignado con ese ID en la tienda de tu rol'
    },
    {
      'name': '+inv {usuario}', 'value': 'Muestra el inventario y la caballeria reclutada del usuario mencionado'
    },
    {
      'name': '+jackpot {apuesta} {dificultad (1, 2, 3)}', 'value': 'Apuesta tu dinero en un juego de azar!!'
    },
    {
      'name': '+caballos', 'value': 'Apuesta tu dinero en una carrera de caballos!!'
    },
    {
      'name': '+ruleta', 'value': 'Apuesta tu dinero en la ruleta del casino!!'
    },
    {
      'name': '+ppt {apuesta}', 'value': 'El clásico piedra, papel o tijera. Apuesta tu dinero y invita a un contrincante!'
    },
    {
      'name': '+give {usuario} {amount/all}', 'value': 'Transfiere una cantidad o todo tu dinero depositado en el banco a un usuario'
    },
    {
      'name': '+mapa', 'value': 'Muestra el mapa del juego actualizado hasta el momento'
    },
    {
      'name': '+reset {usuario} {balance/inventario/ejercito}', 'value': 'Resetea el inventario, balance o el ejercito de un usuario en especifico'
    },
    {
      'name': '+use {ID edificio} {posX} {posY}', 'value': 'Añade un edificio por cada posicion de 10 en 10 en el mapa original'
    },
    {
      'name': '+top', 'value': 'Muestra el top actualizado de las personas con mas dinero total'
    },
    {
      'name': '+list', 'value': 'Muestra los jugadores de esta economia con sus roles respectivos'
    },
    {
      'name': '+collect', 'value': 'Cobra todas las ganancias de tus construcciones cada 24h!'
    },
    {
      'name': '+caballeria', 'value': 'Muestra la caballeria disponible de sus roles respectivos'
    },
    {
      'name': '+reclutar {ID caballeria} {cantidad}', 'value': 'Recluta la cantidad de caballeria solicitada'
    },
    {
      'name': '+construcciones {usuario}', 'value': 'Muestra las construcciones de un usuario, con sus ganancias y mantenimiento junto su ID de construccion'
    },
    {
      'name': '+añadir-defensa {ID solado} {cantidad} {ID construccion}', 'value': 'Añade una cantidad de un soldado en concreto a un edificio'
    },
    {
      'name': '+quitar-defensa {ID solado} {cantidad} {ID construccion}', 'value': 'Quita una cantidad de un soldado en concreto a un edificio'
    },
    {
      'name': '+resaltar {ID construccion} {usuario}', 'value': 'Resalta una construccion en especifico de un usuario en el mapa del juego'
    },
    {
      'name': '+rob {usuario}', 'value': 'Roba un porcentaje de dinero en la cartera de un usuario en específico'
    },
    {
      'name': '+traslado {ID soldado} {cantidad} {usuario}', 'value': 'Traslada una cantidad de un soldado en concreto al usuario mencionado' 
    },
    {
      'name': '+ejercito {usuario}', 'value': 'Muestra el ejercito de un usuario en concreto'
    },
    {
      'name': '+work', 'value': 'Consigue dinero trabajando un poquito'
    },
    {
      'name': '+slut', 'value': 'Consigue dinero robando. CUIDADO porque puedes perder dinero!'
    },
    {
      'name': '+combate {usuario} {ID soldado 1} {cantidad soldado 1} {ID soldado 2} {cantidad soldado 2} ... {ID soldado N} {cantidad soldado N}', 'value': 'Lucha contra el usuario mencionado con el ID y cantidad de la caballeria que quiera mandar', 'rol': 'Mafia'
    },
    {
      'name': '+rendirse {usuario}', 'value': 'Ríndete ante una mafia para poder formar parte de su capofamiglia. Siendo un capofamiglia puedes MORIR para SIEMPRE!!!', 'rol': 'Mafia'
    },
    {
      'name': '+secuestrar {ID soldado 1} {cantidad soldado 1} {ID soldado 2} {cantidad soldado 2} ... {ID soldado N} {cantidad soldado N}', 'value': 'Manda un ejercito en busca de esclavos! Durante las 12h de búsqueda, tu ejercito mandado estará ausente!', 'rol': 'Mafia'
    },
    {
      'name': '+añadir-redada {ID soldado} {cantidad}', 'value': 'Añade una cantidad de soldados en específico al ejercito de redadas. NO se puede sacar soldados del ejercito!', 'no': 'Mafia'
    },
    {
      'name': '+gremio {usuario1} {usuario2} {apodo} {avatar} (opcional)', 'value': 'Formar gremio con un máximo de 3 miembros (contándote a tí mismo) con tal de poder optar a algunas ventajas (se pueden hacer gremios de 2 y 3 personas solo)', 'rol': 'Empresario'
    },
    {
      'name': '+tabla {ID gremio} {ID investigación}', 'value': 'Muestra la tabla de progreso de una investigación en concreta (de las 4 existentes) de un gremio en concreto', 'rol': 'Empresario'
    },
    {
      'name': '+mostrar-gremios', 'value': 'Muestra todos los gremios formados con sus porcentajes desbloqueados de cada investigación en el momento', 'rol': 'Empresario'
    },
    {
      'name': '+mejorar {ID investigación}', 'value': 'Compra el siguiente % a desbloquear de una investigación en concreto', 'rol': 'Empresario'
    },
    {
      'name': '+redada {normal/grande/territorial} {posX} {posY}', 'value': 'Revela todas las construcciones de la mafia dentro del rango de busqueda de cada tipo empezando en una posición en específico del mapa. Una vez revelado, se decide a que construcción atacar con el ejercito de redadas', 'rol': 'Jefe de Policía'
    },
    {
      'name': '+impuestos {porcentaje}', 'value': 'Actualiza el porcentaje de impuestos que se asigna a los edificios construidos en la ciudad', 'rol': 'Alcalde' 
    },
    {
      'name': '+ejercito-redada', 'value': 'Muestra el ejercito de redadas', 'rol': 'Dirigente'
    },
    {
      'name': '+add-money {amount} {wallet/bank} {usuario}', 'value': 'Añade una cantidad de dinero a la cartera o banco de un usuario específico', 'rol': 'Moderador'
    },
    {
      'name': '+remove-money {amount} {wallet/bank} {usuario}', 'value': 'Quita una cantidad de dinero a la cartera o banco de un usuario específico', 'rol': 'Moderador'
    },
    {
      'name': '+autoroles', 'value': 'Actualiza los autoroles de la persona mas rica y la persona con el ejército más poderoso'
    },
    {
      'name': '+actualizar', 'value': 'Actualiza todos los indices y datos de las personas en la Economía II'
    }
  ]

  if has_role(usuario, 'Moderador') is not False:
    pagination_view = HelpPaginationView(help_moderador, usuario, 'https://static.vecteezy.com/system/resources/previews/015/272/283/non_2x/construction-worker-icon-person-profile-avatar-with-hard-helmet-and-jacket-builder-man-in-a-helmet-icon-illustration-vector.jpg')
  elif obtener_rol_usuario(usuario) == 'Mafia':
    pagination_view = HelpPaginationView(help_mafia, usuario, 'https://i2.wp.com/johnothecoder.uk/wp-content/uploads/sites/11/2018/12/Mafia-Online-Avatar-600x600.jpg?ssl=1')
  elif obtener_rol_usuario(usuario) == 'Empresario':
    pagination_view = HelpPaginationView(help_empresario, usuario, 'https://images.vexels.com/media/users/3/129616/isolated/preview/fb517f8913bd99cd48ef00facb4a67c0-silueta-de-avatar-de-empresario.png')
  else:
    pagination_view = HelpPaginationView(help_dirigente, usuario, 'https://cdn.icon-icons.com/icons2/3082/PNG/512/police_policeman_avatar_man_people_icon_191330.png')

  await pagination_view.send(message)

async def Usar(message, game, bot):
  posX = int(message.content.split(' ')[2])
  posY = int(message.content.split(' ')[3])
  objeto_id = int(message.content.split(' ')[1])
  usuario = message.author
  color = None
  if has_role(usuario, 'Mafia'):
    color = (207, 75, 33)
  
  elif has_role(usuario, 'Empresario'):
    color = (0, 0, 128)

  else:
    color = (214, 214, 57)

  if usuario.id in game.solicitud:
    await message.channel.send(embed=discord.Embed(title='Espera!', description='Ya tienes una solicitud de construcción pendiente, espera a que acabe!', color=discord.Color.red()))
    return 0

  inventario = game.show_user_items(usuario.id)
  esta = False
  for objeto in inventario:
    if objeto['id'] == objeto_id:
      esta = True 
  
  if esta is False:
    await message.channel.send(embed=discord.Embed(title='Failed!', description='El ID de objeto puesto no existe!', color=discord.Color.red()))
    return 0
  
  if posX < 0 or posX >= 500 or posY < 0 or posY >= 500:
    await message.channel.send(embed=discord.Embed(title='Failed!', description='No puedes poner coordenadas por debajo de 0 o por encima de 500!!', color=discord.Color.red()))
    return 0
  
  game.solicitud.append(usuario.id)

  if await DibujarMapa(message, game, posX, posY, color, objeto_id, usuario, bot) is False:
    return 0

async def slut_work(message, game):
    emoji = discord.utils.get(message.guild.emojis, id=emoji_id)
    usuario = message.author
    cooldown = datetime.timedelta(seconds=15) ## 20
    multiplicador = 1
    if obtener_rol_usuario(usuario) == 'Mafia':
      if has_role(usuario, 'Jefe del Mercado') is not None:
        multiplicador = 3
      amount = random.randint(50, 125) * multiplicador * 2 ## 50, 125
    else:
      if has_role(usuario, 'Elon Musk') is not None:
        multiplicador = 3
      amount = random.randint(125, 250) * multiplicador * 4 ## 125, 250
    current_time = datetime.datetime.now()
    last_time_used = datetime.datetime.strptime(game.last_used.get(usuario.id, '1970-01-01 00:00:00'), '%Y-%m-%d %H:%M:%S')

    if current_time - last_time_used < cooldown:
        remaining_time = cooldown - (current_time - last_time_used)
        await message.channel.send(embed=discord.Embed(title='Error', description=f"No puedes usar el comando nuevamente durante {remaining_time.seconds:.1f} segundos."))
        return

    game.add_money(usuario.id, amount, 'wallet')

    game.last_used[usuario.id] = current_time.strftime('%Y-%m-%d %H:%M:%S')
    await message.channel.send(embed=discord.Embed(title='Listo!', description=f"Has recibido {amount} monedas. {emoji}"))

  
class ConstruccionesPaginationView(PaginationView):
  def __init__(self, data, user, message, emoji, author_id):
    super().__init__(data)
    self.user = user
    self.message = message
    self.emoji = emoji
    self.author_id = author_id
    
  def create_embed(self, data):
    current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    embed = discord.Embed(title='Ejercito', description=f'Este es el ejercito de {self.user}:', color=discord.Color.blue())
    if self.user.avatar:
      embed.set_thumbnail(url=self.user.avatar.url)
    
    embed = discord.Embed(title='Construcciones', description=f'Construcciones proporcionadas por el usuario: {self.user}', color=discord.Color.blue())
    for objeto in data:
      id = objeto['id']
      nombre = objeto['nombre']
      ganancias = objeto['ganancias']
      mantenimiento = objeto['mantenimiento']
    
      embed.add_field(name=f'Nombre: {nombre} - ID: {id}', value=f'Ganancias: {ganancias} {self.emoji} - Mantenimiento: {mantenimiento} {self.emoji}', inline=False)
      if 'defensa' in objeto and self.user.id == self.author_id:
        for defensa in objeto['defensa']:
          nombre_defensa = defensa['nombre']
          cantidad_defensa = defensa['cantidad']
          embed.add_field(name='__DEFENSA__', value=f'Nombre: {nombre_defensa} - Cantidad: {cantidad_defensa}')
    embed.set_footer(text=f'{current_date}')
    
    return embed

async def mostrar_construcciones(message, game):
  emoji = discord.utils.get(message.guild.emojis, id=emoji_id)
  usuario = message.author
  if len(message.mentions) > 0:
    usuario = message.mentions[0]
  author_id = message.author.id
  construcciones = game.show_user_construcciones(usuario.id)
  if has_role(usuario, 'Mafia') and (has_role(message.author, 'Empresario') or has_role(message.author, 'Dirigente') or has_role(message.author, 'Alcalde')):
    embed = discord.Embed(title='Failed!', description='No puedes ver las construcciones de un mafioso siendo Empresario o Dirigente!')
    await message.channel.send(embed=embed)  
    return 0

  if construcciones is not None:
    pagination_view = ConstruccionesPaginationView(construcciones, usuario, message, emoji, author_id)
    await pagination_view.send(message)
  else:
    await message.channel.send(embed=discord.Embed(title='Construcciones', description=f'El usuario {usuario} no tiene ninguna construcción en el mapa!!', color=discord.Color.blue()))

        

async def lista(message):
  current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  guild = message.guild

  roles = {"Mafia": [], "Empresario": [], "Dirigente": []}

  for member in guild.members:
    member_roles = [role.name for role in member.roles]
    for role_name in roles.keys():
      if role_name in member_roles:
        roles[role_name].append(member)

  embed = discord.Embed(title='Lista de usuarios participantes',
                        color=discord.Color.blue())
  for role_name, members in roles.items():
    if members:
      usuarios = ', '.join(member.display_name for member in members)
      embed.add_field(name=role_name, value=f'- {usuarios}', inline=False)
    else:
      embed.add_field(name=role_name,
                      value='Ningún usuario con este rol',
                      inline=False)

  embed.set_footer(text=f'{current_date}')

  await message.channel.send(embed=embed)


async def mostrar_top(message, game):
  current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  emoji = discord.utils.get(message.guild.emojis, id=emoji_id)
  balances = game.get_all_balances(message)

  sorted_balances = sorted(balances.items(), key=lambda x: x[1]['wallet'] + x[1]['bank'], reverse=True)

  embed = discord.Embed(title='Top Economía', color=discord.Color.blue())

  for i, (user_id, balance) in enumerate(sorted_balances[:10]):
    user = message.guild.get_member(user_id)
    if user:
      position = i + 1
      username = user.display_name
      total_balance = balance['wallet'] + balance['bank']
      embed.add_field(name=f'{position}. {username}', value=f'Total: {total_balance} {emoji}', inline=False)

  embed.set_footer(text=f'{current_date}')

  await message.channel.send(embed=embed)


async def Accionismo(message, bot, game):
  if len(message.mentions) < 1:
    await message.channel.send(embed=discord.Embed(
      title='Failed!',
      description="Debes mencionar al menos a un usuario para formar equipo.",
      color=discord.Color.red()))
    return

  objeto_id = int(message.content.split(' ')[1])
  porcentajes = [
    int(p) for p in message.content.split(' ')[2:len(message.mentions) + 3]
  ]
  usuarios = [message.author] + message.mentions
  confirmados = []

  def check(m):
    return m.author in usuarios and m.content.lower() == "confirmar"

  try:
    for usuario in usuarios:
      await message.channel.send(embed=discord.Embed(
        title='IMPORTANTE!',
        description=
        f"{usuario.mention}, ¿confirmas tu participación? (responde con 'confirmar' en los próximos 60 segundos)",
        color=discord.Color.blue()))
      response = await bot.wait_for("message", check=check, timeout=60)
      confirmados.append(response.author)
  except asyncio.TimeoutError:
    await message.channel.send(embed=discord.Embed(
      title='Failed!',
      description="Se agotó el tiempo de espera. El equipo no se formó.",
      color=discord.Color.red()))

  if len(confirmados) == len(usuarios):
    if sum(porcentajes) == 100:
      equipo = {
        'miembros': [usuario.id for usuario in usuarios], 
        'porcentajes': porcentajes,
        'objeto_id': objeto_id
      }
      if 'empresario' in game.equipos:
        game.equipos['empresario'].append(equipo)
      else:
        game.equipos['empresario'] = [equipo]

      await message.channel.send(embed=discord.Embed(
        title='Confirmado!',
        description="¡Equipo confirmado! ¡Listos para la acción!",
        color=discord.Color.green()))
      print(game.equipos['empresario'])
    else:
      await message.channel.send(embed=discord.Embed(
        title='Failed!',
        description="La suma de los porcentajes debe ser igual a 100.",
        color=discord.Color.red()))
  else:
    await message.channel.send(embed=discord.Embed(
      title='Failed!',
      description=
      "No todos los usuarios confirmaron su participación. El equipo no se formó.",
      color=discord.Color.red()))

async def Gremios(message, bot, game):
  for mention in message.mentions:
    if mention == message.author:
      await message.channel.send(embed=discord.Embed(
      title='Failed!',
      description="No te menciones a ti mismo!",
      color=discord.Color.red()))
      return
  if len(message.mentions) < 1:
    await message.channel.send(embed=discord.Embed(
      title='Failed!',
      description="Debes mencionar al menos a un usuario para formar un gremio.",
      color=discord.Color.red()))
    return

  if len(message.mentions) > 2:
    await message.channel.send(embed=discord.Embed(
      title='Failed!',
      description="Debes mencionar máximo a 2 usuarios máximo para formar un gremio.",
      color=discord.Color.red()))
    return

  if len(message.content.split(' ')) <= len(message.mentions) + 1:
    await message.channel.send(embed=discord.Embed(
      title='Failed!',
      description="Debes poner un apodo al gremio!",
      color=discord.Color.red()))
    return
      
  nombre = message.content.split(' ')[len(message.mentions) + 1]
  
  if len(message.content.split(' ')) > len(message.mentions) + 3:
    await message.channel.send(embed=discord.Embed(
      title='Failed!',
      description="El nombre debe de ser 1 sola palabra!",
      color=discord.Color.red()))
    return

  usuarios = [message.author] + message.mentions
  logo = ' '
  print(len(message.content.split(' ')), len(message.mentions))
  if len(message.content.split(' ')) != len(message.mentions) + 2:
    logo = message.content.split(' ')[len(message.mentions) + 2]

  patron = r'https?://\S+\.(jpg|png|gif)$'
  if re.match(patron, logo) is None and logo != ' ':
    await message.channel.send(embed=discord.Embed(
      title='Failed!',
      description="Solo se admiten avatares .jpg, .png, .gif",
      color=discord.Color.red()))
    return
  
  for g in game.gremios:
    for miembro in g['miembros']:
      for usuario in usuarios:
        if miembro == usuario.id:
          await message.channel.send(embed=discord.Embed(
            title='Failed!',
            description="Tú o uno de los usuarios mencionados pertenecen ya a un gremio!",
            color=discord.Color.red()))
          return

  confirmados = []

  
  def check(m, usuario):
    return m.author == usuario and m.content.lower() == "confirmar" and m.author not in confirmados

  try:
    for usuario in usuarios:
      await message.channel.send(embed=discord.Embed(
        title='IMPORTANTE!',
        description=
        f"{usuario.mention}, ¿confirmas tu participación? (responde con 'confirmar' en los próximos 60 segundos)",
        color=discord.Color.blue()))
      response = await bot.wait_for("message", check=lambda m: check(m, usuario), timeout=60)
      confirmados.append(response.author)
  except asyncio.TimeoutError:
    await message.channel.send(embed=discord.Embed(
      title='Failed!',
      description="Se agotó el tiempo de espera. El gremio no se formó.",
      color=discord.Color.red()))

  if len(confirmados) == len(usuarios):
    gremio = {
      'id': len(game.gremios) + 1,
      'miembros': [usuario.id for usuario in usuarios],
      'desbloqueados': {nombre: [] for nombre in game.tabla.keys()},
      'logo': logo,
      'nombre': nombre
    }
      
    game.gremios.append(gremio)

    await message.channel.send(embed=discord.Embed(
        title='Confirmado!',
        description="¡Gremio confirmado! ¡Listos para la acción!",
        color=discord.Color.green()))
  else:
    await message.channel.send(embed=discord.Embed(
      title='Failed!',
      description=
      "No todos los usuarios confirmaron su participación. El gremio no se formó.",
      color=discord.Color.red()))  

async def mostrar_gremios(message, game):
    current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if not game.gremios:
        await message.channel.send(embed=discord.Embed(
            title='Gremios',
            description='No hay gremios registrados.',
            color=discord.Color.blue()))
        return

    embed = discord.Embed(title='Gremios', color=discord.Color.blue())

    for gremio in game.gremios:
        id = gremio['id']
        apodo = gremio['nombre']
        avatar_url = gremio['logo']
        embed.add_field(name=f'Gremio ID: {id}', value=f'**{apodo.upper()}**', inline=False)
        miembros = [str(message.guild.get_member(usuario_id)) for usuario_id in gremio['miembros']]
        descripcion = '\n'.join(miembros)
        embed.add_field(name='__**Miembros**__', value=descripcion, inline=True)
        if avatar_url != ' ':
          embed.set_thumbnail(url=avatar_url) 

        desbloqueados = []
        for investigacion, datos in game.tabla.items():
            porcentajes_desbloqueados = gremio['desbloqueados'].get(investigacion, [])
            if porcentajes_desbloqueados:
                porcentajes_desbloqueados_str = ', '.join(map(str, porcentajes_desbloqueados))
                desbloqueados.append(f'{datos["nombre"]}: {porcentajes_desbloqueados_str}%')
                
        if desbloqueados:
            embed.add_field(name='Porcentajes desbloqueados:', value='\n'.join(desbloqueados), inline=False)
    embed.set_footer(text=f'{current_date}')
    await message.channel.send(embed=embed)

  
async def reclutar(message, game, bot):
  current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  emoji = discord.utils.get(message.guild.emojis, id=emoji_id)
  author = message.author
  objeto = int(message.content.split(' ')[1])
  cantidad = int(message.content.split(' ')[2])
  roles = ["Empresario", "Dirigente", "Mafia"]

  for rol in roles:
    if discord.utils.get(message.guild.roles, name=rol) in author.roles:
      mensaje = game.reclutar_soldado(author.id, rol, objeto, cantidad, emoji, bot)

      embed = discord.Embed(title='Reclutamiento',
                            description=mensaje,
                            color=discord.Color.blue())
  

  embed.set_footer(text=f'{current_date}')

  await message.channel.send(embed=embed)

async def mostrar_soldados(message, game):
  current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  emoji = discord.utils.get(message.guild.emojis, id=emoji_id)
  roles = ["Empresario", "Dirigente", "Mafia"]
  author = message.author

  for rol in roles:
    if discord.utils.get(message.guild.roles, name=rol) in author.roles:
      soldados = game.show_soldados(rol)
      embed = discord.Embed(title='Tienda',
                            description=f'Bienvenido a la caballeria de {rol}!',
                            color=discord.Color.blue())

  for objeto in soldados:
    id = objeto['id']
    nombre = objeto['nombre']
    precio = objeto['precio']
    mantenimiento = objeto['mantenimiento']
    ataque = objeto['ataque']
    defensa = objeto['defensa']
    vida = objeto['vida']
    embed.add_field(name=nombre, value=f"ID: {id} - Precio: {precio} {emoji},  Mantenimiento: {mantenimiento} {emoji}, Ataque: {ataque} ⚔️, Defensa: {defensa} 🛡️, Vida: {vida} ❤️", inline=False)

  embed.set_footer(text=f'{current_date}')

  await message.channel.send(embed=embed)

class MafiaView(discord.ui.View):
  def __init__(self, message, objeto_id, game):
    super().__init__(timeout=120)
    self.message = message
    self.command_user_id = message.author.id
    self.mention = message.mentions[0]
    self.objeto_id = objeto_id
    self.construcciones = game.construcciones[message.mentions[0].id]
    self.button_pressed = False
    self.inventarioA = game.items[message.author.id]
    self.author = message.author
    
    with open('map_data.pkl', 'rb') as file:
      loaded_data = pickle.load(file)
    self.map_data = loaded_data['map_data']
    self.map_objects = loaded_data['map_objects']
    self.map_original = loaded_data['map_original']
  
  def GuardarMapa(self):
    with open('map_data.pkl', 'wb') as file:
      data = {
        'map_data': self.map_data,
        'map_objects': self.map_objects,
        'map_original': self.map_original
      }
      pickle.dump(data, file)

  @discord.ui.button(label='Secuestrar', style=discord.ButtonStyle.green)
  async def secuestrar(self, interaction: discord.Interaction, button: discord.ui.Button):
    if interaction.user.id == self.command_user_id and self.button_pressed is False:
      tiene = False
      usura = False
      self.clear_items()
      self.button_pressed = True

      if self.inventarioA is None:
        self.inventarioA = []

      esclavos = 0
      for construccion in self.construcciones:
        if construccion['id'] == self.objeto_id:
          nombre = construccion['nombre']
          esclavos = 0
          print(construccion)
          if 'requisitos' in construccion:
            for requisito in construccion['requisitos']:
              if requisito['nombre'] == 'Gerente' or requisito['nombre'] == 'Administrador':
                usura = True
                self.inventarioA.append(requisito)
              else:
                cantidad = int(requisito['cantidad'])
                for objeto in self.inventarioA:
                  if objeto['id'] == 11:
                    tiene = True
                    objeto['cantidad'] += cantidad
                    esclavos += cantidad

                if tiene is False:
                  esclavos += cantidad
                  esclavo = {
                    'id': 11,
                    'nombre': 'Esclavo',
                    'cantidad': cantidad
                  }
                  self.inventarioA.append(esclavo)
          if 'defensa' in construccion:
            for soldado in construccion['defensa']:
              cantidad = int(soldado['cantidad'])
              for objeto in self.inventarioA:
                if objeto['id'] == 11:
                  tiene = True
                  objeto['cantidad'] += cantidad
                  esclavos += cantidad

              if tiene is False:
                esclavos += cantidad
                esclavo = {
                  'id': 11,
                  'nombre': 'Esclavo',
                  'cantidad': cantidad
                }
                self.inventarioA.append(esclavo)

      for construccion in self.construcciones:
        if construccion['id'] == self.objeto_id:
          nombre = construccion['nombre']
          self.construcciones.remove(construccion)

      for x in range(500):
        for y in range(500):  
          if self.map_objects[x][y] and self.map_objects[x][y]['usuario'] == self.mention.id and self.map_objects[x][y]['objeto']['id'] == self.objeto_id:
            self.map_objects[x][y] = None
            self.map_data[x][y] = self.map_original[x][y]  

      self.GuardarMapa()        

      await interaction.response.edit_message(view=self)
      if usura:
        await interaction.followup.send(f'Has conseguido {esclavos} esclavos! Te has encontrado con algunos gerentes y algún administrador, te serán útiles! Han sido añadidos automáticamente a tu inventario', ephemeral=True)
      elif esclavos == 0:
        await interaction.followup.send('No hay nadie vivo! No has podido secuestrar a nadie 😔', ephemeral=True)
      else:
        await interaction.followup.send(f'Has conseguido {esclavos} esclavos! Han sido añadidos automáticamente a tu inventario', ephemeral=True)
      await self.mention.send(f'La mafia ha destruido tu {nombre}!!!')
    else:
      await interaction.response.send_message('No tienes permiso para seleccionar este botón.', ephemeral=True)

  @discord.ui.button(label='Protección', style=discord.ButtonStyle.green)
  async def proteccion(self, interaction: discord.Interaction, button: discord.ui.Button):
    if interaction.user.id == self.command_user_id and self.button_pressed is False:
      self.clear_items()
      await interaction.response.edit_message(view=self)

      self.button_pressed = True
      for construccion in self.construcciones:
        if construccion['id'] == self.objeto_id:
          nombre = construccion['nombre']
          construccion['mafia'] = int(self.author.id)
          await interaction.followup.send(f'{nombre} del jugador {self.mention}, ha sido puesto bajo protección. 🛡️', ephemeral=True)

      
    else:
      await interaction.response.send_message('No tienes permiso para seleccionar este botón.', ephemeral=True)

  @discord.ui.button(label='Destruir', style=discord.ButtonStyle.red)
  async def destruir(self, interaction: discord.Interaction, button: discord.ui.Button):
    if interaction.user.id == self.command_user_id and self.button_pressed is False:
      self.clear_items()
      self.button_pressed = True
      for construccion in self.construcciones:
        if construccion['id'] == self.objeto_id:
          nombre = construccion['nombre']
          self.construcciones.remove(construccion)
      
      for x in range(500):
        for y in range(500):  
          if self.map_objects[x][y] and self.map_objects[x][y]['usuario'] == self.mention.id and self.map_objects[x][y]['objeto']['id'] == self.objeto_id:
            self.map_objects[x][y] = None
            self.map_data[x][y] = self.map_original[x][y]  

      self.GuardarMapa()

      await interaction.response.edit_message(view=self)
      await interaction.followup.send(f'Asesino! Acabas de destruir {nombre} con todas las personas dentro!!!', ephemeral=True)
      await self.mention.send(f'La mafia ha destruido tu {nombre}!!!')
    else:
      await interaction.response.send_message('No tienes permiso para seleccionar este botón.', ephemeral=True)

  async def on_timeout(self):
    if self.button_pressed is False:
      self.clear_items()
      await self.message.channel.send('Se acabó el tiempo', view=self)

class InteractiveView(View):
  def __init__(self, message, bot, mafiaA, mafiaD, rolD, game, atacantes):
    super().__init__()
    self.message = message
    self.mention = message.mentions[0]
    self.author = message.author
    self.ejercitoA = game.ejercito[self.author.id]
    self.ejercitoD = game.ejercito[self.mention.id]
    self.bot = bot
    self.mafiaA = mafiaA
    self.mafiaD = mafiaD
    self.rolD = rolD
    self.game = game
    self.atacantes = atacantes

  @discord.ui.button(label='Me rindo', style=discord.ButtonStyle.red)
  async def on_button_click(self, interaction: discord.Interaction, button: discord.ui.Button):
    if interaction.user == self.author or interaction.user == self.mention:
      if self.rolD == 'Mafia':
        if interaction.user == self.mention:
          for atacante in self.atacantes:
            tiene = False
            for soldado in self.ejercitoA:
              if atacante['id'] == soldado['id']:
                tiene = True
                soldado['cantidad'] += atacante['cantidad']
                break
            if tiene is False:
              self.ejercitoA.append(atacante)

          if self.mafiaD is not None:
            for soldado in self.game.ejercito[self.mafiaD]:
              if soldado['id'] == self.mention.id:
                self.game.ejercito[self.mafiaD].remove(soldado)
              
          id = self.mention.id
          if self.ejercitoD:
            for soldado in self.ejercitoD:
              if soldado['id'] > 3:
                if self.ejercitoA:
                  self.ejercitoA.append(soldado.copy())
                else:
                  self.game.ejercito[self.author.id] = [soldado.copy()]
                self.ejercitoD.remove(soldado)
          
          capofamiglia = {
            'id': int(id),
            'nombre': str(self.mention),
            'cantidad': 1
          }

          if self.ejercitoA:
            self.ejercitoA.append(capofamiglia)
          else:
            self.game.ejercito[self.author.id] = [capofamiglia]

          await self.mention.send(embed=discord.Embed(title='Capofamiglia', description=f'Ahora tú y todos tus capofamiglias perteneceis a la capofamiglia de {self.author}!', color=discord.Color.green()))

        elif interaction.user == self.author:
          if self.mafiaA is not None:
            for soldado in self.game.ejercito[self.mafiaA]:
              if soldado['id'] == self.mention.id:
                self.game.ejercito[self.mafiaA].remove(soldado)
              
          id = self.author.id
          if self.ejercitoA:
            for soldado in self.ejercitoA:
              if soldado['id'] > 3:
                if self.ejercitoD:
                  self.ejercitoD.append(soldado.copy())
                else:
                  self.game.ejercito[self.mention.id] = [soldado.copy()]
                self.ejercitoA.remove(soldado)
              else:
                for aux in self.atacantes:
                  if aux['id'] == soldado['id']:
                    soldado['cantidad'] += aux['cantidad']
          
          capofamiglia = {
            'id': int(id),
            'nombre': str(self.author),
            'cantidad': 1
          }

          if self.ejercitoD:
            self.ejercitoD.append(capofamiglia)
          else:
            self.game.ejercito[self.mention.id] = [capofamiglia]

          await self.author.send(embed=discord.Embed(title='Capofamiglia', description=f'Ahora tú y todos tus capofamiglias perteneceis a la capofamiglia de {self.mention}!', color=discord.Color.green()))

      self.stop()
      self.clear_items()
      await interaction.response.edit_message(view=self)
    else:
      await interaction.response.send_message('No tienes permiso para pulsar este botón. Sólo pueden darle al botón los mafiosos!', ephemeral=True)

async def combate(message, game, bot, soldados_perdidos_A=0, soldados_perdidos_D=0):
  author = message.author
  construccion_id = int(message.content.split(' ')[1])
  mention = message.mentions[0]
  guild = bot.get_guild(g)

  estado = game.combates.get(author.id, False)
  if estado == True:
    await message.channel.send(embed=discord.Embed(title='Failed!', description='Ya estas atacando a alguien!', color=discord.Color.red()))
    return 0

  input_data = message.content.split(' ')
  objetos = []
  for i in range(3, len(input_data), 2):
    objeto_id = int(input_data[i])
    cantidad = int(input_data[i+1])
    objetos.append({'id': objeto_id, 'cantidad': cantidad})

  
  game.combates[author.id] = True
  print(objetos)

  construccionesD = game.show_user_construcciones(mention.id)

  for construccion in construccionesD:
    if 'mafia' in construccion:
      if construccion['mafia'] == author.id:
        game.combates[author.id] = False
        await message.channel.send(embed=discord.Embed(title='Failed!', description='No puedes atacar a un edificio bajo tu protección!', color=discord.Color.red()))
        return 0
    if construccion['id'] == construccion_id:
      if 'defensa' not in construccion:
        game.combates[author.id] = False
        await message.channel.send(embed=discord.Embed(title='Failed!', description='No puedes atacar a este edificio!', color=discord.Color.red()))
        return 0
  
  print(construccionesD)

  capofamigliaD = 0
  nuevo_diccionario_D = []
  for i, objeto in enumerate(construccionesD):
    if objeto['id'] == construccion_id:
      nombre = objeto['nombre']
      indice = i
      if objeto['defensa']:
        for defensa in objeto['defensa']:
          if defensa['id'] > 3:
            capofamigliaD += 1
          nuevo_diccionario_D.append(defensa)

  print(nuevo_diccionario_D)
  
  EjercitoA = game.show_user_ejercito(author.id)
  for soldado in EjercitoA:
    if soldado['id'] == mention.id:
      game.combates[author.id] = False
      await message.channel.send(embed=discord.Embed(title='Failed!', description='No puedes atacar a un miembro de tu capofamiglia!', color=discord.Color.red()))
      return 0
    
  EjercitoD = game.show_user_ejercito(mention.id)
  if EjercitoD:
    for soldado in EjercitoD:
      if soldado['id'] == author.id:
        game.combates[author.id] = False
        await message.channel.send(embed=discord.Embed(title='Failed!', description='No puedes atacar a un miembro de tu capofamiglia!', color=discord.Color.red()))
        return 0
    
  print(objetos)
  objetos_original = objetos.copy()
  objetos_aux = objetos.copy()
  EjercitoA = sorted(EjercitoA, key=lambda x: x['id'], reverse=False)
  print(EjercitoA)
  for objeto in objetos_aux:
    for soldado in EjercitoA:
      if soldado['id'] == objeto['id']:
        if objeto['cantidad'] - soldado['cantidad'] > 0:
          game.combates[author.id] = False
          await message.channel.send(embed=discord.Embed(title='Failed!', description='No puedes poner más soldados de los que tienes!', color=discord.Color.red()))
          return 0
            
  nuevo_diccionario_A = []
  capofamigliaA = 0
  objetos_aux = objetos.copy()
  print(objetos_original) 
  for objeto in objetos_aux:
    for soldado in EjercitoA:
      if soldado['id'] == objeto['id']:
        if objeto['id'] > 3:
          capofamigliaA += 1
        if objeto['cantidad'] > 0:
          nuevo_soldado = soldado.copy()
          nuevo_soldado['cantidad'] = objeto['cantidad']
          soldado['cantidad'] -= objeto['cantidad']
          
          objeto['cantidad'] = 0

          nuevo_diccionario_A.append(nuevo_soldado)
            
  if has_role(author, 'Empresario'):
    game.combates[author.id] = False
    await message.channel.send(embed=discord.Embed(title='Failed!', description=f'{author}, eres Empresario. No puedes atacar!', color=discord.Color.red()))
    return 0
    
  EjercitoA_sorted = sorted(nuevo_diccionario_A, key=lambda x: x['id'], reverse=False)
                
  EjercitoD_sorted = []
  if nuevo_diccionario_D:
    EjercitoD_sorted = sorted(nuevo_diccionario_D, key=lambda x: x['id'], reverse=False)

  cantidad_soldados_A = {}
  cantidad_soldados_D = {}

  for soldado in EjercitoA_sorted:
    soldado_id = soldado['id']
    cantidad = soldado.get('cantidad', 0)
    cantidad_soldados_A[soldado_id] = cantidad_soldados_A.get(soldado_id, 0) + cantidad
                
  if EjercitoD_sorted:
    for soldado in EjercitoD_sorted:
      soldado_id = soldado['id']
      cantidad = soldado.get('cantidad', 0)
      cantidad_soldados_D[soldado_id] = cantidad_soldados_D.get(soldado_id, 0) + cantidad

  print('--------------------')
  print(cantidad_soldados_A)
                
  max_id_R = min(cantidad_soldados_A.keys())
  nivel_actual_A = max_id_R
  nivel_superior_A = -1
  nivel_actual_D = -1
  nivel_superior_D = -1
                
  for clave, valor in cantidad_soldados_A.items():
    if max_id_R < clave:
      nivel_superior_A = clave
      break

  if cantidad_soldados_D:
    max_id_D = min(cantidad_soldados_D.keys())
    nivel_actual_D = max_id_D
    for clave, valor in cantidad_soldados_D.items():
      if max_id_D < clave:
        nivel_superior_D = clave
        break
  else:
    max_id_D = -1
    nivel_actual_D = -1 

  print(f'nivel_actual_D: {nivel_actual_D}, nivel_superior_D: {nivel_superior_D}, max_id_D: {max_id_D}')
      
  perdidas_nivel_actual_A = 0
  perdidas_nivel_actual_D = 0
  aplicado = False
  print(EjercitoD_sorted)
  print(EjercitoA_sorted)

  mafia = None
  guild = bot.get_guild(g)
  
  for member in guild.members:
    if has_role(member, 'Mafia'):

      mafiaA = None
      auxA = game.show_user_ejercito(member.id)
      if auxA:
        for mafia in auxA:
          if mafia['id'] == author.id:
            mafiaA = int(member.id)
            break

      mafiaD = None
      auxD = game.show_user_ejercito(member.id)
      if auxD:
        for mafia in auxD:
          if mafia['id'] == mention.id:
            mafiaD = int(member.id)
            break

  rolD = obtener_rol_usuario(mention)

  embedA = discord.Embed(title='Ataque', description=f'Ataque comenzado!!⚔️', color=discord.Color.blue())
  embedD = discord.Embed(title='Ataque', description=f'Te están atacando!!⚔️', color=discord.Color.blue())
  
  hay = False
  if nivel_actual_A >= 0 and nivel_actual_D >= 0:
    hay = True
    view = InteractiveView(message, bot, mafiaA, mafiaD, rolD, game, EjercitoA_sorted)
    messageA = await author.send(embed = embedA, view=view)

    try:
      messageD = await mention.send(embed=embedD)

      if rolD == 'Mafia':
        messageD = await mention.send(embed = embedD, view=view)
    
    except Exception:
      nivel_actual_D = -1
      hay = False

    multiplicador_A = 1
    multiplicador_D = 1
    if has_role(mention, 'El Padrino') or has_role(mention, 'Jefe de Asalto'):
      multiplicador_D = 3

    if has_role(author, 'El Padrino'):
      multiplicador_A = 3

    while nivel_actual_A >= 0 and nivel_actual_D >= 0 and view.is_finished() is False:
      TotalA = 0
      TotalD = 0
    
      tiene0 = False
      tiene1 = False
      tiene2 = False

      if has_role(mention, 'Dirigente'):
        for a in EjercitoD_sorted:
          if a['id'] == 3:
            TotalD += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_D.get(3, 0)
            tiene0 = True
          if a['id'] == 2:
            TotalD += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_D.get(2, 0)
            tiene1 = True
          if a['id'] == 1:
            TotalD += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_D.get(1, 0) * multiplicador_D
            tiene2 = True
    
        for a in EjercitoD_sorted:
          if a['id'] == 0:
            if tiene0 and tiene1 and tiene2:
              if a['cantidad'] < 40:
                TotalD += (a['ataque'] * 1.5 + (a['defensa'] + 15) * 2.25 + a['vida']) * cantidad_soldados_A.get(0, 0) * 3 * multiplicador_D
              else:
                cantidad_restante = cantidad_soldados_D.get(0, 0) - 40
                TotalD += (a['ataque'] * 1.5 + (a['defensa'] + 15) * 2.25 + a['vida']) * 40 * 3 * multiplicador_D
                TotalD += (a['ataque'] * 1.5 + a['defensa'] * 2.25 + a['vida']) * cantidad_restante * 3 * multiplicador_D
            elif tiene0 and tiene1:
              TotalD += (a['ataque'] * 1.5 + a['defensa'] * 2.25 + a['vida']) * cantidad_soldados_D.get(0, 0) * 3 * multiplicador_D
            elif tiene0 and tiene2:
              if a['cantidad'] < 40:
                TotalD += (a['ataque'] * 1.5 + (a['defensa'] + 15) * 1.5 + a['vida']) * cantidad_soldados_A.get(0, 0) * 3 * multiplicador_D
              else:
                cantidad_restante = cantidad_soldados_D.get(0, 0) - 40
                TotalD += (a['ataque'] * 1.5 + (a['defensa'] + 15) * 1.5 + a['vida']) * 40 * 3 * multiplicador_D
                TotalD += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_restante * 3 * multiplicador_D
            elif tiene1 and tiene2:
              if a['cantidad'] < 40:
                TotalD += (a['ataque'] * 1.5 + (a['defensa'] + 15) * 2.25 + a['vida']) * cantidad_soldados_A.get(0, 0) * multiplicador_D
              else:
                cantidad_restante = cantidad_soldados_D.get(0, 0) - 40
                TotalD += (a['ataque'] * 1.5 + (a['defensa'] + 15) * 2.25 + a['vida']) * 40 * multiplicador_D
                TotalD += (a['ataque'] * 1.5 + a['defensa'] * 2.25 + a['vida']) * cantidad_restante * multiplicador_D
            elif tiene2:
              if a['cantidad'] < 40: 
                TotalD += (a['ataque'] * 1.5 + (a['defensa'] + 15) * 1.5 + a['vida']) * cantidad_soldados_D.get(0, 0) * multiplicador_D
              else:
                cantidad_restante = cantidad_soldados_D.get(0, 0) - 40
                TotalD += (a['ataque'] * 1.5 + (a['defensa'] + 15) * 1.5 + a['vida']) * 40 * multiplicador_D
                TotalD += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_restante * multiplicador_D
            elif tiene1:
              TotalD += (a['ataque'] * 1.5 + a['defensa'] * 2.25 + a['vida']) * cantidad_soldados_D.get(0, 0) * multiplicador_D
            elif tiene0:
              TotalD += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_D.get(0, 0) * 3 * multiplicador_D
            else:
              TotalD += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_D.get(0, 0) * multiplicador_D
        
      tiene0 = False
      tiene1 = False
      if has_role(mention, 'Empresario'):
        for a in EjercitoD_sorted:
          if a['id'] == 3:
            TotalD += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_D.get(3, 0)
            tiene0 = True
          elif a['id'] == 2:
            TotalD += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_D.get(2, 0)
            tiene1 = True
              
        for a in EjercitoD_sorted:
          if a['id'] == 1:
            if tiene0:
              TotalD += ((a['ataque'] + 15) * 1.5 + (a['defensa'] + 20) * 1.5 + a['vida']) * cantidad_soldados_D.get(1, 0) * multiplicador_D
            else:
              TotalD += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_D.get(1, 0) * multiplicador_D
          elif a['id'] == 0:
            if a['cantidad'] >= 10:
              TotalD += (a['ataque'] * 1.5 + (a['defensa'] + 30) * 1.5 + a['vida']) * cantidad_soldados_D.get(0, 0) * multiplicador_D
            else:
              TotalD += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_D.get(0, 0) * multiplicador_D
    
      tiene0 = False
      tiene1 = False
      tienecapo = False

      for a in EjercitoA_sorted:
        if a['id'] == 3:
          TotalA += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_A.get(3, 0)
          tiene0 = True
        elif a['id'] == 2:
          TotalA += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_A.get(2, 0)
          tiene1 = True
        elif a['id'] > 3:
          tienecapo = True
    
      for a in EjercitoA_sorted:
        if a['id'] == 1 or a['id'] == 0:
          if tiene0 and tiene1 and tienecapo:
            if capofamigliaA <= 3:
              if cantidad_soldados_A.get(int(a['id']), 0) < 10:
                TotalA += (a['ataque'] * 1.65 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_A.get(int(a['id']), 0) * 1.25 * 1.15 * capofamigliaA * 2 * multiplicador_A
              else:
                cantidad_restante = cantidad_soldados_A.get(int(a['id']), 0) - 10
                TotalA += (a['ataque'] * 1.65 + a['defensa'] * 1.5 + a['vida']) * 10 * 1.15 * capofamigliaA * 2 * multiplicador_A
                TotalA += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_restante * 1.25 * 1.15 * capofamigliaA * 2 * multiplicador_A
            else:
              if cantidad_soldados_A.get(int(a['id']), 0) < 10:
                TotalA += (a['ataque'] * 1.65 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_A.get(int(a['id']), 0) * 1.25 * 1.15 * 3 * 2 * multiplicador_A
              else:
                cantidad_restante = cantidad_soldados_A.get(int(a['id']), 0) - 10
                TotalA += (a['ataque'] * 1.65 + a['defensa'] * 1.5 + a['vida']) * 10 * 1.15 * 3 * 2 * multiplicador_A
                TotalA += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_restante * 1.25 * 1.15 * 3 * 2 * multiplicador_A
          elif tiene0 and tienecapo:
            if capofamigliaA <= 3:
              TotalA += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_A.get(int(a['id']), 0) * 1.25 * 1.15 * capofamigliaA * 2 * multiplicador_A
            else:
              TotalA += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_A.get(int(a['id']), 0) * 1.25 * 1.15 * 3 * 2 * multiplicador_A
          elif tiene1 and tienecapo:
            if capofamigliaA <= 3:
              if cantidad_soldados_A.get(int(a['id']), 0) < 10:
                TotalA += (a['ataque'] * 1.65 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_A.get(int(a['id']), 0) * 1.15 * capofamigliaA * 2 * multiplicador_A
              else:
                cantidad_restante = cantidad_soldados_A.get(int(a['id']), 0) - 10
                TotalA += (a['ataque'] * 1.65 + a['defensa'] * 1.5 + a['vida']) * 10 * 1.15 * capofamigliaA * 2 * multiplicador_A
                TotalA += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_restante * 1.15 * capofamigliaA * 2 * multiplicador_A
            else:
              if cantidad_soldados_A.get(int(a['id']), 0) < 10:
                TotalA += (a['ataque'] * 1.65 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_A.get(int(a['id']), 0) * 1.15 * 3 * 2 * multiplicador_A
              else:
                cantidad_restante = cantidad_soldados_A.get(int(a['id']), 0) - 10
                TotalA += (a['ataque'] * 1.65 + a['defensa'] * 1.5 + a['vida']) * 10 * 1.15 * 3 * 2 * multiplicador_A
                TotalA += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_restante * 1.15 * 3 * 2 * multiplicador_A
          elif tiene0 and tiene1:
            if cantidad_soldados_A.get(int(a['id']), 0) < 10:
              TotalA += (a['ataque'] * 1.65 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_A.get(int(a['id']), 0) * 1.25 * multiplicador_A
            else:
              cantidad_restante = cantidad_soldados_A.get(int(a['id']), 0) - 10
              TotalA += (a['ataque'] * 1.65 + a['defensa'] * 1.5 + a['vida']) * 10 * multiplicador_A
              TotalA += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_restante * 1.25 * multiplicador_A
          elif tiene0:
            TotalA += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_A.get(int(a['id']), 0) * 1.25 * multiplicador_A
          elif tiene1:
            if cantidad_soldados_A.get(int(a['id']), 0) < 10:
              TotalA += (a['ataque'] * 1.65 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_A.get(int(a['id']), 0) * multiplicador_A
            else:
              cantidad_restante =cantidad_soldados_A.get(int(a['id']), 0) - 10
              TotalA += (a['ataque'] * 1.65 + a['defensa'] * 1.5 + a['vida']) * 10 * multiplicador_A
              TotalA += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_restante * multiplicador_A 
          else:
            TotalA += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_A.get(int(a['id']), 0) * multiplicador_A
    
      tiene0 = False
      tiene1 = False
      tienecapo = False
      
      if has_role(mention, 'Mafia'):
        for a in EjercitoD_sorted:
          if a['id'] == 3:
            TotalD += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_D.get(3, 0)
            tiene0 = True
          elif a['id'] == 2:
            TotalD += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_D.get(2, 0)
            tiene1 = True
          elif a['id'] > 3:
            tienecapo = True
    
        for a in EjercitoD_sorted:
          if a['id'] == 1 or a['id'] == 0:
            if tiene0 and tiene1 and tienecapo:
              if capofamigliaD <= 3:
                if cantidad_soldados_D.get(int(a['id']), 0) < 10:
                  TotalD += (a['ataque'] * 1.65 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_D.get(int(a['id']), 0) * 1.25 * 1.15 * capofamigliaD * 2 * multiplicador_D
                else:
                  cantidad_restante = cantidad_soldados_D.get(int(a['id']), 0) - 10
                  TotalD += (a['ataque'] * 1.65 + a['defensa'] * 1.5 + a['vida']) * 10 * 1.15 * capofamigliaD * 2 * multiplicador_D
                  TotalD += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_restante * 1.25 * 1.15 * capofamigliaD * 2 * multiplicador_D
              else:
                if cantidad_soldados_D.get(int(a['id']), 0) < 10:
                  TotalD += (a['ataque'] * 1.65 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_D.get(int(a['id']), 0) * 1.25 * 1.15 * 3 * 2 * multiplicador_D
                else:
                  cantidad_restante = cantidad_soldados_D.get(int(a['id']), 0) - 10
                  TotalD += (a['ataque'] * 1.65 + a['defensa'] * 1.5 + a['vida']) * 10 * 1.15 * 3 * 2 * multiplicador_D
                  TotalD += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_restante * 1.25 * 1.15 * 3 * 2 * multiplicador_D
            elif tiene0 and tienecapo:
              if capofamigliaD <= 3:
                TotalD += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_D.get(int(a['id']), 0) * 1.25 * 1.15 * capofamigliaD * 2 * multiplicador_D
              else:
                TotalD += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_D.get(int(a['id']), 0) * 1.25 * 1.15 * 3 * 2 * multiplicador_D 
            elif tiene1 and tienecapo:
              if capofamigliaD <= 3:
                if cantidad_soldados_D.get(int(a['id']), 0) < 10:
                  TotalD += (a['ataque'] * 1.65 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_D.get(int(a['id']), 0) * 1.15 * capofamigliaD * 2 * multiplicador_D
                else:
                  cantidad_restante = cantidad_soldados_D.get(int(a['id']), 0) - 10
                  TotalD += (a['ataque'] * 1.65 + a['defensa'] * 1.5 + a['vida']) * 10 * 1.15 * capofamigliaD * 2 * multiplicador_D
                  TotalD += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_restante * 1.15 * capofamigliaD * 2 * multiplicador_D
              else:
                if cantidad_soldados_D.get(int(a['id']), 0) < 10:
                  TotalD += (a['ataque'] * 1.65 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_D.get(int(a['id']), 0) * 1.15 * 3 * 2 * multiplicador_D
                else:
                  cantidad_restante = cantidad_soldados_D.get(int(a['id']), 0) - 10
                  TotalD += (a['ataque'] * 1.65 + a['defensa'] * 1.5 + a['vida']) * 10 * 1.15 * 3 * 2 * multiplicador_D
                  TotalD += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_restante * 1.15 * 3 * 2 * multiplicador_D
            elif tiene0 and tiene1:
              if cantidad_soldados_D.get(int(a['id']), 0) < 10:
                TotalD += (a['ataque'] * 1.65 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_D.get(int(a['id']), 0) * 1.25 * multiplicador_D
              else:
                cantidad_restante = cantidad_soldados_D.get(int(a['id']), 0) - 10
                TotalD += (a['ataque'] * 1.65 + a['defensa'] * 1.5 + a['vida']) * 10 * multiplicador_D
                TotalD += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_restante * 1.25 * multiplicador_D
            elif tiene0:
              TotalD += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_D.get(int(a['id']), 0) * 1.25 * multiplicador_D
            elif tiene1:
              if cantidad_soldados_D.get(int(a['id']), 0) < 10:
                TotalD += (a['ataque'] * 1.65 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_D.get(int(a['id']), 0) * multiplicador_D
              else:
                cantidad_restante = cantidad_soldados_D.get(int(a['id']), 0) - 10
                TotalD += (a['ataque'] * 1.65 + a['defensa'] * 1.5 + a['vida']) * 10 * multiplicador_D
                TotalD += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_restante * multiplicador_D  
            else:
              TotalD += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_D.get(int(a['id']), 0) * multiplicador_D
              
      print(TotalA, TotalD)
      
      fuerza_total = TotalA + TotalD
        
      porcentajeA = TotalA / fuerza_total * 100

      embedA = discord.Embed(title='Ataque', description=f'Has empezado a atacar {nombre} de {mention}.\nSi te quieres rendir, aprieta al botón!\n', color=discord.Color.blue())
      if author.avatar:
        embedA.set_thumbnail(url=author.avatar)

      embedD = discord.Embed(title='Ataque', description=f'Te está atacando tu {nombre} el jugador {author}.\nSi te quieres rendir, aprieta al botón!\n', color=discord.Color.blue())
      if mention.avatar:
        embedD.set_thumbnail(url=mention.avatar)
      
      contenido_soldados_A = ""
      contenido_soldados_D = ""
      for soldado in EjercitoA_sorted:
        id_soldado_A = soldado['id']
        nombre_soldado_A = soldado['nombre']
        cantidad_A = cantidad_soldados_A.get(id_soldado_A, 0)

        contenido_soldados_A += f"ID: {id_soldado_A} | Nombre: {nombre_soldado_A} | Cantidad: {cantidad_A}\n"
                  
      for soldado in EjercitoD_sorted:
        id_soldado_D = soldado['id']
        nombre_soldado_D = soldado['nombre']
        cantidad_D = cantidad_soldados_D.get(id_soldado_D, 0)
                    
        contenido_soldados_D += f"ID: {id_soldado_D} | Nombre: {nombre_soldado_D} | Cantidad: {cantidad_D}\n"

      embedA.add_field(name='__Ejercito Aliado__', value=contenido_soldados_A + f"Fuerza total restante: {TotalA} ⚔️", inline=False)
      embedA.add_field(name='__Ejercito Enemigo__', value=contenido_soldados_D + f"Fuerza total restante: ?????? ⚔️", inline=False)
                  
      embedD.add_field(name=f'__Ejercito Aliado__', value=contenido_soldados_D + f"Fuerza total restante: {TotalD} ⚔️", inline=False)
      embedD.add_field(name='__Ejercito Enemigo__', value=contenido_soldados_A + f"Fuerza total restante: ?????? ⚔️", inline=False)
        
      await messageA.edit(embed = embedA, view=view)
      await messageD.edit(embed = embedD, view=view)

      if aplicado is False:
        total_principio_D = TotalD
        total_principio_A = TotalA
        aplicado = True
      
      if porcentajeA >= 90:
        soldados_perdidos_A = 1
        soldados_perdidos_D = 10
        await asyncio.sleep(1)

      elif porcentajeA >= 80:
        soldados_perdidos_A = 1
        soldados_perdidos_D = 5
        await asyncio.sleep(2) #10

      elif porcentajeA >= 70:
        soldados_perdidos_A = 1
        soldados_perdidos_D = 3
        await asyncio.sleep(5) #100

      elif porcentajeA >= 60:
        soldados_perdidos_A = 1
        soldados_perdidos_D = 2
        await asyncio.sleep(10) #1000

      elif porcentajeA >= 55:
        soldados_perdidos_A = 1
        soldados_perdidos_D = 1.5
        await asyncio.sleep(15) #10000

      elif porcentajeA >= 45:
        soldados_perdidos_A = 1
        soldados_perdidos_D = 1
        await asyncio.sleep(20) #100000

      elif porcentajeA >= 40:
        soldados_perdidos_A = 1.5
        soldados_perdidos_D = 1
        await asyncio.sleep(15) #10000

      elif porcentajeA >= 30:
        soldados_perdidos_A = 2
        soldados_perdidos_D = 1
        await asyncio.sleep(10) #1000

      elif porcentajeA >= 20:
        soldados_perdidos_A = 3
        soldados_perdidos_D = 1
        await asyncio.sleep(5) #100

      elif porcentajeA >= 10:
        soldados_perdidos_A = 5
        soldados_perdidos_D = 1
        await asyncio.sleep(2) #10

      else:
        soldados_perdidos_A = 10
        soldados_perdidos_D = 1
        await asyncio.sleep(1)
    
      cantidad_soldados_A, cantidad_soldados_D, perdidas_nivel_actual_A, perdidas_nivel_actual_D, nivel_actual_A, nivel_superior_A, nivel_actual_D, nivel_superior_D = Perdidas_Soldados(cantidad_soldados_A, cantidad_soldados_D, soldados_perdidos_A, soldados_perdidos_D, perdidas_nivel_actual_A, nivel_actual_A, nivel_superior_A, perdidas_nivel_actual_D, nivel_actual_D, nivel_superior_D)
    
      print(f'nivel_actual_D: {nivel_actual_D}, nivel_superior_D: {nivel_superior_D}, max_id_D: {max_id_D}')
  if hay is True:
    if view.is_finished() is False:
      if construccionesD[indice]['defensa']:
        fuerza_restanteA = TotalA / total_principio_A * 100
        fuerza_restanteD = TotalD / total_principio_D * 100 
      else:
        fuerza_restanteA = 100
        fuerza_restanteD = 0

      print(fuerza_restanteA)
      print(EjercitoA_sorted)
      print(EjercitoA)
      print('----------------------------------')
      print(construccionesD[indice]['defensa'])
      print(EjercitoD_sorted)
      print('//////////////////////////////////////////////')

      if nivel_actual_D == -1:
        for a, b in zip_longest(EjercitoA_sorted, EjercitoD_sorted):
          for soldadoA, soldadoD in zip_longest(EjercitoA, construccionesD[indice]['defensa']):
            if fuerza_restanteA >= 75:
              if a and soldadoA and a['id'] == soldadoA['id']:
                soldadoA['cantidad'] += a['cantidad']
              if soldadoD and soldadoD['id'] > 3:
                miembro = guild.get_member(int(soldadoD['id']))
                game.eliminados.append(miembro)

                miembro.send(embed=discord.Embed(title='Eliminado!', description='Has sido derrotado en batalla, por tanto, quedas eliminado para el resto de la partida 😟', color=discord.Color.red()))

              if soldadoD:
                soldadoD['cantidad'] = 0
                  
            elif fuerza_restanteA >= 60:
              if a and soldadoA and ((a['id'] == soldadoA['id'] == 0) or (a['id'] == soldadoA['id'] == 1)):
                soldadoA['cantidad'] += round(a['cantidad'] - a['cantidad'] * 0.15)
              if b and soldadoD and ((b['id'] == soldadoD['id'] == 0) or (b['id'] == soldadoD['id'] == 1)):
                soldadoD['cantidad'] = round(soldadoD['cantidad'] - b['cantidad'] * 0.85)
              if a and soldadoA and a['id'] == soldadoA['id'] == 2:
                soldadoA['cantidad'] += round(a['cantidad'] - a['cantidad'] * 0.075)
              if b and soldadoD and b['id'] == soldadoD['id'] == 2:
                soldadoD['cantidad'] = round(soldadoD['cantidad'] - b['cantidad'] * 0.425)
              if a and soldadoA and a['id'] == soldadoA['id'] == 3:
                soldadoA['cantidad'] += round(a['cantidad'] - a['cantidad'] * 0.003)
              if b and soldadoD and b['id'] == soldadoD['id'] == 3:
                soldadoD['cantidad'] = round(soldadoD['cantidad'] - b['cantidad'] * 0.17)
              if a and soldadoA and a['id'] > 3 and soldadoA['id'] > 3:
                soldadoA['cantidad'] = 1
                    
            elif fuerza_restanteA >= 40:
              if a and soldadoA and ((a['id'] == soldadoA['id'] == 0) or (a['id'] == soldadoA['id'] == 1)):
                soldadoA['cantidad'] += round(a['cantidad'] - a['cantidad'] * 0.3)
              if b and soldadoD and ((b['id'] == soldadoD['id'] == 0) or (b['id'] == soldadoD['id'] == 1)):
                soldadoD['cantidad'] = round(soldadoD['cantidad'] - b['cantidad'] * 0.8)
              if a and soldadoA and a['id'] == soldadoA['id'] == 2:
                soldadoA['cantidad'] += round(a['cantidad'] - a['cantidad'] * 0.15)
              if b and soldadoD and b['id'] == soldadoD['id'] == 2:
                soldadoD['cantidad'] = round(soldadoD['cantidad'] - b['cantidad'] * 0.4)
              if a and soldadoA and a['id'] == soldadoA['id'] == 3:
                soldadoA['cantidad'] += round(a['cantidad'] - a['cantidad'] * 0.006)
              if b and soldadoD and b['id'] == soldadoD['id'] == 3:  
                soldadoD['cantidad'] = round(soldadoD['cantidad'] - b['cantidad'] * 0.16)
              if a and soldadoA and a['id'] > 3 and soldadoA['id'] > 3:
                soldadoA['cantidad'] = 1

            elif fuerza_restanteA >= 25:
              if a and soldadoA and ((a['id'] == soldadoA['id'] == 0) or (a['id'] == soldadoA['id'] == 1)):
                soldadoA['cantidad'] += round(a['cantidad'] - a['cantidad'] * 0.5)
              if b and soldadoD and ((b['id'] == soldadoD['id'] == 0) or (b['id'] == soldadoD['id'] == 1)):
                soldadoD['cantidad'] = round(soldadoD['cantidad'] - b['cantidad'] * 0.7)
              if a and soldadoA and a['id'] == soldadoA['id'] == 2:
                soldadoA['cantidad'] += round(a['cantidad'] - a['cantidad'] * 0.2)
              if b and soldadoD and b['id'] == soldadoD['id'] == 2:
                soldadoD['cantidad'] = round(soldadoD['cantidad'] - b['cantidad'] * 0.35)
              if a and soldadoA and a['id'] == soldadoA['id'] == 3:
                soldadoA['cantidad'] += round(a['cantidad'] - a['cantidad'] * 0.1)
              if b and soldadoD and b['id'] == soldadoD['id'] == 3:  
                soldadoD['cantidad'] = round(soldadoD['cantidad'] - b['cantidad'] * 0.14)
              if a and soldadoA and a['id'] > 3 and soldadoA['id'] > 3:
                soldadoA['cantidad'] = 1

            else:
              if a and soldadoA and ((a['id'] == soldadoA['id'] == 0) or (a['id'] == soldadoA['id'] == 1)):
                soldadoA['cantidad'] += round(a['cantidad'] - a['cantidad'] * 0.6)
              if b and soldadoD and ((b['id'] == soldadoD['id'] == 0) or (b['id'] == soldadoD['id'] == 1)):
                soldadoD['cantidad'] = round(soldadoD['cantidad'] - b['cantidad'] * 0.6)
              if a and soldadoA and a['id'] == soldadoA['id'] == 2:
                soldadoA['cantidad'] += round(a['cantidad'] - a['cantidad'] * 0.3)
              if b and soldadoD and b['id'] == soldadoD['id'] == 2:
                soldadoD['cantidad'] = round(soldadoD['cantidad'] - b['cantidad'] * 0.3)
              if a and soldadoA and a['id'] == soldadoA['id'] == 3:
                soldadoA['cantidad'] += round(a['cantidad'] - a['cantidad'] * 0.12)
              if b and soldadoD and b['id'] == soldadoD['id'] == 3:
                soldadoD['cantidad'] = round(soldadoD['cantidad'] - b['cantidad'] * 0.12)
              if a and soldadoA and a['id'] > 3 and soldadoA['id'] > 3:
                soldadoA['cantidad'] = 1

            if soldadoD and int(soldadoD['cantidad']) <= 0:
              construccionesD[indice]['defensa'].remove(soldadoD)
            if soldadoA and int(soldadoA['cantidad']) <= 0:
              EjercitoA.remove(soldadoA)      
                  
        await author.send(embed=discord.Embed(title='Victoria!', description=f'{author}, has ganado contra {mention}!😎', color=discord.Color.green()), view=MafiaView(
          message, construccion_id, game))
        
      else:
        for a, b in zip_longest(EjercitoA_sorted, EjercitoD_sorted):
          for soldadoA, soldadoD in zip_longest(EjercitoA, construccionesD[indice]['defensa']):
            if fuerza_restanteD >= 75:
              if soldadoA and soldadoA['id'] > 3:
                miembro = guild.get_member(int(soldadoA['id']))
                game.eliminados.append(miembro)

                miembro.send(embed=discord.Embed(title='Eliminado!', description='Has sido derrotado en batalla, por tanto, quedas eliminado para el resto de la partida 😟', color=discord.Color.red()))
                  
            elif fuerza_restanteD >= 60:
              if b and soldadoD and ((b['id'] == soldadoD['id'] == 0) or (b['id'] == soldadoD['id'] == 1)):
                soldadoD['cantidad'] = round(soldadoD['cantidad'] - b['cantidad'] * 0.15)
              if a and soldadoA and ((a['id'] == soldadoA['id'] == 0) or (a['id'] == soldadoA['id'] == 1)):
                soldadoA['cantidad'] += round(a['cantidad'] - a['cantidad'] * 0.85)
              if b and soldadoD and b['id'] == soldadoD['id'] == 2:
                soldadoD['cantidad'] = round(soldadoD['cantidad'] - b['cantidad'] * 0.075)
              if a and soldadoA and a['id'] == soldadoA['id'] == 2:
                soldadoA['cantidad'] += round(a['cantidad'] - a['cantidad'] * 0.425)
              if b and soldadoD and b['id'] == soldadoD['id'] == 3:
                soldadoD['cantidad'] = round(soldadoD['cantidad'] - b['cantidad'] * 0.003)
              if a and soldadoA and a['id'] == soldadoA['id'] == 3:
                soldadoA['cantidad'] += round(a['cantidad'] - a['cantidad'] * 0.17)
                
            elif fuerza_restanteD >= 40:
              if b and soldadoD and ((b['id'] == soldadoD['id'] == 0) or (b['id'] == soldadoD['id'] == 1)):
                soldadoD['cantidad'] = round(soldadoD['cantidad'] - b['cantidad'] * 0.3)
              if a and soldadoA and ((a['id'] == soldadoA['id'] == 0) or (a['id'] == soldadoA['id'] == 1)):
                soldadoA['cantidad'] += round(a['cantidad'] - a['cantidad'] * 0.8)
              if b and soldadoD and b['id'] == soldadoD['id'] == 2:
                soldadoD['cantidad'] = round(soldadoD['cantidad'] - b['cantidad'] * 0.15)
              if a and soldadoA and a['id'] == soldadoA['id'] == 2:
                soldadoA['cantidad'] += round(a['cantidad'] - a['cantidad'] * 0.4)
              if b and soldadoD and b['id'] == soldadoD['id'] == 3:
                soldadoD['cantidad'] = round(soldadoD['cantidad'] - b['cantidad'] * 0.006)
              if a and soldadoA and a['id'] == soldadoA['id'] == 3:
                soldadoA['cantidad'] += round(a['cantidad'] - a['cantidad'] * 0.16)
                
            elif fuerza_restanteD >= 25:
              if b and soldadoD and ((b['id'] == soldadoD['id'] == 0) or (b['id'] == soldadoD['id'] == 1)):
                soldadoD['cantidad'] = round(soldadoD['cantidad'] - b['cantidad'] * 0.5)
              if a and soldadoA and ((a['id'] == soldadoA['id'] == 0) or (a['id'] == soldadoA['id'] == 1)):
                soldadoA['cantidad'] += round(a['cantidad'] - a['cantidad'] * 0.7)
              if b and soldadoD and b['id'] == soldadoD['id'] == 2:
                soldadoD['cantidad'] = round(soldadoD['cantidad'] - b['cantidad'] * 0.25)
              if a and soldadoA and a['id'] == soldadoA['id'] == 2:
                soldadoA['cantidad'] += round(a['cantidad'] - a['cantidad'] * 0.35)
              if b and soldadoD and b['id'] == soldadoD['id'] == 3:
                soldadoD['cantidad'] = round(soldadoD['cantidad'] - b['cantidad'] * 0.1)
              if a and soldadoA and a['id'] == soldadoA['id'] == 3:
                soldadoA['cantidad'] += round(a['cantidad'] - a['cantidad'] * 0.14)
                
            else:
              if b and soldadoD and ((b['id'] == soldadoD['id'] == 0) or (b['id'] == soldadoD['id'] == 1)):
                soldadoD['cantidad'] = round(soldadoD['cantidad'] - b['cantidad'] * 0.6) 
              if a and soldadoA and ((a['id'] == soldadoA['id'] == 0) or (a['id'] == soldadoA['id'] == 1)):
                soldadoA['cantidad'] += round(a['cantidad'] - a['cantidad'] * 0.6) 
              if b and soldadoD and b['id'] == soldadoD['id'] == 2:
                soldadoD['cantidad'] = round(soldadoD['cantidad'] - b['cantidad'] * 0.3) 
              if a and soldadoA and a['id'] == soldadoA['id'] == 2:
                soldadoA['cantidad'] += round(a['cantidad'] - a['cantidad'] * 0.3) 
              if b and soldadoD and b['id'] == soldadoD['id'] == 3:
                soldadoD['cantidad'] = round(soldadoD['cantidad'] - b['cantidad'] * 0.12)
              if a and soldadoA and a['id'] == soldadoA['id'] == 3:
                soldadoA['cantidad'] += round(a['cantidad'] - a['cantidad'] * 0.12) 

            if soldadoD and int(soldadoD['cantidad']) <= 0:
              construccionesD[indice]['defensa'].remove(soldadoD)
            if soldadoA and int(soldadoA['cantidad']) <= 0:
              EjercitoA.remove(soldadoA)
            
              if soldadoA['id'] > 3:
                miembro = guild.get_member(int(soldado['id']))
                game.eliminados.append(miembro)

                miembro.send(embed=discord.Embed(title='Eliminado!', description='Has sido derrotado en batalla, por tanto, quedas eliminado para el resto de la partida 😟', color=discord.Color.red()))
          
        await message.channel.send(embed=discord.Embed(title='Derrota!', description=f'{author}, has perdido contra {mention}!😟', color=discord.Color.red()))
  else:
    if nivel_actual_D == -1:
      print(EjercitoA)
      print('----------')
      print(EjercitoA_sorted)

      for a in EjercitoA_sorted:
        for soldadoA in EjercitoA:
          if a and soldadoA and soldadoA['id'] == a['id']:
            soldadoA['cantidad'] += a['cantidad']
        
      await author.send(embed=discord.Embed(title='Victoria!', description=f'{author}, has ganado contra {mention}!😎', color=discord.Color.green()), view=MafiaView(
      message, construccion_id, game))
      try:
        await mention.send(embed=discord.Embed(title='Derrota!', description=f'{mention}, has perdido contra {author}!😟', color=discord.Color.red()))
      except Exception:
        game.combates[author.id] = False
        return 0

    else:
      await mention.send(embed=discord.Embed(title='Victoria!', description=f'{mention}, has ganado contra {author}!😎', color=discord.Color.green()))
      await author.send(embed=discord.Embed(title='Derrota!', description=f'{author}, has perdido contra {mention}!😟', color=discord.Color.red()))

  game.combates[author.id] = False

     
      
def Perdidas_Soldados(cantidad_soldados_A, cantidad_soldados_D, soldados_perdidos_A, soldados_perdidos_D, perdidas_nivel_actual_A, nivel_actual_A, nivel_superior_A, perdidas_nivel_actual_D, nivel_actual_D, nivel_superior_D):
    cantidad_soldados_nivel_A = cantidad_soldados_A.get(nivel_actual_A, 0)

    if cantidad_soldados_nivel_A != 0:
        if cantidad_soldados_nivel_A >= soldados_perdidos_A:
            cantidad_soldados_A[nivel_actual_A] -= soldados_perdidos_A
            perdidas_nivel_actual_A += soldados_perdidos_A

            if perdidas_nivel_actual_A >= 10:
                cantidad_soldados_nivel_superior_A = cantidad_soldados_A.get(nivel_superior_A, 0)

                if cantidad_soldados_nivel_superior_A >= 1:
                    cantidad_soldados_A[nivel_superior_A] -= 1
                else:
                    cantidad_soldados_A[nivel_superior_A] = 0

                perdidas_nivel_actual_A = 0
        else:
            soldados_perdidos_A -= cantidad_soldados_nivel_A
            cantidad_soldados_A[nivel_actual_A] = 0
            nivel_actual_A = nivel_superior_A
            nivel_superior_A = next((key for key in sorted(cantidad_soldados_A.keys()) if key > nivel_actual_A), -1)
            perdidas_nivel_actual_A = 0
    else:
        if max(cantidad_soldados_A.keys()) != nivel_actual_A:
            nivel_actual_A = nivel_superior_A
            nivel_superior_A = next((key for key in sorted(cantidad_soldados_A.keys()) if key > nivel_actual_A), -1)
            perdidas_nivel_actual_A = 0
        else:
            nivel_actual_A = -1

    print(nivel_actual_A, nivel_superior_A, cantidad_soldados_nivel_A)
    print(nivel_actual_D, nivel_superior_D, cantidad_soldados_nivel_D)

    cantidad_soldados_nivel_D = cantidad_soldados_D.get(nivel_actual_D, 0)
    if cantidad_soldados_nivel_D != 0:
        if cantidad_soldados_nivel_D >= soldados_perdidos_D:
            cantidad_soldados_D[nivel_actual_D] -= soldados_perdidos_D
            perdidas_nivel_actual_D += soldados_perdidos_D
            if perdidas_nivel_actual_D >= 10:
                cantidad_soldados_nivel_superior_D = cantidad_soldados_D.get(nivel_superior_D, 0)
                if cantidad_soldados_nivel_superior_D >= 1:
                    cantidad_soldados_D[nivel_superior_D] -= 1
                else:
                    cantidad_soldados_D[nivel_superior_D] = 0

                perdidas_nivel_actual_D = 0
        else:
            soldados_perdidos_D -= cantidad_soldados_nivel_D
            cantidad_soldados_D[nivel_actual_D] = 0
            nivel_actual_D = nivel_superior_D
            nivel_superior_D = next((key for key in sorted(cantidad_soldados_D.keys()) if key > nivel_actual_D), -1)
            perdidas_nivel_actual_D = 0
    else:
        if max(cantidad_soldados_D.keys()) != nivel_actual_D:
            nivel_actual_D = nivel_superior_D
            nivel_superior_D = next((key for key in sorted(cantidad_soldados_D.keys()) if key > nivel_actual_D), -1)
            perdidas_nivel_actual_D = 0
        else:
            nivel_actual_D = -1

    print(cantidad_soldados_A, cantidad_soldados_D)
    return cantidad_soldados_A, cantidad_soldados_D, perdidas_nivel_actual_A, perdidas_nivel_actual_D, nivel_actual_A, nivel_superior_A, nivel_actual_D, nivel_superior_D

async def comprar_tabla(message, game):
    usuario = message.author
    investigacion_compra = int(message.content.split(' ')[1])

    for g in game.gremios:
        for miembro in g['miembros']:
            if usuario.id == miembro:
                for index, (investigacion, datos) in enumerate(game.tabla.items(), start=1):
                    if index == investigacion_compra:
                        progresos = datos['procentajes']
                        precios = datos['precio']
                        desbloqueados = g['desbloqueados'].get(investigacion, [])

                        if len(desbloqueados) >= len(progresos):
                            await message.channel.send(embed=discord.Embed(
                                title='Compra no válida',
                                description='Ya has desbloqueado todos los porcentajes de esta investigación.',
                                color=discord.Color.red()))
                            return

                        siguiente_porcentaje = len(desbloqueados) + 1

                        if siguiente_porcentaje > len(progresos):
                            await message.channel.send(embed=discord.Embed(
                                title='Compra no válida',
                                description='Ya has desbloqueado todos los porcentajes de esta investigación.',
                                color=discord.Color.red()))
                            return

                        porcentaje_actual = progresos[siguiente_porcentaje - 1]
                        precio_actual = precios[siguiente_porcentaje - 1]
                        if game.remove_money(usuario.id, precio_actual, 'wallet'):
                            desbloqueados.append(porcentaje_actual)
                            await message.channel.send(embed=discord.Embed(
                                title='Compra exitosa',
                                description=f'Has comprado el porcentaje {porcentaje_actual}% de la investigación {investigacion}.',
                                color=discord.Color.green()))

                            g['desbloqueados'][investigacion] = desbloqueados
                            for i, gremio in enumerate(game.gremios):
                                if gremio['id'] == g['id']:
                                    game.gremios[i] = g
                                    break
                            
                            print(g['desbloqueados'][investigacion])
                            if investigacion == 'Defensa':
                              ejercito = game.show_user_ejercito(usuario.id)

                              for soldado in ejercito:
                                for s in game.soldados['Empresario']:
                                  if s['id'] == soldado['id']:
                                    soldado['defensa'] = s['defensa'] * (1 + 100 / g['desbloqueados'][investigacion][-1])

                            return
                        else:
                            await message.channel.send(embed=discord.Embed(
                                title='Compra no válida',
                                description='No tienes suficiente dinero para realizar esta compra.',
                                color=discord.Color.red()))

                            return 
                        

                await message.channel.send(embed=discord.Embed(
                    title='Investigación no encontrada',
                    description='No se encontró la investigación especificada.',
                    color=discord.Color.red()))
                return

    await message.channel.send(embed=discord.Embed(
        title='Gremio no encontrado',
        description='No se encontró un gremio al que pertenezcas.',
        color=discord.Color.red()))
        
def generar_barra_de_progreso(max_desbloqueado, max_porcentaje, ancho, alto, color_relleno, color_fondo):
    image = Image.new("RGB", (ancho, alto))
    draw = ImageDraw.Draw(image)

    # Dibujar el fondo de la barra
    draw.rectangle([(0, 0), (ancho, alto)], fill=color_fondo)

    # Calcular el ancho de la barra de progreso en función del porcentaje máximo
    progreso_ancho = int(ancho * max_desbloqueado / max_porcentaje)

    # Dibujar la barra de progreso
    draw.rectangle([(0, 0), (progreso_ancho, alto)], fill=color_relleno)
  
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='PNG')
    image_bytes.seek(0)

    return image, image_bytes


async def mostrar_investigaciones(message, game):
    emoji = discord.utils.get(message.guild.emojis, id=emoji_id)
    ancho_barra = 900
    alto_barra = 40
    color_relleno = (0, 0, 255)  # Color azul
    color_fondo = (200, 200, 200)  # Color gris claro
    emoji_tick = '✅'

    gremio_id = int(message.content.split(' ')[1])
    investigacion_id = int(message.content.split(' ')[2]) if len(message.content.split(' ')) > 2 else None
    gremio = None
    for g in game.gremios:
        if g['id'] == gremio_id:
            gremio = g
            break

    if not gremio:
        await message.channel.send(embed=discord.Embed(
            title='Gremio no encontrado',
            description='No se encontró un gremio con el ID proporcionado.',
            color=discord.Color.red()))
        return
    if investigacion_id is not None:
      for investigacion, datos in game.tabla.items():
        if investigacion_id == datos['id']:
          embed = discord.Embed(title=f'Progreso del Gremio ID: {gremio_id}', color=discord.Color.blue())
          id = datos['id']
          nombre = datos['nombre']
          progresos = datos['procentajes']
          precios = datos['precio']

          descripcion = f'**{nombre}**\n'
          for i, progreso in enumerate(progresos):
            
              desbloqueado = investigacion in gremio['desbloqueados'] and i < len(gremio['desbloqueados'][investigacion])
              if desbloqueado:
                  descripcion += f'Progreso: {progreso}% - Precio: {precios[i]} {emoji} - Desbloqueado {emoji_tick}\n'
              else:
                  descripcion += f'Progreso: {progreso}% - Precio: {precios[i]} {emoji}\n'
          embed.add_field(name=f'Investigación: {investigacion} - ID: {id}', value=descripcion, inline=False)
          
          max_desbloqueado = max(gremio['desbloqueados'][investigacion], default=0)
          max_porcentaje = max(datos['procentajes'])
          barra_progreso, image_bytes = generar_barra_de_progreso(max_desbloqueado, max_porcentaje, ancho_barra, alto_barra, color_relleno, color_fondo)
          image_path = f'barra_progreso_{investigacion}.png'
          barra_progreso.save(image_path)
          embed.set_image(url=f'attachment://{image_path}')

          await message.channel.send(embed=embed, file=discord.File(image_bytes, image_path))
          os.remove(image_path)
    else:
      for investigacion, datos in game.tabla.items():
          embed = discord.Embed(title=f'Progreso del Gremio ID: {gremio_id}', color=discord.Color.blue())
          id = datos['id']
          nombre = datos['nombre']
          progresos = datos['procentajes']
          precios = datos['precio']

          descripcion = f'**{nombre}**\n'
          for i, progreso in enumerate(progresos):
            
              desbloqueado = investigacion in gremio['desbloqueados'] and i < len(gremio['desbloqueados'][investigacion])
              if desbloqueado:
                  descripcion += f'Progreso: {progreso}% - Precio: {precios[i]} {emoji} - Desbloqueado {emoji_tick}\n'
              else:
                  descripcion += f'Progreso: {progreso}% - Precio: {precios[i]} {emoji}\n'
          embed.add_field(name=f'Investigación: {investigacion} - ID: {id}', value=descripcion, inline=False)
          
          max_desbloqueado = max(gremio['desbloqueados'][investigacion], default=0)
          max_porcentaje = max(datos['procentajes'])
          barra_progreso, image_bytes = generar_barra_de_progreso(max_desbloqueado, max_porcentaje, ancho_barra, alto_barra, color_relleno, color_fondo)
          image_path = f'barra_progreso_{investigacion}.png'
          barra_progreso.save(image_path)
          embed.set_image(url=f'attachment://{image_path}')

          await message.channel.send(embed=embed, file=discord.File(image_bytes, image_path))

          os.remove(image_path)



async def añadir_defensa(message, game):
  current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  usuario = message.author
  soldado_id = int(message.content.split(' ')[1])
  cantidad = int(message.content.split(' ')[2])
  construccion_id = int(message.content.split(' ')[3])

  if obtener_rol_usuario(usuario) == 'Dirigente':
    usuario = message.mentions[0]

  construccion = game.show_user_construcciones(usuario.id)
  ejercito = game.show_user_ejercito(usuario.id)

  tiene = False
  for objeto in construccion:
    if objeto['id'] == construccion_id:
      nombre_objeto = objeto['nombre']
      if 'defensa' in objeto:
        for defensa in objeto['defensa']:
          if defensa['id'] == soldado_id:
            tiene = True
            for soldado in ejercito:
              if soldado['id'] == soldado_id and soldado['cantidad'] >= cantidad:
                nombre = soldado['nombre']
                              
                defensa['cantidad'] += cantidad
                soldado['cantidad'] -= cantidad

                if soldado['cantidad'] <= 0:
                  ejercito.remove(soldado)

                objeto['mantenimiento'] += soldado['mantenimiento'] * cantidad
                embed = discord.Embed(title='Añadido con éxito!', description=f'{cantidad} {nombre} han sido añadidos con éxito a la construcción {nombre_objeto}!', color=discord.Color.blue())
                embed.set_footer(text=f'{current_date}')
                await message.channel.send(embed=embed)
                return 0


        if tiene is False:
          for soldado in ejercito:
            if soldado['id'] == soldado_id and soldado['cantidad'] >= cantidad:
              soldado_aux = soldado.copy()
              soldado_aux['cantidad'] = cantidad
              nombre = soldado_aux['nombre']
              objeto['defensa'].append(soldado_aux)
              soldado['cantidad'] -= cantidad
              objeto['mantenimiento'] += soldado['mantenimiento'] * cantidad
              if soldado['cantidad'] <= 0:
                ejercito.remove(soldado)

              embed = discord.Embed(title='Añadido con éxito!', description=f'{cantidad} {nombre} han sido añadidos con éxito a la construcción {nombre_objeto}!', color=discord.Color.blue())
              embed.set_footer(text=f'{current_date}')
              await message.channel.send(embed=embed)
              return 0
    elif 'contenido' in objeto:
      for contenido in objeto['contenido']:
        if contenido['id'] == construccion_id:
          nombre_objeto = objeto['nombre']
          if 'defensa' in objeto:
            for defensa in objeto['defensa']:
              if defensa['id'] == soldado_id:
                tiene = True
                for soldado in ejercito:
                  if soldado['id'] == soldado_id and soldado['cantidad'] >= cantidad:
                    nombre = soldado['nombre']
                                  
                    defensa['cantidad'] += cantidad
                    soldado['cantidad'] -= cantidad

                    if soldado['cantidad'] <= 0:
                      ejercito.remove(soldado)

                    objeto['mantenimiento'] += soldado['mantenimiento'] * cantidad
                    embed = discord.Embed(title='Añadido con éxito!', description=f'{cantidad} {nombre} han sido añadidos con éxito a la construcción {nombre_objeto}!', color=discord.Color.blue())
                    embed.set_footer(text=f'{current_date}')
                    await message.channel.send(embed=embed)
                    return 0
            if tiene is False:
              for soldado in ejercito:
                if soldado['id'] == soldado_id and soldado['cantidad'] >= cantidad:
                  soldado_aux = soldado.copy()
                  soldado_aux['cantidad'] = cantidad
                  nombre = soldado_aux['nombre']
                  objeto['defensa'].append(soldado_aux)
                  soldado['cantidad'] -= cantidad

                  if soldado['cantidad'] <= 0:
                    ejercito.remove(soldado)

                  objeto['mantenimiento'] += soldado['mantenimiento'] * cantidad
                  embed = discord.Embed(title='Añadido con éxito!', description=f'{cantidad} {nombre} han sido añadidos con éxito a la construcción {nombre_objeto}!', color=discord.Color.blue())
                  embed.set_footer(text=f'{current_date}')
                  await message.channel.send(embed=embed)
                  return 0



async def quitar_defensa(message, game):
  current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  usuario = message.author
  soldado_id = int(message.content.split(' ')[1])
  cantidad = int(message.content.split(' ')[2])
  construccion_id = int(message.content.split(' ')[3])

  construccion = game.show_user_construcciones(usuario.id)
  ejercito = game.show_user_ejercito(usuario.id)

  rol = obtener_rol_usuario(usuario)

  tienda = game.tienda[rol]

  tiene = False
  for soldado in ejercito:
    if soldado['id'] == soldado_id:
      tiene = True
      for objeto in construccion:
        if objeto['id'] == construccion_id:
          nombre_objeto = objeto['nombre']
          for defensa in objeto['defensa']:
            if defensa['id'] == soldado_id and defensa['cantidad'] >= cantidad:
              for t in tienda:
                if t['nombre'] == objeto['nombre']:
                  for d in t['defensa']:
                    if soldado_id == d['id'] and d['cantidad'] > defensa['cantidad'] - cantidad:
                      embed = discord.Embed(title='Failed!', description='No puedes quitar la defensa predeterminada del edificio!', color=discord.Color.red())
                      embed.set_footer(text=f'{current_date}')
                      await message.channel.send(embed=embed)
                      return 0
              nombre = soldado['nombre']
              defensa['cantidad'] -= cantidad
              soldado['cantidad'] += cantidad
              if defensa['cantidad'] <= 0:
                objeto['defensa'].remove(defensa)

              objeto['mantenimiento'] -= soldado['mantenimiento'] * cantidad

              embed = discord.Embed(title='Quitado con éxito!', description=f'{cantidad} {nombre} han sido quitados con éxito a la construcción {nombre_objeto}!', color=discord.Color.blue())
              embed.set_footer(text=f'{current_date}')
              await message.channel.send(embed=embed)
              break
          break
        elif 'contenido' in objeto:
          for contenido in objeto['contenido']:
            if contenido['id'] == construccion_id:
              nombre_objeto = objeto['nombre']
              for defensa in objeto['defensa']:
                if defensa['id'] == soldado_id and defensa['cantidad'] >= cantidad:
                  for t in tienda:
                    if t['nombre'] == objeto['nombre']:
                      for d in t['defensa']:
                        if soldado_id == d['id'] and d['cantidad'] > defensa['cantidad'] - cantidad:
                          embed = discord.Embed(title='Failed!', description='No puedes quitar la defensa predeterminada del edificio!', color=discord.Color.red())
                          embed.set_footer(text=f'{current_date}')
                          await message.channel.send(embed=embed)
                          return 0
                  nombre = soldado['nombre']
                  defensa['cantidad'] -= cantidad
                  soldado['cantidad'] += cantidad
                  if defensa['cantidad'] <= 0:
                    objeto['defensa'].remove(defensa)
                  
                  objeto['mantenimiento'] -= soldado['mantenimiento'] * cantidad

                  embed = discord.Embed(title='Quitado con éxito!', description=f'{cantidad} {nombre} han sido quitados con éxito a la construcción {nombre_objeto}!', color=discord.Color.blue())
                  embed.set_footer(text=f'{current_date}')
                  await message.channel.send(embed=embed)
                  break
              break

  if tiene is False:
    for objeto in construccion:
      if objeto['id'] == construccion_id:
        nombre_objeto = objeto['nombre']
        for defensa in objeto['defensa']:
          if defensa['id'] == soldado_id and defensa['cantidad'] >= cantidad:
            for t in tienda:
                if t['nombre'] == objeto['nombre']:
                  for d in t['defensa']:
                    if soldado_id == d['id'] and d['cantidad'] > defensa['cantidad'] - cantidad:
                      embed = discord.Embed(title='Failed!', description='No puedes quitar la defensa predeterminada del edificio!', color=discord.Color.red())
                      embed.set_footer(text=f'{current_date}')
                      await message.channel.send(embed=embed)
                      return 0
            defensa_aux = defensa.copy()
            nombre = defensa_aux['nombre']
            ejercito.append(defensa_aux)
            defensa['cantidad'] -= cantidad

            if defensa['cantidad'] <= 0:
              objeto['defensa'].remove(defensa)

            objeto['mantenimiento'] -= soldado['mantenimiento'] * cantidad

            embed = discord.Embed(title='Quitado con éxito!', description=f'{cantidad} {nombre} han sido quitados con éxito a la construcción {nombre_objeto}!', color=discord.Color.blue())
            embed.set_footer(text=f'{current_date}')
            await message.channel.send(embed=embed)
            break
        break 
      elif 'contenido' in objeto:
        for contenido in objeto['contenido']:
          if contenido['id'] == construccion_id:
            nombre_objeto = objeto['nombre']
            for defensa in objeto['defensa']:
              if defensa['id'] == soldado_id and defensa['cantidad'] >= cantidad:
                for t in tienda:
                    if t['nombre'] == objeto['nombre']:
                      for d in t['defensa']:
                        if soldado_id == d['id'] and d['cantidad'] > defensa['cantidad'] - cantidad:
                          embed = discord.Embed(title='Failed!', description='No puedes quitar la defensa predeterminada del edificio!', color=discord.Color.red())
                          embed.set_footer(text=f'{current_date}')
                          await message.channel.send(embed=embed)
                          return 0
                defensa_aux = defensa.copy()
                nombre = defensa_aux['nombre']
                ejercito.append(defensa_aux)
                defensa['cantidad'] -= cantidad

                if defensa['cantidad'] <= 0:
                  objeto['defensa'].remove(defensa)

                objeto['mantenimiento'] -= soldado['mantenimiento'] * cantidad
                  
                embed = discord.Embed(title='Quitado con éxito!', description=f'{cantidad} {nombre} han sido quitados con éxito a la construcción {nombre_objeto}!', color=discord.Color.blue())
                embed.set_footer(text=f'{current_date}')
                await message.channel.send(embed=embed)
                break
            break 
    
    
async def asignar_impuestos(message, game, bot):
  usuario = message.author
  impuesto = int(message.content.split(' ')[1])

  guild = bot.get_guild(g)

  for member in guild.members:
    construcciones = game.show_user_construcciones(member.id)
    if construcciones:
      for construccion in construcciones:
        if 'impuestos' in construccion:
          construccion['impuestos'] = impuesto
  
  await message.channel.send(embed=discord.Embed(title='Impuestos!', description=f'Se han cambiado los impuestos sobre los edificios a un {impuesto}%'))    

async def incorporazione(message, game, bot):
  author = message.author
  mention = message.mentions[0]
  guild = bot.get_guild(g)

  if has_role(mention, 'Mafia'):
    ejercitoM = game.show_user_ejercito(mention.id)

    if ejercitoM is not None:
      for soldado in ejercitoM:
        if soldado['id'] == mention.id:
          await message.channel.send(embed=discord.Embed(title='Failed!', description='Ya formas parte de la capofamiglia!', color=discord.Color.red()))
          return 0
    
    for member in guild.members:
      if has_role(member, 'Mafia'):
        mafias = game.show_user_ejercito(member.id)
        if mafias:
          for m in mafias:
            if m['id'] == author.id:
              await message.channel.send(embed=discord.Embed(title='Failed!', description=f'Ya perteneces a la capofamiglia de {author}!', color=discord.Color.red()))
              return 0
    
    id = author.id

    ejercitoA = game.show_user_ejercito(author.id)

    if ejercitoA is not None:
      for soldado in ejercitoA:
        if soldado['id'] == mention.id:
          await message.channel.send(embed=discord.Embed(title='Failed!', description='No puedes rendirte ante un capofamiglia tuyo!', color=discord.Color.red()))
          return 0 
    
    def check(m):
      return m.author == author and m.content.lower() == "confirmar"

    try:
      await message.channel.send(embed=discord.Embed(
        title='IMPORTANTE!',
        description=
        f"{author.mention}, ¿confirmas tu rendición ante {mention}? (responde con 'confirmar' en los próximos 60 segundos)",
        color=discord.Color.blue()))
      await bot.wait_for("message", check=check, timeout=60)
    except asyncio.TimeoutError:
      await message.channel.send(embed=discord.Embed(
        title='Failed!',
        description="Se agotó el tiempo de espera. No te has rendido!",
        color=discord.Color.red()))
      return 0
        

    for soldado in ejercitoA:
      if soldado['id'] > 3:
        if ejercitoM:
          ejercitoM.append(soldado.copy())
        else:
          game.ejercito[mention.id] = [soldado.copy()]
        ejercitoA.remove(soldado)
    
    capofamiglia = {
      'id': int(id),
      'nombre': str(author),
      'cantidad': 1
    }

    if ejercitoM:
      ejercitoM.append(capofamiglia)
    else:
      game.ejercito[mention.id] = [capofamiglia]

    await message.channel.send(embed=discord.Embed(title='Capofamiglia', description=f'Ahora tú y todos tus capofamiglias perteneceis a la capofamiglia de {mention}!', color=discord.Color.green()))

async def secuestrar(message, game):
  author = message.author

  input_data = message.content.split(' ')
  objetos = []
  for i in range(1, len(input_data) - 1, 2):
    objeto_id = int(input_data[i])
    cantidad = int(input_data[i+1])
    objetos.append({'id': objeto_id, 'cantidad': cantidad})
  EjercitoA = game.show_user_ejercito(author.id)
  
  for soldado in EjercitoA:
    for objeto in objetos:
      if soldado['id'] == objeto['id']:
        if soldado['cantidad'] < objeto['cantidad']:
          await message.channel.send(embed=discord.Embed(title='Failed!', description='No puedes poner más soldados de los que tienes!', color=discord.Color.red()))
          return 0  
  
  cooldown = datetime.timedelta(seconds=43200)
  current_time = datetime.datetime.now()
  last_time_used = datetime.datetime.strptime(game.secuestros.get(author.id, '1970-01-01 00:00:00'), '%Y-%m-%d %H:%M:%S')

  if current_time - last_time_used < cooldown:
    remaining_time = cooldown - (current_time - last_time_used)
    await message.channel.send(embed=discord.Embed(title='Error', description=f"No puedes usar el comando nuevamente durante {remaining_time.seconds:.1f} segundos."))
    return
  
  game.secuestros[author.id] = current_time.strftime('%Y-%m-%d %H:%M:%S')

  print(objetos)
  objetos_aux = objetos.copy()
  EjercitoA = sorted(EjercitoA, key=lambda x: x['id'], reverse=False)
  print(EjercitoA)
  for objeto in objetos_aux:
    for soldado in EjercitoA:
      if soldado['id'] == objeto['id']:
        if objeto['cantidad'] - soldado['cantidad'] > 0:
          await message.channel.send(embed=discord.Embed(title='Failed!', description='No puedes poner más soldados de los que tienes!', color=discord.Color.red()))
          return 0
        
  nuevo_diccionario_A = []
  capofamigliaA = 0
  objetos_aux = objetos.copy()
  for objeto in objetos_aux:
    for soldado in EjercitoA:
      if soldado['id'] == objeto['id']:
        if objeto['id'] > 3:
          capofamigliaA += 1
        if objeto['cantidad'] > 0:
          nuevo_soldado = soldado.copy()
          nuevo_soldado['cantidad'] = objeto['cantidad']
          soldado['cantidad'] -= objeto['cantidad']
          
          objeto['cantidad'] = 0

          nuevo_diccionario_A.append(nuevo_soldado)

  EjercitoA_sorted = sorted(nuevo_diccionario_A, key=lambda x: x['id'], reverse=True)

  cantidad_soldados_A = {}
  
  for soldado in EjercitoA_sorted:
    soldado_id = soldado['id']
    cantidad = soldado.get('cantidad', 0)
    cantidad_soldados_A[soldado_id] = cantidad_soldados_A.get(soldado_id, 0) + cantidad
  
  multiplicador_A = 1

  if has_role(author, 'El Padrino'):
    multiplicador_A = 3

  TotalA = 0

  tiene0 = False
  tiene1 = False
  tienecapo = False

  for a in EjercitoA_sorted:
    if a['id'] == 3:
      TotalA += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_A.get(3, 0)
      tiene0 = True
    elif a['id'] == 2:
      TotalA += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_A.get(2, 0)
      tiene1 = True
    elif a['id'] > 3:
      tienecapo = True
    
  for a in EjercitoA_sorted:
    if a['id'] == 1 or a['id'] == 0:
      if tiene0 and tiene1 and tienecapo:
        if capofamigliaA <= 3:
          if cantidad_soldados_A.get(int(a['id']), 0) < 10:
            TotalA += (a['ataque'] * 1.65 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_A.get(int(a['id']), 0) * 1.25 * 1.15 * capofamigliaA * 2 * multiplicador_A
          else:
            cantidad_restante = cantidad_soldados_A.get(int(a['id']), 0) - 10
            TotalA += (a['ataque'] * 1.65 + a['defensa'] * 1.5 + a['vida']) * 10 * 1.15 * capofamigliaA * 2 * multiplicador_A
            TotalA += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_restante * 1.25 * 1.15 * capofamigliaA * 2 * multiplicador_A
        else:
          if cantidad_soldados_A.get(int(a['id']), 0) < 10:
            TotalA += (a['ataque'] * 1.65 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_A.get(int(a['id']), 0) * 1.25 * 1.15 * 3 * 2 * multiplicador_A
          else:
            cantidad_restante = cantidad_soldados_A.get(int(a['id']), 0) - 10
            TotalA += (a['ataque'] * 1.65 + a['defensa'] * 1.5 + a['vida']) * 10 * 1.15 * 3 * 2 * multiplicador_A
            TotalA += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_restante * 1.25 * 1.15 * 3 * 2 * multiplicador_A
      elif tiene0 and tienecapo:
        if capofamigliaA <= 3:
          TotalA += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_A.get(int(a['id']), 0) * 1.25 * 1.15 * capofamigliaA * 2 * multiplicador_A
        else:
          TotalA += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_A.get(int(a['id']), 0) * 1.25 * 1.15 * 3 * 2 * multiplicador_A
      elif tiene1 and tienecapo:
        if capofamigliaA <= 3:
          if cantidad_soldados_A.get(int(a['id']), 0) < 10:
            TotalA += (a['ataque'] * 1.65 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_A.get(int(a['id']), 0) * 1.15 * capofamigliaA * 2 * multiplicador_A
          else:
            cantidad_restante = cantidad_soldados_A.get(int(a['id']), 0) - 10
            TotalA += (a['ataque'] * 1.65 + a['defensa'] * 1.5 + a['vida']) * 10 * 1.15 * capofamigliaA * 2 * multiplicador_A
            TotalA += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_restante * 1.15 * capofamigliaA * 2 * multiplicador_A
        else:
          if cantidad_soldados_A.get(int(a['id']), 0) < 10:
            TotalA += (a['ataque'] * 1.65 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_A.get(int(a['id']), 0) * 1.15 * 3 * 2 * multiplicador_A
          else:
            cantidad_restante = cantidad_soldados_A.get(int(a['id']), 0) - 10
            TotalA += (a['ataque'] * 1.65 + a['defensa'] * 1.5 + a['vida']) * 10 * 1.15 * 3 * 2 * multiplicador_A
            TotalA += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_restante * 1.15 * 3 * 2 * multiplicador_A
      elif tiene0 and tiene1:
        if cantidad_soldados_A.get(int(a['id']), 0) < 10:
          TotalA += (a['ataque'] * 1.65 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_A.get(int(a['id']), 0) * 1.25 * multiplicador_A
        else:
          cantidad_restante = cantidad_soldados_A.get(int(a['id']), 0) - 10
          TotalA += (a['ataque'] * 1.65 + a['defensa'] * 1.5 + a['vida']) * 10 * multiplicador_A
          TotalA += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_restante * 1.25 * multiplicador_A
      elif tiene0:
        TotalA += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_A.get(int(a['id']), 0) * 1.25 * multiplicador_A
      elif tiene1:
        if cantidad_soldados_A.get(int(a['id']), 0) < 10:
          TotalA += (a['ataque'] * 1.65 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_A.get(int(a['id']), 0) * multiplicador_A
        else:
          cantidad_restante =cantidad_soldados_A.get(int(a['id']), 0) - 10
          TotalA += (a['ataque'] * 1.65 + a['defensa'] * 1.5 + a['vida']) * 10 * multiplicador_A
          TotalA += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_restante * multiplicador_A 
      else:
        TotalA += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_A.get(int(a['id']), 0) * multiplicador_A

  esclavosMax = TotalA / 150
  print(TotalA)
  if TotalA <= 0:
    await author.send('No has mandado ningún soldado 😔')
    return 0
  elif TotalA <= 150:
    esclavosMax = 2

  print(esclavosMax)
  esclavos = random.randint(1, round(esclavosMax))
  print(esclavos)
  inventarioA = game.show_user_items(author.id)
  perdidas = random.randint(30, 100)

  tiene = False
  if inventarioA:
    for items in inventarioA:
      if items['id'] == 11:
        items['cantidad'] += esclavos
        tiene = True
  else:
    inventarioA = []    

  if tiene is False:
    esclavo = {
      'id': 11,
      'nombre': 'Esclavo',
      'cantidad': esclavos
    }
  
    inventarioA.append(esclavo)

  for soldado in EjercitoA:
    for objeto in objetos:
      if soldado['id'] == objeto['id']:
        soldado['cantidad'] = round(soldado['cantidad'] - objeto['cantidad'] * (perdidas / 100))

        if soldado['cantidad'] <= 0:
          EjercitoA.remove(soldado)
        
  if EjercitoA == []:
    del EjercitoA

  await author.send(f'Tus soldados han vuelto con {esclavos} esclavos! Aprovecha y explotalos bien 😉')

async def robar(message, game):
  author = message.author
  mention = message.mentions[0]

  cooldown = datetime.timedelta(seconds=30)
  current_time = datetime.datetime.now()
  last_time_used = datetime.datetime.strptime(game.rob.get(author.id, '1970-01-01 00:00:00'), '%Y-%m-%d %H:%M:%S')

  if current_time - last_time_used < cooldown:
    remaining_time = cooldown - (current_time - last_time_used)
    await message.channel.send(embed=discord.Embed(title='Error', description=f"No puedes usar el comando nuevamente durante {remaining_time.seconds:.1f} segundos."))
    return

  game.rob[author.id] = current_time.strftime('%Y-%m-%d %H:%M:%S')

  balance = game.get_balance(mention.id)

  wallet = balance['wallet']
  
  porcentaje = random.randint(10, 30)

  robado = round(int(wallet) * (porcentaje / 100))

  if wallet <= 0:
    await message.channel.send(embed=discord.Embed(title='Failed!', description='No puedes robar a alguien con menos de 0 monedas en la cartera!', color=discord.Color.red()))
    return 0
  
  game.add_money(author.id, robado, 'wallet')
  game.remove_money(mention.id, robado, 'wallet')

  await message.channel.send(embed=discord.Embed(title='Robado!', description=f'Has robado {robado} monedas a {mention}!', color=discord.Color.green()))


async def intercambiar(message, game):
  author = message.author
  mention = message.mentions[0]
  soldado_id = int(message.content.split(' ')[1])
  cantidad = int(message.content.split(' ')[2])

  if obtener_rol_usuario(author) == obtener_rol_usuario(mention):
    ejercitoA = game.show_user_ejercito(author.id)
    ejercitoM = game.show_user_ejercito(mention.id)
    
    esta = False
    for soldado in ejercitoA:
      if soldado['id'] == soldado_id and soldado['cantidad'] >= cantidad:
        if soldado['cantidad'] == cantidad:
          ejercitoA.remove(soldado)
        else:
          soldado['cantidad'] -= cantidad

        for soldadoM in ejercitoM:
          if soldadoM['id'] == soldado_id:
            soldadoM['cantidad'] += cantidad
            esta = True
            break
        
        if esta is False:
          nuevo_soldado = soldado.copy()
          nuevo_soldado['cantidad'] = cantidad
          ejercitoM.append(nuevo_soldado)
        
        nombre = soldado['nombre']
        
        await message.channel.send(embed=discord.Embed(title='Traslado', description=f'El traslado de {cantidad} {nombre} a la base del usuario {mention}, ha sido efectuado correctamente!', color=discord.Color.green()))
  else:
    await message.channel.send(embed=discord.Embed(title='Failed!', description='No se puede trasladar soldados a un usuario de un equipo diferente al tuyo!', color=discord.Color.red()))

async def añadir_redada(message, game):
  author = message.author
  id_soldado = int(message.content.split(' ')[1])
  cantidad = int(message.content.split(' ')[2])

  ejercito = game.show_user_ejercito(author.id)
  esta = False
  for soldado in ejercito:
    if soldado['id'] == id_soldado and soldado['cantidad'] >= cantidad:
      nombre = soldado['nombre']
      nuevo_soldado = soldado.copy()
      nuevo_soldado['cantidad'] = cantidad
      soldado['cantidad'] -= cantidad

      if obtener_rol_usuario(author) == 'Empresario':
        nuevo_soldado['id'] = soldado['id'] * 2 + 1

      elif obtener_rol_usuario(author) == 'Dirigente':
        nuevo_soldado['id'] = soldado['id'] * 2

      if soldado['cantidad'] <= 0:
        ejercito.remove(soldado)
      
      for soldadoR in game.redada:
        if soldadoR['id'] == nuevo_soldado['id']:
          esta = True
          soldadoR['cantidad'] += cantidad
      
      if esta is False:
        game.redada.append(nuevo_soldado)
      
      await message.channel.send(embed=discord.Embed(title='Añadido!', description=f'Has añadido {cantidad} {nombre} al ejercito de redadas!', color=discord.Color.green()))
      return 0
  
  await message.channel.send(embed=discord.Embed(title='Failed!', description='El soldado o la cantidad establecida, no se encuentra en tu ejercito. Por favor, asegurate de que estás añadiendo una ID y cantidad correcta.', color=discord.Color.red()))

async def mostrar_redada(message, game):
  current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  embed = discord.Embed(title='Ejercito Redada', description='Este es el ejercito actual para las redadas del gobierno:', color=discord.Color.blue())
  for soldado in game.redada:
    id = soldado['id']
    nombre = soldado['nombre']
    cantidad = soldado['cantidad']
    ataque = soldado['ataque']
    defensa = soldado['defensa']
    vida = soldado['vida']
    embed.add_field(name=f'{nombre} - ID: {id}', value=f'Ataque: {ataque} ⚔️, Defensa: {defensa} 🛡️, Vida: {vida} ❤️ - Cantidad: {cantidad}', inline=False)

  embed.set_footer(text=f'{current_date}')

  await message.channel.send(embed=embed)

async def collect(message, game, bot):
  author = message.author
  construcciones = game.show_user_construcciones(author.id)
  if construcciones is None:
    await message.channel.send(embed = discord.Embed(title='Failed!', description='No tienes ninguna construcción!', color=discord.Color.blue()))
    return 0
  
  cooldown = datetime.timedelta(seconds=86400)
  current_time = datetime.datetime.now()
  last_time_used = datetime.datetime.strptime(game.recompensas.get(author.id, '1970-01-01 00:00:00'), '%Y-%m-%d %H:%M:%S')

  if current_time - last_time_used < cooldown:
    remaining_time = cooldown - (current_time - last_time_used)
    await message.channel.send(embed=discord.Embed(title='Error', description=f"No puedes usar el comando nuevamente durante {remaining_time.seconds:.1f} segundos."))
    return

  game.recompensas[author.id] = current_time.strftime('%Y-%m-%d %H:%M:%S')

  guild = bot.get_guild(game.g)
  for m in guild.members:
    if has_role(m, 'Alcalde'):
      alcalde = m
      break

  tiene1 = False
  tiene2 = False
  if construcciones:
    embed = discord.Embed(title='Ganancias', description=f'Aquí están tus ganancias del dia de hoy {author.mention}!', color=discord.Color.blue())
    for c in construcciones:
      construccion = c.copy()
      if 'ganancias' in construccion:
        ultimos_valores = {}
        if game.gremios:
          for g in game.gremios:
            if author.id in g['miembros']:
              for investigacion, desbloqueos in g['desbloqueados'].items():
                valores_no_vacios = [valor for valor in desbloqueos if valor != []]
                if valores_no_vacios:
                  ultimo_valor = valores_no_vacios[-1]
                  ultimos_valores[investigacion] = ultimo_valor
              break

        print(ultimos_valores)
        if 'Ganancias' in ultimos_valores:
          construccion['ganancias'] = c['ganancias'] * (1 + ultimos_valores['Ganancias'] / 100)

        if 'Mantenimiento' in ultimos_valores:
          construccion['mantenimiento'] = c['mantenimiento'] * (1 - ultimos_valores['Mantenimiento'] / 100)
        nombre = construccion['nombre']
              
        if 'impuestos' in construccion:
          if 'Sobornos' in ultimos_valores:
            construccion['impuestos'] = c['impuestos'] * (1 - ultimos_valores['Sobornos'] / 100)
                
          tiene1 = True
          amountAlcalde = construccion['ganancias'] * (construccion['impuestos'] / 100)
          game.add_money(alcalde.id, amountAlcalde, 'bank')
          await alcalde.send(f'El usuario {author} te ha dado su parte de las ganancias en {nombre}!')
              
        if 'mafia' in construccion:
          tiene2 = True
          amountMafia = construccion['ganancias'] * 0.2
          game.add_money(construccion['mafia'].id, amountMafia, 'bank')
          await construccion['mafia'].send(f'El usuario {author} te ha dado su parte de las ganancias en {nombre}!')
              
        if tiene1 and tiene2:
          amountUser = construccion['ganancias'] * (1 - 0.2 - (construccion['impuestos'] / 100))
          game.add_money(author.id, amountUser, 'bank')
          embed.add_field(name=f'{nombre}', value=f'Ganancias obtenidas: {amountUser}')

        elif tiene1:
          amountUser = construccion['ganancias'] * (1 - (construccion['impuestos'] / 100))
          game.add_money(author.id, amountUser, 'bank')
          embed.add_field(name=f'{nombre}', value=f'Ganancias obtenidas: {amountUser}')
              
        elif tiene2:
          amountUser = construccion['ganancias'] * 0.8
          game.add_money(author.id, amountUser, 'bank')
          embed.add_field(name=f'{nombre}', value=f'Ganancias obtenidas: {amountUser}')
              
        else:
          amountUser = construccion['ganancias']
          game.add_money(author.id, amountUser, 'bank')
          embed.add_field(name=f'{nombre}', value=f'Ganancias obtenidas: {amountUser}')
              
        if game.balances[author.id]['bank'] > 0:
          game.remove_money(author.id, construccion['mantenimiento'], 'bank')
        else:
          game.remove_money(author.id, construccion['mantenimiento'], 'wallet')

    embed.set_footer(text=f'{author}')
    await message.channel.send(embed=embed)

  game.save_data()

class Jackpot(discord.ui.View):
  def __init__(self, balance, author, espacio, dificultad, apuesta, m, multiplicador, x):
    super().__init__()
    self.balance = balance
    self.author = author
    self.dinero = 0
    self.espacio = espacio
    self.dificultad = dificultad
    self.mapa = []
    self.apuesta = apuesta
    self.acumulado = self.apuesta / multiplicador
    self.m = m
    self.x = x
    self.activado = False
  
  async def send(self, ctx):
    self.message = await ctx.channel.send('Comencemos!', view=self)
    vector = [0] * self.espacio
    numeros = []
    for i in range(self.x):
      while True:
        random_index = random.randint(0, self.espacio - 1)
        if random_index not in numeros:
          numeros.append(random_index)
        
          vector[random_index] = 1

          break

    data = vector

    for d in data:
      if d == 0:
        dic = {
          'emoji': '💸',
          'descubierto': False
        }
      elif d == 1:
        dic = {
          'emoji': '❌',
          'descubierto': False
        }

      self.mapa.append(dic)

    print(vector)

    await self.update_message(self.mapa)
  
  async def update_message(self, data):
    self.activado = False
    await self.message.edit(embed=self.create_embed(data), view=self)
  
  def create_embed(self, data):
    embed = discord.Embed(title='Jackpot!', description='Bienvenido al juego de Jackpot!\n Cada uno de los botones marca una posición del mapa, cada uno contiene un ❌ o un 💸.\n En caso de querer desmarcar una posición, selecciona el botón correspondiente.\n En caso de encontrar 💸, tu premio se va acumulando hasta que te rindas o encuentres todos los 💸.\n En caso de desmarcar la ❌, el juego acaba y no obtienes NINGUNA recompensa!!!\n Mucha suerte😎!!', color=discord.Color.blue())
    
    if self.author.avatar:
      embed.set_thumbnail(url=self.author.avatar.url)   

    self.dinero = 0
    for indice, m in enumerate(self.mapa):
      print(m)
      if m['descubierto'] is False:
        embed.add_field(name=f'PANEL {indice}', value='❓')
      else:
        emoji = m['emoji']
        embed.add_field(name=f'PANEL {indice}', value=f'{emoji}')
      
      if m['descubierto'] is False:
        button = Button(label=f'{indice}', style=discord.ButtonStyle.green, custom_id=f"{indice}")
        self.add_item(button)
        
      elif m['emoji'] == '💸':
        self.dinero += self.acumulado

    embed.add_field(name='__DINERO ACUMULADO__', value=f'{self.dinero} 💸!', inline=False)

    button = Button(label=f'Plantarse ✋', style=discord.ButtonStyle.danger, custom_id=f"87657827852785782727278")
    self.add_item(button)

    return embed
  
  async def interaction_check(self, interaction: discord.Interaction):
    if interaction.user == self.author and self.activado is False:
      self.activado = True
      await interaction.response.defer()
      selected_component = interaction.data.get('custom_id')
      print(selected_component)
      if selected_component:
        objeto_id = int(selected_component)
        if objeto_id <= self.espacio:
          for index, i in enumerate(self.mapa):
            if index == objeto_id:
              i['descubierto'] = True

              if i['emoji'] == '❌':
                self.clear_items()
                await self.message.edit(view=self)
                await self.m.channel.send(embed=discord.Embed(title='Game Over!', description='Has encontrado la ❌!! El valor acumulado ha sido de 0 monedas. 😔'), view=self)
                return 0
                

              if self.dinero == self.acumulado * (self.espacio - self.x):
                self.clear_items()
                self.balance['wallet'] += self.dinero
                self.message.edit(view=self)
                await self.m.channel.send(embed=discord.Embed(title='Ganaste!', description=f'Has recibido la cantidad de {self.dinero} 💸!!'), view=self)
                return 0
          print(self.mapa)
          self.clear_items()
          await self.update_message(self.mapa)
        
        else:
          self.clear_items()
          self.balance['wallet'] += self.dinero
          await self.message.edit(view=self)
          await self.m.channel.send(embed=discord.Embed(title='Ganaste!', description=f'Has recibido la cantidad de {self.dinero} 💸!!'))
          return 0


async def jackpot(message, game):
  author = message.author

  cooldown = datetime.timedelta(seconds=30)
  current_time = datetime.datetime.now()
  last_time_used = datetime.datetime.strptime(game.jackpot.get(author.id, '1970-01-01 00:00:00'), '%Y-%m-%d %H:%M:%S')

  if current_time - last_time_used < cooldown:
    remaining_time = cooldown - (current_time - last_time_used)
    await message.channel.send(embed=discord.Embed(title='Error', description=f"No puedes usar el comando nuevamente durante {remaining_time.seconds:.1f} segundos."))
    return

  game.jackpot[author.id] = current_time.strftime('%Y-%m-%d %H:%M:%S')

  balance = game.get_balance(author.id)

  dificultad = int(message.content.split(' ')[2])
  apuestas = message.content.split(' ')[1]
  
  if dificultad == 1:
    x = 2
    multiplicador = 6
    espacio = 15
  elif dificultad == 2:
    x = 1
    multiplicador = 4
    espacio = 10
  elif dificultad == 3:
    x = 1
    multiplicador = 1
    espacio = 5
  else:
    await message.channel.send(embed=discord.Embed(title='Error', description=f"No existe ese nivel de dificultad!"))
    return 

  if apuestas == 'all':
    apuestas = balance.get('wallet', 0)

  apuestas = int(apuestas)
  if apuestas <= 0:
    await message.channel.send(embed=discord.Embed(title='Failed!', description='No se pueden apostar menos de 0 monedas!!'), color=discord.Color.red())
    return 0

  if balance['wallet'] < apuestas:
    await message.channel.send(embed=discord.Embed(title='Failed!', description='No se pueden apostar dinero que no tienes!!'), color=discord.Color.red())
    return 0
  
  balance['wallet'] -= apuestas

  jackpot = Jackpot(balance, author, espacio, 1, apuestas, message, multiplicador, x)
  await jackpot.send(message)

class Caballos(discord.ui.View):
  def __init__(self, game):
    super().__init__()
    self.game = game
  
  async def send(self, ctx):
    self.message = await ctx.channel.send('Comencemos!', view=self)

    self.caballos = []
    for i in range(5):
      c = {
        'apuestas': random.randint(2, 8)
      }
      self.caballos.append(c)

      button = Button(label=f'Caballo {i}', style=discord.ButtonStyle.green, custom_id=f"{i}")
      self.add_item(button)

    await self.update_message(self.caballos)

    await asyncio.sleep(30)

    self.clear_items()
    await self.message.edit(view=self)
    await self.carreras(self.caballos)



  async def update_message(self, data):
    await self.message.edit(embed=self.create_embed(data), view=self)
  
  def create_embed(self, data):
    embed = discord.Embed(title='Carreras de caballos!', description='Apuesten por su caballo favorito! Tienen 30 segundos para apostar todos!')
    emojis = ["🐎", "🐴", "🦘", "🦄", "🐐"]
    for index, d in enumerate(data):
      apuestas = d['apuestas']
      emoji = emojis[index]
      embed.add_field(name=f'Caballo {index} {emoji}', value=f'Apuestas a: 1/{apuestas}', inline=False)

      if 'jugadores' in d:
        apuestas = 0
        guild = self.message.guild   
        for indice, apuesta in enumerate(d['jugadores']):
          jugador = guild.get_member(int(apuesta))
          cantidad = d['cantidad'][indice]
          apuestas += d['cantidad'][indice]
          embed.add_field(name=f'__{jugador}__', value=f'{cantidad}')
        embed.add_field(name='__APUESTAS__', value=f'{apuestas}', inline=False)

    embed.add_field(name='\u200b', value='Las apuestas se harán de 250 en 250 por cada vez que se aprete al botón.', inline=False)
    return embed
  
  async def interaction_check(self, interaction: discord.Interaction):
    if self.game.balances[interaction.user.id]['wallet'] >= 250:
      await interaction.response.defer()
      self.game.balances[interaction.user.id]['wallet'] -= 250
      selected_component = interaction.data.get('custom_id')
      boton_id = int(selected_component)
      for index, caballo in enumerate(self.caballos):
        if index == boton_id:
          if 'jugadores' not in caballo:
            caballo['jugadores'] = [interaction.user.id]
            caballo['cantidad'] = [250]
          else:
            esta = False
            for indice, jugador in enumerate(caballo['jugadores']):
              if jugador == interaction.user.id:
                esta = True
                caballo['cantidad'][indice] += 250

            if esta is False:
              caballo['jugadores'].append(interaction.user.id)
              caballo['cantidad'].append(250)

          await self.update_message(self.caballos)
    else:
      await interaction.response.send_message('No tienes 250 monedas en la cartera para apostar!', ephemeral=True)
    
  async def carreras(self, data):
    prob = []    
    for d in data:
      p = 1 / d['apuestas']
      prob.append(p)
      
    caballos = [1, 2, 3, 4, 5]
    emojis = ["🐎", "🐴", "🦘", "🦄", "🐐"]
    meta = 40 
    distancia = 40  
    ganadores = []
    while len(ganadores) < 5:
      numero = random.choices(caballos, weights=prob, k=1)[0]
      if numero not in ganadores:
        ganadores.append(numero)

    print(ganadores)

    embed = discord.Embed(title="Carreras de caballos", description="La carrera ha comenzado!")

    message = await self.message.channel.send(embed=embed, view=self)

    iteraciones = 0
    carrera = [0, 0, 0, 0, 0]
    while max(carrera) < meta:
            lines = []
            for i, caballo in enumerate(caballos):
                emoji = emojis[caballo - 1]
                position = min(carrera[i], distancia)
                progress = "🏁" if position >= distancia else "".join([" "] * position) + emoji + "".join([" "] * (distancia - position - 1))
                lines.append(f"Caballo {caballo}: {progress}")
                for posicion, g in enumerate(ganadores):
                  if g == caballo:
                    carrera[i] += 5 - round(posicion / 2) 
            race_text = "\n".join(lines)
            await message.edit(content=race_text, embed=None, view=self)
            await asyncio.sleep(2)
            iteraciones += 1


    for i, caballo in enumerate(caballos):
      if caballo == ganadores[0]:
        probabilidad = prob[i]
        if 'jugadores' in self.caballos[i]:
          for jugador, cantidad_apostada in zip(self.caballos[i]['jugadores'], self.caballos[i]['cantidad']):
            monto_ganado = cantidad_apostada * (1 / probabilidad)
            self.game.balances[jugador]['wallet'] += monto_ganado 
    
    resultado = [emojis[caballo - 1] for caballo in ganadores]
    resultado_text = " ".join(resultado)
    ganador = resultado[0]
    embed.description = f"Carrera terminada!\nGanadores: {resultado_text}"
    await message.edit(content=f"¡Carrera terminada!\nEl caballo ganador es: {ganador}", embed=embed, view=self)

async def carrera_caballos(message, game):
  author = message.author

  cooldown = datetime.timedelta(seconds=30)
  current_time = datetime.datetime.now()
  last_time_used = datetime.datetime.strptime(game.jackpot.get(author.id, '1970-01-01 00:00:00'), '%Y-%m-%d %H:%M:%S')

  if current_time - last_time_used < cooldown:
    remaining_time = cooldown - (current_time - last_time_used)
    await message.channel.send(embed=discord.Embed(title='Error', description=f"No puedes usar el comando nuevamente durante {remaining_time.seconds:.1f} segundos."))
    return

  game.jackpot[author.id] = current_time.strftime('%Y-%m-%d %H:%M:%S')


  caballos = Caballos(game)
  await caballos.send(message)

async def autoroles(game, message):
  guild = message.guild

  # Diccionario para almacenar la información relacionada
  datos_usuario = {
    'Mafia': {'puntuacion_max': 0, 'usuario': None, 'dinero_max': 0, 'usuario_dinero': None},
    'Buenos': {'puntuacion_max': 0, 'usuario': None, 'dinero_max': 0, 'usuario_dinero': None}
  }

  for miembro in guild.members:
    roles = ['El Padrino', 'Elon Musk', 'Jefe de Asalto', 'Jefe del Mercado']
    for r in roles:
      rol = discord.utils.get(miembro.roles, name=r)
      if rol is not None:
        await miembro.remove_roles(rol)

    rol = obtener_rol_usuario(miembro)

    if rol != 'Mafia' and rol is not None:
      rol = 'Buenos'

    if rol is not None:
      ejercito = game.show_user_ejercito(miembro.id)
            
      if ejercito:
        recuento = sum(soldado['cantidad'] * (4 if soldado['id'] > 3 else 1.5 if soldado['id'] == 1 else 2 if soldado['id'] == 2 else 3 if soldado['id'] == 3 else 1) for soldado in ejercito)

        if recuento > datos_usuario[rol]['puntuacion_max']:
          datos_usuario[rol]['puntuacion_max'] = recuento
          datos_usuario[rol]['usuario'] = miembro
                
      balance = game.get_balance(miembro.id)

      if balance:
        dinero_total = balance['wallet'] + balance['bank']

        if dinero_total > datos_usuario[rol]['dinero_max']:
          datos_usuario[rol]['dinero_max'] = dinero_total
          datos_usuario[rol]['usuario_dinero'] = miembro
  
  embed = discord.Embed(title='Autoroles Economía II', description='Se han cambiado los autoroles de esta partida!', color=discord.Color.blue())

  for rol, datos in datos_usuario.items():
    if rol == 'Buenos':
      if datos['usuario'] is not None:
        usuario = datos['usuario']
        puntuacion = datos['puntuacion_max']
        embed.add_field(name='Rol Jefe de Asalto', value=f"{usuario.mention} | puntuación: {puntuacion}", inline=False)

        rol = discord.utils.get(guild.roles, name='Jefe de Asalto')
        await usuario.add_roles(rol)
      else:
        embed.add_field(name='Rol Jefe de Asalto', value='No hay usuario por ahora...', inline=False)
      
      if datos['usuario_dinero'] is not None:
        usuario = datos['usuario_dinero']
        puntuacion = datos['dinero_max']
        embed.add_field(name='Rol Elon Musk', value=f"{usuario.mention} | puntuación: {puntuacion}", inline=False)

        rol = discord.utils.get(guild.roles, name='Elon Musk')
        await usuario.add_roles(rol)
      else:
        embed.add_field(name='Rol Elon Musk', value='No hay usuario por ahora...', inline=False)
    else:
      if datos['usuario'] is not None:
        usuario = datos['usuario']
        puntuacion = datos['puntuacion_max']
        embed.add_field(name='Rol El Padrino', value=f"{usuario.mention} | puntuación: {puntuacion}", inline=False)

        rol = discord.utils.get(guild.roles, name='El Padrino')
        await usuario.add_roles(rol)
      else:
        embed.add_field(name='Rol El Padrino', value='No hay usuario por ahora...', inline=False)
      
      if datos['usuario_dinero'] is not None:
        usuario = datos['usuario_dinero']
        puntuacion = datos['dinero_max']
        embed.add_field(name='Rol Jefe del Mercado', value=f"{usuario.mention} | puntuación: {puntuacion}", inline=False)

        rol = discord.utils.get(guild.roles, name='Jefe del Mercado')
        await usuario.add_roles(rol)
      else:
        embed.add_field(name='Rol Jefe del Mercado', value='No hay usuario por ahora...', inline=False)
  
  await message.channel.send(embed=embed)


class Ruleta:
  def __init__(self, game, bot):
    super().__init__()
    self.bot = bot
    self.game = game
    self.apuestas_grupo = {'par': [], 'impar': [], 'docena1': [], 'docena2': [], 'docena3': []}
    self.apuestas_numero = [[] for _ in range(37)]

  async def send(self, ctx):
    self.message = await ctx.channel.send('Comencemos!')
    
    await self.update_message()

    for i in range(20):
      try:
        await self.bot.wait_for('message', check = self.on_message, timeout=2.0)
        await self.update_message()


      except asyncio.TimeoutError:
        await self.update_message()
        continue
      else:
        break

    await self.ruleta()

  async def ruleta(self):
    # Lista de números para simular la ruleta
    numeros = list(range(1, 37))

    embed = discord.Embed(title='¡Ruleta en marcha!', description='Girando...', color=0xFF0000)
    await self.message.edit(embed=embed)
   
    for _ in range(10): 
        numero_actual = random.choice(numeros)  
        numeros.remove(numero_actual)  
        embed.description = f'Número actual: **{numero_actual}**'
        await self.message.edit(embed=embed)
        await asyncio.sleep(1) 

    resultado = random.choice(numeros)
    embed.description = f'Resultado final: **{resultado}**'
    embed.color = 0x00FF00  

    ## pares o impares
    if resultado % 2 == 0:
      if self.apuestas_grupo['par'] != []:
        for jugadores in self.apuestas_grupo['par']:
          jugador = jugadores['jugador']
          apuesta = jugadores['apuesta'] * 2
          balance = self.game.get_balance(jugador.id)
          balance['wallet'] += apuesta

          embed.add_field(name=f'{jugador}', value=f'Ha ganado {apuesta} 💸!')

    else:
      if self.apuestas_grupo['impar'] != []:
        for jugadores in self.apuestas_grupo['impar']:
          jugador = jugadores['jugador']
          apuesta = jugadores['apuesta'] * 2
          balance = self.game.get_balance(jugador.id)
          balance['wallet'] += apuesta

          embed.add_field(name=f'{jugador}', value=f'Ha ganado {apuesta} 💸!')

    ## docenas
    if resultado > 0 and resultado <= 12:
      if self.apuestas_grupo['docena1'] != []:
        for jugadores in self.apuestas_grupo['docena1']:
          jugador = jugadores['jugador']
          apuesta = jugadores['apuesta'] * 3
          balance = self.game.get_balance(jugador.id)
          balance['wallet'] += apuesta

          embed.add_field(name=f'{jugador}', value=f'Ha ganado {apuesta} 💸!')

    elif resultado > 12 and resultado <= 24:
      if self.apuestas_grupo['docena2'] != []:
        for jugadores in self.apuestas_grupo['docena2']:
          jugador = jugadores['jugador']
          apuesta = jugadores['apuesta'] * 3
          balance = self.game.get_balance(jugador.id)
          balance['wallet'] += apuesta

          embed.add_field(name=f'{jugador}', value=f'Ha ganado {apuesta} 💸!')

    elif resultado > 24 and resultado <= 36:
      if self.apuestas_grupo['docena3']  != []:
        for jugadores in self.apuestas_grupo['docena3']:
          jugador = jugadores['jugador']
          apuesta = jugadores['apuesta'] * 3
          balance = self.game.get_balance(jugador.id)
          balance['wallet'] += apuesta

          embed.add_field(name=f'{jugador}', value=f'Ha ganado {apuesta} 💸!')
    
    ## numero
    if self.apuestas_numero[resultado] != []:
      for jugadores in self.apuestas_numero[resultado]:
        jugador = jugadores['jugador']
        apuesta = jugadores['apuesta'] * 36
        balance = self.game.get_balance(jugador.id)
        balance['wallet'] += apuesta

        embed.add_field(name=f'{jugador}', value=f'Ha ganado {apuesta} 💸!')
    
    await self.message.edit(embed=embed)
      

  def create_embed(self):
    embed = discord.Embed(title='__LA RULETA__', description='Bienvenido a la ruleta de la fortuna!\nDeberás apostar para poder participar, tienes tres formas de apostar:\n\n**1 - Por número:** Escribe un numero del **0 al 36** para apostar a ese número | Apuesta acertada => 37 x Apostado\n**2 - Por par o impar:** Puedes apostar a que saldrá un número par o impar | Apuesta acertada => 2 x Apostado\n**3 - Docena:** Puedes apostar a que saldrá un número entre una docena (docena 1: 1-12, docena 2: 13-24, docena 3: 25-36) | Apuesta acertada => 3 x Apostado\n\nTenéis 30 segundos para apostar todo lo necesario\nMucha suerte!!🍀', color=discord.Color.blue())
    embed.set_thumbnail(url='https://cdn-icons-png.flaticon.com/512/2006/2006249.png')

    embed.add_field(name='__PARA APOSTAR__', value='**COMANDO:** +bet {numero/(par/impar)/(docena1/docena2/docena3)} {apuesta}', inline=False)
    embed.add_field(name='__EJEMPLOS__', value='**Apuesta 130 al numero 5:** 5 130\n**Apuesta 500 a impar:** impar 500\n**Apuesta 200 a la docena2:** docena2 200', inline=False)

    for clave, valor in self.apuestas_grupo.items():
      if valor != []:
        for elemento in valor:
          jugador = elemento['jugador']
          apuesta = elemento['apuesta']
          embed.add_field(name=f'__{clave}__', value=f'**{jugador.mention}** - {apuesta}')
    
    for i in range(len(self.apuestas_numero)):
      for elemento in self.apuestas_numero[i]:
        if 'jugador' in elemento:
          jugador = elemento['jugador']
          apuesta = elemento['apuesta']
          embed.add_field(name=f'__NUMERO: {i}__', value=f'**{jugador.mention}** - {apuesta}')

    return embed

  async def update_message(self):
    await self.message.edit(embed=self.create_embed())

  def on_message(self, message):
    if message.content == '+bet' or message.content.startswith('+bet '):
      miembro = message.author
      tipo = message.content.split(' ')[1]
      apuesta = int(message.content.split(' ')[2])

      balance = self.game.get_balance(miembro.id)
      if apuesta <= balance['wallet']:
        if tipo.lower() in ['par', 'impar', 'docena1', 'docena2', 'docena3']:
          tipo = tipo.lower()
          if not any(apuesta['jugador'] == miembro for apuesta in self.apuestas_grupo[tipo]):
            balance['wallet'] -= apuesta
            self.apuestas_grupo[tipo].append({'jugador': miembro, 'apuesta': apuesta})
          else:
            for apuesta_actual in self.apuestas_grupo[tipo]:
              if apuesta_actual['jugador'] == miembro:
                balance['wallet'] -= apuesta
                apuesta_actual['apuesta'] += apuesta
                break
        else:
          try:
            numero = int(tipo)
          except ValueError:
            return
          
          if 0 <= numero <= 36:
            if not any(apuesta['jugador'] == miembro for apuesta in self.apuestas_numero[numero]):
              balance['wallet'] -= apuesta
              self.apuestas_numero[numero].append({'jugador': miembro, 'apuesta': apuesta})
            else:
              for apuesta_actual in self.apuestas_numero[numero]:
                if apuesta_actual['jugador'] == miembro:
                  balance['wallet'] -= apuesta
                  apuesta_actual['apuesta'] += apuesta
                  break       

async def ruleta(game, message, bot):
  author = message.author

  cooldown = datetime.timedelta(seconds=30)
  current_time = datetime.datetime.now()
  last_time_used = datetime.datetime.strptime(game.jackpot.get(author.id, '1970-01-01 00:00:00'), '%Y-%m-%d %H:%M:%S')

  if current_time - last_time_used < cooldown:
    remaining_time = cooldown - (current_time - last_time_used)
    await message.channel.send(embed=discord.Embed(title='Error', description=f"No puedes usar el comando nuevamente durante {remaining_time.seconds:.1f} segundos."))
    return

  game.jackpot[author.id] = current_time.strftime('%Y-%m-%d %H:%M:%S')

  ruleta = Ruleta(game, bot)

  await ruleta.send(message)

class PiedraPapelTijeras(discord.ui.View):
  def __init__(self, game, apuesta, message):
    super().__init__()
    self.game = game
    self.apuesta = apuesta
    self.author = message.author
    self.contrincante = None
    self.activado = False
    self.selecciones = ['nada', 'nada']
    self.empates = 0

  async def send(self, ctx):
    self.message = await ctx.channel.send('Comencemos!')
    await self.update_message()

  async def update_message(self):
    await self.message.edit(embed=self.create_embed(), view=self)

  def create_embed(self):
    embed = discord.Embed(title='Piedra, Papel o Tijeras', description=f'Bienvenido al clásico Piedra, Papel o Tijeras, {self.author.mention}!\n\nHas apostado {self.apuesta} 💸\n\nInvita a tu contrincante!', color=discord.Color.gold())

    if self.contrincante is not None:
      piedra = Button(label='Piedra', style=discord.ButtonStyle.green, custom_id='Piedra')
      papel = Button(label='Papel', style=discord.ButtonStyle.green, custom_id='Papel')
      tijera = Button(label='Tijera', style=discord.ButtonStyle.green, custom_id='Tijera')
      self.add_item(piedra)
      self.add_item(papel)
      self.add_item(tijera)
      embed.add_field(name='Contrincante:', value=f'{self.contrincante.mention}', inline=False)

      embed.add_field(name='\u200b', value='Empieza la partida! Tenéis 10 segundos para elegir piedra, papel o tijera!', inline=False)
    else:
      buttonU = Button(label='Únete!', style=discord.ButtonStyle.green, custom_id='0')
      buttonC = Button(label='Cancelar', style=discord.ButtonStyle.red, custom_id='1')
      self.add_item(buttonU)
      self.add_item(buttonC)
      
      embed.add_field(name='Contrincante', value='Aún no hay contrincante, esperando...', inline=False)

    embed.set_thumbnail(url= 'https://cdn-icons-png.flaticon.com/512/6831/6831874.png')

    return embed

  async def interaction_check(self, interaction: discord.Interaction):
    await interaction.response.defer()
    selected_component = interaction.data.get('custom_id')
    print(selected_component)
    if interaction.user != self.author and selected_component == '0':
      self.activado = True
      balance = self.game.get_balance(interaction.user.id)

      if self.apuesta <= balance['wallet']:
        balance['wallet'] -= self.apuesta

        self.contrincante = interaction.user

        self.clear_items()
        await self.message.edit(view=self)

        await self.update_message()
        
        self.activado = False

        await asyncio.sleep(10)

        await self.final()
    
    elif interaction.user == self.author and selected_component == '1':
      self.activado = True
      self.clear_items()
      await self.message.edit(view=self)
      balance = self.game.get_balance(self.author.id)

      balance['wallet'] += self.apuesta

      self.activado = False
    
    elif (interaction.user == self.author or interaction.user == self.contrincante) and self.activado is False and selected_component != '0' and selected_component != '1':

      await interaction.followup.send(f'Has escogido {selected_component}!',ephemeral=True)
      self.activado = True

      if interaction.user == self.author:
        self.selecciones[0] = selected_component
      else:
        self.selecciones[1] = selected_component

      self.activado = False

  async def final(self):
    if self.selecciones[1] == 'nada' or self.selecciones[0] == 'nada':
      balance = self.game.get_balance(self.author.id)
      balance['wallet'] += self.apuesta

      balance = self.game.get_balance(self.contrincante.id)
      balance['wallet'] += self.apuesta

      self.clear_items()
      await self.message.edit(view=self)
    else:
      embed = discord.Embed(title='Resultado', description=f'**{self.author.mention}**: {self.selecciones[0]}\n**{self.contrincante.mention}**: {self.selecciones[1]}', color=discord.Color.gold())
      embed.set_thumbnail(url = 'https://cdn-icons-png.flaticon.com/512/6831/6831874.png')

      apuesta = self.apuesta * 2

      if self.selecciones[0] == self.selecciones[1]:
        self.empates += 1

        embed.add_field(name='Empate!', value=f'Lleváis {self.empates} empates. Tenéis otros 10 segundos para elegir piedra, papel o tijera!', inline=False)
        await self.message.edit(embed=embed, view=self)

        if self.empates == 3:
          embed.add_field(name='Anulado!', value='Partida anulada por 3 empates!')

          balance = self.game.get_balance(self.author.id)
          balance['wallet'] += self.apuesta

          balance = self.game.get_balance(self.contrincante.id)
          balance['wallet'] += self.apuesta
          
          self.clear_items()
          await self.message.edit(embed=embed, view=self)

          return
        else:
          self.selecciones = ['nada', 'nada']

          await asyncio.sleep(10)

          await self.final()
      
      elif self.selecciones[0] == 'Piedra':
        if self.selecciones[1] == 'Tijera':
          balance = self.game.get_balance(self.author.id)
          balance['wallet'] += apuesta
          embed.add_field(name='GANADOR!', value=f'{self.author.mention} ha ganado {apuesta} 💸!')
        else:
          balance = self.game.get_balance(self.contrincante.id)
          balance['wallet'] += apuesta
          embed.add_field(name='GANADOR!', value=f'{self.contrincante.mention} ha ganado {apuesta} 💸!')
        
        self.clear_items()
        await self.message.edit(embed=embed, view=self)
      elif self.selecciones[0] == 'Tijera':
        if self.selecciones[1] == 'Piedra':
          balance = self.game.get_balance(self.contrincante.id)
          balance['wallet'] += apuesta
          embed.add_field(name='GANADOR!', value=f'{self.contrincante.mention} ha ganado {apuesta} 💸!')
        else:
          balance = self.game.get_balance(self.author.id)
          balance['wallet'] += apuesta
          embed.add_field(name='GANADOR!', value=f'{self.author.mention} ha ganado {apuesta} 💸!')
        
        self.clear_items()
        await self.message.edit(embed=embed, view=self)
      else:
        if self.selecciones[1] == 'Piedra':
          balance = self.game.get_balance(self.author.id)
          balance['wallet'] += apuesta
          embed.add_field(name='GANADOR!', value=f'{self.author.mention} ha ganado {apuesta} 💸!')
        else:
          balance = self.game.get_balance(self.contrincante.id)
          balance['wallet'] += apuesta
          embed.add_field(name='GANADOR!', value=f'{self.contrincante.mention} ha ganado {apuesta} 💸!')
        
        self.clear_items()
        await self.message.edit(embed=embed, view=self)

async def ppt(game, message):
  author = message.author

  apuesta = int(message.content.split(' ')[1])

  cooldown = datetime.timedelta(seconds=30)
  current_time = datetime.datetime.now()
  last_time_used = datetime.datetime.strptime(game.jackpot.get(author.id, '1970-01-01 00:00:00'), '%Y-%m-%d %H:%M:%S')

  if current_time - last_time_used < cooldown:
    remaining_time = cooldown - (current_time - last_time_used)
    await message.channel.send(embed=discord.Embed(title='Error', description=f"No puedes usar el comando nuevamente durante {remaining_time.seconds:.1f} segundos."))
    return

  game.jackpot[author.id] = current_time.strftime('%Y-%m-%d %H:%M:%S')

  balance = game.get_balance(author.id)

  if balance['wallet'] >= apuesta:
    balance['wallet'] -= apuesta

    ppt = PiedraPapelTijeras(game, apuesta, message)

    await ppt.send(message)
  else:
    await message.channel.send(embed=discord.Embed(title='Error', description=f"No tienes esa cantidad de dinero!", color=discord.Color.red()))


async def actualizar_indices(message, game):
  guild = message.guild

  for member in guild.members:
    ejercito = game.show_user_ejercito(member.id)
    construcciones = game.show_user_construcciones(member.id)

    rol = obtener_rol_usuario(member)

    if rol != 'Alcalde' and rol:
      for caballeria in game.soldados[rol]:
        if ejercito:
          for soldado in ejercito:
            if soldado['nombre'] == caballeria['nombre']:
              soldado['id'] = caballeria['id']
        
        if construcciones:
          for construccion in construcciones:
            if 'defensa' in construccion and construccion['defensa'] != []:
              for defensa in construccion['defensa']:
                print(defensa)
                if defensa['nombre'] == caballeria['nombre']:
                  defensa['id'] = caballeria['id']

      
      






