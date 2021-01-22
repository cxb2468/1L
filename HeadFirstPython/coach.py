
#教练要 从 运动数据文本中提取  4个运动员成绩前3的时间 分别是多少？

# 读取4个txt文件，拿到从‘，’分割 的数据
# with open("jame.txt","r",encoding="utf-8") as jameFile:
#     jame =jameFile.readline().strip().split(',')
# print(jame)
#
# with open("juli.txt","r",encoding="utf-8") as juliFile:
#     juli =juliFile.readline().strip().split(',')
# print(juli)
#
# with open("mike.txt","r",encoding="utf-8") as mikeFile:
#     mike =mikeFile.readline().strip().split(',')
# print(mike)
#
# with open("sara.txt","r",encoding="utf-8") as saraFile:
#     sara =saraFile.readline().strip().split(',')
# print(sara)
#将 上述 4个同类代码 抽取成get_coach_data()方法 返回字典{}
def get_coach_data(fileName):
    try:
        with open(fileName,"r",encoding="utf-8") as fn:
            data = fn.readline()
            temp = data.strip().split(",")
            print(temp)

        return ({"name": temp.pop(0).split('"')[1],
                 "DOB": temp.pop(0),
                 "Times"  : str(sorted(set(format(t) for t in temp))[0:3])})
    except IOError:
        print(str(IOError))
        return (None)


# pop前两个数据 对运动成绩数据  进行处理 将数据以  - ； 分割，然后再拼接成 1.11的形式

def format(times):
    if "-" in times:
        splitter = "-"
    elif ":"  in times:
         splitter = ":"
    else:
         return times
    time = times.split(splitter)
    min = time[0]
    sec = time[1]
    return (min +"."+sec)


jame = get_coach_data("jame.txt")
juli = get_coach_data("juli.txt")
mike = get_coach_data("mike.txt")
sara = get_coach_data("sara.txt")

print(jame["name"]+" 3 times : "+jame["Times"])
print(juli["name"]+" 3 times : "+juli["Times"])
print(mike["name"]+" 3 times : "+mike["Times"])
print(sara["name"]+" 3 times : "+sara["Times"])