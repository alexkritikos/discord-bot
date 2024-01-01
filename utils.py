def to_multi_line_text(filename):
    with open(filename) as file:
        multi_line_text = "\n".join(line.strip() for line in file)
    return multi_line_text