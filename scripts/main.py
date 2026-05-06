from data import teams, schedule
from metrics import print_league_summary, print_team_comparison, run_seed_experiment, print_additional_results
from calculations import (
    is_valid_schedule,
    league_travel_cost,
    team_travel_cost,
    optimize_schedule
)

# used to fix initial data
def debug_week(schedule, week):
    print(f"\nWeek {week} matches:")
    seen = {}

    for match in schedule[week]:
        home, away = match
        print(match)

        for team in match:
            if team in seen:
                print(f"Duplicate team found: {team}")
                print(f"Previous match: {seen[team]}")
                print(f"Current match: {match}")
            else:
                seen[team] = match

def main():
    valid, message = is_valid_schedule(schedule)
    print("Schedule valid:", valid)
    print(message)

    if not valid:
        debug_week(schedule, 38)
        return

    initial_cost = league_travel_cost(schedule, teams)
    print("Initial league travel:", round(initial_cost, 2), "km")

    best_schedule, best_cost, accepted_swaps, tested_swaps = optimize_schedule(
        schedule,
        teams,
        iterations=5000,
        seed=0
    )

    print_league_summary(
        initial_cost,
        best_cost,
        accepted_swaps,
        tested_swaps
    )

    results = print_team_comparison(
        schedule,
        best_schedule,
        teams,
        team_travel_cost
    )

    print_additional_results(results)

if __name__ == "__main__":
    main()