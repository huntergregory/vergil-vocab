from abc import ABC
from scan.Scanner import *


# parses whitakers latin principal part & definition lines
class Word(ABC):
    PROPER_NAME = "Assume this is capitalized proper name/abbr"

    def __init__(self, unparsed_search_keyword, unparsed_principal_parts, unparsed_definitions, default_hash_value):
        self.default_hash_value = default_hash_value
        self.principal_parts = False
        self.definitions = False

        self._parse_parts(unparsed_principal_parts)
        self._parse_definitions(unparsed_definitions)
        if self.principal_parts is False:
            first_space = unparsed_search_keyword.index(" ")
            self.principal_parts = unparsed_search_keyword[0:first_space]
        self.__success = self.definitions is not False

    # set self.principal_parts to False if fails
    def _parse_parts(self, unparsed_principal_parts):
        pass

    # set self.definitions to False if fails
    def _parse_definitions(self, unparsed_definitions):
        semicolon_scanner = Scanner(delimiter=r";")
        semicolon_scanner.set_text(unparsed_definitions)
        self.definitions = []
        if semicolon_scanner.current_contains(self.PROPER_NAME) or semicolon_scanner.current_contains(r"\["):
            self.definitions = False  # FIXME currently can't handle when alternate parts come before definitions
            return
        self.definitions = [semicolon_scanner.current]
        while semicolon_scanner.has_next():
            self.definitions.append(semicolon_scanner.get_next()[1:])  # skip the space

    def failed(self):
        return not self.__success

    def __hash__(self):
        if not self.__success:
            return self.default_hash_value
        return hash(self.principal_parts)

    def __eq__(self, other):
        return self.__success and isinstance(other, Word) and self.principal_parts == other.principal_parts

    def __str__(self):
        definitions_string = self.definitions[0]
        for k in range(1, len(self.definitions)):
            definitions_string += "\n" + self.definitions[k]
        return self.principal_parts + "\n" + definitions_string + "\n"
