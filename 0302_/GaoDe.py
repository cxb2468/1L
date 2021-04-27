from urllib.parse import quote
from urllib import  request
import json
import xlwt

amap_web_key = "d9906f709e822ba01a01d7448ed32de7"
poi_search_url = "http://restapi.amap.com/v3/place/text"
poi_boundyaary_url= "https://ditu.amap.com/detail/get/detail"

cityName ="无锡"
classfiled = "加油站"

def getPois(cityName,keyWords):
    i = 1
    poiList = []
    while True:
        result = getPoipage(cityName,keyWords,i)
        # print(result)
        result = json.loads(result)
        if result["count"] == "0":
            break
        hand(poiList,result)
        i = i+1
        return poiList


def write2Excel(poiList,cityName,classfield):

    book = xlwt.Workbook(encoding="utf-8",style_compression=0)
    sheet = book.add_sheet(classfield,cell_overwrite_ok=True)


    sheet.write(0,0,"id")
    sheet.write(0, 1, "name")
    sheet.write(0,2, "location")
    sheet.write(0,3, "pname")
    sheet.write(0,4, "pcode")
    sheet.write(0,5, "cityname")
    sheet.write(0,6, "citycode")
    sheet.write(0,7, "adname")
    sheet.write(0,8, "adcode")
    sheet.write(0,9, "addresss")
    sheet.write(0,10, "type")
    sheet.write(0, 11, "typecode")
    sheet.write(0, 12, "gridcode")
    sheet.write(0, 13, "entr_location")
    sheet.write(0, 14, "timestamp")
    sheet.write(0, 15, "tel")
    sheet.write(0, 16, "postcode")
    sheet.write(0, 17, "tag")
    sheet.write(0, 18, "shopid")
    sheet.write(0, 19, "shopinfo")




    for i in range(len(poiList)):
        print(i)


        sheet.write(i + 1,0, poiList[i]["id"])
        sheet.write(i + 1,1, poiList[i]["name"])
        sheet.write(i + 1,2, poiList[i]["location"])
        sheet.write(i + 1,3, poiList[i]["pname"])
        sheet.write(i + 1,4, poiList[i]["pcode"])
        sheet.write(i + 1,5, poiList[i]["cityname"])
        sheet.write(i + 1,6, poiList[i]["citycode"])
        sheet.write(i + 1,7, poiList[i]["adname"])
        sheet.write(i + 1,8, poiList[i]["adcode"])
        sheet.write(i + 1, 9, poiList[i]["addresss"])
        sheet.write(i + 1, 10, poiList[i]["type"])
        sheet.write(i + 1, 11, poiList[i]["typecode"])
        sheet.write(i + 1, 12, poiList[i]["gridcode"])
        sheet.write(i + 1, 13, poiList[i]["entr_location"])
        sheet.write(i + 1, 14, poiList[i]["timestamp"])
        sheet.write(i + 1, 15, poiList[i]["tel"])
        sheet.write(i + 1, 16, poiList[i]["postcode"])
        sheet.write(i + 1, 17, poiList[i]["tag"])
        sheet.write(i + 1, 18, poiList[i]["shopid"])
        sheet.write(i + 1, 19, poiList[i]["shopinfo"])
    book.save(r"" +cityName + "_"+classfield+".xls")

def hand(poiList,result):
    pois =result["pois"]
    for i in range(len(pois)):
        poiList.append(pois[i])

def getPoipage(cityName,keyWords,page):
    req_url = poi_search_url + "?key="+amap_web_key+"&extensions=all&keywords=" +quote(
              keyWords)+"&city="+ quote(cityName) +"&citylimit=true"+ "&offset=25" + "&page" + str(
              page) +"&output=json"
    data = ""
    with request.urlopen(req_url) as f:
        data = f.read()
        data = data.decode("utf-8")

    return data

pois = getPois(cityName,classfiled)

print(pois)

write2Excel(pois,cityName,classfiled)
print("写入成功")





