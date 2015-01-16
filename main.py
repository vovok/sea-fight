#!python
# -*- coding: utf-8 -*-
import service
from random import choice, randint
from copy import copy, deepcopy
from logging import basicConfig, INFO, info

basicConfig(format=u'[%(asctime)s]  %(message)s', level=INFO)


class Game(object):
	def __init__(self, player1, player2):
		info(u'Начало игры')
		self.player_list = [player1, player2]
		self.curr_player = None
		self.player_log_list()

	def player_log_list(self):
		info(u'Игроки: %s', ", ".join([x.player_name for x in self.player_list]))

	def game(self):
		# Выбираем игрока для первого хода
		if self.curr_player is None:
			self.curr_player = choice(self.player_list)
		# Получаем координаты для хода
		crd_for_shoot = self.curr_player.step()
		# Выделяем второго игрока из списка
		player2 = filter(lambda x: x != self.curr_player, self.player_list)[0]
		# Ходим и сохраняем результаты хода
		shoot_res = player2.shoot(crd_for_shoot)
		# Передаём результаты хода ходившему игроку
		#logging.info(u'Ходит: %s, координаты: %s, статус: %s', self.curr_player.player_name, crd_for_shoot, shoot_res)
		self.curr_player.return_shoot_state(shoot_res, crd_for_shoot, player2)
		# Меняем счётчик текущего пользователя, если ходивший промазал
		if shoot_res == u'Мимо!':
			self.curr_player = player2
		# Конец игры и вывод статистики
		elif shoot_res == u'Убил последний корабль!':
			self.curr_player.scores += 1
			info(u'Выйграл: %s', self.curr_player.player_name)
			info(u'%s', ", ".join([str(x.player_name) + u" набрал очков:  " + str(x.scores) + u", ходов: " + str(x.steps) for x in self.player_list]))
			# Подготавливаем к следующей игре
			stats.get_stats(self.player_list)
			self.curr_player.reset_values()
			info(u'------------------')
			return self.curr_player
		# Если игра продолжается, то перезапускаем функцию game()
		return self.game()


class Player(object):
	def __init__(self):
		self.player_name = service.rdn_usr_name()
		self.combinations = deepcopy(service.GLOBAL_DATA)
		self.ships = self.create_ships()
		self.alien = []
		self.recomendation_pool = []
		self.ships_defeat = []
		self.succ_shoots = []
		self.scores = 0
		self.steps = 0
		self.tur_scores = 0

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

	def return_shoot_state(self, state, crd, player2):
		"""Стратегия дальнейщих ходов в зависимости от результата текущего хода"""
		if state == u'Попал!':
			self.scores += 1
			if not self.recomendation_pool:
				crd_rec = [[crd[0] - 1, crd[1]], [crd[0] + 1, crd[1]], [crd[0], crd[1] - 1], [crd[0], crd[1] + 1]]
				crd_rec = filter(lambda x: 0 <= x[0] <= 9 and 0 <= x[1] <= 9, crd_rec)
				crd_rec = filter(lambda x: x not in self.alien, crd_rec)
				self.succ_shoots.append(crd)
				self.recomendation_pool.extend(crd_rec)
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
						self.recomendation_pool.extend(crd_rec)
		elif state == u'Убил!':
			for ship in player2.ships:
				if crd in ship.cord:
					self.alien.extend(ship.halo)
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

	def reset_values(self):
		self.combinations = deepcopy(service.GLOBAL_DATA)
		self.create_ships()
		self.alien = []
		self.recomendation_pool = []
		self.ships_defeat = []
		self.succ_shoots = []
		self.tur_scores += self.scores
		self.scores = 0
		self.steps = 0


class Ship(object):
	def __init__(self, ship_type, cord, halo):
		self.ship_type = ship_type
		self.cord = cord
		self.halo = halo
		self.shoots = []
		self.state = u''

	def get_state(self):
		if len(self.shoots) == self.ship_type:
			self.state = u'Убил!'
		else:
			self.state = u'Попал!'
		return self.state

class Statistic(object):
	def __init__(self):
		self.step_all = []
		self.step_winners = []
		self.scores_loosers = []
		self.step_loosers = []

	def get_stats(self, player_list):
		for pl in player_list:
			self.step_all.append(pl.steps)
			if len(pl.ships_defeat) == 10:
				self.scores_loosers.append(pl.scores)
				self.step_loosers.append(pl.steps)
			else:
				self.step_winners.append(pl.steps)

	def count_middles(self):
		return sum(self.step_all)/float(len(self.step_all)), sum(self.step_winners)/float(len(self.step_winners)), sum(self.step_loosers)/float(len(self.step_loosers)), sum(self.scores_loosers)/float(len(self.scores_loosers))


if __name__ == '__main__':
	stats = Statistic()
	turnaiment_player_counter = 1024
	info(u'Начало турнира')
	tur_player_list = [Player() for player in range(turnaiment_player_counter)]
	info(u'Список игроков: %s', ", ".join([x.player_name for x in tur_player_list]))
	tur_player_list_next_iter = []
	while len(tur_player_list) != 1:
		for player_ind in range(1, len(tur_player_list), 2):
			winner = Game(tur_player_list[player_ind-1], tur_player_list[player_ind]).game()
			tur_player_list_next_iter.append(winner)
		tur_player_list = copy(tur_player_list_next_iter)
		tur_player_list_next_iter = []
	else:
		info(u'Турнир выйграл: %s, набрал очков: %s', tur_player_list[0].player_name, tur_player_list[0].tur_scores)
	med_step_all, med_step_win, med_step_looser, med_score_looser = stats.count_middles()
	info(u'Статистика: \n\t1. Среднее количесво ходов (всех игроков): %.2f,\n\t2. Среднее количество ходов выйгравших игроков: %.2f,\n\t3. Среднее количество ходов проигравших игроков: %.2f,\n\t4. Среднее количество очков, которое набрали проигравшие: %.2f', med_step_all, med_step_win, med_step_looser,med_score_looser)
