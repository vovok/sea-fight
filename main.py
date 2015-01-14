#!python
# -*- coding: utf-8 -*-
import service
from random import choice, randint
from copy import deepcopy
import logging

logging.basicConfig(format=u'[%(asctime)s]  %(message)s', level=logging.INFO)


class Game(object):
	def __init__(self):
		logging.info(u'Начало игры')
		self.user_list = self.create_users()
		self.curr_user = None

	def create_users(self):
		self.user_list = []
		for u in range(2):
			self.user_list.append(User())
		logging.info(u'Игроки: %s', ", ".join([x.user_name for x in self.user_list]))
		return self.user_list

	def game(self):
		# Выбираем игрока для первого хода
		if self.curr_user is None:
			self.curr_user = choice(self.user_list)
		# Получаем координаты для хода
		crd_for_shoot = self.curr_user.step()
		# Выделяем второго игрока из списка
		user2 = filter(lambda x: x != self.curr_user, self.user_list)[0]
		# Ходим и сохраняем результаты хода
		shoot_res = user2.shoot(crd_for_shoot)
		# Передаём результаты хода ходившему игроку
		logging.info(u'Ходит: %s, координаты: %s, статус: %s', self.curr_user.user_name, crd_for_shoot, shoot_res)
		self.curr_user.return_shoot_state(shoot_res, crd_for_shoot)
		# Меняем счётчик текущего пользователя, если ходивший промазал
		if shoot_res == u'Мимо!':
			self.curr_user = user2
		# Конец игры и вывод статистики
		elif shoot_res == u'Убил последний корабль!':
			self.curr_user.scores += 1
			logging.info(u'Выйграл: %s', self.curr_user.user_name)
			logging.info(u'%s', ", ".join([str(x.user_name) + u" набрал очков:  " + str(x.scores) + u", ходов: " + str(x.steps) for x in self.user_list]))
			return
		# Если игра продолжается, то перезапускаем функцию game()
		return self.game()


class User(object):
	def __init__(self):
		self.user_name = service.rdn_usr_name()
		self.combinations = deepcopy(service.GLOBAL_DATA)
		self.ships = self.create_ships()
		self.alien = []
		self.recomendation_pool = []
		self.ships_defeat = []
		self.succ_shoots = []
		self.scores = 0
		self.steps = 0

	def create_ships(self):
		self.ships = []
		buff_cord = []
		ships = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
		for ship in ships:
			if self.combinations[ship]:
				cords = choice(self.combinations[ship])
				overlay = service.set_halo(cords)
				self.data_cleaner(cords, overlay)
				buff_cord.append([ship, cords, overlay])
			else:
				self.combinations = deepcopy(service.GLOBAL_DATA)
				return self.create_ships()
		for cords_for_unpack in buff_cord:
			ship, cords, overlay = cords_for_unpack
			self.ships.append(Ship(ship, cords, overlay))
		return self.ships

	def shoot(self, cords):
		"""Возвращает результат стрельбы по координатам"""
		for ship in self.ships:
			if cords in ship.cord:
				ship.shoots.append(cords)
				shoot_res = ship.get_state()
				if shoot_res == u'Убил!':
					self.ships_defeat.append(1)
					if len(self.ships_defeat) == 10:
						return u'Убил последний корабль!'
				return shoot_res
		else:
			return u'Мимо!'

	def step(self):
		"""Выбор координат для хода"""
		if not self.recomendation_pool:
			x, y = randint(0, 9), randint(0, 9)
			if [x, y] not in self.alien:
				self.alien.append([x, y])
				self.steps += 1
				return [x, y]
			else:
				return self.step()
		else:
			crd = self.recomendation_pool.pop(0)
			self.alien.append(crd)
			self.steps += 1
			return crd

	def return_shoot_state(self, state, crd):
		"""Стратегия дальнейщих ходов в зависимости от результата текущего хода"""
		if state == u'Попал!':
			self.scores += 1
			if not self.recomendation_pool:
				crd_rec = [[crd[0] - 1, crd[1]], [crd[0] + 1, crd[1]], [crd[0], crd[1] - 1], [crd[0], crd[1] + 1]]
				crd_rec = filter(lambda x: 0 <= x[0] <= 9 and 0 <= x[1] <= 9, crd_rec)
				crd_rec = filter(lambda x: x not in self.alien, crd_rec)
				self.succ_shoots.append(crd)
				return self.recomendation_pool.extend(crd_rec)
			else:
				crd_s1 = self.recomendation_pool[0]
				crd_s2 = self.succ_shoots[0]
				for ind in range(2):
					if crd_s1[ind] != crd_s2[ind]:
						if crd_s1[ind] > crd_s2[ind]:
							crd_rec = [[crd_s1[ind]+1, crd_s1[ind]+2], [crd_s2[ind]-1, crd_s2[ind]-2]]
						else:
							crd_rec = [[crd_s1[ind]-1, crd_s1[ind]-2], [crd_s2[ind]+1, crd_s2[ind]+2]]
						crd_rec = filter(lambda x: 0 <= x[0] <= 9 and 0 <= x[1] <= 9, crd_rec)
						crd_rec = filter(lambda x: x not in self.alien, crd_rec)
						return self.recomendation_pool.extend(crd_rec)
		elif state == u'Убил!':
			self.scores += 1
			self.recomendation_pool = []
			self.succ_shoots = []


	def data_cleaner(self, cords, overlay):
		"""Удаляет использованные комбинации из словаря комбинаций пользователя
		используется при создании кораблей"""
		del_index = {}
		for ship in self.combinations.keys():
			del_index[ship] = []
			for ind, crd_pack in enumerate(self.combinations[ship]):
				for crd in cords + overlay:
					if crd in crd_pack and ind not in del_index[ship]:
						del_index[ship].append(ind)
		for ship in del_index.keys():
			for ind_for_del in reversed(del_index[ship]):
				del self.combinations[ship][ind_for_del]


class Ship(object):
	def __init__(self, ship_type, cord, halo):
		self.ship_type = ship_type
		self.cord = cord
		self.overlay = halo
		self.shoots = []
		self.state = u''

	def get_state(self):
		if len(self.shoots) == self.ship_type:
			self.state = u'Убил!'
		else:
			self.state = u'Попал!'
		return self.state

if __name__ == '__main__':
	Game().game()