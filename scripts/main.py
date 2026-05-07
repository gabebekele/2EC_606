import os
import matplotlib.pyplot as plt
from data import teams, schedule
from metrics import print_league_summary, get_team_results, print_additional_results
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

def print_results_table(results):
    print("\nTeam Travel Comparison")
    print("-" * 80)
    print(f"{'Team':25} {'Original km':>12} {'Optimized km':>14} {'Improvement':>16}")
    print("-" * 80)

    for name, original, optimized, improvement in results:
        print(
            f"{name:25} "
            f"{round(original, 2):>12} "
            f"{round(optimized, 2):>14} "
            f"{round(improvement, 2):>16}"
        )

    print("-" * 80)

def plot_team_improvement(results):
    os.makedirs("results", exist_ok=True)

    names = [row[0] for row in results]
    improvements = [row[3] for row in results]

    plt.figure(figsize=(14, 7))
    plt.bar(names, improvements)
    plt.axhline(0)
    plt.xticks(rotation=75, ha="right")
    plt.ylabel("Travel Reduction (km)")
    plt.title("Travel Improvement by Team After Optimization")
    plt.tight_layout()

    plt.savefig("results/team_improvement.png", dpi=300)
    plt.close()

def main():
    # Used to initialize data
    valid, message = is_valid_schedule(schedule)
    print(message)
    if not valid:
        debug_week(schedule, 38)
        return

    initial_cost = league_travel_cost(schedule, teams)

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

    results = get_team_results(
        schedule,
        best_schedule,
        teams,
        team_travel_cost
    )

    print_additional_results(results)

    print_results_table(results)
    plot_team_improvement(results)

    print("\nPlot saved: results/team_improvement.png")

    

if __name__ == "__main__":
    main()