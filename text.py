import core
from datetime import time, timedelta


def main():
    frames = [None] * 118
    c1 = core.Choice(0, 2)
    c2 = core.Choice(1, 3, -1)
    frames[0] = core.Frame(1, [c1, c2], [(50, timedelta(minutes=10)), (86, timedelta(minutes=10)), (106, timedelta(minutes=5)),
                                    (114, timedelta(minutes=3)),(126, timedelta(minutes=3)),(134, timedelta(hours=2, minutes=27))], time(7,0))
    frames[1] = core.Frame(2, 4)
    frames[2] = core.Frame(3, 4)
    c1 = core.Choice(2, 5)
    c2 = core.Choice(3, 8)
    c3 = core.Choice(4, 11)
    frames[3] = core.Frame(4, [c1, c2, c3], [(10, timedelta(minutes=10))], time(10, 5))
    c1 = core.Choice(5, 6, -2)
    c2 = core.Choice(6, 7, -1)
    frames[4] = core.Frame(5, [c1, c2])
    frames[5] = core.Frame(6, 142)
    frames[6] = core.Frame(7, 12)
    c1 = core.Choice(7, 9)
    c2 = core.Choice(8, 10, -2)
    frames[7] = core.Frame(8, [c1, c2])
    frames[8] = core.Frame(9, 12)
    frames[9] = core.Frame(10, 143)
    frames[10] = core.Frame(11, 12)
    c1 = core.Choice(9, 13)
    c2 = core.Choice(10, 14, 2)
    c3 = core.Choice(11, 15, -1)
    frames[11] = core.Frame(12, [c1, c2, c3], None, time(10, 25))
    frames[12] = core.Frame(13, 16)
    frames[13] = core.Frame(14, 16, [(18, timedelta(seconds=10)), (30, timedelta(minutes=5))])
    frames[14] = core.Frame(15, 16)
    c1 = core.Choice(12, 17)
    c2 = core.Choice(13, 18)
    c3 = core.Choice(14, 19, -1)
    frames[15] = core.Frame(16, [c1, c2, c3], [(7, timedelta(minutes=3)),(199, timedelta(hours=1, minutes=38))])
    frames[16] = core.Frame(17, 21, [(7, timedelta(minutes=2))])
    frames[17] = core.Frame(18, 20)
    frames[18] = core.Frame(19, 20)
    frames[19] = core.Frame(20, 21, None, time(12, 20))
    c1 = core.Choice(15, 22, -1)
    c2 = core.Choice(16, 23)
    c3 = core.Choice(17, 24)
    frames[20] = core.Frame(21, [c1, c2, c3], None, time(13, 0))
    frames[21] = core.Frame(22, 25)
    frames[22] = core.Frame(23, 25)
    frames[23] = core.Frame(24, 25)
    c1 = core.Choice(18, 26)
    c2 = core.Choice(19, 32)
    frames[24] = core.Frame(25, [c1, c2], None, time(13, 25))
    c1 = core.Choice(20, 27, -1)
    c2 = core.Choice(21, 28, 4)
    c3 = core.Choice(22, 29)
    frames[25] = core.Frame(26, [c1, c2, c3])
    frames[26] = core.Frame(27, 0)
    frames[27] = core.Frame(28, 35, [(34, timedelta(minutes=10))])
    c1 = core.Choice(23, 30, -3)
    c2 = core.Choice(24, 31, -2) # Сье...ться
    frames[28] = core.Frame(29, [c1, c2])
    frames[29] = core.Frame(30, 25)
    frames[30] = core.Frame(31, 144)
    c1 = core.Choice(25, 33, -2)
    c2 = core.Choice(26, 34, -2)
    frames[31] = core.Frame(32, [c1, c2])
    frames[32] = core.Frame(33, 145)
    frames[33] = core.Frame(34, 146)
    c1 = core.Choice(27, 36, -1)
    c2 = core.Choice(28, 37)
    frames[34] = core.Frame(35, [c1, c2], None, time(14,30))
    frames[35] = core.Frame(36, 46)
    c1 = core.Choice(29, 38)
    c2 = core.Choice(30, 39, 6)
    frames[36] = core.Frame(37, [c1, c2])
    frames[37] = core.Frame(38, 46)
    c1 = core.Choice(31, 40, -2)
    c2 = core.Choice(32, 41)
    frames[38] = core.Frame(39, [c1, c2])
    frames[39] = core.Frame(40, 147)
    frames[40] = core.Frame(41, 42)
    # Ветвление 1-13
    c1 = core.Choice(33)
    c2 = core.Choice(34)
    c3 = core.Choice(35,56)
    c4 = core.Choice(36,54, -3)     # Нападение
    c5 = core.Choice(24,55, -3)
    c6 = core.Choice(37,50, -3)
    c7 = core.Choice(24,51, -2)
    c8 = core.Choice(38)
    c9 = core.Choice(39,59, 5)
    frames[41] = core.Frame(42, [c1, c2], [(0, timedelta(minutes=2, seconds=44))])   #43 | 521
    frames[42] = core.Frame(43, 44, [(49, timedelta(minutes=5))])
    # after 44 (45 or 523)
    frames[43] = core.Frame(44, None, [(0, timedelta(minutes=2))])
    frames[44] = core.Frame(45, 49)
    frames[45] = core.Frame(46, [c1, c2], [(0, timedelta(minutes=2, seconds=44))])   #47 | 522
    frames[46] = core.Frame(47, 48, [(11, timedelta(minutes=5))])
    # after 48 (49 or 524)
    frames[47] = core.Frame(48, None)
    frames[48] = core.Frame(49, [c6, c7])
    frames[49] = core.Frame(50, 35)
    frames[50] = core.Frame(51, 144)
    frames[51] = core.Frame(521, 44)
    frames[52] = core.Frame(522, 48)
    frames[53] = core.Frame(523, 53)
    frames[54] = core.Frame(524, 53)

    frames[55] = core.Frame(53, [c3, c4, c5], [(0, timedelta(minutes=5))])
    frames[56] = core.Frame(54, 35)
    frames[57] = core.Frame(55, 35)
    frames[58] = core.Frame(56, [c8, c9])
    frames[59] = core.Frame(57, 63)
    frames[60] = core.Frame(58, 63)
    frames[61] = core.Frame(59, 60)
    frames[62] = core.Frame(60, 63)
    frames[63] = core.Frame(61, 63)
    frames[64] = core.Frame(62, 148)
    c1 = core.Choice(40, 65, -1)
    c2 = core.Choice(41, 64)
    frames[65] = core.Frame(63, [c1, c2], [(15, timedelta(minutes=30))], time(15, 30))
    # Ветвление 1-21
    frames[66] = core.Frame(64, 66)
    frames[67] = core.Frame(65, 66)
    c1 = core.Choice(42,71)
    c2 = core.Choice(43,88)
    c3 = core.Choice(24,67, 8)
    frames[68] = core.Frame(66, [c1, c2, c3], None, time(16, 15))
    frames[69] = core.Frame(67, [c1, c2])
    # Friend answers the questions
    frames[70] = core.Frame(68, 76)
    frames[71] = core.Frame(69, 81)
    frames[72] = core.Frame(70, 150)
    c1 = core.Choice("A=F*s*cosA", 72)
    c2 = core.Choice("A=N/t", 73)
    c3 = core.Choice("A=mg/v", 74)
    c4 = core.Choice("A=F*s", 75)
    frames[73] = core.Frame(71, [c1, c2, c3, c4])
    frames[74] = core.Frame(72, 1)
    frames[75] = core.Frame(73, 0)
    frames[76] = core.Frame(74, 0)
    frames[77] = core.Frame(75, 0)
    c1 = core.Choice(44, 77)
    c2 = core.Choice(45, 78)
    c3 = core.Choice(46, 79)
    c4 = core.Choice(47, 80)
    frames[78] = core.Frame(76, [c1, c2, c3, c4])
    frames[79] = core.Frame(77, 0)
    frames[80] = core.Frame(78, 1)
    frames[81] = core.Frame(79, 0)
    frames[82] = core.Frame(80, 0)
    c1 = core.Choice(48, 82)
    c2 = core.Choice(49, 83)
    c3 = core.Choice(50, 84)
    frames[83] = core.Frame(81, [c1, c2, c3])
    frames[84] = core.Frame(82, 0)
    frames[85] = core.Frame(83, 0)
    frames[86] = core.Frame(84, 1)
    frames[87] = core.Frame(85, 149)
    frames[88] = core.Frame(86, 101)
    frames[89] = core.Frame(87, 150)
    c1 = core.Choice(36,0)
    c2 = core.Choice(51, 1)
    c3 = core.Choice(52, 2)
    A = [c1, c2, c3]
    for i in range(10):
        frames[90+i] = core.Frame(88 + i, A)
    frames[100] = core.Frame(98, 151)
    frames[101] = core.Frame(99, 66)
    frames[102] = core.Frame(100, 66)
    c1 = core.Choice(53,102, 11, core.Prob())
    c2 = core.Choice(54,103, -1, core.Prob())
    c3 = core.Choice(55,104, 0, core.Prob())
    frames[103] = core.Frame(101, [c1, c2, c3], None, time(17, 30))
    frames[104] = core.Frame(102, 105)
    frames[105] = core.Frame(103, 105)
    frames[106] = core.Frame(104, 105)
    c1 = core.Choice(56,106, 0, core.Prob())
    c2 = core.Choice(57,110, 3, core.Prob())
    c3 = core.Choice(58,112, -2, core.Prob())
    c4 = core.Choice(59,111, 7, core.Prob())
    frames[107] = core.Frame(105, [c1, c2, c3, c4], None, time(18, 15))
    d1 = core.Choice(60, 107)
    d2 = core.Choice(61, 108)
    d3 = core.Choice(62, 109, 10)
    frames[108] = core.Frame(106, [d1, d2, d3], [(0, timedelta(minutes=20)),(29, timedelta(minutes=10))])
    c = [c2, c3, c4]
    frames[109] = core.Frame(107, c)
    frames[110] = core.Frame(108, c)
    frames[111] = core.Frame(109, c, [(28, timedelta(minutes=1))])
    frames[112] = core.Frame(110, [c1, c3, c4],[(0, timedelta(minutes=15)),(34, timedelta(minutes=3))])
    frames[113] = core.Frame(111, [c1, c2, c3], [(0, timedelta(minutes=30)),(23, timedelta(minutes=3)),(47, timedelta(minutes=4)),
                                   (64, timedelta(minutes=1)),(104, timedelta(minutes=1))])
    frames[114] = core.Frame(112, 141, [(0, timedelta(minutes=9)),(37, timedelta(minutes=1)),(79, timedelta(minutes=1)),
                                   (105, timedelta(minutes=3)),(118, timedelta(minutes=1))])
    frames[115] = core.Frame(113, 152, [(0, timedelta(minutes=10))])

    # Special frames for frame branch
    c1 = core.Choice(100, 85, -2)
    c2 = core.Choice(101, 86)
    c3 = core.Choice(102, 87, -2)
    c4 = core.Choice(103, 70, 9)
    frames[116] = core.Frame(114, [c1, c2, c3, c4])

    c1 = core.Choice(104, 98, -2)
    c2 = core.Choice(105, 99, -3)
    c3 = core.Choice(106, 100, -3)
    frames[117] = core.Frame(115, [c1, c2, c3])
    return core.FrameArray(frames)


def main1():
    endings = [None] * 12
    A = core.constants.checkpoints
    endings[0] = core.Ending(141, 63, A[4])
    endings[1] = core.Ending(142, 64, A[0])
    endings[2] = core.Ending(143, 65, A[0])
    endings[3] = core.Ending(144, 66, A[1])
    endings[4] = core.Ending(145, 67, A[1])
    endings[5] = core.Ending(146, 68, A[1])
    endings[6] = core.Ending(147, 69, A[2])
    endings[7] = core.Ending(148, 70, A[2])
    endings[8] = core.Ending(149, 71, A[3])
    endings[9] = core.Ending(150, 72, A[3])
    endings[10] = core.Ending(151, 73, A[3])
    endings[11] = core.Ending(152, 74, A[5])
    return core.FrameArray(endings)


def main2():
    chr = [None] * 11
    chr[0] = core.Character(1, 75, 16)
    chr[1] = core.Character(2, 77, 16)
    chr[2] = core.Character(3, 79, 40)
    chr[3] = core.Character(4, 81, 12)
    chr[4] = core.Character(5, 83, 17)
    chr[5] = core.Character(6, 85, 16)
    chr[6] = core.Character(7, 87, 69)
    chr[7] = core.Character(8, 89, 17)
    chr[8] = core.Character(9, 91, 17)
    chr[9] = core.Character(10, 93, 16)
    chr[10] = core.Character(11, 95, 150)
    return core.FrameArray(chr)


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


def read_description(file_path, size, cord, surface, font, color=None, para_gap=0.8):
    """
    size = (max_width, max_height) — используем только ширину, но можно расширить под высоту
    cord = (x, y) — стартовая позиция
    """
    if color is None:
        color = core.constants.color_front
    max_w = size[0]
    x, y = cord

    with open(file_path, 'r', encoding='utf-8') as f:
        paragraphs = f.read().split('\n')

    space_w, line_h = font.size(' ')
    para_gap_px = int(line_h * para_gap)

    def blit_line(text):
        nonlocal y
        if text:
            surface.blit(font.render(text, True, color), (x, y))
            y += line_h

    def split_long_word(word):
        """Режем слишком длинное слово на части, чтобы влезало в max_w."""
        parts = []
        cur = ''
        for ch in word:
            nxt = cur + ch
            if font.size(nxt)[0] <= max_w or not cur:
                cur = nxt
            else:
                parts.append(cur + '-')  # мягкий перенос
                cur = ch
        if cur:
            parts.append(cur)
        return parts

    for para in paragraphs:
        words = para.split(' ') if para else ['']
        line = ''

        i = 0
        while i < len(words):
            w = words[i]
            if font.size(w)[0] > max_w:
                chunks = split_long_word(w)
                # сначала попробуем прицепить 1-й кусок к текущей строке
                for j, chunk in enumerate(chunks):
                    candidate = f"{line} {chunk}".strip() if line else chunk
                    if font.size(candidate)[0] <= max_w:
                        line = candidate
                    else:
                        blit_line(line)
                        line = chunk
                i += 1
                continue

            candidate = f"{line} {w}".strip() if line else w
            if font.size(candidate)[0] <= max_w:
                line = candidate
                i += 1
            else:
                # текущая строка уже полная — выводим и начинаем новую
                blit_line(line)
                line = ''  # не увеличиваем i, попробуем то же слово в новой строке

        blit_line(line)
        # промежуток между абзацами
        y += para_gap_px
