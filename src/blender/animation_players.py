IS_TEST = False
DIR = '/Users/luis/Git/relative-age-effect/src/blender/'
PLAYER_SPACING_HOR = 0.75
PLAYER_SPACING_VER = 0.5
PLAYERS_PER_ROW_MONTH = 3
COL_SPACING_MONTH = 3
CLUB_OBJECT = {
    'Manchester City': '0. Player Manchester City',
    'Chelsea FC': '0. Player Chelsea FC',
    'Liverpool FC': '0. Player Liverpool FC',
    'Arsenal FC': '0. Player Arsenal FC',
    'Manchester United': '0. Player Manchester United',
    'Tottenham Hotspur': '0. Player Tottenham Hotspur',
    'Aston Villa': '0. Player Aston Villa',
    'West Ham United': '0. Player West Ham United',
    'Newcastle United': '0. Player Newcastle United',
    'Leicester City': '0. Player Leicester City',
    'Wolverhampton Wanderers': '0. Player Wolverhampton Wanderers',
    'Everton FC': '0. Player Everton FC',
    'Brighton & Hove Albion': '0. Player Brighton & Hove Albion',
    'Southampton FC': '0. Player Southampton FC',
    'Brentford FC': '0. Player Brentford FC',
    'Nottingham Forest': '0. Player Nottingham Forest',
    'Leeds United': '0. Player Leeds United',
    'Crystal Palace': '0. Player Crystal Palace',
    'Fulham FC': '0. Player Fulham FC',
    'AFC Bournemouth': '0. Player AFC Bournemouth'
}

if not IS_TEST:
    import sys
    import subprocess
    import os
    import bpy

    # Install packages into Blender:
    def python_exec():
        import os
        import bpy
        try:
            # 2.92 and older
            path = bpy.app.binary_path_python
        except AttributeError:
            # 2.93 and later
            import sys
            path = sys.executable
        return os.path.abspath(path)

    try:
        from pandas import read_csv
    except:
        python_exe = python_exec()
        # upgrade pip
        subprocess.call([python_exe, "-m", "ensurepip"])
        subprocess.call([python_exe, "-m", "pip", "install", "--upgrade", "pip"])
        # install required packages
        subprocess.call([python_exe, "-m", "pip", "install", "pandas"])
        subprocess.call([python_exe, "-m", "pip", "install", "math"])


import pandas as pd
import math

# Process data from CSV file:
df = pd.read_csv(DIR+'../../data/premier_league.csv')
df['player_id'] = df.apply(lambda x: x['name'] + '_' + x['club'], axis=1)
player_club = dict(zip(df['player_id'], df['club']))
player_coordinates_start = dict()
player_coordinates_end = dict()
month_count = df[['month_number', 'player_id']].groupby(['month_number']).count().reset_index()
month_players = dict(zip(month_count['month_number'], [[] for x in month_count['month_number']]))
for index, row in df.iterrows():
    month_players[row['month_number']].append(row['player_id'])

# Find players' starting position:


# Find players' ending positions:
counter_month = 0
for month in month_players.keys():
    counter_month += 1
    counter_player = 0
    for player in month_players[month]:
        counter_player += 1
        row = math.floor((counter_player - 1) / PLAYERS_PER_ROW_MONTH) + 1
        col = counter_player - math.floor((counter_player - 1) / PLAYERS_PER_ROW_MONTH) * PLAYERS_PER_ROW_MONTH
        player_coordinates_end[player] = (
            (counter_month - 1) * COL_SPACING_MONTH + col * PLAYER_SPACING_HOR, (row - 1) * PLAYER_SPACING_VER)


if IS_TEST:
    import matplotlib.pyplot as plt
    # x = [player_coordinates_start[x][0] for x in df['player_id']]
    # y = [player_coordinates_start[x][1] for x in df['player_id']]
    x = [player_coordinates_end[x][0] for x in df['player_id']]
    y = [player_coordinates_end[x][1] for x in df['player_id']]
    plt.scatter(x, y, c="blue")
else:
    for month in month_players.keys():
        for player in month_players[month]:
            for obj in bpy.context.selected_objects:
                obj.select_set(False)  # deselect all objects
            bpy.data.objects[CLUB_OBJECT[player_club[player]]].select_set(True)
            bpy.ops.object.duplicate(linked=False)
            bpy.data.objects[CLUB_OBJECT[player_club[player]]].select_set(False)
            for obj in bpy.context.selected_objects:
                obj.name = player
                obj.location[0] = player_coordinates_end[player][0]
                obj.location[1] = player_coordinates_end[player][1]

print("END")
