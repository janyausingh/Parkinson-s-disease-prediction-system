from flask import Flask, render_template, request
import joblib

# Initialize the Flask app
app = Flask(__name__)

# Load the trained model
model = joblib.load("model.pkl")

@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    if request.method == "POST":
        try:
            # Replace with actual feature names from your form
            features = [
                float(request.form["mean"]),
                float(request.form["std"]),
                float(request.form["kurtosis"]),
                float(request.form["skewness"]),
                float(request.form["entropy"]),
            ]
            prediction = model.predict([features])[0]
            result = "✅ Parkinson's Detected" if prediction == 1 else "🧠 Healthy"
        except Exception as e:
            result = f"❌ Error: {e}"

    return render_template("index.html", result=result)

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
