import os
import sys
from pathlib import Path

path = Path(sys.path[0]) #脚本所在目录
path = path.joinpath("..").joinpath("source").joinpath("_posts") #进入posts目录

files = os.listdir(path)
for file in files:
    file_path = path.joinpath(path, file)
    if os.path.isdir(file_path):
        if len(os.listdir(file_path)) == 0: #移除空文件夹
            os.removedirs(file_path)
            print(f"{file_path} is removed.")