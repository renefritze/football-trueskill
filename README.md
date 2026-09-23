# football-trueskill
compare league placements with classical scoring vs. TrueSkill(tm)

CSV match data courtesy of http://football-data.co.uk/

## Usage

Requires [uv](https://docs.astral.sh/uv/).

```sh
uv run football-trueskill                                   # defaults to data/german_bundesliga/2016.csv
uv run football-trueskill data/german_bundesliga/2015.csv
```

## Development

```sh
uv sync                      # create .venv with runtime + dev dependencies from uv.lock
uv run pre-commit install    # run ruff, ty and friends on every commit
uv run pytest
uv run ruff check . && uv run ruff format .
uv run ty check
```
