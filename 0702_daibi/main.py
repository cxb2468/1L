from comtypes import client
import os, time, random, copy


# 174 棋子
# 171 等级 回合 金币
##27 ts.文字_识字 (32498,32629,32512,32638,"#27",0.75)
class DaiBi():
    def __init__(self, players, earlys, main_chesss, backups, number=2, is_capitulate=False):
        '''
        tft人工智能类
        :param players: 邀请的好友列表
        :param earlys: 早期过渡阵容列表
        :param main_chesss: 主阵容列表
        :param backups: 备选英雄列表
        :param number: 玩多少次 默认2局
        :param is_capitulate: 是否自动投降 默认为False
        '''
        self.lw = self.__regLW()  # 注册乐玩
        self.lw.SetPath('.\image')  # 设置全局路径
        self.lw.SetShowErrorMsg(0)  # 设置不弹错误窗口
        self.lw.SetDict(0, '1024x768_bout.txt')  # 回合
        self.lw.SetDict(1, '1024x768_chess.txt')  # 棋子
        self.lw.SetDict(2, '1024x768_else.txt')  # 羁绊
        self.lw.SetDict(3, '1024x768_money.txt')  # 金币
        self.lw.SetDict(4, '1024x768_level.txt')  # 等级
        self.is_capitulate = is_capitulate  # 是否需要自动投降
        self.earlys = earlys  # 早期过渡阵容列表
        self.main_chesss = main_chesss  # 主阵容列表
        self.backups = backups  # 备选英雄列表
        self.chess_iofo_ons = []  # 当前 场上的棋子
        self.chess_iofo_offs = []  # 当前 备战的棋子
        self.hwnd_home = 0  # home窗口句柄
        self.number = number  # 玩多少局
        self.width, self.height = 0, 0  # 目标窗口大小
        self.friends = [[171, 196, 216, 237],
                        [172, 329, 212, 365],
                        [173, 463, 210, 497],
                        [509, 460, 547, 500],
                        [848, 467, 880, 496],
                        [847, 332, 882, 362],
                        [847, 201, 883, 232],
                        ]  # 加号的位置列表
        self.players = players  # 玩家id列表
        # 需要邀请多少位好友就留下多少个位置
        self.friends = self.friends[0:len(self.players)]
        # 上场位的矩阵信息

        self.on_pos = [[[226, 303], [725, 303]],
                       [[250, 361], [760, 361]],
                       [[207, 412], [731, 412]],
                       [[245, 468], [789, 468]],
                       ]

        # 将中间5个位置补齐
        for j, pos in enumerate(self.on_pos):
            jg = pos[1][0] - pos[0][0]
            bc = jg // 6
            a = [pos[0]]  # 头
            for i in range(5):
                # 计算中间的
                a.append([pos[0][0] + (i + 1) * bc, pos[0][1]])
            a.append(pos[1])  # 尾

            self.on_pos[j] = a
            print('战斗席', a)
        self.on_pos_null = []  # 空位置有哪些
        self.off_pos_null = []  # 空位置有哪些
        # 观战位矩阵信息
        self.off_pos = [[130, 557],
                        [800, 557],
                        ]
        # 将中间7个位置补齐
        jg = self.off_pos[1][0] - self.off_pos[0][0]
        bc = jg // 8
        a = [self.off_pos[0]]
        for i in range(7):
            a.append([self.off_pos[0][0] + (i + 1) * bc, self.off_pos[0][1]])
        a.append(self.off_pos[1])
        self.off_pos = a
        print('观战席', self.off_pos)
        # 初始化时的矩阵颜色信息,用来判断是否有英雄在上面

        self.init_on_colors = [
            ['6D6D45-050505', '777347-050505', '8B783B-050505', 'AE803B-050505', 'B1863A-050505', 'A48241-050505',
             '9A9A6E-050505'],
            ['927E4B-050505', '937343-050505', '9F7C3C-050505', 'B39352-050505', '9B783C-050505', '6E7631-050505',
             '938B52-050505'],
            ['737335-050505', 'AEA264-050505', 'A28C52-050505', 'AA8249-050505', '8B7333-050505', '827635-050505',
             '9A965B-050505'],
            ['988433-050505', '8B7035-050505', '816A3C-050505', '89814C-050505', 'A28D4E-050505', '68832F-050505',
             '446627-050505']]
        # 初始化时的备战颜色信息,用来判断是否有英雄在上面

        self.init_off_colors = ['B39A77-050505', 'A49575-050505', '9F9075-050505', 'A28B72-050505', 'A48976-050505', '978373-050505', '9D8970-050505', 'A79373-050505', 'B9A472-050505']
        # 商店坐标
        self.goods = [[171, 739, 268, 760],
                      [309, 738, 411, 760],
                      [456, 739, 562, 759],
                      [602, 739, 701, 758],
                      [746, 739, 838, 759]
                      ]

    def __regLW(self):
        '''
        注册乐玩插件,需要把文件lw.dll放在根目录
        :return: 返回乐玩对象
        '''
        try:
            lw = client.CreateObject("lw.lwsoft3")
        except:
            os.system('regsvr32 lw.dll')
            lw = client.CreateObject("lw.lwsoft3")
        return lw

    def awaitHome(self, display=0, mouse=0, keypad=0, added=0, mode=0):
        '''
        寻找游戏home窗口,并且等待,它出现后自动绑定
        :return:
        '''
        # 解除一切绑定
        self.lw.UnBindWindow()
        hwnd_home = 0
        # 等待home窗口
        while hwnd_home == 0:
            hwnd_home = self.lw.FindWindow('League of Legends', 'RCLIENT')
        hwnd_home = self.lw.FindWindow('', 'CefBrowserWindow', '', 0, hwnd_home)
        hwnd_home = self.lw.FindWindow('', 'Chrome_WidgetWin_0', '', 0, hwnd_home)
        hwnd_home = self.lw.FindWindow('Chrome Legacy Window', 'Chrome_RenderWidgetHostHWND', '', 0, hwnd_home)
        # 绑定窗口
        self.hwnd_home = hwnd_home
        self.lw.SetWindowState(hwnd_home, 1)  # 激活
        ret = self.lw.BindWindow(hwnd_home, display, mouse, keypad, added, mode)
        time.sleep(1)
        self.lw.GetWindowSize(hwnd_home)  # 取窗口大小
        self.width, self.height = self.lw.x(), self.lw.y()
        return ret

    def jbLogin(self):
        '''
        登录界面
        :return:
        '''

        pass

    def jbHome(self):
        '''
        home界面的脚本
        :return:
        '''
        # 等待home出现,并且绑定
        self.awaitHome(display=3, mouse=2, keypad=2, added=0, mode=0)

        # 点击play按钮
        self.findPic('play.bmp', 1, 2, 5, 5)

        # 点击云顶之奕
        self.findPic('ydzy.bmp|ydzy1.bmp', 1, 2, 70, 30, 678, 278, 827, 346)

        # 点击确认
        self.findPic('qr.bmp', 1, 3, 5, 5)

        # 开好房间后,等待开始
        self.jbRoom()

    def jbRoom(self):
        '''
        开好房间后,准备开始界面
        :return:
        '''
        # 邀请好友 生成一个全是0的列表,具体看需要邀请多少个好友,最多7个
        rets = [1 for i in range(len(players))]
        rets2 = [0 for i in range(len(players))]  # 留着用来对比

        while True:
            if rets == rets2:  # 如果好友位都占了,则开始运行
                break
            for friend, player, i in zip(self.friends, self.players, range(len(self.players))):
                print('正在邀请', player)
                # 寻找加号 记录下来了,用来判断好友是不是全部到位了
                rets[i] = self.findPic('jh.bmp', 1, 2, 5, 5, friend[0], friend[1], friend[2], friend[3])
                if rets[i] != 0:
                    # 寻找放大镜按钮,并且点击输入框--------------------
                    self.findPic('fdj.bmp|fdj1.bmp', 1, 1, -250, 10)
                    # 在输入框中输入队友id
                    self.lw.LeftDoubleClick()
                    time.sleep(0.1)
                    self.lw.LeftDoubleClick()
                    # 输入名字

                    self.lw.SendString(player, 1)
                    time.sleep(1)
                    # 点击放大镜按钮
                    self.findPic('fdj.bmp', 1, 1, 5, 5)
                    # 点击发送邀请
                    self.findPic('fsyq.bmp', 1, 1, 5, 5)
                print('邀请成功', player)
                # -------------------------------------------
            time.sleep(5)  # 等待5秒钟
        print('全部队友邀请成功!')
        # 点击寻找对局
        self.findPic('xzdj.bmp|xzdj1.bmp', 1, 2, 5, 5)

        while True:
            if self.lw.GetKeyState(122) == 1:
                return
            ret = self.findPic('js.bmp', 1, 2, 5, 5)
            time.sleep(5)
            # 游戏界面是否出现,如果出现了就不在点继续按钮
            hwnd_game = self.lw.FindWindow('League of Legends (TM) Client', 'RiotWindowClass')
            if hwnd_game != 0:
                break
        print('成功进入游戏!')
        self.jbGame(hwnd_game)

    def jbGame(self, hwnd):
        # 将窗口转移到
        self.lw.UnBindWindow()  # 解除绑定
        self.lw.BindWindow(hwnd, 3, 0, 0, 0, 0)

        # 这里是游戏过程
        self.jbPlay()

        # 游戏结束后 绑定home窗口
        self.lw.UnBindWindow()  # 解除绑定
        self.lw.BindWindow(self.hwnd_home, 3, 2, 2, 0, 0)

    def jbPlay(self):
        '''
        具体的游戏过程脚本
        :return:
        '''
        # -----
        bout_tx=f'4{random.randint(2, 6)}'
        pos_xx = [[655, 304], [514, 453], [373, 323], [499, 232]]  # 选秀抢装备的位置
        bout_old = []  # 保留已经操作过的回合
        while self.lw.FindWindow('League of Legends (TM) Client', 'RiotWindowClass') != 0:
            time.sleep(2)
            if self.lw.GetKeyState(122) == 1:
                return
            # 当前回合
            self.lw.UseDict(0)  # 切换至回合字库
            bout = self.lw.Ocr(362, 3, 503, 27, "#80", 0.77)
            if bout != None and bout not in bout_old:  # 回合数是否寻找成功
                # 选秀
                if bout == '11' or bout == '24' or bout == '34' or bout == '44' or bout == '54' or bout == '64':
                    print('当前回合:', bout, '选秀')
                    for sss in range(15):  # 直到回合变了,才跳出
                        self.lw.UseDict(0)  # 切换至回合字库
                        po = pos_xx[random.randint(0, 3)]  # 随机一个选秀位置
                        self.lw.MoveTo(po[0], po[1])  # 走向这里,去抢装备
                        self.lw.RightClick()
                        time.sleep(1)
                elif bout == '13' or bout == '14':  # 这两个回合随便买
                    print('当前回合:', bout, '随便买')
                    if self.findPic('xzyj.bmp', 0, 0, 0, 0, 414, 589, 497, 613, 0) == 1:
                        zbls = [[171, 673], [360, 676], [548, 661], [725, 674]]
                        print('当前回合:', bout, '选装备环节')
                        if int(bout) < 40:  # 只有两件时
                            zbl = zbls[random.randint(1, 2)]
                        else:  # 4件时
                            zbl = zbls[random.randint(0, 3)]
                        self.lw.MoveTo(zbl[0], zbl[1])
                        time.sleep(0.2)
                        self.lw.LeftClick()
                    self.buyChess()
                else:  # 正常关卡
                    print(111)
                    # 先判断这个回合是否已经操作过了
                    money = self.getMoney()  # 获取钱
                    level = self.getLevel()  # 当前等级
                    print('当前回合:', bout, '正常操作', money, level)
                    # 0.判断是否是需要投降 是否需要购买升级
                    if bout == '25' or bout == '32' or bout == '41' or bout == '51':  # 这几个回合需要升级
                        print('当前回合:', bout, '需要升级', money, level)
                        self.addLevel(money, level)  # 根据金币的多少和目前等级来购买经验
                    # 4阶段 随机一个回合进行投降
                    if bout == bout_tx and self.is_capitulate == True:
                        print('当前回合:', bout, '需要投降')
                        # 寻找这些按钮,,如果没找到则继续找,,直到成功为止
                        ret = 0
                        while ret == 0:
                            # 寻找齿轮按钮
                            ret = self.findPic('cl.bmp', 1, 2, 5, 5)
                            # 寻找发起投降按钮
                            ret = self.findPic('fqtx.bmp', 1, 2, 5, 5)
                            # 寻找确认投降按钮
                            ret = self.findPic('tx.bmp', 1, 2, 5, 5)
                        time.sleep(10)  # 等待10秒钟
                        break  # 本局结束
                    # 如果遇到选装备环节
                    if self.findPic('xzyj.bmp', 0, 0, 5, 5, 414, 589, 497, 613, 0) == 1:
                        zbls = [[171, 673], [360, 676], [548, 661], [725, 674]]
                        print('当前回合:', bout, '选装备环节')
                        if int(bout) < 40:  # 只有两件时
                            zbl = zbls[random.randint(1, 2)]
                        else:  # 4件时
                            zbl = zbls[random.randint(0, 3)]
                        self.lw.MoveTo(zbl[0], zbl[1])
                        time.sleep(0.2)
                        self.lw.LeftClick()
                    # 正常流程
                    print('当前回合:', bout, '无多余操作', money, level)
                    # 1.扫描作战位
                    self.getChessIofoOns()
                    # 2.扫描观战位
                    self.getChessIofoOffs()
                    # 3.扫描装备位置 并且给场上排列前茅的 英雄设置装备
                    # self.setEquips()
                    # 4.根据收集到的 所有信息 来判断哪些是需要留下来的英雄
                    count = self.countArray(bout, level)  # 计算得出哪些英雄是需要的
                    print(count)
                    # 5.根据收集到的 所有信息 来购买商店的英雄 补足羁绊凑2-3星 并且判断 是否需要刷新牌库
                    self.buyChess(count)  # 根据留下的羁绊来刷新商店并且购买英雄
                    if bout == '42' or int(bout) >= 50:
                        self.refresh(money, count)  # 根据金币的多少和留下的羁绊来刷新商店并且购买英雄
                    # 6.将没上场的羁绊内的英雄替换放入场中(位置优先为已经有英雄上场的位置)
                    self.setPos(count, bout, level)
                bout_old.append(bout)  # 将找到的回合记录下来 备份一个
                self.lw.MoveTo(0, 0)  # 鼠标移开
                self.lw.LeftClick()
        print('本局结束')

    def color_list(self):
        init_on_colors = []
        for item in self.on_pos:  # 一排
            colors = []
            for pos in item:  # 每一个坐标
                # 每一个坐标都进行取色
                color = self.lw.GetColor(pos[0], pos[1]) + '-050505'
                colors.append(color)
            init_on_colors.append(colors)
        self.init_on_colors = init_on_colors

        init_on_colors = []
        for item in self.on_pos:  # 一排
            colors = []
            for pos in item:  # 每一个坐标
                # 每一个坐标都进行取色
                color = self.lw.GetColor(pos[0], pos[1]) + '-050505'
                colors.append(color)
            init_on_colors.append(colors)
        self.init_on_colors = init_on_colors

        init_off_colors = []
        for pos in self.off_pos:
            color = self.lw.GetColor(pos[0], pos[1]) + '-050505'
            init_off_colors.append(color)
        self.init_off_colors = init_off_colors

        print(self.init_on_colors)
        print(self.init_off_colors)

    def setEquips(self):
        pass

    def getChessIofoOns(self):
        '''
        获取当前在场上的棋子信息
        :return:
        '''
        on_pos_null = []
        chess_iofo_ons = []
        i = 0
        for item, item2 in zip(self.on_pos, self.init_on_colors):
            if i % 2 == 0:
                time.sleep(0.5)
                self.lw.MoveTo(item[0][0] + 50, item[0][1] + 50)
                self.lw.RightClick()  # 移动一下角色 顺便捡金币
            else:
                time.sleep(0.5)
                self.lw.MoveTo(item[-1][0] + 50, item[-1][1] + 50)
                self.lw.RightClick()  # 移动一下角色 顺便捡金币
            for pos, color in zip(item, item2):
                if self.lw.GetKeyState(122) == 1:
                    return
                # 判断颜色 如果有很明显的变化则进行识别操作
                if self.lw.CmpColor(pos[0], pos[1], color, 0.8) == 1:
                    self.lw.MoveTo(pos[0], pos[1])
                    self.lw.LeftClick()  # 将英雄提起来
                    time.sleep(0.3)
                    self.lw.UseDict(2)  # 切换至其它字库
                    ret = self.lw.Ocr(377, 698, 446, 736, "#27", 0.8)
                    if ret == '出售以':
                        self.lw.LeftClick()  # 放下英雄
                        time.sleep(0.1)
                        self.lw.RightClick()  # 展示英雄资料
                        time.sleep(0.3)
                        star = self.lw.Ocr(pos[0], pos[1] - 80, pos[0] + 150, pos[1] + 150, "#27", 0.75)
                        self.lw.UseDict(1)  # 切换至棋子字库
                        name = self.lw.Ocr(pos[0], pos[1] - 50, pos[0] + 230, pos[1] + 150, "#186", 0.7)
                        if star == None or star == 'None':
                            star == '★'
                        # 将在战争席的英雄信息记录下来
                        chess_iofo_ons.append({'pos': pos, 'name': name, 'star': star})
                        self.lw.RightClick()  # 将信息取消


                else:  # 空位置
                    on_pos_null.append(pos)
            i += 1

        self.on_pos_null = on_pos_null  # 更新空位置
        self.chess_iofo_ons = chess_iofo_ons  # 更新在场上的英雄信息
        print(self.chess_iofo_ons)

    def getChessIofoOffs(self):
        chess_iofo_offs = []
        off_pos_null = []
        for pos, color in zip(self.off_pos, self.init_off_colors):
            if self.lw.GetKeyState(122) == 1:
                return
            # 判断颜色 如果有很明显的变化则进行识别操作
            if self.lw.CmpColor(pos[0], pos[1], color, 0.8) == 1:
                self.lw.MoveTo(pos[0], pos[1])
                self.lw.LeftClick()  # 将英雄提起来
                time.sleep(0.3)
                self.lw.UseDict(2)  # 切换至其它字库
                ret = self.lw.Ocr(377, 698, 446, 736, "#27", 0.8)
                if ret == '出售以':
                    self.lw.LeftClick()  # 放下英雄
                    time.sleep(0.1)
                    self.lw.RightClick()  # 展示英雄资料
                    time.sleep(0.3)
                    star = self.lw.Ocr(pos[0], pos[1] - 80, pos[0] + 150, pos[1] + 150, "#27", 0.77)
                    self.lw.UseDict(1)  # 切换至棋子字库
                    name = self.lw.Ocr(pos[0], pos[1] - 50, pos[0] + 230, pos[1] + 150, "#186", 0.70)

                    if star == None or star == 'None':
                        star == '★'
                    # 将在备战席的英雄信息记录下来
                    chess_iofo_offs.append({'pos': pos, 'name': name, 'star': star})
                    self.lw.RightClick()  # 将信息取消
            else:
                off_pos_null.append(pos)
        self.off_pos_null = off_pos_null  # 空位置
        self.chess_iofo_offs = chess_iofo_offs  # 更新在备战席的英雄信息
        print(self.chess_iofo_offs)

    def getMoney(self):
        '''
        获取当前有多少金币
        :return:
        '''
        self.lw.UseDict(3)  # 切换至金币字库
        ret = self.lw.Ocr(448, 628, 480, 649, "#171", 0.70 )
        if ret == '':
            return 0
        else:
            try:
                return int(ret)
            except:
                return 0

    def getLevel(self):
        '''
        获取当前等级
        :return:
        '''
        self.lw.UseDict(4)  # 切换至等级字库
        ret = self.lw.Ocr(24, 628, 37, 647, "#171", 0.7)
        if ret == '':
            return 0
        else:
            try:
                return int(ret)
            except:
                return 0

    def countArray(self, bout, level):
        # 如果是前期则发现前期列表中有就都买
        count = []  # 留下和需要购买的
        if bout == '13' or bout == '14' or bout == '21' or bout == '22' or bout == '23':
            # 将所有的前期英雄都标记为可以购买
            for item in self.earlys:
                count += item
        else:
            if level < 7:
                # 如果小于7级则以凑出早期过渡阵容为主
                count = self.getWeight(self.earlys)
            else:  # 大于7级后
                count = self.getWeight(self.main_chesss)
        return count

    def getWeight(self, chesss_array):
        # 所有已拥有的棋子
        chess_iofo_all = self.chess_iofo_ons + self.chess_iofo_offs
        ears = []  # 权重列表
        # 计算权重
        # 扫描前期列表中哪个当前完整度最高的
        for chess in chess_iofo_all:
            e = 0
            for early in chesss_array:
                if chess['name'] in early:
                    if chess['star'] == '★':
                        e += 1  # 权重值
                    elif chess['star'] == '★★':
                        e += 3  # 权重值
                    elif chess['star'] == '★★★':
                        e += 9  # 权重值
                    else:
                        e += 1
            ears.append(e)

        # 取出权重最高的前期卡组
        try:
            return chesss_array[ears.index(max(ears))]
        except:
            return []

    def addLevel(self, money, level):
        # 自动升级程序
        while self.getLevel() != level or self.getLevel() == None:  # 不等于为止 也就是升级了
            self.lw.KeyPress(70)
            time.sleep(0.2)
            if money < 4:
                return  # 不够钱了也结束

    def refresh(self, money, count):
        # 刷新商店
        max = random.randint(1, 30)  # 随机多少次
        for i in range(max):
            money -= 2
            last_money = copy.copy(money)
            self.lw.KeyPress(68)  # 按D刷新牌库
            time.sleep(0.2)
            self.buyChess(count)  # 购买需要的棋子
            time.sleep(0.5)
            if last_money == self.getMoney():  # 如果买不了了说明位置满了
                return
            if money < 2:  # 没钱了
                return

    def buyChess(self, count=None):

        self.lw.UseDict(1)  # 切换至棋子字库
        for item in self.goods:
            name = self.lw.Ocr(item[0], item[1], item[2], item[3], "#174", 0.77)
            if count == None:  # 前期随便买
                self.lw.MoveTo(item[0] + 65, item[1] - 40)
                time.sleep(0.2)
                self.lw.LeftClick()
            else:
                if name in count:  # 只要在阵容中则购买
                    self.lw.MoveTo(item[0] + 65, item[1] - 40)
                    time.sleep(0.2)
                    self.lw.LeftClick()

    def setPos(self, count, bout, level):
        try:
            # 所有已拥有的棋子
            print('设置站位,以及判断需不需要卖掉')
            if bout == '21' or bout == '22' or bout == '23' or bout == '24' or bout == '25' or bout == '26' or bout == '27':
                chess_iofo_all = self.chess_iofo_ons + self.chess_iofo_offs

                length = len(self.chess_iofo_ons)
                # 使用星级进行排序 冒泡 倒序
                n = len(chess_iofo_all)
                for i in range(n):
                    for j in range(0, n - i - 1):
                        # 如果星级大于则进行上浮
                        if len(chess_iofo_all[j]['star']) < len(chess_iofo_all[j + 1]['star']):
                            chess_iofo_all[j], chess_iofo_all[j + 1] = chess_iofo_all[j + 1], chess_iofo_all[j]

                for i in range(level):  # 一共就这么多位置
                    if chess_iofo_all[i] not in self.chess_iofo_ons:  # 这个棋子不在场上 才需要操作
                        if i + 1 < length:  # 优先场上的位置
                            # 选中这个英雄
                            self.lw.MoveTo(chess_iofo_all[i]['pos'][0], chess_iofo_all[i]['pos'][1])
                            time.sleep(0.2)
                            self.lw.LeftClick()

                            # 放到战斗席位置交换
                            self.lw.MoveTo(self.chess_iofo_ons[i]['pos'][0], self.chess_iofo_ons[i]['pos'][1])
                            time.sleep(0.2)
                            self.lw.LeftClick()
                        else:
                            # 如果有空位,那就放一个空的地方
                            # 选中这个英雄
                            self.lw.MoveTo(chess_iofo_all[i]['pos'][0], chess_iofo_all[i]['pos'][1])
                            time.sleep(0.2)
                            self.lw.LeftClick()

                            # 放到战斗席位置交换 空位置中靠后排,,最靠后的位置
                            self.lw.MoveTo(self.on_pos_null[-1]['pos'][0], self.on_pos_null[-1]['pos'][1])
                            time.sleep(0.2)
                            self.lw.LeftClick()
            else:  # 正常对局时
                # 1.将不是count中的棋子卖出
                # 战斗席的
                ls_s = []
                for item in self.chess_iofo_ons:
                    if item['name'] not in count and item['name'] != None:
                        # 卖出该棋子
                        self.lw.MoveTo(item['pos'][0], item['pos'][1])
                        time.sleep(0.2)
                        # 按E卖出
                        self.lw.KeyPress(69, )
                        self.on_pos_null.append(item['pos'])  # 剩余的位置增加一个
                    else:
                        ls_s.append(item)  # 重新计算战斗席的英雄信息
                self.chess_iofo_ons = ls_s

                # 备战席的
                ls_s = []
                for item in self.chess_iofo_offs:
                    if item['name'] not in count and item['name'] != None:
                        # 卖出该棋子
                        self.lw.MoveTo(item['pos'][0], item['pos'][1])
                        time.sleep(0.2)
                        # 按E卖出
                        self.lw.KeyPress(69, )
                        self.off_pos_null.append(item['pos'])  # 剩余的位置增加一个
                    else:
                        ls_s.append(item)  # 重新计算战斗席的英雄信息
                self.chess_iofo_offs = ls_s

                chess_iofo_all = self.chess_iofo_ons + self.chess_iofo_offs

                # 2.排序 ,将星级高放前面,然后去除重复
                # 使用星级进行排序 冒泡 倒序
                n = len(chess_iofo_all)
                for i in range(n):
                    for j in range(0, n - i - 1):
                        # 如果星级大于则进行上浮
                        if len(chess_iofo_all[j]['star']) < len(chess_iofo_all[j + 1]['star']):
                            chess_iofo_all[j], chess_iofo_all[j + 1] = chess_iofo_all[j + 1], chess_iofo_all[j]

                # 去掉重复的,优先留下前面的
                ls = []
                iofo_all = []
                for item in chess_iofo_all:
                    if item['name'] not in ls:
                        iofo_all.append(item)  # 这要这个名字没出现过的

                    ls.append(item['name'])  # 将名字加入进去,,这要就会有一次加入成功这个name

                chess_iofo_all = iofo_all  # 只留下没重复的

                length = len(self.chess_iofo_ons)  #这个我后加的 为了下一个length不报红
                for i in range(level):  # 一共就这么多位置
                    if chess_iofo_all[i] not in self.chess_iofo_ons:  # 这个棋子不在场上 才需要操作
                        if i + 1 < length:  # 优先场上的位置
                            # 选中这个英雄
                            self.lw.MoveTo(chess_iofo_all[i]['pos'][0], chess_iofo_all[i]['pos'][1])
                            time.sleep(0.2)
                            self.lw.LeftClick()

                            # 放到战斗席位置交换
                            self.lw.MoveTo(self.chess_iofo_ons[i]['pos'][0], self.chess_iofo_ons[i]['pos'][1])
                            time.sleep(0.2)
                            self.lw.LeftClick()
                        else:
                            # 如果有空位,那就放一个空的地方
                            # 选中这个英雄
                            self.lw.MoveTo(chess_iofo_all[i]['pos'][0], chess_iofo_all[i]['pos'][1])
                            time.sleep(0.2)
                            self.lw.LeftClick()

                            # 放到战斗席位置交换 空位置中靠后排,,最靠后的位置
                            self.lw.MoveTo(self.on_pos_null[-1]['pos'][0], self.on_pos_null[-1]['pos'][1])
                            time.sleep(0.2)
                            self.lw.LeftClick()
        except:
            pass

    def start_main(self):
        '''
        房主脚本
        :return:
        '''
        # 执行主界面脚本
        self.jbHome()
        for i in range(self.number):
            if self.lw.GetKeyState(122) == 1:
                return
            # 邀请好友,直到满足条件
            self.jbRoom()

        # 最后释放绑定
        self.lw.UnBindWindow()

    def test(self):
        # 测试代码
        hwnd_game = self.lw.FindWindow('League of Legends (TM) Client', 'RiotWindowClass')
        self.jbGame(hwnd_game)

    def findPic(self, pic, isClick=1, time_sleep=0, dex=1, dey=1, x1=0, y1=0, x2=-1, y2=-1, htime=5000):
        '''
        找单个图,默认会点击,
        :param pic: 图片名
        :param isClick: 是否点击 1点击 0不点 默认1
        :param time_sleep: 点击后等待时间
        :param dex: 偏移x
        :param dey: 偏移y
        :param x1: x1 起始点
        :param y1: y1 起始点
        :param x2: 默认为窗口的宽度
        :param y2: 默认为窗口的高度
        :return:
        '''
        if x2 == -1:
            x2 = self.width
        if y2 == -1:
            self.height
        ret = self.lw.FindPic(x1, y1, x2, y2, pic,
                              '050505', 0.7, 0, htime, isClick, dex, dey, 100)
        print(pic, ret)
        if time_sleep > 0 and isClick == 1:
            time.sleep(time_sleep)
        return ret


if __name__ == "__main__":
    # 玩家id列表
    # 'Carry丶JianSheng',
    players = []
    # 早期过度阵容
    earlys = [['蕾欧娜', '亚托克斯', '薇恩', '锤石', '维鲁斯', '波比', '诺提勒斯'],
              ['瑟提', '努努和威朗普', '卡莉斯塔', '布兰德', '沃里克', '古拉加斯', '维克托'],
              ['莫甘娜', '弗莱基米尔', '乐芙兰', '卡兹克', '丽桑卓', '拉克丝', '璐璐'],
              ]
    # 主阵容
    main_chesss = [
        ['蕾欧娜', '锤石', '波比', '诺提勒斯', '塔里克斯', '盖伦', '德莱厄斯'],
        ['瑟提', '努努和威朗普', '卡莉斯塔', '布兰德', '沃里克', '古拉加斯', '维克托', '维克兹'],
        ['莫甘娜', '弗莱基米尔', '乐芙兰', '卡兹克', '丽桑卓', '拉克丝', '璐璐', '瑞兹'],
    ]
    # 替补
    backups = [
        ['德莱厄斯', '波比'],
        ['古拉加斯', '沃利贝尔'],
        ['拉克丝', '千珏']
    ]
    db = DaiBi(players, earlys, main_chesss, backups,is_capitulate=True)
    #是否是直接测试
    if db.lw.FindWindow('League of Legends (TM) Client', 'RiotWindowClass')!=0:
        db.test()
    else:
        db.start_main()
