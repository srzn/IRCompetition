import csv
import os
import json
import sys
import numpy as np
from collections import defaultdict


if __name__ == '__main__':
    
    # open the file
    fil_=open('SarsCoV.dat','r',encoding = "utf8")
    lins=fil_.readlines()
    cnt=0
    for lines in lins:
        print(cnt)
        cnt+=1
