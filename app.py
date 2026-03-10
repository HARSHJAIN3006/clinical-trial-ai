from flask import Flask, request, render_template_string, redirect, url_for, session
import pandas as pd
import random
import os
import json

app = Flask(__name__)
app.secret_key = "trial_secret"
# User storage (for demo)
users = {}
otp_store = {}

# Load CSV database safely
base_path = os.path.dirname(__file__)
csv_path = os.path.join(base_path, "clinical_trials.csv")

trials = pd.read_csv(csv_path).to_dict(orient="records")
print(trials[0])

# Main HTML Page
html = """
<html>
<head>
<title>AI Clinical Trial Platform</title>
<p style="font-size:18px;margin-bottom:25px;">
AI-powered platform that connects patients with the most relevant clinical trials based on disease, location, and eligibility criteria.
</p>

<style>

body{
font-family:Arial;
background:linear-gradient(rgba(0,0,0,0.4),rgba(0,0,0,0.4)), url("/static/IMG.jpg");
background-size:cover;
background-position:center;
background-attachment:fixed;
color:white;
text-align:center;
padding:40px;
}

.container{
background:white;
color:black;
padding:30px;
border-radius:10px;
width:600px;
margin:auto;
}

input{
width:80%;
padding:10px;
margin:10px;
}

button{
padding:10px 20px;
background:#5c6bc0;
color:white;
border:none;
border-radius:5px;
}

.result{
margin-top:15px;
padding:15px;
background:#f4f4f4;
border-radius:5px;
text-align:left;
}

/* ---- Navbar styles ---- */

.navbar{
background:linear-gradient(90deg,#3949ab,#5c6bc0);
padding:15px;
margin-bottom:30px;
border-radius:12px;
display:flex;
justify-content:center;
gap:30px;
box-shadow:0px 4px 10px rgba(0,0,0,0.2);
}

.navbar a{
background:white;
color:#3949ab;
padding:10px 18px;
border-radius:25px;
text-decoration:none;
font-weight:bold;
font-size:16px;
transition:0.3s;
}

.navbar a:hover{
background:#e8eaf6;
transform:scale(1.05);
}
</style>

</head>

<body>

<div class="navbar">

<a href="/">🏠 Home</a>
<a href="/trials">🧪 Clinical Trials</a>
<a href="/dashboard">📊 Doctor Dashboard</a>
<a href="/logout">🚪 Logout</a>
</div>

<h1>AI Clinical Trial Matching Platform</h1>

<div class="container">

<h2>Patient Dashboard</h2>

<form method="POST">

<input type="text" name="name" placeholder="Patient Name" required>

<input type="number" name="age" placeholder="Patient Age" required>

<input type="text" name="disease" placeholder="Disease (example diabetes)" required>

<input type="text" name="location" placeholder="City (example mumbai)" required>

<input type="text" name="phase" placeholder="Trial Phase (Phase I / II / III / IV)" required>

<button type="submit">Search Clinical Trials</button>

</form>

{% if name %}
<h3>Welcome {{name}}</h3>
<h4>Matching Trials</h4>
{% endif %}
{% if not matches %}
<div style="background:#ffebee;color:#b71c1c;padding:12px;border-radius:6px;margin-top:15px;">
<b>No matching trials found.</b> Try changing disease or location.
</div>
{% endif %}

{% for trial in matches %}

<div class="result">

<b>Trial ID:</b> {{trial['trial_id']}} <br>
<b>Disease:</b> {{trial['disease']}} <br>
<b>Drug:</b> {{trial['drug']}} <br>
<b>Phase:</b> {{trial['phase']}} <br>
<b>Hospital:</b> {{trial['hospital']}} <br>
<b>Location:</b> {{trial['location']}} <br>
<b>AI Match Score:</b> {{trial['score']}} % <br>

</div>


{% endfor %}

</div>

<br>

<hr style="margin-top:40px">

<p style="font-size:14px;color:white;">
AI Clinical Trial Platform • Connecting Patients to Research • Made in INDIA by Indian
</p>

</body>
</html>
"""

# Patient Matching Route
@app.route("/signup", methods=["GET","POST"])
def signup():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        otp = str(random.randint(100000,999999))

        otp_store[email] = {
            "otp": otp,
            "password": password
        }

        print("OTP for demo:", otp)

        return redirect(url_for("verify_otp", email=email))

    return """
    <h1>Signup</h1>

    <form method="POST">

    Email:<br>
    <input name="email" required><br><br>

    Password:<br>
    <input type="password" name="password" required><br><br>

    <button type="submit">Send OTP</button>

    </form>

    <p>Already have account? <a href="/login">Login</a></p>
    """

@app.route("/verify/<email>", methods=["GET","POST"])
def verify_otp(email):

    if request.method == "POST":

        user_otp = request.form["otp"]

        if otp_store[email]["otp"] == user_otp:

            users[email] = otp_store[email]["password"]

            otp_store.pop(email)

            return redirect(url_for("login"))

        else:
            return "<h3>Invalid OTP</h3>"

    return f"""
    <h1>Enter OTP</h1>

    <p>OTP sent to {email}</p>

    <form method="POST">

    <input name="otp" placeholder="Enter OTP" required><br><br>

    <button type="submit">Verify OTP</button>

    </form>
    """
@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        if email in users and users[email] == password:

            session["user"] = email

            return redirect(url_for("home"))

        else:
            return "<h3>Invalid login credentials</h3>"

    return """
    <h1>Login</h1>

    <form method="POST">

    Email:<br>
    <input name="email" required><br><br>

    Password:<br>
    <input type="password" name="password" required><br><br>

    <button type="submit">Login</button>

    </form>

    <p>Don't have account? <a href="/signup">Signup</a></p>
    """
@app.route("/", methods=["GET","POST"])
def home():
    if "user" not in session:
        return redirect(url_for("login"))

    matches = []
    name = ""

    if request.method == "POST":

        name = request.form["name"]
        age = int(request.form["age"])
        disease = request.form["disease"].lower()
        location = request.form["location"].lower()
        phase = request.form["phase"].lower()

        for trial in trials:

            trial_disease = str(trial.get("disease","")).lower()
            trial_location = str(trial.get("location","")).lower()
            trial_phase = str(trial.get("phase","")).lower()

            age_min = int(trial.get("age_min",0))
            age_max = int(trial.get("age_max",120))

            score = 0

            if disease in trial_disease:
                score += 40

            if location in trial_location:
                score += 30

            if phase in trial_phase:
                score += 20

            if age_min <= age <= age_max:
                score += 10

            if score > 40:

                trial_copy = trial.copy()
                trial_copy["score"] = random.randint(80,98)

                matches.append(trial_copy)

        matches = matches[:5]

        session["matches"] = matches
        session["name"] = name

        return redirect(url_for("home"))

    matches = session.pop("matches", [])
    name = session.pop("name", "")

    return render_template_string(html, matches=matches, name=name)
# Clinical Trial Database Page
@app.route("/trials")
def trials_page():

    html_output = """
    <html>

    <head>

    <title>Clinical Trials Database</title>

    <style>

    body{
    font-family:Arial;
    background:#5c6bc0;
    padding:40px;
    }

    .container{
    width:900px;
    margin:auto;
    }

    .card{
    background:white;
    padding:20px;
    margin:20px;
    border-radius:10px;
    box-shadow:0px 0px 10px rgba(0,0,0,0.2);
    }

    h1{
    text-align:center;
    color:white;
    }

    .topbar{
    width:900px;
    margin:auto;
    margin-bottom:20px;
    }

    .homebtn{
    background:white;
    padding:10px 18px;
    border-radius:8px;
    text-decoration:none;
    font-weight:bold;
    color:#3949ab;
    }

    </style>

    </head>

    <body>

    <div class="topbar">
    <a href="/" class="homebtn">⬅ Back to Home</a>
    </div>

    <h1>Clinical Trials Database</h1>

    <div class="container">
    """

    for trial in trials:

        html_output += f"""
        <div class="card">

        <b>Trial ID:</b> {trial.get('trial_id','N/A')} <br><br>

        <b>Disease:</b> {trial.get('disease','N/A')} <br>

        <b>Drug:</b> {trial.get('drug','N/A')} <br>

        <b>Phase:</b> {trial.get('phase','N/A')} <br>

        <b>Location:</b> {trial.get('location','N/A')} <br>

        <b>Hospital:</b> {trial.get('hospital','N/A')}

        </div>
        """

    html_output += """
    </div>

    </body>

    </html>
    """

    return html_output


# ADD THIS BELOW
@app.route("/dashboard")
def dashboard():

    total_trials = len(trials)

    disease_count = {}
    phase_count = {}

    for trial in trials:

        disease = trial.get("disease","")
        phase = trial.get("phase","")

        disease_count[disease] = disease_count.get(disease,0) + 1
        phase_count[phase] = phase_count.get(phase,0) + 1

    return f"""
<html>
<head>
<title>Doctor Dashboard</title>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<style>

body{{
font-family:Arial;
background:#5c6bc0;
padding:40px;
text-align:center;
}}

.container{{
width:900px;
margin:auto;
}}

.card{{
background:white;
padding:20px;
margin:20px;
border-radius:10px;
box-shadow:0px 0px 10px rgba(0,0,0,0.2);
}}

h1{{
color:white;
}}

canvas{{
margin-top:20px;
}}

.topbar{{
width:900px;
margin:auto;
margin-bottom:20px;
text-align:left;
}}

.homebtn{{
background:white;
padding:10px 18px;
border-radius:8px;
text-decoration:none;
font-weight:bold;
color:#3949ab;
box-shadow:0px 0px 8px rgba(0,0,0,0.2);
}}

.homebtn:hover{{
background:#e8eaf6;
}}

</style>
</head>

<body>

<div class="topbar">
<a href="/" class="homebtn">⬅ Back to Home</a>
</div>

<h1>Doctor / Research Dashboard</h1>

<div class="container">

<div class="card">
<h2>Total Clinical Trials</h2>
<h3>{total_trials}</h3>
</div>

<div class="card">
<h2>Trials by Disease</h2>
<canvas id="diseaseChart"></canvas>
</div>

<div class="card">
<h2>Trials by Phase</h2>
<canvas id="phaseChart"></canvas>
</div>

</div>

<script>

var diseaseLabels = {list(disease_count.keys())};
var diseaseValues = {list(disease_count.values())};

var phaseLabels = {list(phase_count.keys())};
var phaseValues = {list(phase_count.values())};

new Chart(document.getElementById('diseaseChart'), {{
type: 'pie',
data: {{
labels: diseaseLabels,
datasets: [{{
data: diseaseValues
}}]
}}
}});

new Chart(document.getElementById('phaseChart'), {{
type: 'bar',
data: {{
labels: phaseLabels,
datasets: [{{
data: phaseValues
}}]
}}
}});

</script>

</body>
</html>
"""
# Run server
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)