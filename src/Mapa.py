from PIL import Image, ImageDraw
import discord
import io
import pickle
import os
import datetime
import math
import asyncio

from Commands import *
from Utils import has_role, obtener_rol_usuario
from discord.ui import Button, View
from discord.ext import commands


g = 696380553515106380

map_size = 500

# Crear una matriz para representar el mapa
map_data = [[(255, 255, 255)] * map_size for _ in range(map_size)]
map_objects = [[None] * map_size for _ in range(map_size)]
map_original = [[(255, 255, 255)] * map_size for _ in range(map_size)]

async def GenerarMapa():
  
  square_size = 300
  border_width = 30

  square_x1 = (map_size - square_size) // 2
  square_y1 = (map_size - square_size) // 2
  square_x2 = square_x1 + square_size
  square_y2 = square_y1 + square_size

  
  

  for x in range(square_x1, square_x2):
    for y in range(square_y1, square_y2):
      map_data[x][y] = (128, 128, 128)
    
   
  for x in range(map_size):
    for y in range(map_size):
      if not (square_x1 <= x < square_x2 and square_y1 <= y < square_y2):
        map_data[x][y] = (0, 128, 0)

  for x in range(square_x1 - border_width, square_x2 + border_width):
    for y in range(square_y1 - border_width, square_y2 + border_width):
      if not (square_x1 <= x < square_x2 and square_y1 <= y < square_y2):
        map_data[x][y] = (51, 102, 153)

  center_x = (square_x1 + square_x2) // 2
  center_y = (square_y1 + square_y2) // 2

  for x in range(center_x - 10, center_x + 10):
    for y in range(square_y1 - 30, square_y2 + 30):
      map_data[x][y] = (178, 178, 178)

  for y in range(center_y - 10, center_y + 10):
    for x in range(square_x1 - 30, square_x2 + 30):
      map_data[x][y] = (178, 178, 178)

  for x in range(map_size):
    for y in range(map_size):
      if x % 10 == 0 or y % 10 == 0:
        map_data[x][y] = (0, 0, 0)

  center_x = map_size // 2
  center_y = map_size // 2
  structure_size = 60

  for x in range(center_x - structure_size // 2, center_x + structure_size // 2):
    for y in range(center_y - structure_size // 2, center_y + structure_size // 2):
      map_data[x][y] = (60, 60, 60)

  map_image = Image.new('RGB', (map_size, map_size))

  for x in range(map_size):
    for y in range(map_size):
      map_image.putpixel((x, y), map_data[x][y])
    
  for x in range(map_size):
    for y in range(map_size):
      map_original[x][y] = map_data[x][y]

  map_image.save('map.png')

async def mapa_final(message):
  usuario = message.author
  CargarMapa()
  map_image = Image.new('RGB', (map_size, map_size))
  if has_role(usuario, 'Mafia') is False:
    objeto = None
    usuario = None

    for x in range(map_size): 
      for y in range(map_size):  
        if (map_objects[x][y] and not objeto and not usuario) or (not map_objects[x][y] and objeto and usuario):
          map_image.putpixel((x, y), (0, 0, 0))
        elif map_objects[x][y] and objeto and objeto['id'] != map_objects[x][y]['objeto']['id']:
          map_image.putpixel((x, y), (0, 0, 0))
        elif map_data[x][y] == (207, 75, 33):
          map_image.putpixel((x, y), map_original[x][y])
        else:
          map_image.putpixel((x, y), map_data[x][y])

        if map_objects[x][y]:
          if x < map_size - 1 and map_objects[x + 1][y]:
            objeto = map_objects[x + 1][y]['objeto']
            usuario = map_objects[x + 1][y]['usuario']
          elif y < map_size - 1 and map_objects[x][y + 1]:
            objeto = map_objects[x][y + 1]['objeto']
            usuario = map_objects[x][y + 1]['usuario']
          else:
            objeto = None
            usuario = None
        else:
          objeto = None
          usuario = None

    map_image.save('noMafia.png')
    await message.channel.send(file=discord.File('noMafia.png'))

  else:
    objeto = None
    usuario = None
    for x in range(map_size):
      for y in range(map_size):
        if (map_objects[x][y] and not objeto and not usuario) or (not map_objects[x][y] and objeto and usuario):
          map_image.putpixel((x, y), (0, 0, 0))
        elif map_objects[x][y] and objeto and objeto['id'] != map_objects[x][y]['objeto']['id']:
          map_image.putpixel((x, y), (0, 0, 0))

        map_image.putpixel((x, y), map_data[x][y])

        if map_objects[x][y]:
          if x < map_size - 1 and map_objects[x + 1][y]:
            objeto = map_objects[x + 1][y]['objeto']
            usuario = map_objects[x + 1][y]['usuario']
          elif y < map_size - 1 and map_objects[x][y + 1]:
            objeto = map_objects[x][y + 1]['objeto']
            usuario = map_objects[x][y + 1]['usuario']
          else:
            objeto = None
            usuario = None
        else:
          objeto = None
          usuario = None
    
    map_image.save('map.png')
    await message.channel.send(file=discord.File('map.png'))


class ViewAlcalde(discord.ui.View):
  def __init__(self, message, alcalde, draw, usuario, color, map_objects, x, y, inventario_alcalde, construcciones_alcalde, map_data, map_image, inventario_usuario, construcciones_usuario, game, objeto):
    super().__init__()
    self.message = message
    self.alcalde = alcalde
    self.draw = draw
    self.usuario = usuario
    self.color = color
    self.map_objects = map_objects
    self.x = x
    self.y = y
    self.inventario_alcalde = inventario_alcalde
    self.construcciones_alcalde = construcciones_alcalde
    self.map_data = map_data
    self.map_image = map_image
    self.inventario_usuario = inventario_usuario
    self.construcciones_usuario = construcciones_usuario
    self.game = game
    self.objeto = objeto    
  
  @discord.ui.button(label="Aceptar", style=discord.ButtonStyle.green, custom_id='aceptar')
  async def aceptar_button(self, interaction: discord.Interaction, button: discord.ui.Button):
    if interaction.user.id == self.alcalde.id:
      self.game.solicitud.remove(self.usuario.id)
      esta_mapa = False
      aplicado = False
      for item in self.inventario_usuario:
        if item['id'] == self.objeto['id']:
          espacio = item['espacio']
          nombre = item['nombre']

          if self.construcciones_usuario is not None:
            id = len(self.construcciones_usuario) + 1
          else:
            id = 1
          
          objeto_aux = item.copy()
          objeto_aux['id'] = id
          objeto_aux['cantidad'] = 1
          if 'defensa' in item:
            objeto_aux['defensa'] = item['defensa'].copy()        

      if espacio == 1:
        if self.construcciones_alcalde:
          for construccion in self.construcciones_alcalde:
            if construccion['nombre'] == 'Casa' and 'asignado' not in construccion:
              esta_mapa = True
              aplicado= True
              construccion['asignado'] = objeto_aux
              break

        if esta_mapa is False:
          for anchuraX in range(10):
            for anchuraY in range(10):
              if self.map_data[self.x + anchuraX + 11][self.y + anchuraY + 1] != (128, 128, 128) and self.map_data[self.x + anchuraX + 11][self.y + anchuraY + 1] != (0, 0, 0):
                await interaction.response.send_message('No se puede asignar la casa a la derecha de la construcción!', ephemeral=True)
                return 0     
              
          if self.inventario_alcalde:      
            for casa in self.inventario_alcalde:
              if casa['nombre'] == 'Casa':
                aplicado = True
                casa_aux = casa.copy()
                casa_aux['asignado'] = objeto_aux.copy()
                espacio_casa = casa_aux['espacio']
                if self.construcciones_alcalde:
                  casa_aux['id'] = len(self.construcciones_alcalde) + 1
                else:
                  casa_aux['id'] = 1

                casa_aux['cantidad'] = 1
                for anchuraX in range(int(math.sqrt(espacio_casa)) * 10):
                  for anchuraY in range(int(math.sqrt(espacio_casa)) * 10):
                    self.draw.rectangle([(self.x + 10, self.y), (self.x + anchuraX + 10, self.y + anchuraY)], fill=(214, 214, 57))

                    self.map_data[self.x + anchuraX + 10][self.y + anchuraY] = (214, 214, 57)
                    self.map_objects[self.x + anchuraX + 10][self.y + anchuraY] = {'usuario': int(self.usuario.id), 'objeto': casa_aux}

                if self.construcciones_alcalde:    
                  self.construcciones_alcalde.append(casa_aux)
                else:
                  self.game.construcciones[self.alcalde.id] = [casa_aux]

                self.map_image.save('map.png')
                GuardarMapa()

                if casa['cantidad'] > 1:
                  casa['cantidad'] -= 1
                else:
                  self.inventario_alcalde.remove(casa)
  
                await self.alcalde.send(f'Se ha construido una casa al lado de {nombre}!') 

            if aplicado is False:
              self.clear_items()
              await interaction.response.edit_message(view=self)
              await interaction.followup.send('No tienes casas!', ephemeral=True)
              await self.message.channel.send(embed=discord.Embed(title='Rechazado!', description=f'{self.usuario.mention}, el alcalde ha rechazado la construcción de {nombre}, no tiene casas!', color=discord.Color.red()))
          else:
            self.clear_items()
            await interaction.response.edit_message(view=self)
            await interaction.followup.send('No tienes casas!', ephemeral=True)
            await self.message.channel.send(embed=discord.Embed(title='Rechazado!', description=f'{self.usuario.mention}, el alcalde ha rechazado la construcción de {nombre}, no tiene casas!', color=discord.Color.red()))
             

      if aplicado or espacio > 1:      
        objeto_aux['impuestos'] = 20
        for anchuraX in range(int(math.sqrt(espacio)) * 10):
          for anchuraY in range(int(math.sqrt(espacio)) * 10):
            self.draw.rectangle([(self.x, self.y), (self.x + anchuraX, self.y + anchuraY)], fill=self.color)
              
            self.map_data[self.x + anchuraX][self.y + anchuraY] = self.color
            self.map_objects[self.x + anchuraX][self.y + anchuraY] = {'usuario': int(self.usuario.id), 'objeto': objeto_aux}

        if self.construcciones_usuario is not None:
          self.construcciones_usuario.append(objeto_aux)
        else:
          self.game.construcciones[self.usuario.id] = [objeto_aux]
                
        if self.objeto['cantidad'] > 1:
          self.objeto['cantidad'] -= 1
        else:
          self.inventario_usuario.remove(self.objeto)

        self.map_image.save('map.png')
        GuardarMapa()
        self.clear_items()
        
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(f'Has aceptado la construcción de {nombre} en la ciudad!', ephemeral=True)
        await self.message.channel.send(embed=discord.Embed(title='Aceptado!', description=f'{self.usuario.mention}, el alcalde ha aceptado la construcción de {nombre}!', color=discord.Color.green()))

  @discord.ui.button(label="Rechazar", style=discord.ButtonStyle.red, custom_id="rechazar")
  async def rechazar_button(self, interaction: discord.Interaction, button: discord.ui.Button):
    if interaction.user.id == self.alcalde.id:
      nombre = self.objeto['nombre']

      self.game.solicitud.remove(self.usuario.id)

      self.clear_items()
      await interaction.response.edit_message(view=self)
      await interaction.followup.send("Has rechazado la construcción.", ephemeral=True)
      await self.message.channel.send(embed=discord.Embed(title='Rechazado!', description=f'{self.usuario.mention}, el alcalde ha rechazado la construcción de {nombre}!', color=discord.Color.red()))
  
async def DibujarMapa(message, game, x, y, color, objeto_id, usuario, bot):
  CargarMapa()
  es_ciudad = False
  guild = bot.get_guild(g)
  inventario_usuario = game.show_user_items(usuario.id)
  construcciones_usuario = game.show_user_construcciones(usuario.id)
  for o in inventario_usuario:
    if o['id'] == objeto_id:
      objeto = o
      nombre = o['nombre'] 
      espacio = o['espacio']

  if x % 10 == 0 and y % 10 == 0:
    for anchuraX in range(0, int(math.sqrt(espacio)) * 10, 5):
        for anchuraY in range(0, int(math.sqrt(espacio)) * 10, 5):
          indexX = x + anchuraX + 1
          indexY = y + anchuraY + 1
            
          if indexX >= len(map_data) or indexY >= len(map_data[indexX]):
            game.solicitud.remove(usuario.id)
            await message.channel.send(embed=discord.Embed(title='Failed!', description='Estás fuera de los límites del mapa.'))
            return False
          
          if map_data[x + anchuraX + 1][y + anchuraY + 1] != (0, 128, 0) and map_data[x + anchuraX + 1][y + anchuraY + 1] != (128, 128, 128):
            game.solicitud.remove(usuario.id)
            await message.channel.send(embed=discord.Embed(title='Failed!', description='No puedes añadir el edificio en el agua, en los caminos o encima de otros edificios!'))
            return False
          if map_data[x + anchuraX + 1][y + anchuraY + 1] == (128, 128, 128):
            es_ciudad = True

    for member in guild.members:
      if has_role(member, 'Alcalde'):
        alcalde = member
        break
    
    if has_role(usuario, 'Mafia') and es_ciudad and (nombre != 'Casa de usura' or nombre != 'Plantación pequeña'):
      game.solicitud.remove(usuario.id)
      await message.channel.send(embed=discord.Embed(title='Failed!', description='Solo puedes construir Casas de usura y/o Plantaciones pequeñas en la ciudad!', color=discord.Color.red()))
      return False
    
    if has_role(usuario, 'Mafia') and es_ciudad is False and nombre == 'Casa de usura':
      game.solicitud.remove(usuario.id)
      await message.channel.send(embed=discord.Embed(title='Failed!', description='Solo puedes construir Casas de usura en la ciudad!', color=discord.Color.red()))  
      return False
    
    for o in inventario_usuario:
        if o['id'] == objeto_id:
          espacio = int(o['espacio'])
          nombre = o['nombre']
          if 'max_construccion' in o:
            total = 0
            if construcciones_usuario:
              for construccion in construcciones_usuario:
                if construccion['nombre'] == o['nombre']:
                  total += 1
                    
            
            if o['max_construccion'] < total + 1:
              game.solicitud.remove(usuario.id)
              embed = discord.Embed(title='Failed!', description=f'Ya has construido el máximo de {nombre}!!!', color=discord.Color.red())
              await message.channel.send(embed=embed)
              return 0 
    
    if obtener_rol_usuario(usuario) != 'Mafia' and es_ciudad is False:
      game.solicitud.remove(usuario.id)
      await message.channel.send(embed=discord.Embed(title='Failed!', description='Solo puedes construir en la ciudad!!', color=discord.Color.red()))
      return False

    map_image = Image.open('map.png')
    draw = ImageDraw.Draw(map_image)

    nombre = objeto['nombre']
    if es_ciudad and has_role(usuario, 'Empresario') and nombre != 'Casa de usura':
      

      inventario_alcalde = game.show_user_items(alcalde.id)
      construcciones_alcalde = game.show_user_construcciones(alcalde.id)

      await message.channel.send(embed=discord.Embed(title='Petición enviada!', description=f'Has mandado una petición de construcción de {nombre} al alcalde. En breves te respondera!'))
      await alcalde.send(embed=discord.Embed(title='Alcalde!', description=f'El usuario {usuario} quiere construir {nombre} en la posicion {x} , {y} de la ciudad con un espacio de {espacio} casillas.\n Aceptas su construcción?', color=discord.Color.green()), 
                        view=ViewAlcalde(message, alcalde, draw, usuario, color, map_objects, x, y, inventario_alcalde, construcciones_alcalde, map_data, map_image, inventario_usuario, construcciones_usuario, game, objeto))
      

      return False
    else:
      for o in inventario_usuario:
        if o['id'] == objeto_id:
          if construcciones_usuario is not None:
            id = len(construcciones_usuario) + 1
          else:
            id = 1
          
          objeto_aux = o.copy()
          objeto_aux['id'] = id
          objeto_aux['cantidad'] = 1
          if 'defensa' in o:
            objeto_aux['defensa'] = o['defensa'].copy()
          if construcciones_usuario is not None:
            construcciones_usuario.append(objeto_aux)
          else:
            game.construcciones[usuario.id] = [objeto_aux]
          

          if o['cantidad'] > 1:
            o['cantidad'] -= 1
          else:
            inventario_usuario.remove(o)

            if inventario_usuario == []:
              inventario_usuario = None
          
          break

      for anchuraX in range(int(math.sqrt(espacio)) * 10):
        for anchuraY in range(int(math.sqrt(espacio)) * 10):
          draw.rectangle([(x, y), (x + anchuraX, y + anchuraY)], fill=color)
          map_data[x + anchuraX][y + anchuraY] = color
          map_objects[x + anchuraX][y + anchuraY] = {'usuario': int(usuario.id), 'objeto': objeto_aux}



    map_image.save('map.png')
    GuardarMapa()

    game.solicitud.remove(usuario.id)

    await message.channel.send(embed=discord.Embed(title='Construido!', description=f'Se ha construido {nombre} en {x},{y}'))
    return True
  else:
    game.solicitud.remove(usuario.id)
    await message.channel.send(embed=discord.Embed(title='Failed!', description='Solo se admiten posiciones de 10 en 10!'))
    return False

def GuardarMapa():
  with open('map_data.pkl', 'wb') as file:
    data = {
      'map_data': map_data,
      'map_objects': map_objects,
      'map_original': map_original
    }
    pickle.dump(data, file)


def CargarMapa():
  global map_data, map_objects, map_original
  try:
    with open('map_data.pkl', 'rb') as file:
      loaded_data = pickle.load(file)
    map_data = loaded_data['map_data']
    map_objects = loaded_data['map_objects']
    map_original = loaded_data['map_original']

  except FileNotFoundError:
    map_data = [[(255, 255, 255)] * map_size for _ in range(map_size)]
    map_objects = [[None] * map_size for _ in range(map_size)]
    map_original = [[(255, 255, 255)] * map_size for _ in range(map_size)]

  print(map_data)

async def MostrarMapa(message):
    if os.path.isfile('map_data.pkl'):
        CargarMapa()
    else:
        await GenerarMapa()
        GuardarMapa()

    await mapa_final(message)

async def construccion_mapa(message):
  usuario = message.mentions[0]
  objeto_id = int(message.content.split(' ')[1])

  if (obtener_rol_usuario(usuario) == obtener_rol_usuario(message.author) and has_role(usuario, 'Mafia') is False) or usuario == message.author:
    CargarMapa()
    if obtener_rol_usuario(message.author) == 'Mafia':
      map_image = Image.open('map.png')
      draw = ImageDraw.Draw(map_image)
    else:
      map_image = Image.open('noMafia.png')
      draw = ImageDraw.Draw(map_image)
    
    for x in range(len(map_objects)):
      for y in range(len(map_objects[x])):
        if map_objects[x][y] is not None and map_objects[x][y]['usuario'] == usuario.id and map_objects[x][y]['objeto']['id'] == objeto_id:
          draw.rectangle([(x,y), (x), (y)], outline=(87, 35, 100))

    image_bytes = io.BytesIO()
    map_image.save(image_bytes, format='PNG')
    image_bytes.seek(0)
    if obtener_rol_usuario(message.author) == 'Mafia':
      await message.channel.send(file=discord.File(image_bytes, filename='map.png'))
    else:
      await message.channel.send(file=discord.File(image_bytes, filename='noMafia.png'))


async def Redada(message, bot, game):
  current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  tipos = {'normal': 9, 'grande': [[[100 , 100] , [240 , 240]] , [[260 , 100] , [390 , 260]] , [[100 , 260] , [230 , 390]] , [[260 , 260] , [390 , 390]]], 'territorial': [[[0 , 0], [500 , 70]] , [[0 , 70] , [70 , 430]] , [[0 , 430] , [500 , 500]] , [[430 , 70] , [500 , 430]]]}
  precio = {'normal': 15000, 'grande': 100000, 'territorial': 1000000}
  tipo = message.content.split(' ')[1]
  posX = int(message.content.split(' ')[2])
  posY = int(message.content.split(' ')[3])
  guild = bot.get_guild(g)
  author = message.author

  estado = game.combates.get(author.id, False)
  if estado == True:
    await message.channel.send(embed=discord.Embed(title='Failed!', description='Ya estas atacando a alguien!', color=discord.Color.red()))
    return 0
  
  game.combates[author.id] = True
  
  construcciones_redada = []
  if tipo == 'normal':
    cantidad = tipos['normal']
    if posX % 10 == 0 and posY % 10 == 0:
      if game.remove_money(author.id, precio[tipo], 'wallet') is False:
        game.combates[author.id] = False
        await message.channel.send(embed=discord.Embed(title='Failed!', description='No tienes suficiente dinero para la redada!', color=discord.Color.red()))
        return 0
      CargarMapa()
      map_image = Image.open('noMafia.png')
      draw = ImageDraw.Draw(map_image)
      for x in range(0, int(math.sqrt(cantidad)) * 10 + 10, 10):
        for y in range(0, int(math.sqrt(cantidad)) * 10 + 10, 10):
          draw.rectangle([(posX, posY), (posX + x, posY + y)], outline=(255, 0, 0))
          
      for anchuraX in range(int(math.sqrt(cantidad)) * 10):
        for anchuraY in range(int(math.sqrt(cantidad)) * 10):
          if map_objects[posX + anchuraX][posY + anchuraY] is not None and has_role(guild.get_member(int(map_objects[posX + anchuraX][posY + anchuraY]['usuario'])), 'Mafia'):
            draw.rectangle([(posX, posY), (posX + anchuraX, posY + anchuraY)], fill=(207, 75, 33))
            if map_objects[posX + anchuraX][posY + anchuraY] not in construcciones_redada and obtener_rol_usuario(guild.get_member(int(map_objects[posX + anchuraX][posY + anchuraY]['usuario']))) == 'Mafia':
              construcciones_redada.append(map_objects[posX + anchuraX][posY + anchuraY])

      image_bytes = io.BytesIO()
      map_image.save(image_bytes, format='PNG')
      image_bytes.seek(0)
      
      embed = discord.Embed(title='Redada', description=f'Se ha realizado una redada {tipo}.\n Se han encontrado las siguientes construcciones:', color=discord.Color.blue())
      for construccion in construcciones_redada:
        usuario = construccion['usuario']
        objeto = construccion['objeto']
        id = objeto['id']
        nombre = objeto['nombre']
        embed.add_field(name=f'{guild.get_member(int(usuario))}', value=f'ID: {id} - Nombre: {nombre}', inline=False)

              
      embed.set_footer(text=f'{current_date}')

      view = RedadaView(construcciones_redada, message, game, bot, tipo)
      
      await message.channel.send(embed=embed, file=discord.File(image_bytes, filename='map.png'), view=view)

  elif tipo == 'grande' or tipo == 'territorial':
    if posX % 10 == 0 and posY % 10 == 0:
      for sector in tipos[tipo]:
        if sector[0][0] <= posX and sector[0][1] <= posY and sector[1][0] >= posX and sector[1][1] >= posY:
          if game.remove_money(author.id, precio[tipo], 'wallet') is False:
            game.combates[author.id] = False
            await message.channel.send(embed=discord.Embed(title='Failed!', description='No tienes suficiente dinero para la redada!', color=discord.Color.red()))
            return 0
          
          CargarMapa()
          map_image = Image.open('noMafia.png')
          draw = ImageDraw.Draw(map_image)
          for x in range(sector[0][0], sector[1][0] + 10, 10):
            for y in range(sector[0][1], sector[1][1] + 10, 10):
              draw.rectangle([(sector[0][0], sector[0][1]), (x, y)], outline=(255, 0, 0))
          
          for anchuraX in range(sector[0][0], sector[1][0]):
            for anchuraY in range(sector[0][1], sector[1][1]):
              draw.rectangle([(sector[0][0], sector[0][1]), (x, y)], outline=(255, 0, 0))
              if map_objects[anchuraX][anchuraY] is not None and has_role(guild.get_member(int(map_objects[anchuraX][anchuraY]['usuario'])), 'Mafia'):
                draw.rectangle([(anchuraX, anchuraY), (anchuraX, anchuraY)], fill=(207, 75, 33))
                if map_objects[anchuraX][anchuraY] not in construcciones_redada and obtener_rol_usuario(guild.get_member(int(map_objects[anchuraX][anchuraY]['usuario']))) == 'Mafia':
                  construcciones_redada.append(map_objects[anchuraX][anchuraY])

          image_bytes = io.BytesIO()
          map_image.save(image_bytes, format='PNG')
          image_bytes.seek(0)
          
          embed = discord.Embed(title='Redada', description=f'Se ha realizado una redada {tipo}.\n Se han encontrado las siguientes construcciones:', color=discord.Color.blue())
          for construccion in construcciones_redada:
            usuario = construccion['usuario']
            objeto = construccion['objeto']
            id = objeto['id']
            nombre = objeto['nombre']
            embed.add_field(name=f'{guild.get_member(int(usuario))}', value=f'ID: {id} - Nombre: {nombre}', inline=False)

                  
          embed.set_footer(text=f'{current_date}')

          view = RedadaView(construcciones_redada, message, game, bot, tipo)
          
          await message.channel.send(embed=embed, file=discord.File(image_bytes, filename='map.png'), view=view)

class RedadaView(discord.ui.View):
    def __init__(self, construcciones_redada, message, game, bot, tipo):
        super().__init__()
        self.construcciones_redada = construcciones_redada
        self.message = message
        self.game = game
        self.bot = bot
        self.tipo = tipo
        self.construcciones = game.construcciones
        self.guild = bot.get_guild(g)
        self.redada = game.redada
        self.combates = game.combates

        for construccion in construcciones_redada:
            objeto = construccion['objeto']
            usuario_id = construccion['usuario']
            objeto_id = objeto['id']
            
            member = self.guild.get_member(usuario_id)

            button = Button(label=f'ID : {objeto_id} - {member}', style=discord.ButtonStyle.green, custom_id=f"{objeto['id']}|{usuario_id}")
            self.add_item(button)  
        
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

    async def interaction_check(self, interaction: discord.Interaction): 
        if interaction.user == self.message.author:
            selected_component = interaction.data.get('custom_id')
            if selected_component:
                objeto_id, usuario_id = selected_component.split("|")
                objeto_id = int(objeto_id)
                usuario_id = int(usuario_id)
                mention = self.guild.get_member(usuario_id)
                author = self.message.author   
                print(objeto_id, usuario_id)

                construccionesD = self.construcciones[int(usuario_id)]

                for construccion in construccionesD:
                  if construccion['id'] == objeto_id:
                    nombre = construccion['nombre']

                self.clear_items()
                await interaction.response.edit_message(view=self)
                
                if self.tipo == 'territorial':
                  embedD = discord.Embed(title='Atacando!', description=f'Hemos recibido un chivatazo! Van a atacar tu {nombre} - ID: {objeto_id}. Tienes 30 min para prepararte', color=discord.Color.gold())
                  embedR = discord.Embed(title='Atacando!', description='El ataque ha comenzado!! Tienes 30 min para prepararte!', color=discord.Color.gold())
                  mensajeD = await mention.send(embed=embedD)
                  mensajeR = await self.message.channel.send(embed=embedR)
                  await asyncio.sleep(1800) # 7200
                else:
                  embedD = discord.Embed(title='Atacando!', description=f'Hemos recibido un chivatazo! Van a atacar tu {nombre} - ID: {objeto_id}. Tienes 15 min para prepararte', color=discord.Color.gold())
                  embedR = discord.Embed(title='Atacando!', description='El ataque ha comenzado!! Tienes 15 min para prepararte!', color=discord.Color.gold())
                  mensajeD = await mention.send(embed=embedD)
                  mensajeR = await self.message.channel.send(embed=embedR)
                  await asyncio.sleep(900) # 3600
                

                soldados_perdidos_R = 0
                soldados_perdidos_D = 0
                
                EjercitoR_aux = self.redada.copy()

                for soldado in self.redada:
                  soldado['cantidad'] == 0

                if EjercitoR_aux is None:
                  self.combates[self.message.author.id] = False
                  self.game.remove_money(self.message.author.id, 10000, 'wallet')
                  await self.message.channel.send(embed=discord.Embed(title='Multa!', description='Como se te ocurre hacer una redada sin ejercito! \n El ayuntamiento te ha multado con 10000 monedas!', color=discord.Color.red()))
                  return 0

                capofamigliaD = 0
                nuevo_diccionario_D = []
                for i, objeto in enumerate(construccionesD):
                  if objeto['id'] == objeto_id:
                    nombre = objeto['nombre']
                    indice = i
                    if objeto['defensa']:
                      for defensa in objeto['defensa']:
                        if defensa['id'] > 3:
                          capofamigliaD += 1
                        nuevo_diccionario_D.append(defensa)
                
                EjercitoR_sorted = sorted(EjercitoR_aux, key=lambda x: x['id'], reverse=False)
                
                EjercitoD_sorted = []
                if nuevo_diccionario_D:
                  EjercitoD_sorted = sorted(nuevo_diccionario_D, key=lambda x: x['id'], reverse=False)

                cantidad_soldados_R = {}
                cantidad_soldados_D = {}

                for soldado in EjercitoR_sorted:
                  soldado_id = soldado['id']
                  cantidad = soldado.get('cantidad', 0)
                  cantidad_soldados_R[soldado_id] = cantidad_soldados_R.get(soldado_id, 0) + cantidad
                
                if EjercitoD_sorted:
                  for soldado in EjercitoD_sorted:
                    soldado_id = soldado['id']
                    cantidad = soldado.get('cantidad', 0)
                    cantidad_soldados_D[soldado_id] = cantidad_soldados_D.get(soldado_id, 0) + cantidad
                
                max_id_R = min(cantidad_soldados_R.keys())
                nivel_actual_R = max_id_R
                nivel_superior_R = -1
                nivel_actual_D = -1
                nivel_superior_D = -1
                
                for clave, valor in cantidad_soldados_R.items():
                  if max_id_R < clave:
                    nivel_superior_R = clave
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
                
                multiplicador_D = 1
                if has_role(mention, 'El Padrino'):
                  multiplicador_D = 3  

                perdidas_nivel_actual_R = 0
                perdidas_nivel_actual_D = 0
                aplicado = False

                print(EjercitoD_sorted)

                while nivel_actual_R >= 0 and nivel_actual_D >= 0:
                  TotalA = 0
                  TotalD = 0
                  tiene7 = False
                  tiene6 = False
                  tiene2 = False

                  for a in EjercitoR_sorted:
                    if a['id'] == 7:
                      TotalA += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_R.get(7, 0)
                      tiene7 = True
                    
                    if a['id'] == 6:
                      TotalA += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_R.get(0, 0)
                      tiene6 = True
                    
                    if a['id'] == 2:
                      TotalA += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_R.get(2, 0) 
                      tiene2 = True
                    
                  for a in EjercitoR_sorted:
                    ## ejercito empresarios
                    if a['id'] == 3:
                      if tiene7:
                        TotalA += ((a['ataque'] + 15) * 1.5 + (a['defensa'] + 20) * 1.5 + a['vida']) * cantidad_soldados_R.get(3, 0)
                      else:
                        TotalA += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_R.get(3, 0)
                    if a['id'] == 5:
                      if a['cantidad'] >= 10:
                        TotalA += (a['ataque'] * 1.5 + (a['defensa'] + 30) * 1.5 + a['vida']) * cantidad_soldados_R.get(5, 0)
                      else:
                        TotalA += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_R.get(5, 0)
                    if a['id'] == 1:
                      TotalA += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_R.get(1, 0)
                    
                    ## ejercito dirigentes
                    if a['id'] == 0:
                      if tiene6 and tiene2:
                        if a['cantidad'] <= 40:
                          TotalA += (a['ataque'] * 1.5 + (a['defensa'] + 15) * 1.5 + a['vida']) * cantidad_soldados_R.get(0, 0) * 2
                        else:
                          cantidad_restante = cantidad_soldados_R.get(0, 0) - 40
                          TotalA += (a['ataque'] * 1.5 + (a['defensa'] + 15) * 1.5 + a['vida']) * 40 * 2
                          TotalA += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_restante * 2
                      elif tiene2:
                        if a['cantidad'] <= 40:
                          TotalA += (a['ataque'] * 1.5 + (a['defensa'] + 15) * 1.5 + a['vida']) * cantidad_soldados_R.get(0, 0)
                        else:
                          cantidad_restante = cantidad_soldados_R.get(0, 0) - 40
                          TotalA += (a['ataque'] * 1.5 + (a['defensa'] + 15) * 1.5 + a['vida']) * 40
                          TotalA += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_restante
                      elif tiene6:
                        TotalA += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_R.get(0, 0) * 2
                      else:
                        TotalA += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_R.get(0, 0)

                    if a['id'] == 4:
                      TotalA += (a['ataque'] * 1.5 + a['defensa'] * 1.5 + a['vida']) * cantidad_soldados_R.get(4, 0)
                  

                  tiene0 = False
                  tiene1 = False
                  tienecapo = False
                  
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
                  
                  embedR = discord.Embed(title='Atacando!', description='El ataque ha comenzado!! No tienes mas tiempo para prepararte!', color=discord.Color.gold())
                  embedD = discord.Embed(title='Atacando!', description='El ataque ha comenzado!! No tienes mas tiempo para prepararte!', color=discord.Color.gold())
                  contenido_soldados_A = ""
                  contenido_soldados_D = ""
                  for soldado in EjercitoR_sorted:
                    id_soldado_A = soldado['id']
                    nombre_soldado_A = soldado['nombre']
                    cantidad_A = cantidad_soldados_R.get(id_soldado_A, 0)

                    contenido_soldados_A += f"ID: {id_soldado_A} | Nombre: {nombre_soldado_A} | Cantidad: {cantidad_A}\n"
                  
                  for soldado in EjercitoD_sorted:
                    id_soldado_D = soldado['id']
                    nombre_soldado_D = soldado['nombre']
                    cantidad_D = cantidad_soldados_D.get(id_soldado_D, 0)
                    
                    contenido_soldados_D += f"ID: {id_soldado_D} | Nombre: {nombre_soldado_D} | Cantidad: {cantidad_D}\n"

                  embedR.add_field(name='__Ejercito Redadas__', value=contenido_soldados_A + f"Fuerza total restante: {TotalA}", inline=False)
                  embedR.add_field(name='__Ejercito Enemigo__', value=contenido_soldados_D + f"Fuerza total restante: ??????", inline=False)
                  await mensajeR.edit(embed=embedR)

                  embedD.add_field(name=f'__Ejercito Mafia__', value=contenido_soldados_D + f"Fuerza total restante: {TotalD}", inline=False)
                  embedD.add_field(name='__Ejercito Redadas__', value=contenido_soldados_A + f"Fuerza total restante: ??????", inline=False)
                  try:
                    await mensajeD.edit(embed=embedD)
                  except Exception:
                    nivel_actual_D = -1

                  print('-------------')
                  print(porcentajeA)
                  
                  if aplicado is False:
                    total_principio_D = TotalD
                    total_principio_R = TotalA
                    aplicado = True
                  
                  if porcentajeA >= 90:
                    soldados_perdidos_R = 1
                    soldados_perdidos_D = 10
                    await asyncio.sleep(1)

                  elif porcentajeA >= 80:
                    soldados_perdidos_R = 1
                    soldados_perdidos_D = 5
                    await asyncio.sleep(2) #10

                  elif porcentajeA >= 70:
                    soldados_perdidos_R = 1
                    soldados_perdidos_D = 3
                    await asyncio.sleep(5) #100

                  elif porcentajeA >= 60:
                    soldados_perdidos_R = 1
                    soldados_perdidos_D = 2
                    await asyncio.sleep(10) #1000

                  elif porcentajeA >= 55:
                    soldados_perdidos_R = 1
                    soldados_perdidos_D = 1.5
                    await asyncio.sleep(15) #10000

                  elif porcentajeA >= 45:
                    soldados_perdidos_R = 1
                    soldados_perdidos_D = 1
                    await asyncio.sleep(20) #100000

                  elif porcentajeA >= 40:
                    soldados_perdidos_R = 1.5
                    soldados_perdidos_D = 1
                    await asyncio.sleep(15) #10000

                  elif porcentajeA >= 30:
                    soldados_perdidos_R = 2
                    soldados_perdidos_D = 1
                    await asyncio.sleep(10) #1000

                  elif porcentajeA >= 20:
                    soldados_perdidos_R = 3
                    soldados_perdidos_D = 1
                    await asyncio.sleep(5) #100

                  elif porcentajeA >= 10:
                    soldados_perdidos_R = 5
                    soldados_perdidos_D = 1
                    await asyncio.sleep(2) #10

                  else:
                    soldados_perdidos_R = 10
                    soldados_perdidos_D = 1
                    await asyncio.sleep(1)
                  
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
                    
                    print(nivel_actual_D, nivel_superior_D)

                    print(cantidad_soldados_A, cantidad_soldados_D)
                    return cantidad_soldados_A, cantidad_soldados_D, perdidas_nivel_actual_A, perdidas_nivel_actual_D, nivel_actual_A, nivel_superior_A, nivel_actual_D, nivel_superior_D


                  cantidad_soldados_R, cantidad_soldados_D, perdidas_nivel_actual_R, perdidas_nivel_actual_D, nivel_actual_R, nivel_superior_R, nivel_actual_D, nivel_superior_D = Perdidas_Soldados(cantidad_soldados_R, cantidad_soldados_D, soldados_perdidos_R, soldados_perdidos_D, perdidas_nivel_actual_R, nivel_actual_R, nivel_superior_R, perdidas_nivel_actual_D, nivel_actual_D, nivel_superior_D)

                for soldado1 in self.redada:
                  for soldado2 in EjercitoR_aux:
                    if soldado1['id'] == soldado2['id']:
                      soldado1['cantidad'] = soldado2['cantidad']
                
                EjercitoR = self.redada

                if construccionesD[indice]['defensa']:
                  fuerza_restanteA = TotalA / total_principio_R * 100
                  fuerza_restanteD = TotalD / total_principio_D * 100 
                else:
                  fuerza_restanteA = 100
                  fuerza_restanteD = 0
                soldados_eliminar = []
                
                if nivel_actual_D == -1:
                  for a, b in zip_longest(EjercitoR_sorted, EjercitoD_sorted):
                    for soldadoA, soldadoD in zip_longest(EjercitoR, construccionesD[indice]['defensa']):
                      if fuerza_restanteA >= 75:
                        if a and soldadoA and a['id'] == soldadoA['id']:
                          soldadoA['cantidad'] += a['cantidad']

                        if soldadoD:
                          soldadoD['cantidad'] = 0
                            
                      elif fuerza_restanteA >= 60:
                        if a and soldadoA and ((a['id'] == soldadoA['id'] == 0) or (a['id'] == soldadoA['id'] == 1) or (a['id'] == soldadoA['id'] == 2) or (a['id'] == soldadoA['id'] == 3)):
                          soldadoA['cantidad'] += round(a['cantidad'] - a['cantidad'] * 0.15)
                        if b and soldadoD and ((b['id'] == soldadoD['id'] == 1) or (b['id'] == soldadoD['id'] == 0)):
                          soldadoD['cantidad'] = round(soldadoD['cantidad'] - b['cantidad'] * 0.85)
                        if a and soldadoA and (a['id'] == soldadoA['id'] == 4 or a['id'] == soldadoA['id'] == 5):
                          soldadoA['cantidad'] += round(a['cantidad'] - a['cantidad'] * 0.075)
                        if b and soldadoD and b['id'] == soldadoD['id'] == 2:
                          soldadoD['cantidad'] = round(soldadoD['cantidad'] - b['cantidad'] * 0.425)
                        if a and soldadoA and (a['id'] == soldadoA['id'] == 6 or a['id'] == soldadoA['id'] == 7):
                          soldadoA['cantidad'] += round(a['cantidad'] - a['cantidad'] * 0.003)
                        if b and soldadoD and b['id'] == soldadoD['id'] == 3:
                          soldadoD['cantidad'] = round(soldadoD['cantidad'] - b['cantidad'] * 0.17)
                              
                      elif fuerza_restanteA >= 40:
                        if a and soldadoA and ((a['id'] == soldadoA['id'] == 0) or (a['id'] == soldadoA['id'] == 1) or (a['id'] == soldadoA['id'] == 2) or (a['id'] == soldadoA['id'] == 3)):
                          soldadoA['cantidad'] += round(a['cantidad'] - a['cantidad'] * 0.3)
                        if b and soldadoD and ((b['id'] == soldadoD['id'] == 1) or (b['id'] == soldadoD['id'] == 0)):
                          soldadoD['cantidad'] = round(soldadoD['cantidad'] - b['cantidad'] * 0.8)
                        if a and soldadoA and (a['id'] == soldadoA['id'] == 4 or a['id'] == soldadoA['id'] == 5):
                          soldadoA['cantidad'] += round(a['cantidad'] - a['cantidad'] * 0.15)
                        if b and soldadoD and b['id'] == soldadoD['id'] == 2:
                          soldadoD['cantidad'] = round(soldadoD['cantidad'] - b['cantidad'] * 0.4)
                        if a and soldadoA and (a['id'] == soldadoA['id'] == 6 or a['id'] == soldadoA['id'] == 7):
                          soldadoA['cantidad'] += round(a['cantidad'] - a['cantidad'] * 0.006)
                        if b and soldadoD and b['id'] == soldadoD['id'] == 3:  
                          soldadoD['cantidad'] = round(soldadoD['cantidad'] - b['cantidad'] * 0.16)
                        
                      elif fuerza_restanteA >= 25:
                        if a and soldadoA and ((a['id'] == soldadoA['id'] == 0) or (a['id'] == soldadoA['id'] == 1) or (a['id'] == soldadoA['id'] == 2) or (a['id'] == soldadoA['id'] == 3)):
                          soldadoA['cantidad'] += round(a['cantidad'] - a['cantidad'] * 0.5)
                        if b and soldadoD and ((b['id'] == soldadoD['id'] == 1) or (b['id'] == soldadoD['id'] == 0)):
                          soldadoD['cantidad'] = round(soldadoD['cantidad'] - b['cantidad'] * 0.7)
                        if a and soldadoA and (a['id'] == soldadoA['id'] == 4 or a['id'] == soldadoA['id'] == 5):
                          soldadoA['cantidad'] += round(a['cantidad'] - a['cantidad'] * 0.2)
                        if b and soldadoD and b['id'] == soldadoD['id'] == 2:
                          soldadoD['cantidad'] = round(soldadoD['cantidad'] - b['cantidad'] * 0.35)
                        if a and soldadoA and (a['id'] == soldadoA['id'] == 6 or a['id'] == soldadoA['id'] == 7):
                          soldadoA['cantidad'] += round(a['cantidad'] - a['cantidad'] * 0.1)
                        if b and soldadoD and b['id'] == soldadoD['id'] == 3:  
                          soldadoD['cantidad'] = round(soldadoD['cantidad'] - b['cantidad'] * 0.14)
                              
                      else:
                        if a and soldadoA and ((a['id'] == soldadoA['id'] == 0) or (a['id'] == soldadoA['id'] == 1) or (a['id'] == soldadoA['id'] == 2) or (a['id'] == soldadoA['id'] == 3)):
                          soldadoA['cantidad'] += round(a['cantidad'] - a['cantidad'] * 0.6)
                        if b and soldadoD and ((b['id'] == soldadoD['id'] == 1) or (b['id'] == soldadoD['id'] == 0)):
                          soldadoD['cantidad'] = round(soldadoD['cantidad'] - b['cantidad'] * 0.6)
                        if a and soldadoA and (a['id'] == soldadoA['id'] == 4 or a['id'] == soldadoA['id'] == 5):
                          soldadoA['cantidad'] += round(a['cantidad'] - a['cantidad'] * 0.3)
                        if b and soldadoD and b['id'] == soldadoD['id'] == 2:
                          soldadoD['cantidad'] = round(soldadoD['cantidad'] - b['cantidad'] * 0.3)
                        if a and soldadoA and (a['id'] == soldadoA['id'] == 6 or a['id'] == soldadoA['id'] == 7):
                          soldadoA['cantidad'] += round(a['cantidad'] - a['cantidad'] * 0.12)
                        if b and soldadoD and b['id'] == soldadoD['id'] == 3:
                          soldadoD['cantidad'] = round(soldadoD['cantidad'] - b['cantidad'] * 0.12)
                              
                      if soldadoD and int(soldadoD['cantidad']) <= 0:
                        construccionesD[indice]['defensa'].remove(soldadoD)
                      if soldadoA and int(soldadoA['cantidad']) <= 0:
                        EjercitoR.remove(soldadoA)   

                  for construccion in self.construcciones[int(usuario_id)]:
                    if construccion['id'] == int(objeto_id):
                      self.construcciones[int(usuario_id)].remove(construccion)
                  
                  for x in range(500):
                    for y in range(500):  
                      if self.map_objects[x][y] and self.map_objects[x][y]['usuario'] == int(usuario_id) and self.map_objects[x][y]['objeto']['id'] == int(objeto_id):
                        self.map_objects[x][y] = None
                        self.map_data[x][y] = self.map_original[x][y]    

                  self.GuardarMapa() 
                            
                  await mensajeR.edit(embed=discord.Embed(title='Victoria!', description=f'{author}, has ganado contra {mention}!😎', color=discord.Color.green()))
                  await mensajeD.edit(embed=discord.Embed(title='Derrota!', description=f'{mention}, has perdido contra {author}!😟', color=discord.Color.red()))
                  
                else:
                  for a, b in zip_longest(EjercitoR_sorted, EjercitoD_sorted):
                    for soldadoA, soldadoD in zip_longest(EjercitoR, construccionesD[indice]['defensa']):
                      if fuerza_restanteD >= 75:
                        if soldadoA['id'] > 3:
                          miembro = self.guild.get_member(int(soldadoA['id']))
                          self.game.eliminados.append(miembro)

                          miembro.send(embed=discord.Embed(title='Eliminado!', description='Has sido derrotado en batalla, por tanto, quedas eliminado para el resto de la partida 😟', color=discord.Color.red()))
                        
                        if soldadoA:
                          soldadoA['cantidad'] = 0     
                        
                      elif fuerza_restanteD >= 60:
                        if b and soldadoD and ((b['id'] == soldadoD['id'] == 1) or (b['id'] == soldadoD['id'] == 0)):
                          soldadoD['cantidad'] = round(soldadoD['cantidad'] - b['cantidad'] * 0.15)
                        if a and soldadoA and ((a['id'] == soldadoA['id'] == 0) or (a['id'] == soldadoA['id'] == 1) or (a['id'] == soldadoA['id'] == 2) or (a['id'] == soldadoA['id'] == 3)):
                          soldadoA['cantidad'] += round(a['cantidad'] - a['cantidad'] * 0.85)
                        if b and soldadoD and b['id'] == soldadoD['id'] == 2:
                          soldadoD['cantidad'] = round(soldadoD['cantidad'] - b['cantidad'] * 0.075)
                        if a and soldadoA and (a['id'] == soldadoA['id'] == 4 or a['id'] == soldadoA['id'] == 5):
                          soldadoA['cantidad'] += round(a['cantidad'] - a['cantidad'] * 0.425)
                        if b and soldadoD and b['id'] == soldadoD['id'] == 3:
                          soldadoD['cantidad'] = round(soldadoD['cantidad'] - b['cantidad'] * 0.003)
                        if a and soldadoA and (a['id'] == soldadoA['id'] == 6 or a['id'] == soldadoA['id'] == 7):
                          soldadoA['cantidad'] += round(a['cantidad'] - a['cantidad'] * 0.17)
                          
                      elif fuerza_restanteD >= 40:
                        if b and soldadoD and ((b['id'] == soldadoD['id'] == 1) or (b['id'] == soldadoD['id'] == 0)):
                          soldadoD['cantidad'] = round(soldadoD['cantidad'] - b['cantidad'] * 0.3)
                        if a and soldadoA and ((a['id'] == soldadoA['id'] == 0) or (a['id'] == soldadoA['id'] == 1) or (a['id'] == soldadoA['id'] == 2) or (a['id'] == soldadoA['id'] == 3)):
                          soldadoA['cantidad'] += round(a['cantidad'] - a['cantidad'] * 0.8)
                        if b and soldadoD and b['id'] == soldadoD['id'] == 2:
                          soldadoD['cantidad'] = round(soldadoD['cantidad'] - b['cantidad'] * 0.15)
                        if a and soldadoA and a['id'] == soldadoA['id'] == 1:
                          soldadoA['cantidad'] += round(a['cantidad'] - a['cantidad'] * 0.4)
                        if b and soldadoD and b['id'] == soldadoD['id'] == 3:
                          soldadoD['cantidad'] = round(soldadoD['cantidad'] - b['cantidad'] * 0.006)
                        if a and soldadoA and (a['id'] == soldadoA['id'] == 6 or a['id'] == soldadoA['id'] == 7):
                          soldadoA['cantidad'] += round(a['cantidad'] - a['cantidad'] * 0.16)
                          
                      elif fuerza_restanteD >= 25:
                        if b and soldadoD and ((b['id'] == soldadoD['id'] == 1) or (b['id'] == soldadoD['id'] == 0)):
                          soldadoD['cantidad'] = round(soldadoD['cantidad'] - b['cantidad'] * 0.5)
                        if a and soldadoA and ((a['id'] == soldadoA['id'] == 0) or (a['id'] == soldadoA['id'] == 1) or (a['id'] == soldadoA['id'] == 2) or (a['id'] == soldadoA['id'] == 3)):
                          soldadoA['cantidad'] += round(a['cantidad'] - a['cantidad'] * 0.7)
                        if b and soldadoD and b['id'] == soldadoD['id'] == 2:
                          soldadoD['cantidad'] = round(soldadoD['cantidad'] - b['cantidad'] * 0.25)
                        if a and soldadoA and (a['id'] == soldadoA['id'] == 4 or a['id'] == soldadoA['id'] == 5):
                          soldadoA['cantidad'] += round(a['cantidad'] - a['cantidad'] * 0.35)
                        if b and soldadoD and b['id'] == soldadoD['id'] == 3:
                          soldadoD['cantidad'] = round(soldadoD['cantidad'] - b['cantidad'] * 0.1)
                        if a and soldadoA and (a['id'] == soldadoA['id'] == 6 or a['id'] == soldadoA['id'] == 7):
                          soldadoA['cantidad'] += round(a['cantidad'] - a['cantidad'] * 0.14)
                          
                      else:
                        if b and soldadoD and ((b['id'] == soldadoD['id'] == 1) or (b['id'] == soldadoD['id'] == 0)):
                          soldadoD['cantidad'] = round(soldadoD['cantidad'] - b['cantidad'] * 0.6) 
                        if a and soldadoA and ((a['id'] == soldadoA['id'] == 0) or (a['id'] == soldadoA['id'] == 1) or (a['id'] == soldadoA['id'] == 2) or (a['id'] == soldadoA['id'] == 3)):
                          soldadoA['cantidad'] += round(a['cantidad'] - a['cantidad'] * 0.6) 
                        if b and soldadoD and b['id'] == soldadoD['id'] == 2:
                          soldadoD['cantidad'] = round(soldadoD['cantidad'] - b['cantidad'] * 0.3) 
                        if a and soldadoA and (a['id'] == soldadoA['id'] == 4 or a['id'] == soldadoA['id'] == 5):
                          soldadoA['cantidad'] += round(a['cantidad'] - a['cantidad'] * 0.3) 
                        if b and soldadoD and b['id'] == soldadoD['id'] == 3:
                          soldadoD['cantidad'] = round(soldadoD['cantidad'] - b['cantidad'] * 0.12)
                        if a and soldadoA and (a['id'] == soldadoA['id'] == 6 or a['id'] == soldadoA['id'] == 7):
                          soldadoA['cantidad'] += round(a['cantidad'] - a['cantidad'] * 0.12) 
                          
                      if soldadoD and int(soldadoD['cantidad']) <= 0:
                        construccionesD[indice]['defensa'].remove(soldadoD)
                      if soldadoA and int(soldadoA['cantidad']) <= 0:
                        EjercitoR.remove(soldadoA)  
                    
                  await mensajeR.edit(embed=discord.Embed(title='Derrota!', description=f'{author}, has perdido contra {mention}!😟', color=discord.Color.red()))
                  await mensajeD.edit(embed=discord.Embed(title='Victoria!', description=f'{mention}, has ganado contra {author}!😎', color=discord.Color.green()))
                  
                for soldado in soldados_eliminar:
                  if soldado in construccionesD[indice]['defensa']:
                    construccionesD[indice]['defensa'].remove(soldado)
                  if soldado in EjercitoR:
                    EjercitoR.remove(soldado)
                  if soldado['id'] > 3:
                    miembro = self.guild.get_member(int(soldado['id']))
                    self.game.eliminados.append(miembro)

                    miembro.send(embed=discord.Embed(title='Eliminado!', description='Has sido derrotado en batalla, por tanto, quedas eliminado para el resto de la partida 😟', color=discord.Color.red()))
          
            self.combates[self.message.author.id] = False      
        else:
          await interaction.response.send_message("No tienes permiso para seleccionar este objeto.", ephemeral=True)
        
          


    

