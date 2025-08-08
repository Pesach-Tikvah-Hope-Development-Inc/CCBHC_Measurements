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
diagnoses_list = ["depression", "bipolar"]

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
