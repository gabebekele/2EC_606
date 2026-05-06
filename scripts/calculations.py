from copy import deepcopy
from haversine import haversine, Unit


def is_valid_schedule(schedule, num_teams=20):
    """
    schedule:
        dict[int, list[tuple[int, int]]]
        week -> list of (home_team_id, away_team_id)

    Returns:
        (bool, str)
    """
    teams = set(range(1, num_teams + 1))

    # Track totals
    home_counts = {team: 0 for team in teams}
    away_counts = {team: 0 for team in teams}
    pair_counts = {}  # frozenset({a,b}) -> total meetings
    directed_counts = {}  # (home, away) -> count

    expected_weeks = set(range(1, 39))
    if set(schedule.keys()) != expected_weeks:
        return False, "Schedule must contain exactly weeks 1 through 38."

    for week in range(1, 39):
        matches = schedule[week]

        if len(matches) != 10:
            return False, f"Week {week} must have exactly 10 matches."

        used_this_week = set()

        for home, away in matches:
            if home == away:
                return False, f"Week {week}: team {home} cannot play itself."

            if home not in teams or away not in teams:
                return False, f"Week {week}: invalid team id in match ({home}, {away})."

            if home in used_this_week or away in used_this_week:
                return False, f"Week {week}: a team appears more than once."

            used_this_week.add(home)
            used_this_week.add(away)

            home_counts[home] += 1
            away_counts[away] += 1

            undirected = frozenset((home, away))
            pair_counts[undirected] = pair_counts.get(undirected, 0) + 1
            directed_counts[(home, away)] = directed_counts.get((home, away), 0) + 1

    # Each team: 19 home, 19 away
    for team in teams:
        if home_counts[team] != 19:
            return False, f"Team {team} has {home_counts[team]} home games, not 19."
        if away_counts[team] != 19:
            return False, f"Team {team} has {away_counts[team]} away games, not 19."

    # Each pair must meet exactly twice
    expected_num_pairs = num_teams * (num_teams - 1) // 2
    if len(pair_counts) != expected_num_pairs:
        return False, "Not all team pairs are represented exactly once in the pair map."

    for pair, count in pair_counts.items():
        if count != 2:
            return False, f"Pair {sorted(pair)} plays {count} times instead of 2."

    # Each directed matchup must happen at most once
    for matchup, count in directed_counts.items():
        if count != 1:
            return False, f"Matchup {matchup} occurs {count} times instead of 1."

    return True, "Schedule is valid."


def build_team_weekly_schedule(schedule, num_teams=20):
    """
    Converts league schedule into per-team weekly schedule.

    Returns:
        dict[int, list[tuple[int, int, bool]]]
        team_id -> [(week, opponent_id, is_home), ...]
    """
    team_schedule = {team: [] for team in range(1, num_teams + 1)}

    for week in range(1, 39):
        for home, away in schedule[week]:
            team_schedule[home].append((week, away, True))
            team_schedule[away].append((week, home, False))

    for team in team_schedule:
        team_schedule[team].sort(key=lambda x: x[0])

    return team_schedule


def team_travel_cost(team_id, schedule, teams):
    """
    Travel rule:
    - Start at home stadium.
    - If away: travel to opponent stadium.
    - If consecutive away games: go directly from previous away stadium to next away stadium.
    - If a home game happens after an away game: return home before that home game.
    - If the final game is away: return home after the season.

    teams:
        dict[int, {"coords": (lat, lon), ...}]
    """
    weekly = build_team_weekly_schedule(schedule)[team_id]
    home_coords = teams[team_id]["coords"]

    total = 0.0
    current_location = home_coords
    currently_away = False

    for _, opponent_id, is_home in weekly:
        if is_home:
            if currently_away:
                total += haversine(current_location, home_coords, unit=Unit.KILOMETERS)
                current_location = home_coords
                currently_away = False
        else:
            opponent_coords = teams[opponent_id]["coords"]
            total += haversine(current_location, opponent_coords, unit=Unit.KILOMETERS)
            current_location = opponent_coords
            currently_away = True

    if currently_away:
        total += haversine(current_location, home_coords, unit=Unit.KILOMETERS)

    return total


def league_travel_cost(schedule, teams):
    """
    Sum of all team travel costs.
    """
    return sum(team_travel_cost(team_id, schedule, teams) for team_id in teams)


def team_travel_breakdown(team_id, schedule, teams):
    """
    Optional helper for debugging / reporting.
    Returns a readable travel log for one team.
    """
    weekly = build_team_weekly_schedule(schedule)[team_id]
    home_coords = teams[team_id]["coords"]
    home_name = teams[team_id]["name"]

    total = 0.0
    current_location = home_coords
    current_label = f"{home_name} Home"
    currently_away = False
    legs = []

    for week, opponent_id, is_home in weekly:
        opponent_name = teams[opponent_id]["name"]
        opponent_coords = teams[opponent_id]["coords"]

        if is_home:
            if currently_away:
                dist = haversine(current_location, home_coords, unit=Unit.KILOMETERS)
                total += dist
                legs.append((week, current_label, f"{home_name} Home", round(dist, 2)))
                current_location = home_coords
                current_label = f"{home_name} Home"
                currently_away = False
        else:
            dist = haversine(current_location, opponent_coords, unit=Unit.KILOMETERS)
            total += dist
            legs.append((week, current_label, opponent_name, round(dist, 2)))
            current_location = opponent_coords
            current_label = opponent_name
            currently_away = True

    if currently_away:
        dist = haversine(current_location, home_coords, unit=Unit.KILOMETERS)
        total += dist
        legs.append((39, current_label, f"{home_name} Home", round(dist, 2)))

    return {
        "team": home_name,
        "total_km": round(total, 2),
        "legs": legs,
    }


def propose_swap(schedule, week1, match_idx1, week2, match_idx2):
    """
    Swap two matches between two weeks.
    Returns a NEW schedule.
    """
    new_schedule = deepcopy(schedule)
    new_schedule[week1][match_idx1], new_schedule[week2][match_idx2] = (
        new_schedule[week2][match_idx2],
        new_schedule[week1][match_idx1],
    )
    return new_schedule

def can_swap(schedule, week1, match_idx1, week2, match_idx2):
    match1 = schedule[week1][match_idx1]
    match2 = schedule[week2][match_idx2]

    teams_match1 = set(match1)
    teams_match2 = set(match2)

    # Teams already used in week1, excluding match1
    week1_teams = set()
    for i, match in enumerate(schedule[week1]):
        if i != match_idx1:
            week1_teams.update(match)

    # Teams already used in week2, excluding match2
    week2_teams = set()
    for i, match in enumerate(schedule[week2]):
        if i != match_idx2:
            week2_teams.update(match)

    # match2 must be allowed to move into week1
    if teams_match2 & week1_teams:
        return False

    # match1 must be allowed to move into week2
    if teams_match1 & week2_teams:
        return False

    return True


def optimize_schedule(schedule, teams, iterations=5000, seed=None):
    import random

    if seed is not None:
        random.seed(seed)

    best_schedule = deepcopy(schedule)

    valid, msg = is_valid_schedule(best_schedule, num_teams=len(teams))
    if not valid:
        raise ValueError(f"Initial schedule is invalid: {msg}")

    best_cost = league_travel_cost(best_schedule, teams)
    accepted_swaps = 0
    tested_swaps = 0

    for _ in range(iterations):
        w1, w2 = random.sample(range(1, 39), 2)

        i1 = random.randrange(len(best_schedule[w1]))
        i2 = random.randrange(len(best_schedule[w2]))

        if not can_swap(best_schedule, w1, i1, w2, i2):
            continue

        tested_swaps += 1

        candidate = propose_swap(best_schedule, w1, i1, w2, i2)

        valid, _ = is_valid_schedule(candidate, num_teams=len(teams))
        if not valid:
            continue

        candidate_cost = league_travel_cost(candidate, teams)

        if candidate_cost < best_cost:
            best_schedule = candidate
            best_cost = candidate_cost
            accepted_swaps += 1

    return best_schedule, best_cost, accepted_swaps, tested_swaps