import numpy as np
import torch
import torch.nn as nn
import torch.functional as f
import torch.optim as optim
import detect_face
#import dnmf
#import gabor
from torch.utils.data import Dataset, DataLoader
import os
import random

# expressions = {'N': [1, 0, 0, 0, 0],
#                'A': [0, 1, 0, 0, 0],
#                'F': [0, 0, 1, 0, 0],
#                'C': [0, 0, 0, 1, 0], #HC
#                'O': [0, 0, 0, 0, 1] #HO
#                }

expressions = {'N': 0,
               'A': 1,
               'F': 2,
               'C': 3, #HC
               'O': 4 #HO
               }


gabor_data = []
gabor_labels = []
path = os.getcwd() + '/gabor_output_2/gabors'
folders = os.listdir(path)
print(folders)
for fold in folders:
    temp_path = path + '/' + str(fold)
    files = os.listdir(temp_path)

    for file in files:

        if str(file)[-3:] == 'txt':
            text = open(temp_path + '/' + str(file))
            lst = text.read().splitlines()
            data_tens = [int(i) for i in lst]
            label = expressions[str(file)[-5]]
            gabor_data.append(data_tens)
            gabor_labels.append(label)

print(len(gabor_data))

class GaborData(Dataset):

    def __init__(self, data, labels):
        self.data = data
        self.labels = labels

    def __getitem__(self, index):
        dat = torch.tensor(self.data[index]).float()
        lab = torch.tensor(self.labels[index])

        return (dat, lab)

    def __len__(self):
        return len(self.data)

dataset = GaborData(gabor_data, gabor_labels)
train_set, test_set = torch.utils.data.random_split(dataset, [1200, 95]) # change depending on dataset size

trainloader = DataLoader(train_set, batch_size=10, shuffle=True)
testloader = DataLoader(test_set, batch_size=10, shuffle=True)




EPOCHS = 3

class FaceEx(nn.Module):

    def __init__(self, input, h1, h2, classes):
        super().__init__()
        self.relu = nn.ReLU()
        self.sig = nn.Sigmoid()
        self.lsm = nn.LogSoftmax()
        self.fc1 = nn.Linear(input, h1)
        self.fc2 = nn.Linear(h1, h2)
        self.fc3 = nn.Linear(h2, classes)


    def forward(self, batch):
        out = self.fc1(batch)
        out = self.relu(out)
        out = self.fc2(out)
        out = self.relu(out)
        out = self.fc3(out)

        #return torch.tensor(np.linalg.norm(self.fc4(out).detach().numpy()))
        #return self.sig(self.fc4(out))
        return out


net = FaceEx(1680, 60, 60, 5)
#net.train()
opt = optim.Adam(net.parameters(), lr=0.1)
loss_func = nn.CrossEntropyLoss(torch.tensor([0.2, 1, 1, 1, 1]))



for epoch in range(EPOCHS):
    for data in trainloader:
        X, y = data

        net.zero_grad()
        output = net(X)
        print(output)
        loss = loss_func(output, y)

        loss.backward()
        opt.step()

test_correct = 0
total = 0
for data in testloader:
    X, y = data
    output = net(X)
    if torch.argmax(output) == y[0]:
        #print(torch.argmax(output))
        print(y[0])
        test_correct += 1
    total += 1

print(test_correct / total)


