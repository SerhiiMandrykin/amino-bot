import os
import re


class Obscene:
    """
    Class Obscene
    Check if text has obscene
    """

    def __init__(self):
        """
        Initializing
        Getting obscene list
        """
        with open(os.getcwd() + '/obscene.txt', 'r', encoding='UTF-8') as obscene_file:
            self.obscene = obscene_file.read().split(',')
            obscene_file.close()

        with open(os.getcwd() + '/not_obscene.txt', 'r', encoding='UTF-8') as not_obscene_file:
            self.not_obscene = not_obscene_file.read().split(',')
            not_obscene_file.close()

    def is_clear(self, text):
        obscene_pattern = r''.join(['(' + ''.join(x + '|' for x in self.obscene) + ')'])[:-2] + ')'
        non_obscene_pattern = r''.join(['(' + ''.join(x + '|' for x in self.not_obscene) + ')'])[:-2] + ')'

        patterns = [
            r'пош(е|ё)л\s?(т(ы|и))?\s?на',
        ]

        for i in patterns:
            if re.match(i, text, flags=re.IGNORECASE | re.UNICODE):
                return False

        if re.match(obscene_pattern, text, flags=re.IGNORECASE | re.UNICODE) and not re.match(
                non_obscene_pattern, text, flags=re.IGNORECASE | re.UNICODE):
            return False

        return True
