from pathlib import Path

from football_trueskill.skill import ClassicRanking, main

DATA = Path(__file__).parent.parent / "data" / "german_bundesliga"


def test_classic_scoring() -> None:
    r = ClassicRanking()
    r.score_game(2, 1)
    r.score_game(1, 1)
    r.score_game(0, 3)
    assert (r.points, r.goals_scored, r.goals_conceded, r.goal_diff) == (4, 3, 5, -2)


def test_classic_ordering() -> None:
    a, b = ClassicRanking(), ClassicRanking()
    a.score_game(3, 0)
    b.score_game(1, 0)
    assert b < a
    assert not a < b


def test_main_prints_table(capsys) -> None:
    main([str(DATA / "2016.csv")])
    out = capsys.readouterr().out
    assert "TrueSkill" in out
    assert "Bayern Munich" in out
    assert "18." in out
