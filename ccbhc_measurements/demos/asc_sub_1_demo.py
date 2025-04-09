from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
import random
import pandas as pd

random.seed(12345)
pop_size = 1000
encouters_per_patient = 20
preventive_visits = 10
screenings = 250
cpt_codes = [
    '99385',
    '99386',
    '99387',
    '99395',
    '99396',
    '99397'
]
screening_types = [
    "audit",
    "audit-c",
    "single question screening"
]
races = [
    "White",
    "Black",
    "Indian",
    "Unknown"
    ]
ethnicities = [
    "Not Hispanic",
    "Hispanic",
    "Unknown"
    ]
insurances = [
    "Blue Cross Blue Shield",
    "UnitedHealthcare",
    "Medicare",
    "Medicaid"
    ]
# create random patient data
patient_id = random.sample(range(10_000,99_999),pop_size)
dob = [(datetime(1990, 1, 1) + timedelta(days=random.randint(0, (datetime(2020, 12, 31) - datetime(1990, 1, 1)).days))) for _ in range(pop_size)]
# create random encounter data
encounter_patient_ids = patient_id * encouters_per_patient
encounter_dobs = dob*encouters_per_patient
encounter_id = random.sample(range(10_000,99_999),k= (pop_size) * encouters_per_patient)
encounter_date = [(datetime(2024, 1, 1) + timedelta(days=random.randint(0, 365))) for _ in range((pop_size) * encouters_per_patient)]
# set 10 random visits as preventitive
encounter_cpt_code = ['dummy_cpt'] * len(encounter_patient_ids)
for num in range(preventive_visits):
    index = random.randint(0,len(encounter_cpt_code))
    encounter_cpt_code[index] = random.choices(cpt_codes)
# set counselings
for num in range(375):
    index = random.randint(0,len(encounter_id))
    encounter_cpt_code[index] = 'G2200'
# set random visits as screenings
screening_type = [None] * len(encounter_patient_ids)
score = [None] * len(encounter_patient_ids)
for num in range(screenings):
    index = random.randint(0,len(screening_type))
    screening_type[index] = random.choices(screening_types).pop()
    score[index] = random.randint(0,10)
# make rand values for Diagnosis
diagnosis_patient_id = random.sample(patient_id,k=100)
diagnosis_date = [(datetime(2024, 1, 1) + timedelta(days=random.randint(0, 365))) for _ in range(100)]
diagnosis = ["F01.B2","F02.83","F03.C4","Dummy Diagnosis"] * 25

# make rand values for Demograpics
race = random.choices(races,k=pop_size)
ethnicity = random.choices(ethnicities,k=pop_size)

# make rand values for insurance
insurance = random.choices(insurances,k=pop_size)
insurance_start_date = [(datetime(2023, 1, 1) + timedelta(days=random.randint(0, (datetime(2024, 12, 31) - datetime(2023, 1, 1)).days))) for _ in range(pop_size)]
insurance_end_date = [start + relativedelta(years=1) for start in insurance_start_date]

encounter_data = pd.DataFrame({
    "patient_id":encounter_patient_ids,
    "patient_DOB":encounter_dobs,
    "encounter_id":encounter_id,
    "encounter_datetime":encounter_date,
    "cpt_code":encounter_cpt_code,
    "screening":screening_type,
    "score":score
    }
)
encounter_data['patient_id'] = encounter_data['patient_id'].astype(str)
encounter_data['encounter_id'] = encounter_data['encounter_id'].astype(str)

diagnosis_data = pd.DataFrame({
                    "patient_id":diagnosis_patient_id,
                    "encounter_datetime":diagnosis_date,
                    "diagnosis":diagnosis})
diagnosis_data.patient_id = diagnosis_data.patient_id.astype(str)

sex = random.choices(["male","female"],k=pop_size)
demographic_data = pd.DataFrame({
                    "patient_id":patient_id,
                    "sex":sex,
                    "race":race,
                    "ethnicity":ethnicity})
demographic_data.patient_id = demographic_data.patient_id.astype(str)

insurance_data = pd.DataFrame({
                    "patient_id":patient_id,
                    "insurance":insurance,
                    "start_datetime":insurance_start_date,
                    "end_datetime":insurance_end_date,})
insurance_data.patient_id = insurance_data.patient_id.astype(str)

data = [encounter_data, diagnosis_data, demographic_data, insurance_data]
