#!/usr/bin/env python

import sys
import csv
import trueskill as ts
import pprint
import tabulate

class ClassicRanking(object):

    def __init__(self):
        self.goals_scored = 0
        self.goals_conceded = 0
        self.points = 0

    def score_game(self, goals_scored, goals_conceded):
        self.goals_conceded += goals_conceded
        self.goals_scored += goals_scored
        if goals_scored > goals_conceded:
            self.points += 3
        elif goals_scored == goals_conceded:
            self.points += 1

    @property
    def goal_diff(self):
        return self.goals_scored - self.goals_conceded

    def __lt__(self, other):
        if self.points < other.points:
            return True
        if self.points > other.points:
            return False
        # self.points == other.points
        if self.goal_diff < other.goal_diff:
            return True
        if self.goal_diff > other.goal_diff:
            return False
        # self.goal_diff == other.goal_diff
        if self.goals_scored < other.goals_scored:
            return True
        if self.goals_scored > other.goals_scored:
            return False
        raise RuntimeError


def _team_names(fn):
    ret = set()
    with open(fn) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            ret.add(row['HomeTeam'])
    return ret


def process_season(fn, teams):
    with open(fn) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            home = row['HomeTeam']
            away = row['AwayTeam']
            ranking_home, classic_home = teams[home]
            ranking_away, classic_away = teams[away]
            score_home = int(row['FTHG'])
            score_away = int(row['FTAG'])
            if score_home > score_away:
                ranking_home, ranking_away = ts.rate_1vs1(ranking_home, ranking_away)
            elif score_home < score_away:
                ranking_away, ranking_home = ts.rate_1vs1(ranking_away, ranking_home)
            else:
                ranking_home, ranking_away = ts.rate_1vs1(ranking_home, ranking_away, drawn=True)
            classic_home.score_game(score_home, score_away)
            classic_away.score_game(score_away, score_home)
            teams[home], teams[away] = (ranking_home, classic_home), (ranking_away, classic_away)


def print_table(teams):
    skillteams = sorted(teams.items(), key=lambda var: var[1][0])
    skillteams.reverse()
    classicteams = sorted(teams.items(), key=lambda var: var[1][1])
    classicteams.reverse()
    ranks = ['{:02d}.'.format(i) for i in range(1, len(skillteams)+1)]
    rows = [['Pos', 'TrueSkill', 'mu', 'Classic', 'pts'],]
    for r, c, s in zip(ranks, skillteams, classicteams):
        rows.append([r, c[0], '{:1f}'.format(c[1][0].mu), s[0], s[1][1].points])
    print(tabulate.tabulate(rows))

csv_filename = '2016.csv'
teams = { t: (ts.Rating(), ClassicRanking()) for t in _team_names(csv_filename) }
process_season(csv_filename, teams)
print_table(teams)
