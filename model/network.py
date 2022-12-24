import torch
import torch.nn as nn

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
