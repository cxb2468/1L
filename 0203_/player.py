import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from cv2 import cv2


def play_func():
    moviePath = filedialog.askopenfilename()
    pBtn.place_forget()
    movie = cv2.VideoCapture(moviePath)
    while movie.isOpened():
        ret, readyFrame = movie.read()
        if ret:
            movieFrame = cv2.cvtColor(readyFrame, cv2.COLOR_BGR2RGBA)
            newImage = Image.fromarray(movieFrame).resize((1080, 720))
            newCover = ImageTk.PhotoImage(image=newImage)
            videoLable.configure(image=newCover)
            videoLable.image = newCover
            root.update_idletasks()
            root.update()


root = tk.Tk()
root.title("Video Player")
root.geometry("1080x720")
root["bg"] = "#333333"
root.iconbitmap("./img/play.ico")

movieImage = Image.open("./img/movie.jpg")
cover = ImageTk.PhotoImage(image=movieImage)

videoLable = tk.Label(root, width=1080, height=720, bd=0, image=cover)
videoLable.place(x=0, y=0)

pImg = Image.open("./img/play.png").resize((64, 64))
pImgTk = ImageTk.PhotoImage(image=pImg)

pBtn = tk.Button(root, image=pImgTk, cursor='hand2', command=play_func)
pBtn.place(x=508, y=328)

pBar = tk.Scale(root, from_=0, to=90, length=1080, orient=tk.HORIZONTAL,
                resolution=0.1, showvalue=0, bd=0, cursor="hand2")
pBar.place(x=0, y=700)

root.mainloop()