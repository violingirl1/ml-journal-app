from flask import Flask, request, jsonify, render_template
from ml_core.analyzer import analyze_journal_entry
# Import our brand new database helper functions
from database import init_db, save_entry, get_all_entries

app = Flask(__name__)

# Initialize the database table right when the app turns on
init_db()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    if not data or 'entry' not in data:
        return jsonify({"error": "No journal entry text provided"}), 400
        
    user_entry = data['entry']
    
    # 1. Process the text using our ML script
    ml_results = analyze_journal_entry(user_entry)
    
    # 2. Persist the results into our SQLite database so they aren't lost
    save_entry(user_entry, ml_results['mood'], ml_results['score'], ml_results['tags'])
    
    return jsonify(ml_results)

# NEW ROUTE: Lets the frontend fetch the historical timeline of journal reflections
@app.route('/api/history', methods=['GET'])
def history():
    past_entries = get_all_entries()
    return jsonify(past_entries)

if __name__ == '__main__':
    app.run(debug=True, port=5002)