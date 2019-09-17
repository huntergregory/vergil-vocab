import re;


class Scanner:
    def __init__(self, text):
        self.text = text
        self.current = None

    def set_next_line(self):
        if self.text is None:
            raise Exception
        next_newline = self.text.find("\n")
        if next_newline == -1:
            raise Exception
        self.current = self.text[0:next_newline]
        if len(self.text) == next_newline - 1:
            self.text = None
        else:
            self.text = self.text[next_newline + 1:]

    def has_next(self):
        return self.text.find("\n") >= 0

    def remove_from_current(self, regex, replacement):  # add flags??
        self.current = re.sub(regex, replacement, self.current)

    def get_current(self):
        if self.current is None:
            raise Exception
        return self.current
