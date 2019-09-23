import requests
from tqdm import trange

from parse.scan.Scanner import *
from parse.latin import WordFactory


def get_eclogues_url(num):
    return "https://www.thelatinlibrary.com/vergil/ec" + str(num)  + ".shtml"


def get_whitakers_url(word):
    return "http://archives.nd.edu/cgi-bin/wordz.pl?keyword=" + word


def parse_eclogues_words(num, line_start = 1, line_end = -1):
    text = requests.get(get_eclogues_url(num)).text
    body_regex = r".*<p class=\"internal_navigation\">\s*(<p>.*p>)+.*<div class=\"footer\">"
    body_match = re.search(body_regex, text, re.S | re.I)
    if not body_match:
        print("no matches...")
        return False
    paragraphs = body_match.group(1)
    space_regex = r"(&nbsp;)*<FONT Size=\d+>\d+</FONT>"
    no_spaces = re.sub(space_regex, "", paragraphs, flags=re.S | re.I)
    no_starting_p_tags = re.sub(r"<p", "", no_spaces)
    punctuation_regex = r"/[\]\.,\/#!\?$%\^&\*;:{}=\-_`~()\"'(&#151)"
    all_but_space = r"\t\r\n\f"
    special_new_line_regex = "([\w" + punctuation_regex + "])[" + all_but_space + "]+(\w)"
    special_new_line = re.sub(special_new_line_regex, "\1 \2", no_starting_p_tags)
    no_new_line = re.sub(r"[" + all_but_space + r"]", "", special_new_line)
    tag_regex = r"</?[a-zA-z]+>"
    lines = re.compile(tag_regex).split(no_new_line)
    clean_lines = [re.sub(r"[" + punctuation_regex + r"]", "", line) for line in lines]
    print('\n----------------------------------------------\nBEGIN')
    non_empty_clean_lines = []
    not_space_pattern = re.compile(r"\S")
    for line in clean_lines:
        if not_space_pattern.match(line):
            non_empty_clean_lines.append(line)
            print(line)
    return non_empty_clean_lines


def search_for_word(word):
    text = requests.get(get_whitakers_url(word)).text
    regex = r'<pre>\n(.*)</pre>'
    match = re.search(regex, text, re.S)
    if match:
        return match.group(1)
    else:
        return False


def main(num=2):
    # latin = parse_eclogues_words(num)  # TODO have line number inputs
    words = ["Formosum", "pastor", "Corydon", "ardebat", "Alexin"]
    if not words:
        print("Couldn't find latin")
        return
    scanner = Scanner()
    word_factory = WordFactory.WordFactory()
    latin_words = set()
    for k in trange(len(words)):
        word_text = search_for_word(words[k])
        if not word_text:
            continue
        scanner.set_text(word_text)
        while scanner.has_next():
            scanner.move_to_next()
            if not scanner.current_contains(r"\[XXX\w*]\]"):
                continue
            latin_word = word_factory.get_word(scanner.current, scanner.get_next())
            if latin_word:
                latin_words.add(latin_word)

    # TODO see if defs already in a list of known latin
    # TODO output nicely, word + definition(s)


if __name__ == '__main__':
    main()


