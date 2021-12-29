import os
""" Get the current absolute path to the Repository on your system. 
Usefull for handling data and tests while being agnostic to current work dir
"""

path = os.path.abspath(os.getcwd())
while 'aisscv' in path:
    path = os.path.abspath(path+'/..')

__RepoPath__ = path
