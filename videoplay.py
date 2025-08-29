import pygame
from moviepy import VideoFileClip
import core
import os
import text
import numpy as np
import cv2
from PIL import Image, ImageDraw
from screen import SettingsScreen
from menu import ChooseAbility


def play_video(game):
    """
    Синхронный проигрыватель:
      - Время берём от аудио (pygame.mixer.music) → видео-кадр по current_time
      - Перемотка: сначала двигаем аудио (set_pos), затем current_time = pos
      - Пауза/возврат: восстанавливаем опорные часы без дрейфа
    """
    constants = core.constants
    link = game.frame.link
    video_path = core.res(f"media/media{link}.mp4")
    audio_path = core.res(f"media/media{link}.mp3")
    sub_path   = core.res(f"subs/{game.settings['lang']}/media{link}")

    # --- загрузка видео ---
    clip = VideoFileClip(video_path)  # MoviePy 2.x
    fps = max(1, int(round(clip.fps or 24)))
    size_screen = game.screen.get_size()
    pygame.mouse.set_visible(False)

    # --- инициал аудио ---
    if os.path.exists(audio_path):
        pygame.mixer.music.load(audio_path)
    pygame.mixer.music.set_volume(game.settings['volume'])

    # --- игровое время кадра ---
    if game.frame.time is not None:
        t = game.frame.time
        game.time_s = game.time.replace(hours=t.hour, minutes=t.minute, seconds=0)
        game.time = game.time_s.copy()
    else:
        game.time_s = game.time.copy()

    # чекпоинт/автосейв — как у вас
    if link not in constants.saves_range:
        if game.saves['continue'] and game.saves['load']:
            if link != game.saves['load'].link:
                game.frame.time_s = game.time_s
                game.frame.temp_s = game.temp
                game.saves['continue'] = game.frame
        else:
            game.frame.time_s = game.time_s
            game.frame.temp_s = game.temp
            game.saves['continue'] = game.frame
    if link in constants.checkpoints:
        game.save()

    # Выбор способности (как у вас)
    if link == 1 and not game.block[0]:
        last_frame = clip.get_frame(0.0)
        sc = ChooseAbility(game, last_frame)
        sc.loop()
        game.block[0] = True

    # --- субтитры ---
    subs_exist = os.path.exists(sub_path)
    subs = text.read_subtitles(sub_path) if subs_exist else []
    sub_index = 0
    Nsub = (len(subs) - 1) if subs_exist else -1

    # --- “часы аудио”: позиция = audio_base + (ticks_now - t0)/1000 ---
    # старт
    pygame.mixer.music.play()
    audio_base_sec = 0.0               # где начинается аудио в секундах
    audio_sec_toadd = 0
    t0_ms = pygame.time.get_ticks()    # тик, когда мы стартовали/смещали audio_base_sec

    def audio_now() -> float:
        # На некоторых платформах get_pos() даёт -1; наша опора — (ticks - t0) + base
        # но если get_pos корректен, можно использовать его для доп.проверки
        dt = (pygame.time.get_ticks() - t0_ms) / 1000.0
        return max(0.0, min(audio_base_sec + dt, clip.duration))

    def seek_audio(to_sec: float):
        nonlocal audio_base_sec, t0_ms
        to_sec = max(0.0, min(to_sec, clip.duration))
        try:
            pygame.mixer.music.set_pos(to_sec)
        except Exception:
            # set_pos может не поддерживать mp3 на некоторых платформах;
            # fallback: остановить/запустить и «симулировать» позицию (будет неидеально)
            pygame.mixer.music.stop()
            pygame.mixer.music.play()
        audio_base_sec = to_sec
        t0_ms = pygame.time.get_ticks()

    # индексация “нестандартных прибавок” к времени (как в вашем коде)
    time_index = 0

    clock = pygame.time.Clock()
    running = True
    temp_exit_to_menu = False

    while running:
        open_setting = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.exit_game()
                running = False

            elif event.type == pygame.VIDEORESIZE:
                game.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                game.init_font(event.w)

            elif event.type == pygame.WINDOWMINIMIZED:
                open_setting = 1

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    if not game.fullscreen:
                        game.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                        game.fullscreen = True
                    else:
                        game.screen = pygame.display.set_mode(game.screen.get_size(), pygame.RESIZABLE)
                        game.fullscreen = False

                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    # -5 секунд
                    new_t = audio_now() - 5.0
                    seek_audio(new_t)
                    # коррекция игрового времени
                    game.time.subtract(seconds=5)
                    if new_t <= 0:
                        time_index = 0
                        game.time = game.time_s.copy()
                    if game.frame.atimes and time_index > 0:
                        prev = game.frame.atimes[time_index - 1]
                        if new_t < prev[0]:
                            game.time.subtract(seconds=prev[1].seconds)
                            time_index -= 1

                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    # +5 секунд (не заходим за хвост)
                    cur = audio_now()
                    dif = clip.duration - cur
                    if dif > 5:
                        seek_audio(cur + 5.0)
                        game.time.add(seconds=5)
                    elif dif > 1:
                        seek_audio(cur + (dif - 1))
                        game.time.add(seconds=(dif - 1))

                elif event.key == pygame.K_ESCAPE:
                    open_setting = 2

        if open_setting:
            # пауза
            pygame.mixer.music.pause()
            paused_minimized = (open_setting == 1)
            cur_time = audio_now()
            last_frame = clip.get_frame(cur_time)
            # обновим время
            secs = int(cur_time) - audio_sec_toadd
            game.time.add(seconds=secs)
            audio_sec_toadd += secs
            sc = SettingsScreen(game, last_frame, 1)
            if paused_minimized:
                sc.paused = True
            sc.loop()
            if sc.temp:
                running = False
                temp_exit_to_menu = True
            pygame.mouse.set_visible(False)
            # возвращаемся — продолжаем c текущей позиции
            pygame.mixer.music.unpause()
            # переустановим базу, чтобы не было скачка
            audio_base_sec = cur_time
            t0_ms = pygame.time.get_ticks()

        # текущее время по аудио
        t = audio_now()

        # конец видео
        if t >= clip.duration:
            # обновим время
            cur_time = audio_now()
            secs = int(cur_time) - audio_sec_toadd
            game.time.add(seconds=secs)
            break

        # ваш “добавочный” счётчик по atimes
        if game.frame.atimes and time_index < len(game.frame.atimes):
            rw = game.frame.atimes[_clamp(time_index, 0, len(game.frame.atimes)-1)]
            if t >= rw[0]:
                game.time.add(seconds=rw[1].seconds)
                time_index += 1

        # получаем кадр ровно на текущем t (синхронно с аудио)
        frame = clip.get_frame(t)

        # (по умолчанию) субтитры через PIL/pygame — быстрее
        if game.settings['subtitles'] and subs_exist:
            if sub_index <= Nsub:
                cur_str = subs[sub_index]
                st, en, txt = cur_str
                if st <= t < en:
                    pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    draw = ImageDraw.Draw(pil)
                    w, h = pil.size
                    bbox = draw.textbbox((0, 0), txt, font=game.font_sub)
                    tw = bbox[2] - bbox[0]
                    x = (w - tw) // 2
                    y = h - 50
                    draw.rectangle((x - 5, y - 5, x + (bbox[2]-bbox[0]) + 5, y + (bbox[3]-bbox[1]) + 5), fill=constants.color_front)
                    draw.text((x, y), txt, font=game.font_sub, fill=constants.color_back)
                    frame = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)
                elif t >= en and sub_index < Nsub:
                    sub_index += 1
                elif sub_index > 0 and t < st and t < subs[sub_index - 1][1]:
                    sub_index -= 1

        # blit
        surf = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        game.screen.blit(pygame.transform.scale(surf, size_screen), (0, 0))
        pygame.display.flip()
        # визуальная частота = fps видео
        clock.tick(fps)

    pygame.mixer.music.stop()
    if temp_exit_to_menu:
        return None
    return clip.get_frame(clip.duration)


# маленький helper, если нужен безопасный индекс
def _clamp(i, lo, hi):
    return lo if i < lo else (hi if i > hi else i)