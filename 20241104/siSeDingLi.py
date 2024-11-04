import geopandas as gpd
import folium
from shapely.geometry import shape

# 读取JSON格式的中国地图数据
url = 'https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json'
china_map = gpd.read_file(url, encoding='utf-8')

# 进行几何图形的拓扑修复
china_map['geometry'] = china_map['geometry'].apply(lambda x: shape(x).buffer(0))

# 创建省份颜色映射
color_map = {}
colors = ['red', 'green', 'blue', 'yellow']

# 遍历省份
for index, row in china_map.iterrows():
    # 获取相邻省份的颜色
    neighbor_colors = set(color_map[neighbor] for neighbor in china_map.index[china_map.intersects(row['geometry'])] if
                          neighbor in color_map)
    # 找到一个未被使用的颜色
    next_color = next((color for color in colors if color not in neighbor_colors), None)
    # 为该省份分配颜色
    color_map[index] = next_color

# 将颜色映射应用到DataFrame
china_map['color'] = china_map.index.map(color_map)

# 创建交互式地图
m = folium.Map(location=[35.8617, 104.1954], zoom_start=4)

# 添加 GeoJSON 图层
folium.GeoJson(
    china_map,
    style_function=lambda x: {
        'fillColor': x['properties']['color'],
        'color': 'black',
        'weight': 1,
        'fillOpacity': 0.7
    }
).add_to(m)

m.save('china_map.html')
print('已生成地图文件china_map.html')