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
    fil_=open('SarsCoV.dat','w',encoding = "utf8")
    with open('metadata.csv',encoding ="utf8") as f_in:
        reader = csv.DictReader(f_in)
        cnt=0
        for row in reader:
            print(cnt)
            cnt+=1
            temp1 = row['uid']
            if temp1 in uidlist:
                print('already in it')
                continue
            uid=temp1
            uidlist.add(uid)
            title = row['title']
            
            abstract = row['abstract']
            authors = row['authors'].split('; ')
            if abstract:
                    fil_.write(abstract.strip())
                    fil_.write('\n')
            else:
                    fil_.write(title.strip())
                    fil_.write('\n')
            # access the full text (if available) for Intro
            #introduction = []
            #if row['pdf_json_files']:
            #    for json_path in row['pdf_json_files'].split('; '):
            #        print(json_path)
            #        with open(json_path) as f_json:
            #            full_text_dict = json.load(f_json)

                        # grab introduction section from *some* version of the full text
            #            for paragraph_dict in full_text_dict['body_text']:
            #                paragraph_text = paragraph_dict['text']
            #                section_name = paragraph_dict['section']
            #                if 'intro' in section_name.lower():
            #                    introduction.append(paragraph_text)
                        # stop searching other copies of full text if already got introduction
            #            if introduction:
            #                temp=[''.join(x) for x in introduction]
            #                fil_.write(temp.strip())
            #                fil_.write('\n')
            #                break
            #else:
            #    if abstract:
            #        fil_.write(abstract.strip())
            #        fil_.write('\n')
            #    else:
            #        fil_.write(title.strip())
            #        fil_.write('\n')        
    
            # save for later usage
            #uid_to_text[uid].append({
            #    'title': title,
            #    'abstract': abstract,
            #    'introduction': introduction
            #})
    
    fil_.close()    
