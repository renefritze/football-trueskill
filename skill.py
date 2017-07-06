#!/usr/bin/env python

import sys
import csv
import trueskill as ts
import pprint

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

teamcount = 18
csv_filename = '2016.csv'
teams = { t: (ts.Rating(), ClassicRanking()) for t in _team_names(csv_filename) }

process_season(csv_filename, teams)

teams = sorted(teams.items(), key=lambda var: var[1][0])
teams.reverse()
pprint.pprint(teams)
