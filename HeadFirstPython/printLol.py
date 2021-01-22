


def printLol(theList,indent=False,level=0):
    for each_item in  theList:
        if isinstance(each_item,list):
            printLol(each_item,indent,level+1)
        else:
            if indent:
                for tab_stop in range(level):
                    print("\t",end='')
            print(each_item)


def print1(nameList,indent=False):
    for name in nameList:
        if isinstance(name,list):
           print1(name,indent)
        else:
            print(name)


names = ["zhangShan","liSi",["wangWu","zhaoLiu"],"tianQi",["wangBa","123","789"],"zhouJiu"]

# print(len(names))
# printLol(names)
# print("indent = True")
# printLol(names,True)
# print("level=4")

# print1(names)

