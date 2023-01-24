IS_TEST = False
DIR = '/Users/luis/Git/relative-age-effect/src/blender/'
FONT_DIR = '/Users/luis/Library/CloudStorage/GoogleDrive-luis.s.calejo@gmail.com/My Drive/Memeable Data/Fonts/roboto/Roboto-Regular.ttf'


# Stage 1: text labels moving; stage 2: players falling; stage 3: players walking; stage 4: players looking up
STAGE1_START = 10
STAGE1_END = 130
STAGE1_PLAYER_Z = 35
STAGE2_START = 140
STAGE2_RANDOM = 5  # randomness interval in frames of players falling
STAGE2_ROW_INTERVAL = 15 # interval in nr of frames between each row of players falling
STAGE2_FALL_TIME = 60  # time in frames for players falling
STAGE3_START = 400
STAGE3_RANDOM = 60  # randomness interval in frames until players start walking
STAGE3_ROTATE_TIME = 15  # time in frames that players take to rotate until target
STAGE3_PLAYER_SPEED = 10  # Avg walking speed in meters/second
STAGE4_START = 1200
STAGE4_END = 1400
STAGE4_RANDOM = 120  # randomness interval in frames until players look up
RANDOM_SEED = 1
FPS = 60




STAGE1_TEXT_Y = -30


START_MARGIN_HOR = 6
START_PLAYER_SPACING_HOR = 1
START_PLAYER_SPACING_VER = 1
START_PLAYERS_PER_ROW = 10
START_TEAMS_PER_ROW = 4
START_TEAM_SPACING_HOR = 12
START_TEAM_SPACING_VER = 7
START_TEAM_TEXT_MARGIN = 1.5
END_PLAYER_SPACING_HOR = 0.75
END_PLAYER_SPACING_VER = 0.5
END_PLAYERS_PER_ROW = 3
END_MONTH_SPACING_HOR = 3
END_CHART_MARGIN_VER = -1.5

# This script requires that every team is mapped to an already existing blender model:
TEAM_BLENDER_OBJECT = {
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
        subprocess.call([python_exe, "-m", "pip", "install", "random"])


    def unselect_all_objects():
        for obj in bpy.context.selected_objects:
            obj.select_set(False)  # deselect all objects


    # def insert_and_change_text(coordinates, label, label_name):
    #     bpy.ops.object.text_add(location=coordinates, enter_editmode=True, name=label_name)
    #     for k in range(4):
    #         bpy.ops.font.delete(type='PREVIOUS_OR_SELECTION')
    #     for char in label:
    #         bpy.ops.font.text_insert(text=char)
    #     bpy.ops.object.editmode_toggle()

    def insert_and_change_text(coordinates, label, label_name):
        text_data = bpy.data.curves.new(name=label_name, type='FONT')
        text_object = bpy.data.objects.new(name=label_name, object_data=text_data)
        text_object.location = coordinates
        bpy.context.scene.collection.objects.link(text_object)
        bpy.context.view_layer.objects.active = text_object
        bpy.ops.object.editmode_toggle()
        for k in range(4):
            bpy.ops.font.delete(type='PREVIOUS_OR_SELECTION')
        for char in label:
            bpy.ops.font.text_insert(text=char)
        bpy.ops.object.editmode_toggle()

    def newMaterial(id):
        mat = bpy.data.materials.get(id)
        if mat is None:
            mat = bpy.data.materials.new(name=id)
        mat.use_nodes = True
        if mat.node_tree:
            mat.node_tree.links.clear()
            mat.node_tree.nodes.clear()
        return mat


    def newShader(id, type, r, g, b):
        mat = newMaterial(id)
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        output = nodes.new(type='ShaderNodeOutputMaterial')
        if type == "diffuse":
            shader = nodes.new(type='ShaderNodeBsdfDiffuse')
            nodes["Diffuse BSDF"].inputs[0].default_value = (r, g, b, 1)
        elif type == "emission":
            shader = nodes.new(type='ShaderNodeEmission')
            nodes["Emission"].inputs[0].default_value = (r, g, b, 1)
            nodes["Emission"].inputs[1].default_value = 0.01
        elif type == "glossy":
            shader = nodes.new(type='ShaderNodeBsdfGlossy')
            nodes["Glossy BSDF"].inputs[0].default_value = (r, g, b, 1)
            nodes["Glossy BSDF"].inputs[1].default_value = 0
        links.new(shader.outputs[0], output.inputs[0])
        return mat


    def update_fonts(font_dir):
        # Iterate through all the text objects
        for obj in bpy.data.objects:
            if obj.type == 'FONT':
                # Change the font
                obj.data.font = bpy.data.fonts.load(font_dir)

import pandas as pd
import math
import random


def calculate_travel_time(start, end, speed):
    distance = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
    time = round(distance / speed)
    return time


# Process data from CSV file:
random.seed(RANDOM_SEED)
df = pd.read_csv(DIR + '../../data/premier_league.csv')
df['player_id'] = df.apply(lambda x: x['name'] + '_' + x['club'], axis=1)
player_team = dict(zip(df['player_id'], df['club']))
month_count = df[['month_number', 'player_id']].groupby(['month_number']).count().reset_index()
month_players = dict(zip(month_count['month_number'], [[] for x in month_count['month_number']]))
month_label = dict(zip(df['month_number'], df['month']))
month_label_name = dict(zip(df['month_number'], ['Text Month ' + x for x in df['month']]))
months = month_players.keys()
team_players = dict(zip(df['club'].unique(), [[] for x in df['club'].unique()]))
team_label_name = dict(zip(df['club'].unique(), ['Text Team ' + x for x in df['club'].unique()]))
teams = team_players.keys()
for index, row in df.iterrows():
    month_players[row['month_number']].append(row['player_id'])
    team_players[row['club']].append(row['player_id'])

# Find starting positions of players and text labels:
player_coordinates_stage2 = dict()
player_coordinates_stage3 = dict()
team_text_coordinates = dict()
team_row = dict()
month_text_coordinates = dict()
counter_team = 0
for team in teams:
    counter_team += 1
    counter_player = 0
    
    row_team = math.floor((counter_team - 1) / START_TEAMS_PER_ROW) + 1
    team_row[team] = row_team
    col_team = counter_team - math.floor((counter_team - 1) / START_TEAMS_PER_ROW) * START_TEAMS_PER_ROW
    team_text_coordinates[team] = ((col_team - 1) * START_TEAM_SPACING_HOR + START_PLAYER_SPACING_HOR,
                                   (row_team - 1) * START_TEAM_SPACING_VER - START_TEAM_TEXT_MARGIN, 0)
    for player in team_players[team]:
        counter_player += 1
        row = math.floor((counter_player - 1) / START_PLAYERS_PER_ROW) + 1
        col = counter_player - math.floor((counter_player - 1) / START_PLAYERS_PER_ROW) * START_PLAYERS_PER_ROW
        row_team = math.floor((counter_team - 1) / START_TEAMS_PER_ROW) + 1
        col_team = counter_team - math.floor((counter_team - 1) / START_TEAMS_PER_ROW) * START_TEAMS_PER_ROW
        player_coordinates_stage2[player] = (
            (col_team - 1) * START_TEAM_SPACING_HOR + col * START_PLAYER_SPACING_HOR,
            (row_team - 1) * START_TEAM_SPACING_VER + (row - 1) * START_PLAYER_SPACING_VER,
            STAGE1_PLAYER_Z
        )
        player_coordinates_stage3[player] = (
            player_coordinates_stage2[player][0],
            player_coordinates_stage2[player][1],
            0
        )

# Find ending positions of players:
player_coordinates_stage4 = dict()
counter_month = 0
for month in months:
    counter_month += 1
    counter_player = 0
    month_text_coordinates[month] = (
        (counter_month - 1) * END_MONTH_SPACING_HOR + END_PLAYER_SPACING_HOR,
        END_CHART_MARGIN_VER,
        0
    )
    for player in month_players[month]:
        counter_player += 1
        row = math.floor((counter_player - 1) / END_PLAYERS_PER_ROW) + 1
        col = counter_player - math.floor((counter_player - 1) / END_PLAYERS_PER_ROW) * END_PLAYERS_PER_ROW
        player_coordinates_stage4[player] = (
            (counter_month - 1) * END_MONTH_SPACING_HOR + col * END_PLAYER_SPACING_HOR,
            (row - 1) * END_PLAYER_SPACING_VER,
            0
        )

if IS_TEST:
    import matplotlib.pyplot as plt
    x = [player_coordinates_stage3[x][0] for x in df['player_id']]
    y = [player_coordinates_stage3[x][1] for x in df['player_id']]
    # x = [player_coordinates_stage4[x][0] for x in df['player_id']]
    # y = [player_coordinates_stage4[x][1] for x in df['player_id']]
    plt.scatter(x, y, c="blue")
else:
    # Delete existing objects:
    unselect_all_objects()
    for player in player_team.keys():
        if player in bpy.data.objects:
            bpy.data.objects[player].select_set(True)
            bpy.ops.object.delete(use_global=False, confirm=False)
    for team in teams:
        if team_label_name[team] in bpy.data.objects:
            bpy.data.objects[team_label_name[team]].select_set(True)
            bpy.ops.object.delete(use_global=False, confirm=False)
    for month in months:
        if month_label_name[month] in bpy.data.objects:
            bpy.data.objects[month_label_name[month]].select_set(True)
            bpy.ops.object.delete(use_global=False, confirm=False)

    # Generate team text labels:
    for team in teams:
        insert_and_change_text(team_text_coordinates[team], team, team_label_name[team])
        mat = newShader("Text Material", "emission", 255, 255, 255)
        bpy.context.active_object.data.materials.append(mat)

    # Generate players and chart labels:
    for month in months:
        insert_and_change_text(month_text_coordinates[month], month_label[month], month_label_name[month])
        mat = newShader("Text Material", "emission", 255, 255, 255)
        bpy.context.active_object.data.materials.append(mat)
        for player in month_players[month]:
            for obj in bpy.context.selected_objects:
                obj.select_set(False)  # deselect all objects
            bpy.data.objects[TEAM_BLENDER_OBJECT[player_team[player]]].select_set(True)
            bpy.ops.object.duplicate(linked=False)
            bpy.data.objects[TEAM_BLENDER_OBJECT[player_team[player]]].select_set(False)
            for obj in bpy.context.selected_objects:
                obj.name = player
                # Stage 2: Falling
                obj.location[0] = player_coordinates_stage2[player][0]
                obj.location[1] = player_coordinates_stage2[player][1]
                obj.location[2] = player_coordinates_stage2[player][2]
                frame_start_falling = STAGE2_START + random.randint(0,STAGE2_RANDOM) + team_row[player_team[player]]*STAGE2_ROW_INTERVAL
                frame_end_falling = frame_start_falling + STAGE2_FALL_TIME
                obj.keyframe_insert(data_path="location", index=-1, frame=frame_start_falling)
                obj.location[0] = player_coordinates_stage3[player][0]
                obj.location[1] = player_coordinates_stage3[player][1]
                obj.location[2] = player_coordinates_stage3[player][2]
                obj.keyframe_insert(data_path="location", index=-1, frame=frame_end_falling)
                frame_start_spinning = STAGE3_START+random.randint(0, STAGE3_RANDOM)
                frame_start_walking = frame_start_spinning + STAGE3_ROTATE_TIME
                frame_end_walking = frame_start_walking + FPS * calculate_travel_time(player_coordinates_stage3[player], player_coordinates_stage4[player], STAGE3_PLAYER_SPEED)
                obj.keyframe_insert(data_path="location", index=-1, frame=STAGE3_START)
                obj.keyframe_insert(data_path="location", index=-1, frame=frame_start_walking)
                # (!!) insert spinning!
                obj.location[0] = player_coordinates_stage4[player][0]
                obj.location[1] = player_coordinates_stage4[player][1]
                obj.keyframe_insert(data_path="location", index=-1, frame=frame_end_walking)
                # (!!) insert spinning
    #Update fonts:
    update_fonts(FONT_DIR)

print("END")
