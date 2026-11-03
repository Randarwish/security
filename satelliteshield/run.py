"""EuroSAT Sentinel-2 RGB robustness benchmark. Run: python satelliteshield/run.py"""
import argparse
import json
import random
from pathlib import Path

def main():
    import numpy as np
    import torch
    from torch import nn
    from torch.utils.data import DataLoader, random_split
    from torchvision.datasets import EuroSAT
    from torchvision.transforms import ToTensor

    p = argparse.ArgumentParser()
    p.add_argument("--epochs", type=int, default=5)
    p.add_argument("--batch-size", type=int, default=64)
    p.add_argument("--epsilon", type=float, default=4/255)
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()
    if args.epochs < 1 or args.batch_size < 1 or not (0 <= args.epsilon <= 1):
        p.error("Invalid experiment parameters")
    random.seed(args.seed); np.random.seed(args.seed); torch.manual_seed(args.seed)
    if torch.cuda.is_available(): torch.cuda.manual_seed_all(args.seed)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dataset = EuroSAT(root="data", download=True, transform=ToTensor())
    n = len(dataset)
    train, val, test = random_split(dataset, [int(.7*n), int(.15*n), n-int(.7*n)-int(.15*n)], generator=torch.Generator().manual_seed(args.seed))
    loaders = [DataLoader(s, batch_size=args.batch_size, shuffle=i==0) for i,s in enumerate((train,val,test))]
    model = nn.Sequential(nn.Conv2d(3,32,3,padding=1),nn.ReLU(),nn.MaxPool2d(2),nn.Conv2d(32,64,3,padding=1),nn.ReLU(),nn.AdaptiveAvgPool2d(1),nn.Flatten(),nn.Linear(64,10)).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)

    def attack(x,y,kind):
        if kind is None: return x
        origin = x.detach()
        adv = origin.clone()
        steps = 1 if kind == "fgsm" else 10
        alpha = args.epsilon if kind == "fgsm" else max(args.epsilon/4, 1e-8)
        for _ in range(steps):
            adv = adv.detach().requires_grad_(True)
            grad = torch.autograd.grad(nn.functional.cross_entropy(model(adv),y),adv)[0]
            adv = (adv.detach()+alpha*grad.sign()).clamp(origin-args.epsilon,origin+args.epsilon).clamp(0,1)
        return adv.detach()

    def score(loader,kind=None):
        model.eval(); correct=total=0
        for x,y in loader:
            x,y=x.to(device),y.to(device)
            with torch.enable_grad(): xx=attack(x,y,kind)
            with torch.no_grad(): correct += (model(xx).argmax(1)==y).sum().item()
            total+=len(y)
        return {"correct":correct,"total":total,"accuracy":correct/total}

    history=[]
    for epoch in range(args.epochs):
        model.train(); total_loss=0
        for x,y in loaders[0]:
            x,y=x.to(device),y.to(device)
            opt.zero_grad(); loss=nn.functional.cross_entropy(model(x),y); loss.backward(); opt.step()
            total_loss += loss.item()*len(y)
        history.append({"epoch":epoch+1,"train_loss":total_loss/len(train),"validation":score(loaders[1])})
        print(history[-1])
    results={"dataset":"EuroSAT RGB / Sentinel-2-derived","seed":args.seed,"epsilon":args.epsilon,"split":"random 70/15/15, NOT geographic","history":history,"clean":score(loaders[2]),"fgsm":score(loaders[2],"fgsm"),"pgd":score(loaders[2],"pgd")}
    Path("results").mkdir(exist_ok=True)
    Path("results/satelliteshield.json").write_text(json.dumps(results,indent=2))
    print(json.dumps({k:results[k] for k in ("clean","fgsm","pgd")},indent=2))

if __name__=="__main__": main()
