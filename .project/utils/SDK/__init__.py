from os.path import dirname, basename, isfile, join
import glob

# 将包名显示暴漏在外，这样from SDK import *就会导入该文件夹下的所有.py文件
modules = glob.glob(join(dirname(__file__), "*.py"))
__all__ = [basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]
