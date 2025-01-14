import heapq
from flask import Flask, render_template, request, jsonify
import sqlite3
from Inverted_Index import InvertedIndex

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    if query:
        # Get records from the database
        results = get_records(query)
        
        # Return results as a list of lists (each record is a list of column values)
        return jsonify(results)
    
    return jsonify({'error': 'No query provided'}), 400

@app.route('/full-text/<int:id>')
def full_text(id):
    # Fetch the full record from the database
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT speech FROM unfiltered_records WHERE id = ?", (id,))
    record = cursor.fetchone()
    conn.close()
    if record:
        return render_template('full_text.html', text=record[0])
    else:
        return "Record not found", 404

def get_records(query):

    # Path to the csv file
    input_file = "Greek_Parliament_Proceedings_1989_2020.csv"

    # Initialize the InvertedIndex class
    inverted_index = InvertedIndex()

    print(f"started loading catalog")
    inverted_index.load_index("inverted_index.pkl")
    inverted_index.num_of_docs = 706801 

    heap_ids = inverted_index.search_query(query)


    ranked = []
    for i in range(min(20, len(heap_ids))):
        score, id = heapq.heappop(heap_ids)
        ranked.append(id)
        

    # Open a connection to the SQLite database
    conn = sqlite3.connect('data.db') 
    cursor = conn.cursor()

    placeholders = ', '.join(['?'] * len(ranked))
    sql_query = f"SELECT * FROM unfiltered_records WHERE id IN ({placeholders})"
    cursor.execute(sql_query, ranked)

    results = cursor.fetchall()
    
    # Close the connection
    conn.close()


    id_index = {id_val: idx for idx, id_val in enumerate(ranked)}

    # Sort results based on the order in id_order
    sorted_results = sorted(results, key=lambda x: id_index[x[0]])

    return sorted_results

if __name__ == '__main__':
    app.run(debug=True)

