from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from ml_core.analyzer import analyze_journal_entry
from database import init_db, save_entry, get_user_entries, create_user, verify_user

app = Flask(__name__)
app.secret_key = "super_secret_pastel_vibe_key" # Needed for cookie session encryption

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_page'

init_db()

# Simple User class for Session tracking
class User(UserMixin):
    def __init__(self, user_dict):
        self.id = user_dict['id']
        self.username = user_dict['username']

@login_manager.user_loader
def load_user(user_id):
    import sqlite3
    conn = sqlite3.connect("journal.db")
    cursor = conn.cursor()
    cursor.execute('SELECT id, username FROM users WHERE id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return User({"id": row[0], "username": row[1]})
    return None

# --- ROUTING PAGES ---

@app.route('/')
@login_required
def home():
    return render_template('index.html', username=current_user.username)

@app.route('/login')
def login_page():
    return render_template('login.html')

# --- AUTH API ENDPOINTS ---

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "Missing credentials"}), 400
    
    success = create_user(data['username'], data['password'])
    if success:
        return jsonify({"message": "Account created! Now login."})
    return jsonify({"error": "Username already exists, bud."}), 400

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user_data = verify_user(data['username'], data['password'])
    
    if user_data:
        user_obj = User(user_data)
        login_user(user_obj, remember=True) # "remember=True" keeps them logged in!
        return jsonify({"message": "Logged in successfully!"})
    return jsonify({"error": "Invalid username or password"}), 401

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login_page'))

# --- JOURNAL API ENDPOINTS (SECURED) ---

@app.route('/api/analyze', methods=['POST'])
@login_required
def analyze():
    data = request.get_json()
    user_entry = data['entry']
    
    ml_results = analyze_journal_entry(user_entry)
    
    # Link the entry directly to the currently logged in user's ID
    save_entry(current_user.id, user_entry, ml_results['mood'], ml_results['score'], ml_results['tags'])
    return jsonify(ml_results)

@app.route('/api/history', methods=['GET'])
@login_required
def history():
    past_entries = get_user_entries(current_user.id)
    return jsonify(past_entries)

if __name__ == '__main__':
    app.run(debug=True, port=5002)