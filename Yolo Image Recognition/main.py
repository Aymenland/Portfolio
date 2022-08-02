import os
import glob
import subprocess


def train(batch, epoch):
    """Training"""

    subprocess.run(["python", "yolov5/train.py", "--img", "640", "--batch", str(batch), "--epochs", str(epoch), "--data",
                    "yolov5/dataset.yaml", "--weights", "yolov5s.pt"])


def test():
    """Testing"""

    subprocess.run(["python", "yolov5/detect.py", "--weights", "yolov5/runs/train/exp/weights/best.pt",
                    "--img", "640", "--conf", "0.25", "--source", "yolov5/data/dataset/test/images"])


if __name__ == "__main__":
    train(8, 100)
    test()
