import numpy as np


class Connect6:
    # 棋盘初始化
    def __init__(self):
        self.board_size = (19, 19)
        self.board = np.zeros(self.board_size)
        self.empty = 0
        self.black = 1
        self.white = 2
        self.connect = 6
        self.turn = 1
        self.win = False
        self.done = False

        # 为了基于棋盘上已有棋盘，重新计算一个边界棋盘，约束神经网络计算结果
        self.chess_bound = 3
        self.chess_bound_map = np.zeros((self.board_size[0], self.board_size[1]))
        # 威胁数和威胁棋谱
        self.black_threat_count = 0
        self.black_threat_map = np.zeros((self.board_size[0], self.board_size[1]))
        self.white_threat_count = 0
        self.white_threat_map = np.zeros((self.board_size[0], self.board_size[1]))

        # 遍历使用的四个方向
        self.dx = [0, 1, 1, 1]
        self.dy = [1, 0, -1, 1]

    def reset(self):
        self.__init__()

    # 在棋盘落子，同时更新 win bound threat
    def step(self, pos):
        if self.check_pos(pos) and self.board[pos[0]][pos[1]] == self.empty:
            self.board[pos[0]][pos[1]] = self.get_player()
        else:
            raise IndexError()
        self.update_win(pos)
        self.update_bound(pos)
        self.update_threat(pos)
        self.turn += 1
        # print(pos)
        # print("黑棋")
        # print(self.black_threat_count)
        # print("白棋")
        # print(self.white_threat_count)
        # print("——————————————————————————————")

    # 在棋盘落子，同时更新 win bound threat(威胁防守策略)
    def samestep(self, pos, player):
        self.board[pos[0]][pos[1]] = player
        self.update_win(pos)
        self.update_bound(pos)
        self.update_threat(pos)
        self.turn += 1
        # print(pos)
        # print("黑棋")
        # print(self.black_threat_count)
        # print("白棋")
        # print(self.white_threat_count)
        # print("——————————————————————————————")

    # 根据现有棋盘状态计算喂给神经网络的19*19*5的数组分别为
    # 我方棋盘，对手棋盘和3个全为0或全为1的棋盘（用于区分第一手棋和第二手棋）
    def pre_processing(self, state, player, chess):
        if player == self.black:
            state1 = (state == self.black).astype(int)[:, :, np.newaxis]
            state2 = (state == self.white).astype(int)[:, :, np.newaxis]
        else:
            state1 = (state == self.white).astype(int)[:, :, np.newaxis]
            state2 = (state == self.black).astype(int)[:, :, np.newaxis]
        if chess == 2:
            state3 = np.ones(self.board_size)[:, :, np.newaxis]
            state4 = np.zeros(self.board_size)[:, :, np.newaxis]
        else:
            state3 = np.zeros(self.board_size)[:, :, np.newaxis]
            state4 = np.ones(self.board_size)[:, :, np.newaxis]
        state5 = np.ones(self.board_size)[:, :, np.newaxis]

        # 五个棋盘归一为一个19*19*5的数组
        prep_state = np.concatenate((state1, state2, state3, state4, state5), axis=-1)
        return prep_state

    def check_pos(self, pos):
        return pos[0] >= 0 and pos[1] >= 0 and pos[0] < self.board_size[0] and pos[1] < self.board_size[1]

    def check_win(self):
        return self.win

    def check_done(self):
        return self.win or self.turn >= self.board_size[0] * self.board_size[1]

    # 获取当前棋手
    def get_player(self):
        if (self.turn // 2) % 2 == 0:
            return self.black
        else:
            return self.white

    # 获得对手
    def get_opponent(self):
        player = self.get_player()
        if player == self.black:
            return self.white
        elif player == self.white:
            return self.black

    # 第一手棋or第二手棋
    def get_chess(self):
        if self.turn % 2 == 0:
            return 2
        else:
            return 1

    def get_state(self):
        return np.array(self.board)

    def get_bound_map(self):
        return np.array(self.chess_bound_map)

    def get_threat_count(self, player):
        if player == self.black:
            return self.black_threat_count
        elif player == self.white:
            return self.white_threat_count

    def get_threat_map(self, player):
        if player == self.black:
            return np.array(self.black_threat_map)
        elif player == self.white:
            return np.array(self.white_threat_map)

    # 在八个方向上进行搜索可下棋的点
    def update_win(self, pos):
        player = self.get_player()
        board = self.get_state()

        for i in range(4):
            count = 0
            for j in range(-self.connect + 1, self.connect):
                target = [pos[0] + self.dy[i] * j, pos[1] + self.dx[i] * j]

                if self.check_pos(target):
                    if board[target[0]][target[1]] == player:
                        count += 1
                    else:
                        count = 0
                else:
                    count = 0

                if count >= self.connect:
                    self.win = True

    # 更新落子棋盘边界，基于棋盘已有棋子的周围3格。
    def update_bound(self, pos):
        for i in range(4):
            for j in range(-self.chess_bound, self.chess_bound + 1):
                target = [pos[0] + self.dy[i] * j, pos[1] + self.dx[i] * j]

                if self.check_pos(target):
                    self.chess_bound_map[target[0]][target[1]] = 1

    # 更新黑白棋子的威胁数和威胁棋谱
    def update_threat(self, pos):
        player = self.get_player()
        board = self.get_state()

        black_threat_count_delta = 0
        black_threat_map_delta = np.zeros((board.shape[0], board.shape[1]))
        white_threat_count_delta = 0
        white_threat_map_delta = np.zeros((board.shape[0], board.shape[1]))

        board[pos[0]][pos[1]] = self.empty
        black_threat_count, black_threat_map = self.get_threat_line(board, pos, self.black)
        black_threat_count_delta -= black_threat_count
        black_threat_map_delta = np.subtract(black_threat_map_delta, black_threat_map)
        white_threat_count, white_threat_map = self.get_threat_line(board, pos, self.white)
        white_threat_count_delta -= white_threat_count
        white_threat_map_delta = np.subtract(white_threat_map_delta, white_threat_map)

        board[pos[0]][pos[1]] = player
        black_threat_count, black_threat_map = self.get_threat_line(board, pos, self.black)
        black_threat_count_delta += black_threat_count
        black_threat_map_delta = np.add(black_threat_map_delta, black_threat_map)
        white_threat_count, white_threat_map = self.get_threat_line(board, pos, self.white)
        white_threat_count_delta += white_threat_count
        white_threat_map_delta = np.add(white_threat_map_delta, white_threat_map)

        self.black_threat_count += black_threat_count_delta
        self.black_threat_map = np.add(self.black_threat_map, black_threat_map_delta)
        self.white_threat_count += white_threat_count_delta
        self.white_threat_map = np.add(self.white_threat_map, white_threat_map_delta)

    # 计算棋盘的威胁数和威胁棋谱（连续的六个棋格内，无对手棋子且有4个或者5个我方棋子，此时计为威胁。）
    def get_threat_line(self, board, pos, player):
        threat_count = 0
        threat_map = np.zeros((self.board_size[0], self.board_size[1]))

        if player == self.black:
            op_player = self.white
        else:
            op_player = self.black

        for i in range(4):
            target = [pos[0], pos[1]]
            # 将target移动至四个方向的边缘。
            while self.check_pos(target):
                target[0] -= self.dy[i]
                target[1] -= self.dx[i]

            player_list = []
            empty_list = []
            # 将target反方向移动实现对落子的8个方向的遍历。
            while True:
                target[0] += self.dy[i]
                target[1] += self.dx[i]
                if not self.check_pos(target):
                    break

                while len(player_list) != 0:
                    distance = max([abs(target[0] - player_list[0][0]), abs(target[1] - player_list[0][1])])
                    if distance < self.connect:
                        break
                    player_list.pop(0)
                while len(empty_list) != 0:
                    distance = max([abs(target[0] - empty_list[0][0]), abs(target[1] - empty_list[0][1])])
                    if distance < self.connect:
                        break
                    empty_list.pop(0)

                if board[target[0]][target[1]] == self.empty:
                    empty_list.append([target[0], target[1]])
                elif board[target[0]][target[1]] == player:
                    player_list.append([target[0], target[1]])
                # 遇到对方棋子直接重新开始。
                elif board[target[0]][target[1]] == op_player:
                    player_list = []
                    empty_list = []

                if len(player_list) >= self.connect - 2 and len(empty_list) == self.connect - len(player_list):
                    if len(empty_list) == 0:
                        continue

                    threat_count += 1
                    for j in range(self.connect):
                        threat_map[target[0] - self.dy[i] * j][target[1] - self.dx[i] * j] += 1

                    target = [empty_list[-1][0], empty_list[-1][1]]
                    player_list = []
                    empty_list = []

        return threat_count, threat_map
