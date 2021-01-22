# coding:utf-8

import os
os.system("python printLol.py")
import pickle
import sys
from printLol import printLol



man = []
other = []
print(os.getcwd())
try:
    data = open("test.txt")
    for eachLine in data:
        try:
            line = eachLine.split(":")
            role = line[0].strip()
            lineSpoken  =line[1].strip()
            if role == "man":
                man.append(lineSpoken)
            elif role == "other man":
                other.append(lineSpoken)
        except ValueError:
            pass
    data.close()



except IOError:
    print("data is missing!")
printLol(man)
printLol(other)

try:
    with open("man.txt",'w', encoding='utf-8') as manFile:
        print(man,file=manFile)
    with open("other.txt",'w', encoding='utf-8') as otherFile:
        print(other,file= otherFile)
except IOError as err:
    print("File ERROR: "+str(err))

newMan = []
try:
    with open("man.txt","rb") as manFile:
        newMan = pickle.load(manFile)
except pickle.PickleError as perr:
    print("pickle ERROR:  " + str(perr))
print(newMan)