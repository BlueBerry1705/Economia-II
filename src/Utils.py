import discord
import pickle
import random

def has_role(member, role_name):
    role = discord.utils.get(member.roles, name=role_name)
    return role is not None

def obtener_rol_usuario(usuario):
    if discord.utils.get(usuario.roles, name='Mafia'):
        return 'Mafia'
    elif discord.utils.get(usuario.roles, name='Empresario'):
        return 'Empresario'
    elif discord.utils.get(usuario.roles, name='Dirigente'):
        return 'Dirigente'
    elif discord.utils.get(usuario.roles, name='Alcalde'):
        return 'Alcalde'
    else:
        return None
    
class Ajedrez:
    def __init__(self):
        self.puntuaciones = {}

    def añadir_puntos(self, jugador, puntos):
        if jugador in self.puntuaciones:
            self.puntuaciones[jugador] += puntos
        else:
            self.puntuaciones[jugador] = puntos

    def quitar_puntos(self, jugador, puntos):
        if jugador in self.puntuaciones:
            self.puntuaciones[jugador] -= puntos
            if self.puntuaciones[jugador] < 0:
                self.puntuaciones[jugador] = 0

    def obtener_puntuacion_jugador(self, jugador):
        return self.puntuaciones.get(jugador, 0)
    
    def top_puntuaciones(self):
        sorted_puntuaciones = sorted(self.puntuaciones.items(), key=lambda x: x[1], reverse=True)

        top_10 = sorted_puntuaciones[:10]

        return top_10
    
    def save_data(self):
        data = {
        'puntos': self.puntuaciones
        }
        with open('ajedrez.pickle', 'wb') as file:
            pickle.dump(data, file)

    def load_data(self):
        try:
            with open('ajedrez.pickle', 'rb') as file:
                data = pickle.load(file)
                self.puntuaciones = data.get('puntos', {})
        except FileNotFoundError:
            self.puntuaciones = {}

async def mostrar_puntuacion(ajedrez, message):
    member = message.author
    if len(message.mentions) > 0:
        member = message.mentions[0]

    puntuacion = ajedrez.obtener_puntuacion_jugador(member.id)

    embed = discord.Embed(title=f'Puntuaje de {member.display_name}',
                        color=discord.Color.blue())
    if member.avatar:
        embed.set_thumbnail(url=member.avatar.url)
    embed.add_field(name='Puntuación',
                    value=f'{puntuacion} puntos',
                    inline=False)


    await message.channel.send(embed=embed)

async def top_ajedrez(ajedrez, message):
    balances = ajedrez.top_puntuaciones()

    embed = discord.Embed(title='Top Ajedrez', color=discord.Color.blue())

    for i, (user_id, puntos) in enumerate(balances):
        user = message.guild.get_member(user_id)
        username = user.display_name
        embed.add_field(name=f'{i + 1}. {username}', value=f'Puntuación: {puntos}', inline=False)

    await message.channel.send(embed=embed)

async def gestionar_puntos(ajedrez, message):
    if len(message.mentions) == 0 or len(message.mentions) == 1:
        await message.channel.send(
        embed=discord.Embed(title='Failed',
                            value='❌ Debes mencionar a un usuario.',
                            color=discord.Color.red()))
        return

    ganador = message.mentions[0]
    perdedor = message.mentions[1]

    puntuacion_ganador = ajedrez.obtener_puntuacion_jugador(ganador.id)
    puntuacion_perdedor = ajedrez.obtener_puntuacion_jugador(perdedor.id)

    diferencia = abs(puntuacion_ganador - puntuacion_perdedor)

    if diferencia >= 1000:
        puntuacion = random.randint(300, 350)
        ajedrez.añadir_puntos(ganador.id, puntuacion)
        ajedrez.quitar_puntos(perdedor.id, puntuacion)
    elif diferencia >= 500:
        puntuacion = random.randint(200, 250)
        ajedrez.añadir_puntos(ganador.id, puntuacion)
        ajedrez.quitar_puntos(perdedor.id, puntuacion)
    elif diferencia >= 200:
        puntuacion = random.randint(100, 150)
        ajedrez.añadir_puntos(ganador.id, puntuacion)
        ajedrez.quitar_puntos(perdedor.id, puntuacion)
    elif diferencia >= 100:
        puntuacion = random.randint(50, 75)
        ajedrez.añadir_puntos(ganador.id, puntuacion)
        ajedrez.quitar_puntos(perdedor.id, puntuacion)
    else:
        puntuacion = random.randint(15, 30)
        ajedrez.añadir_puntos(ganador.id, puntuacion)
        ajedrez.quitar_puntos(perdedor.id, puntuacion)

    embed = discord.Embed(
      title='Gestionar Partida',
      description=f'Se han añadido {puntuacion} puntos a {ganador.mention} y se han quitado {puntuacion} puntos a {perdedor.mention}!',
      color=discord.Color.green())
    await message.channel.send(embed=embed)

    