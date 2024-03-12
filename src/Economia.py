import pickle
from Utils import has_role
import datetime
import random


class Economia:
  def __init__(self):
    self.g = 696380553515106380
    self.carreras = {}
    self.rob = {}
    self.jackpot = {}
    self.recompensas = {}
    self.solicitud = []
    self.secuestros = {}
    self.eliminados = []
    self.last_used = {}
    self.combates = {}
    self.frases = {}
    self.balances = {}
    self.ejercito = {}
    self.redada = []
    self.items = {}
    self.construcciones = {}
    self.equipos = {}
    self.gremios = []
    self.tabla = {
      'Ganancias': {'id': 1, 'nombre': 'Dinero rápido', 'descripcion': 'Con esto ganarás más con los establecimientos a tu disposición', 'procentajes': [5, 10, 15, 20, 30], 'precio': [20000, 100000, 500000, 1000000, 2500000]},
      'Mantenimiento': {'id': 2, 'nombre': 'Refuerzos construcción', 'descripcion': 'Con esto reducirás los costos de mantenimiento de todos tus edificios', 'procentajes': [5, 10, 15, 30], 'precio': [50000, 150000, 450000, 1000000]},
      'Sobornos': {'id': 3, 'nombre': 'Sobornos gobierno', 'descripcion': 'El gobierno permitirá ciertos vacíos en las cuentas de algunos empresarios', 'procentajes': [5, 10, 15, 20, 30], 'precio': [100000, 200000, 400000, 750000, 1000000]},
      'Defensa': {'id': 4, 'nombre': 'Blindaje cinético', 'descripcion': 'Un blindaje futurista que hará verdaderos juggernauts a tus soldados', 'procentajes': [5, 15, 30, 40, 50], 'precio': [25000, 75000, 225000, 775000, 3000000]}  
    }
    self.soldados = {
      'Dirigente': [
        {'id': 3, 'nombre': 'Comisario general', 'precio': 10000, 'mantenimiento': 5500, 'ataque': 10, 'defensa': 150, 'vida': 100, 'max_persona': 3},
        {'id': 2, 'nombre': 'Comisario', 'precio': 30000, 'mantenimiento': 3000, 'ataque': 45, 'defensa': 40, 'vida': 100},
        {'id': 1, 'nombre': 'Inspector', 'precio': 1500, 'mantenimiento': 500, 'ataque': 45, 'defensa': 40, 'vida': 100},
        {'id': 0, 'nombre': 'Policia', 'precio': 500, 'mantenimiento': 150, 'ataque': 30, 'defensa': 25, 'vida': 100}
        ],
      'Empresario': [
        {'id': 3, 'nombre': 'Guardia de honor', 'precio': 1500, 'mantenimiento': 240, 'ataque': 65, 'defensa': 80, 'vida': 100},
        {'id': 2, 'nombre': 'Guardaespaldas', 'precio': 500, 'mantenimiento': 140, 'ataque': 40, 'defensa': 70, 'vida': 100},
        {'id': 1, 'nombre': 'Guardia', 'precio': 250, 'mantenimiento': 90, 'ataque': 35, 'defensa': 55, 'vida': 100},
        {'id': 0, 'nombre': 'Portero', 'precio': 150, 'mantenimiento': 50, 'ataque': 20, 'defensa': 50, 'vida': 100}
        ],
      'Mafia': [
        {'id': 3, 'nombre': 'Consiglieri', 'precio': 15000, 'mantenimiento': 1000, 'ataque': 150, 'defensa': 50, 'vida': 250, 'max_persona': 1},
        {'id': 2, 'nombre': 'Capodecina', 'precio': 5000, 'mantenimiento': 25, 'ataque': 90, 'defensa': 30, 'vida': 100}, 
        {'id': 1, 'nombre': 'Sgarristi', 'precio': 3000, 'mantenimiento': 15, 'ataque': 85, 'defensa': 25, 'vida': 100},
        {'id': 0, 'nombre': 'Piciotti', 'precio': 1000, 'mantenimiento': 15, 'ataque': 70, 'defensa': 15, 'vida': 100}]}
    
    self.tienda = {
      'Dirigente': [
        {'id': 0, 'nombre': 'Casa', 'precio': 1500, 'ganancias': 50, 'mantenimiento': 0, 'espacio': 1},
        {'id': 1, 'nombre': 'Estación policía pequeña', 'nivel': 2, 'precio': 30000, 'ganancias': 0, 'mantenimiento': 500, 'espacio': 4, 'poblacion': 20, 'defensa': [{'id': 0, 'nombre': 'Policia', 'precio': 500, 'mantenimiento': 150, 'ataque': 30, 'defensa': 25, 'vida': 100, 'cantidad': 75}]},
        {'id': 2, 'nombre': 'Estación policía mediana', 'nivel': 3, 'precio': 150000, 'ganancias': 0, 'mantenimiento': 1200, 'espacio': 9, 'poblacion': 125, 'max_total': 15, 'max_construccion': 10, 'defensa': [{'id': 0, 'nombre': 'Policia', 'precio': 500, 'mantenimiento': 150, 'ataque': 30, 'defensa': 25, 'vida': 100, 'cantidad': 500}]},
        {'id': 3, 'nombre': 'Estación policía grande', 'nivel': 4, 'precio': 1500000, 'ganancias': 0, 'mantenimiento': 4000, 'espacio': 25, 'poblacion': 500, 'max_total': 2, 'max_construccion': 2, 'defensa': [{'id': 0, 'nombre': 'Policia', 'precio': 500, 'mantenimiento': 150, 'ataque': 30, 'defensa': 25, 'vida': 100, 'cantidad': 10000}]},
        #{'id': 4, 'nombre': 'Centro comercial', 'precio': 1000000, 'ganancias': 0, 'mantenimiento': 17700, 'espacio': 36, 'max_persona': 3, 'max_construccion': 3,  'niveles': [{'nivel': 1, 'cantidad': 50}, {'nivel': 2, 'cantidad': 15}, {'nivel': 3, 'cantidad': 3}], 'requisitos': [{'nombre': 'Director', 'cantidad': 1}, {'nombre': 'Estación policía mediana', 'cantidad': 1}], 'defensa': [], 'contenido': [{'id': 2, 'nombre': 'Estación policía mediana', 'nivel': 2, 'precio': 150000, 'ganancias': 0, 'mantenimiento': 1200, 'espacio': 9, 'poblacion': 125, 'max_total': 15, 'max_construccion': 10, 'defensa': []}]},
        #{'id': 5, 'nombre': 'Gran centro Elías', 'precio': 10000000, 'ganancias': 0, 'mantenimiento': 17700, 'espacio': 64, 'max_persona': 1, 'max_total': 1, 'max_construccion': 1,  'niveles': [{'nivel': 1, 'cantidad': 200}, {'nivel': 2, 'cantidad': 50}, {'nivel': 3, 'cantidad': 10}, {'nivel': 4, 'cantidad': 3}], 'requisitos': [{'nombre': 'Director', 'cantidad': 1}, {'nombre': 'Estación policía mediana', 'cantidad': 1}], 'defensa': [], 'contenido': [{'id': 2, 'nombre': 'Estación policía mediana', 'nivel': 2, 'precio': 150000, 'ganancias': 0, 'mantenimiento': 1200, 'espacio': 9, 'poblacion': 125, 'defensa': []}]},
        #{'id': 6, 'nombre': 'Barracones', 'precio': 1000000, 'ganancias': 0, 'mantenimiento': 0, 'espacio': 150, 'poblacion': [{'nombre': 'soldado', 'cantidad': 1000}, {'nombre': 'Capitan', 'cantidad': 50}, {'nombre': 'Coronel', 'cantidad': 3}, {'nombre': 'General', 'cantidad': 1}], 'defensa': []},
        {'id': 4, 'nombre': 'Director', 'ganancias': 0, 'precio': 100000, 'mantenimiento': 15000},
        {'id': 5, 'nombre': 'Campaña de reclutamiento', 'precio': 1000000, 'ganancias': 50000, 'mantenimiento': 25000, 'espacio': 25, 'max_total': 4, 'defensa': [], 'requisitos': [{'nombre': 'Director', 'cantidad': 1}]}],
      'Empresario': [
        {'id': 0, 'nombre': 'Establecimiento de tacos Ricky', 'nivel': 1, 'precio': 10000, 'ganancias': 1200, 'mantenimiento': 500, 'espacio': 1, 'requisitos': [{'nombre': 'Empleado', 'cantidad': 10}], 'defensa': []},     
        {'id': 1, 'nombre': 'Restaurante humilde', 'nivel': 2, 'precio': 23000, 'ganancias': 2300, 'mantenimiento': 1150, 'espacio': 4, 'requisitos': [{'nombre': 'Empleado', 'cantidad': 20}, {'nombre': 'Gerente', 'cantidad': 1}], 'defensa': []},
        {'id': 2, 'nombre': 'Restaurante de lujo', 'nivel': 3, 'precio': 50000, 'ganancias': 6500, 'mantenimiento': 3550, 'espacio': 4, 'requisitos': [{'nombre': 'Empleado', 'cantidad': 30}, {'nombre': 'Gerente', 'cantidad': 3}, {'nombre': 'Administrador', 'cantidad': 1}], 'defensa': []},        
        {'id': 3, 'nombre': 'Casino', 'nivel': 3, 'precio': 60000, 'ganancias': 9000, 'mantenimiento': 3550, 'espacio': 9, 'max_persona': 1, 'requisitos': [{'nombre': 'Empleado', 'cantidad': 30}, {'nombre': 'Gerente', 'cantidad': 3}, {'nombre': 'Administrador', 'cantidad': 1}], 'defensa': []}, 
        {'id': 4, 'nombre': 'Gran casinocke', 'nivel': 4, 'precio': 1500000, 'ganancias': 220000, 'mantenimiento': 42150, 'espacio': 16, 'max_persona': 1, 'max_total': 3, 'requisitos': [{'nombre': 'Empleado', 'cantidad': 30}, {'nombre': 'Gerente', 'cantidad': 15}, {'nombre': 'Administrador', 'cantidad': 1}], 'defensa': []},
        {'id': 5, 'nombre': 'Banco', 'nivel': 3, 'precio': 65250, 'ganancias': 8000, 'mantenimiento': 3000, 'espacio': 9, 'requisitos': [{'nombre': 'Gerente', 'cantidad': 15}, {'nombre': 'Administrador', 'cantidad': 1}], 'defensa': []},
        {'id': 6, 'nombre': 'Gran Bluanco', 'nivel': 4, 'precio': 1300000, 'ganancias': 190500, 'mantenimiento': 45500, 'espacio': 16, 'max_persona': 1, 'max_total': 3, 'requisitos': [{'nombre': 'Gerente', 'cantidad': 10}, {'nombre': 'Administrador', 'cantidad': 10}], 'defensa': []},   
        {'id': 7, 'nombre': 'Makenkia de inversiones', 'nivel': 4, 'precio': 1000000, 'ganancias': 160000, 'mantenimiento': 42750, 'espacio': 16, 'max_persona': 1, 'max_total': 3, 'requisitos': [{'nombre': 'Gerente', 'cantidad': 5}, {'nombre': 'Administrador', 'cantidad': 5}], 'defensa': []},       
        {'id': 8, 'nombre': 'Carli`s shop', 'nivel': 1, 'precio': 1000, 'ganancias': 200, 'mantenimiento': 150, 'espacio': 1, 'requisitos': [{'nombre': 'Gerente', 'cantidad': 1}], 'defensa': []},
        {'id': 9, 'nombre': 'Supermercado express', 'nivel': 2, 'precio': 10000, 'ganancias': 1990, 'mantenimiento': 1530, 'espacio': 4, 'requisitos': [{'nombre': 'Empleado', 'cantidad': 3}, {'nombre': 'Gerente', 'cantidad': 5}, {'nombre': 'Administrador', 'cantidad': 1}], 'defensa': []},
        {'id': 10, 'nombre': 'Supermercado grande', 'nivel': 3, 'precio': 65000, 'ganancias': 10000, 'mantenimiento': 3800, 'espacio': 8, 'requisitos': [{'nombre': 'Empleado', 'cantidad': 10}, {'nombre': 'Gerente', 'cantidad': 10}, {'nombre': 'Administrador', 'cantidad': 1}], 'defensa': []},
        {'id': 11, 'nombre': 'Gran Dylancado', 'nivel': 4, 'precio': 1500000, 'ganancias': 200000, 'mantenimiento': 54500, 'espacio': 16, 'max_persona': 1, 'max_total': 3, 'requisitos': [{'nombre': 'Empleado', 'cantidad': 50}, {'nombre': 'Gerente', 'cantidad': 30}, {'nombre': 'Administrador', 'cantidad': 3}], 'defensa': []},
        {'id': 12, 'nombre': 'Empleado', 'precio': 250, 'ganancias': 0, 'mantenimiento': 30},
        {'id': 13, 'nombre': 'Gerente', 'precio': 750, 'ganancias': 0, 'mantenimiento': 50},
        {'id': 14, 'nombre': 'Administrador', 'precio': 3500, 'ganancias': 0, 'mantenimiento': 500}],
      'Mafia': [
        {'id': 0, 'nombre': 'Plantación pequeña', 'precio': 0, 'ganancias': 165, 'mantenimiento': 0, 'espacio': 1, 'requisitos': [{'nombre': 'Esclavo', 'cantidad': 10}, {'nombre': 'Piciotti', 'cantidad': 3}], 'defensa': [{'id': 0, 'nombre': 'Piciotti', 'ataque': 70, 'defensa': 15, 'vida': 100, 'cantidad': 3}]}, 
        {'id': 1, 'nombre': 'Plantación mediana', 'precio': 0, 'ganancias': 1500, 'mantenimiento': 0, 'espacio': 9, 'requisitos': [{'nombre': 'Esclavo', 'cantidad': 70}, {'nombre': 'Piciotti', 'cantidad': 15}, {'nombre': 'Capodecina', 'cantidad': 1}], 'defensa': [{'id': 0, 'nombre': 'Piciotti', 'ataque': 70, 'defensa': 15, 'vida': 100, 'cantidad': 15}, {'id': 1, 'nombre': 'Capodecina', 'ataque': 90, 'defensa': 30, 'vida': 100, 'cantidad': 1}]}, 
        {'id': 2, 'nombre': 'Plantación grande', 'precio': 0, 'ganancias': 4000, 'mantenimiento': 0, 'espacio': 25, 'requisitos': [{'nombre': 'Esclavo', 'cantidad': 200}, {'nombre': 'Sgarristi', 'cantidad': 30}, {'nombre': 'Capodecina', 'cantidad': 3}], 'defensa': [{'id': 1, 'nombre': 'Sgarristi', 'ataque': 70, 'defensa': 15, 'vida': 100, 'cantidad': 30}, {'id': 1, 'nombre': 'Capodecina', 'ataque': 90, 'defensa': 30, 'vida': 100, 'cantidad': 3}]}, 
        {'id': 3, 'nombre': 'Mini fábrica', 'precio': 10000, 'ganancias': 865, 'mantenimiento': 300, 'espacio': 1, 'requisitos': [{'nombre': 'Esclavo', 'cantidad': 15}, {'nombre': 'Piciotti', 'cantidad': 3}], 'defensa': [{'id': 0, 'nombre': 'Piciotti', 'ataque': 70, 'defensa': 15, 'vida': 100, 'cantidad': 3}]}, 
        {'id': 4, 'nombre': 'Fábrica mediana', 'precio': 50000, 'ganancias': 5900, 'mantenimiento': 500, 'espacio': 4, 'requisitos': [{'nombre': 'Esclavo', 'cantidad': 50}, {'nombre': 'Piciotti', 'cantidad': 15}, {'nombre': 'Capodecina', 'cantidad': 1}], 'defensa': [{'id': 0, 'nombre': 'Piciotti', 'ataque': 70, 'defensa': 15, 'vida': 100, 'cantidad': 15}, {'id': 1, 'nombre': 'Capodecina', 'ataque': 90, 'defensa': 30, 'vida': 100, 'cantidad': 1}]},
        {'id': 5, 'nombre': 'Fábrica grande', 'precio': 150000, 'ganancias': 16000, 'mantenimiento': 1000, 'espacio': 9, 'requisitos': [{'nombre': 'Esclavo', 'cantidad': 150}, {'nombre': 'Sgarristi', 'cantidad': 25}, {'nombre': 'Capodecina', 'cantidad': 3}], 'defensa': [{'id': 1, 'nombre': 'Sgarristi', 'ataque': 70, 'defensa': 15, 'vida': 100, 'cantidad': 25}, {'id': 2, 'nombre': 'Capodecina', 'ataque': 90, 'defensa': 30, 'vida': 100, 'cantidad': 3}]},        
        {'id': 6, 'nombre': 'Casa de usura', 'nivel': 3, 'precio': 10000, 'ganancias': 3000, 'mantenimiento': 0, 'espacio': 4, 'requisitos': [{'nombre': 'Gerente', 'cantidad': 10}, {'nombre': 'Administrador', 'cantidad': 1}, {'nombre': 'Piciotti', 'cantidad': 20}, {'nombre': 'Capodecina', 'cantidad': 2}], 'defensa': [{'id': 0, 'nombre': 'Piciotti', 'ataque': 70, 'defensa': 15, 'vida': 100, 'cantidad': 20}, {'id': 2, 'nombre': 'Capodecina', 'ataque': 90, 'defensa': 30, 'vida': 100, 'cantidad': 2}]},
        {'id': 7, 'nombre': 'Cuartel pequeño', 'precio': 5000, 'ganancias': 0, 'mantenimiento': 0, 'espacio': 1, 'poblacion': 20, 'defensa': []},    
        {'id': 8, 'nombre': 'Cuartel mediano', 'precio': 30000, 'ganancias': 0, 'mantenimiento': 0, 'espacio': 9, 'poblacion': 150, 'defensa': []},
        {'id': 9, 'nombre': 'Cuartel grande', 'precio': 100000, 'ganancias': 0, 'mantenimiento': 0, 'espacio': 25, 'poblacion': 500, 'defensa': []},  
        {'id': 10, 'nombre': 'Cuartel de guerra', 'precio': 1000000, 'ganancias': 0, 'mantenimiento': 0, 'espacio': 49, 'poblacion': 1000, 'defensa': []}]}
    

  def create_user_if_not_exists(self, user_id):
    self.balances.setdefault(user_id, {'wallet': 0, 'bank': 0})

  def get_balance(self, user_id):
    self.create_user_if_not_exists(user_id)
    return self.balances[user_id]

  def get_all_balances(self, message):
    all_balances = {}
    guild = message.guild
    
    for member in guild.members:
      balances = self.get_balance(member.id)
      total_balance = balances['wallet'] + balances['bank']
      if total_balance > 0:
        all_balances[member.id] = balances
    
    return all_balances

  def add_money(self, user_id, amount, type):
    self.create_user_if_not_exists(user_id)
    self.balances[user_id][type] += amount

  def remove_money(self, user_id, amount, type):
    self.create_user_if_not_exists(user_id)
    if amount <= 0:
      return False
    if self.balances[user_id][type] < amount:
      return False
    
    self.balances[user_id][type] -= amount
    return True


  def transfer_money(self, sender_id, recipient_id, amount):
    self.create_user_if_not_exists(sender_id)
    self.create_user_if_not_exists(recipient_id)
    if self.balances[sender_id]['bank'] >= amount and self.balances[sender_id]['bank'] != 0:
      self.balances[sender_id]['bank'] -= amount
      self.balances[recipient_id]['bank'] += amount
      return True
    return False
    
  def reset(self, user, type, message):
    users = None
    if user == 'all':
      guild = message.guild
      users = guild.members
    if type == 'inventario':
      if users is not None:
        for usuario in users:
          if usuario.id in self.items:
            del self.items[usuario.id]
        return True
      del self.items[user.id]     
      return True
    elif type == 'balance':
      if users is not None:
        for usuario in users:
          if usuario.id in self.balances:
            self.balances[usuario.id] = {
              'wallet': 0,
              'bank': 0
            }
        return True
      self.balances[user.id] = {
        'wallet': 0,
        'bank': 0
      }
      return True    
    elif type == 'ejercito':
      if users is not None:
        for usuario in users:
          if usuario.id in self.ejercito:
            del self.ejercito[usuario.id]
        return True
      del self.ejercito[user.id]
      return True
    elif type == 'construcciones':
      if users is not None:
        for usuario in users:
          if usuario.id in self.construcciones:
            with open('map_data.pkl', 'rb') as file:
              loaded_data = pickle.load(file)
            map_data = loaded_data['map_data']
            map_objects = loaded_data['map_objects']
            map_original = loaded_data['map_original']

            for x in range(500):
              for y in range(500):  
                if map_objects[x][y] and map_objects[x][y]['usuario'] == usuario.id:
                  map_objects[x][y] = None
                  map_data[x][y] = map_original[x][y]  
            
            with open('map_data.pkl', 'wb') as file:
              data = {
                'map_data': map_data,
                'map_objects': map_objects,
                'map_original': map_original
              }
              pickle.dump(data, file) 
            del self.construcciones[usuario.id]
        return True
      with open('map_data.pkl', 'rb') as file:
        loaded_data = pickle.load(file)
      map_data = loaded_data['map_data']
      map_objects = loaded_data['map_objects']
      map_original = loaded_data['map_original']

      for x in range(500):
        for y in range(500):  
          if map_objects[x][y] and map_objects[x][y]['usuario'] == user.id:
            map_objects[x][y] = None
            map_data[x][y] = map_original[x][y]  
            
      with open('map_data.pkl', 'wb') as file:
        data = {
          'map_data': map_data,
          'map_objects': map_objects,
          'map_original': map_original
        }
        pickle.dump(data, file) 

      del self.construcciones[user.id]
      return True
    elif type == 'solicitudes':
      if users is not None:
        for usuario in users:
          if usuario.id in self.solicitud:
            self.solicitud.remove(usuario.id)
        return True
      self.solicitud.remove(user.id)
      return True
    elif type == 'collect':
      if users is not None:
        for usuario in users:
          if usuario.id in self.collect:
            del self.collect[usuario.id]
        return True
      del self.collect[user.id]
      return True
    elif type == 'secuestros':
      if users is not None:
        for usuario in users:
          if usuario.id in self.secuestros:
            del self.secuestros[usuario.id]
        return True
      del self.secuestros[user.id]
      return True

    return False
    
  def save_data(self):
    data = {
      'balances': self.balances,
      'items': self.items,
      'equipos': self.equipos,
      'gremios': self.gremios,
      'ejercito': self.ejercito,
      'construcciones': self.construcciones,
      'redada': self.redada,
      'eliminados': self.eliminados,
      'secuestros': self.secuestros,
      'solicitud': self.solicitud,
      'recompensas': self.recompensas,
      'jackpot': self.jackpot,
      'rob': self.rob,
      'carreras': self.carreras
    }
    with open('economy_data.pickle', 'wb') as file:
      pickle.dump(data, file)

  def load_data(self):
    try:
      with open('economy_data.pickle', 'rb') as file:
        data = pickle.load(file)
        self.balances = data.get('balances', {})
        self.items = data.get('items', {})
        self.equipos = data.get('equipos', {})
        self.gremios = data.get('gremios', [])
        self.ejercito = data.get('ejercito', {})
        self.construcciones = data.get('construcciones', {})
        self.redada = data.get('redada', [])
        self.eliminados = data.get('eliminados', [])
        self.secuestros = data.get('secuestros', {})
        self.solicitud = data.get('solicitud', [])
        self.recompensas = data.get('recompensas', {})
        self.jackpot = data.get('jackpot', {})
        self.rob = data.get('rob', {})
        self.carreras = data.get('carreras', {})
    except FileNotFoundError:
      self.balances = {}
      self.items = {}
      self.equipos = {}
      self.gremios = []
      self.ejercito = {}
      self.construcciones = {}
      self.redada = []
      self.eliminados = []
      self.secuestros = {}
      self.solicitud = []
      self.recompensas = {}
      self.jackpot = {}
      self.rob = {}
      self.carreras = {}

  def search_object(self, id_object, role):
    for objeto in self.tienda[role]:
      if objeto['id'] == id_object:
        return objeto
    return None

  def search_soldado(self, id_object, role):
    for objeto in self.soldados[role]:
      if objeto['id'] == id_object:
        return objeto
    return None
    
  def reclutar_soldado(self, user_id, role, soldado_id, cantidad, emoji, bot):
    soldado = self.search_soldado(soldado_id, role)

    if soldado is not None:
      ejercito = self.show_user_ejercito(user_id)
      total = 0
      if ejercito:
        for s in ejercito:
          if s['id'] <= 3:
            total += s['cantidad'] 
      total += cantidad

      construcciones = self.show_user_construcciones(user_id)
      poblacion = 0
      
      if role == 'Dirigente':
        guild = bot.get_guild(self.g)
        for member in guild.members:
          if has_role(member, 'Alcalde'):
            alcalde = member
            break
        
        construcciones_alcalde = self.show_user_construcciones(alcalde.id)
        if construcciones_alcalde:
          for objeto in construcciones_alcalde:
            if 'poblacion' in objeto:
              poblacion += objeto['poblacion']

      if construcciones:
        for objeto in construcciones:
          if 'poblacion' in objeto:
            poblacion += objeto['poblacion']

      if role != 'Empresario':
        if poblacion < total:
          return f"No tiene espacio para tantos soldados! Ahora mismo, tienes un espacio maximo de {poblacion}!"
      
      price = soldado['precio'] * cantidad
      nombre = soldado['nombre']
      if 'max_persona' in soldado:
        if soldado['max_persona'] > 0:
          cantidad_actual = self.get_soldado_cantidad(user_id, soldado['id'])
          if cantidad_actual >= soldado['max_persona']:
            return f"Ya has alcanzado el límite máximo de reclutamiento de {nombre}.❌❌"
          elif cantidad > soldado['max_persona']:
            return f"No puedes reclutar más de {soldado['max_persona']} {nombre}.❌❌"
      if self.remove_money(user_id, price, 'wallet'):
        soldado_aux = soldado.copy()

        for g in self.gremios:
          if user_id in g['miembros'] and g['desbloqueados']['Defensa'] != []:
              soldado_aux['defensa'] = soldado['defensa'] * (1 + 100 / g['desbloqueados']['Defensa'][-1])

        self.add_soldado(user_id, soldado_aux, cantidad) 
            
        return f"¡Has comprado {cantidad} {nombre} por {price} {emoji}!✅✅"
      else:
        return f"No tienes suficientes {emoji} para reclutarlo.❌❌"
    else:
      return "El soldado no está disponible en la caballeria.❌❌"
      
  def show_soldados(self, role):
    if role in self.soldados:
      return self.soldados[role]
    else:
      return None

  def show_gremios(self, user_id):
    if user_id in self.gremios:
      return self.gremios[user_id]
    else:
      return None
      
  def add_soldado(self, user_id, soldado, cantidad):
    self.create_user_if_not_exists(user_id)
    
    # Verificar el límite de reclutamiento máximo
    if 'maximo' in soldado:
      if soldado['maximo'] > 0:
        cantidad_actual = self.get_soldado_cantidad(user_id, soldado['id'])
        
        if cantidad_actual >= soldado['maximo']:
          return False
        elif cantidad + cantidad_actual > soldado['maximo']:
          return False
        
    if user_id in self.ejercito:
      for item in self.ejercito[user_id]:
        if item['id'] == soldado['id']:
          item.setdefault('cantidad', 0)
          item['cantidad'] += cantidad
          return
      soldado_actualizado = soldado.copy()
      soldado_actualizado['cantidad'] = cantidad
      self.ejercito[user_id].append(soldado_actualizado)
    else:
      soldado['cantidad'] = cantidad
      self.ejercito[user_id] = [soldado]
    
    return True

  def get_soldado_cantidad(self, user_id, soldado_id):
    if user_id in self.ejercito:
        for item in self.ejercito[user_id]:
            if item['id'] == soldado_id:
                return item.get('cantidad', 0)
    return 0
    
  def buy_object(self, user, role, object_id, cantidad, emoji):
    objeto = self.search_object(object_id, role)
    if objeto is not None:
        
      if 'requisitos' in objeto:
        if user.id not in self.items:
          return f"No cumples con los requisitos necesarios para comprar {objeto['nombre']}.❌❌"
        
        soldados = self.soldados[role]
        requisitos_ejercito = False 
        requisitos = objeto['requisitos']
        for r in requisitos:
          for e in soldados:
            if r['nombre'] == e['nombre']:
              requisitos_ejercito = True
        tiene = False
        if 'max_persona' in objeto:
          inventario = self.show_user_items(user.id)
          if inventario:
            for item in inventario:
              if item['id'] == objeto['id'] and objeto['max_persona'] < item['cantidad'] + cantidad:
                tiene = True
                return f"Has alcanzado el máximo de {objeto['nombre']}.❌❌"
          if tiene is False:
            if objeto['max_persona'] < cantidad:
              return f"No puedes comprar tantos {objeto['nombre']}!❌❌"
            
        if 'max_total' in objeto:
          if objeto['max_total'] - cantidad < 0:
            return f"Se ha alcanzado el máximo de {objeto['nombre']}.❌❌"
          
        if requisitos:
          for requisito in requisitos:
            nombre_requisito = requisito['nombre']
            cantidad_requisito = requisito['cantidad']
            items_aux = self.items[user.id].copy()
            for item in items_aux:
              if item['nombre'] == nombre_requisito and item['cantidad'] < cantidad_requisito * cantidad:
                return f"No cumples con los requisitos necesarios para comprar {objeto['nombre']}.❌❌"  
            ejercito = self.show_user_ejercito(user.id)
            if requisitos_ejercito:
              if ejercito:
                ejercito_aux = ejercito.copy()
                for soldado in ejercito_aux:
                  if soldado['nombre'] == nombre_requisito and soldado['cantidad'] < cantidad_requisito * cantidad:
                    return f"No cumples con los requisitos necesarios para comprar {objeto['nombre']}.❌❌" 
              else:
                return f"No cumples con los requisitos necesarios para comprar {objeto['nombre']}.❌❌" 
        
        for requisito in requisitos:
          nombre_requisito = requisito['nombre']
          cantidad_requisito = requisito['cantidad']
          for item in self.items[user.id]:
            if item['nombre'] == nombre_requisito and item['cantidad'] >= cantidad_requisito * cantidad:
              item['cantidad'] -= cantidad_requisito * cantidad

              if item['cantidad'] <= 0:
                self.items[user.id].remove(item)

              break
          ejercito = self.show_user_ejercito(user.id)
          if requisitos_ejercito:
            if ejercito:
              for soldado in ejercito:
                if soldado['nombre'] == nombre_requisito and soldado['cantidad'] >= cantidad_requisito * cantidad:
                  soldado['cantidad'] -= cantidad_requisito * cantidad

                  if soldado['cantidad'] <= 0:
                    self.ejercito[user.id].remove(soldado)

                  break

      price = objeto['precio'] * cantidad
      nombre = objeto['nombre']
      if self.balances[user.id]['wallet'] < price:
        return f"No tienes suficientes {emoji} para comprar ese objeto.❌❌"
      
      if 'max_total' in objeto:
        if objeto['max_total'] - cantidad >= 0:
          objeto['max_total'] -= cantidad
        else:
          return f"Se ha alcanzado el máximo de {objeto['nombre']}.❌❌"
      print(cantidad)
      self.remove_money(user.id, price, 'wallet')
      self.add_item(user.id, objeto, cantidad)
        
      return f"¡Has comprado {cantidad} {nombre} por {price} {emoji}!✅✅"       
    else:
      return "El objeto no está disponible en la tienda.❌❌"

  def show_user_items(self, user_id):
    if user_id in self.items:
      if self.items[user_id] == []:
        del self.items[user_id]
        
      return self.items[user_id]
    else:
      return None

  def show_user_ejercito(self, user_id):
    if user_id in self.ejercito:
      if self.ejercito[user_id] == []:
        del self.ejercito[user_id]
      
      return self.ejercito[user_id]
    else:
      return None

  def show_user_construcciones(self, user_id):
    if user_id in self.construcciones:
      if self.construcciones[user_id] == []:
        del self.construcciones[user_id]

      return self.construcciones[user_id]
    else:
      return None
  
  def search_construccion(self, user_id, construccion_id):
    if user_id in self.construcciones:
      for construcciones in self.construcciones[user_id]:
        if construcciones['id'] == construccion_id:
          return construcciones
    return None
      
  def show_shop(self, role):
    if role in self.tienda:
      return self.tienda[role]

  def add_item(self, user_id, objeto, cantidad):
    self.create_user_if_not_exists(user_id)
    if user_id in self.items:
      for item in self.items[user_id]:
        if item['id'] == objeto['id']:
          item.setdefault('cantidad', 0)
          item['cantidad'] += cantidad
          return
      item_actualizado = objeto.copy()
      item_actualizado['cantidad'] = cantidad
      self.items[user_id].append(item_actualizado)
    else:
      objeto['cantidad'] = cantidad
      self.items[user_id] = [objeto]
      
    return True
