import torch
import torch.nn as nn
import numpy as np

class ThreeD_Net(nn.Module):
    conv_midden_dim = [8, 16]
    fc_midden_dim = [64, ]
    def __init__(self, input_channel, state_dim, bias = True, dropout = 0.1):
        super(ThreeD_Net, self).__init__()

        self.conv1 = nn.Conv3d(in_channels=input_channel, out_channels=self.conv_midden_dim[0], kernel_size=3, 
                                stride=(2, 2, 2), padding=(3, 3, 3), bias=bias)
        self.bn1 = nn.BatchNorm3d(self.conv_midden_dim[0])
        self.relu = nn.ReLU(inplace=True)

        self.conv2 = nn.Conv3d(in_channels=self.conv_midden_dim[0], out_channels=self.conv_midden_dim[1], kernel_size=1, 
                                stride=(2, 2, 2), bias=bias)
        self.bn2 = nn.BatchNorm3d(self.conv_midden_dim[1])

        self.avgpool = nn.AdaptiveAvgPool3d((1, 1, 1))

        self.fc1 = nn.Linear(in_features=state_dim, out_features=self.fc_midden_dim[-1], bias=bias)

        self.fc2 = nn.Linear(in_features=self.fc_midden_dim[-1] + self.conv_midden_dim[1], out_features=self.fc_midden_dim[-1], bias=bias)
        self.fc3 = nn.Linear(in_features=self.fc_midden_dim[-1], out_features=1, bias=bias)
        
        self.dropout = nn.Dropout(dropout)

        self.init_weights()

    def init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv3d):
                nn.init.kaiming_normal_(m.weight,
                                        mode='fan_out',
                                        nonlinearity='relu')
            elif isinstance(m, nn.BatchNorm3d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                nn.init.constant_(m.bias, 0)

    def forward(self, x, state):
        bs = x.shape[0]
        out = self.conv1(x)
        out = self.dropout(self.bn1(out))
        out = self.relu(out)

        out = self.conv2(out)
        out = self.dropout(self.bn2(out))
        out = self.relu(out)
        out = self.avgpool(out).view(bs, self.conv_midden_dim[1])
        
        state = self.fc1(state)
        state = self.dropout(state)
        state = self.relu(state)

        
        out = torch.concat([out, state], dim=-1)
        out = self.relu(out)

        out = self.fc2(out)
        out = self.relu(out)

        out = self.fc3(out)
        
        return out
    

class DeepQNetwork(nn.Module):
    def __init__(self):
        super(DeepQNetwork, self).__init__()

        self.conv1 = nn.Sequential(nn.Linear(5, 64), nn.ReLU(inplace=True))
        self.conv2 = nn.Sequential(nn.Linear(64, 64), nn.ReLU(inplace=True))
        self.conv3 = nn.Sequential(nn.Linear(64, 1))

        self._create_weights()

    def _create_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                nn.init.constant_(m.bias, 0)

    def forward(self, x):
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.conv3(x)

        return x


class DeepQNetwork_Two(nn.Module):
    def __init__(self, input_dim):
        super(DeepQNetwork_Two, self).__init__()
        
        self.conv1 = nn.Sequential(nn.Linear(input_dim, 512), nn.ReLU(inplace=True))
        self.conv2 = nn.Sequential(nn.Linear(512, 512), nn.ELU(inplace=True))
        self.conv3 = nn.Sequential(nn.Linear(512, 64), nn.ELU(inplace=True))
        self.conv4 = nn.Sequential(nn.Linear(64, 1))

        self._create_weights()

    def _create_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                nn.init.constant_(m.bias, 0)

    def forward(self, x):
        bs = x.shape[0]
        x = x.view(bs, -1)
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.conv3(x)
        x = self.conv4(x)
        return x

def is_Done(state, cargo):
    '''
    在三维平面暴力搜索可以放置的位置。
    
    Args:
        state:货车车厢状态,0代表空,1代表已经放置其它货物,numpy数组。
        cargo:货物信息，长宽高，字典。
        
    Returns:
        返回元组，(装好当前货物之后的状态，货物坐标，是否能放)。
    '''
    l, w, h = state.shape
    cargo_l, cargo_w, cargo_h = cargo['length'], cargo['width'], cargo['height']
    
    for i in range(1, l+1-cargo_l):
        for j in range(1, w+1-cargo_w):
            for k in range(1, h+1-cargo_h):
                if state[i:i+cargo_l, j:j+cargo_w, k:k+cargo_h].sum()==0:
                    state[i:i+cargo_l, j:j+cargo_w, k:k+cargo_h] = 1
                    return state, (i, j, k), False
    
    return state, (-1,-1,-1), True

def match_trucks_with_cargos(trucks, cargos):
    """
    匹配货车和货物的函数。

    Args:
        trucks: 货车列表，每个元素是一个字典，包含货车的长宽高和载重信息。
        cargos: 货物列表，每个元素是一个字典，包含货物的长宽高和重量信息。

    Returns:
        匹配结果，返回一个列表，每个元素是一个字典，表示匹配到的货车和货物的信息，包含货车的索引、货物的索引和数量信息。
    """
    # 构建动态规划的二维表格
    # dp[i][j] 表示考虑前 i 个货车和前 j 个货物，能够装载的最大重量
    dp = np.zeros(shape=(len(trucks) + 1, len(cargos) + 1))
    cargoLocations = np.zeros(shape=(len(trucks) + 1, len(cargos) + 1, 3))
    truckStates = [np.zeros(shape=(truck['length'], truck['width'], truck['height'])) for truck in trucks]
    

    # 逐个考虑每个货车和货物
    for i in range(1, len(trucks) + 1):
        for j in range(1, len(cargos) + 1):
            # 如果当前货车能够装载当前货物，则需要比较选和不选两种情况
            state, coordinate, Done = is_Done(truckStates[i-1], cargos[j-1])
            if ( not Done and
                trucks[i - 1]['load_capacity'] >= cargos[j - 1]['weight']):
                # 如果选当前货物，则装载重量增加 cargos[j-1]['weight']
                dp[i][j] = max(dp[i][j-1] + cargos[j-1]['weight'], dp[i][j-1])
                cargoLocations[i][j] = coordinate
            else:
                # 如果不选当前货物，则只能选择前面的货物
                dp[i][j] = dp[i][j-1]
       
    # 回溯得到匹配结果
    matchResults = []
    for i in range(1, len(trucks) + 1):
        buf = []
        for j in range(1, len(cargos) + 1):
            if cargoLocations[i][j][0]!=-1:
                buf.append((cargoLocations[i][j][0], cargoLocations[i][j][1], cargoLocations[i][j][2], j))
        buf.append(dp[i][-1]/trucks[i-1]['load_capacity'])
        matchResults.append(buf)

    return matchResults


