import requests
import sys
from scan.Scanner import *
from latin import WordFactory

REPLACE_TAG_REGEXS = [r"<p>", r"</p>", r"<font size=\d+>[\d\w ]+</font>"]
BREAK_REGEX = r"<br>"
PUNCTUATION_REGEX = r"[\[\]\.,\/#!\?$%\^&\*;:{}=\-_`~()\"'(&#151;)]"
FUNKY_SPACE_REGEX = r"&nbsp;"

## TODO trim front whitespace, split based on any white space


def get_eclogues_url(book_num):
    return "https://www.thelatinlibrary.com/vergil/ec" + str(book_num) + ".shtml"


def get_whitakers_url(word):
    return "http://archives.nd.edu/cgi-bin/wordz.pl?keyword=" + word


def get_words_in_line(line):
    return re.split(r"\s+", line)


def parse_lines(url):
    lines = []
    text = requests.get(url).text
    body_regex = r".*<p class=\"internal_navigation\">\s*(<p>.*p>)+.*<div class=\"footer\">"
    body_match = re.search(body_regex, text, re.S | re.I)
    if not body_match:
        return False
    paragraphs = body_match.group(1)
    paragraphs = re.sub(BREAK_REGEX, "\n", paragraphs, flags=re.I)
    for regex in REPLACE_TAG_REGEXS:
        paragraphs = re.sub(regex, "", paragraphs, flags=re.I)
    paragraphs = re.sub(FUNKY_SPACE_REGEX, "", paragraphs)
    paragraphs = re.sub(PUNCTUATION_REGEX, " ", paragraphs)
    scanner = Scanner(text=paragraphs)
    if scanner.current_contains(r"\w"):
        lines.append(get_words_in_line(scanner.current))
    while scanner.has_next():
        scanner.move_to_next()
        if scanner.current_contains(r"\w"):
            lines.append(get_words_in_line(scanner.current))

    if len(lines) > 0:
        return lines
    return False


def search_for_word(word):
    text = requests.get(get_whitakers_url(word)).text
    regex = r'<pre>\n(.*)</pre>'
    match = re.search(regex, text, re.S)
    if match:
        return match.group(1)
    else:
        return False


def output_vocab(word_set):
    with open("vocab.txt", "w+") as file:
        for word in word_set:
            file.write(str(word))
            file.write("\n")


def main(url, line_start=0, line_end=-1):
    lines = parse_lines(url)
    if not lines:
        print("Couldn't find latin")
        return

    if line_end < 0 or line_start == line_end:
        lines = lines[line_start - 1:]
    else:
        lines = lines[line_start - 1:line_end - 1]
    scanner = Scanner()
    word_factory = WordFactory.WordFactory()
    latin_words = []
    for k in range(len(lines)):
        for word in lines[k]:
            if word == '':
                continue
            word_text = search_for_word(word)
            if not word_text:
                continue
            scanner.set_text(word_text)
            while scanner.has_next():
                previous = scanner.current
                scanner.move_to_next()
                if not scanner.current_contains(r"\[XXX\w*\]"):
                    continue
                latin_word = word_factory.get_word(previous, scanner.current, scanner.get_next())
                if latin_word and latin_word not in latin_words:
                    latin_words.append(latin_word)

    # TODO see if defs already in a list of known latin
    output_vocab(latin_words)


# TODO use sysout
if __name__ == '__main__':
    book_num = int(sys.argv[1])
    start = int(sys.argv[2])
    end = int(sys.argv[3])
    # book_num = 10
    # start = 1
    # end = 10
    main(get_eclogues_url(book_num), line_start=start, line_end=end)
