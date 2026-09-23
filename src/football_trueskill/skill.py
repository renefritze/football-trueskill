"""Compare league placements with classical scoring vs. TrueSkill(tm)."""

import argparse
import csv
from pathlib import Path

import tabulate
import trueskill as ts

DEFAULT_CSV = Path("data/german_bundesliga/2016.csv")

type Teams = dict[str, tuple[ts.Rating, ClassicRanking]]


class ClassicRanking:
    def __init__(self) -> None:
        self.goals_scored = 0
        self.goals_conceded = 0
        self.points = 0

    def score_game(self, goals_scored: int, goals_conceded: int) -> None:
        self.goals_conceded += goals_conceded
        self.goals_scored += goals_scored
        if goals_scored > goals_conceded:
            self.points += 3
        elif goals_scored == goals_conceded:
            self.points += 1

    @property
    def goal_diff(self) -> int:
        return self.goals_scored - self.goals_conceded

    def _sort_key(self) -> tuple[int, int, int]:
        return self.points, self.goal_diff, self.goals_scored

    def __lt__(self, other: ClassicRanking) -> bool:
        return self._sort_key() < other._sort_key()


def _team_names(fn: Path) -> set[str]:
    with fn.open(newline="") as csvfile:
        return {row["HomeTeam"] for row in csv.DictReader(csvfile)}


def process_season(fn: Path, teams: Teams) -> None:
    with fn.open(newline="") as csvfile:
        for row in csv.DictReader(csvfile):
            home = row["HomeTeam"]
            away = row["AwayTeam"]
            ranking_home, classic_home = teams[home]
            ranking_away, classic_away = teams[away]
            score_home = int(row["FTHG"])
            score_away = int(row["FTAG"])
            if score_home > score_away:
                ranking_home, ranking_away = ts.rate_1vs1(ranking_home, ranking_away)
            elif score_home < score_away:
                ranking_away, ranking_home = ts.rate_1vs1(ranking_away, ranking_home)
            else:
                ranking_home, ranking_away = ts.rate_1vs1(
                    ranking_home, ranking_away, drawn=True
                )
            classic_home.score_game(score_home, score_away)
            classic_away.score_game(score_away, score_home)
            teams[home] = (ranking_home, classic_home)
            teams[away] = (ranking_away, classic_away)


def build_table(teams: Teams) -> list[list[str | int]]:
    skillteams = sorted(teams.items(), key=lambda t: t[1][0].mu, reverse=True)
    classicteams = sorted(teams.items(), key=lambda t: t[1][1], reverse=True)
    rows: list[list[str | int]] = [["Pos", "TrueSkill", "mu", "Classic", "pts"]]
    for pos, (s_name, (rating, _)), (c_name, (_, classic)) in zip(
        range(1, len(skillteams) + 1), skillteams, classicteams, strict=True
    ):
        rows.append([f"{pos:02d}.", s_name, f"{rating.mu:1f}", c_name, classic.points])
    return rows


def process_file(csv_filename: Path) -> None:
    teams: Teams = {
        t: (ts.Rating(), ClassicRanking()) for t in _team_names(csv_filename)
    }
    process_season(csv_filename, teams)
    print(tabulate.tabulate(build_table(teams)))


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "csv_file",
        nargs="?",
        type=Path,
        default=DEFAULT_CSV,
        help=f"football-data.co.uk season CSV (default: {DEFAULT_CSV})",
    )
    args = parser.parse_args(argv)
    process_file(args.csv_file)


if __name__ == "__main__":
    main()
