import os
from pprint import pprint

def dir_walk(path):
    """
    Searches and adds the .py files found in the specified path.
    :param path:
    :return:
    """



    os.walk(path)
    dir_contents = dict(root='', subdirs='', files='')
    dir_list = list()

    for root, subdirs, files in os.walk(path):
        dir_contents.update(root=root)
        dir_contents.update(subdirs=subdirs)
        dir_contents.update(files=files)
        dir_list.append(dir_contents.copy())
    return dir_list
        # print('root:')
        # pprint(root)
        # print('subdir:')
        # pprint(subdir)
        # print('files:')
        # pprint(files)

def parse_dir(dir_list):
    for dir_info in dir_list:
        print(dir_info.get('root'), '\t', dir_info.get('subdirs'), '\t', dir_info.get('files'))

if __name__ == '__main__':

    path = os.getcwd() + '/tic_modules'
    dir_list = dir_walk(path)
    parse_dir(dir_list)