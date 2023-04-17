from tkinter import *
from tkinter import messagebox
import net
import board
import datetime


class Move:
    NONE = 0
    black = 1
    white = 2
    EDGE = 19

    def __init__(self, player=NONE, x1=-1, y1=-1, x2=-1, y2=-1):
        self.player = player
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def __str__(self):
        return 'player: {0}, x1: {1}, y1: {2}, x2: {3}, y2: {4}'.format(self.player, self.x1, self.y1, self.x2, self.y2)

    # def invalidate(self):
    #     self.player = None
    #     self.x1 = -1
    #     self.y1 = -1
    #     self.x2 = -1
    #     self.y2 = -1

    def isValidated(self):
        if self.player != Move.black and self.player != Move.white:
            return False
        if Move.isValidPosition(self.x1, self.y1) and Move.isValidPosition(self.x2, self.y2):
            return True
        return False

    def isValidPosition(x, y):
        if x >= 0 and x < Move.EDGE and y >= 0 and y < Move.EDGE:
            return True
        return False


class GameState:
    Idle = 0
    AI2Human = 1
    Human2Human = 2

    WaitForHumanFirst = 1
    WaitForHumanSecond = 2

    Win = 3


class App(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master, width=640, height=700)
        self.pack()
        self.gameMode = GameState.Idle
        self.gameState = GameState.Idle
        self.agent = net.Connect6()
        self.environment = board.Connect6()
        self.save_path = 'save'
        self.initResource()
        self.createBoard()
        self.initBoard()

        self.a_time = 0
        self.l_time = 0
        self.b_time = 0
        self.e_time = 0

    def destroy(self):
        Frame.destroy(self)

    def initResource(self):

        # 加载图片
        self.images = {}
        im = self.images
        im['go_u'] = PhotoImage(file='imgs/go_u.gif')
        im['go_ul'] = PhotoImage(file='imgs/go_ul.gif')
        im['go_ur'] = PhotoImage(file='imgs/go_ur.gif')
        im['go'] = PhotoImage(file='imgs/go.gif')
        im['go_l'] = PhotoImage(file='imgs/go_l.gif')
        im['go_r'] = PhotoImage(file='imgs/go_r.gif')
        im['go_d'] = PhotoImage(file='imgs/go_d.gif')
        im['go_dl'] = PhotoImage(file='imgs/go_dl.gif')
        im['go_dr'] = PhotoImage(file='imgs/go_dr.gif')
        im['go_-'] = PhotoImage(file='imgs/go_-.gif')
        im['go_b'] = PhotoImage(file='imgs/go_b.gif')
        im['go_w'] = PhotoImage(file='imgs/go_w.gif')
        im['go_bt'] = PhotoImage(file='imgs/go_bt.gif')
        im['go_wt'] = PhotoImage(file='imgs/go_wt.gif')

        # 画布
        self.canvas = Canvas(self, width=640, height=640)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=1)
        # 按钮布局
        self.controlFrame = LabelFrame(self)
        self.controlFrame.pack(fill=BOTH, expand=1)
        # 黑棋选择
        self.controlFrame.selectblack = labelframe = LabelFrame(self.controlFrame, text='黑棋选手')
        labelframe.pack(fill=X, expand=1)
        labelframe.blackImg = Label(labelframe, image=self.images['go_b'])
        labelframe.blackImg.pack(side=LEFT, anchor=W)
        self.blackSelected = StringVar()
        labelframe.humanRBtn = Radiobutton(labelframe, text="人类", variable=self.blackSelected, value=' ')
        labelframe.humanRBtn.select()
        labelframe.humanRBtn.pack(anchor=W)
        labelframe.engineRBtn = Radiobutton(labelframe, text="AI", variable=self.blackSelected, value='AI')
        labelframe.engineRBtn.pack(anchor=W)
        # 白棋选择
        self.controlFrame.selectwhite = labelframe = LabelFrame(self.controlFrame, text='白棋选手')
        labelframe.pack(fill=X, expand=1)
        labelframe.whiteImg = Label(labelframe, image=self.images['go_w'])
        labelframe.whiteImg.pack(side=LEFT, anchor=W)
        self.whiteSelected = StringVar()
        labelframe.humanRBtn = Radiobutton(labelframe, text="人类", variable=self.whiteSelected, value=' ')
        labelframe.humanRBtn.select()
        labelframe.humanRBtn.pack(anchor=W)
        labelframe.engineRBtn = Radiobutton(labelframe, text="AI", variable=self.whiteSelected, value='AI')
        labelframe.engineRBtn.pack(anchor=W)
        # 时间显示
        self.controlFrame.distime = labelframe = LabelFrame(self.controlFrame, text='时间显示')
        labelframe.pack(fill=X, expand=1)
        labelframe.timelabel1 = Label(labelframe, text='总共用时：')
        labelframe.timelabel1.pack(side=TOP, fill=X)
        labelframe.alltime = Label(labelframe, text='0.000000')
        labelframe.alltime.pack(fill=X)
        labelframe.timelabel2 = Label(labelframe, text='上步用时:')
        labelframe.timelabel2.pack(fill=X)
        labelframe.lasttime = Label(labelframe, text='0.000000')
        labelframe.lasttime.pack(fill=X)
        # 游戏菜单
        self.controlFrame.gameContral = labelframe = LabelFrame(self.controlFrame, text='游戏菜单')
        labelframe.pack(fill=X, expand=1)
        labelframe.newBtn = Button(labelframe, text='开始游戏', command=self.newGame)
        labelframe.newBtn.pack(side=TOP, fill=X)
        labelframe.quitBtn = Button(labelframe, text='退出游戏', command=self.master.destroy)
        labelframe.quitBtn.pack(fill=X)

    # 创建棋盘单元格
    def createBoardUnit(self, x, y, imageKey):
        lb = Label(self.canvas, height=32, width=32)
        lb.x = x
        lb.y = y
        lb['image'] = self.images[imageKey]
        lb.initImage = self.images[imageKey]
        lb.bind('<Button-1>', self.onClickBoard)
        self.gameBoard[x][y] = lb
        return lb

    # 创建完整棋盘
    def createBoard(self):
        self.gameBoard = [[0 for i in range(Move.EDGE)] for i in range(Move.EDGE)]
        self.moveList = []
        gameBoard = self.gameBoard
        # 顶部棋盘构建
        self.createBoardUnit(0, 0, 'go_ul')
        for j in range(1, 18):
            self.createBoardUnit(0, j, 'go_u')
        self.createBoardUnit(0, 18, 'go_ur')
        # 中部棋盘构建
        for i in range(1, 18):
            gameBoard[i][0] = self.createBoardUnit(i, 0, 'go_l')
            for j in range(1, 18):
                gameBoard[i][j] = self.createBoardUnit(i, j, 'go')

            gameBoard[i][18] = self.createBoardUnit(i, 18, 'go_r')
        # 9个棋盘中心点
        self.createBoardUnit(3, 3, 'go_-')
        self.createBoardUnit(3, 9, 'go_-')
        self.createBoardUnit(3, 15, 'go_-')
        self.createBoardUnit(9, 3, 'go_-')
        self.createBoardUnit(9, 9, 'go_-')
        self.createBoardUnit(9, 15, 'go_-')
        self.createBoardUnit(15, 3, 'go_-')
        self.createBoardUnit(15, 9, 'go_-')
        self.createBoardUnit(15, 15, 'go_-')
        # 低部棋盘构建
        self.createBoardUnit(18, 0, 'go_dl')
        for j in range(1, 18):
            self.createBoardUnit(18, j, 'go_d')
        self.createBoardUnit(18, 18, 'go_dr')

    # 初始化棋盘
    def initBoard(self):
        self.moveList = []
        for i in range(Move.EDGE):
            for j in range(Move.EDGE):
                self.unplaceplayer(i, j)

    def unplaceplayer(self, i, j):
        gameBoard = self.gameBoard
        gameBoard[i][j]['image'] = gameBoard[i][j].initImage
        gameBoard[i][j].player = 0
        gameBoard[i][j].grid(row=i, column=j)

    # 判定某个方向是否有6子相连
    def connectedByDirection(self, x, y, dx, dy):
        gameBoard = self.gameBoard
        cnt = 1
        xx = dx
        yy = dy
        while Move.isValidPosition(x + xx, y + yy) and gameBoard[x][y].player == gameBoard[x + xx][y + yy].player:
            xx += dx
            yy += dy
            cnt += 1
        xx = -dx
        yy = -dy
        while Move.isValidPosition(x + xx, y + yy) and gameBoard[x][y].player == gameBoard[x + xx][y + yy].player:
            xx -= dx
            yy -= dy
            cnt += 1
        if cnt >= 6:
            return True
        return False

    def connectedBy(self, x, y):
        # 四个方向
        if self.connectedByDirection(x, y, 1, 1):
            return True
        if self.connectedByDirection(x, y, 1, -1):
            return True
        if self.connectedByDirection(x, y, 1, 0):
            return True
        if self.connectedByDirection(x, y, 0, 1):
            return True
        return False

    # 输赢判定
    def isWin(self, move):
        if move.isValidated():
            # 对刚下的两步棋的周边进行搜索
            return self.connectedBy(move.x1, move.y1) or self.connectedBy(move.x2, move.y2)
        return False

    def nextplayer(self):
        player = Move.black
        if len(self.moveList) % 2 == 1:
            player = Move.white
        return player

    def newGame(self):
        self.initBoard()
        self.a_time = 0
        self.l_time = 0
        self.b_time = 0
        self.e_time = 0
        black = self.blackSelected.get().strip()
        white = self.whiteSelected.get().strip()
        # ''表示人类选手
        if black == '' and white == '':
            self.toGameMode(GameState.Human2Human)
            self.toGameState(GameState.WaitForHumanFirst)
        elif black != '' and white != '':
            messagebox.showinfo("六子棋", "AI VS AI 功能尚未完善，请重新选择！")
        else:
            self.agent.init()
            self.agent.load(self.save_path)
            self.toGameMode(GameState.AI2Human)
            self.environment.reset()
            if black != '':

                self.b_time = datetime.datetime.now()

                action = self.agent.get_action(self.environment)
                player = self.nextplayer()
                self.move = Move(player, action[0], action[1], action[0], action[1])
                self.addToMoveList(self.move)
                self.placeStone(self.move.player, action[0], action[1])
                self.environment.step(action)
                self.toGameState(GameState.WaitForHumanFirst)

                self.e_time = datetime.datetime.now()
                self.l_time = self.e_time - self.b_time
                self.a_time += self.l_time.total_seconds()

                msg = self.a_time;
                self.controlFrame.distime.alltime['text'] = msg;
                msg = self.l_time.total_seconds();
                self.controlFrame.distime.lasttime['text'] = msg;

            else:
                self.toGameState(GameState.WaitForHumanFirst)

    def addToMoveList(self, move):
        n = len(self.moveList)
        if n > 0:
            m = self.moveList[n - 1]
            self.placeplayer(m.player, m.x1, m.y1)
            self.placeplayer(m.player, m.x2, m.y2)
        self.moveList.append(move)

    def makeMove(self, move):
        if move.isValidated():
            self.placeStone(move.player, move.x1, move.y1)
            self.placeStone(move.player, move.x2, move.y2)
            self.addToMoveList(move)
        return move

    def placeStone(self, player, x, y):
        self.placeplayer(player, x, y, 't')
        if self.connectedBy(x, y):
            self.winner = player
            self.toGameState(GameState.Win)
            if player == Move.black:
                messagebox.showinfo("六子棋", "黑棋胜利！！！")

            else:
                messagebox.showinfo("六子棋", "白棋胜利！！！")

    def placeplayer(self, player, x, y, extra=''):
        if player == Move.black:
            imageKey = 'go_b'
        elif player == Move.white:
            imageKey = 'go_w'
        else:
            return
        imageKey += extra
        self.gameBoard[x][y].player = player
        self.gameBoard[x][y]['image'] = self.images[imageKey]
        self.gameBoard[x][y].grid(row=x, column=y)

    def toGameMode(self, mode):
        self.gameMode = mode

    def toGameState(self, state):
        self.gameState = state

    def onClickBoard(self, event):
        x = event.widget.x
        y = event.widget.y
        self.l_time = 0
        self.b_time = 0
        self.e_time = 0
        if not self.gameBoard[x][y].player == Move.NONE:
            return
        if self.gameMode == GameState.Human2Human:
            player = self.nextplayer()
            if len(self.moveList) == 0:
                self.move = Move(player, x, y, x, y)
                self.placeStone(self.move.player, x, y)
                self.addToMoveList(self.move)
                self.toGameState(GameState.WaitForHumanFirst)

            elif self.gameState == GameState.WaitForHumanFirst:
                self.move = Move(player, x, y)
                self.placeStone(self.move.player, x, y)
                if self.gameState == GameState.WaitForHumanFirst:
                    self.toGameState(GameState.WaitForHumanSecond)

            elif self.gameState == GameState.WaitForHumanSecond:
                self.move.x2 = x
                self.move.y2 = y
                self.placeStone(self.move.player, x, y)
                self.addToMoveList(self.move)
                if self.gameState == GameState.WaitForHumanSecond:
                    self.toGameState(GameState.WaitForHumanFirst)

            return

        if self.gameMode == GameState.AI2Human:
            player = self.nextplayer()

            if len(self.moveList) == 0:
                self.move = Move(player, x, y, x, y)
                self.placeStone(self.move.player, x, y)
                self.addToMoveList(self.move)
                self.environment.step((x, y))
                self.toGameState(GameState.WaitForHumanFirst)

                player = self.nextplayer()
                # 开始计时
                self.b_time = datetime.datetime.now()

                action = self.agent.get_action(self.environment)
                self.move = Move(player, action[0], action[1])
                self.placeStone(self.move.player, action[0], action[1])
                self.environment.step(action)

                action = self.agent.get_action(self.environment)
                self.move.x2 = action[0]
                self.move.y2 = action[1]
                self.addToMoveList(self.move)
                self.placeStone(self.move.player, action[0], action[1])
                self.environment.step(action)

                # 结束计时
                self.e_time = datetime.datetime.now()
                self.l_time = self.e_time - self.b_time
                self.a_time += self.l_time.total_seconds()
                msg = self.a_time;
                self.controlFrame.distime.alltime['text'] = msg;
                msg = self.l_time.total_seconds();
                self.controlFrame.distime.lasttime['text'] = msg;

                return

            if self.gameState == GameState.WaitForHumanFirst:
                self.move = Move(player, x, y)
                self.placeStone(self.move.player, x, y)
                self.environment.step((x, y))
                if self.gameState == GameState.WaitForHumanFirst:
                    self.toGameState(GameState.WaitForHumanSecond)

            elif self.gameState == GameState.WaitForHumanSecond:
                self.move.x2 = x
                self.move.y2 = y
                self.placeStone(self.move.player, x, y)
                self.addToMoveList(self.move)
                self.environment.step((x, y))
                if self.gameState == GameState.WaitForHumanSecond:
                    self.toGameState(GameState.WaitForHumanFirst)

                player = self.nextplayer()
                # 开始计时
                self.b_time = datetime.datetime.now()

                action = self.agent.get_action(self.environment)
                self.move = Move(player, action[0], action[1])
                self.placeStone(self.move.player, action[0], action[1])
                self.environment.step(action)

                action = self.agent.get_action(self.environment)
                self.move.x2 = action[0]
                self.move.y2 = action[1]
                self.addToMoveList(self.move)
                self.placeStone(self.move.player, action[0], action[1])
                self.environment.step(action)

                # 结束计时
                self.e_time = datetime.datetime.now()
                self.l_time = self.e_time - self.b_time
                self.a_time += self.l_time.total_seconds()
                msg = self.a_time;
                self.controlFrame.distime.alltime['text'] = msg;
                msg = self.l_time.total_seconds();
                self.controlFrame.distime.lasttime['text'] = msg;

        return


def main():
    root = Tk()
    app = App(root)
    app.master.title('六子棋')
    app.mainloop()


if __name__ == '__main__':
    main()
