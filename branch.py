import core
import pygame
from screen import Screen
from io import BytesIO
from PIL import Image


class MyWidget:
    __slots__ = ("choices", "thumb_key", "time", "temp", "_frame_surface", "selected",
                 "mark", "_rect", "font", "colors", "button_labels", "buttons")
    def __init__(self, choices, last_frame, _time, temp):
        self.colors = None
        self.button_labels = None
        self.buttons = None
        self._rect = None
        self.choices = choices
        self.font = None

        if isinstance(last_frame, pygame.Surface):
            base = last_frame
        else:
            base = pygame.surfarray.make_surface(last_frame.swapaxes(0, 1))

        self._frame_surface = base.convert()
        self.thumb_key = id(self)
        self.time = _time
        self.temp = temp
        self.selected = False
        self.mark = False

    def rect(self, new_value):
        self._rect = new_value
        self.font = pygame.font.Font(core.constants.text_font, int(new_value.width * 0.03))

    def update_geom(self, game):
        txt = game.locale.txt
        self.buttons = core.get_geometry(self.choices, self.font, self._rect, txt)
        core.update_choice(self, txt)

    def draw(self, screen):
        thumb = core.THUMBS.get(self.thumb_key, self._frame_surface, (self._rect.w, self._rect.h))
        screen.blit(thumb, self._rect.topleft)

        if self.selected:
            c = core.constants.color_title
        else:
            c = core.constants.color_front
        pygame.draw.rect(screen, c, self._rect, width=2)

        for rect, label, color in zip(self.buttons, self.button_labels, self.colors):
            shifted_rect = rect.move(self._rect.topleft)
            Screen.draw_button_static(shifted_rect, label, screen, self.font, color_b=color[0], color_t=color[1])

    def __getstate__(self):
        state = {slot: getattr(self, slot) for slot in self.__slots__[:4]}
        surf = getattr(self, '_frame_surface', None)

        if surf:
            raw_str = pygame.image.tostring(surf, "RGB")
            pil_img = Image.frombytes("RGB", surf.get_size(), raw_str)
            buf = BytesIO()
            pil_img.save(buf, format="JPEG", quality=75)  # сжимаем в JPEG
            state["_frame_surface"] = buf.getvalue()
        else:
            state["_frame_surface"] = None
        return state

    def __setstate__(self, state):
        for slot in self.__slots__[:5]:
            setattr(self, slot, state[slot])

        fb = state.get('_frame_surface')
        if fb:
            buf = BytesIO(fb)
            pil_img = Image.open(buf).convert("RGB")
            size = pil_img.size
            mode = pil_img.mode
            surf = pygame.image.fromstring(pil_img.tobytes(), size, mode)
            self._frame_surface = surf.convert()
        else:
            self._frame_surface = None

        setattr(self, "selected", False)
        setattr(self, "mark", False)
        for slot in self.__slots__[7:]:
            setattr(self, slot, None)


class TreeChoiceScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.scroll_start_x = None
        self.drag_start_x = None
        self.shifted_rects = None
        self.exit_label = None
        self.widget_size = None
        self.widgets = None
        self.y = None
        self.spacing = None
        self.event_pos = None

        self.scroll_x = 0
        self.target_scroll_x = 0
        self.dragging = False
        self.game = game
        game.score = 0.008
        self.result = None
        self.exit = None

        # ---- Параметры разгона ----
        self.scroll_base = 50.0  # px/сек — базовая
        self.scroll_accel = 200.0  # px/сек^2 — ускорение
        self.scroll_cap = 300.0  # px/сек — максимум
        self.accel_delay = 0.10  # сек — задержка до разгона

        # ---- Служебное ----
        self._hold_dir = 0  # -1 (влево), +1 (вправо), 0 — нет удержания
        self._hold_start_ms = 0
        self._key_timer_event = pygame.USEREVENT + 5
        self._key_tick_ms = 16  # ~60 Гц; можно 20-33мс

        # На всякий случай удостоверимся, что таймер не активен:
        pygame.time.set_timer(self._key_timer_event, 0)

        self.selected_frame_idx = None  # индекс виджета (int)
        self.selected_choice_idx = None  # индекс кнопки внутри виджета (int)
        self.update()


    def update(self):
        spacing = 562.5 * self.x_100 * self.game.score
        self.spacing = spacing
        widget_size = (500*self.x_100*self.game.score, 375*self.y_100*self.game.score)
        self.y = 3.5 * self.y_100 + widget_size[1]
        y = self.y_100 * 1.8
        x = self.x_100 * 1.2

        self.widgets = []
        self.widget_size = widget_size
        frames = self.game.frame_s
        for i, frame in enumerate(frames):
            rect = pygame.Rect(x + i * spacing, y, *self.widget_size)
            frame.rect(rect)
            frame.update_geom(self.game)
            self.widgets.append(frame)

        max_scroll = self._max_scroll()
        self.target_scroll_x = max(0, min(self.target_scroll_x, max_scroll))

        dx_smooth = self.target_scroll_x - self.scroll_x
        self.scroll_x = self.target_scroll_x if abs(dx_smooth) < 1 else self.scroll_x + dx_smooth * 0.2

        # Ограничение прокрутки
        max_scroll = self._max_scroll()
        self.target_scroll_x = max(0, min(self.target_scroll_x, max_scroll))

        # Плавное движение scroll_x к target_scroll_x
        dx = self.target_scroll_x - self.scroll_x
        if abs(dx) < 1:
            self.scroll_x = self.target_scroll_x
        else:
            self.scroll_x += dx * 0.2  # коэф. сглаживания

        w = 2.5 * self.x_100
        h = self.y_100 // 2
        self.exit = pygame.Rect(self.size[0] - self.x_100 * 1.5 - w, self.size[1] - self.y_100*1.25, w, h)
        self.exit_label = self.game.locale.tmenu[7]
        self.shifted_rects = [w._rect.move(-self.scroll_x, 0) for w in self.widgets]

    def _press_button(self):
        if self.selected_frame_idx is None or self.selected_choice_idx is None:
            return
        frame = self.widgets[self.selected_frame_idx]
        choice = frame.choices[self.selected_choice_idx]
        self.result = (frame, choice.link)
        self.stop()

    def _max_scroll(self):
        x = self.x_100 * 1.2
        return max(0, len(self.widgets) * self.spacing - self.size[0] + x)

    def _ensure_widget_visible(self, idx, margin=30):
        """Если выбранный виджет не в видимой области — плавно доводим target_scroll_x."""
        if idx is None or not self.widgets:
            return
        wr = self.widgets[idx]
        shifted = wr._rect.move(-self.scroll_x, 0)
        left_limit = margin
        right_limit = self.size[0] - margin

        if shifted.left < left_limit:
            delta = left_limit - shifted.left
            self.target_scroll_x = max(0, self.scroll_x - delta)
        elif shifted.right > right_limit:
            delta = shifted.right - right_limit
            self.target_scroll_x = min(self._max_scroll(), self.scroll_x + delta)

    def _clear_all_selected_flags(self):
        for w in self.widgets:
            w.selected = False
            for ch in w.choices:
                ch.selected = False

    def _set_selected(self, frame_idx=None, choice_idx=None):
        """Выделяем виджет и (опционально) вариант внутри него; обновляем флаги selected."""
        self._clear_all_selected_flags()
        self.selected_frame_idx = frame_idx
        self.selected_choice_idx = None

        if frame_idx is not None:
            self.widgets[frame_idx].selected = True

            if choice_idx is not None and 0 <= choice_idx < len(self.widgets[frame_idx].choices):
                self.selected_choice_idx = choice_idx
                self.widgets[frame_idx].choices[choice_idx].selected = True
                # чтобы цвета/подписи обновились верно
                self.widgets[frame_idx].update_geom(self.game)

    def handle_event(self, event):
        super().handle_event(event)
        c = self.x_100 * 0.6
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.stop()
                return
            elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                # если уже удерживаем противоположную — переключаемся
                dir_new = -1 if event.key == pygame.K_LEFT else +1
                now = pygame.time.get_ticks()
                # старт или смена направления
                if self._hold_dir != dir_new:
                    self._hold_dir = dir_new
                    self._hold_start_ms = now
                # мгновенный «пинок» на базовой скорости (по вкусу)
                step = self.scroll_base * (self._key_tick_ms / 1000.0)
                self.target_scroll_x += step * self._hold_dir
                # включаем свой тикер, если он не включён
                pygame.time.set_timer(self._key_timer_event, self._key_tick_ms)

            elif event.key in (pygame.K_a, pygame.K_d):
                if not self.widgets:
                    return
                if self.selected_frame_idx is None:
                    # первый выбор — ближайший видимый
                    self._set_selected(0, 0 if self.widgets[0].choices else None)
                else:
                    if event.key == pygame.K_a and self.selected_frame_idx > 0:
                        self._set_selected(self.selected_frame_idx - 1, 0)
                    elif event.key == pygame.K_d and self.selected_frame_idx + 1 < len(self.widgets):
                        self._set_selected(self.selected_frame_idx + 1, 0)
                self._ensure_widget_visible(self.selected_frame_idx)

            elif event.key in (pygame.K_w, pygame.K_s):
                if self.selected_frame_idx is None:
                    return
                n = len(self.widgets[self.selected_frame_idx].choices)
                if n == 0:
                    return
                ci = 0 if self.selected_choice_idx is None else self.selected_choice_idx
                ci = (ci + (1 if event.key == pygame.K_s else -1)) % n
                self._set_selected(self.selected_frame_idx, ci)

            elif event.key == pygame.K_RETURN:
                self._press_button()

            elif event.key in (pygame.K_KP_PLUS, pygame.K_KP_MINUS, pygame.K_MINUS, pygame.K_EQUALS):
                if event.mod & pygame.KMOD_CTRL:
                    x = 1 if event.key in (pygame.K_KP_PLUS, pygame.K_EQUALS) else -1
                    self.game.score += 0.0005 * x
                    if self.game.score < 0.005:
                        self.game.score = 0.005
                    elif self.game.score > 0.015:
                        self.game.score = 0.015

        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                # Нажатые две стрелки? Если отпустили ту, что активна — глушим.
                # (Можно усложнить: проверить вторую клавишу и переключиться на неё.)
                self._hold_dir = 0
                pygame.time.set_timer(self._key_timer_event, 0)

        # 3) Потеря фокуса — обязательно глушим, чтобы не «залипало»
        elif event.type == pygame.WINDOWFOCUSLOST or event.type == pygame.ACTIVEEVENT:
            # В новых pygame есть WINDOWFOCUSLOST, в старых — ACTIVEEVENT c gain=0/state=1
            self._hold_dir = 0
            pygame.time.set_timer(self._key_timer_event, 0)

        # 4) Наш таймерный тик — двигаем с разгонами
        elif event.type == self._key_timer_event and self._hold_dir != 0:
            now = pygame.time.get_ticks()
            held = max(0.0, (now - self._hold_start_ms) / 1000.0)  # в секундах
            t = max(0.0, held - self.accel_delay)  # задержка старта
            # v = v0 + a*t, с капом
            v = min(self.scroll_base + self.scroll_accel * t, self.scroll_cap)
            # смещение за тик
            step = v * (self._key_tick_ms / 1000.0)
            self.target_scroll_x += step * self._hold_dir

            # кламп скролла
            max_scroll = self._max_scroll()
            if self.target_scroll_x < 0:
                self.target_scroll_x = 0
            elif self.target_scroll_x > max_scroll:
                self.target_scroll_x = max_scroll

        elif event.type == pygame.MOUSEWHEEL:
            if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                self.target_scroll_x -= event.y * c
            else:
                self.target_scroll_x -= event.x * c

            self.game.score += 0.0005 * event.y
            if self.game.score < 0.005:
                self.game.score = 0.005
            elif self.game.score > 0.015:
                self.game.score = 0.015

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.exit.collidepoint(event.pos):
                core.constants.click.play()
                self.stop()
                return

            # клик по кнопке внутри какого-то виджета
            for i, (w, shifted) in enumerate(zip(self.widgets, self.shifted_rects)):
                if not shifted.collidepoint(event.pos):
                    continue
                # проверяем его кнопки
                for j, brect in enumerate(w.buttons):
                    # локальная кнопка -> экранные координаты:
                    btn_rect_screen = brect.move(shifted.topleft)
                    if btn_rect_screen.collidepoint(event.pos):
                        self._set_selected(i, j)
                        self._ensure_widget_visible(i)
                        self._press_button()
                        return

            self.dragging = True
            self.drag_start_x = event.pos[0]
            self.scroll_start_x = self.target_scroll_x

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                dx = event.pos[0] - self.drag_start_x
                self.target_scroll_x = min(self._max_scroll(), max(0, self.scroll_start_x - dx))
            # подсветка виджета рамкой под курсором
            under = None
            for i, shifted in enumerate(self.shifted_rects):
                if shifted.collidepoint(event.pos):
                    under = i
                    break
            self._clear_all_selected_flags()

            if under is not None:
                # Подсветка всего виджета
                self.widgets[under].selected = True
                for ch in self.widgets[under].choices:
                    ch.selected = False

                for ci, button_rect in enumerate(self.widgets[under].buttons):
                    btn_rect_screen = button_rect.move(self.shifted_rects[under].topleft)
                    if btn_rect_screen.collidepoint(event.pos):
                        self.widgets[under].choices[ci].selected = True
                        break

    def draw(self):
        self.screen.fill(core.constants.color_back)
        shifted_rects = self.shifted_rects

        # Соединяем соседние виджеты линиями
        line_width = 3
        if shifted_rects:
            first = shifted_rects[0]
            start_point = (first.left - self.spacing // 2, first.centery)
            pygame.draw.line(self.screen, core.constants.color_menuwidget, start_point, first.center, width=line_width)

        for i in range(len(shifted_rects) - 1):
            p1 = shifted_rects[i].center
            p2 = shifted_rects[i + 1].center
            pygame.draw.line(self.screen, core.constants.color_menuwidget, p1, p2, width=line_width)

        if shifted_rects:
            last = shifted_rects[-1]
            x = max(last.right + self.spacing // 2, self.screen.get_size()[0])
            end_point = (x, last.centery)
            pygame.draw.line(self.screen, core.constants.color_menuwidget, last.center, end_point, width=line_width)

        # Отображаем виджеты
        y = 0.3 * self.y_100
        yc = y + self.x_100 * 0.5
        for widget, shifted in zip(self.widgets, shifted_rects):
            saved = widget._rect
            widget._rect = shifted
            widget.draw(self.screen)

            s = widget.time.strftime('%H:%M:%S')
            size = self.game.font.size(s)
            cord = (widget._rect.centerx - size[0] // 2, yc - size[1] // 2)
            self.screen.blit(self.game.font.render(s, True, core.constants.color_front), cord)
            if widget.thumb_key in self.game.unseen['frames']:
                self.draw_badge_internal(cord[0]+size[0], cord[1])
                widget.mark = True

            cord = (widget._rect.midtop[0], yc + size[1])
            pygame.draw.line(self.screen, core.constants.color_menuwidget, widget._rect.midtop, cord, width=line_width)
            widget._rect = saved

        # Текст
        tmenu = self.game.locale.tmenu
        y = self.y
        x = self.x_100 * 1.5
        w = self.x_100 * 3
        h = self.y_100 * 0.6
        r = pygame.Rect(x, y, w, h)
        n = len(self.game.frame_s)
        pos = Screen.draw_button_static(r, f'{tmenu[20]} ({n}/28):', self.screen, self.game.font,
                                  color_b=core.constants.color_back, color_t=core.constants.color_front)
        self.draw_badge(pygame.Rect(*pos, 0, 0), len(self.game.unseen['frames']))
        y += h*1.3
        r = pygame.Rect(x, y, w, h)
        n = self.game.collection['speedrun']
        pos = Screen.draw_button_static(r, f':speedrun: {tmenu[21]} ({n}/10)', self.screen, self.game.font_text,
                                  color_b=core.constants.color_back, color_t=core.constants.color_front)
        self.draw_badge(pygame.Rect(*pos, 0, 0), self.game.unseen['speedrun'])
        y += h
        r = pygame.Rect(x, y, w, h)
        n = len(self.game.collection['biography'])
        Screen.draw_button_static(r, f':biography: {tmenu[5]} ({n}/11)', self.screen, self.game.font_text,
                                  color_b=core.constants.color_back, color_t=core.constants.color_front)
        y += h
        r = pygame.Rect(x, y, w, h)
        n = len(self.game.collection['endings'])
        Screen.draw_button_static(r, f':ending: {tmenu[6]} ({n}/12)', self.screen, self.game.font_text,
                                  color_b=core.constants.color_back, color_t=core.constants.color_front)

        y += h
        r = pygame.Rect(x, y, w, h)
        n = self.game.collection['death']
        pos = Screen.draw_button_static(r, f':death: {tmenu[22]} ({n}/6)', self.screen, self.game.font_text,
                                  color_b=core.constants.color_back, color_t=core.constants.color_front)
        self.draw_badge(pygame.Rect(*pos, 0, 0), self.game.unseen['death'])

        # Exit button
        self.draw_button(self.exit, self.exit_label, False, None)

    def stop(self):
        # Сбрасываем динамические состояния ввода
        self.dragging = False
        self.selected_choice_idx = None

        self.game.unseen['frames'].difference_update({w.thumb_key for w in self.widgets if w.mark})
        self.game.unseen['speedrun'] = 0
        self.game.unseen['death'] = 0
        super().stop()