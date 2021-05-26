import requests
import pygal
from pygal.style import LightColorizedStyle as LCS,LightenStyle as LS




#执行API调用 并存储响应
url ='https://api.github.com/search/repositories?q=language:python&sort=stars'
r = requests.get(url)
print("Code: ",r.status_code)


#将API响应存储在一个变量中
responseDict = r.json()

#处理结果
print(responseDict.keys())

#key： item的信息
repos =responseDict['items']
print("Repos: ",len(repos))

#研究第一个位置的item
repo1 =repos[0]
print('\nkeys: ',len(repo1))

for k,v in sorted(repo1.items()):
    print(k)



names = []
stars = []
plots = []


for repo in repos:
    names.append(repo['name'])
    # stars.append(repo['stargazers_count'])

    plot = {'value' : repo['stargazers_count'],'lable' : repo['description'],'xlink' : repo['html_url']}
    plots.append(plot)



 #可视化
my_style =LS('#333366',base_style=LCS)

myConfig = pygal.Config()
myConfig.x_label_rotation = 45
myConfig.show_legend = False
myConfig.title_font_size = 24
myConfig.lable_font_size = 14
myConfig.major_lable_font_size = 18
myConfig.truncate_label = 15
myConfig.show_y_guides = False
myConfig.width = 1200


chart = pygal.Bar(myConfig,style = my_style)
# chart = pygal.Bar(style = my_style,x_label_rotation = 45,show_Legend=False)
chart.title = 'Most Star'
chart.x_labels = names

chart.add('',plots)
chart.render_to_file('python_repos_python.svg')