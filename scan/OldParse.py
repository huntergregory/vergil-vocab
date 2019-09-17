import requests;
import re;
from tqdm import trange;


def get_eclogues_url(num):
    return "https://www.thelatinlibrary.com/vergil/ec" + str(num)  + ".shtml"


def get_whitakers_url(word):
    return "http://archives.nd.edu/cgi-bin/wordz.pl?keyword=" + word


def search_for_word(word):
    text = requests.get(get_whitakers_url(word)).text
    regex = '<pre>\n(.*)\s\s</pre>'
    match = re.search(regex, text, re.S)
    if match:
        clean_text = match.group(1)
        # TODO get dictionary definitions
    else:
        # TODO handle no match (probably won't happen, different than unknown word)
        return False


def parse_eclogues_words(num, line_start = 1, line_end = -1):
    text = requests.get(get_eclogues_url(num)).text
    body_regex = ".*<p class=\"internal_navigation\">\s*(<p>.*p>)+.*<div class=\"footer\">"
    body_match = re.search(body_regex, text, re.S | re.I)
    if not body_match:
        print("no matches...")
        return False
    paragraphs = body_match.group(1)
    print(paragraphs)
    space_regex = "(&nbsp;)*<FONT Size=\d+>\d+</FONT>"
    no_spaces = re.sub(space_regex, "", paragraphs, flags= re.S | re.I)
    start_p_regex = "<p>"
    no_starting_p_tags = re.sub(start_p_regex, "", no_spaces)
    punctuation_regex = "/[\]\.,\/#!\?$%\^&\*;:{}=\-_`~()\"'(&#151)"
    all_but_space = "\t\r\n\f"
    special_new_line_regex = "([\w" + punctuation_regex + "])[" + all_but_space + "]+(\w)"
    special_new_line = re.sub(special_new_line_regex, "\1 \2", no_starting_p_tags)
    no_new_line = re.sub("[" + all_but_space + "]", "", special_new_line)
    tag_regex = "</?[a-zA-z]+>"
    lines = re.compile(tag_regex).split(no_new_line)
    clean_lines = [re.sub("[" + punctuation_regex + "]", "", line) for line in lines]
    print('\n----------------------------------------------\nBEGIN')
    non_empty_clean_lines = []
    not_space_pattern = re.compile("\S")
    for line in clean_lines:
        if not_space_pattern.match(line):
            non_empty_clean_lines.append(line)
            print(line)
    return non_empty_clean_lines


def main(num=2):
    words = parse_eclogues_words(num)  # TODO have line number inputs
    if words:
        for k in trange(len(words)):
            word = words[k] 
            definitions = search_for_word(word)
            # TODO see if defs already in a list of known words
            # TODO output nicely, word + definition(s)


if __name__ == '__main__':
    main()


