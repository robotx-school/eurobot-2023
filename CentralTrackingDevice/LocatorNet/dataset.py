from torch.utils.data import Dataset, DataLoader
import torch
import pandas as pd

class Data(Dataset):
    def __init__(self, data):
            tmp_data_x = []
            tmp_data_y = []
            for _, row in data.iterrows(): 
                input_x, input_y, target_x, target_y = row['px_x'], row['px_y'], row['field_x'], row['field_y']
                tmp_data_x.append([input_x, input_y])
                tmp_data_y.append([target_x, target_y])
            self.x = torch.tensor(tmp_data_x * 5).float()
            self.y = torch.tensor(tmp_data_y * 5).float()

    def __getitem__(self,index):
        return self.x[index],self.y[index]
    
    def __len__(self):
        return len(self.x)

if __name__ == "__main__":
    data = pd.read_csv("sample.csv")
    print("Creating dataset")
    dataset = Data(data)
    #print(dataset.__len__())
    print(dataset.__getitem__(1))
