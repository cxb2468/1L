import sys,pyperclip



passwords ={"email":"123@qq.com",
           "blog":"www.blog.com",
           "qq":"123456"

}

if len(sys.argv) <2:
    print("用法：py passwordBox.py [account] - copy account password")
    sys.exit()

account = sys.argv[1]

if account in passwords:
    pyperclip.copy(passwords[account])
    print("密码： "+account+" 已复制至剪切板。")
else:
    print("无此用户 "+account)