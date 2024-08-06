from ui import Win as MainWin
from control import Controller as MainUIController
app = MainWin(MainUIController())
if __name__ == "__main__":
    app.mainloop()