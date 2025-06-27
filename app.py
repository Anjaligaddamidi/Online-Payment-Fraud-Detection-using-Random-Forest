from flask import Flask, request, render_template, redirect, url_for, session
import pandas as pd
import numpy as np
import os

app = Flask(__name__)
app.secret_key = "super_secret_key"  # Replace with a secure key in production

# Paths
USER_DB = "users.csv"

# Ensure user database exists
if not os.path.exists(USER_DB):
    pd.DataFrame(columns=["email", "password"]).to_csv(USER_DB, index=False)

# --- Route: Register ---
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        users = pd.read_csv(USER_DB)

        if email in users["email"].values:
            return render_template("register.html", error="Email already registered.")

        new_user = pd.DataFrame([[email, password]], columns=["email", "password"])
        new_user.to_csv(USER_DB, mode='a', header=False, index=False)
        return redirect(url_for("login"))

    return render_template("register.html")

# --- Route: Login ---
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"].strip()

        users = pd.read_csv(USER_DB)
        user = users[(users["email"] == email) & (users["password"] == password)]

        if not user.empty:
            session["user"] = email
            return redirect(url_for("predict"))
        else:
            return render_template("login.html", error="Invalid credentials.")
    return render_template("login.html")

# --- Route: Prediction (Rule-based logic only) ---
@app.route("/predict", methods=["GET", "POST"])
def predict():
    if "user" not in session:
        return redirect(url_for("login"))

    prediction = None

    if request.method == "POST":
        try:
            amount = float(request.form["amount"])
            oldbalanceOrg = float(request.form["oldbalanceOrg"])
            newbalanceOrig = float(request.form["newbalanceOrig"])

            # Rule-based fraud logic
            if (oldbalanceOrg - newbalanceOrig) == amount:
                prediction = "Legitimate"
            else:
                prediction = "Fraudulent"
        except Exception as e:
            prediction = f"Error: {e}"

    return render_template("predict.html", prediction=prediction)

# --- Route: Logout ---
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

# --- Run the app ---
if __name__ == "__main__":
    app.run(debug=True)
