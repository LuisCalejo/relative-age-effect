import setup_python_blender

IS_TEST = False
if not IS_TEST:
    import bpy

    setup_python_blender.install_packages(["pandas", "math", "random", "numpy", "datetime"])

import datetime

FRAME_START = 600
FRAME_END = 1400


def interpolate_dates_string(number_of_frames, start_date, end_date):
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    date_range = end_date - start_date
    date_interval = date_range / (number_of_frames - 1)
    frame_dates = []
    for i in range(number_of_frames):
        frame_date = start_date + (date_interval * i)
        formatted_frame_date = frame_date.strftime('%Y, %B %d')
        frame_dates.append(formatted_frame_date)
    return frame_dates


def interpolate_ages_string(number_of_frames, birthdate, start_date, end_date):
    birthdate = datetime.datetime.strptime(birthdate, "%Y-%m-%d")
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    date_range = end_date - start_date
    date_interval = date_range / (number_of_frames - 1)
    ages = []
    for i in range(number_of_frames):
        frame_date = start_date + (date_interval * i)
        age = frame_date - birthdate
        # years = int(age.days / 365.25)
        # months = int((age.days % 365.25) / 30.4375)
        # days = int(age.days - years*365.25)
        years = int(age.days / 365.22)  # quick workaround to round the years down
        months = int((age.days % 365.22) / 30.4375)  # quick workaround to round the years down
        days = int(age.days - years*365.22)  # quick workaround to round the years down
        if months == 1:
            day_label = " day"
        else:
            day_label = " days"
        age_str = str(years) + " years, " + str(days) + day_label
        ages.append(age_str)
    return ages


def interpolate_ages_int(number_of_frames, birthdate, start_date, end_date):
    birthdate = datetime.datetime.strptime(birthdate, "%Y-%m-%d")
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    date_range = end_date - start_date
    date_interval = date_range / (number_of_frames - 1)
    ages = []
    for i in range(number_of_frames):
        frame_date = start_date + (date_interval * i)
        age = frame_date - birthdate
        ages.append(age.days)
    return ages


age_red_string = interpolate_ages_string(FRAME_END - FRAME_START + 1, '2004-01-01', '2022-12-31', '2010-09-01')
age_blue_string = interpolate_ages_string(FRAME_END - FRAME_START + 1, '2004-12-31', '2022-12-31', '2010-09-01')
age_blue_string[FRAME_END-FRAME_START] = "5 years, 244 days"  # quick workaround to correct age
age_red_int = interpolate_ages_int(FRAME_END - FRAME_START + 1, '2004-01-01', '2022-12-31', '2010-09-01')
age_blue_int = interpolate_ages_int(FRAME_END - FRAME_START + 1, '2004-12-31', '2022-12-31', '2010-09-01')
frame_dates = interpolate_dates_string(FRAME_END - FRAME_START + 1, '2022-12-31', '2010-09-01')


if not IS_TEST:
    # Update text labels:
    scene = bpy.context.scene
    text_date = scene.objects['Text Date']
    text_red_age = scene.objects['Text Red Age']
    text_blue_age = scene.objects['Text Blue Age']
    text_red_percent = scene.objects['Text Red Percent']

    def recalculate_text(scene):
        if scene.frame_current < 600:
            text_date.data.body = frame_dates[0]
            age_red_string_frame = age_red_string[0]
            age_blue_string_frame = age_blue_string[0]
            age_red_int_frame = age_red_int[0]
            age_blue_int_frame = age_blue_int[0]
        elif 600 <= scene.frame_current <= 1400:
            text_date.data.body = frame_dates[scene.frame_current - FRAME_START]
            age_red_string_frame = age_red_string[scene.frame_current - FRAME_START]
            age_blue_string_frame = age_blue_string[scene.frame_current - FRAME_START]
            age_red_int_frame = age_red_int[scene.frame_current - FRAME_START]
            age_blue_int_frame = age_blue_int[scene.frame_current - FRAME_START]
        else:
            text_date.data.body = frame_dates[FRAME_END - FRAME_START]
            age_red_string_frame = age_red_string[FRAME_END - FRAME_START]
            age_blue_string_frame = age_blue_string[FRAME_END - FRAME_START]
            age_red_int_frame = age_red_int[FRAME_END - FRAME_START]
            age_blue_int_frame = age_blue_int[FRAME_END - FRAME_START]
        age_red_percent_frame = round(100 * (age_red_int_frame / age_blue_int_frame - 1))
        text_red_age.data.body = 'Born: 2004, January 1\nAge: ' + age_red_string_frame
        text_blue_age.data.body = 'Born: 2004, December 31\nAge: ' + age_blue_string_frame
        text_red_percent.data.body = '(' + str(age_red_percent_frame) + '% older than Blue)'
    bpy.app.handlers.frame_change_pre.append(recalculate_text)
print("END")