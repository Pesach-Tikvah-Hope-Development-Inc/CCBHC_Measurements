from datetime import timedelta
from datetime import datetime
from dateutil.relativedelta import relativedelta
import random
import pandas as pd

random.seed(12345)
pop_size = 1000
encouters_per_patient = 20
scores = [1,2,3,4,5,6,7,8,9,10]
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
patient_id = random.sample(range(10_000,99_999),pop_size)
dob = [(datetime(1990, 1, 1) + timedelta(days=random.randint(0, (datetime(2020, 12, 31) - datetime(1990, 1, 1)).days))) for _ in range(pop_size)]

# make rand values for PHQ df
dob = dob*encouters_per_patient
encounter_patient_id = patient_id * encouters_per_patient
encounter_id = random.sample(range(10_000,99_999),k= pop_size * encouters_per_patient)
encounter_date = [(datetime(2024, 1, 1) + timedelta(days=random.randint(0, 365))) for _ in range(pop_size * encouters_per_patient)]
total_score = random.choices(scores,k=pop_size * encouters_per_patient)

# make rand values for Diagnosis
diagnosis_patient_id = random.choices(patient_id,k=100)
diagnosis_date = [(datetime(2024, 1, 1) + timedelta(days=random.randint(0, 365))) for _ in range(100)]
diagnosis = ["F34.0"]*100

# make rand values for Demograpics
race = random.choices(races,k=pop_size)
ethnicity = random.choices(ethnicities,k=pop_size)

# make rand values for insurance
insurance = random.choices(insurances,k=pop_size)
insurance_start_date = [(datetime(2023, 1, 1) + timedelta(days=random.randint(0, (datetime(2024, 12, 31) - datetime(2023, 1, 1)).days))) for _ in range(pop_size)]
insurance_end_date = [start + relativedelta(years=1) for start in insurance_start_date]


# create dataframes with repeatable values
phq_data = pd.DataFrame({
                    "patient_id":encounter_patient_id,
                    "patient_DOB":dob,
                    "encounter_id":encounter_id,
                    "encounter_datetime":encounter_date,
                    "total_score":total_score})
phq_data.patient_id = phq_data.patient_id.astype(str)
phq_data.total_score = phq_data.total_score.astype(int)
phq_data.encounter_id = phq_data.encounter_id.astype(str)

diagnosis_data = pd.DataFrame({
                    "patient_id":diagnosis_patient_id,
                    "encounter_datetime":diagnosis_date,
                    "diagnosis":diagnosis})
diagnosis_data.patient_id = diagnosis_data.patient_id.astype(str)

demographic_data = pd.DataFrame({
                    "patient_id":patient_id,
                    "race":race,
                    "ethnicity":ethnicity})
demographic_data.patient_id = demographic_data.patient_id.astype(str)

insurance_data = pd.DataFrame({
                    "patient_id":patient_id,
                    "insurance":insurance,
                    "start_datetime":insurance_start_date,
                    "end_datetime":insurance_end_date,})
insurance_data.patient_id = insurance_data.patient_id.astype(str)

data = [phq_data, diagnosis_data, demographic_data, insurance_data]