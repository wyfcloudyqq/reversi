### **黑白棋 课程设计 + AI**

[![build](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/im0qianqian/Reversi) [![release](https://img.shields.io/badge/release-v1.0-blue.svg)](https://github.com/im0qianqian/Reversi/releases) [![platform](https://img.shields.io/badge/platform-win-9cf.svg)](https://github.com/im0qianqian/Reversi/releases) [![license](https://img.shields.io/badge/license-MIT-brightgreen.svg)](https://raw.githubusercontent.com/im0qianqian/Reversi/master/LICENSE)

#### 准备
	编程语言：python
	编译环境：VS2022 + EasyX
	编译平台：Windows 10 专业版

#### 介绍
	黑白棋，又叫翻转棋（Reversi）、奥赛罗棋（Othello）、苹果棋或反棋（Anti reversi）。
	游戏通过相互翻转对方的棋子，最后以棋盘上谁的棋子多来判断胜负。
	它的游戏规则简单，因此上手很容易，但是它的变化又非常复杂。
	有一种说法是：只需要几分钟学会它，却需要一生的时间去精通它。

##### 单人模式
	玩家执黑棋
	提供简单、中等、困难AI。
	其中简单AI返回可转化棋子最大位置，
	中等以及困难AI进行极大极小博弈树搜索，返回搜索指定层数之后的最优解。

##### 双人模式
	黑棋为先，两人交替出棋    
##### 联机对战	
        通过Socket编程实现，两人必须处于同一个局域网下，一人创建，一人连接，
	连接成功后进入游戏，对弈开始，其中服务端为白棋，客户端为黑棋，黑棋为先。
##### 观战模式
	电脑 Middle 对战电脑 Difficult
##### 游戏介绍
		"五步之内，百人不当",
		"十年磨剑，一孤侠道",
		"千里挥戈，万众俯首",
		"四海江湖，百世王道",
		"每一个来到墨问的人 都会面临选择",
		"天下皆白 唯我独黑",
		"民生涂炭 奈之若何",
		"墨门绝术 克而不攻",
		"八横八纵 兼爱平生",
		"墨家主张非攻兼爱 要获得胜利",
		"并非一定要通过杀戮 攻城为下 攻心为上",
		"墨攻棋局 棋子虽然不多",
		"但是敌我双方的转化 却是千变万化 步步惊心",
##### 操作说明
		"王道之室中 不是普通的棋局",
		"而是根据本门绝学精髓设计而成的墨攻棋阵",
		"墨攻棋阵与围棋明显的不同就是",
		"墨攻棋局中不会有任何棋子被杀死",
		"当一方的棋子被另一方棋子前后围堵",
		"那这些棋子就转化成另一方",
		"当然 如果这些棋子又被围堵时",
		"还可以再次转化",
		"最后六十四格棋盘布满时就看双方谁的棋子数量多",
		"哪一方就获胜",
		"墨攻棋局 每一次落子必须要形成转换",
		"如果对方没有可被转换的棋子时",
		"这种情况 本方就只能放弃这一轮出手",
		"能够把对手逼入这种困境 就叫作破阵 是最厉害的招数",

##### 关于
		天下皆白，唯我独黑。
		民生涂炭，奈之若何。
		墨门绝术，克而不攻。
		八横八纵，兼爱平生。

##### 退出游戏
	游戏中 ESC 退出返回到上一级

#### 关于
	作者：邬云飞
	版本：v1.0
	说明：游戏中部分界面可按ESC退出，使用过程中如若发现Bug，请不要忘记在这里留言哦！
	网站：https://www.dreamwings.cn/

##### 已知Bug：


##### 已修复Bug：


#### 链接：[黑白棋中的AI](https://www.dreamwings.cn/reversi/3013.html)

















# Reversi

## 摘要：
计算机博弈是人工智能的重要分支之一，是一种对策性游戏,是人工智能的主要研究领域之一,它涉及人工智能中的搜索方法、推理技术和决策规划等。目前广泛研究的是确定的、二人、零和、完备信息的
博弈搜索。文中通过对黑白棋程序进行系统的设计,将生成的博弈树节点的估值过程和对博弈树搜索过程相结合,采用传统的Alpha-Beta剪枝和max-min原则方法给出了博弈程序设计的核心内容:包括博弈树
搜索和估值函数两个方面,提出对原算法的一种改进。通过对棋盘的数据结构的设计和基于模板匹配的局面评估方法,最大程度地提高下棋的效率和AI。

## 关键词：
博弈树；黑白棋；估值函数；

## Absrtact：
Computer game is one of the important branches of artificial intelligence, is a kind of countermeasure game, is one of the main research fields of artificial intelligence,
it involves search methods, reasoning technology and decision planning in artificial intelligence. At present, the game search of deterministic, two-person, zero-sum, and
complete information is widely studied. In this paper, through the systematic design of the reversi program, the valuation process of the generated game tree node and the game 
tree search process are combined, and the traditional Alpha-Beta pruning and max-min principle methods are used to give the core content of game program design: including game 
tree search and valuation function, and an improvement of the original algorithm is proposed. Through the design of the data structure of the chessboard and the situation 
evaluation method based on template matching, the efficiency and AI of chess play are maximized.
    
## Keyword:
Game Tree Reversi; valuation; function; 

## 参考文献
[1]彭之军.计算机博弈算法在黑白棋中的应用[J].现代信息科技,2021,5(17):73-77+81.<br>
[2]刘佳瑶,林涛.黑白棋博弈系统设计[J].智能计算机与应用,2020,10(05):176-179+182.<br>
[3]汪源,黄文敏.智能黑白棋机器人设计[J].电子世界,2017(20):123-124.<br>
[4]黄海同.黑白棋AI设计探究[J].电脑知识与技术,2016,12(29):198-200.<br>
[5]李小舟. 基于改进博弈树的黑白棋设计与实现[D].华南理工大学,2010.<br>
[6]小杨猫猫.攻防黑白棋[J].数学大王(超级脑力),2023(Z1):28-31.<br>


## 软件架构说明
## 安装教程
### 安装环境
xxxx
xxxx
## 使用说明
xxxx
xxxx
xxxx
## 参与贡献
Fork 本仓库
新建 Feat_xxx 分支
提交代码
新建 Pull Request
