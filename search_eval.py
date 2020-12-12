import math
import sys
import time
import metapy
import pytoml
import numpy as np
import pandas as pd
import pandas_read_xml as pdx
import xml.etree.ElementTree as ET #https://stackoverflow.com/questions/13244533/iterating-through-xml-in-python-through-keyerror

class InL2Ranker(metapy.index.RankingFunction):
    
    def __init__(self, some_param):
        self.param = some_param
        super(InL2Ranker,self).__init__()
    
    def score_one(self, sd):
        
        tfn = sd.doc_term_count*math.log(1+sd.avg_dl/sd.doc_size,2)
        log_numerator = math.log(((sd.num_docs+1)/(sd.corpus_term_count+0.5)),2)
        tfn_prod = tfn/(tfn+self.param)
        tot_score = sd.query_term_weight*tfn_prod*log_numerator
        
        return tot_score
    
def load_ranker(cfg_file,opt,k1,b,k3,k4,l,m,s,d):
    if opt==0:
        rank1=metapy.index.OkapiBM25(k1=k1, b=b, k3=k3)
    elif opt==1:
        rank1 = InL2Ranker(k4)
    elif opt==2:
        rank1 = metapy.index.JelinekMercer(l)
    elif opt==3:
        rank1 = metapy.index.DirichletPrior(m)
    elif opt==4:
        rank1 = metapy.index.PivotedLength(s)
    elif opt==5:
        rank1 = metapy.index.AbsoluteDiscount(d)
    else:
        rank1 = InL2Ranker(1.0)
        
    return rank1

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: {} config.toml <num>".format(sys.argv[0]))
        sys.exit(1)

    
    cfg = sys.argv[1]
    option=int(sys.argv[2])
    print('Building or loading index...')
    print('option')
    print(option)
    count_=0
    max_ndcg=0.0
    max_k1=0
    max_b=0
    max_k3=0
    max_k4=0
    max_l=0
    max_m=0
    max_s=0
    max_d=0
    cfg2='config-test.toml'
    idx2=metapy.index.make_inverted_index(cfg2)
    print('Num test docs')
    print(idx2.num_docs())
    fii = open('evalprediction.txt','w')
    if(option==0):
        for k1 in np.arange(1,10,1):
            for b in np.arange(0,1,0.1):
                
                count_+=1
                idx = metapy.index.make_inverted_index(cfg)
                print('Num docs')
                print(idx.num_docs())
                
                
                ranker = load_ranker(cfg,option,k1,b,500,1,1,1,1,1)
                ev = metapy.index.IREval(cfg)

                with open(cfg, 'r') as fin:
                    cfg_d = pytoml.load(fin)

                query_cfg = cfg_d['query-runner']
                if query_cfg is None:
                    print("query-runner table needed in {}".format(cfg))
                    sys.exit(1)

                start_time = time.time()
                top_k = 1000
                query_path = query_cfg.get('query-path', 'queries.txt')
                
                query_start = query_cfg.get('query-id-start', 0)

                query = metapy.index.Document()
                ndcg = 0.0
                num_queries = 0

                #print('Running queries')

                with open(query_path) as query_file:
                    for query_num, line in enumerate(query_file):
                        query.content(line.strip())
                        #print(line)
                        results = ranker.score(idx, query, top_k)
                        ndcg += ev.ndcg(results, query_start + query_num, top_k)
                        avg_p = ev.avg_p(results, query_num, top_k)
                        num_queries+=1
                        #print("Query {} average precision: {}".format(query_num + 1, avg_p))
                ndcg= ndcg / num_queries
                if max_ndcg<ndcg:
                    max_ndcg=ndcg
                    max_k1=k1
                    max_b=b
                    #max_k3=k3
                print('iter',count_)    
                #print("NDCG@{}: {}".format(top_k, ndcg))
                #print("Elapsed: {} seconds".format(round(time.time() - start_time, 4)))
        print('Max NDCG for Okapi',max_ndcg)
        print('Max k1 for Okapi',max_k1)
        print('Max b for Okapi',max_b)
        #print('Max k3 for Okapi',max_k3)
        rankertest = load_ranker(cfg2,option,max_k1,max_b,500,1,1,1,1,1)
        with open(cfg2, 'r') as fin:
            cfg2_d = pytoml.load(fin)

            query_cfg = cfg2_d['query-runner']
            if query_cfg is None:
                print("query-runner table needed in {}".format(cfg2))
                sys.exit(1)

            start_time = time.time()
            top_k = 1000
            query_path = query_cfg.get('query-path', 'queries.txt')

            query_start = query_cfg.get('query-id-start', 0)

            query = metapy.index.Document()

            #print('Running queries')
            print('Final results')
            cntt=0
            
            with open(query_path) as query_file:
                for query_num, line in enumerate(query_file):
                    cntt=query_num+1
                    query.content(line.strip())
                    #print(line)
                    results = rankertest.score(idx2, query, top_k)
                    for i in results:
                        fii.write(str(cntt))
                        fii.write('\t')
                        fii.write(str(i[0]))
                        fii.write('\t')
                        fii.write(str(i[1]))
                        fii.write('\n')
            
    elif(option==1):
        for k4 in np.arange(0.1,10,0.1):
            count_+=1
            idx = metapy.index.make_inverted_index(cfg)
            ranker = load_ranker(cfg,option,2.2,1,500,k4,1,1,1,1)
            ev = metapy.index.IREval(cfg)

            with open(cfg, 'r') as fin:
                cfg_d = pytoml.load(fin)

            query_cfg = cfg_d['query-runner']
            if query_cfg is None:
                print("query-runner table needed in {}".format(cfg))
                sys.exit(1)

            start_time = time.time()
            top_k = 1000
            query_path = query_cfg.get('query-path', 'queries.txt')
            query_start = query_cfg.get('query-id-start', 0)

            query = metapy.index.Document()
            ndcg = 0.0
            num_queries = 0

            #print('Running queries')

            with open(query_path) as query_file:
                for query_num, line in enumerate(query_file):
                    query.content(line.strip())
                    results = ranker.score(idx, query, top_k)
                    ndcg += ev.ndcg(results, query_start + query_num, top_k)
                    avg_p = ev.avg_p(results, query_num, top_k)
                    num_queries+=1
                    print("Query {} average precision: {}".format(query_num + 1, avg_p))
            ndcg= ndcg / num_queries
            if max_ndcg<ndcg:
                max_ndcg=ndcg
                max_k4=k4
            #print(count_)    
            print("NDCG@{}: {}".format(top_k, ndcg))
            #print("Elapsed: {} seconds".format(round(time.time() - start_time, 4)))                    
        print('Max NDCG for InL2ranker',max_ndcg)
        print('Max k4 for Okapi',max_k4)
    elif(option==2):
        for l in np.arange(0.1,100,0.1):
            count_+=1
            idx = metapy.index.make_inverted_index(cfg)
            ranker = load_ranker(cfg,option,2.2,1,500,5.6,l,0.1,1,1)
            ev = metapy.index.IREval(cfg)

            with open(cfg, 'r') as fin:
                cfg_d = pytoml.load(fin)

            query_cfg = cfg_d['query-runner']
            if query_cfg is None:
                print("query-runner table needed in {}".format(cfg))
                sys.exit(1)

            start_time = time.time()
            top_k = 10
            query_path = query_cfg.get('query-path', 'queries.txt')
            query_start = query_cfg.get('query-id-start', 0)

            query = metapy.index.Document()
            ndcg = 0.0
            num_queries = 0

            #print('Running queries')

            with open(query_path) as query_file:
                for query_num, line in enumerate(query_file):
                    query.content(line.strip())
                    results = ranker.score(idx, query, top_k)
                    ndcg += ev.ndcg(results, query_start + query_num, top_k)
                    num_queries+=1
            ndcg= ndcg / num_queries
            if max_ndcg<ndcg:
                max_ndcg=ndcg
                max_l=l
            print(count_)    
            print("NDCG@{}: {}".format(top_k, ndcg))
            #print("Elapsed: {} seconds".format(round(time.time() - start_time, 4)))                    
        print('Max NDCG for JenkinFuckin',max_ndcg)
        print('Max l for Okapi',max_l)
    elif(option==3):
        for m in np.arange(0,100,0.1):
            count_+=1
            idx = metapy.index.make_inverted_index(cfg)
            ranker = load_ranker(cfg,option,2.2,1,500,5.6,0.6,m,1,1)
            ev = metapy.index.IREval(cfg)

            with open(cfg, 'r') as fin:
                cfg_d = pytoml.load(fin)

            query_cfg = cfg_d['query-runner']
            if query_cfg is None:
                print("query-runner table needed in {}".format(cfg))
                sys.exit(1)

            start_time = time.time()
            top_k = 10
            query_path = query_cfg.get('query-path', 'queries.txt')
            query_start = query_cfg.get('query-id-start', 0)

            query = metapy.index.Document()
            ndcg = 0.0
            num_queries = 0

            #print('Running queries')

            with open(query_path) as query_file:
                for query_num, line in enumerate(query_file):
                    query.content(line.strip())
                    results = ranker.score(idx, query, top_k)
                    ndcg += ev.ndcg(results, query_start + query_num, top_k)
                    num_queries+=1
            ndcg= ndcg / num_queries
            if max_ndcg<ndcg:
                max_ndcg=ndcg
                max_m=m
            print(count_)    
            print("NDCG@{}: {}".format(top_k, ndcg))
            #print("Elapsed: {} seconds".format(round(time.time() - start_time, 4)))                    
        print('Max NDCG for Dirichlet smooth',max_ndcg)
        print('Max l for Okapi',max_m)
    elif(option==4):
        for s in np.arange(0,5,0.005):
            count_+=1
            idx = metapy.index.make_inverted_index(cfg)
            ranker = load_ranker(cfg,option,2.2,1,500,5.6,0.6,69,s,1)
            ev = metapy.index.IREval(cfg)

            with open(cfg, 'r') as fin:
                cfg_d = pytoml.load(fin)

            query_cfg = cfg_d['query-runner']
            if query_cfg is None:
                print("query-runner table needed in {}".format(cfg))
                sys.exit(1)

            start_time = time.time()
            top_k = 10
            query_path = query_cfg.get('query-path', 'queries.txt')
            query_start = query_cfg.get('query-id-start', 0)

            query = metapy.index.Document()
            ndcg = 0.0
            num_queries = 0

            #print('Running queries')

            with open(query_path) as query_file:
                for query_num, line in enumerate(query_file):
                    query.content(line.strip())
                    results = ranker.score(idx, query, top_k)
                    ndcg += ev.ndcg(results, query_start + query_num, top_k)
                    num_queries+=1
            ndcg= ndcg / num_queries
            if max_ndcg<ndcg:
                max_ndcg=ndcg
                max_s=s
            print(count_)    
            print("NDCG@{}: {}".format(top_k, ndcg))
            #print("Elapsed: {} seconds".format(round(time.time() - start_time, 4)))                    
        print('Max NDCG for Pivoted',max_ndcg)
        print('Max l for Pivoted',max_s)
        
    elif(option==5):
        for d in np.arange(0,1,0.01):
            count_+=1
            idx = metapy.index.make_inverted_index(cfg)
            ranker = load_ranker(cfg,option,2.2,1,500,5.6,0.6,69,0.35,d)
            ev = metapy.index.IREval(cfg)

            with open(cfg, 'r') as fin:
                cfg_d = pytoml.load(fin)

            query_cfg = cfg_d['query-runner']
            if query_cfg is None:
                print("query-runner table needed in {}".format(cfg))
                sys.exit(1)

            start_time = time.time()
            top_k = 10
            query_path = query_cfg.get('query-path', 'queries.txt')
            query_start = query_cfg.get('query-id-start', 0)

            query = metapy.index.Document()
            ndcg = 0.0
            num_queries = 0

            #print('Running queries')

            with open(query_path) as query_file:
                for query_num, line in enumerate(query_file):
                    query.content(line.strip())
                    results = ranker.score(idx, query, top_k)
                    ndcg += ev.ndcg(results, query_start + query_num, top_k)
                    num_queries+=1
            ndcg= ndcg / num_queries
            if max_ndcg<ndcg:
                max_ndcg=ndcg
                max_d=d
            print(count_)    
            print("NDCG@{}: {}".format(top_k, ndcg))
            #print("Elapsed: {} seconds".format(round(time.time() - start_time, 4)))                    
        print('Max NDCG for abs disc',max_ndcg)
        print('Max d for Pivoted',max_d)
        fii.close()
    else:
      
        idx = metapy.index.make_inverted_index(cfg)
        ranker = load_ranker(cfg,option,1.1,1,3,1.2,1,3,1)
        ev = metapy.index.IREval(cfg)

        with open(cfg, 'r') as fin:
            cfg_d = pytoml.load(fin)

        query_cfg = cfg_d['query-runner']
        if query_cfg is None:
            print("query-runner table needed in {}".format(cfg))
            sys.exit(1)

        start_time = time.time()
        top_k = 10
        query_path = query_cfg.get('query-path', 'queries.txt')
        query_start = query_cfg.get('query-id-start', 0)

        query = metapy.index.Document()
        ndcg = 0.0
        num_queries = 0

        print('Running queries')

        with open(query_path) as query_file:
            for query_num, line in enumerate(query_file):
                query.content(line.strip())
                results = ranker.score(idx, query, top_k)
                ndcg += ev.ndcg(results, query_start + query_num, top_k)
                num_queries+=1
        ndcg= ndcg / num_queries

        print("NDCG@{}: {}".format(top_k, ndcg))
        print("Elapsed: {} seconds".format(round(time.time() - start_time, 4)))
        fii.close()