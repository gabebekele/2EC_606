## Overview
Professional sports leagues like the English Premier League require teams to travel frequently throughout a season, leading to significant logistical costs, fatigue, and performance impacts. While schedules are designed primarily for fairness and broadcasting considerations, they are not necessarily optimized for travel efficiency. This project aims to model the league schedule as a graph problem and analyze whether the total travel distance across all teams can be reduced, while maintaining schedule requirements.

## Problem Statement


> ### Can the Premier League schedule be adjusted to reduce total team travel while still satisfying the basic league scheduling rules?

This is modeled as a scheduling optimization problem. Each team’s stadium is treated as a location, and travel between stadiums is measured using geographic distance.

The optimizer attempts to improve the schedule by swapping matches between weeks while preserving league constraints.

## Dataset

The dataset was manually constructed from the current Premier League season schedule.

Each team includes:

- Team name
- Unique team ID from 1 to 20
- Stadium coordinates as latitude and longitude
- A list of 38 opponents, one for each matchweek
- A list of matchweeks where the team plays away

The full league schedule is reconstructed from this data as:

```python
schedule = {
    1: [(home_team_id, away_team_id), ...],
    2: [(home_team_id, away_team_id), ...],
    ...
    38: [(home_team_id, away_team_id), ...]
}
```

## Graph Representation

The league is modeled as a weighted graph:

- **Nodes** represent teams/stadiums
- **Edges** represent travel between stadiums
- **Edge weights** represent distance in kilometers

Each team’s season can be viewed as a path through this graph. If a team plays consecutive away games, it travels directly from one away stadium to the next. If a team has a home game, it returns to its home stadium.

---

## Algorithm

This project uses a **hill-climbing heuristic** that repeatedly tries small changes and keeps a change only if it improves the result.

### Steps

1. Start with the valid current Premier League schedule
2. Compute total league travel distance
3. Randomly choose two matches from different weeks
4. Check whether the swap keeps both weeks valid
5. Swap the matches
6. Recompute total league travel
7. Keep the swap only if it lowers total travel
8. Repeat for a fixed number of iterations

Because this is a difficult combinatorial scheduling problem, the goal is not to prove a perfect global optimum, but instead to find a better schedule using an approximate method.

---

## Scheduling Constraints

A schedule is valid only if:

- There are exactly 38 matchweeks
- Each matchweek has exactly 10 matches
- No team plays more than once in the same week
- Each team plays 38 total matches
- Each team has 19 home games and 19 away games
- Every pair of teams plays exactly twice
- Each pair has one home matchup and one away matchup

---

## Travel Model

Travel is calculated using the Haversine formula, which estimates the distance between two latitude/longitude coordinates.

### Travel Rules

- Teams start at their home stadium
- For an away match, the team travels to the opponent’s stadium
- For consecutive away matches, the team travels directly from the previous away stadium to the next away stadium
- Before a home match, the team returns to its home stadium
- If the last match is away, the team returns home to conclude the season

---

## Results

Using a fixed random seed for reproducibility, the optimizer found a valid schedule with lower total league travel.

### Example Output

```text
Initial league travel: 133815.87 km
Optimized league travel: 121776.57 km
Total improvement: 12039.29 km
Percent improvement: 9.0 %
Accepted swaps: 19

Additional Results:
Teams improved: 17
Teams worsened: 0
Teams unchanged: 3 

Biggest improvement: Newcastle United 3203.85 km
Biggest travel increase: Brighton 0.0 km
Average team travel before: 6690.79 km
Average team travel after: 6088.83 km


Team Travel Comparison
--------------------------------------------------------------------------------
Team                       Original km   Optimized km      Improvement
--------------------------------------------------------------------------------
Newcastle United               9674.46        6470.61          3203.85
Bournemouth                    8232.59        6639.84          1592.75
Everton                        6731.01        5296.94          1434.08
Arsenal                        5904.34        4746.67          1157.67
Leeds                          6419.17        5684.45           734.72
Burnley                        6629.91        5991.53           638.38
Chelsea                        6380.07        5771.27            608.8
West Ham                       6516.73        6040.85           475.89
Wolves                         5406.46        5007.34           399.12
Brentford                       6038.1        5678.48           359.62
Sunderland                     9193.48        8855.79           337.69
Fulham                         5867.82        5554.83           312.98
Nottingham Forest              5757.17        5453.59           303.58
Tottenham                      6083.37        5797.45           285.92
Aston Villa                    5392.71        5289.69           103.02
Manchester United              6352.96        6272.08            80.88
Manchester City                6495.18        6484.82            10.36
Brighton                       8035.79        8035.79              0.0
Crystal Palace                 6589.55        6589.55              0.0
Liverpool                      6114.99        6114.99              0.0
--------------------------------------------------------------------------------
```

This means the hill-climbing optimizer reduced estimated total league travel by about 12,039 km while maintaining a valid schedule. The results show that even a simple heuristic can find meaningful improvements in a real-world scheduling problem.

## Evaluation Metrics

- Initial league travel distance
- Optimized league travel distance
- Total improvement in kilometers
- Percent improvement
- Number of accepted swaps
- Team-by-team travel before and after optimization
- Biggest team improvements
- Teams that improved, worsened, or stayed the same
- Plot of travel improvement by team

## Files

#### scripts/data.py
Contains the team data, stadium coordinates, fixtures, away weeks, and reconstructed schedule.

#### scripts/calculations.py
Contains the schedule validation logic, travel cost functions, swap logic, and hill-climbing optimizer.
#### scripts/main.py
Runs the project, validates the schedule, computes baseline travel, runs the optimizer, prints results, and creates the results plot.
#### results/team_improvement.png
A bar chart showing how each team’s travel changed after optimization.


## How to Run
### 1. Clone the repository

git clone https://github.com/gabebekele/2EC_606.git

cd 2EC_606

### 2. Install dependencies

pip install -r requirements.txt
### 3. Run the project

python scripts/main.py


No AI or resources other than the Premier league site for scheduling as well as google maps for stadium coordinates were used in this submission.