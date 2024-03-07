import argparse
import re

morse_code = {
    'A': '·—',
    'B': '—·',
    'C': '·——·',
    'D': '—··',
    'E': '·',
    'F': '··—·',
    'G': '·——·—·',
    'H': '····',
    'I': '··',
    'J': '·———',
    'K': '—·—',
    'L': '·—··',
    'M': '·——',
    'N': '—·',
    'O': '———',
    'P': '·——·',
    'Q': '·—·—',
    'R': '·—·',
    'S': '···',
    'T': '—··—',
    'U': '··—',
    'V': '···—',
    'W': '·——',
    'X': '—··—',
    'Y': '—·——',
    'Z': '——··',
    ' ': ' / ',
    '0': '—————',
    '1': '·————',
    '2': '··———',
    '3': '···——',
    '4': '····—',
    '5': '·····',
    '6': '—····',
    '7': '——···',
    '8': '———··',
    '9': '————·',
    '.': '·—·—·—',
    ',': '——··——',
    '?': '··——··',
    '!': '—·—·——',
    '"': '·—··—·'
}

morse_code_dict = {v: k for k, v in morse_code.items()}


def text_to_morse(text):
    morse_string = ''
    text = text.upper()
    for char in text:
        try:
            if char == ' ':
                morse_string += morse_code[char]
            else:
                morse_string += morse_code[char] + ' '
        except KeyError as e:
            return f"Sorry! We found the following key wasn't recognized: {e}"
    return morse_string.strip()


def morse_to_text(morse):
    text = []
    morse = morse.split(' / ')
    morse = [word.split() for word in morse]
    for word in morse:
        for char in word:
            text.append(morse_code_dict[char])
        text.append(" ")
    return ''.join(text)


def check_morse(morse_string):
    morse_string = morse_string.replace('.', '·')
    if re.search(r'[\-_]', morse_string):
        morse_string = re.sub(r'[\-_]', '—', morse_string)
        print(morse_string)
    return morse_string


def output():
    parser = argparse.ArgumentParser(
        description='Text to Morse code translator',
        prog='morse-py3'
    )
    parser.add_argument('input_string', metavar='I', type=str,
                        help='Input for translator')
    parser.add_argument('--morse', dest='morse_flag', action='store_true',
                        help='Translate input to Morse code')
    parser.add_argument('--text', dest='text_flag', action='store_true',
                        help='Translate input from Morse code to text')

    args = parser.parse_args()

    if args.morse_flag:
        translated_text = text_to_morse(args.input_string)
    elif args.text_flag:
        translated_text = morse_to_text(args.input_string)
    else:
        print("Please specify either --morse or --text flag")
        return

    print(translated_text)


def get_morse_code(text):
    observation = ["beep beep dah dah something like that. . . "]
    msg = f"{observation}\n```{text_to_morse(text)}```"
    return msg


if __name__ == "__main__":
    print(text_to_morse("SOS"))