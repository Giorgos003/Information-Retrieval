import sqlite3
import pickle
import sys
from keyword_extraction import dense_keyword_extraction as kx

# Step-1: Load the initial features from db (creates parl_members_vecs.pkl)
#-----------------------------------------
conn = sqlite3.connect('data.db')
cursor = conn.cursor()

data = conn.execute("SELECT DISTINCT member_name, GROUP_CONCAT(DISTINCT political_party), GROUP_CONCAT(DISTINCT member_region), GROUP_CONCAT(DISTINCT roles), GROUP_CONCAT(DISTINCT member_gender)FROM unfiltered_records GROUP BY member_name").fetchall()

members = [list(row) for row in data]

with open("parl_members_vecs.pkl", "wb") as file:
    pickle.dump(members, file)


# Step-2: Preprocess and adding a feature for keywords (creates parl_members_vecs.pkl)
#-----------------------------------------
with open("parl_members_vecs.pkl", "rb") as file:
    members = pickle.load(file)

for i in range(len(members)):
    member_name = members[i][0]
    print(member_name)

    parties = members[i][1].split(",")
    members[i][1] = parties

    regions = members[i][2].split(",") if members[i][2] else []
    members[i][2] = regions

    # Extracting irrelevant characters from the roles
    roles = members[i][3].replace("[","").replace("]","").replace("'","").replace('"',"")
    roles = roles.split(",")
    members[i][3] = roles

    # Encoding gender as 0 or 1 to make it easier to compare
    gender = 1 if members[i][4] == 'female' else 0
    members[i][4] = gender

    # Saving the surname of the members in a different field
    # for easier comparisons between members
    tokenized_name = members[i][0].split(" ")

    surname = tokenized_name[0] if len(tokenized_name) == 3 else tokenized_name[1]
    members[i].insert(1,surname)


    members[i].append(kx(member_name, ""))

with open("parl_members_vecs.pkl", "wb") as file:
    pickle.dump(members, file)


# Step-3: Calculate the similarities 
#-----------------------------------------
with open("parl_members_vecs.pkl", "rb") as file:
    members = pickle.load(file)

sims = []
for m1 in members:
    for m2 in members:
        if m1[1] >= m2[1]:
            continue

        surname_similarity = 1 if m1[1] == m2[1] else 0

        try:
            parties_similarity = len(set(m1[2]) & set(m2[2]))/len(set(m1[2]) | set(m2[2]))
        except:
            parties_similarity = 0

        try:
            regions_similarity = len(set(m1[3]) & set(m2[3]))/len(set(m1[3]) | set(m2[3]))
        except:
            regions_similarity = 0

        try:
            roles_similarity = len(set(m1[4]) & set(m2[4]))/len(set(m1[4]) | set(m2[4]))
        except:
            roles_similarity = 0

        gender_similarity = 1 if m1[5] == m2[5] else 0

        try:
            keywords_similarity = len(set(m1[6]) & set(m2[6]))/len(set(m1[6]) | set(m2[6]))
        except:
            keywords_similarity = 0


        # Calculate the weighted similarity between 2 politicians
        sims.append( (m1[0],m2[0], (surname_similarity*2 + parties_similarity*3 + regions_similarity*1 + roles_similarity*2 + gender_similarity*1 + keywords_similarity*3)/12 ) )


sorted_sims = sorted(sims, key=lambda x:x[2], reverse=True)

with open("parl_members_sims.pkl", "wb") as file:
    pickle.dump(sorted_sims, file)


        
