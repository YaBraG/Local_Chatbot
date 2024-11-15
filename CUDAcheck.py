import torch
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# print(device)
# torch.cuda.is_available()
# x = torch.rand(5, 3)
# print(x)
torch.cuda.empty_cache()
print(torch.cuda.is_available())
print(torch.cuda.device_count())