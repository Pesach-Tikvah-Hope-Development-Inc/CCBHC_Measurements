from datetime import timedelta
from datetime import datetime
from dateutil.relativedelta import relativedelta
import random
import pandas as pd

random.seed(12345)
pop_size = 1000
preventitive_patients = 20
encouters_per_patient = 20
cpt_codes = [
    '99385', '99386', '99387', '99395', '99396','99397', # preventive cpts
    '12345', '67890' # dummy cpts
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
patient_id = random.sample(range(10_000,99_999),pop_size - preventitive_patients)
dob = [(datetime(1990, 1, 1) + timedelta(days=random.randint(0, (datetime(2020, 12, 31) - datetime(1990, 1, 1)).days))) for _ in range(pop_size - preventitive_patients)]

# make rand values for visits df
visits_patient_id = patient_id * encouters_per_patient
dob = dob*encouters_per_patient
encounter_id = random.sample(range(10_000,99_999),k= (pop_size - preventitive_patients) * encouters_per_patient)
encounter_date = [(datetime(2024, 1, 1) + timedelta(days=random.randint(0, 365))) for _ in range((pop_size - preventitive_patients) * encouters_per_patient)]

# make rand values preventitive visits
preventitive_patient_id = random.sample(range(1_000,9_999),preventitive_patients)
preventitive_dob = [(datetime(1990, 1, 1) + timedelta(days=random.randint(0, (datetime(2020, 12, 31) - datetime(1990, 1, 1)).days))) for _ in range(preventitive_patients)]
preventitive_encounter_id = random.sample(range(1_000,9_999),k= preventitive_patients)
preventitive_encounter_date = [(datetime(2024, 1, 1) + timedelta(days=random.randint(0, 365))) for _ in range(preventitive_patients)]
preventitive_cpt_code = random.choices(cpt_codes,k=preventitive_patients)

# make rand values for screenings
screening_ids = patient_id + preventitive_patient_id
screening_datetime = [(datetime(2023, 1, 1) + timedelta(days=random.randint(0, 1095))) for _ in range(pop_size)]

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


visits = pd.DataFrame({
    "patient_id":visits_patient_id,
    "patient_DOB":dob,
    "encounter_id":encounter_id,
    "encounter_datetime":encounter_date
})
visits.patient_id = visits.patient_id.astype(str)
visits.encounter_id = visits.encounter_id.astype(str)

preventitive_visits = pd.DataFrame({
    "patient_id":preventitive_patient_id,
    "patient_DOB":preventitive_dob,
    "encounter_id":preventitive_encounter_id,
    "encounter_datetime":preventitive_encounter_date,
    "cpt_code" : preventitive_cpt_code
})
preventitive_visits.patient_id = preventitive_visits.patient_id.astype(str)
preventitive_visits.encounter_id = preventitive_visits.encounter_id.astype(str)

screenings = pd.DataFrame({
    "patient_id":screening_ids,
    "screening_datetime":screening_datetime
})
screenings.patient_id = screenings.patient_id.astype(str)

diagnosis_data = pd.DataFrame({
                    "patient_id":diagnosis_patient_id,
                    "encounter_datetime":diagnosis_date,
                    "diagnosis":diagnosis})
diagnosis_data.patient_id = diagnosis_data.patient_id.astype(str)

demographic_data = pd.DataFrame({
                    "patient_id":patient_id + preventitive_patient_id,
                    "race":race,
                    "ethnicity":ethnicity})
demographic_data.patient_id = demographic_data.patient_id.astype(str)

insurance_data = pd.DataFrame({
                    "patient_id":patient_id + preventitive_patient_id,
                    "insurance":insurance,
                    "start_datetime":insurance_start_date,
                    "end_datetime":insurance_end_date,})
insurance_data.patient_id = insurance_data.patient_id.astype(str)

data = [visits, preventitive_visits, screenings, diagnosis_data, demographic_data, insurance_data]
