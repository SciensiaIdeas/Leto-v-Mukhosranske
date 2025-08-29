from screen import Screen
import core
import pygame
from screen import SettingsScreen, Information
import numpy as np
from text import read_description


class ChoiceScreen(Screen):
    def __init__(self, game, frame, last_frame, type=0):
        super().__init__(game)
        self.game = game
        if isinstance(last_frame, pygame.Surface):
            base = last_frame
        else:
            base = pygame.surfarray.make_surface(last_frame.swapaxes(0, 1))

        self.frame_surface = base.convert()

        w = 0
        if type == -2:
            probs = [ch.dialog for ch in frame.choices if isinstance(ch.dialog, core.Prob)]
            if probs and all(not fr.open for fr in probs):
                self.choices = frame.choices.copy()
                self.choices.append(core.Choice(game.locale.txt[99], False, 0))
                self._add_bet_option = True
            else:
                self.choices = frame.choices
                self._add_bet_option = False

            # Подсказка (чтоб игрок не забыл)
            if not game.block[3]:
                content = core.res(f'subs/{game.settings['lang']}/tip4')
                sc = Information(game, self.frame_surface, game.locale.tmenu[40], content)
                sc.loop()
                game.block[3] = True
        elif type == -3:
            self.choices = [ch for ch in frame.choices if isinstance(ch.dialog, core.Prob) and not ch.dialog.open]
            w = self.x_100 * 0.8
        else:
            self.choices = frame.choices
        self.buttons = core.get_geometry(self.choices, self.game.font, self.screen, game.locale.txt, w)
        self.button_labels = []
        self.colors = []
        self.result = None
        self.type = type
        self.selected_choice = None
        self.event_pos = None
        self.link = frame.link

        if type == -3:
            # --- мини-игра ставок ---
            pygame.mixer.music.load(core.constants.searching)
            pygame.mixer.music.play(loops=-1)
            self._gameindex = 0 if self.link == 101 else 1
            N = game.saves['max_credits'][self._gameindex]
            if N < 8:
                initial_bet = min(game.saves['credits'], N / 2)
                a = initial_bet / len(self.choices)
                self._bet_inc = N / 16
            else:
                initial_bet = min(game.saves['credits'], N // 2)
                a = initial_bet // len(self.choices)
                self._bet_inc = 1
            core.Prob.update_d(N)

            self._bet_spend = a * len(self.choices)
            self._bet_min = a
            self._bet_m = a
            self._bet_max = min(self.game.saves['credits'], int(0.8*N))
            self._bet_tri = []
            self._ok_rect = None
            self._cancel_rect = None
            self._bet_gap = 6
            self._tri_w = 18
            self._tri_h = 14
            for choice in (ch for ch in self.choices if isinstance(ch.dialog, core.Prob) and not ch.dialog.open):
                choice.dialog.update(a)
        elif type == -1:
            self.heart_icon = pygame.image.load(core.res('media/heart.png')).convert_alpha()
            self.clock_icon = pygame.image.load(core.res('media/clock.png')).convert_alpha()

            # Подсказка (чтоб игрок не забыл)
            if not game.block[2]:
                content = core.res(f'subs/{game.settings['lang']}/tip3')
                sc = Information(game, self.frame_surface, game.locale.tmenu[39], content)
                sc.loop()
                game.block[2] = True

            if frame.link == 88:
                core.constants.fight_s.set_volume(self.game.settings['volume'] / 2)
                self.game.fight_ss = core.constants.fight_s.play()
            self.fight_config = None
        self.update()

    def _press_button(self):
        if not self.selected_choice:
            return

        choice = self.selected_choice
        if isinstance(choice.dialog, core.Prob):
            prob = choice.dialog
            if prob.open:
                if prob.dotry():
                    choice.dialog = False
                    self.result = choice.link
                    self.stop()
                else:
                    self.result = -1
                    core.constants.wrong.play()
            else:
                self.result = -1
                core.constants.wrong.play()
        else:
            self.result = choice.link
            self.stop()

        if self.type != -1 and self.result != -1:
            if self.link == 67:
                choices = self.game.cache['frames'][66].choices
                x = self.game.temp
                self.game.temp = 0
                core.reward_player(choice, self.game, choices, 66, self.frame_surface)
                self.game.temp = x
            else:
                core.reward_player(choice, self.game, self.choices, self.link, self.frame_surface)

        if self.type == -2 and not self._add_bet_option:
            probs = [ch.dialog for ch in self.choices if isinstance(ch.dialog, core.Prob)]
            if probs and all(not p.open for p in probs):
                # не трогай исходный список, делай копию
                self.choices = self.choices.copy()
                self.choices.append(core.Choice(self.game.locale.txt[99], False, 0))
                self._add_bet_option = True

                # пересчитать UI
                self.buttons = core.get_geometry(self.choices, self.game.font, self.screen, self.game.locale.txt)
                self.button_labels.clear()
                self.colors.clear()
                core.update_choice(self, self.game.locale.txt)

    def predicate(self, choice) -> bool:
        return isinstance(choice.dialog, core.Prob) and not (choice.dialog.open or self.type == -3)

    def handle_event(self, event):
        super().handle_event(event)

        if event.type == pygame.MOUSEMOTION:
            if event.pos != self.event_pos:
                self.event_pos = event.pos
                self.selected_choice = None

            for button_rect, choice in zip(self.buttons, self.choices):
                if button_rect.collidepoint(event.pos):
                    if not self.predicate(choice):
                        self.selected_choice = choice
                        choice.selected = True
                    else:
                        choice.selected = False
                else:
                    choice.selected = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.type == -3:
                # клики по треугольникам
                for i, (up_r, dn_r) in enumerate(self._bet_tri):
                    if up_r.collidepoint(event.pos):
                        step = 5 if (pygame.key.get_mods() & pygame.KMOD_SHIFT) else 1
                        self.selected_choice = self.choices[i]
                        self._change_bet(step)
                        break
                    if dn_r.collidepoint(event.pos):
                        step = 5 if (pygame.key.get_mods() & pygame.KMOD_SHIFT) else 1
                        self.selected_choice = self.choices[i]
                        self._change_bet(-step)
                        break

                # ОК / Отмена
                if self._ok_rect and self._ok_rect.collidepoint(event.pos):
                    # принять ставки: списать кредиты и зафиксировать
                    self._commit_bet()

                if self._cancel_rect and self._cancel_rect.collidepoint(event.pos):
                    self.stop()
            else:
                self._press_button()


        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.type == -3:
                    self.stop()
                else:
                    if self.type == -2:
                        t = 4
                    elif self.type == -1:
                        t = 3
                    else:
                        t = 2

                    screen = SettingsScreen(self.game, self.frame_surface, t)
                    screen.loop()
                    if screen.temp:
                        self.temp = True
                        self.stop()

            elif pygame.K_1 <= event.key <= pygame.K_9:
                digit = event.key - pygame.K_1
                if digit < len(self.choices):
                    choice = self.choices[digit]
                    if not self.predicate(choice):
                        for ch in self.choices:
                            ch.selected = False
                        choice.selected = True
                        self.selected_choice = choice
                        self._press_button()

            elif event.key in (pygame.K_w, pygame.K_s):
                valid_choices = [
                    (i, ch) for i, ch in enumerate(self.choices)
                    if not self.predicate(ch)
                ]
                if not valid_choices:
                    return

                selected_index = next((i for i, ch in enumerate(self.choices) if ch.selected), -1)

                if selected_index == -1:
                    next_index = valid_choices[0][0]
                else:
                    valid_indexes = [i for i, _ in valid_choices]
                    current_pos = valid_indexes.index(selected_index)
                    if event.key == pygame.K_s:
                        next_index = valid_indexes[(current_pos + 1) % len(valid_indexes)]
                    else:
                        next_index = valid_indexes[(current_pos - 1) % len(valid_indexes)]

                for ch in self.choices:
                    ch.selected = False
                self.choices[next_index].selected = True
                self.selected_choice = self.choices[next_index]

            elif self.type == -3 and event.key in (pygame.K_UP, pygame.K_DOWN):
                # ↑/↓ управляют ставкой выбранного Prob
                step = 5 if (pygame.key.get_mods() & pygame.KMOD_SHIFT) else 1
                if event.key == pygame.K_UP:
                    self._change_bet(step)
                else:
                    self._change_bet(-step)

            elif event.key == pygame.K_RETURN:
                if self.type == -3:
                    self._commit_bet()
                else:
                    self._press_button()


    def update(self):
        core.update_choice(self, self.game.locale.txt)

        if self.type == -3:
            self._bet_tri = []
            pad = self._bet_gap
            tw, th = self._tri_w, self._tri_h
            for rect in self.buttons:
                # рисуем треугольники справа внутри кнопки
                x_right = rect.right - pad - tw
                y_center = rect.centery
                up_rect = pygame.Rect(x_right, y_center - th - pad, tw, th)
                down_rect = pygame.Rect(x_right, y_center + pad, tw, th)
                self._bet_tri.append((up_rect, down_rect))

            # нижняя панель "ОК | кредиты | Отмена"
            w_btn = int(self.size[0] * 0.12)
            h_btn = int(self.y_100 * 0.48)
            y = self.size[1] - int(self.y_100 * 1.1)
            x_left = self.buttons[0].x
            x_right = self.buttons[0].right
            self._ok_rect = pygame.Rect(x_left, y, w_btn, h_btn)
            self._cancel_rect = pygame.Rect(x_right - w_btn, y, w_btn, h_btn)


    def draw(self):
        self.screen.blit(pygame.transform.scale(self.frame_surface, self.size), (0, 0))
        # Драка
        if self.type == -1:
            size = self.size
            s = min(*size) // 20
            icon_size = (s, s)
            heart_icon = pygame.transform.scale(self.heart_icon, icon_size)
            clock_icon = pygame.transform.scale(self.clock_icon, icon_size)
            spacing = s // 6
            x_50 = int(0.024 * size[0])
            y_30 = int(0.026 * size[1])
            y_50 = int(0.043 * size[1])
            for i in range(self.fight_config[0]):
                x = size[0] - (icon_size[0] + spacing) * (i + 1) - x_50
                y = size[1] - icon_size[1] - y_30
                self.screen.blit(heart_icon, (x, y))

            for i in range(self.fight_config[1]):
                x = x_50 + (icon_size[0] + spacing) * i
                y = size[1] - icon_size[1] - y_30
                self.screen.blit(heart_icon, (x, y))

            # Отображение оставшегося времени
            t = self.fight_config[2]
            x0 = (size[0] - icon_size[0] * t - spacing * (t - 1)) // 2
            y = y_50
            for i in range(t):
                x = x0 + (icon_size[0] + spacing) * i
                self.screen.blit(clock_icon, (x, y))

        for rect, label, color in zip(self.buttons, self.button_labels, self.colors):
            self.draw_button(rect, label, False, None, color_b=color[0], color_t=color[1])

        if self.type > 0:
            size = self.size
            description = core.res(f'subs/{self.game.settings['lang']}/question{self.type}')
            s = (size[0] - 100, size[1] * 0.08)
            pygame.draw.rect(self.screen, core.constants.color_back, (50, 50, *s))
            read_description(description, s, (50, 50), self.screen, self.game.font_text)

        if self.type == -3:
            # треугольники
            tri_color = core.constants.color_txtused
            for (up_r, dn_r), ch in zip(self._bet_tri, self.choices):
                # up triangle
                ux, uy, uw, uh = up_r
                up_points = [(ux + uw // 2, uy), (ux + uw, uy + uh), (ux, uy + uh)]
                pygame.draw.polygon(self.screen, tri_color, up_points)

                # down triangle
                dx, dy, dw, dh = dn_r
                dn_points = [(dx, dy), (dx + dw, dy), (dx + dw // 2, dy + dh)]
                pygame.draw.polygon(self.screen, tri_color, dn_points)

            # нижняя панель: ОК | кредиты | Отмена
            left_text = self.game.font.render("OK", True, core.constants.color_back)
            right_text = self.game.font.render(self.game.locale.tmenu[23], True, core.constants.color_back)
            s = f'{self.game.locale.tmenu[24]}: {self.game.saves['attempts'][self._gameindex]}'
            attempt_text = self.game.font_title.render(s, True, core.constants.color_back)

            # кнопки
            pygame.draw.rect(self.screen, core.constants.color_menuwidget, self._ok_rect, border_radius=6)
            pygame.draw.rect(self.screen, core.constants.color_menuwidget, self._cancel_rect, border_radius=6)

            # текст на кнопках
            lt = left_text.get_rect(center=self._ok_rect.center)
            rt = right_text.get_rect(center=self._cancel_rect.center)
            y = self._ok_rect.topleft[1]
            center = (self.buttons[0].centerx, y - self.y_100)
            ct = attempt_text.get_rect(center=center)
            self.screen.blit(left_text, lt)
            self.screen.blit(right_text, rt)
            self.screen.blit(attempt_text, ct)

            # кредиты между кнопками
            val = round(self.game.saves['credits'] - self._bet_spend, 1)
            credits_str = f":fly: {val}"
            w = self.x_100 * 1.8
            r = pygame.Rect(center[0] - w // 2, y, w, self.y_100 * 0.5)
            Screen.draw_button_static(r, credits_str, self.screen, self.game.font_title,
                                      color_b=core.constants.color_front)

    def _change_bet(self, x):
        ch = self.selected_choice
        bet = ch.dialog.x
        bet_new = bet + x * self._bet_inc
        if self._bet_spend+x <= self._bet_max and bet_new>0 and bet_new/self._bet_min<=3 and self._bet_m/bet_new<=3:
            self._bet_spend += x * self._bet_inc
            self._bet_min = min(ch.dialog.x for ch in self.choices)
            self._bet_m = max(ch.dialog.x for ch in self.choices)
            ch.dialog.update(bet_new)
        else:
            core.constants.wrong.play()

    def _commit_bet(self):
        self.game.saves['credits'] -= self._bet_spend
        self.game.saves['max_credits'][self._gameindex] -= self._bet_spend
        self.game.saves['attempts'][self._gameindex] += 1
        for ch in self.choices:
            ch.dialog.open = True
        self.stop()

    def stop(self):
        if self.type == -3:
            pygame.mixer.music.stop()
        super().stop()


class PubgScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.game = game
        image = pygame.image.load(core.res('media/pubg.png'))
        array = pygame.surfarray.array3d(image)
        self.array_swapped = np.swapaxes(array, 0, 1)
        self.image = image
        self.update()

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.x1 < event.pos[0] < self.x2 and self.y1 < event.pos[1] < self.y2:
                core.constants.click.play()
                self.stop()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                screen = SettingsScreen(self.game, self.array_swapped, 2)
                screen.loop()
                if screen.temp:
                    # Выход в меню
                    self.temp = True
                    self.stop()

    def update(self):
        size = self.size
        self.x1 = 0.83 * size[0]
        self.y1 = 0.915 * size[1]
        self.x2 = 0.983 * size[0]
        self.y2 = 0.972 * size[1]

    def draw(self):
        stretched_image = pygame.transform.scale(self.image, self.size)
        self.screen.blit(stretched_image, (0, 0))

    def stop(self):
        super().stop()