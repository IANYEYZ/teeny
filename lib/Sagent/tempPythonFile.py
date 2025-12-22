import sqlite3
import random
from datetime import datetime, timedelta

DB_FILE = "medical_system.db"
conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()

cur.executescript("""
DROP TABLE IF EXISTS patients;
CREATE TABLE patients (
    id INTEGER PRIMARY KEY,
    name TEXT,
    gender TEXT,
    age INTEGER,
    symptom TEXT,
    department TEXT,
    doctor TEXT,
    appointment_date TEXT,
    status TEXT
);
""")

# --- Expanded name pools ---
first_names_m = [
    "James", "John", "Robert", "Michael", "David", "William", "Richard", "Joseph",
    "Thomas", "Charles", "Christopher", "Daniel", "Matthew", "Anthony", "Mark",
    "Donald", "Steven", "Paul", "Andrew", "Joshua", "Kenneth", "Kevin", "Brian",
    "George", "Edward", "Ronald", "Timothy", "Jason", "Jeffrey", "Ryan", "Jacob",
    "Gary", "Nicholas", "Eric", "Jonathan", "Stephen", "Larry", "Justin", "Scott",
]

first_names_f = [
    "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan",
    "Jessica", "Sarah", "Karen", "Nancy", "Lisa", "Margaret", "Betty", "Sandra",
    "Ashley", "Dorothy", "Kimberly", "Emily", "Donna", "Michelle", "Carol",
    "Amanda", "Melissa", "Deborah", "Stephanie", "Rebecca", "Laura", "Helen",
    "Sharon", "Cynthia", "Kathleen", "Amy", "Shirley", "Angela", "Anna", "Brenda",
]

last_names = [
    "Smith", "Johnson", "Brown", "Taylor", "Anderson", "Thomas", "Jackson", "White",
    "Harris", "Martin", "Thompson", "Garcia", "Martinez", "Robinson", "Clark",
    "Rodriguez", "Lewis", "Lee", "Walker", "Hall", "Allen", "Young", "King",
    "Wright", "Scott", "Torres", "Nguyen", "Hill", "Green", "Adams", "Nelson",
    "Baker", "Campbell", "Perez", "Mitchell", "Roberts", "Carter", "Phillips",
    "Evans", "Turner", "Parker", "Collins", "Edwards", "Stewart", "Sanchez",
]

departments = {
    "Cardiology": ["chest pain", "palpitations", "shortness of breath", "fatigue"],
    "Neurology": ["headache", "dizziness", "seizure", "numbness"],
    "Pediatrics": ["fever", "cough", "sore throat", "vomiting"],
    "Dermatology": ["rash", "itching", "skin irritation", "acne"],
    "Orthopedics": ["back pain", "joint pain", "fracture", "sprain"],
    "Ophthalmology": ["blurred vision", "eye pain", "redness", "dry eyes"],
    "ENT": ["ear pain", "hearing loss", "nasal congestion", "sore throat"],
    "Gastroenterology": ["stomach pain", "nausea", "diarrhea", "heartburn"],
}

status_choices = ["waiting", "in progress", "done", "cancelled"]

# --- Helpers ---
def random_name(gender):
    first = random.choice(first_names_m if gender == "Male" else first_names_f)
    last = random.choice(last_names)
    return f"{first} {last}"

def random_doctor(dept):
    return f"Dr. {random.choice(last_names)}"

def random_date():
    d = datetime.now() - timedelta(days=random.randint(0, 30))
    return d.strftime("%Y-%m-%d")

# --- Generate & insert data ---
patients = []
for i in range(100):
    gender = random.choice(["Male", "Female"])
    age = random.randint(1, 90)
    dept = random.choice(list(departments.keys()))
    symptom = random.choice(departments[dept])
    doctor = random_doctor(dept)
    appointment = random_date()
    status = random.choice(status_choices)
    name = random_name(gender)

    patients.append((name, gender, age, symptom, dept, doctor, appointment, status))

cur.executemany("""
INSERT INTO patients (name, gender, age, symptom, department, doctor, appointment_date, status)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", patients)

conn.commit()
conn.close()

print(f"✅ Inserted {len(patients)} fake patients with varied names into {DB_FILE}")
