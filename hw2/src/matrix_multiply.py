"""
Implementation of SimRank algorithm.

ref: https://en.wikipedia.org/wiki/SimRank

@date: Oct 4, 2018
@author: Zhenye Na
"""

import sys
import math
import numpy
from numpy import matrix

from scipy import sparse
from scipy.sparse import identity

# num_of_links = int(sys.stdin.readline())
num_of_links = 1000

logs = []

# for _ in range(num_of_links):
#     log = sys.stdin.readline()
#     logs.append(log)
#
# query = sys.stdin.readline().split(",")
# query_user = query[0]
# query_ad = query[1]

with open('../data/large_sample2.txt', 'r') as log_fp:
    logs = [ log.strip() for log in log_fp.readlines() ]

# query = sys.stdin.readline().strip().split(",")
# 896,6
query_user = "896"
query_ad = "6"

logs_tuple = [tuple(log.split(",")) for log in logs]

queries = list(set([ log[0] for log in logs_tuple ]))
ads = list(set([ log[1] for log in logs_tuple ]))

# Graph means the relations number
graph = matrix(numpy.zeros([len(queries), len(ads)]))

# create graph
for log in logs_tuple:
    query = log[0]
    ad = log[1]
    q_i = queries.index(query)
    a_j = ads.index(ad)
    graph[q_i, a_j] += 1

sgraph = sparse.csr_matrix(graph)

# similarity scores
query_sim = matrix(numpy.identity(len(queries)))
ad_sim = matrix(numpy.identity(len(ads)))
# query_sim = identity(len(queries))
# ad_sim = identity(len(ads))


def get_ads_num(query):
    q_i = queries.index(query)
    return sgraph.todense()[q_i]

def get_queries_num(ad):
    a_j = ads.index(ad)
    return sgraph.todense().transpose()[a_j]

def get_ads(query):
    series = get_ads_num(query).tolist()[0]
    return [ ads[x] for x in xrange(len(series)) if series[x] > 0 ]


def get_queries(ad):
    series = get_queries_num(ad).tolist()[0]
    return [ queries[x] for x in xrange(len(series)) if series[x] > 0 ]


def query_simrank(q1, q2, C):

    if q1 == q2: return 1

    prefix = C / (get_ads_num(q1).sum() * get_ads_num(q2).sum())
    postfix = 0

    for ad_i in get_ads(q1):
        for ad_j in get_ads(q2):
            i = ads.index(ad_i)
            j = ads.index(ad_j)
            postfix += ad_sim[i, j]

    return prefix * postfix


def ad_simrank(a1, a2, C):

    if a1 == a2: return 1

    prefix = C / (get_queries_num(a1).sum() * get_queries_num(a2).sum())
    postfix = 0

    for query_i in get_queries(a1):
        for query_j in get_queries(a2):
            i = queries.index(query_i)
            j = queries.index(query_j)
            postfix += query_sim[i,j]

    return prefix * postfix


def simple_simrank(C=0.8, k=10):

    for run in range(k):
        # queries simrank
        new_query_sim = matrix(numpy.identity(len(queries)))
        for qi in queries:
            for qj in queries:
                i = queries.index(qi)
                j = queries.index(qj)
                new_query_sim[i,j] = query_simrank(qi, qj, C)

        # ads simrank
        new_ad_sim = matrix(numpy.identity(len(ads)))
        for ai in ads:
            for aj in ads:
                i = ads.index(ai)
                j = ads.index(aj)
                new_ad_sim[i,j] = ad_simrank(ai, aj, C)

        # query_sim = new_query_sim
        # ad_sim = new_ad_sim

    return new_query_sim, new_ad_sim

def query_simrank_geometric(q1, q2):
    if q1 == q2:
        return 1

    prefix = 0.
    num = numpy.sum(get_ads_num(q1) == get_ads_num(q2))
    for i in range(1, num+1):
        prefix += 1 / math.pow(2, i)
    # print("query_simrank_geometric ->", prefix)
    postfix = 0

    for ad_i in get_ads(q1):
        for ad_j in get_ads(q2):
            i = ads.index(ad_i)
            j = ads.index(ad_j)
            postfix += ad_sim[i, j]

    return prefix * postfix


def ad_simrank_geometric(a1, a2):
    if a1 == a2: return 1

    prefix = 0.
    num = numpy.sum(get_queries_num(a1) == get_queries_num(a2))
    for i in range(1, num+1):
        prefix += 1 / math.pow(2, i)
    # print("ad_simrank_geometric ->", prefix)
    postfix = 0

    for query_i in get_queries(a1):
        for query_j in get_queries(a2):
            i = queries.index(query_i)
            j = queries.index(query_j)
            postfix += query_sim[i,j]

    return prefix * postfix


def evidence_geometric(k=10):
    """Incorporate evidence - geometric."""
    for _ in range(k):
        # queries simrank
        new_query_sim = matrix(numpy.identity(len(queries)))
        for qi in queries:
            for qj in queries:
                i = queries.index(qi)
                j = queries.index(qj)
                new_query_sim[i,j] = query_simrank_geometric(qi, qj)

        # ads simrank
        new_ad_sim = matrix(numpy.identity(len(ads)))
        for ai in ads:
            for aj in ads:
                i = ads.index(ai)
                j = ads.index(aj)
                new_ad_sim[i,j] = ad_simrank_geometric(ai, aj)

        # query_sim = new_query_sim
        # ad_sim = new_ad_sim

    return new_query_sim, new_ad_sim


def query_simrank_exponential(q1, q2):
    if q1 == q2:
        return 1

    prefix = 0.
    num = numpy.sum(get_ads_num(q1) == get_ads_num(q2))
    prefix = 1 - math.exp(-num)
    # print("query_simrank_exponential ->", prefix)
    postfix = 0

    for ad_i in get_ads(q1):
        for ad_j in get_ads(q2):
            i = ads.index(ad_i)
            j = ads.index(ad_j)
            postfix += ad_sim[i, j]

    return prefix * postfix


def ad_simrank_exponential(a1, a2):
    if a1 == a2:
        return 1

    prefix = 0.
    num = numpy.sum(get_queries_num(a1) == get_queries_num(a2))
    prefix = 1 - math.exp(-num)
    # print("ad_simrank_exponential ->", prefix)
    postfix = 0

    for query_i in get_queries(a1):
        for query_j in get_queries(a2):
            i = queries.index(query_i)
            j = queries.index(query_j)
            postfix += query_sim[i,j]

    return prefix * postfix



def evidence_exponential(k=10):
    """Incorporate evidence - exponential."""
    for _ in range(k):
        # queries simrank
        new_query_sim = matrix(numpy.identity(len(queries)))
        for qi in queries:
            for qj in queries:
                i = queries.index(qi)
                j = queries.index(qj)
                new_query_sim[i,j] = query_simrank_exponential(qi, qj)

        # ads simrank
        new_ad_sim = matrix(numpy.identity(len(ads)))
        for ai in ads:
            for aj in ads:
                i = ads.index(ai)
                j = ads.index(aj)
                new_ad_sim[i,j] = ad_simrank_exponential(ai, aj)

        # query_sim = new_query_sim
        # ad_sim = new_ad_sim

    return new_query_sim, new_ad_sim



def print_result_simple_simrank(query_user, query_ad, query_sim, ad_sim):
    # for query
    q_i = queries.index(query_user)
    a_j = ads.index(query_ad)

    query_sim_list = query_sim.tolist()
    ad_sim_list = ad_sim.tolist()

    target_query_list = query_sim_list[q_i]
    target_ad_list = ad_sim_list[a_j]

    queries_int = [int(i) for i in queries]
    query_list = list(zip(target_query_list, queries_int))

    ads_int = [int(i) for i in ads]
    ad_list = list(zip(target_ad_list, ads_int))

    query_list.sort(key=lambda sl: (-sl[0], sl[1]))
    ad_list.sort(key=lambda sl: (-sl[0], sl[1]))


    q_result = []
    for i in range(len(query_list)):
        if str(query_list[i][1]) != query_user:
            # print(str(query_list[i][1]), query_user)
            q_result.append(str(query_list[i][1]))
            if len(q_result) == 3:
                break

    a_result = []
    for i in range(len(ad_list)):
        if str(ad_list[i][1]) != query_ad:
            # print(str(ad_list[i][1]), query_ad)
            a_result.append(str(ad_list[i][1]))
            if len(a_result) == 3:
                break

    print(",".join(q_result))
    print(",".join(a_result))


if __name__ == '__main__':
    # print(queries)
    # print(ads)
    query_sim, ad_sim = simple_simrank()
    # print(query_sim)
    # print(ad_sim)
    print_result_simple_simrank(query_user, query_ad, query_sim, ad_sim)

    query_sim, ad_sim = evidence_geometric()
    # print(query_sim)
    # print(ad_sim)
    print_result_simple_simrank(query_user, query_ad, query_sim, ad_sim)

    query_sim, ad_sim = evidence_exponential()
    print_result_simple_simrank(query_user, query_ad, query_sim, ad_sim)