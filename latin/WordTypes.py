from latin.Word import *
from scan.Scanner import *

## FIXME everything but noun & prep, first part before KEYWORD
## FIXME add INTERJ??


class Adjective(Word):
    scanner = Scanner(delimiter=r"  ADJ")

    def __init__(self, unparsed_search_keyword, unparsed_principal_parts, unparsed_definitions, default_hash_value):
        Word.__init__(self, unparsed_search_keyword, unparsed_principal_parts, unparsed_definitions, default_hash_value)

    def _parse_parts(self, unparsed_definitions):
        self.scanner.set_text(unparsed_definitions)
        self.principal_parts = self.scanner.current


class Verb(Word):  # handle deponents
    scanner = Scanner(delimiter=r"  V")

    def __init__(self, unparsed_search_keyword, unparsed_principal_parts, unparsed_definitions, default_hash_value):
        Word.__init__(self, unparsed_search_keyword, unparsed_principal_parts, unparsed_definitions, default_hash_value)

    def _parse_parts(self, unparsed_definitions):
        self.scanner.set_text(unparsed_definitions)
        self.principal_parts = self.scanner.current


class Pronoun(Word):
    scanner = Scanner(delimiter=r",")

    def __init__(self, unparsed_search_keyword, unparsed_principal_parts, unparsed_definitions, default_hash_value):
        Word.__init__(self, unparsed_search_keyword, unparsed_principal_parts, unparsed_definitions, default_hash_value)

    def _parse_parts(self, unparsed_definitions):
        self.scanner.set_text(unparsed_definitions)
        if not self.scanner.has_next():
            self.principal_parts = False
        else:
            self.principal_parts = self.scanner.current + "," + self.scanner.get_next()
            if self.scanner.has_next():
                self.principal_parts += "," + self.scanner.get_next()


class Noun(Word):
    def __init__(self, unparsed_search_keyword, unparsed_principal_parts, unparsed_definitions, default_hash_value):
        Word.__init__(self, unparsed_search_keyword, unparsed_principal_parts, unparsed_definitions, default_hash_value)

    def _parse_parts(self, unparsed_definitions):
        try:
            comma = unparsed_definitions.index(",")
            self.principal_parts = unparsed_definitions[0:comma]
            first_n = unparsed_definitions.index("  N ")
            self.principal_parts += unparsed_definitions[comma:first_n]
            gender = unparsed_definitions[first_n + 5]
            self.principal_parts += ", " + gender
        except ValueError:
            self.principal_parts = False


class Adverb(Word):
    scanner = Scanner(delimiter="  ADV")

    def __init__(self, unparsed_search_keyword, unparsed_principal_parts, unparsed_definitions, default_hash_value):
        Word.__init__(self, unparsed_search_keyword, unparsed_principal_parts, unparsed_definitions, default_hash_value)

    def _parse_parts(self, unparsed_definitions):
        self.scanner.set_text(unparsed_definitions)
        self.principal_parts = self.scanner.current


class Preposition(Word):
    def __init__(self, unparsed_search_keyword, unparsed_principal_parts, unparsed_definitions, default_hash_value):
        Word.__init__(self, unparsed_search_keyword, unparsed_principal_parts, unparsed_definitions, default_hash_value)

    def _parse_parts(self, unparsed_definitions):
        try:
            prep_keyword = unparsed_definitions.index("  PREP  ")
            self.principal_parts = unparsed_definitions[0:prep_keyword]
            rest = unparsed_definitions[prep_keyword + 8:]
            space = rest.index(" ")
            self.principal_parts += "(takes " + rest[0:space] + ")"
        except ValueError:
            self.principal_parts = False
