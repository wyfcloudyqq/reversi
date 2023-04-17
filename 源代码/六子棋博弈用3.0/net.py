from keras import backend as K
from keras import models
from keras import layers
from keras import optimizers
import tensorflow as tf
import numpy as np
import copy
import os

import board

config = tf.ConfigProto()
config.gpu_options.allow_growth = True
session = tf.Session(config=config)
K.tensorflow_backend.set_session(session)


class Connect6:
    def __init__(self):
        self.board_size = (19, 19)
        self.model = None
        self.session = None
        self.graph = None

    def init(self):
        self.model = self.build_model()
        self.model._make_predict_function()
        self.session = K.get_session()
        self.graph = tf.get_default_graph()

    # 深度神经网络模型结构
    def build_model(self):
        inputs = layers.Input(shape=(self.board_size[0], self.board_size[1], 5))
        layer = layers.Conv2D(256, (1, 1), use_bias=False, padding='same', kernel_initializer='he_normal')(inputs)
        for i in range(19):
            conv_layer = layers.BatchNormalization()(layer)
            conv_layer = layers.PReLU()(conv_layer)
            conv_layer = layers.Conv2D(64, (1, 1), use_bias=False, padding='same', kernel_initializer='he_normal')(
                conv_layer)
            conv_layer = layers.BatchNormalization()(conv_layer)
            conv_layer = layers.PReLU()(conv_layer)
            conv_layer = layers.Conv2D(64, (3, 3), use_bias=False, padding='same', kernel_initializer='he_normal')(
                conv_layer)
            conv_layer = layers.BatchNormalization()(conv_layer)
            conv_layer = layers.PReLU()(conv_layer)
            conv_layer = layers.Conv2D(256, (1, 1), use_bias=False, padding='same', kernel_initializer='he_normal')(
                conv_layer)
            layer = layers.Add()([layer, conv_layer])
        layer = layers.BatchNormalization()(layer)
        layer = layers.PReLU()(layer)
        layer = layers.Conv2D(1, (1, 1), padding='same', kernel_initializer='he_normal')(layer)
        layer = layers.Flatten()(layer)
        outputs = layers.Activation('softmax')(layer)

        model = models.Model(inputs=inputs, outputs=outputs)
        model.compile(optimizer=optimizers.Adam(lr=3e-4), loss='categorical_crossentropy')
        return model

    # 模型加载
    def load(self, path):
        model_path = os.path.join(path, 'model')
        self.model.load_weights(model_path)

    # 获得要执行的动作
    def get_action(self, environment):
        # 第一步棋落在棋盘中心
        if environment.turn == 1:
            action = (self.board_size[0] // 2, self.board_size[1] // 2)
        else:
            action = self.search_action(environment)
        return action

    # 寻找下一步执行的策略 选择进攻 或 选择防守 或 就近随机处理下一步棋
    def search_action(self, environment):
        player = environment.get_player()
        opponent = environment.get_opponent()
        player_threat = environment.get_threat_count(player)
        opponent_threat = environment.get_threat_count(opponent)

        mask = None
        if player_threat > 0:
            # 进攻策略1（棋盘有胜利局面才会执行，执行即获取胜利）
            action = self.get_attack(environment)
            if action != None:
                return action
        if opponent_threat > 0:
            # 防守策略1
            mask = self.get_defense_mask(environment)
        if mask is None:
            # 进攻策略2
            mask = self.get_attack_threat_mask(environment)
        if mask.sum() == 0:
            # 防守策略2
            mask = self.get_defense_threat_mask(environment)
        # 随机策略
        if mask.sum() == 0:
            mask = self.get_basic_mask(environment)
            mask = self.get_effective(environment, mask)
        if mask.sum() == 0:
            mask = self.get_basic_mask(environment)

        # 获得19*19*5数组喂给深度神经网络
        state = environment.get_state()
        state = environment.pre_processing(state, player, environment.get_chess())
        state = np.array([state])

        # 调用神经网络进行预测，减少搜索范围。
        with self.session.as_default():
            with self.graph.as_default():
                policy = self.model.predict(state)[0]

        choice_list = np.argsort(policy)
        for choice in reversed(choice_list):
            action = (choice // self.board_size[1], choice % self.board_size[1])
            if mask[action[0]][action[1]] > 0:
                return action

    # 进攻策略1（连成自己威胁，即胜利）
    def get_attack(self, environment):
        player = environment.get_player()
        state = environment.get_state()
        threat_map = environment.get_threat_map(player)

        for y in range(environment.board_size[0]):
            for x in range(environment.board_size[1]):
                if threat_map[y][x] > 0 and state[y][x] == environment.empty:
                    action = (y, x)
                    next_environment = copy.deepcopy(environment)
                    next_environment.step(action)

                    if next_environment.check_win():
                        return action
                    if next_environment.check_done():
                        continue
                    # 第二步棋 只有成功才会有返回值。
                    if environment.get_chess() == 1:
                        continue
                    if self.get_attack(next_environment) is not None:
                        return action

        return None

    # 防守策略1（减少对手威胁数）
    def get_defense_mask(self, environment):
        opponent = environment.get_opponent()
        state = environment.get_state()
        mask = np.zeros(environment.board_size)
        threat = environment.get_threat_count(opponent)
        threat_map = environment.get_threat_map(opponent)

        for y in range(environment.board_size[0]):
            for x in range(environment.board_size[1]):
                if threat_map[y][x] > 0 and state[y][x] == environment.empty:
                    action = (y, x)
                    next_environment = copy.deepcopy(environment)
                    next_environment.step(action)
                    next_threat = next_environment.get_threat_count(opponent)

                    # 对手威胁减少（四子相连的个数减少）
                    if next_environment.check_done() or next_threat - threat < 0:
                        mask[action[0]][action[1]] = 1

        return mask

    # 进攻策略2（增加自己威胁数）
    def get_attack_threat_mask(self, environment):
        player = environment.get_player()
        state1 = environment.get_state()
        bound_map1 = environment.get_bound_map()
        mask2 = np.zeros(environment.board_size)
        mask3 = np.zeros(environment.board_size)

        for y1 in range(environment.board_size[0]):
            for x1 in range(environment.board_size[1]):
                if bound_map1[y1][x1] > 0 and state1[y1][x1] == environment.empty:
                    action1 = (y1, x1)
                    next_environment1 = copy.deepcopy(environment)
                    next_environment1.step(action1)
                    next_threat1 = next_environment1.get_threat_count(player)

                    if next_threat1 == 2:
                        mask2[action1[0]][action1[1]] = 1
                    if next_threat1 > 2:
                        mask3[action1[0]][action1[1]] = 1
                    if next_environment1.check_done():
                        continue
                    # 第二步棋
                    if environment.get_chess() == 2:
                        state2 = next_environment1.get_state()
                        bound_map2 = next_environment1.get_bound_map()
                        for y2 in range(environment.board_size[0]):
                            for x2 in range(environment.board_size[1]):
                                if (y1 * environment.board_size[0] + x1) < (y2 * environment.board_size[0] + x2):
                                    if bound_map2[y1][x1] > 0 and state2[y1][x1] == next_environment1.empty:
                                        action2 = (y2, x2)
                                        next_environment2 = copy.deepcopy(next_environment1)
                                        next_environment2.step(action2)
                                        next_threat2 = next_environment2.get_threat_count(player)
                                        if next_threat2 == 2:
                                            mask2[action2[0]][action2[1]] = 1
                                        if next_threat2 > 2:
                                            mask3[action2[0]][action2[1]] = 1
                                        if next_environment1.check_done():
                                            continue

        if mask3.sum() == 0:
            return mask2
        else:
            return mask3

    # 防守策略2（降低对手下一步的威胁数）
    def get_defense_threat_mask(self, environment):
        opponent = environment.get_opponent()
        state1 = environment.get_state()
        bound_map1 = environment.get_bound_map()
        mask = np.zeros(environment.board_size)

        for y1 in range(environment.board_size[0]):
            for x1 in range(environment.board_size[1]):
                if bound_map1[y1][x1] > 0 and state1[y1][x1] == environment.empty:
                    action1 = (y1, x1)
                    next1_environment = copy.deepcopy(environment)
                    next1_environment.samestep(action1, opponent)
                    if next1_environment.check_done():
                        continue

                    state2 = next1_environment.get_state()
                    bound_map2 = next1_environment.get_bound_map()
                    for y2 in range(environment.board_size[0]):
                        for x2 in range(environment.board_size[1]):
                            if (y1 * environment.board_size[0] + x1) < (y2 * environment.board_size[0] + x2):
                                if bound_map2[y2][x2] > 0 and state2[y2][x2] == next1_environment.empty:
                                    action2 = (y2, x2)

                                    next2_environment = copy.deepcopy(next1_environment)
                                    next2_environment.samestep(action2, opponent)

                                    next2_threat = next2_environment.get_threat_count(opponent)
                                    if next2_threat > 1:
                                        mask[action2[0]][action2[1]] += 1
                                        mask[action1[0]][action1[1]] += 1
                                    if next1_environment.check_done():
                                        continue
        t = np.max(mask)
        for y in range(environment.board_size[0]):
            for x in range(environment.board_size[1]):
                if mask[y][x] != t:
                    mask[y][x] = 0
        return mask

    # 随机处理下一步棋
    def get_basic_mask(self, environment):
        state = environment.get_state()
        mask = np.zeros(environment.board_size)
        bound_map = environment.get_bound_map()

        # bound_map 基于当前棋盘分布重新划分较小区域，进行约束，在前两种情况搜索无果的策略。
        for y in range(environment.board_size[0]):
            for x in range(environment.board_size[1]):
                if bound_map[y][x] > 0 and state[y][x] == environment.empty:
                    action = (y, x)
                    mask[action[0]][action[1]] = 1

        return mask

    def get_effective(self, environment, mask):
        state_p = environment.get_state()
        player = environment.get_player()
        opponent = environment.get_opponent()

        dx = [0, 1, 1, 1, 0, -1, -1, -1]
        dy = [1, 0, -1, 1, -1, 0, 1, -1]

        for y in range(environment.board_size[0]):
            for x in range(environment.board_size[1]):
                if state_p[y][x] == environment.empty:
                    state_p[y][x] = player

        for y in range(environment.board_size[0]):
            for x in range(environment.board_size[1]):
                if mask[y][x] > 0:
                    dir_count = 0
                    for i in range(8):
                        for j in range(1, 6):
                            check = (y + dx[i] * j, x + dy[i] * j)
                            if self.check_pos(check):
                                if state_p[check[0]][check[1]] == opponent:
                                    dir_count += 1
                                    break
                            else:
                                dir_count += 1
                                break
                    if dir_count == 8:
                        mask[y][x] = 0
        return mask

    def check_pos(self, pos):
        return pos[0] >= 0 and pos[1] >= 0 and pos[0] < self.board_size[0] and pos[1] < self.board_size[1]
