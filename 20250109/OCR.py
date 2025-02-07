import time
from ctypes import windll
import numpy as np
import cv2
from mss import mss


class Mxbx:
    def __init__(self):
        print('欢迎使用')
        windll.user32.SetProcessDPIAware()
        self.sct = mss()

    def GetCapture(self, x1, y1, x2, y2):
        '''
        截图
        :param x1:
        :param y1:
        :param x2:
        :param y2:
        :return: rgb图像
        '''
        monitor = {'top': y1, 'left': x1, 'width': x2 - x1, 'height': y2 - y1}
        pic = self.sct.grab(monitor)
        pic = cv2.cvtColor(np.array(pic), cv2.COLOR_RGBA2RGB)
        return pic

    def parse_custom_color(self, color_string):
        r, g, b = int(color_string[4:6], 16), int(color_string[2:4], 16), int(color_string[0:2], 16)
        if len(color_string) > 6:
            dr, dg, db = int(color_string[7:9], 16), int(color_string[9:11], 16), int(color_string[11:13], 16)
        else:
            dr, dg, db = 0, 0, 0
        lower_rgb = np.array([max(0, r - dr), max(0, g - dg), max(0, b - db)], dtype=np.uint8)
        upper_rgb = np.array([min(255, r + dr), min(255, g + dg), min(255, b + db)], dtype=np.uint8)
        return lower_rgb, upper_rgb

    def Stressshow(self, x1, y1, x2, y2, colors, types=0):
        '''
        隐藏其他颜色为黑色，只保留选中颜色
        :param x1: 起点x
        :param y1: 起点Y
        :param x2: 终点x
        :param y2: 终点Y
        :param colors: 十六进制颜色，可以从大漠的色彩描述直接获取
        :param types: 0：原来颜色，非零：白色
        :return:
        '''
        image = self.GetCapture(x1, y1, x2, y2)
        colors = colors.split("|")
        masks = np.zeros_like(image[:, :, 0], dtype=np.uint8)
        for color in colors:
            lower_rgb, upper_rgb = self.parse_custom_color(color)
            mask = cv2.inRange(image, lower_rgb, upper_rgb)
            masks += mask
        result = cv2.bitwise_and(image, image, mask=masks)
        if types:
            result[np.where(masks != 0)] = [255, 255, 255]
        return result

    def SetDict(self, lines):
        '''
        初始化字库文件
        :param lines: 字库数组
        :return: 点阵数据
        '''
        des = {}
        for line in lines[1:]:
            parts = line.split("$")
            hex_str = parts[0]
            hex_values = np.array([int(c, 16) for c in hex_str], dtype=np.uint8)
            bin_values = np.unpackbits(hex_values[:, None], axis=1).reshape(-1, 8)[:, 4:]  # 只需要后4位
            num_elements = bin_values.shape[0]
            remainder = num_elements % 11
            if remainder != 0:
                padding = 11 - remainder
                bin_values = np.pad(bin_values, ((0, padding), (0, 0)), mode='constant', constant_values=0)
            bin_values = bin_values.reshape(-1, 11).T
            des.setdefault(parts[1], bin_values)
        return lines[0], des

    def Ocr(self, x1, y1, x2, y2, thd, DIict):
        '''
        点阵文字识别
        :param x1:
        :param y1:
        :param x2:
        :param y2:
        :param thd: 相似度
        :param DIict: 字库
        :return:
        '''

        def filter_points(points, max_distance):
            if points.shape[0] <= 1:
                return points

            diff = points[:, None, :] - points[None, :, :]
            distances = np.linalg.norm(diff, axis=2)
            mask = distances < max_distance
            to_remove = np.zeros(len(points), dtype=bool)
            for i in range(len(points)):
                if to_remove[i]:
                    continue
                for j in range(i + 1, len(points)):
                    if mask[i, j]:
                        to_remove[j] = True
            cleaned_data = points[~to_remove]
            return cleaned_data

        img = self.Stressshow(x1, y1, x2, y2, DIict[0], 1)
        img = (img != 0).any(axis=2).astype(int)
        img = np.array(img, dtype=np.uint8)
        res = {}
        for key, value in DIict[1].items():
            _, h = value.shape
            if x2 - x1 > h and y2 - y1 > 11:
                result = cv2.matchTemplate(value, img, cv2.TM_CCOEFF_NORMED)
                loc = np.column_stack(np.where(result >= thd))
                loc = filter_points(loc, min(6, h))
                if loc.size > 1:
                    py, px = 6 + y1, int(h / 2 + x1)
                    loc += (py, px)
                    loc = loc[:, [1, 0]]
                    res.setdefault(key, loc)
        return res if len(res) > 0 else 0

    def Getocr(self, input_data, x_size=15):
        '''
        解析ocr
        :param input_data:ocr返回值
        :param x_size: x间距，距离小合并到一起
        :return:
        '''
        output = [(key, tuple(row)) for key, arr in input_data.items() for row in arr]
        output.sort(key=lambda x: x[1][1])
        groups = []
        current_group = []
        for i, (char, coord) in enumerate(output):
            if current_group:
                last_coord = current_group[-1][1]
                if abs(coord[1] - last_coord[1]) <= 5:
                    current_group.append((char, coord))
                else:
                    groups.append(current_group)
                    current_group = [(char, coord)]
            else:
                current_group.append((char, coord))
        if current_group:
            groups.append(current_group)

        def merge_by_x_coordinate(groups, size=x_size):
            merged_groups = []
            for group in groups:
                group.sort(key=lambda x: x[1][0])
                merged_group = []
                current_subgroup = []
                for i, (char, coord) in enumerate(group):
                    if not current_subgroup:
                        current_subgroup.append((char, coord))
                    else:
                        last_char, last_coord = current_subgroup[-1]
                        if abs(coord[0] - last_coord[0]) <= size:
                            current_subgroup.append((char, coord))
                        else:
                            merged_group.append(current_subgroup)
                            current_subgroup = [(char, coord)]
                if current_subgroup:
                    merged_group.append(current_subgroup)
                merged_groups.append(merged_group)
            return merged_groups

        merged_groups = merge_by_x_coordinate(groups, size=x_size)

        def merge_characters(merged_groups):
            merged_dict = {}
            for group in merged_groups:
                for subgroup in group:
                    merged_char = ''.join([char for char, _ in subgroup])
                    first_coord = subgroup[0][1]
                    if merged_char not in merged_dict:
                        merged_dict[merged_char] = []
                    merged_dict[merged_char].append(first_coord)
            return merged_dict

        merged_dict = merge_characters(merged_groups)
        return merged_dict


a = Mxbx()
st = time.time()

# 初始化字库数据，第一行为颜色值，后续为字库数据
zk1 = a.SetDict(['b6ffdb-202020|ffffff-202020|ffb666-303030|90dbff-202020|ffffdb-202020',
                 '2080525220500D21A1FD44C0D0560A864008110$梁$0.0.52$13',
                 '04108610C604A4030$3$0.0.16$11',
                 '200001007FF$1$0.0.13$11',
                 '268C1A00C01803001C60$0$0.0.20$11',
                 ])
# 这个字库数据是电脑右下角时间及日期
zk2 = a.SetDict(['d0d4d5-303030',
                 '200401007FFFFE$1$0.0.25$11',
                 '40F8360CC11863F85E08$2$0.0.32$11',
                 '40508610C21CE6F78060$3$0.0.28$11',
                 '0100E0340C8711FFFFF808$4$0.0.37$11',
                 '085F0620C418C70F80E0$5$0.0.28$11',
                 '1F8ED920C4188318E1F0$6$0.0.33$11',
                 '80100201C0F871383C0600$7$0.0.24$11',
                 '33CFCE10C21843FCDCF0$8$0.0.39$11',
                 '7C58C608C11826DF8FC0$9$0.0.35$11',
                 '3F8C1E00C01803C19FE0$0$0.0.31$11'])

b = a.Ocr(1763, 1032, 1855, 1079, 0.9, zk2)
if b:
    b = a.Getocr(b, 15)

print(time.time() - st)
print(b)