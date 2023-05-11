from dataset import Data
from torch import nn, optim
import pandas as pd
from torch.utils.data import DataLoader
#from tmp import Data
import torch

class linear_regression(nn.Module):
    def __init__(self, input_size, output_size):
        super(linear_regression,self).__init__()
        self.linear = nn.Linear(input_size, output_size)
    def forward(self, x):
        yhat = self.linear(x)
        return yhat


if __name__ == "__main__":
    data = pd.read_csv("./sample.csv")
    dataset = Data(data)
    #dataset = Data()
    model = linear_regression(2, 2)
    optimizer = optim.SGD(model.parameters(), lr = 0.1)
    criterion = nn.MSELoss()
    train_loader = DataLoader(dataset=dataset, batch_size=1)
    LOSS = []
 
    epochs = 100
   
    for epoch in range(epochs):
        for x, y in train_loader:
            print(x)
            yhat = model(x)
            print(yhat)
            #calculate the loss
            loss = criterion(yhat, y)
            #store loss/cost 
            LOSS.append(loss.item())
            print("Criterion:", loss.item())
            #clear gradient 
            optimizer.zero_grad()
            #Backward pass: compute gradient of the loss with respect to all the learnable parameters
            loss.backward()
            #the step function on an Optimizer makes an update to its parameters
            optimizer.step()

