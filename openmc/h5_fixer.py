import sys,os
import os.path
# import string

cwd = os.getcwd() # return string of current working directory
tmpStr = 'if h5py.__version__ == \'2.6.0\':'
for root,dirs,files in os.walk(cwd):
    # print('dirpath -> '+str(root))
    # print('dirs -> '+str(dirs))
    # print('files -> '+str(files)+'\n')

    # if len(dirs)>0:
    #     print(dirs)
    #     tmpPath = str(root)+'/'+str(dirs[0])
    # else:
    #     tmpPath = str(root)+'/'+str(dirs)


    for elem in files:
        if '.pyc' in elem:
            continue
        else:
            tmpPath = str(root)+'/'+str(elem)
            with open(tmpPath,'r') as file1:
                for line in file1:
                    if tmpStr in line:
                        print(str(elem)+' has h5py data to change!')
