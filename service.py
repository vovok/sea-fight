#!python
# -*- coding: utf-8 -*-
from random import randint, choice
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


def gen_cord(strategy):
    """Генератор всех возможных комбинаций координат + генерирует случайную стратегию из 12 координат"""
    all_comb, cords_for_1_ship = GLOBAL_DATA
    GLOBAL_DATA[1]["random_12"] = []
    while len(GLOBAL_DATA[1]["random_12"]) != 12:
        x_cord = randint(0, 9)
        y_cord = randint(0, 9)
        if [x_cord, y_cord] not in GLOBAL_DATA[1]["random_12"]:
            GLOBAL_DATA[1]["random_12"].append([x_cord, y_cord])
    for_1_ship = cords_for_1_ship[strategy]
    for_other_ship = filter(lambda x: x not in for_1_ship, all_comb)
    cord_comb = {1: [[x] for x in for_1_ship], 2: [], 3: [], 4: []}
    for ship in filter(lambda x: x != 1, cord_comb.keys()):
        for cord in for_other_ship:
            hor_direction = [cord] + [[cord[0] + x, cord[1]] for x in range(1, ship)]
            ver_direction = [cord] + [[cord[0], cord[1] + x] for x in range(1, ship)]
            for dir_d in [hor_direction, ver_direction]:
                for cord_d in dir_d:
                    if cord_d not in for_other_ship:
                        break
                else:
                    cord_comb[ship].append(dir_d)
    return cord_comb


def get__cord_for_1_ship():
    """Генерирует 7 кобинайций расстановки однопалубных и возвращает случайную комбинацию"""
    cord_for_1_ship = {
        "for_1_ship_left": filter(lambda x: x[0] in range(0, 6) and x[1] in range(0, 10), CORD_10_10),
        "for_1_ship_right": filter(lambda x: x[0] in range(4, 10) and x[1] in range(0, 10), CORD_10_10),
        "for_1_ship_top": filter(lambda x: x[0] in range(0, 10) and x[1] in range(0, 6), CORD_10_10),
        "for_1_ship_bottom": filter(lambda x: x[0] in range(0, 10) and x[1] in range(4, 10), CORD_10_10),
        "for_1_ship_center_horisontal": filter(lambda x: x[0] in range(2, 10) and x[1] in range(2, 8), CORD_10_10),
        "for_1_ship_center_vertical": filter(lambda x: x[0] in range(2, 8) and x[1] in range(0, 10), CORD_10_10),
        "for_1_ship_36": filter(lambda x: x[0] in range(2, 8) and x[1] in range(2, 8), CORD_10_10)}
    return CORD_10_10, cord_for_1_ship


def gen_cross_cord():
    cross_cord = []
    cross_cord.extend([[x, x] for x in range(10)])
    cross_cord.extend([[9 - x, x] for x in range(10)])
    cross_cord.extend([[x, y] for x in range(5, 6) for y in range(1, 10, 2)])
    cross_cord.extend([[x, y] for x in range(4, 5) for y in range(0, 10, 2)])
    cross_cord.extend([[x, y] for y in range(5, 6) for x in range(1, 10, 2)])
    cross_cord.extend([[x, y] for y in range(4, 5) for x in range(0, 10, 2)])
    del_cords = [[x, y] for x in range(4, 6) for y in range(4, 6)]
    for del_crd in del_cords:
        while 1:
            if del_crd in cross_cord:
                cross_cord.remove(del_crd)
            else:
                break
    return cross_cord


def gen_linear_cord_var_2():
    """http://habrahabr.ru/post/180995/ вариант 2"""
    linear_cord = []
    linear_cord.extend([[3 - x, 0 + x] for x in range(4)])
    linear_cord.extend([[7 - x, 0 + x] for x in range(8)])
    linear_cord.extend([[2 + x, 9 - x] for x in range(8)])
    linear_cord.extend([[6 + x, 9 - x] for x in range(4)])
    return linear_cord


CORD_10_10 = [[x / 10, x % 10] for x in range(100)]
GLOBAL_DATA = get__cord_for_1_ship()
STEPS_STRATEGY = {"cross": gen_cross_cord(), "linear": gen_linear_cord_var_2(), "random": []}
