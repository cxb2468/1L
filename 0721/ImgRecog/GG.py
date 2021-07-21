from imutils import contours
import cv2
import os



def cv_show(name, img):
    cv2.imshow(name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def resize(image, width=None, height=None, inter=cv2.INTER_AREA):
    dim = None
    (h, w) = image.shape[:2]
    if width is None and height is None:
        return image
    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))
    resized = cv2.resize(image, dim, interpolation=inter)
    return resized


def load_digits():
    # 加载数字模板
    # path = r"C:\Users\17513\Desktop\Flying\numbers"
    path = numbers_address
    filename = os.listdir(path)
    for file in filename:
        # print(file)
        img = cv2.imread(
            numbers_address + "\\" + file)
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img_temp = cv2.threshold(
            img_gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        cnt = cv2.findContours(img_temp, cv2.RETR_EXTERNAL,
                               cv2.CHAIN_APPROX_NONE)[0]
        x, y, w, h = cv2.boundingRect(cnt[0])
        digit_roi = cv2.resize(img_temp[y:y+h, x:x+w], (57, 88))
        # draw_img_temp = cv2.drawContours(img, cnt, 0, (0, 0, 255), 1)
        # 将数字模板存到列表中
        digits.append(digit_roi)
        # cv_show("666", digit_roi)
    # print("加载数字模板成功")


def demo(index):
    # cv2.namedWindow("666", 1)
    rectKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 25))
    sqKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    target_path = now_dir + "\\" + "demo_" + str(index) + ".png"
    img_origin = cv2.imread(target_path)
    img_origin = resize(img_origin, width=300)
    img_gray = cv2.cvtColor(img_origin, cv2.COLOR_BGR2GRAY)
    gaussian = cv2.GaussianBlur(img_gray, (5, 5), 1)
    img_temp = cv2.threshold(
        gaussian, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    img_top = cv2.morphologyEx(img_temp, cv2.MORPH_TOPHAT, rectKernel)
    img_sobel_x = cv2.Sobel(img_top, cv2.CV_64F, 1, 0, ksize=7)
    img_sobel_x = cv2.convertScaleAbs(img_sobel_x)
    img_sobel_y = cv2.Sobel(img_top, cv2.CV_64F, 0, 1, ksize=7)
    img_sobel_y = cv2.convertScaleAbs(img_sobel_y)
    img_sobel_xy = cv2.addWeighted(img_sobel_x, 1, img_sobel_y, 1, 0)
    img_closed = cv2.morphologyEx(img_sobel_xy, cv2.MORPH_CLOSE, rectKernel)
    thresh = cv2.threshold(
        img_closed, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    img_closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, sqKernel)
    cnts = cv2.findContours(
        img_closed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[0]
    (cnts, boundingBoxes) = contours.sort_contours(cnts, "top-to-bottom")
    # draw_img = img_origin.copy()
    # for (i, c) in enumerate(cnts):
    #     x, y, w, h = cv2.boundingRect(c)
    #     sortedImage = cv2.rectangle(
    #         draw_img, (x, y), (x+w, y+h), (0, 255, 0), 1)
    #     # sortedImage = contours.label_contour(draw_img, c, i, color=(0, 0, 0), thickness=1)
    #     cv_show("666", sortedImage)
    draw_img = img_origin.copy()
    draw_img = cv2.drawContours(draw_img, cnts, -1, (0, 0, 255), 1)
    # cv_show("666", draw_img)

    # 存放正确数字序列（包含逗号）的轮廓，即过滤掉不需要的轮廓
    right_loc = []
    # con = []
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        ar = w/float(h)
        if ar > 2:
            right_loc.append((x, y, w, h))
            # con.append(c)
    # print(len(con))
    # draw_img = img_origin.copy()
    # draw_img = cv2.drawContours(draw_img, con, -1, (0, 0, 255), 1)
    # cv_show('666', draw_img)
    # print("加载demo数字大轮廓成功")
    for (gx, gy, gw, gh) in right_loc:
        # 用于存放识别到的数字
        digit_out = []
        if (gy-10 < 0):
            now_gy = gy
        else:
            now_gy = gy-10
        if (gx - 10 < 0):
            now_gx = gx
        else:
            now_gx = gx-10
        img_digit = gaussian[now_gy:gy+gh+10, now_gx:gx+gw+10]
        # 二值化处理
        img_thresh = cv2.threshold(
            img_digit, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        # cv_show("666", img_thresh)
        # 寻找轮廓 找出每个数字的轮廓（包含逗号） 正确的话应该有9个轮廓
        digitCnts = cv2.findContours(
            img_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[0]
        # 从左到右排列
        (cnts, boundingBoxes) = contours.sort_contours(digitCnts, "left-to-right")
        cnts = list(cnts)
        # for (i, c) in enumerate(cnts):
        #     sortedImage = contours.label_contour(img_thresh, c, i, color=(0, 0, 0), thickness=1)
        #     cv_show("666", sortedImage)
        flag = 0
        if len(cnts) == 9:
            del cnts[1]
            del cnts[2]
            del cnts[3]
            del cnts[4]
            # for (i, c) in enumerate(cnts):
            #     sortedImage = contours.label_contour(img_thresh, c, i, color=(0, 0, 0), thickness=1)
            #     cv_show("666", sortedImage)
            cnts = tuple(cnts)
            # img_out = cv2.drawContours(img_digit, digitCnts, -1, (0, 0, 255), 1)
            # cv_show("666", img_out)
            # print(len(digitCnts))
            num_roi = []
            for c in cnts:
                x, y, w, h = cv2.boundingRect(c)
                # img_out = cv2.rectangle(
                #     img_digit, (x, y), (x+w, y+h), (0, 0, 255), 1)
                # cv_show("666", img_out)
                num_roi.append((x, y, w, h))
            for (rx, ry, rw, rh) in num_roi:
                roi = img_digit[ry:ry+rh, rx:rx+rw]
                roi = cv2.resize(roi, (57, 88))
                roi = cv2.GaussianBlur(roi, (5, 5), 1)
                roi = cv2.threshold(
                    roi, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
                # cv_show("666", roi)
                source = []
                for digitROI in digits:
                    res = cv2.matchTemplate(
                        roi, digitROI, cv2.TM_CCOEFF_NORMED)
                    max_val = cv2.minMaxLoc(res)[1]
                    source.append(max_val)
                digit_out.append(str(source.index(max(source))))
            # digit_out.reverse()
            cv2.rectangle(img_origin, (gx-5, gy-5),
                          (gx+gw+5, gy+gh+5), (0, 0, 255), 1)
            print(digit_out)
        else:
            print("读取失败")
            flag = 1
        t = ''
        with open(now_dir + "\\temp.txt", 'a+') as q:
            if flag == 0:
                for content in digit_out:
                    t = t + str(content) + " "
                q.write(t.strip(" "))
                q.write('\n')
                t = ''
            else:
                q.write("读取失败")
                q.write('\n')
    # cv_show("666", img_origin)


if __name__ == "__main__":
    # 存放数字模板列表
    digits = []
    # 当前运行目录
    now_dir = os.getcwd()
    print("当前运行目录：" + now_dir)
    numbers_address = now_dir + "\\numbers"
    load_digits()
    # demo(1)
    times = input("请输入程序运行次数：")
    for i in range(1, int(times) + 1):
        demo(i)
    print("输出成功，请检查本地temp.txt文件")
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    while True:
        if input("输入小写‘q’并回车退出") == 'q':
            break
