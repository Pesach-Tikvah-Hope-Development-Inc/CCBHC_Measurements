from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
import random
import pandas as pd

random.seed(12345)
pop_size = 30
encounters_per_patient = 18
screenings_count = 18
diagnostics_count = 25
races = [
    "White",
    "Other Race",
    "Black or African American",
    "American Indian or Alaska Native",
    "Native Hawaiian or Other Pacific Islander",
    "Asian"
]
ethnicities = [
    "Not Hispanic or Latino",
    "Hispanic or Latino"
]
insurances = [
    "united aetna payer",
    "medicaid",
    "life on insurance",
    "united healthcare medicaid",
    "in health",
    "self pay",
    "fidelis medicaid",
    "bc/bs (healthplus) medicaid"
    "cigna (pvt)"
]
# actual ICD-10 code sets
depression_codes = [
    'F01.51',
    'F32.A','F32.0','F32.1','F32.2','F32.3','F32.4','F32.5','F32.89','F32.9',
    'F33.0','F33.1','F33.2','F33.3','F33.40','F33.41','F33.42','F33.8','F33.9',
    'F34.1','F34.81','F34.89',
    'F43.21','F43.23',
    'F53.0','F53.1',
    'O90.6',
    'O99.340','O99.341','O99.342','O99.343','O99.345'
]
bipolar_codes = [
    'F31.10','F31.11','F31.12','F31.13',
    'F31.2',
    'F31.30','F31.31','F31.32',
    'F31.4','F31.5',
    'F31.60','F31.61','F31.62','F31.63','F31.64',
    'F31.70','F31.71','F31.72','F31.73','F31.74','F31.75','F31.76','F31.77','F31.78',
    'F31.81','F31.89',
    'F31.9'
]
diagnoses_list = depression_codes + bipolar_codes
patient_ids = random.sample(range(10_000, 99_999), pop_size)
dob = [
    datetime(1990, 1, 1) + timedelta(
        days=random.randint(0, (datetime(2020, 12, 31) - datetime(1990, 1, 1)).days)
    )
    for _ in range(pop_size)
]

# --- Populace ---
encounter_patient_ids = patient_ids * encounters_per_patient
encounter_dobs = dob * encounters_per_patient
encounter_ids = random.sample(range(10_000, 99_999), k=pop_size * encounters_per_patient)
encounter_dates = [
    datetime(2024, 1, 1) + timedelta(days=random.randint(0, 365))
    for _ in range(pop_size * encounters_per_patient)
]
encounter_data = pd.DataFrame({
    "patient_id": encounter_patient_ids,
    "patient_DOB": encounter_dobs,
    "encounter_id": encounter_ids,
    "encounter_datetime": encounter_dates,
})
encounter_data['patient_id'] = encounter_data['patient_id'].astype(str)
encounter_data['encounter_id'] = encounter_data['encounter_id'].astype(str)
encounter_data['encounter_datetime'] = pd.to_datetime(encounter_data['encounter_datetime'])
encounter_data['patient_DOB'] = pd.to_datetime(encounter_data['patient_DOB'])
populace = encounter_data[['patient_id', 'encounter_id', 'encounter_datetime', 'patient_DOB']].copy()

# --- Diagnostic_History ---
diagnostic_patient_ids = random.choices(patient_ids, k=diagnostics_count)
diagnostic_encounter_dates = [
    datetime(2024, 1, 1) + timedelta(days=random.randint(0, 365))
    for _ in range(diagnostics_count)
]
diagnoses = random.choices(diagnoses_list, k=diagnostics_count)
diagnostic_history = pd.DataFrame({
    "patient_id": [str(pid) for pid in diagnostic_patient_ids],
    "encounter_datetime": diagnostic_encounter_dates,
    "diagnosis": diagnoses
})
diagnostic_history['encounter_datetime'] = pd.to_datetime(diagnostic_history['encounter_datetime'])

# --- CDF_Screenings ---
screening_patient_ids = random.choices(patient_ids, k=screenings_count)
screening_encounter_ids = random.sample(range(10_000, 99_999), k=screenings_count)
screening_dates = [
    datetime(2024, 1, 1) + timedelta(days=random.randint(0, 365))
    for _ in range(screenings_count)
]
total_scores = [random.randint(0, 15) for _ in range(screenings_count)]
cdf_screenings = pd.DataFrame({
    "patient_id": [str(pid) for pid in screening_patient_ids],
    "encounter_id": [str(eid) for eid in screening_encounter_ids],
    "screening_date": screening_dates,
    "total_score": [float(x) for x in total_scores]

})
cdf_screenings['screening_date'] = pd.to_datetime(cdf_screenings['screening_date'])

# --- Demographic_Data ---
demographic_races = random.choices(races, k=pop_size)
demographic_ethnicities = random.choices(ethnicities, k=pop_size)
demographic_data = pd.DataFrame({
    "patient_id": [str(pid) for pid in patient_ids],
    "race": demographic_races,
    "ethnicity": demographic_ethnicities
})

# --- Insurance_History ---
insurance_choices = random.choices(insurances, k=pop_size)
insurance_start_dates = [
    datetime(2023, 1, 1) + timedelta(
        days=random.randint(0, (datetime(2024, 12, 31) - datetime(2023, 1, 1)).days)
    )
    for _ in range(pop_size)
]
insurance_end_dates = [start + relativedelta(years=1) for start in insurance_start_dates]
insurance_history = pd.DataFrame({
    "patient_id": [str(pid) for pid in patient_ids],
    "insurance": insurance_choices,
    "start_datetime": insurance_start_dates,
    "end_datetime": insurance_end_dates
})
insurance_history['start_datetime'] = pd.to_datetime(insurance_history['start_datetime'])
insurance_history['end_datetime'] = pd.to_datetime(insurance_history['end_datetime'])

data = [
    populace,
    diagnostic_history,
    cdf_screenings,
    demographic_data,
    insurance_history
]
