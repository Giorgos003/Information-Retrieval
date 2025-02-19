import sqlite3
import pickle
import sys
from keyword_extraction_test import dense_keyword_extraction as kx

def find_id_ranges():
    pass

ids = find_id_ranges()
ids = [0, 9403, 9422, 16845, 187008, 227160, 367031, 502921, 645448, 733130, 836965, 846059, 846093, 1003708, 1026146, 1236629, 1280917 + 1]
conn = sqlite3.connect('data.db')
cursor = conn.cursor()

data = conn.execute("select distinct government from unfiltered_records")
governments = [gov[0].replace("[","").replace("]","").replace("'","").replace('"',"") for gov in data]

for i in range(len(ids) - 1):
    left = ids[i]
    right = ids[i+1]-1

    print(governments[i])
    print("---------------------------------------")
        
    data = conn.execute(f"SELECT political_party, count(distinct member_name), group_concat(speech) FROM unfiltered_records where id>={left} and id<={right} group by political_party").fetchall()

    data = [list(row) for row in data]

    for party in data:
        party_name = party[0]
        num_politicians = party[1]
        num_words = len(party[2].split())

        print(f"{party_name}: {num_words/num_politicians:.0f}")
    print()
    print()

conn.close()
    
