from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
import random
import pandas as pd

random.seed(12345)

pop_size = 30
encounters_per_patient = 4
screenings_count = 8  # number of screening records


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
    "test ins",
    "life on insurance",
    "in health",
    "fidelis medicaid"
]
patient_ids = random.sample(range(10_000, 99_999), pop_size)
dob = [datetime(1990, 1, 1) + timedelta(days=random.randint(0, (datetime(2020, 12, 31) - datetime(1990, 1, 1)).days)) for _ in range(pop_size)]

# --- Populace ---
encounter_patient_ids = patient_ids * encounters_per_patient
encounter_dobs = dob * encounters_per_patient
encounter_ids = random.sample(range(10_000, 99_999), k=pop_size * encounters_per_patient)
encounter_dates = [datetime(2024, 1, 1) + timedelta(days=random.randint(0, 365)) for _ in range(pop_size * encounters_per_patient)]

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

# --- SDOH_Screenings ---
screening_patient_ids = random.choices(patient_ids, k=screenings_count)
screening_ids = random.sample(range(100000, 999999), screenings_count)
screening_dates = [datetime(2024, 1, 1) + timedelta(days=random.randint(0, 365)) for _ in range(screenings_count)]
screening_data = pd.DataFrame({
    "patient_id": screening_patient_ids,
    "screening_id": [str(sid) for sid in screening_ids],
    "screening_date": screening_dates
})
screening_data['patient_id'] = screening_data['patient_id'].astype(str)
screening_data['screening_id'] = screening_data['screening_id'].astype(str)
screening_data['screening_date'] = pd.to_datetime(screening_data['screening_date'])

# --- Demographic_Data ---
demographic_races = random.choices(races, k=pop_size)
demographic_ethnicities = random.choices(ethnicities, k=pop_size)
demographic_data = pd.DataFrame({
    "patient_id": patient_ids,
    "race": demographic_races,
    "ethnicity": demographic_ethnicities
})
demographic_data['patient_id'] = demographic_data['patient_id'].astype(str)

# --- Insurance_History ---
insurance_choices = random.choices(insurances, k=pop_size)
insurance_start_dates = [
    datetime(2023, 1, 1) + timedelta(days=random.randint(0, (datetime(2024, 12, 31) - datetime(2023, 1, 1)).days))
    for _ in range(pop_size)
]
insurance_end_dates = [start + relativedelta(years=1) for start in insurance_start_dates]
insurance_data = pd.DataFrame({
    "patient_id": patient_ids,
    "insurance": insurance_choices,
    "start_datetime": insurance_start_dates,
    "end_datetime": insurance_end_dates
})
insurance_data['patient_id'] = insurance_data['patient_id'].astype(str)
insurance_data['start_datetime'] = pd.to_datetime(insurance_data['start_datetime'])
insurance_data['end_datetime'] = pd.to_datetime(insurance_data['end_datetime'])

data = [encounter_data, screening_data, demographic_data, insurance_data]