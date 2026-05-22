from flask import Flask, request, jsonify, render_template
from ml_core.analyzer import analyze_journal_entry

# 1. Initialize our Flask Web Application
app = Flask(__name__)

# 2. Create a basic test route for the main web address
@app.route('/')
def home():
    # This renders the index.html file we just built inside the templates folder
    return render_template('index.html')

# 3. Create the API endpoint where our frontend will send the journal text
@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    
    if not data or 'entry' not in data:
        return jsonify({"error": "No journal entry text provided"}), 400
        
    user_entry = data['entry']
    
    # Pass the text over to our Phase 2 ML core to crunch the numbers
    ml_results = analyze_journal_entry(user_entry)
    
    return jsonify(ml_results)

# Start the local server on port 5001
if __name__ == '__main__':
    app.run(debug=True, port=5001)