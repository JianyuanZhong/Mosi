import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from torch.autograd import Variable
import matplotlib.pyplot as plt
import numpy as np
import gzip, cPickle

class MosiDataset(Dataset):
    def __init__(self, X, Y):
        self.X = X
        self.Y = Y
        
    def __len__(self):
        return len(self.X)
    
    def __getitem__(self, idx):
        X = torch.FloatTensor(self.X[idx])
        Y = torch.FloatTensor(self.Y[idx])
        return X,Y


def pad_tensor(vec, pad, dim):
    """
    args:
        vec - tensor to pad
        pad - the size to pad to
        dim - dimension to pad

    return:
        a new tensor padded to 'pad' in dimension 'dim'
    """
    pad_size = list(vec.shape)
    pad_size[dim] = pad - vec.size(dim)
    return torch.cat([vec, torch.zeros(*pad_size)], dim=dim)


class PadCollate:
    """
    a variant of callate_fn that pads according to the longest sequence in
    a batch of sequences
    """

    def __init__(self, dim=0):
        """
        args:
            dim - the dimension to be padded (dimension of time in sequences)
        """
        self.dim = dim

    def pad_collate(self, batch):
        """
        args:
            batch - list of (tensor, label)

        reutrn:
            xs - a tensor of all examples in 'batch' after padding
            ys - a LongTensor of all labels in batch
        """
        # find longest sequence
        max_len = max(map(lambda x: x[0].shape[self.dim], batch))
        # pad according to max_len
        batch = map(lambda (x, y):
                    (pad_tensor(x, pad=max_len, dim=self.dim), y), batch)
        # stack all
        xs = torch.stack(map(lambda x: x[0], batch), dim=0)
        ys = torch.FloatTensor(map(lambda x: x[1], batch))
        return xs, ys

    def __call__(self, batch):
        return self.pad_collate(batch)


def load_data(file_name):
	fp=gzip.open(file_name,'rb') 
	(x,y) =cPickle.load(fp)
	fp.close()
	return x,y

def get_data_loader(x,y):
	data=MosiDataset(x,y)
	d_loader=DataLoader(data, batch_size=6, shuffle=True, num_workers=2, collate_fn=PadCollate(dim=0))
	return d_loader


def get_unpad_data(x):
    x = x.cpu()
    x=x.numpy()
    x=x[~np.all(x == 0, axis=1)]
    return x



def test_data_loader():
    x=[[[1,2],[4,6]],[[4,5]],[[6,7],[10,11]],[[4,7],[10,11]],[[4,7],[10,11],[1,0]],[[8,7],[10,11]],[[5,5]]]
    y=[[1],[0],[1],[1],[1],[0],[0]]
    data_loader=get_data_loader(x,y)
    for i, data in enumerate(data_loader):
        seq ,label = data
        print seq,label
        for j,x in enumerate(seq):
            x=get_unpad_data(x)
            print x

# test_data_loader()




