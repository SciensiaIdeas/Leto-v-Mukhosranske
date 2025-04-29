import sys

import numpy as np
import pygame
import pygame.freetype
from moviepy.editor import VideoFileClip
import cv2
from PIL import Image, ImageDraw, ImageFont
import os
import core
import text
import moment
import pickle


class Main:
    def __init__(self, filepath = None):
        pygame.init()
        info = pygame.display.Info()
        screen_size = info.current_w, info.current_h
        self.screen = pygame.display.set_mode(screen_size, pygame.RESIZABLE)
        pygame.display.set_caption("Лето в Мухосранске")

        pygame.mixer.init()
        width = screen_size[0]
        self.font_sub = ImageFont.truetype("arial.ttf", int(0.012 * width))
        self.font = pygame.font.Font(None, int(0.03 * width))
        self.font_text = pygame.font.Font(None, int(0.025 * width))
        self.font_title = pygame.font.Font(None, int(0.049 * width))
        self.font_b = pygame.freetype.SysFont('Courier', int(0.02 * width))
        self.blue = (91, 155, 213)
        self.click = pygame.mixer.Sound(core.res('media/click.wav'))
        self.fight_s = pygame.mixer.Sound(core.res('media/fight.wav'))
        self.wrong = pygame.mixer.Sound(core.res('media/wrong.wav'))
        self.clock = pygame.mixer.Sound(core.res('media/clock.wav'))
        self.fight_ss = None
        self.click.set_volume(0.3)
        self.score = 0
        self.search = 0
        self.fighting = None
        self.skip_save = (49,50,53,54,55,56,63,65,67,68,69,70,71,72,73,74,75,76,77,78,79,84,85,86,87,88,89,90,91,92,101,102,103,104,105,106,107)
        self.frame_sb = None
        self.time_sb = None

        if filepath is None:
            self.block = -1
            self.endings = set()
            self.biography = {1}

            self.time = moment.date(2019, 6, 13)
            self.time = self.time.replace(hours=7)
            self.time_s = None
            self.time_ss = None

            self.frame_s = None
            self.frame = None
            self.frames = text.main()
            self.endings_ = text.main1()
            self.biography_ = text.main2()

            self.volume = 1.0
            self.subtitles = True
        else:
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
                self.block = data['block']
                self.endings = data['endings']
                self.biography = data['biography']
                self.time = data['time']
                self.time_s = data['time_s']
                self.time_ss = data['time_ss']
                self.frame_s = data['frame_s']
                self.frame = data['frame']
                self.endings_ = data['endings_']
                self.frames = data['frames']
                self.biography_ = data['biography_']
                self.volume = data['volume']
                self.subtitles = data['subtitles']

    def general_events(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            self.save()
            sys.exit()
        elif event.type == pygame.VIDEORESIZE:
            width = event.w
            self.font_sub = ImageFont.truetype("arial.ttf", int(0.012 * width))
            self.font = pygame.font.Font(None, int(0.03 * width))
            self.font_text = pygame.font.Font(None, int(0.025 * width))
            self.font_title = pygame.font.Font(None, int(0.049 * width))
            self.font_b = pygame.freetype.SysFont('Courier', int(0.02 * width))

    def show_settings(self, last_frame):
        frame_surface = pygame.surfarray.make_surface(last_frame.swapaxes(0, 1))
        pygame.mouse.set_visible(True)
        running = True
        while running:
            size = self.screen.get_size()
            self.screen.blit(pygame.transform.scale(frame_surface, size), (0, 0))
            x_100 = int(0.06 * size[0])
            y_100 = int(0.097 * size[1])
            for event in pygame.event.get():
                self.general_events(event)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if x_100 < event.pos[0] < 3*x_100 and 2.5*y_100 < event.pos[1] < 2.7*y_100:  # Ползунок громкости
                        self.volume = (event.pos[0] - x_100) / (2*x_100)
                        self.click.play()
                    if 2.8*x_100 < event.pos[0] < 3.1*x_100 and 3*y_100 < event.pos[1] < 3.3*y_100:  # Чекбокс субтитров
                        self.subtitles = not self.subtitles
                        self.click.play()
                    if x_100 < event.pos[0] < 4*x_100 and 3.9*y_100 < event.pos[1] < 4.3*y_100:  # Кнопка продолжить
                        running = False
                        self.click.play()
                    if x_100 < event.pos[0] < 4*x_100 and 4.5*y_100 < event.pos[1] < 4.9*y_100:  # Кнопка сохранить
                        link = self.frame.link
                        if link in self.skip_save:
                            self.time_ss = self.time_sb
                            self.frame_s = self.frame_sb
                        else:
                            self.time_ss = self.time_s
                            self.frame_s = self.frame
                        self.click.play()
                        running = False
                    if x_100 < event.pos[0] < 4*x_100 and 5.1*y_100 < event.pos[1] < 5.5*y_100:  # Кнопка выход
                        link = self.frame.link
                        if link in self.skip_save:
                            self.time = self.time_sb
                            self.frame = self.frame_sb
                        if self.fight_ss is not None:
                            if self.fight_ss.get_busy():
                                self.fight_ss.stop()
                        self.click.play()
                        self.main_menu()
                        return True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

            # Полупрозрачный фон
            overlay = pygame.Surface(size, pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            self.screen.blit(overlay, (0, 0))
            overlay = pygame.Surface((size[0] // 3, size[1]), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 128))
            self.screen.blit(overlay, (0, 0))

            black = (0, 0, 0)
            white = (255, 255, 255)
            width = 2*x_100; height = 0.2*y_100

            self.screen.blit(self.font.render("НАСТРОЙКИ", True, black), (1.2*x_100, y_100))
            self.screen.blit(self.font.render("Громкость", True, black), (x_100, 2*y_100))
            x = x_100; y = 2.5*y_100
            pygame.draw.rect(self.screen, self.blue, (x, y, width, height))
            pygame.draw.rect(self.screen, white, (x, y, self.volume * width, height))

            # Чекбокс субтитров
            x = 2.8*x_100; y = 3*y_100; s = 0.3*x_100
            self.screen.blit(self.font.render("Субтитры", True, black), (x_100, y - 3))
            pygame.draw.rect(self.screen, self.blue, (x, y, s, s))
            if self.subtitles:
                pygame.draw.line(self.screen, white, (x, y), (x + s, y + s), 3)
                pygame.draw.line(self.screen, white, (x, y + s), (x + s, y), 3)

            # Кнопки
            s1 = 0.4*y_100
            pygame.draw.rect(self.screen, self.blue, (x_100, 3.9*y_100, 3*x_100, s1))
            self.screen.blit(self.font.render("Продолжить", True, white), (1.4*x_100, 3.95*y_100))
            pygame.draw.rect(self.screen, self.blue, (x_100, 4.5*y_100, 3*x_100, s1))
            self.screen.blit(self.font.render("Сохраниться", True, white), (1.35*x_100, 4.55*y_100))
            pygame.draw.rect(self.screen, self.blue, (x_100, 5.1 * y_100, 3 * x_100, s1))
            self.screen.blit(self.font.render("Выход в меню", True, white), (1.2 * x_100, 5.15 * y_100))
            self.screen.blit(self.font_title.render(self.time.strftime('%H:%M:%S'), True, black), (1.3*x_100, 9.5 * y_100))

            pygame.display.flip()
        if self.fight_ss is not None:
            if self.fight_ss.get_busy():
                self.fight_s.set_volume(self.volume / 2)

    def show_ending(self, link):
        pygame.mouse.set_visible(True)
        image = pygame.image.load(core.res(f'media/end{link}.jpg'))
        loop = pygame.mixer.Sound(core.res('media/end.mp3'))
        loop.set_volume(0.3)
        running = True
        loop.play(loops=-1)
        description = core.res(f'subs/end{link}')
        while running:
            size = self.screen.get_size()
            x_100 = int(0.06 * size[0])
            y_100 = int(0.097 * size[1])
            w = 2.5 * x_100; h = y_100 // 2
            button_replay_pos = (x_100 // 2, size[1] - y_100)
            button_exit_pos = (size[0] - 3*x_100, size[1] - y_100)
            for event in pygame.event.get():
                self.general_events(event)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = event.pos
                    if button_replay_pos[0] <= mouse_pos[0] <= button_replay_pos[0] + w and \
                            button_replay_pos[1] <= mouse_pos[1] <= button_replay_pos[1] + h:
                        running = False
                        self.click.play()
                    elif button_exit_pos[0] <= mouse_pos[0] <= button_exit_pos[0] + w and \
                            button_exit_pos[1] <= mouse_pos[1] <= button_exit_pos[1] + h:
                        self.click.play()
                        loop.stop()
                        self.main_menu()
                        return

            h1 = size[1] // 2
            w1 = (size[0]-16*h1/9) // 2
            ending_image = pygame.transform.scale(image, (16*h1/9, h1))

            self.screen.fill((255, 255, 255))
            title_surface = self.font_title.render(self.endings_[link].name, True, (255, 0, 0))
            title_rect = title_surface.get_rect(center=(size[0] // 2, 0.6*y_100))
            self.screen.blit(title_surface, title_rect)
            self.screen.blit(ending_image, (w1, 1.2*y_100))

            text.read_description(description, (size[0]-0.4*x_100, h1-3*y_100), (0.2*x_100, h1+1.5*y_100), self.screen, self.font_text)

            d1 = x_100*1.25; d2 = y_100*0.25
            pygame.draw.rect(self.screen, self.blue, (*button_replay_pos, w, h))
            replay_surface = self.font.render("Переиграть", True, (255,255,255))
            replay_rect = replay_surface.get_rect(center=(button_replay_pos[0] + d1, button_replay_pos[1] + d2))
            self.screen.blit(replay_surface, replay_rect)
            pygame.draw.rect(self.screen, self.blue, (*button_exit_pos, w, h))
            exit_surface = self.font.render("Выход", True, (255,255,255))
            exit_rect = exit_surface.get_rect(center=(button_exit_pos[0] + d1, button_exit_pos[1] + d2))
            self.screen.blit(exit_surface, exit_rect)

            pygame.display.flip()
        loop.stop()

    def show_ending1(self, link, n):
        pygame.mouse.set_visible(True)
        image = pygame.image.load(core.res(f'media/end{link}.jpg'))
        description = core.res(f'subs/end{link}')
        while True:
            size = self.screen.get_size()
            x_100 = int(0.06 * size[0])
            y_100 = int(0.097 * size[1])
            w = 2.5 * x_100; h = y_100 // 2
            button_replay_pos = (x_100 // 2, size[1] - y_100)
            button_exit_pos = (size[0] - 3*x_100, size[1] - y_100)
            for event in pygame.event.get():
                self.general_events(event)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    if button_replay_pos[0] <= mouse_pos[0] <= button_replay_pos[0] + w and \
                            button_replay_pos[1] <= mouse_pos[1] <= button_replay_pos[1] + h:
                        self.click.play()
                        return -1
                    elif button_exit_pos[0] <= mouse_pos[0] <= button_exit_pos[0] + w and \
                            button_exit_pos[1] <= mouse_pos[1] <= button_exit_pos[1] + h:
                        self.click.play()
                        return 1
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return 0

            h1 = size[1] // 2
            w1 = (size[0]-16*h1/9) // 2
            ending_image = pygame.transform.scale(image, (16*h1/9, h1))

            self.screen.fill((255, 255, 255))
            title_surface = self.font_title.render(self.endings_[link].name, True, (255, 0, 0))
            title_rect = title_surface.get_rect(center=(size[0] // 2, 0.6*y_100))
            self.screen.blit(title_surface, title_rect)
            self.screen.blit(ending_image, (w1, 1.2*y_100))

            text.read_description(description, (size[0]-0.4*x_100, h1-3*y_100), (0.2*x_100, h1+1.5*y_100), self.screen, self.font_text)

            d1 = x_100*1.25; d2 = y_100*0.25
            pygame.draw.rect(self.screen, self.blue, (*button_replay_pos, w, h))
            t = "Выход" if n == 0 or n == 3 else "Предыдущий"
            replay_surface = self.font.render(t, True, (255,255,255))
            replay_rect = replay_surface.get_rect(center=(button_replay_pos[0] + d1, button_replay_pos[1] + d2))
            self.screen.blit(replay_surface, replay_rect)
            pygame.draw.rect(self.screen, self.blue, (*button_exit_pos, w, h))
            t = "Выход" if n == 2 or n == 3 else "Следующий"
            exit_surface = self.font.render(t, True, (255,255,255))
            exit_rect = exit_surface.get_rect(center=(button_exit_pos[0] + d1, button_exit_pos[1] + d2))
            self.screen.blit(exit_surface, exit_rect)

            pygame.display.flip()

    def show_biography(self, link, n):
        pygame.mouse.set_visible(True)
        image = pygame.image.load(core.res(f'media/chr{link}.png'))
        description = core.res(f'subs/chr{link}')
        while True:
            size = self.screen.get_size()
            x_100 = int(0.06 * size[0])
            y_100 = int(0.097 * size[1])
            w = 2.5 * x_100; h = y_100 // 2
            button_replay_pos = (x_100 // 2, size[1] - y_100)
            button_exit_pos = (size[0] - 3*x_100, size[1] - y_100)
            for event in pygame.event.get():
                self.general_events(event)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    if button_replay_pos[0] <= mouse_pos[0] <= button_replay_pos[0] + w and \
                            button_replay_pos[1] <= mouse_pos[1] <= button_replay_pos[1] + h:
                        self.click.play()
                        return -1
                    elif button_exit_pos[0] <= mouse_pos[0] <= button_exit_pos[0] + w and \
                            button_exit_pos[1] <= mouse_pos[1] <= button_exit_pos[1] + h:
                        self.click.play()
                        return 1
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return 0

            h1 = size[1] // 2
            w1 = (size[0]-16*h1/9) // 2
            ending_image = pygame.transform.scale(image, (16*h1/9, h1))

            self.screen.fill((255, 255, 255))
            self.screen.blit(ending_image, (w1, 0))

            black = (0, 0, 0)
            ch = self.biography_[link - 1]
            text1, rect1 = self.font_b.render(ch.name, fgcolor=black, style=pygame.freetype.STYLE_STRONG)
            text2, rect2 = self.font_b.render(ch.subtitle, fgcolor=black, style=pygame.freetype.STYLE_OBLIQUE)
            text3, rect3 = self.font_b.render(f'({ch.age} лет)', fgcolor=black, style=pygame.freetype.STYLE_NORMAL)
            y = h1+0.2*y_100
            x = 0.2*x_100
            self.screen.blit(text1, (x, y))
            x += rect1.w + 0.2 * x_100
            self.screen.blit(text3, (x, y))
            y += rect1.h + 0.1*y_100
            x = 0.2*x_100
            self.screen.blit(text2, (x, y))
            y += rect2.h + 0.3 * y_100

            text.read_description(description, (size[0]-0.4*x_100, h1-h-y), (0.2*x_100, y), self.screen, self.font_text)

            d1 = x_100*1.25; d2 = y_100*0.25
            pygame.draw.rect(self.screen, self.blue, (*button_replay_pos, w, h))
            t = "Выход" if n == 0 or n == 3 else "Предыдущий"
            replay_surface = self.font.render(t, True, (255,255,255))
            replay_rect = replay_surface.get_rect(center=(button_replay_pos[0] + d1, button_replay_pos[1] + d2))
            self.screen.blit(replay_surface, replay_rect)
            pygame.draw.rect(self.screen, self.blue, (*button_exit_pos, w, h))
            t = "Выход" if n == 2 or n == 3 else "Следующий"
            exit_surface = self.font.render(t, True, (255,255,255))
            exit_rect = exit_surface.get_rect(center=(button_exit_pos[0] + d1, button_exit_pos[1] + d2))
            self.screen.blit(exit_surface, exit_rect)

            pygame.display.flip()

    def show_guide(self):
        pygame.mouse.set_visible(True)
        if self.endings.__contains__(141):
            loop = pygame.mixer.Sound(core.res('media/guide.wav'))
            loop.set_volume(0.3)
            loop.play(loops=-1)
        running = True
        description = core.res('subs/guide')
        while running:
            size = self.screen.get_size()
            x_100 = int(0.06 * size[0])
            y_100 = int(0.097 * size[1])
            w = 2.5 * x_100; h = y_100 // 2
            button_exit_pos = ((size[0] - w) // 2, size[1] - y_100)
            for event in pygame.event.get():
                self.general_events(event)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = event.pos
                    if button_exit_pos[0] <= mouse_pos[0] <= button_exit_pos[0] + w and \
                            button_exit_pos[1] <= mouse_pos[1] <= button_exit_pos[1] + h:
                        self.click.play()
                        running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

            self.screen.fill((255, 255, 255))
            if self.endings.__contains__(141):
                t = "Спасибо за игру"
            else:
                t = "Как играть"
            title_surface = self.font_title.render(t, True, (255, 0, 0))
            title_rect = title_surface.get_rect(center=(size[0] // 2, y_100))
            self.screen.blit(title_surface, title_rect)

            text.read_description(description, (size[0] - 0.8 * x_100, size[1] - 1.9 * y_100), (0.4 * x_100, 1.8 * y_100),
                                  self.screen, self.font_text)

            d1 = x_100 * 1.25; d2 = y_100 * 0.25
            pygame.draw.rect(self.screen, self.blue, (*button_exit_pos, w, h))
            exit_surface = self.font.render("Выход", True, (255, 255, 255))
            exit_rect = exit_surface.get_rect(center=(button_exit_pos[0] + d1, button_exit_pos[1] + d2))
            self.screen.blit(exit_surface, exit_rect)

            pygame.display.flip()
        if self.endings.__contains__(141):
            loop.stop()

    def show_disclaimer(self):
        description = core.res('subs/disclaimer')
        running = True
        while running:
            size = self.screen.get_size()
            x_100 = int(0.06 * size[0])
            y_100 = int(0.097 * size[1])
            for event in pygame.event.get():
                self.general_events(event)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    running = False
                if event.type == pygame.KEYDOWN:
                    running = False

            self.screen.fill((0, 0, 0))
            title_surface = self.font_title.render("Дисклеймер", True, (255, 0, 0))
            title_rect = title_surface.get_rect(center=(size[0] // 2, y_100))
            self.screen.blit(title_surface, title_rect)

            h1 = 1.7*y_100
            text.read_description(description, (size[0]-0.4*x_100, size[1]-h1-y_100), (0.2*x_100, h1), self.screen,
                                  self.font_text, color=(255,255,255))
            pygame.display.flip()

        self.main_menu()

    def play_video(self):
        link = self.frame.link
        video_path = core.res(f'media/media{link}.mp4')
        audio_path = core.res(f'media/media{link}.mp3')
        sub_path = core.res(f'subs/media{link}')
        clip = VideoFileClip(video_path)
        pygame.mixer.music.set_volume(self.volume)
        fps = clip.fps
        pygame.mouse.set_visible(False)
        running = True
        current_time = 0  # Время в секундах
        step = 1 / fps  # Шаг времени между кадрами
        _fps = 0    # Абсолютное число кадров
        time_index = 0
        if self.frame.time is not None:
            t = self.frame.time
            self.time_s = self.time.replace(hours=t.hour, minutes=t.minute, seconds=0)
            self.time = self.time_s.copy()
        else:
            self.time_s = self.time.copy()

        if os.path.exists(sub_path):
            subtitles = text.read_subtitles(sub_path)
            sub_index = 0
            subs_exist = True
            N = len(subtitles) - 1
        else:
            subs_exist = False

        if os.path.exists(audio_path):
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()
        clock = pygame.time.Clock()

        while running:
            for event in pygame.event.get():
                self.general_events(event)
                if event.type == pygame.KEYDOWN:
                    dif = clip.duration - current_time
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        current_time -= 5
                        self.time.subtract(seconds=5)
                        if current_time < 0:
                            current_time = 0
                            time_index = 0
                            self.time = self.time_s
                        elif self.frame.atimes is not None and time_index > 0:
                            _rewind = self.frame.atimes[time_index-1]
                            if current_time < _rewind[0]:
                                sec = _rewind[1].seconds
                                self.time.subtract(seconds=sec)
                                time_index -= 1

                        pygame.mixer.music.set_pos(current_time)
                    elif (event.key == pygame.K_RIGHT or event.key == pygame.K_d) and dif > 5:
                        current_time += 5
                        self.time.add(seconds=5)
                        pygame.mixer.music.set_pos(current_time)
                    elif event.key == pygame.K_ESCAPE:
                        pygame.mixer.music.pause()
                        last_frame = clip.get_frame(current_time)
                        if self.show_settings(last_frame):
                            return
                        pygame.mixer.music.set_volume(self.volume)
                        pygame.mouse.set_visible(False)
                        pygame.mixer.music.unpause()

            # Ограничиваем время в пределах видео
            if current_time >= clip.duration:
                current_time = clip.duration
                running = False
            if _fps >= fps:
                self.time.add(seconds=1)
                _fps = 0
            if self.frame.atimes is not None:
                if time_index < len(self.frame.atimes):
                    _rewind = self.frame.atimes[time_index]
                    if current_time >= _rewind[0]:
                        sec = _rewind[1].seconds
                        self.time.add(seconds=sec)
                        time_index += 1

            # Получаем кадр для текущего времени
            frame = clip.get_frame(current_time)
            frame = np.array(frame, copy=True)
            # Добавляем субтитры
            if self.subtitles and subs_exist:
                cur_str = subtitles[sub_index]
                if cur_str[0] <= current_time < cur_str[1]:
                    pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    draw = ImageDraw.Draw(pil_image)

                    _text = cur_str[2]
                    width, height = pil_image.size
                    text_bbox = draw.textbbox((0, 0), _text, font=self.font_sub)
                    text_width = text_bbox[2] - text_bbox[0]
                    x = (width - text_width) // 2
                    y = height - 50
                    draw.rectangle((x - 5, y - 5, text_bbox[2] + x + 5, text_bbox[3] + y + 5), fill="black")
                    draw.text((x, y), _text, font=self.font_sub, fill=(255, 255, 255))
                    frame = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
                elif current_time >= cur_str[1]:
                    if sub_index < N:
                        sub_index += 1
                elif sub_index > 0:
                    if current_time < cur_str[0] and current_time < subtitles[sub_index-1][1]:
                        sub_index -= 1

            # Преобразуем кадр для Pygame
            frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
            self.screen.blit(pygame.transform.scale(frame_surface, self.screen.get_size()), (0, 0))
            pygame.display.flip()

            # Увеличиваем текущее время
            current_time += step
            _fps += 1
            clock.tick(fps)

        # Останавливаем аудио
        pygame.mixer.music.stop()
        return clip.get_frame(clip.duration)

    def show_choice(self, last_frame):
        choices = self.frame.choices
        frame_surface = pygame.surfarray.make_surface(last_frame.swapaxes(0, 1))
        pygame.mouse.set_visible(True)
        # Определение кнопок
        buttons = core.get_geometry(choices, self.font, self.screen)

        if self.frame.link == 96 or self.frame.link == 100 or 102 <= self.frame.link <= 106:
            pygame.mixer.music.load(core.res('media/searching.mp3'))
            pygame.mixer.music.play(loops=-1)

        while True:
            self.screen.blit(pygame.transform.scale(frame_surface, self.screen.get_size()), (0, 0))
            core.create_buttons(choices, buttons, self.font, self.screen)
            pygame.display.flip()
            new_link = core.add_button_events(self, choices, buttons, last_frame)
            if new_link is not None:
                if new_link == -1:
                    self.wrong.play()
                else:
                    if self.frame.link == 96 or self.frame.link == 100 or 102 <= self.frame.link <= 106:
                        pygame.mixer.music.stop()
                    return new_link

    def show_choice1(self, last_frame, question):
        choices = self.frame.choices
        frame_surface = pygame.surfarray.make_surface(last_frame.swapaxes(0, 1))
        pygame.mouse.set_visible(True)

        # Определение кнопок
        buttons = core.get_geometry(choices, self.font, self.screen)

        while True:
            size = self.screen.get_size()
            self.screen.blit(pygame.transform.scale(frame_surface, size), (0, 0))
            core.create_buttons(choices, buttons, self.font, self.screen)

            description = core.res(f'subs/question{question}')
            s = (size[0] - 100, size[1] // 16)
            pygame.draw.rect(self.screen, (255, 255, 255), (50, 50, *s))
            text.read_description(description, s, (50, 50), self.screen, self.font_text)

            pygame.display.flip()
            new_link = core.add_button_events(self, choices, buttons, last_frame)
            if new_link is not None:
                return new_link

    def show_choice2(self, last_frame):
        choices = self.frame.choices
        frame_surface = pygame.surfarray.make_surface(last_frame.swapaxes(0, 1))
        pygame.mouse.set_visible(True)
        heart_icon = pygame.image.load(core.res('media/heart.png')).convert_alpha()
        clock_icon = pygame.image.load(core.res('media/clock.png')).convert_alpha()
        buttons = core.get_geometry(choices, self.font, self.screen)

        while True:
            size = self.screen.get_size()
            self.screen.blit(pygame.transform.scale(frame_surface, size), (0, 0))
            s = min(*size) // 20
            icon_size = (s, s)
            heart_icon = pygame.transform.scale(heart_icon, icon_size)
            clock_icon = pygame.transform.scale(clock_icon, icon_size)
            spacing = s // 6
            x_50 = int(0.024 * size[0])
            y_30 = int(0.026 * size[1])
            y_50 = int(0.043 * size[1])
            for i in range(self.fighting[0]):
                x = size[0] - (icon_size[0] + spacing) * (i + 1) - x_50
                y = size[1] - icon_size[1] - y_30
                self.screen.blit(heart_icon, (x, y))

            for i in range(self.fighting[1]):
                x = x_50 + (icon_size[0] + spacing) * i
                y = size[1] - icon_size[1] - y_30
                self.screen.blit(heart_icon, (x, y))

            # Отображение оставшегося времени
            t = self.fighting[2]
            x0 = (size[0] - icon_size[0]*t - spacing*(t-1)) // 2
            y = y_50
            for i in range(t):
                x = x0 + (icon_size[0] + spacing) * i
                self.screen.blit(clock_icon, (x, y))

            core.create_buttons(choices, buttons, self.font, self.screen)
            pygame.display.flip()
            new_link = core.add_button_events(self, choices, buttons, last_frame)
            if new_link is not None:
                return new_link

    def pubg(self):
        image = pygame.image.load(core.res('media/pubg.png'))
        pygame.mouse.set_visible(True)
        running = True
        while running:
            size = self.screen.get_size()
            x1 = 0.83 * size[0]
            y1 = 0.915 * size[1]
            x2 = 0.983 * size[0]
            y2 = 0.972 * size[1]
            for event in pygame.event.get():
                self.general_events(event)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if x1 < event.pos[0] < x2 and y1 < event.pos[1] < y2:
                        running = False
                        self.click.play()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        array = pygame.surfarray.array3d(image)
                        array_swapped = np.swapaxes(array, 0, 1)
                        if self.show_settings(array_swapped):
                            return
                        pygame.mixer.music.set_volume(self.volume)

            stretched_image = pygame.transform.scale(image, size)
            self.screen.blit(stretched_image, (0, 0))
            pygame.display.flip()

    def main_menu(self):
        video_path = core.res('media/menu.mp4')
        audio_path = core.res('media/menu.wav')
        clip = VideoFileClip(video_path)
        logo_icon = pygame.image.load(core.res('media/logo.png'))
        clock_icon = pygame.image.load(core.res('media/clock.png'))
        pygame.mixer.music.set_volume(self.volume / 2)
        fps = clip.fps
        pygame.mouse.set_visible(True)
        running = True
        current_time = 0.4
        step = 1 / fps

        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play(loops=-1)
        clock = pygame.time.Clock()

        white = (255, 255, 255)
        black = (0, 0, 0)
        text_ = '--:--'
        time = moment.date(2019, 6, 13)

        while running:
            size = self.screen.get_size()
            x_100 = int(0.06 * size[0])
            y_100 = int(0.097 * size[1])
            s1 = 0.5 * y_100
            x = 2.7 * x_100
            x2 = 8.7 * x_100
            w = 3 * x_100
            w2 = 3.2 * x_100

            for event in pygame.event.get():
                self.general_events(event)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.save()
                        pygame.quit()
                        sys.exit()
                if event.type == pygame.MOUSEMOTION:
                    pos = event.pos
                    if x < pos[0] < x + w and 2.8 * y_100 < pos[1] < 3.3 * y_100:
                        if text_ != '07:00':
                            self.clock.play()
                            text_ = '07:00'
                    elif x < pos[0] < x + w and 3.6 * y_100 < pos[1] < 4.1 * y_100 and self.time_ss is not None:
                        if time != self.time_ss:
                            self.clock.play()
                            time = self.time_ss
                            text_ = self.time_ss.strftime('%H:%M')
                    elif x < pos[0] < x + w and 4.4 * y_100 < pos[1] < 4.9 * y_100 and self.time_s is not None:
                        if time != self.time_s:
                            self.clock.play()
                            time = self.time_s
                            text_ = self.time_s.strftime('%H:%M')
                    else:
                        text_ = '--:--'
                        time = moment.date(2019, 6, 13)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    if x < pos[0] < x + w and 2.8 * y_100 < pos[1] < 3.3 * y_100:
                        self.click.play()
                        self.start(1)
                        return
                    elif x < pos[0] < x + w and 3.6 * y_100 < pos[1] < 4.1 * y_100 and self.frame_s is not None:
                        self.click.play()
                        self.start(self.frame_s.link)
                        return
                    elif x < pos[0] < x + w and 4.4 * y_100 < pos[1] < 4.9 * y_100 and self.frame is not None:
                        self.click.play()
                        self.start(self.frame.link)
                        return
                    elif x2 < pos[0] < x2 + w2 and 2.8 * y_100 < pos[1] < 3.3 * y_100:
                        pygame.mixer.music.pause()
                        self.click.play()
                        self.show_guide()
                        pygame.mixer.music.unpause()
                    elif x2 < pos[0] < x2 + w2 and 3.6 * y_100 < pos[1] < 4.1 * y_100:
                        pygame.mixer.music.pause()
                        self.click.play()
                        i = 0
                        n = len(self.biography)
                        biography = list(self.biography)
                        while 0 <= i < n:
                            if n == 1:
                                k = 3
                            else:
                                if i == 0:
                                    k = 0
                                elif i == n - 1:
                                    k = 2
                                else:
                                    k = 1
                            res = self.show_biography(biography[i], k)
                            if res == 0:
                                break
                            i += res
                        pygame.mixer.music.unpause()
                    elif x2 < pos[0] < x2 + w2 and 4.4 * y_100 < pos[1] < 4.9 * y_100 and self.endings:
                        pygame.mixer.music.pause()
                        self.click.play()
                        i = 0
                        n = len(self.endings)
                        biography = list(self.endings)
                        while 0 <= i < n:
                            if n == 1:
                                k = 3
                            else:
                                if i == 0:
                                    k = 0
                                elif i == n - 1:
                                    k = 2
                                else:
                                    k = 1
                            res = self.show_ending1(biography[i], k)
                            if res == 0:
                                break
                            i += res
                        pygame.mixer.music.unpause()
                    elif x2 < pos[0] < x2 + w2 and 5.2 * y_100 < pos[1] < 5.7 * y_100:
                        self.save()
                        pygame.quit()
                        sys.exit()

            # Ограничиваем время
            if current_time >= clip.duration:
                current_time = 0.4

            # Получаем кадр для текущего времени
            frame = clip.get_frame(current_time)
            frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
            self.screen.blit(pygame.transform.scale(frame_surface, size), (0, 0))
            s = (12 * x_100, 1.75 * y_100)
            x1 = (size[0] - s[0]) // 2
            stretched_image = pygame.transform.scale(logo_icon, s)
            self.screen.blit(stretched_image, (x1, 0))
            k = 1.2 * x_100
            self.screen.blit(pygame.transform.scale(clock_icon, (k, k)), (0.8*x_100, 3.2*y_100))
            self.screen.blit(self.font.render(text_, True, black), (0.9 * x_100, 3.4 * y_100 + k))

            pygame.draw.rect(self.screen, self.blue, (x, 2.8 * y_100, w, s1))
            self.screen.blit(self.font.render("Новая игра", True, white), (3.15 * x_100, 2.85 * y_100))
            if self.frame_s is None:
                surf = pygame.Surface((w, s1))
                surf.fill(self.blue)
                surf.set_alpha(128)
                self.screen.blit(surf, (x, 3.6 * y_100))
            else:
                pygame.draw.rect(self.screen, self.blue, (x, 3.6 * y_100, w, s1))
            self.screen.blit(self.font.render("Загрузиться", True, white), (3.1 * x_100, 3.65 * y_100))
            if self.frame is None:
                surf = pygame.Surface((w, s1))
                surf.fill(self.blue)
                surf.set_alpha(128)
                self.screen.blit(surf, (x, 4.4 * y_100))
            else:
                pygame.draw.rect(self.screen, self.blue, (x, 4.4 * y_100, w, s1))
            self.screen.blit(self.font.render("Продолжить", True, white), (3.1 * x_100, 4.45 * y_100))

            w = w2
            pygame.draw.rect(self.screen, self.blue, (x2, 2.8 * y_100, w, s1))
            if self.endings.__contains__(141):
                t = "Как какать"
            else:
                t = "Как играть"
            self.screen.blit(self.font.render(t, True, white), (9.35 * x_100, 2.85 * y_100))
            pygame.draw.rect(self.screen, self.blue, (x2, 3.6 * y_100, w, s1))
            self.screen.blit(self.font.render(f"Биография ({len(self.biography)}/11)", True, white), (8.85 * x_100, 3.65 * y_100))
            if not self.endings:
                surf = pygame.Surface((w, s1))
                surf.fill(self.blue)
                surf.set_alpha(128)
                self.screen.blit(surf, (x2, 4.4 * y_100))
            else:
                pygame.draw.rect(self.screen, self.blue, (x2, 4.4 * y_100, w, s1))
            self.screen.blit(self.font.render(f"Концовки ({len(self.endings)}/12)", True, white), (8.95 * x_100, 4.45 * y_100))
            pygame.draw.rect(self.screen, self.blue, (x2, 5.2 * y_100, w, s1))
            self.screen.blit(self.font.render("Выход", True, white),(9.6 * x_100, 5.25 * y_100))
            text1, rect1 = self.font_b.render("© Sciensia Ideas 2025 (v2.1)", fgcolor=black, style=pygame.freetype.STYLE_STRONG)
            self.screen.blit(text1, (x_100, size[1] - y_100*0.5))
            pygame.display.flip()

            # Увеличиваем текущее время
            current_time += step
            clock.tick(fps)

            # Останавливаем аудио
        pygame.mixer.music.stop()

    def questioning(self, current_link: int):
        score = self.frame.next_link
        x = current_link - 66
        q = x // 5
        self.score += score
        link = q*5 + 71
        if q == 2:
            if self.score == 3:
                link = 82
            elif self.score == 0:
                link = 80
            else:
                link = 81
        return link

    def fight(self, act: int):
        config = self.fighting[3]
        link = core.fighting(act, config)
        win = config['win_']
        if win is None:
            self.fighting[2] -= 1
        elif win:
            self.fighting[1] -= 1
        else:
            self.fighting[0] -= 1
            self.fighting[2] -= 1

        if self.fighting[0] == 0:
            res = 94
        elif self.fighting[1] == 0:
            res = 93
        elif self.fighting[2] == 0:
            res = 95
        else:
            res = link
        return link, res

    def start(self, current_link):
        frames = self.frames
        endings = self.endings_
        while True:
            if current_link < 141:
                if current_link == 0:
                    self.pubg()
                    current_link = 35
                else:
                    flag = True
                    if current_link == 35:
                        self.endings_[3].next_link = 35
                    elif current_link == 66:
                        self.score = 0
                    elif current_link == 83:
                        config = {'w_change': [], 'l_change': [], 'd_change': [], 'stats': [], 'win': None, 'win_': None}
                        self.fighting = [4, 5, 7, config]
                    elif current_link == 96:
                        text.br_update(frames[96], len(self.endings), self, False)
                        text.br_update(frames[100], len(self.endings), self, True)
                    elif current_link == 100:
                        self.search = 0
                        text.br_update(frames[100], len(self.endings), self, True)
                    elif current_link == 42:
                        c8 = frames[53].choices[0]
                        c8.link = 54
                        frames[56].choices = 57
                    elif current_link == 44:
                        c8 = frames[53].choices[0]
                        c8.link = 55
                        k1 = core.Choice("Она для девушки", True, 58)
                        k2 = core.Choice("Ты знаешь зачем)", True, 59)
                        frames[56].choices = [k1, k2]
                    elif current_link == 61:
                        c1 = frames[65].choices[0]
                        c1.link = 64
                    elif current_link == 62:
                        c1 = frames[65].choices[0]
                        c1.link = 66
                    else:
                        flag = False
                    self.frame = frames[current_link]
                    if flag:
                        self.frame_sb = self.frame
                        self.time_sb = self.time
                    last_frame = self.play_video()
                    # Два раза поиск в конце
                    if 102 <= current_link <= 106:
                        if self.search < 1:
                            fr = frames[100]
                            self.frame.choices = fr.choices.copy()
                            if current_link <= 104:
                                self.frame.choices.pop(0)
                                if current_link == 104 and isinstance(self.frame.choices[1].dialog, core.Prob):
                                    self.frame.choices[1].dialog.high = True
                                    self.frame.choices[1].dialog.update(len(self.endings))
                            elif current_link == 106:
                                self.frame.choices.pop(3)
                            else:
                                self.frame.choices.pop(current_link-104)
                            self.time.add(minutes=20)
                            self.search += 1
                        else:
                            self.frame.choices = None
                    if self.frame.characters is not None:
                        self.biography = self.biography.union(self.frame.characters)
                    if self.frame.choices:
                        # Миниигра вопросы
                        if 66 <= current_link <= 79:
                            q = (current_link - 66) // 5
                            choice = self.show_choice1(last_frame, q+1)
                        # Миниигра драка
                        elif 83 <= current_link <= 92:
                            if current_link == 83:
                                self.fight_s.set_volume(self.volume / 2)
                                self.fight_ss = self.fight_s.play()
                            x = self.show_choice2(last_frame)
                            choice, res = self.fight(x)
                            if choice != res:
                                frames[choice].choices = None
                                frames[choice].next_link = res
                        else:
                            choice = self.show_choice(last_frame)
                        # пропуск
                        if 100 <= current_link <= 107 and choice == 108:
                            k = (2 - self.search) * 45
                            self.time.add(minutes=k)
                        current_link = choice
                    else:
                        # Миниигра вопросы
                        if 66 <= current_link <= 79:
                            current_link = self.questioning(current_link)
                        elif 84 <= current_link <= 92:
                            self.frame.choices = frames[83].choices
                            current_link = self.frame.next_link
                            self.fight_s.stop()
                        else:
                            current_link = self.frame.next_link
            else:
                self.endings.add(current_link)
                frame = endings[current_link]
                self.show_ending(current_link)
                if self.frame.link == 48:
                    current_link = 35
                else:
                    current_link = frame.next_link

    def save(self):
        with open(save_path, 'wb') as f:
            save_dat = {
                'block': self.block,
                'endings': self.endings,
                'biography': self.biography,
                'time': self.time,
                'time_s': self.time_s,
                'time_ss': self.time_ss,
                'frame_s': self.frame_s,
                'frame': self.frame,
                'endings_': self.endings_,
                'frames': self.frames,
                'biography_': self.biography_,
                'volume': self.volume,
                'subtitles': self.subtitles
            }
            pickle.dump(save_dat, f)


if __name__ == "__main__":
    save_path = core.res('saves/main.dat')
    if os.path.exists(save_path):
        game = Main(save_path)
        try:
            game.main_menu()
        except:
            game.save()
    else:
        game = Main()
        try:
            game.show_disclaimer()
        except:
            game.save()
