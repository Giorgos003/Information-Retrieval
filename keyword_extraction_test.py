import sqlite3
import string
import re
import networkx as nx
import Preprocess_tools
import pandas as pd


def extract_keywords(text): # Attention! Pass-by value
    """
    This function extracts keywords from a text string. It uses the k-core decomposition algorithm.
    At first, it preprocesses the speech so all capital letters, punctuation and numbers are removed. Also, tokenises the
    text.
    Finally, ut runs the k-core decomposition algorithm and extracts the keywords.

    :param text: input text string, the speech that we want to extract keywords from
    :return: the list of keywords of that speech
    """

    # Start by preprocessing the speech


    # Lowercase the text
    text = text.lower()

    # In some cases there was a problem that words had that form: "...αυτού.Επίσης..." or "αποτιμητικών/παραποιημένων"
    # And when we do the punctuation removal these words are taken as one
    # So we these commands we split the these kind of words beforehand

    # Pre-compiled regex patterns
    dot_splitter = re.compile(r'(\w)\.(\w)')
    slash_splitter = re.compile(r'(\w)/(\w)')

    text = dot_splitter.sub(r'\1. \2', text)    # Adds space after "."
    text = slash_splitter.sub(r'\1/ \2', text)    # Adds space after "/"


    # Remove punctuations
    greek_punctuation = string.punctuation + "«»"    # in 'string.punctuation' the '«»' are not included
    text = text.translate(str.maketrans('', '', greek_punctuation))

    # Tokenise the text
    token_pattern = re.compile(r'\b\w+\b')  # pre-compile for speed
    list_of_tokens = token_pattern.findall(text)
    del text    # we do not need it anymore. We free RAM space


    # Remove as many stopwords as possible
    stopwords = {'αλλά', 'αλίμονο', 'αλλού', 'αν', 'ανέφερε', 'αυτό', 'αυτή', 'αυτές', 'αυτούς', 'εφόσον', 'αυτού', 'αυτός',
                 'αυτός', 'βαθμός', 'βεβαίως', 'δηλαδή', 'δημοσίως', 'διά', 'δικά', 'διότι', 'δυστυχώς', 'εάν', 'εδώ',
                 'εξ', 'εγώ', 'εκ', 'εκεί', 'εκούσια', 'εν', 'ενώ', 'ευτυχώς', 'η', 'ή', 'ήδη', 'ίδια', 'ιδία', 'ίσως',
                 'καθώς', 'καλός', 'καλύτερα', 'καμία', 'καμία', 'και', 'καινούργια', 'κανείς', 'κανένα', 'κάτι',
                 'καμία', 'κάνει', 'κάνω', 'κοιτάξτε', 'κοινό', 'κουβέντα', 'κοίτα', 'λοιπόν', 'λόγω', 'μα', 'με',
                 'μέσα', 'μη', 'μετά', 'μπορεί', 'μου', 'να', 'νάτο', 'να', 'αν', 'όχι' 'ναι', 'όμως', 'ο', 'οποία',
                 'όποια', 'όπου', 'ότι', 'παρά', 'πάνω', 'πήγε', 'πολύ', 'ποιος', 'πρώτα', 'πώς', 'πρόβλημα', 'σας',
                 'σημαίνει', 'συνεπώς', 'στους', 'στη', 'στην', 'στους', 'στην', 'συγκριτικά', 'το', 'το', 'τότε',
                 'τούτο', 'όλα', 'όλοι', 'όπου', 'ότι', 'πάλι', 'πέρα', 'που', 'πρώτο', 'σου', 'συν', 'συνήθως',
                 'σχεδόν', 'το', 'τούτο', 'των', 'του', 'των', 'όπως', 'όταν', 'πριν', 'σύντομα', 'σίγουρα', 'σε',
                 'στο', 'στους', 'στον', 'στον', 'των', 'του', 'το', 'της', 'τους', 'το', 'το', 'τη', 'την', 'μας',
                 'σας', 'αλλά', 'αν', 'αντί', 'απο', 'αυτά', 'αυτές', 'αυτή', 'αυτό', 'αυτοί', 'αυτού', 'αυτούς', 'αυτών',
                 'αἱ', 'αυτό', 'αυτός', 'αὖ', 'γάρ', 'γα', 'γα^', 'γε', 'για', 'γαρ', "δ'", 'δέ', 'δή', 'δαί', 'δε',
                 'δεν', "δι", 'διά', 'διὰ', 'δε', 'δ’', 'εαν', 'είμαι', 'είμαστε', 'είναι', 'είσαι', 'είστε', 'εκείνα',
                 'εκείνες', 'εκείνη', 'εκείνο', 'εκείνοι', 'εκείνος', 'εκείνους', 'εκείνων', 'ενώ', 'επ', 'επί', 'εί',
                 'ειμί', 'εἰς', 'εἰσ', 'εἴ', 'είμαι', 'είτε', 'η', 'θα', 'ίσως', 'κ', 'καί', 'καίτοι', 'καθ', 'και',
                 'κατ', 'κατά', 'κι', 'κάν', 'καν', 'μέν', 'μήτε', 'μα', 'με', 'μεθ', 'μετ', 'μετά', 'μη', 'μην', 'μεν',
                 'μὲν', 'μὴ', 'μὴν', 'να', 'ο', 'οι', 'όμως', 'όπως', 'οσο', 'οτι', 'οἱ', 'οἳ', 'οἷς', 'οὐ', 'οὐδ',
                 'ουδεμία', 'ουδεμιά', 'ουδείς', 'ουδέ', 'ουδέν', 'ουκ', 'ούκ', 'ουχ', 'ούτε', 'ούτως', 'παρ', 'παρά', 'παρά',
                 'περί', 'περί', 'ποια', 'ποιές', 'ποιο', 'ποιοι', 'ποίος', 'ποιους', 'ποιων', 'ποτέ', 'που', 'πού',
                 'προ', 'προς', 'πρός', 'πρὸ', 'πρὸς', 'πως', 'πωσ', 'σε', 'στη', 'στην', 'στο', 'στον', 'σύ', 'σύν',
                 'σος', 'συ', 'συν', 'τα', 'την', 'τι', 'τις', 'τίσ', 'τα', 'τε', 'την', 'τησ', 'τι', 'τινά',
                 'τις', 'τισ', 'το', 'τοί', 'τοι', 'τοιούτος', 'τοιούτο', 'τον', 'τότε', 'του', 'του', 'τους', 'τοις',
                 'των', 'το', 'τον', 'τότε', 'τα', 'τας', 'την', 'το', 'τόν', 'τῆς', 'τῆσ', 'τῇ', 'των', 'τω', 'ως',
                 "αλλ'", 'ἀλλ’', 'απ', 'ἀπό', 'από', 'ἀφ', 'ἂν', 'ἃ', 'άλλος', 'άλλο', 'ἄν', 'ἄρα', 'ἅμα', 'ἐάν', 'ἐγώ',
                 'ἐγὼ', 'εκ', 'εν', 'εξ', 'επί', 'έτι', 'εφ', 'εάν', 'η', 'την', 'η', 'ης', 'ίνα', 'όν', 'ον', 'ος',
                 'ο', 'όδε', 'όθεν', 'όπερ', 'ὅς', 'ὅσ', 'ὅτε', 'ὅτι', 'υπ', 'υπέρ', 'υπό', 'ως', 'ώς', 'ώστε', 'βρε',
                 'μια', 'μία', 'μίας', 'μιας', 'στα', 'στο', 'ένα', 'γιατί', 'επειδή', 'διότι', 'καθώς', 'αφού', 'α', 'με',
                 'έναν', 'εμείς', 'οποίο', 'λίγο', 'όχι', 'ναι'}
    list_of_tokens = [word for word in list_of_tokens if word not in stopwords]


    # Remove the numbers that are into the tokenised speech
    list_of_tokens = [word for word in list_of_tokens if not word.isdigit()]




    # And now we do the keywords extraction


    # Create the directed graph
    graph = nx.DiGraph()

    # Set the length of the sliding window
    window_length =  3

    # We add the edges
    # For each token/word, we add edges between this word and its nearby words
    for i, word in enumerate(list_of_tokens):
        for j in range(i + 1, min(i + window_length, len(list_of_tokens))):
            graph.add_edge(word, list_of_tokens[j])


    # Remove the self-loops so the algorithm of k-core decomposition can work
    # We get the above error if we don't remove the self-loops
    graph.remove_edges_from(nx.selfloop_edges(graph))


    del  list_of_tokens     # We free up memory


    # Apply the k-core decomposition
    core_numbers = nx.core_number(graph)

    # Transform it to a dictionary so we can process it more easily
    core_numbers = dict(core_numbers)
    # print(core_numbers)


    ############################################################################################################
    # εδώ αν θέλουμε μπορούμε να ταξινομήσουμε τα keywords με βάση τη σημαντικότητα τους. Για ταχύτητα το βάζω σε
    # σχόλια… Βλέπουμε τι θέλουμε να κάνουμε…

    # Sort the core_numbers according the core number of each word
    core_numbers = sorted(core_numbers.items(), key=lambda x: x[1], reverse=True)

    # Convert the result back to a dictionary
    core_numbers = dict(core_numbers)
    # print(core_numbers)
    ############################################################################################################


    # Choose the words with core number bigger than 2
    # These are the keywords
    keywords = []
    cores = []
    for word, core in core_numbers.items():
        if int(core) > 2:   # We choose the 2 by-default
            keywords.append(word)
            cores.append(core)


    return keywords, cores




def keyword_extraction_test1(member_of_parliament, party):
    """
    This function loads from the database the rows that matches with the speech that the user wants to extract
    keywords from. Every speech that needs keyword extraction is used as input to the extract_keywords function.

    :param member_of_parliament: string, that contains the name of the MP that, from their speeches, we
        want to extract keywords from
    :param party: string, that contains the name of the party that we want to extract keywords from
    :return: nothing
    """
    # Path to our database file
    db_path = "all_the_data.db"
    db_path = 'data.db'

    # Connect to the database
    conn = sqlite3.connect(db_path)

    # Create a cursor object to interact with the database
    c = conn.cursor()

    # Get the list of all tables in the database
    # There is only one table in our database which of course contains our data in columns
    # The whole process is described in 'create_db_script.py' file
    c.execute("SELECT name FROM sqlite_master WHERE type=\'table\';")
    table_name = c.fetchone()[0]

    # Create indexes to the columns that are part of the query (the inputs of this function) so it
    # can run significantly faster
    c.execute(f'CREATE INDEX IF NOT EXISTS idx_member_name ON {table_name} (member_name)')
    c.execute(f'CREATE INDEX IF NOT EXISTS idx_political_party ON {table_name} (political_party)')

    # Before we run the query, we first preprocess the member_of_parliament & party variables (string) so they do not contain
    # capital letters & accents
    # Do not forget that in the database all data except for the speech is already preprocessed
    # Check the 'create_db_script.py' file
    member_of_parliament = member_of_parliament.lower()
    party = party.lower()

    # For the accents removal we use a function from the 'Preprocess_tools.py' file
    member_of_parliament  = Preprocess_tools.remove_accents(member_of_parliament)
    party = Preprocess_tools.remove_accents(party)

    # print(member_of_parliament, party)

    ###################################################################################################################

    # Καθώς δε γίνεται ο χρήστης να δίνει πάντα το ακριβές όνομα κάθε πολιτικού, υπάρχει η σκέψη να δέχεται ένα όνομα
    # και να βρίσκει έναν πολιτικό που περιέχει το όνομα αυτό και να βρίσκει keywords στις δικές του ομιλίες

    ###################################################################################################################


    # Fetch all the MPs from the table that have the 'member_of_parliament' name
    # and are from the 'party' political party
    # We should take into consideration that one of these strings can be empty
    if len(member_of_parliament) > 0 and len(party) > 0:
        c.execute(f'SELECT id, member_name, political_party, sitting_date, speech FROM {table_name} WHERE member_name=\'{member_of_parliament}\' and political_party=\'{party}\';')
    elif len(member_of_parliament) > 0:
        c.execute(f'SELECT id, member_name, political_party, sitting_date, speech FROM {table_name} WHERE member_name=\'{member_of_parliament}\';')
    elif len(party) > 0:
        c.execute(f'SELECT id, member_name, political_party, sitting_date, speech FROM {table_name} WHERE political_party=\'{party}\';')


    # For start, the output, will be stored in a csv file which will be named 'output.csv'
    # This 'output.csv' will store the ID, Name, Party, Date and the Keywords of each speach that was selected
    # in the above queries
    with open('output.csv', 'w', newline='', encoding='utf-8') as file:

        output_file = 'output.csv'

        # Prepare the CSV with a header
        columns = ['ID', 'Name', 'Party', 'Date', 'Keywords']
        df = pd.DataFrame(columns=columns)
        df.to_csv(output_file, index=False, encoding='utf-8')

        # Iterate each row of the database
        # In that way we do not store the bunch in the Main Memory but only one line each time
        for row in c:
            # In row[-1] contains the speech. The speech is not preprocessed
            keywords, cores = extract_keywords(row[-1])
            if len(keywords) > 0:
                current_row = pd.DataFrame([{
                    'ID': row[0],
                    'Name': row[1],
                    'Party': row[2],
                    'Speech': row[3],
                    'Keywords': ', '.join(keywords)
                }])

                # Append the row to the CSV file
                current_row.to_csv(output_file, mode='a', header=False, index=False, encoding='utf-8')

    # Close the connection
    conn.close()

    return

def dense_keyword_extraction(member_of_parliament, party):
    """
    This function loads from the database the rows that matches with the speech that the user wants to extract
    keywords from. Every speech that needs keyword extraction is used as input to the extract_keywords function.

    :param member_of_parliament: string, that contains the name of the MP that, from their speeches, we
        want to extract keywords from
    :param party: string, that contains the name of the party that we want to extract keywords from
    :return: nothing
    """
    # Path to our database file
    db_path = "all_the_data.db"
    db_path = 'data.db'

    # Connect to the database
    conn = sqlite3.connect(db_path)

    # Create a cursor object to interact with the database
    c = conn.cursor()

    # Get the list of all tables in the database
    # There is only one table in our database which of course contains our data in columns
    # The whole process is described in 'create_db_script.py' file
    c.execute("SELECT name FROM sqlite_master WHERE type=\'table\';")
    table_name = c.fetchone()[0]

    # Create indexes to the columns that are part of the query (the inputs of this function) so it
    # can run significantly faster
    c.execute(f'CREATE INDEX IF NOT EXISTS idx_member_name ON {table_name} (member_name)')
    c.execute(f'CREATE INDEX IF NOT EXISTS idx_political_party ON {table_name} (political_party)')

    # Before we run the query, we first preprocess the member_of_parliament & party variables (string) so they do not contain
    # capital letters & accents
    # Do not forget that in the database all data except for the speech is already preprocessed
    # Check the 'create_db_script.py' file
    member_of_parliament = member_of_parliament.lower()
    party = party.lower()

    # For the accents removal we use a function from the 'Preprocess_tools.py' file
    member_of_parliament  = Preprocess_tools.remove_accents(member_of_parliament)
    party = Preprocess_tools.remove_accents(party)

    # print(member_of_parliament, party)

    ###################################################################################################################

    # Καθώς δε γίνεται ο χρήστης να δίνει πάντα το ακριβές όνομα κάθε πολιτικού, υπάρχει η σκέψη να δέχεται ένα όνομα
    # και να βρίσκει έναν πολιτικό που περιέχει το όνομα αυτό και να βρίσκει keywords στις δικές του ομιλίες

    ###################################################################################################################


    # Fetch all the MPs from the table that have the 'member_of_parliament' name
    # and are from the 'party' political party
    # We should take into consideration that one of these strings can be empty
    if len(member_of_parliament) > 0 and len(party) > 0:
        c.execute(f'SELECT id, member_name, political_party, sitting_date, speech FROM {table_name} WHERE member_name=\'{member_of_parliament}\' and political_party=\'{party}\';')
    elif len(member_of_parliament) > 0:
        c.execute(f'SELECT id, member_name, political_party, sitting_date, speech FROM {table_name} WHERE member_name=\'{member_of_parliament}\';')
    elif len(party) > 0:
        c.execute(f'SELECT id, member_name, political_party, sitting_date, speech FROM {table_name} WHERE political_party=\'{party}\';')


    

    # Iterate each row of the database
    # In that way we do not store the bunch in the Main Memory but only one line each time
    speeches = ""
    for row in c:
        # In row[-1] contains the speech. The speech is not preprocessed
        speeches = speeches + row[-1]

    # Close the connection
    conn.close()

    keywords, cores = extract_keywords(speeches)

    if cores:
        num_dense_keywords = cores.count(max(cores))
        return keywords[:num_dense_keywords]
    else:
        return []

dense_keyword_extraction("κασιδιαρης παναγιωτη ηλιας", "")