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
diagnoses_list = bipolar_codes

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

populace['follow_up'] = random.choices([True, False], k=len(populace))
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

# --- Screenings (for merging into populace) ---
screened = populace.sample(n=screenings_count, replace=False,random_state=12345).assign(
    screening_type = lambda df: random.choices(['PHQ9','PHQA','PSC-17'], k=len(df)),
    total_score    = lambda df: [random.randint(0,15) for _ in df.index],
    # screening_date = lambda df: df['encounter_datetime']
)
populace = populace.merge(
    screened[['patient_id','encounter_id','total_score','screening_type']],
    on=['patient_id','encounter_id'],
    how='left'
)

# populace['follow_up'] = random.choices([True, False], k=len(populace))

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

CDF_CH_sub_1_data = [
    populace,
    diagnostic_history,
    demographic_data,
    insurance_history
]
