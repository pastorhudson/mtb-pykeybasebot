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
    command = command.split("\"")
          # .split("\""))
    msg = f"Stupid Poll: {command[1]}\n"
    option_num = 1
    for index, option in enumerate(command[2:]):
        if option != " " and option != "":
            msg += f":{get_moji(option_num)}: {option}\n"
            option_num += 1

    return msg, option_num-1


if __name__ == "__main__":
    make_poll('!poll "Should @pastorhudson change his profile picture?" "Definitely!" "Absolutely!" "Of course he should!"')