import time
import os

# 1451543831

# print(time.asctime(time.localtime(1451543831)))
print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(1451543831)))


def generator_filename():
    i = 0
    while True:
        yield '{d}.txt'.format(d=i)
        i = + 1


print(generator_filename().__next__())

dd = os.path.getsize('/Users/Ming/Documents/pycharm-projects/ZhiHu/Zhihu/Zhihu/middlewares.py')
cc = os.path.getsize('/Users/Ming/Documents/pycharm-projects/ZhiHu/Zhihu/ResultPackage/0.txt')
print(dd,type(dd))
print(cc)