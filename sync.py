"""
WNBA box score sync -> JSON file. No database required.

Run this on your own machine whenever you want fresh numbers:
    pip install nba_api
    python sync.py

It writes data/dvp.json, which the Next.js app reads directly.
After running, commit + push data/dvp.json and Vercel will redeploy
with the updated numbers.
"""

import json
import time
from collections import defaultdict
from nba_api.stats.endpoints import leaguegamefinder, boxscoretraditionalv2, commonteamroster
from nba_api.stats.endpoints import leaguedashteamstats

WNBA_LEAGUE_ID = "10"
SEASON = "2026"


def get_team_map():
    """Numeric team_id -> abbreviation, pulled fresh each run."""
    teams = leaguedashteamstats.LeagueDashTeamStats(
        league_id_nullable=WNBA_LEAGUE_ID, season=SEASON
    ).get_data_frames()[0]
    return dict(zip(teams["TEAM_ID"].astype(str), teams["TEAM_ABBREVIATION"]))


def get_player_positions(team_ids):
    """player_id -> 'G'/'F'/'C', pulled from each team's roster."""
    positions = {}
    for team_id in team_ids:
        roster = commonteamroster.CommonTeamRoster(
            team_id=team_id, league_id_nullable=WNBA_LEAGUE_ID, season=SEASON
        ).get_data_frames()[0]
        for _, row in roster.iterrows():
            pos_raw = str(row["POSITION"]).upper()
            pos = "G" if "GUARD" in pos_raw else "F" if "FORWARD" in pos_raw else "C"
            positions[str(row["PLAYER_ID"])] = pos
        time.sleep(0.6)
    return positions


def main():
    team_map = get_team_map()
    positions = get_player_positions(team_map.keys())

    finder = leaguegamefinder.LeagueGameFinder(
        league_id_nullable=WNBA_LEAGUE_ID, season_nullable=SEASON
    )
    game_ids = finder.get_data_frames()[0]["GAME_ID"].unique()

    # raw[team_id][position] = list of stat-lines allowed against that team
    raw = defaultdict(lambda: defaultdict(list))

    for game_id in game_ids:
        box = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=game_id)
        player_stats = box.get_data_frames()[0]
        teams_in_game = player_stats["TEAM_ID"].astype(str).unique()

        for _, row in player_stats.iterrows():
            pid = str(row["PLAYER_ID"])
            if pid not in positions:
                continue
            own_team = str(row["TEAM_ID"])
            opp_team = next(t for t in teams_in_game if t != own_team)
            raw[opp_team][positions[pid]].append({
                "pts": row["PTS"] or 0,
                "reb": row["REB"] or 0,
                "ast": row["AST"] or 0,
                "stl": row["STL"] or 0,
                "blk": row["BLK"] or 0,
                "fg3m": row["FG3M"] or 0,
                "fgm": row["FGM"] or 0,
                "fga": row["FGA"] or 0,
            })
        time.sleep(0.6)

    result = {"G": [], "F": [], "C": []}
    for team_id, by_pos in raw.items():
        abbr = team_map.get(team_id, team_id)
        for pos in ["G", "F", "C"]:
            lines = by_pos.get(pos, [])
            if not lines:
                continue
            n = len(lines)
            fga_total = sum(l["fga"] for l in lines)
            fgm_total = sum(l["fgm"] for l in lines)
            result[pos].append({
                "team_id": abbr,
                "games_sampled": n,
                "pts_allowed": round(sum(l["pts"] for l in lines) / n, 1),
                "reb_allowed": round(sum(l["reb"] for l in lines) / n, 1),
                "ast_allowed": round(sum(l["ast"] for l in lines) / n, 1),
                "stl_allowed": round(sum(l["stl"] for l in lines) / n, 1),
                "blk_allowed": round(sum(l["blk"] for l in lines) / n, 1),
                "fg3m_allowed": round(sum(l["fg3m"] for l in lines) / n, 1),
                "fg_pct_allowed": round(100 * fgm_total / fga_total, 1) if fga_total else 0,
            })
        # sort each position list by points allowed, most to least
    for pos in result:
        result[pos].sort(key=lambda r: r["pts_allowed"], reverse=True)

    with open("data/dvp.json", "w") as f:
        json.dump(result, f, indent=2)

    print("Wrote data/dvp.json")


if __name__ == "__main__":
    main()
