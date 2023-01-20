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


