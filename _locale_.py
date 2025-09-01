import core
import locale
import json


def get_default_lang(lang_map) -> str:
    _locale = locale.getlocale()[0]
    # Load lang with country
    config = lang_map.get(_locale)
    if not config:
        # Load only lang
        config = lang_map.get(_locale.split('_')[0])
    if not config:
        return 'eng'
    return config



class Locale:
    __slots__ = ("txt", "tmenu", "languages", "index")
    def __init__(self, lang):
        self.txt = None
        self.tmenu = None
        with open(core.res("subs/config.json"), 'r', encoding='utf-8') as file:
            lang_map = json.load(file)
            self.languages = tuple(lang_map.values())
            if not lang:
                language = get_default_lang(lang_map)
                self.index = self.languages.index(language)
            else:
                self.index = self.languages.index(lang)


    def change_lang(self, direction):
        self.index = (self.index + direction) % len(self.languages)
        lang = self.languages[self.index]
        with open(core.res(f'subs/{lang}/choices'), encoding='utf-8') as file:
            content = list(s.strip() for s in file.readlines())
            self.txt = content
        with open(core.res(f'subs/{lang}/menu'), encoding='utf-8') as file:
            content = list(s.strip() for s in file.readlines())
            self.tmenu = content
        return lang
