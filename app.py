from flask import Flask, render_template, request, redirect, url_for, session
import joblib
import sqlite3
import warnings
from werkzeug.security import generate_password_hash, check_password_hash

# Suppress joblib/sklearn warnings
warnings.filterwarnings("ignore", category=UserWarning)

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Replace this with a secure key in production

# Load the trained model
model = joblib.load("model.pkl")

# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------------- ROUTES ---------------- #

@app.route("/")
def landing():
    return render_template("landing.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    msg = ""
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            msg = "❌ Username already exists."
        finally:
            conn.close()
    return render_template("signup.html", msg=msg)

@app.route("/login", methods=["GET", "POST"])
def login():
    msg = ""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[0], password):
            session["user"] = username
            return redirect(url_for("predict"))
        else:
            msg = "❌ Invalid credentials."
    return render_template("login.html", msg=msg)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

@app.route("/predict", methods=["GET", "POST"])
def predict():
    if "user" not in session:
        return redirect(url_for("login"))

    result = None
    error = None

    if request.method == "POST":
        try:
            features = [
                float(request.form["mean"]),
                float(request.form["std"]),
                float(request.form["kurtosis"]),
                float(request.form["skewness"]),
                float(request.form["entropy"])
            ]
            prediction = model.predict([features])[0]
            result = "✅ Parkinson's Detected" if prediction == 1 else "🧠 Healthy"
        except Exception as e:
            error = f"❌ Error: {e}"

    return render_template("index.html", result=result, error=error)

# ----------------------------------------- #

if __name__ == "__main__":
    app.run(debug=True)
