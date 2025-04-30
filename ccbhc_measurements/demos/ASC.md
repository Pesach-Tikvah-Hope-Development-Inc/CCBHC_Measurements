# Alchohol Screening & Counseling (ASC)

## Table of Contents

- [Measurement Definition](#measurement-definition)
- [Required Data](#required-data)
- [Output Data](#output-data)
- [Code Demonstration](#code-demonstration)
- [Notes](#notes)

## Measurement Definition

The ASC measure calculates the Percentage of clients aged 18 years and older who were
screened for unhealthy alcohol use using a Systematic Screening Method at least once within the
last 12 months AND who received brief counseling if identified as an unhealthy alcohol user

[Click here to see SAMHSA's definitions](https://www.samhsa.gov/sites/default/files/ccbhc-quality-measures-technical-specifications-manual.pdf)

### SubMeasure 1

Percentage of clients aged 18 years and older who were screened for unhealthy alcohol use
using a Systematic Screening Method at least once within the last 12 months

### SubMeasure 2

Percentage of clients aged 18 years and older who were identified as unhealthy alcohol users
(in submeasure #1) who received Brief Counseling

## Required Data

[Click here to see the Input and Output Diagram](https://github.com/Pesach-Tikvah-Hope-Development-Inc/CCBHC_Measurements/blob/main/ccbhc_measurements/diagrams/ASC%20Input%20Output%20Requirements.pdf)

### SubMeasure 1

The following dataframes are required to calculate the ASC SubMeasure 1
- Encounters
- Diagnoses
- Demographic Data
- Insurance History

#### Encounters

The encounters dataframe must have the following columns and datatypes
- patient_id : str - Unique Patient Identifier
- patient_DOB : datetime64[ns] - Patients' Date of Birth
- encounter_id : str - Unique Visit Identifier (duplicates allowed for multiple CPT codes)
- encounter_datetime : datetime64[ns] - Date of visit
- cpt_code : str - A single CPT code (for more than one CPT code use separate lines and duplicate the rest of the information)
- screening : str - Type of systemactic screening used or blank if the encounter was not a screening
- score : int - Sscreening score or blank if the encounter was not a screening

#### Diagnosis

The diagnosis dataframe must have the following columns and datatypes
- patient_id : str - Unique Patient Identifier
- encounter_datetime : datetime64[ns] - Date of visit
- diagnosis : str - ICD10 Code to determine whether patients are excluded from the measure (for encounters with mulitple diagnoses, duplicate the entire line and change the ICD10 code to the new diagnosis)

#### Demographic Data

The demographics dataframe must have the following columns and datatypes
- patient_id : str - Unique Patient Identifier
- sex : str - Patient's sex
- race : str - Patient's race
- ethnicity : str - Patient's ethnicity

#### Insurance History

The insurance dataframe must have the following columns and datatypes
- patient_id : str - Unique Patient Identifier
- insurance : str - Insurance Name (will only be classified as Medicaid if "medicaid" in name, case insensitive)
- start_datetime : datetime64[ns] - Start Date of Insurance
- end_datetime : datetime64[ns] - End Date of Insurance (blanks fill be filled with today)

### SubMeasure 2

SubMeasure 2 is a subset of SubMeasure 1 and can be calculated from the results of SubMeasure 1 and does not need any additional data

## Output Data

The following dataframes are returned by the ASC Measure
- ASC_sub_1
- ASC_sub_1_stratification
- ASC_sub_2
- ASC_sub_2_stratification

### ASC_sub_1

- patient_id - Unique Patient Identifier
- patient_measurement_year_id - An ID created to match patients to their measurement year
- encounter_id - Unique Visit Identifier (returns the patient's most recent encounter id)
- numerator - Whether they satisfied the conditions to be included in the numerator
- medicaid - Whether the patient was on medicaid ONLY at the time of the index visit

### ASC_sub_1_stratification

- patient_id : Unique Patient Identifier
- ethnicity : Patient's ethnicity
- race : Patient's race

### ASC_sub_2

- patient_id - Unique Patient Identifier
- patient_measurement_year_id - An ID created to match patients to their measurement year
- numerator - Whether they satisfied the conditions to be included in the numerator
- numerator_time - A time frame after the sreening the counseling happened
- medicaid - Whether the patient was on medicaid ONLY at the time of the index visit

### ASC_sub_2_stratification

- patient_id : Unique Patient Identifier
- ethnicity : Patient's ethnicity
- race : Patient's race

## Code Demonstration

```sh
import pandas as pd
import ccbhc_measurements as ccbhc
```

#### - Step 1: Load in the data into Pandas Dataframes

```sh
all_inclusive_excel_file = r"../file/path/to/ASC Sub 1 Data.xlsx"
encounters = pd.read_xlsx(all_inclusive_excel_file, sheet_name = "encounters")
diagnosis_data = pd.read_xlsx(all_inclusive_excel_file, sheet_name = "diagnosis")
demographic_data = pd.read_xlsx(all_inclusive_excel_file, sheet_name = "demographic")
insurance_data = pd.read_xlsx(all_inclusive_excel_file, sheet_name = "insurance")
```

#### - Step 2: Ensure that the dataframes have the correct columns

```sh
encounters = encounters[["patient_id","patient_DOB","encounter_id","encounter_datetime","cpt_code","is_screening"]].copy()
diagnosis_data = diagnosis_data[["patient_id","encounter_datetime","diagnosis"]].copy()
demographic_data = demographic_data[["patient_id","race","ethnicity"]].copy()
insurance_data = insurance_data[["patient_id","insurance","start_datetime","end_datetime"]].copy()
```

#### - Step 3: Ensure that the columns are the correct data types

```sh
encounters['patient_id'] = encounters['patient_id'].astype(str)
encounters['patient_DOB'] = pd.to_datetime(encounters['patient_DOB'])
encounters['encounter_id'] = encounters['encounter_id'].astype(str)
encounters['encounter_datetime'] = pd.to_datetime(encounters['encounter_datetime'])
encounters['cpt_code'] = encounters['cpt_code'].astype(str)
encounters['screening'] = encounters['screening'].astype(str)
encounters['score'] = encounters['score'].astype(int)

diagnosis_data['patient_id'] = diagnosis_data['patient_id'].astype(str)
diagnosis_data['encounter_datetime'] = pd.to_datetime(diagnosis_data['encounter_datetime'])
diagnosis_data['diagnosis'] = diagnosis_data['diagnosis'].astype(str)

demographic_data['patient_id'] = demographic_data['patient_id'].astype(str)
demographic_data['sex'] = demographic_data['sex'].astype(str)
demographic_data['race'] = demographic_data['race'].astype(str)
demographic_data['ethnicity'] = demographic_data['ethnicity'].astype(str)

insurance_data['patient_id'] = insurance_data['patient_id'].astype(str)
insurance_data['insurace'] = insurance_data['insurace'].astype(str)
insurance_data['start_datetime'] = pd.to_datetime(insurance_data['start_datetime'])
insurance_data['end_datetime'] = pd.to_datetime(insurance_data['end_datetime'])
```

#### - Step 4: Calculate ASC

```sh
submeasure_data = [encounters,diagnosis_data,demographic_data,insurance_data]
measure = ccbhc.ASC(submeasure_data)
results = measure.get_all_submeasures()
for name, data in results.items():
    data.to_excel(name+".xlsx", index=False)
    # OR
    data.to_sql(name,DB_connection)
    # OR 
    # any other desired way to save Dataframes
```

## Notes

- Systematic Screenings
    - SAMHSA allows for multiple types of screenings such as AUDIT, AUDIT-C and the Single Question Screening.

- Medicaid
    - Any patient not included in the medicaid dataframe will be marked as "other" in the final data.

- SubMeasure 2
    - SubMeasure 2 is a subset of SubMeasure 1 and therefore `ASC.__sub2__.get_submeasure_data()` should not be called before `ASC.__sub1__.get_submeasure_data()`.
<hr>

[Back to Top](#ccbhc-measurements)
