def get_moji(num):
   nums = {
       1: "one",
       2: "two",
       3: "three",
       4: "four",
       5: "five",
       6: "six",
       7: "seven",
       8: "eight",
       9: "nine",
       10: "ten",
   }
   return nums[num]


def make_poll(command):
    s = command.replace("”", '\"')
    s = s.replace("“", '\"')
    split_command = s.split("\"")
    # print(split_command)
    # if not len(split_command) > 1:
    #     split_command = command.split("”")
    #     print(split_command)
    try:
        msg = f"Stupid Poll: {split_command[1]}\n"
    except IndexError:
        return ["\n".join(["`You have failed.", '!poll "Should we move the office to a beach?" "Yes" "No"`']), []]
    option_num = 1
    emojis = []
    for index, option in enumerate(split_command[2:]):
        if option != " " and option != "":
            msg += f":{get_moji(option_num)}: {option}\n"
            emojis.append(f":{get_moji(option_num)}:")
            option_num += 1

    return msg, emojis


async def make_ai_poll(bot, event, question, options):
    conversation_id = event.msg.conv_id


    msg = f"Stupid Poll: {question}\n"
    option_num = 1
    emojis = []
    for index, option in enumerate(options):
        if option != " " and option != "":
            msg += f":{get_moji(option_num)}: {option}\n"
            emojis.append(f":{get_moji(option_num)}:")
            option_num += 1

    if not options:
        await bot.chat.send(conversation_id, msg)
    else:
        poll_msg = await bot.chat.send(conversation_id, msg)
        for emoji in emojis:
            await bot.chat.react(conversation_id, poll_msg.message_id, emoji)

    return


if __name__ == "__main__":
    s = '!poll “Does IPhone ruin everything?” “yes” “No”'

    print(make_poll(s))
    # s = '!poll "Will we ever use this?" "Probably not" "You literally wasted an hour of your life" "This is @sakanakami fault"'
    # print(make_poll(s))
