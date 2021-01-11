import shutil,os

os.chdir("C:\\")
print(shutil.copy("C:\\spam.txt","C:\\delicious"))
print(shutil.copy("updateExcel.xlsx","C:\\delicious"))
# print(shutil.move('spam.txt', 'c:\\does_not_exist\\eggs\\ham'))
os.chdir("C:\\")
for folderName,subFolders,fileNames in os.walk("C:\\"):
    print("当前文件夹名："+folderName)
    for subFolder in subFolders:
        print("子文件夹名："+folderName)
    for fileName in fileNames:
        print("文件名："+fileName)
    print("")