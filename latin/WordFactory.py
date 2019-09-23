from latin.WordTypes import *
from scan.Scanner import *


class WordFactory:
    __init_count = 0

    VERB = " V "
    ADJECTIVE = " ADJ "
    NOUN = " N "
    ADVERB = " ADV "
    PREPOSITION = " PREP "
    PRONOUN = " PRON "

    def __init__(self):
        self.__init_count += 1
        self.scanner = Scanner()
        pass

    def get_word(self, unparsed_search_keyword, principal_parts, definitions):
        self.scanner.set_text(principal_parts)
        word = None
        if self.scanner.current_contains(self.NOUN):
            word = Noun(unparsed_search_keyword, principal_parts, definitions, self.__init_count)
        elif self.scanner.current_contains(self.VERB):
            word = Verb(unparsed_search_keyword, principal_parts, definitions, self.__init_count)
        elif self.scanner.current_contains(self.ADJECTIVE):
            word = Adjective(unparsed_search_keyword, principal_parts, definitions, self.__init_count)
        elif self.scanner.current_contains(self.ADVERB):
            word = Adverb(unparsed_search_keyword, principal_parts, definitions, self.__init_count)
        elif self.scanner.current_contains(self.PREPOSITION):
            word = Preposition(unparsed_search_keyword, principal_parts, definitions, self.__init_count)
        elif self.scanner.current_contains(self.PRONOUN):
            word = Pronoun(unparsed_search_keyword, principal_parts, definitions, self.__init_count)
        if word is None or word.failed():
            return None
        return word

    def had_success(self):
        return self.success
