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
    split_command = command.split("\"")
    if not len(split_command) > 1:
        split_command = command.split("”")
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


if __name__ == "__main__":
    print(make_poll('!poll “Does this work?” “Ya of course” “No”'))
