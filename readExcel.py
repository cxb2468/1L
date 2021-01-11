import openpyxl,pprint
print("打开工作簿")
wb = openpyxl.load_workbook("口算.xlsx")
sheet = wb["population"]
countryData = {}

#读取每行row 数据
print("读取每行数据。。。")
for row  in range(2,sheet.max_row+1):
    state =sheet["B"+str(row)].value
    country = sheet["C"+str(row)].value
    pop = sheet["D" + str(row)].value
    #数据结构
    countryData.setdefault(state,{})

    countryData[state].setdefault(country,{"tracts":0,"pop":0})

    countryData[state][country]["tracts"] +=1

    countryData[state][country]["pop"] += int(pop)

#将结果写入文件
print("写入结果数据")
resultFile = open("readExcel2010.py","w")
resultFile.write("allData = " +pprint.pformat(countryData))
print("已完成！")



