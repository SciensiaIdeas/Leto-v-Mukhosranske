from core import *
from datetime import time, timedelta


def main():
    frames = [None] * 108
    c1 = Choice("Здарова, я бык, а ты корова", True, 2)
    c2 = Choice("Привет", True, 3)
    frames[0] = Frame(1, [c1, c2], [(50, timedelta(minutes=10)), (86, timedelta(minutes=10)), (106, timedelta(minutes=5)),
                                    (114, timedelta(minutes=3)),(126, timedelta(minutes=3)),(134, timedelta(hours=2, minutes=27))], time(7,0))
    frames[1] = Frame(2, 4)
    frames[2] = Frame(3, 4)
    c1 = Choice("Нормальные бодибилдеры стероиды не принимают", True, 5)
    c2 = Choice("Меня мама Стероидом назвала. Зачем мне стероиды?", True, 8)
    c3 = Choice("А ты вообще качаться не умеешь!", True, 11)
    frames[3] = Frame(4, [c1, c2, c3], [(10, timedelta(minutes=10))], time(10, 5))
    c1 = Choice("А тебе вообще надо похудеть, говна мешок!", True, 6)
    c2 = Choice("Давай без оскорблений, ты вообще-то не лучше!", True, 7)
    frames[4] = Frame(5, [c1, c2])
    frames[5] = Frame(6, 142)
    frames[6] = Frame(7, 12)
    c1 = Choice("Показать своё могущество", False, 9)
    c2 = Choice("Ой, это ты зря сказал", True, 10)
    frames[7] = Frame(8, [c1, c2])
    frames[8] = Frame(9, 12)
    frames[9] = Frame(10, 143)
    frames[10] = Frame(11, 12)
    c1 = Choice("Я пешком", True, 13)
    c2 = Choice("Я на лифте", True, 14)
    c3 = Choice("Поедем вдвоём на лифте", True, 15)
    frames[11] = Frame(12, [c1, c2, c3], None, time(10, 25))
    frames[12] = Frame(13, 16)
    frames[13] = Frame(14, 16, [(18, timedelta(seconds=10)), (30, timedelta(minutes=5))])
    frames[14] = Frame(15, 16)
    frames[14].characters = {2}
    c1 = Choice("Выбежать из его дома", False, 17)
    c2 = Choice("Посмотреть на него как на дебила", False, 18)
    c3 = Choice("У тебя друзей мало!", True, 19)
    frames[15] = Frame(16, [c1, c2, c3], [(7, timedelta(minutes=3)),(199, timedelta(hours=1, minutes=38))])
    frames[16] = Frame(17, 21, [(7, timedelta(minutes=2))])
    frames[17] = Frame(18, 20)
    frames[18] = Frame(19, 20)
    frames[19] = Frame(20, 21, None, time(12, 20))
    c1 = Choice("Ты ещё с негром Виталей того", True, 22)
    c2 = Choice("Ты дрочишь на Рикардо Милоса?", True, 23)
    c3 = Choice("Видимо тебе не нравится её жопа", True, 24)
    frames[20] = Frame(21, [c1, c2, c3], None, time(13, 0))
    frames[21] = Frame(22, 25)
    frames[22] = Frame(23, 25)
    frames[23] = Frame(24, 25)
    c1 = Choice("Го в PUBG", True, 26)
    c2 = Choice("Го в Майнкрафт", True, 32)
    frames[24] = Frame(25, [c1, c2], None, time(13, 25))
    c1 = Choice("Сковородочный режим", False, 27)
    c2 = Choice("А почему он лучше? Ты в него не играл", True, 28)
    c3 = Choice("На... тебя твой батя сажает", True, 29)
    frames[25] = Frame(26, [c1, c2, c3])
    frames[26] = Frame(27, 0)
    frames[27] = Frame(28, 35, [(34, timedelta(minutes=10))])
    frames[27].characters = {4}
    c1 = Choice("Сражаться до последнего", False, 30)
    c2 = Choice("Съе...ться", False, 31)
    frames[28] = Frame(29, [c1, c2])
    frames[29] = Frame(30, 25)
    frames[30] = Frame(31, 144)
    c1 = Choice("Мне тебя по горло хватило", True, 33)
    c2 = Choice("Сосни моего очка", True, 34)
    frames[31] = Frame(32, [c1, c2])
    frames[32] = Frame(33, 145)
    frames[33] = Frame(34, 146)
    c1 = Choice("Фу, глиномесы!", True, 36)
    c2 = Choice("Извините, а что вы делаете?", True, 37)
    frames[34] = Frame(35, [c1, c2], None, time(14,30))
    frames[35] = Frame(36, 44)
    c1 = Choice("Чё мы будем слушать этих геев", True, 38)
    c2 = Choice("Окей, рассказывайте", True, 39)
    frames[36] = Frame(37, [c1, c2])
    frames[36].characters = {5, 6}
    frames[37] = Frame(38, 44)
    c1 = Choice("Воспользоваться \"волшебной палочкой\"", False, 40)
    c2 = Choice("Мне действительно жаль", True, 41)
    frames[38] = Frame(39, [c1, c2])
    frames[39] = Frame(40, 147)
    frames[40] = Frame(41, 42)
    # Ветвление 1-13
    c1 = Choice("Воспользоваться шаурмой", False, 43)
    c2 = Choice("Ты на что намекаешь? У меня нет еды", True, 49)
    c3 = Choice("Ты чё тут делаешь?", True, 53)
    c4 = Choice("Нападение", False, 51)
    c5 = Choice("Съе...ться", False, 52)
    c6 = Choice("Ты чё орёшь?", True, 47)
    c7 = Choice("Съе...ться", False, 48)
    c8 = Choice("Предложить шаурму", False)
    c9 = Choice("Предложить \"волшебную палочку\"", False, 56)
    frames[41] = Frame(42, [c1, c2], [(0, timedelta(minutes=2))])
    frames[42] = Frame(43, 46, [(56, timedelta(minutes=5)), (79, timedelta(minutes=3))])
    c1 = Choice("Воспользоваться шаурмой", False, 45)
    c2 = Choice("Ты на что намекаешь? У меня нет еды", True, 50)
    frames[43] = Frame(44, [c1, c2], [(0, timedelta(minutes=2))])
    frames[44] = Frame(45, 46, [(11, timedelta(minutes=5)), (17, timedelta(minutes=4))])
    frames[45] = Frame(46, [c6, c7], [(0, timedelta(minutes=5)), (25, timedelta(minutes=1))])
    frames[46] = Frame(47, 35, [(11, timedelta(hours=1))])
    frames[47] = Frame(48, 144)
    frames[48] = Frame(49, [c3, c4, c5], [(11, timedelta(minutes=5)), (34, timedelta(minutes=3)), (75, timedelta(minutes=5))])
    frames[49] = Frame(50, [c3, c4, c5],[(10, timedelta(minutes=5)), (23, timedelta(minutes=3)), (29, timedelta(minutes=5))])
    frames[50] = Frame(51, 35, [(20, timedelta(minutes=45))])
    frames[51] = Frame(52, 35, [(6, timedelta(minutes=35))])
    frames[52] = Frame(53, [c8, c9])
    frames[53] = Frame(54, 60)
    frames[54] = Frame(55, 60)
    frames[55] = Frame(56, 57)
    frames[55].characters = {7}
    frames[56] = Frame(57, 60)
    frames[57] = Frame(58, 60)
    frames[58] = Frame(59, 148)
    c1 = Choice("Давай поиграем в ассоциации", True, 62)
    c2 = Choice("Можешь ЕГЭ по физике порешать", True, 61)
    frames[59] = Frame(60, [c1, c2], [(15, timedelta(minutes=30))], time(15, 30))
    # Ветвление 1-21
    frames[60] = Frame(61, 63)
    frames[61] = Frame(62, 63)
    c1 = Choice("Буду благодарен", True, 66)
    c2 = Choice("Я вашу мамашу вокруг оси Y вертел", True, 83)
    c3 = Choice("Съе...ться", False, 65)
    c4 = Choice("Буду благодарен", True, 66)
    frames[62] = Frame(63, [c1, c2, c3], None, time(16, 15))
    frames[63] = Frame(64, 150)
    frames[64] = Frame(65, [c4, c2])
    frames[64].characters = {8, 9}
    c1 = Choice("A=F*s*cosA", True, 67)
    c2 = Choice("A=N/t", True, 68)
    c3 = Choice("A=mg/v", True, 69)
    c4 = Choice("A=F*s", True, 70)
    frames[65] = Frame(66, [c1, c2, c3, c4])
    frames[66] = Frame(67, 1)
    frames[67] = Frame(68, 0)
    frames[68] = Frame(69, 0)
    frames[69] = Frame(70, 0)
    c1 = Choice("4 сек", True, 72)
    c2 = Choice("5 сек", True, 73)
    c3 = Choice("6 сек", True, 74)
    c4 = Choice("8 сек", True, 75)
    frames[70] = Frame(71, [c1, c2, c3, c4])
    frames[71] = Frame(72, 0)
    frames[72] = Frame(73, 1)
    frames[73] = Frame(74, 0)
    frames[74] = Frame(75, 0)
    c1 = Choice("0,24 Н", True, 77)
    c2 = Choice("1,5 Н", True, 78)
    c3 = Choice("0 Н", True, 79)
    frames[75] = Frame(76, [c1, c2, c3])
    frames[76] = Frame(77, 0)
    frames[77] = Frame(78, 0)
    frames[78] = Frame(79, 1)
    frames[79] = Frame(80, 149)
    frames[80] = Frame(81, 96)
    frames[81] = Frame(82, 150)
    c1 = Choice("Нападение", False, 0)
    c2 = Choice("Защита", False, 1)
    c3 = Choice("Толкнуть", False, 2)
    A = [c1, c2, c3]
    for i in range(4, 14):
        frames[78 + i] = Frame(79 + i, A)
    frames[92] = Frame(93, 151)
    frames[93] = Frame(94, 149)
    frames[94] = Frame(95, 149)
    c1 = Choice("Поискать на гаражах", Prob(), 97)
    c2 = Choice("Осмотреть место встречи", Prob(), 98)
    c3 = Choice("Позвонить в домофон", Prob(), 99)
    c4 = Choice("Пропустить ход", False, 100)
    frames[95] = Frame(96, [c1, c2, c3, c4], None, time(17, 30))
    for ch in frames[95].choices[:-1]:
        ch.dialog.high = True
    frames[96] = Frame(97, 100)
    frames[97] = Frame(98, 100)
    frames[98] = Frame(99, 100)
    c1 = Choice("Поискать на деревьях", Prob(), 101)
    c2 = Choice("Спросить учителя физики", Prob(), 105)
    c3 = Choice("Поискать на крыше", Prob(), 107)
    c5 = Choice("Проверить штаб на холме", Prob(), 106)
    c4 = Choice("Пропустить ход", False, 108)
    frames[99] = Frame(100, [c1, c2, c3, c5, c4], None, time(18, 15))
    d1 = Choice("Собачье говно есть на земле!", True, 102)
    d2 = Choice("Может ты не будешь выеб…ся и скажешь где Сардель", True, 103)
    d3 = Choice("Принести ему земли", False, 104)
    frames[100] = Frame(101, [d1, d2, d3], [(0, timedelta(minutes=20)),(29, timedelta(minutes=10))])
    frames[101] = Frame(102, 108)
    frames[102] = Frame(103, 108)
    frames[103] = Frame(104, 108, [(28, timedelta(minutes=1))])
    frames[103].characters = {10}
    frames[104] = Frame(105, 108,[(0, timedelta(minutes=15)),(34, timedelta(minutes=3))])
    frames[104].characters = {3}
    frames[105] = Frame(106, 108, [(0, timedelta(minutes=30)),(23, timedelta(minutes=3)),(47, timedelta(minutes=4)),
                                   (64, timedelta(minutes=1)),(104, timedelta(minutes=1))])
    frames[106] = Frame(107, 141, [(0, timedelta(minutes=9)),(37, timedelta(minutes=1)),(79, timedelta(minutes=1)),
                                   (105, timedelta(minutes=3)),(118, timedelta(minutes=1))])
    frames[106].characters = {11}
    frames[107] = Frame(108, 152, [(0, timedelta(minutes=10))])
    frames[107].characters = {3}
    return FrameArray(frames)


def main1():
    endings = [None] * 12
    endings[0] = Ending(141, 'Каноническая концовка', 96)
    endings[1] = Ending(142, 'Одинокая концовка', 4)
    endings[2] = Ending(143, 'Мамкина-помощь концовка', 4)
    endings[3] = Ending(144, 'Предательская концовка', 25)
    endings[4] = Ending(145, 'Концовка дотера', 25)
    endings[5] = Ending(146, 'Майнкрафт концовка', 25)
    endings[6] = Ending(147, 'Концовка иноагента', 35)
    endings[7] = Ending(148, 'Счастливая концовка', 35)
    endings[8] = Ending(149, 'Плохая концовка', 63)
    endings[9] = Ending(150, 'Концовка ботана', 60)
    endings[10] = Ending(151, 'Успешная концовка', 63)
    endings[11] = Ending(152, 'Концовка шИзЫы', 96)
    return FrameArray(endings)


def main2():
    chr = [None] * 11
    chr[0] = Character(1,"Стероид Протеинов", "главный герой", 16)
    chr[1] = Character(2,"Сардель Толстой", "одноклассник и лучший друг Стероида", 16)
    chr[2] = Character(3,"Роза Протеинова", "мама Стероида", 40)
    chr[3] = Character(4,"Крипер228", "майнкрафт-школьник", 12)
    chr[4] = Character(5,"Хуис Нони", "транссексуал из Америки", 17)
    chr[5] = Character(6,"Алекс Браун", "парень Хуис", 16)
    chr[6] = Character(7,"Бомжой", "пространственно-временной бомж", 69)
    chr[7] = Character(8,"Потенциал Высоцкий", "клон Хуиса из параллельной вселенной, гопник-физик", 17)
    chr[8] = Character(9,"Заряд Магнитов", "друг Потенциала, гопник-физик", 17)
    chr[9] = Character(10,"Коряг Бревно", "клон Алекса из параллельной вселенной, древесный житель", 16)
    chr[10] = Character(11,"Мухосранск", "город, в котором происходят события игры", 150)
    return chr


def br_update(frame, n: int, cls, flag: bool):
    if n == cls.block:
        for ch in frame.choices:
            if isinstance(ch.dialog, Prob):
                ch.dialog.update(n)
    else:
        for ch in frame.choices:
            if isinstance(ch.dialog, Prob):
                ch.dialog.update(n)
                ch.dialog.open = True
        if flag:
            cls.block = n


def read_subtitles(file_path):
    subtitles = []
    with open(file_path, 'r', encoding='utf-8') as file:
        rows = file.read().splitlines()
        n = len(rows)
        for i in range(0, n, 2):
            if i + 1 < n:
                time_range = rows[i].split(",")
                start_time = float(time_range[0])
                end_time = float(time_range[1])
                subtitle_text = rows[i + 1]
                subtitles.append((start_time, end_time, subtitle_text))
    return subtitles


def read_description(file_path, size, cord, surface, font, color=(0,0,0)):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()  # Читаем весь текст
        paragraphs = text.split('\n')  # Разбиваем на абзацы

    y = cord[1]

    for paragraph in paragraphs:
        words = paragraph.split(' ')
        i = 0
        n = len(words)

        while i < n:
            string = []
            while font.size(' '.join(string))[0] <= size[0]:
                string.append(words[i])
                i += 1
                if i >= n:
                    break
            else:
                i -= 1
                string.pop()

            s = ' '.join(string)
            line_surface = font.render(s, True, color)
            surface.blit(line_surface, (cord[0], y))
            y += font.size(s)[1]  # Переход на новую строку

        y += font.size(' ')[1]  # Добавляем промежуток между абзацами



