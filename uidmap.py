import csv
import os
import json
import sys
import numpy as np
from collections import defaultdict


if __name__ == '__main__':
    uid_to_text = defaultdict(list)
    uidlist=set()
    # open the file
    
    fi1=open('uidmap.txt','w')
    fi2=open('uidrevmap.txt','w')
    with open('metadata.csv',encoding ="utf8") as f_in:
        reader = csv.DictReader(f_in)
        cnt=0
        for row in reader:
            # access some metadata
            temp1 = row['uid']
            if temp1 in uidlist:
                print('already in it so counting down')
                #cnt-=1
                continue
            uid=temp1
            uidlist.add(uid)
            fi1.write(uid)
            fi1.write('\t')
            fi1.write(str(cnt))
            fi1.write('\n')
            fi2.write(str(cnt))
            fi2.write('\t')
            fi2.write(uid)
            fi2.write('\n')
            cnt+=1
            print(cnt)
    fi1.close()
    fi2.close()
    d={}
    with open("uidmap.txt") as f:
        for line in f:
            (key, val) = line.split()
            d[key] = val
    fil_=open('covqrels.txt','w')
    f1=open('qrels.txt','r')
    Li_=f1.readlines()
    for lines in Li_:
        (q,u,r)=lines.strip().split()
        
        fil_.write(q)
        fil_.write('\t')
        fil_.write(d[u])
        fil_.write('\t')
        fil_.write(r)
        fil_.write('\n')
    fil_.close()
    print('ENtered the test phase')
    d1={}
    with open("uidrevmaptest.txt") as f:
        for line in f:
            (key, val) = line.split()
            d1[key] = val
    fil1_=open('predictions.txt','w')
    f1=open('evalprediction.txt','r')
    Li_=f1.readlines()
    for lines in Li_:
        (q,u,r)=lines.strip().split()
        
        fil1_.write(q)
        fil1_.write('\t')
        fil1_.write(d1[u])
        fil1_.write('\t')
        fil1_.write(r)
        fil1_.write('\n')
    fil1_.close()
    
