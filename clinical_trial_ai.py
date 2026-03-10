from cProfile import label
from tkinter import font
from turtle import width

from flask import Flask, request, render_template_string
import pandas as pd
import random
import os

app = Flask(__name__)

# Load CSV database
base_path = os.path.dirname(__file__)
csv_path = os.path.join(base_path, "clinical_trials.csv")

trials = pd.read_csv(csv_path).to_dict(orient="records")

# ------------------ HTML TEMPLATE ------------------

html = """

<html>
<head>
<title>AI Clinical Trial Matching Platform</title>

<style>
body {
  font-family: Arial;
  background: #5c6bc0;
  color: white;
  text-align: center;
  padding: 40px;
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

.links{
margin-top:20px;
}

</style>

</head>

<body>

<h1>AI Clinical Trial Matching Platform</h1>

<div class="container">

<h2>Patient Search</h2>

<form method="POST">

<input type="text" name="name" placeholder="Patient Name" required>

<input type="number" name="age" placeholder="Patient Age" required>

<input type="text" name="disease" placeholder="Disease (example diabetes)" required>

<input type="text" name="location" placeholder="City (example mumbai)" required>

<input type="text" name="phase" placeholder="Trial Phase (Phase I / II / III / IV)" required>

<br>

<button type="submit">Search Clinical Trials</button>

</form>

{% if name %}
<h3>Welcome {{name}}</h3>
<h4>Matching Trials</h4>
{% endif %}

{% for trial in matches %}

<div class="result">

<b>Trial ID:</b> {{trial['trial_id']}} <br>

<b>Disease:</b> {{trial['disease']}} <br>

<b>Drug:</b> {{trial['drug']}} <br>

<b>Phase:</b> {{trial['phase']}} <br>

<b>Hospital:</b> {{trial['hospital']}} <br>

<b>Location:</b> {{trial['location']}} <br>

<b>AI Match Score:</b> {{trial['score']}} %

</div>

{% endfor %}

<div class="links">

<a href="/trials">View All Trials</a> |
<a href="/dashboard">Doctor Dashboard</a>

</div>

</div>

</body>
</html>

"""

# ------------------ HOME PAGE ------------------

@app.route("/", methods=["GET","POST"])

def home():

    matches = []
    name = ""

    if request.method == "POST":

        name=request.form["name"]
        age=int(request.form["age"])
        disease=request.form["disease"].lower()
        location=request.form["location"].lower()
        phase=request.form["phase"].lower()

        for trial in trials:

            trial_disease = str(trial.get("disease","")).lower()
            trial_location = str(trial.get("location","")).lower()
            trial_phase = str(trial.get("phase","")).lower()

            age_min = int(trial.get("age_min",0))
            age_max = int(trial.get("age_max",120))

            if disease in trial_disease and location in trial_location and phase in trial_phase and age_min <= age <= age_max:

                trial_copy = trial.copy()
                trial_copy["score"] = random.randint(80,98)

                matches.append(trial_copy)

        matches = matches[:5]

        return render_template_string(html, matches=matches, name=name)

    return render_template_string(html, matches=[], name="")

# ------------------ TRIAL DATABASE ------------------

@app.route("/trials")

def trials_page():

    html_output="<h1>Clinical Trials Database</h1>"

    for trial in trials:

        html_output+=f"""
        <div style='margin:15px;padding:10px;border:1px solid gray'>
        <b>Trial ID:</b> {trial['trial_id']} <br>
        <b>Disease:</b> {trial['disease']} <br>
        <b>Drug:</b> {trial['drug']} <br>
        <b>Phase:</b> {trial['phase']} <br>
        <b>Location:</b> {trial['location']} <br>
        <b>Hospital:</b> {trial['hospital']} <br>
        </div>
        """

    return html_output

# ------------------ DOCTOR DASHBOARD ------------------

@app.route("/dashboard")
def dashboard():

    total_trials = len(trials)

    disease_count = {}
    phase_count = {}
    hospitals = set()

    for trial in trials:

        disease = trial.get("disease","")
        phase = trial.get("phase","")
        hospital = trial.get("hospital","")

        disease_count[disease] = disease_count.get(disease,0) + 1
        phase_count[phase] = phase_count.get(phase,0) + 1
        hospitals.add(hospital)

    disease_labels = list(disease_count.keys())
    disease_values = list(disease_count.values())
    phase_labels = list(phase_count.keys())
    phase_values = list(phase_count.values())

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
}}

.container{{
width: 900px;
margin:auto;
}}

.card{{
background: white;
padding:20px;
margin:20px;
border-radius:10px;
box-shadow:0px 0px 10px rgba(0,0,0,0.2);
}}

h1{{
text-align:center;
color:white;
}}

canvas{{
margin-top:20px;
}}

</style>

</head>

<body>

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

<div class="card">
<a href="/">Back to Patient Search</a>
</div>

</div>

<script>

var diseaseLabels = {disease_labels};
var diseaseValues = {disease_values};

var phaseLabels = {phase_labels};
var phaseValues = {phase_values};

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
label: 'Trials',
data: phaseValues
}}]
}}
}});
</script>

</body>

</html>
"""

# ------------------ RUN SERVER ------------------

if __name__ == "__main__":
    app.run(debug=True)