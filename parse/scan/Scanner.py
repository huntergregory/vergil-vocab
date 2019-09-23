import re


class Scanner:
    def __init__(self, delimiter="\n", text=None):
        self.delimiter = delimiter
        self.text = text
        self.current = None
        if text:
            self.set_text(text)

    def set_text(self, text):
        self.text = text
        next_delimiter = self.text.find(self.delimiter)
        if next_delimiter == -1:
            self.current = self.text
        if next_delimiter == 0:
            self.set_text(self.text[1:])
            return
        self.current = self.text[0:next_delimiter]
        self.text = self.text[next_delimiter + 1:]

    def get_next(self):
        self.move_to_next()
        return self.current

    def move_to_next(self):
        if self.text is None:
            raise Exception
        next_delimiter = self.text.find(self.delimiter)
        if next_delimiter == -1:
            raise Exception
        self.current = self.text[0:next_delimiter]  # don't include delimiter
        if len(self.text) == next_delimiter - 1:
            self.text = None
        else:
            self.text = self.text[next_delimiter + 1:]

    def has_next(self):
        return self.text.find(self.delimiter) >= 0

    def remove_from_current(self, regex, replacement):  # add flags??
        self.current = re.sub(regex, replacement, self.current)

    def current_contains(self, regex):
        if re.match(r".*" + regex, self.current):
            return True
        else:
            return False
