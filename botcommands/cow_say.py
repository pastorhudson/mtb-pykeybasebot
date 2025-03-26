def cowsay(message, width=30):
    """
    Generate cowsay ASCII art with the given text in a speech bubble.

    Args:
        message (str): The text to be displayed in the speech bubble.
        width (int, optional): Maximum width of the speech bubble. Defaults to 40.

    Returns:
        str: The complete cowsay ASCII art as a string.
    """
    # Wrap the text to fit within the specified width
    lines = []
    current_line = ""

    for word in message.split():
        if len(current_line) + len(word) + 1 <= width:
            if current_line:
                current_line += " " + word
            else:
                current_line = word
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    # Create the speech bubble
    bubble = []

    if len(lines) == 1:
        bubble.append(f"< {lines[0]} >")
    else:
        bubble.append(f"/ {lines[0]} {' ' * (width - len(lines[0]) - 2)}\\")

        for line in lines[1:-1]:
            padding = width - len(line) - 2
            bubble.append(f"| {line}{' ' * padding} |")

        bubble.append(f"\\ {lines[-1]} {' ' * (width - len(lines[-1]) - 2)}/")

    # Create the top and bottom borders of the speech bubble
    bubble_width = max(len(line) for line in bubble)
    bubble.insert(0, " " + "_" * (bubble_width - 2))
    bubble.append(" " + "-" * (bubble_width - 2))

    # Create the cow
    cow = [
        "        \\   ^__^",
        "         \\  (oo)\\_______",
        "            (__)\\       )\\/\\",
        "                ||----w |",
        "                ||     ||"
    ]

    # Combine the speech bubble and cow
    combined = "\n".join(bubble + cow)
    return f"```{combined}```"


# Example usage
if __name__ == "__main__":
    message = "Hello! I'm a cow saying things through Python code!"
    print(cowsay(message))