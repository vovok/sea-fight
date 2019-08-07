#!/usr/bin/env python
# -*- coding: utf-8 -*-
import service
from random import choice, randint, shuffle
from copy import copy, deepcopy
from logging import basicConfig, INFO, info

basicConfig(format=u'[%(asctime)s]  %(message)s', level=INFO)


class Game(object):
    def __init__(self, player1, player2):
        # info(u'Начало игры')
        self.player_list = [player1, player2]
        self.curr_player = None
        self.player_log_list()

    def player_log_list(self):
        # info(u'Игроки: %s', ", ".join([x.player_name for x in self.player_list]))
        pass

    def game(self):
        tour_stats.game_id += 1
        # Выбираем игрока для первого хода
        if self.curr_player is None:
            self.curr_player = choice(self.player_list)
        # Получаем координаты для хода
        crd_for_shoot = self.curr_player.strategy.get_crd_for_step()
        # Выделяем второго игрока из списка
        player2 = filter(lambda x: x != self.curr_player, self.player_list)[0]
        # Ходим и сохраняем результаты хода
        shoot_res = player2.shoot(crd_for_shoot)
        # Передаём результаты хода ходившему игроку
        # logging.info(u'Ходит: %s, координаты: %s, статус: %s', self.curr_player.player_name, crd_for_shoot, shoot_res)
        self.curr_player.strategy.return_shoot_state(shoot_res, crd_for_shoot, player2)
        self.curr_player.stat.step += 1
        if shoot_res in [u'Убил!', u'Попал!']:
            self.curr_player.stat.score += 1
        # Меняем счётчик текущего пользователя, если ходивший промазал
        if shoot_res == u'Мимо!':
            self.curr_player = player2
        # Конец игры и вывод статистики
        if shoot_res == u'Убил!':
            self.curr_player.stat.ships_defeat.append(1)
            if len(self.curr_player.stat.ships_defeat) == 10:
                # info(u'Выйграл: %s', self.curr_player.player_name)
                # info(u'%s', ", ".join([str(x.player_name) + u" набрал очков:  " + str(x.scores) + u", ходов: " + str(x.steps) for x in self.player_list]))
                # Сбрасываем счётчики
                self.curr_player.stat.tur_scores += self.curr_player.stat.score
                tour_stats.get_stats(self.player_list)
                self.curr_player.reset_values()
                # info(u'------------------')
                return self.curr_player
        # Если игра продолжается, то перезапускаем функцию game()
        return self.game()


class Player(object):
    def __init__(self):
        self.player_name = service.rdn_usr_name()
        self.strategy = PlayerStrategy()
        self.stat = PlayerStatistic()
        self.ships = self.create_ships()

    def create_ships(self):
        self.ships = []
        buff_cord = []
        ships = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
        for ship in ships:
            if self.strategy.combinations[ship]:
                cords = choice(self.strategy.combinations[ship])
                overlay = service.set_halo(cords)
                self.strategy.data_cleaner(cords, overlay)
                buff_cord.append([ship, cords, overlay])
            else:
                self.strategy.reload()
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
                return shoot_res
        else:
            return u'Мимо!'

    def reset_values(self):
        self.strategy.reset()
        self.stat.reset()
        self.ships = self.create_ships()


class Ship(object):
    def __init__(self, ship_type, cord, halo):
        self.ship_type = ship_type
        self.cord = cord
        self.halo = halo
        self.shoots = []
        self.state = u'Цел'

    def get_state(self):
        if len(self.shoots) == self.ship_type:
            self.state = u'Убил!'
        else:
            self.state = u'Попал!'
        return self.state


class PlayerStatistic(object):
    def __init__(self):
        self.score = 0
        self.step = 0
        self.ships_defeat = []
        self.tur_scores = 0

    def reset(self):
        self.score = 0
        self.step = 0
        self.ships_defeat = []


class TournaimentStatistic(object):
    def __init__(self):
        self.game_id = 0
        self.step_all = []
        self.step_winners = []
        self.scores_loosers = []
        self.step_loosers = []
        self.players_copy_list = []

    def get_stats(self, player_list):
        self.players_copy_list.extend([deepcopy(player) for player in player_list])

    def count_middles(self):
        self.step_all = [player.stat.step for player in self.players_copy_list]
        self.step_winners = [player.stat.step for player in self.players_copy_list if
                             len(player.stat.ships_defeat) == 10]
        self.step_loosers = [player.stat.step for player in self.players_copy_list if
                             len(player.stat.ships_defeat) != 10]
        self.scores_loosers = [player.stat.score for player in self.players_copy_list if
                               len(player.stat.ships_defeat) != 10]
        return sum(self.step_all) / float(len(self.step_all)), sum(self.step_winners) / float(
            len(self.step_winners)), sum(self.step_loosers) / float(len(self.step_loosers)), sum(
            self.scores_loosers) / float(len(self.scores_loosers))

    def startegy_effect(self):
        report_strategy = {u"Победители": [], u"Проигравшие": []}
        for player in self.players_copy_list:
            pl_stat = ""
            if len(player.stat.ships_defeat) == 10:
                pl_stat = u"Победители"
            else:
                pl_stat = u"Проигравшие"
            report_strategy[pl_stat].append(
                [player.strategy.ships_strategy_collocation, player.strategy.steps_strategy])
        return report_strategy


class PlayerStrategy(object):
    def __init__(self):
        self.alien_cords = []
        self.recomendation_pool = []
        self.succ_shoots = []
        self.ships_strategy_collocation = STRATEGY_QUOTA.pop()
        self.combinations = deepcopy(service.gen_cord(self.ships_strategy_collocation))
        self.steps_strategy = choice(list(service.STEPS_STRATEGY.keys()))
        self.steps_cords = deepcopy(service.STEPS_STRATEGY[self.steps_strategy])

    def get_crd_for_step(self):
        """Выбор координат для хода"""
        if self.recomendation_pool:
            crd = self.recomendation_pool.pop(0)
        elif self.steps_cords:
            shuffle(self.steps_cords)
            crd = self.steps_cords.pop(0)
        else:
            crd = choice(filter(lambda x: x not in self.alien_cords, service.CORD_10_10))
        if crd in self.recomendation_pool:
            self.recomendation_pool.remove(crd)
        elif crd in self.recomendation_pool:
            self.recomendation_pool.remove(crd)
        self.alien_cords.append(crd)
        return crd

    def return_shoot_state(self, state, crd, player2):
        """Стратегия дальнейщих ходов в зависимости от результата текущего хода"""
        if state == u'Попал!':
            if not self.recomendation_pool:
                crd_rec = [[crd[0] - 1, crd[1]], [crd[0] + 1, crd[1]], [crd[0], crd[1] - 1], [crd[0], crd[1] + 1]]
                crd_rec = filter(lambda x: 0 <= x[0] <= 9 and 0 <= x[1] <= 9, crd_rec)
                self.succ_shoots.append(crd)
                self.recomendation_pool.extend([crd for crd in crd_rec if crd not in self.alien_cords])
            else:
                crd_s1 = self.recomendation_pool[0]
                crd_s2 = self.succ_shoots[0]
                for ind in range(2):
                    if crd_s1[ind] != crd_s2[ind]:
                        if crd_s1[ind] > crd_s2[ind]:
                            crd_rec = [[crd_s1[ind] + 1, crd_s1[ind] + 2], [crd_s2[ind] - 1, crd_s2[ind] - 2]]
                        else:
                            crd_rec = [[crd_s1[ind] - 1, crd_s1[ind] - 2], [crd_s2[ind] + 1, crd_s2[ind] + 2]]
                        crd_rec = filter(lambda x: 0 <= x[0] <= 9 and 0 <= x[1] <= 9, crd_rec)
                        self.recomendation_pool.extend([crd for crd in crd_rec if crd not in self.alien_cords])
        elif state == u'Убил!':
            for ship in player2.ships:
                if crd in ship.cord:
                    self.alien_cords.extend([crd for crd in ship.halo if crd not in self.alien_cords])
                    self.steps_cords = filter(lambda x: x not in ship.halo and x not in self.alien_cords,
                                              self.steps_cords)
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

    def reload(self):
        self.combinations = deepcopy(service.gen_cord(self.ships_strategy_collocation))

    def reset(self):
        self.alien_cords = []
        self.recomendation_pool = []
        self.succ_shoots = []
        self.combinations = deepcopy(service.gen_cord(self.ships_strategy_collocation))
        self.steps_strategy = choice(service.STEPS_STRATEGY.keys())
        self.steps_cords = deepcopy(service.STEPS_STRATEGY[self.steps_strategy])


if __name__ == '__main__':
    turnaiment_player_counter = 1024
    tour_stats = TournaimentStatistic()
    info(u'Начало турнира')
    STRATEGY_QUOTA = [y for y in ["for_1_ship_left",
                                  "for_1_ship_right",
                                  "for_1_ship_top",
                                  "for_1_ship_bottom",
                                  "for_1_ship_center_horisontal",
                                  "for_1_ship_center_vertical",
                                  "for_1_ship_36",
                                  "random_12"] for x in range(int(turnaiment_player_counter / 8))]
    shuffle(STRATEGY_QUOTA)
    tur_player_list = [Player() for player in range(turnaiment_player_counter)]
    # info(u'Список игроков: %s', ", ".join([x.player_name for x in tur_player_list]))
    tur_player_list_next_iter = []
    while len(tur_player_list) != 1:
        for player_ind in range(1, len(tur_player_list), 2):
            winner = Game(tur_player_list[player_ind - 1], tur_player_list[player_ind]).game()
            tur_player_list_next_iter.append(winner)
        tur_player_list = copy(tur_player_list_next_iter)
        tur_player_list_next_iter = []
    else:
        info(u'Турнир выйграл: %s, набрал очков: %s', tur_player_list[0].player_name,
             tur_player_list[0].stat.tur_scores)
    med_step_all, med_step_win, med_step_looser, med_score_looser = tour_stats.count_middles()
    info(
        u'Статистика: \n\t1. Среднее количесво ходов (всех игроков): %.2f,\n\t2. Среднее количество ходов выйгравших игроков: %.2f,\n\t3. Среднее количество ходов проигравших игроков: %.2f,\n\t4. Среднее количество очков, которое набрали проигравшие: %.2f',
        med_step_all, med_step_win, med_step_looser, med_score_looser)
    res_strat = tour_stats.startegy_effect()
    for pl_stat in res_strat.keys():
        info(u'%s:', pl_stat)
        bf = []
        for strategy_com in res_strat[pl_stat]:
            if strategy_com not in bf:
                bf.append(strategy_com)
                info(u'%s: %s', ", ".join(strategy_com), res_strat[pl_stat].count(strategy_com))
