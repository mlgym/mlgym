import os
import torch
import pickle
from torchvision import transforms
from torch.utils.data import Dataset, DataLoader

def unpickle(file):
    with open(file, 'rb') as fo:
        dict = pickle.load(fo, encoding='bytes')
    return dict

class CustomCIFAR10Dataset(Dataset):
    def __init__(self, data_dir, folds, transform=None):
        self.data_dir = data_dir
        self.transform = transform
        self.folds = folds
        self.data, self.labels = self.load_data()

    def load_data(self):
        data = []
        labels = []
        for i in self.folds:
            batch_data = unpickle(os.path.join(self.data_dir, f'data_batch_{i}'))
            data.append(batch_data[b'data'])
            labels.extend(batch_data[b'labels'])
        data = torch.cat([torch.tensor(batch, dtype=torch.float32) / 255.0 for batch in data])
        labels = torch.tensor(labels, dtype=torch.long)
        return data, labels

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        image = self.data[idx].view(3, 32, 32).permute(1, 2, 0)
        label = self.labels[idx]
        if self.transform:
            image = self.transform(image)
        return {'image': image, 'label': label}

# Define any additional transformations if needed
# Convert PIL Image to PyTorch Tensor
transform = transforms.Compose([
    transforms.ToTensor()
])

batch_size = 64

# Create an instance of the custom dataset & dataloader
custom_dataset = CustomCIFAR10Dataset(data_dir='./downloads/cifar-10-python', folds=[1,2,3], transform=transform)
train_dataloader = DataLoader(custom_dataset, batch_size=batch_size, shuffle=True)
print("train_dataloader = ",len(train_dataloader))

custom_dataset = CustomCIFAR10Dataset(data_dir='./downloads/cifar-10-python', folds=[4,5], transform=transform)
val_dataloader = DataLoader(custom_dataset, batch_size=batch_size, shuffle=False)
print("val_dataloader = ",len(val_dataloader))
