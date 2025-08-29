import moment
import pygame.freetype
from PIL import ImageFont
import os
import core
import pickle

import text
from core import constants
from videoplay import play_video
from choice import ChoiceScreen, PubgScreen
from menu import MainMenu, DisclaimerScreen
from screen import EndingScreen
import sys
import _locale_


class Main:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.fullscreen = True

        self.score = 0.008
        self.init_font(self.screen.get_size()[0])
        core.constants.EMOJI_IMAGES = {
            ':death:': pygame.image.load(core.res('media/emoji/death.png')).convert_alpha(),
            ':ending:': pygame.image.load(core.res('media/emoji/ending.png')).convert_alpha(),
            ':biography:': pygame.image.load(core.res('media/emoji/person.png')).convert_alpha(),
            ':speedrun:': pygame.image.load(core.res('media/emoji/star.png')).convert_alpha(),
            ':fly:': pygame.image.load(core.res('media/emoji/fly.png')).convert_alpha(),
        }
        self.fight_ss = None
        self.temp = 0
        self.time = moment.date(2019, 6, 13)

        if not os.path.exists(save_path):
            self.collection = {'endings': set(), 'biography': {1}, 'speedrun': 0, 'death': 0}
            self.plus_factor = {'ending': 5, 'biography': 6, 'speedrun': 6, 'death': 10}
            self.unseen = {'endings': set(), 'biography': set(), 'speedrun': 0, 'death': 0, 'frames': set()}
            self.time_s = None
            self.frame = None
            self.time = self.time.replace(hours=7)

            self.saves = {'load': None, 'continue': None, 'credits': 0, 'max_credits': [120, 160],
                          'attempts': [1, 1], 'sw': 0}
            self.settings = {'volume': 1.0, 'subtitles': True, 'theme': 0}

            self.block = [False] * 4
            self.locale = _locale_.Locale(None)
            self.settings['lang'] = self.locale.change_lang(0)
            self.frame_s = core.SortedKeyList(key=core.attrgetter('time'))

            self.cache = {'frames': text.main(), 'endings': text.main1(), 'biography': text.main2()}
            self.saves['branch_ch'] = [[core.Choice(38,57,0), core.Choice(39,59, 5)],
                                            [core.Choice(38,58,-1), core.Choice(39,59, 0)],
                                            [core.Choice(97,61,0), core.Choice(98,62, -2)]]
        else:
            with open(save_path, 'rb') as f:
                data = pickle.load(f)
                self.collection = data['collection']
                self.plus_factor = data['plus_factor']
                self.unseen = data['unseen']
                self.saves = data['saves']
                self.block = data['block']
                self.settings = data['settings']
                self.cache = data['cache']

                self.locale = _locale_.Locale(self.settings['lang'])
                self.locale.change_lang(0)

            if os.path.exists(save_path2):
                with open(save_path2, 'rb') as f:
                    data = pickle.load(f)
                    self.frame_s = core.SortedKeyList(data, key=core.attrgetter('time'))
            else:
                self.frame_s = core.SortedKeyList(key=core.attrgetter('time'))

        theme_lst = core.res("themes/list.txt")
        with open(theme_lst, 'r', encoding='utf-8') as f:
            self.themes = [theme.strip() for theme in f.readline().split(',')]

        name = self.themes[self.settings['theme']]
        constants.change_theme(name)
        pygame.display.set_caption(self.locale.tmenu[34])
        core.constants.click.set_volume(0.3 * self.settings['volume'])

    def exit_game(self):
        pygame.quit()
        self.save()
        sys.exit()

    def init_font(self, width):
        self.font_sub = ImageFont.truetype(core.constants.sub_font, int(0.012 * width))
        self.font = pygame.font.Font(None, int(0.03 * width))   # 0.03
        self.font_text = pygame.font.Font(core.constants.text_font, int(0.018 * width))
        self.font_title = pygame.font.Font(None, int(0.049 * width))
        self.font_b = pygame.freetype.SysFont(core.constants.bold_font, int(0.02 * width))

    def questioning(self, current_link: int):
        score = self.frame.next_link
        x = current_link - 71
        q = x // 5
        self.score += score
        if q == 2:
            if self.score == 3:
                link = 87
            elif self.score == 0:
                link = 85
            else:
                link = 86
        else:
            link = q * 5 + 76
        return link

    def fight(self, act: int):
        config = self.temp[3]
        link = core.fighting(act, config)
        win = config['win_']
        if win is None:
            self.temp[2] -= 1
        elif win:
            self.temp[1] -= 1
        else:
            self.temp[0] -= 1
            self.temp[2] -= 1

        if self.temp[0] == 0:
            res = 99
        elif self.temp[1] == 0:
            res = 98
        elif self.temp[2] == 0:
            res = 100
        else:
            res = link
        return link, res

    def init_games(self, current_link):
        if current_link in (71, 101, 105):
            self.score = 0
        else:
            config = {'w_change': [], 'l_change': [], 'd_change': [], 'stats': [], 'win': None, 'win_': None}
            self.temp = [4, 5, 8, config]

    def do_braching(self, frame, current_link):
        if current_link == 42:
            frame.choices[0].link = 43
            frame.choices[1].link = 521
            self.temp = 0
        elif current_link == 46:
            frame.choices[0].link = 47
            frame.choices[1].link = 522
            self.temp = 1
        elif current_link == 43 or current_link == 47:
            self.temp *= 2
        elif current_link == 521 or current_link == 522:
            self.temp *= 2
            self.temp += 1
        elif current_link == 44:
            if self.temp % 2 == 0:
                frame.next_link = 45
            else:
                frame.next_link = 523
        elif current_link == 48:
            if self.temp % 2 == 0:
                frame.next_link = 49
            else:
                frame.next_link = 524
        elif current_link == 56:
            x = self.temp // 2
            frame.choices = self.saves['branch_ch'][x]
        elif current_link == 59:
            if self.temp // 2 == 0:
                frame.choices = None
            else:
                frame.choices = self.saves['branch_ch'][2]

        # Ветвление2
        elif current_link == 64 or current_link == 65:
            self.temp = 65 - current_link
        elif current_link == 67:
            self.temp += 1


    def do_games(self, frames, last_frame, current_link):
        # Миниигра вопросы
        if current_link in core.constants.question_range:
            q = (current_link - 71) // 5
            if self.temp == 2:
                choice = 68 + q
            else:
                screen = ChoiceScreen(self, self.frame, last_frame, q + 1)
                screen.loop()
                if screen.temp:
                    return None
                choice = screen.result
        # Миниигра драка
        elif current_link in core.constants.fight_range:
            screen = ChoiceScreen(self, self.frame, last_frame, -1)
            screen.fight_config = self.temp
            screen.loop()
            if screen.temp:
                return None
            x = screen.result

            choice, res = self.fight(x)
            if choice != res:
                frames[choice].choices = None
                frames[choice].next_link = res
        # Миниигра поиск
        elif current_link in constants.search_range or current_link in constants.search_range_after:
            if self.score >= 2:
                choice = 113
            else:
                if current_link == 109 and isinstance(self.frame.choices[1].dialog, core.Prob):
                    pr = self.frame.choices[1].dialog
                    pr.high = True
                    pr.update(pr.x)
                x = 0
                while x == 0:
                    screen = ChoiceScreen(self, self.frame, last_frame, -2)
                    screen.loop()
                    if screen.temp:
                        return None
                    x = screen.result
                    if x == 0:
                        screen = ChoiceScreen(self, self.frame, last_frame, -3)
                        screen.loop()
                choice = screen.result
                self.score += 1
                self.time.add(minutes=20)
        # Обычный экран
        else:
            screen = ChoiceScreen(self, self.frame, last_frame)
            screen.loop()
            choice = screen.result
        return choice

    def handle_extra_frame(self, last_frame, frames, cond, link):
        l = 113 + cond
        frame = frames[l]
        if frame:
            if cond == 1:
                t = 88 if link == 70 else link
                choice = frame.choices[t - 85]
            else:
                choice = frame.choices[link - 98]

            result = core.reward_player(choice, self, frame.choices, link, last_frame)
            if result:
                frames.remove(l)


    def start(self, current_link):
        frames = self.cache['frames']
        endings = self.cache['endings']
        while True:
            if current_link < 141 or current_link > 500:
                last_frame = None
                if current_link == 0:
                    sc = PubgScreen(self)
                    sc.loop()
                    current_link = core.constants.checkpoints[2]
                    if sc.temp:
                        return
                    continue

                self.frame = frames[current_link]
                if current_link in core.constants.checkpoints[1:3]:
                    endings[144].next_link = current_link
                elif current_link in (70, 71, 88, 101, 105):
                    self.init_games(current_link)
                # Ветвление
                elif current_link in (42, 43, 44, 46, 47, 48, 521, 522, 56, 59, 64, 65, 67):
                    self.do_braching(self.frame, current_link)

                # Доп.фреймы
                if last_frame:
                    if current_link in (70, 85, 86, 87):
                        self.handle_extra_frame(last_frame, frames, 1, current_link)
                    elif current_link in (98, 99, 100):
                        self.handle_extra_frame(last_frame, frames, 2, current_link)

                last_frame = play_video(self)
                if last_frame is None:
                    return

                if self.frame.choices:
                    current_link = self.do_games(frames, last_frame, current_link)
                    if current_link is None:
                        return
                else:
                    # Миниигра вопросы
                    if current_link in core.constants.question_range:
                        current_link = self.questioning(current_link)
                    # Миниигра драка
                    elif current_link in core.constants.fight_range:
                        self.frame.choices = frames[88].choices
                        current_link = self.frame.next_link
                        core.constants.fight_s.stop()
                    else:
                        current_link = self.frame.next_link

            else:
                if current_link not in self.collection['endings']:
                    self.collection['endings'].add(current_link)
                    self.unseen['endings'].add(current_link)
                frame = endings[current_link]
                sc = EndingScreen(self, current_link)
                sc.loop()
                if sc.temp:
                    return
                current_link = frame.next_link

    def save(self):
        with open(save_path, 'wb') as f:
            save_dat = {
                'collection': self.collection,
                'plus_factor': self.plus_factor,
                'unseen': self.unseen,
                'saves': self.saves,
                'block': self.block,
                'settings': self.settings,
                'cache': self.cache
            }
            pickle.dump(save_dat, f)

        if self.saves['sw'] < len(self.frame_s):
            with open(save_path2, 'wb') as f:
                pickle.dump(tuple(self.frame_s), f)
                self.saves['sw'] = len(self.frame_s)


if __name__ == "__main__":
    save_path = core.res('saves/main.dat')
    save_path2 = core.res('saves/widgets.dat')
    game = Main()

    while True:
        if not game.block[1]:
            screen = DisclaimerScreen(game)
            screen.loop()
            game.block[1] = True

        screen = MainMenu(game)
        screen.loop()
        if screen.temp == 0:
            break
        game.start(screen.temp)

    game.exit_game()
