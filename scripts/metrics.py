def print_league_summary(initial_cost, best_cost, accepted_swaps, tested_swaps):
    improvement = initial_cost - best_cost
    percent_improvement = (improvement / initial_cost) * 100 if initial_cost else 0

    print("\nLeague Travel Summary")
    print("-" * 80)

    print("Initial league travel:", round(initial_cost, 2), "km")
    print("Optimized league travel:", round(best_cost, 2), "km")
    print("Total improvement:", round(improvement, 2), "km")
    print("Percent improvement:", round(percent_improvement, 2), "%")
    print("Accepted swaps:", accepted_swaps)

def get_team_results(schedule, best_schedule, teams, team_travel_cost):
    results = []

    for team_id in teams:
        original = team_travel_cost(team_id, schedule, teams)
        optimized = team_travel_cost(team_id, best_schedule, teams)
        improvement = original - optimized

        results.append((
            teams[team_id]["name"],
            original,
            optimized,
            improvement
        ))

    results.sort(key=lambda x: x[3], reverse=True)
    return results

# used to determine which random seed would perform well (selected 0)
def run_seed_experiment(schedule, teams, optimize_schedule, num_seeds=50, iterations=5000):
    best_result = None

    for seed in range(num_seeds):
        best_schedule, best_cost, accepted_swaps, tested_swaps = optimize_schedule(
            schedule,
            teams,
            iterations=iterations,
            seed=seed
        )

        if best_result is None or best_cost < best_result["best_cost"]:
            best_result = {
                "seed": seed,
                "best_schedule": best_schedule,
                "best_cost": best_cost,
                "accepted_swaps": accepted_swaps,
                "tested_swaps": tested_swaps
            }

    return best_result


def print_additional_results(results):
    improved = sum(1 for _, _, _, improvement in results if improvement > 0)
    worsened = sum(1 for _, _, _, improvement in results if improvement < 0)
    unchanged = sum(1 for _, _, _, improvement in results if improvement == 0)

    print("\nAdditional Results:")
    print("Teams improved:", improved)
    print("Teams worsened:", worsened)
    print("Teams unchanged:", unchanged,"\n")

    best_team = max(results, key=lambda x: x[3])
    worst_team = min(results, key=lambda x: x[3])

    print("Biggest improvement:", best_team[0], round(best_team[3], 2), "km")
    print("Biggest travel increase:", worst_team[0], round(worst_team[3], 2), "km")

    original_values = [original for _, original, _, _ in results]
    optimized_values = [optimized for _, _, optimized, _ in results]

    avg_original = sum(original_values) / len(original_values)
    avg_optimized = sum(optimized_values) / len(optimized_values)

    print("Average team travel before:", round(avg_original, 2), "km")
    print("Average team travel after:", round(avg_optimized, 2), "km\n")