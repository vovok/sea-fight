#!python
# -*- coding: utf-8 -*-
from random import randint
from itertools import permutations as comb


def rdn_usr_name():
	"""Генерирует случайное имя для робота на основе 5-ти суффиксов"""
	suffix_list = ['pa', 'li', 'ra', 'co', 'si']
	res = ''
	for cntr in range(3): res += suffix_list[randint(0, 4)]
	return res.capitalize() + str(randint(0, 999))


def adds(cord, delta):
	"""Функция суммирования значений двух списков"""
	sum_list = []
	for i in range(len(cord)):
		sum_list.append(cord[i] + delta[i])
	return sum_list

def set_halo(cords):
	"""Функция генерации ореола по координатам"""
	halo = []
	delta_comb = list(comb(range(-1, 2), 2))
	delta_comb += [(1, 1), (-1, -1)]
	for cord in cords:
		for delta in delta_comb:
			ads = adds(cord, delta)
			if ads != 0 and ads not in halo and ads not in cords:
				halo.append(ads)
	return filter(lambda x: 0 <= x[0] <= 9 and 0 <= x[1] <= 9, halo)

def gen_cord():
	"""Генератор всех возможных комбинаций координат"""
	all_comb = [[x/10, x % 10] for x in range(100)]
	for_1_ship = filter(lambda x: x[0] in range(2, 8) and x[1] in range(2, 8), all_comb)
	for_other_ship = filter(lambda x: x not in for_1_ship, all_comb)
	cord_comb = {1: [[x] for x in for_1_ship], 2: [], 3: [], 4: []}
	for ship in filter(lambda x: x != 1, cord_comb.keys()):
		for cord in for_other_ship:
			hor_direction = [cord] + [[cord[0]+x, cord[1]] for x in range(1, ship)]
			ver_direction = [cord] + [[cord[0], cord[1]+x] for x in range(1, ship)]
			for dir_d in [hor_direction, ver_direction]:
				for cord_d in dir_d:
					if cord_d not in for_other_ship:
						break
				else:
					cord_comb[ship].append(dir_d)
	return cord_comb

GLOBAL_DATA = gen_cord()
