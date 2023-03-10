import datetime
import re
from string import ascii_letters, digits


def save_user_choice(update, context):
    user_data = context.user_data
    text = update.message.text
    category = user_data['choice']
    user_data[category] = text
    del user_data['choice']

def end(update, context):
    update.message.reply_text(
        'До встречи)'
    )


def is_valid_date(date: str) -> bool:
    chars = ascii_letters + digits
    day = date[0:2]
    month = date[3:5]
    year = date[6:]
    if date[2] in chars or date[5] in chars and not all(map(lambda x: x.isdigit(), [day, month, year])):
        return False
    day, month, year = map(int, [day, month, year])
    try:
        return datetime.date(year, month, day) >= datetime.date.today()
    except:
        return False


def is_time_valid(time: str) -> bool:
    try:
        hours, minutes = map(int, time.split(re.search(r'[-.:]{1}', time).group()))
    except:
        return False
    if 0 <= hours < 24 and 0 <= minutes < 60:
        return True
    return False


def get_timekeyboard(datetime_now):
    now_hours =  datetime_now.strftime('%H')
    counter = 0
    temp_time = []
    time_keyboard = []
    now_hours =  int(datetime_now.strftime('%H'))
    for hour in range(now_hours, 25):
        if hour < 10:
            hour = f'0{hour}.00'
        elif hour == 24:
            hour = '00:00'
        else:
            hour = f'{hour}.00'
        temp_time.append(hour)
        counter += 1
        if counter == 6:
            time_keyboard.append(temp_time)
            temp_time = []
            counter = 0
    if counter != 0:
        time_keyboard.append(temp_time)
    return time_keyboard


