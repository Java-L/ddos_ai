import os
from graphviz import Digraph

# 设置Graphviz可执行文件路径
os.environ["PATH"] += os.pathsep + r"E:\Graphviz\bin"


def plot_teacher_model():
    dot = Digraph()

    # 输入层
    dot.node('Input', 'Input Layer')

    # Inception模块
    dot.node('Conv1', 'Conv1 (1x1)')
    dot.node('Conv3_1', 'Conv3_1 (1x1)')
    dot.node('Conv3_2', 'Conv3_2 (3x3)')
    dot.node('Conv5_1', 'Conv5_1 (1x1)')
    dot.node('Conv5_2', 'Conv5_2 (5x5)')
    dot.node('MaxPool', 'MaxPool (3x3)')
    dot.node('PoolConv', 'PoolConv (1x1)')

    # 后续层
    dot.node('Conv1d', 'Conv1D (64)')
    dot.node('Pool', 'MaxPool (10)')
    dot.node('BatchNorm', 'BatchNorm (128)')
    dot.node('GRU', 'GRU (256)')
    dot.node('Attention', 'MultiHeadAttention (256)')
    dot.node('GlobalAvgPool', 'GlobalAvgPool (1D)')
    dot.node('FC', 'Fully Connected (1)')

    # 添加边
    dot.edge('Input', 'Conv1', label='Inception')
    dot.edge('Input', 'Conv3_1', label='Inception')
    dot.edge('Input', 'Conv5_1', label='Inception')
    dot.edge('Input', 'MaxPool', label='Inception')

    dot.edge('Conv3_1', 'Conv3_2', label='1x1 -> 3x3')
    dot.edge('Conv5_1', 'Conv5_2', label='1x1 -> 5x5')

    dot.edge('MaxPool', 'PoolConv', label='MaxPool -> 1x1')

    dot.edge('Conv1', 'Conv1d', label='Conv1D')
    dot.edge('Conv3_2', 'Conv1d', label='Conv1D')
    dot.edge('Conv5_2', 'Conv1d', label='Conv1D')
    dot.edge('PoolConv', 'Conv1d', label='Conv1D')

    dot.edge('Conv1d', 'Pool', label='MaxPool (10)')
    dot.edge('Pool', 'BatchNorm', label='BatchNorm')

    dot.edge('BatchNorm', 'GRU', label='GRU')
    dot.edge('GRU', 'Attention', label='Attention')

    dot.edge('Attention', 'GlobalAvgPool', label='GlobalAvgPool')
    dot.edge('GlobalAvgPool', 'FC', label='Fully Connected')

    # 输出层
    dot.edge('FC', 'Output', label='Sigmoid')

    # 渲染和显示图
    dot.render('teacher_model', format='png', view=True)


# 绘制网络模型
plot_teacher_model()
