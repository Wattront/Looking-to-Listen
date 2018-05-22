# modules we are gonna use
import chainer
import chainer.links as L
import chainer.functions as F
from chainer import cuda
from chainer.training import extensions
from chainer.functions.loss.mean_squared_error import mean_squared_error
import chainermn

import numpy as np
import matplotlib.pyplot as plt
import argparse

from network import Audio_Visual_Net

# setup
np.random.seed(0)

# main
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gpu", "-g", type=int, default=-1,
                        help="specify GPU")
    args = parser.parse_args()
    
    if args.gpu >= 0:
        xp = cuda.cupy
        cuda.get_device(args.gpu).use()
    else:
        xp = np
    
    print("loading model...")
    model = L.Classifier(Audio_Visual_Net(), lossfun=mean_squared_error, accfun=mean_squared_error)
    if args.gpu >= 0:
        model.to_gpu(args.gpu)
    optimizer = chainer.optimizers.Adam()
    optimizer.setup(model)
    
    print("loading data...")

    X = [
        (xp.random.rand(1, 298, 257).astype(xp.float32) + 1.,
         xp.random.rand(1024, 75, 1).astype(xp.float32) + 1.,
         xp.random.rand(1024, 75, 1).astype(xp.float32) + 1.,
         xp.random.rand(298, 257*2).astype(xp.float32))
    ]
    train = X + X + X + X + X + X + X + X + X + X + X + X
    train_iter = chainer.iterators.SerialIterator(dataset=train, batch_size=6, shuffle=True, repeat=True)
    
    print("setting trainer...")
    updater = chainer.training.StandardUpdater(train_iter, optimizer, device=args.gpu)
    trainer = chainer.training.Trainer(updater, (10, "epoch"), out="result")

    trainer.extend(extensions.LogReport())
    trainer.extend(extensions.ProgressBar())
    trainer.extend(extensions.PrintReport(["epoch", "main/loss"]))
    
    print("start training...")
    trainer.run()
    
    model.to_cpu()
    chainer.serializers.save_npz("result/model", model)
    chainer.serializers.save_npz("result/optimizer", optimizer)

if __name__ == "__main__":
    main()