IS_TEST = False
DIR = '/Users/luis/Git/relative-age-effect/src/blender/'
FONT_DIR = '/Users/luis/Library/CloudStorage/GoogleDrive-luis.s.calejo@gmail.com/My Drive/Memeable Data/Fonts/roboto/Roboto-Regular.ttf'


# Stage 1: camera moves (manually); stage 2: start players falling, months appear; stage 3: players start walking; stage 4: players looking up
RANDOM_SEED = 1
FPS = 60
STAGE2_START = 300
STAGE2_PLAYER_Z = 35  # height from which the players fall
STAGE2_RANDOM = 5  # randomness interval in frames of players falling
STAGE2_ROW_INTERVAL = 15 # interval in nr of frames between each row of players falling
STAGE2_FALL_TIME = 60  # time in frames for players falling
STAGE2_PLAYER_SPACING_X = 1
STAGE2_PLAYER_SPACING_Y = 1
STAGE2_PLAYERS_PER_ROW = 10
STAGE2_TEAMS_PER_ROW = 4
STAGE2_TEAM_SPACING_X = 12
STAGE2_TEAM_SPACING_Y = 7
STAGE2_TEAM_TEXT_MARGIN = 1.5
# STAGE2_MONTH_FRAME = 500  # frame where months appear
STAGE2_MONTH_DISTANCE = -20  # starting distance of month labels from chart
STAGE2_MONTH_WAIT = 150  # time for months to appear in position (since beginning of stage 2)
STAGE2_MONTH_DURATION = 120  # duration of month label animation
STAGE3_START = 760
STAGE3_RANDOM = 60  # randomness interval in frames until players start walking
STAGE3_ROTATE_SPEED = 3  # rotation speed in degrees/frame for players to rotate until target
STAGE3_PLAYER_SPEED = 10  # Avg walking speed in meters/second
STAGE3_TEXT_WAIT = 150 # Waiting time in nr of frames until team labels move away
STAGE4_START = 1200
STAGE4_TEXT_DISTANCE_Y = 70 # Distance in meters that the team labels move away from camera
STAGE4_CHART_X = 4
STAGE4_CHART_Y = -15
STAGE4_RANDOM = 120  # randomness interval in frames until players look up
STATE4_PLAYER_ROTATION_X = -15  # rotation in degrees for players looking up
STATE4_PLAYER_ROTATION_DURATION = 30  # duration in nr of frames for the players to look up
STAGE4_PLAYER_SPACING_X = 0.75
STAGE4_PLAYER_SPACING_Y = 0.5
STAGE4_PLAYERS_PER_ROW = 3
STAGE4_MONTH_SPACING_X = 3
STAGE4_TEXT_MARGIN_Y = -1.5

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
        subprocess.call([python_exe, "-m", "pip", "install", "numpy"])


    def unselect_all_objects():
        for obj in bpy.context.selected_objects:
            obj.select_set(False)  # deselect all objects


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

    def create_keyframe_position(object, frame, coordinates):
        unselect_all_objects()
        bpy.data.objects[object].select_set(True)
        for obj in bpy.context.selected_objects:
            obj.location[0] = coordinates[0]
            obj.location[1] = coordinates[1]
            obj.location[2] = coordinates[2]
            obj.keyframe_insert(data_path="location", index=-1, frame=frame)

    def create_keyframe_rotation(object, frame, rotation):
        unselect_all_objects()
        bpy.data.objects[object].select_set(True)
        for obj in bpy.context.selected_objects:
            obj.rotation_euler[0] = rotation[0]*math.pi/180
            obj.rotation_euler[1] = rotation[1]*math.pi/180
            obj.rotation_euler[2] = rotation[2]*math.pi/180
            obj.keyframe_insert(data_path="rotation_euler", index=-1, frame=frame)


    def rotation_until_target(coordinates_from, coordinates_to):
        vector1 = (0, -1, 0)
        vector2 = (coordinates_to[0] - coordinates_from[0], coordinates_to[1] - coordinates_from[1], 0)
        angle = angle_between_vectors(vector1, vector2)
        if vector1[0]>vector2[0]:
            angle = -angle
        return angle

    def unit_vector(vector):
        """ Returns the unit vector of the vector.  """
        return vector / np.linalg.norm(vector)


    def angle_between_vectors(v1, v2):
        v1_u = unit_vector(v1)
        v2_u = unit_vector(v2)
        angle_radians = np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))
        angle = angle_radians * (180/math.pi)
        return angle

    # def angles_between_points(coordinates_from, coordinates_to):
    #     # Calculate the difference vectors
    #     dx = coordinates_to[0] - coordinates_from[0]
    #     dy = coordinates_to[1] - coordinates_from[1]
    #     dz = coordinates_to[2] - coordinates_from[2]
    #     # Calculate the angles
    #     angle_x = math.degrees(math.atan2(dy, dz))
    #     angle_y = math.degrees(math.atan2(dx, dz))
    #     angle_z = math.degrees(math.atan2(dy, dx))
    #     return angle_x, angle_y, angle_z

    def walk_from_to(object, frame_start, coordinates_from, coordinates_to):
        unselect_all_objects()
        bpy.data.objects[object].select_set(True)
        angle = rotation_until_target(coordinates_from, coordinates_to)
        rotation_time = abs(angle / STAGE3_ROTATE_SPEED)
        frame_start_walking = frame_start + rotation_time
        frame_end_walking = frame_start_walking + FPS * calculate_travel_time(coordinates_from, coordinates_to, STAGE3_PLAYER_SPEED)
        for obj in bpy.context.selected_objects:
            rotation_start = (obj.rotation_euler[0], obj.rotation_euler[1], obj.rotation_euler[2])
            rotation_end = (obj.rotation_euler[0], obj.rotation_euler[1], obj.rotation_euler[2] + angle)
            create_keyframe_rotation(object, frame_start, rotation_start)
            create_keyframe_rotation(object, frame_start_walking, rotation_end)
            create_keyframe_position(object, frame_start_walking, coordinates_from)
            create_keyframe_position(object, frame_end_walking, coordinates_to)
            create_keyframe_rotation(object, frame_end_walking, rotation_end)
            create_keyframe_rotation(object, frame_end_walking + rotation_time, rotation_start)



import pandas as pd
import math
import random
import numpy as np


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
team_text_coordinates_stage2 = dict()
team_text_coordinates_stage4 = dict()
team_row = dict()
month_text_coordinates = dict()
month_text_coordinates_start = dict()
counter_team = 0
for team in teams:
    counter_team += 1
    counter_player = 0
    
    row_team = math.floor((counter_team - 1) / STAGE2_TEAMS_PER_ROW) + 1
    team_row[team] = row_team
    col_team = counter_team - math.floor((counter_team - 1) / STAGE2_TEAMS_PER_ROW) * STAGE2_TEAMS_PER_ROW
    team_text_coordinates_stage2[team] = ((col_team - 1) * STAGE2_TEAM_SPACING_X + STAGE2_PLAYER_SPACING_X,
                                   (row_team - 1) * STAGE2_TEAM_SPACING_Y - STAGE2_TEAM_TEXT_MARGIN, 0)
    team_text_coordinates_stage4[team] = (
        team_text_coordinates_stage2[team][0],
        team_text_coordinates_stage2[team][1] + STAGE4_TEXT_DISTANCE_Y,
        team_text_coordinates_stage2[team][2]
    )
    for player in team_players[team]:
        counter_player += 1
        row = math.floor((counter_player - 1) / STAGE2_PLAYERS_PER_ROW) + 1
        col = counter_player - math.floor((counter_player - 1) / STAGE2_PLAYERS_PER_ROW) * STAGE2_PLAYERS_PER_ROW
        row_team = math.floor((counter_team - 1) / STAGE2_TEAMS_PER_ROW) + 1
        col_team = counter_team - math.floor((counter_team - 1) / STAGE2_TEAMS_PER_ROW) * STAGE2_TEAMS_PER_ROW
        player_coordinates_stage2[player] = (
            (col_team - 1) * STAGE2_TEAM_SPACING_X + col * STAGE2_PLAYER_SPACING_X,
            (row_team - 1) * STAGE2_TEAM_SPACING_Y + (row - 1) * STAGE2_PLAYER_SPACING_Y,
            STAGE2_PLAYER_Z
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
        STAGE4_CHART_X + (counter_month - 1) * STAGE4_MONTH_SPACING_X + STAGE4_PLAYER_SPACING_X,
        STAGE4_CHART_Y + STAGE4_TEXT_MARGIN_Y,
        0
    )
    for player in month_players[month]:
        counter_player += 1
        row = math.floor((counter_player - 1) / STAGE4_PLAYERS_PER_ROW) + 1
        col = counter_player - math.floor((counter_player - 1) / STAGE4_PLAYERS_PER_ROW) * STAGE4_PLAYERS_PER_ROW
        player_coordinates_stage4[player] = (
            STAGE4_CHART_X + (counter_month - 1) * STAGE4_MONTH_SPACING_X + col * STAGE4_PLAYER_SPACING_X,
            STAGE4_CHART_Y + (row - 1) * STAGE4_PLAYER_SPACING_Y,
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
        insert_and_change_text(team_text_coordinates_stage2[team], team, team_label_name[team])
        mat = newShader("Text Material", "emission", 255, 255, 255)
        bpy.context.active_object.data.materials.append(mat)
        create_keyframe_position(team_label_name[team], STAGE3_START + STAGE3_TEXT_WAIT, team_text_coordinates_stage2[team])
        create_keyframe_position(team_label_name[team], STAGE4_START, team_text_coordinates_stage4[team])

    # Generate players and chart labels:
    for month in months:
        insert_and_change_text(month_text_coordinates[month], month_label[month], month_label_name[month])
        mat = newShader("Text Material", "emission", 255, 255, 255)
        bpy.context.active_object.data.materials.append(mat)
        # Create keyframes:
        month_text_coordinates_start[month] = (
            month_text_coordinates[month][0],
            month_text_coordinates[month][1] + STAGE2_MONTH_DISTANCE,
            month_text_coordinates[month][2]
        )
        create_keyframe_position(month_label_name[month], STAGE2_START+STAGE2_MONTH_WAIT, (month_text_coordinates_start[month]))
        create_keyframe_position(month_label_name[month], STAGE2_START+STAGE2_MONTH_WAIT+STAGE2_MONTH_DURATION, month_text_coordinates[month])

        for player in month_players[month]:
            unselect_all_objects()
            bpy.data.objects[TEAM_BLENDER_OBJECT[player_team[player]]].select_set(True)
            bpy.ops.object.duplicate(linked=False)
            bpy.data.objects[TEAM_BLENDER_OBJECT[player_team[player]]].select_set(False)
            for obj in bpy.context.selected_objects:
                obj.name = player
                frame_start_falling = STAGE2_START + random.randint(0,STAGE2_RANDOM) + team_row[player_team[player]]*STAGE2_ROW_INTERVAL
                frame_end_falling = frame_start_falling + STAGE2_FALL_TIME
                create_keyframe_position(player, frame_start_falling, player_coordinates_stage2[player])
                create_keyframe_position(player, frame_end_falling, player_coordinates_stage3[player])
                frame_start_spinning = STAGE3_START+random.randint(0, STAGE3_RANDOM)
                walk_from_to(player, frame_start_spinning, player_coordinates_stage3[player], player_coordinates_stage4[player])
                # frame_start_walking = frame_start_spinning + STAGE3_ROTATE_TIME
                # frame_end_walking = frame_start_walking + FPS * calculate_travel_time(player_coordinates_stage3[player], player_coordinates_stage4[player], STAGE3_PLAYER_SPEED)
                # create_keyframe_position(player, frame_start_walking, player_coordinates_stage3[player])
                # create_keyframe_position(player, frame_end_walking, player_coordinates_stage4[player])
                # (!!) insert spinning!
                frame_start_looking_up = STAGE4_START + random.randint(0,STAGE4_RANDOM)
                frame_end_looking_up = frame_start_looking_up + STATE4_PLAYER_ROTATION_DURATION
                create_keyframe_rotation(player, frame_start_looking_up, (0,0,0))
                create_keyframe_rotation(player, frame_end_looking_up, (STATE4_PLAYER_ROTATION_X,0,0))

    update_fonts(FONT_DIR)

print("END")
