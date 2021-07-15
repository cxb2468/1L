# 1L
python 学习之旅

问：【Git】pull遇到错误：error: Your local changes to the following files would be overwritten by merge:
答：别急我们有如下三部曲
	打开Git Bash  cd至目标.git目录中，输入如下3行命令：
    git stash  
    git pull origin master  
    git stash pop  


