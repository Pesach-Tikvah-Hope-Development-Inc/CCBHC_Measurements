# Depression Remission at Six Months (DEP-REM-6)

## Table of Contents

- [Measurement Definition](#measurement-definition)
- [Required Data](#required-data)
- [Output Data](#output-data)
- [Code Demonstration](#code-demonstration)
- [Notes](#notes)

## Measurement Definition

The DEP-REM-6 measure calculates the Percentage of clients (12 years of age or older) with
Major Depression or Dysthymia who reach Remission Six Months (+/- 60 days) after an Index
Event Date

[Click here to see SAMHSA's definitions](https://www.samhsa.gov/sites/default/files/ccbhc-quality-measures-technical-specifications-manual.pdf)

### SubMeasure 1

Percentage of clients who scored above nine on a PHQ-9 and scored under five six months later 

## Required Data

[Click here to see the Input and Output Diagram](https://github.com/Pesach-Tikvah-Hope-Development-Inc/CCBHC_Measurements/blob/main/ccbhc_measurements/diagrams/DEP%20REM%20Input-Output%20Example.pdf)

### SubMeasure 1

The following dataframes are required to calculate the DEP-REM-6 SubMeasure 1
- PHQ9s
- Diagnoses
- Demographic Data
- Insurance History

#### PHQ9s

The PHQ9s dataframe must have the following columns and datatypes
- patient_id : str - Unique Patient Identifier
- patient_DOB : datetime64[ns] - Patients' Date of Birth
- encounter_id : str - Unique Visit Identifier
- encounter_datetime : datetime64[ns] - Date of visit
- total_score : int, float - PHQ9 score


#### Diagnosis

The diagnosis dataframe must have the following columns and datatypes
- patient_id : str - Unique Patient Identifier
- encounter_datetime : datetime64[ns] - Date of visit
- diagnosis : str - ICD10 Code to determine whether patients are excluded from the measure (for encounters with mulitple diagnoses, duplicate the entire line and change the ICD10 code to the new diagnosis)

#### Demographic Data

The demographics dataframe must have the following columns and datatypes
- patient_id : str - Unique Patient Identifier
- race : str - Patient's race
- ethnicity : str - Patient's ethnicity

#### Insurance History

The insurance dataframe must have the following columns and datatypes
- patient_id : str - Unique Patient Identifier
- insurance : str - Insurance Name (will only be classified as Medicaid if "medicaid" in name, case insensitive)
- start_datetime : datetime64[ns] - Start Date of Insurance
- end_datetime : datetime64[ns] - End Date of Insurance (blanks fill be filled with today)

## Output Data

The following dataframes are returned by the ASC Measure
- DEP_REM_sub_1
- DEP_REM_sub_1_stratification

### DEP_REM_sub_1

- patient_id - Unique Patient Identifier
- patient_measurement_year_id - An ID created to match patients to their measurement year
- encounter_id - Unique Visit Identifier (returns the patient's first encounter id where they scored above nine)
- numerator - Whether they satisfied the conditions to be included in the numerator
- numerator_reason - Why they did or didn't satisfy the condition to be included in the numerator
- age - Whether the patient was a child or adult at the time of PHQ9 administration
- medicaid - Whether the patient was on medicaid ONLY at the time of the index visit


### DEP_REM_sub_1_stratification

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
all_inclusive_excel_file = r"../file/path/to/DEP REM Sub 1 Data.xlsx"
phq_data = pd.read_xlsx(all_inclusive_excel_file, sheet_name = "phq9")
diagnosis_data = pd.read_xlsx(all_inclusive_excel_file, sheet_name = "diagnosis")
demographic_data = pd.read_xlsx(all_inclusive_excel_file, sheet_name = "demographic")
insurance_data = pd.read_xlsx(all_inclusive_excel_file, sheet_name = "insurance")
```

#### - Step 2: Ensure that the dataframes have the correct columns

```sh
phq_data = phq_data[["patient_id","patient_DOB","encounter_id","encounter_datetime","total_score"]].copy()
diagnosis_data = diagnosis_data[["patient_id","encounter_datetime","diagnosis"]].copy()
demographic_data = demographic_data[["patient_id","race","ethnicity"]].copy()
insurance_data = insurance_data[["patient_id","insurance","start_datetime","end_datetime"]].copy()
```

#### - Step 3: Ensure that the columns are the correct data types

```sh
phq_data['patient_id'] = phq_data['patient_id'].astype(str)
phq_data['patient_DOB'] = pd.to_datetime(phq_data['patient_DOB'])
phq_data['encounter_id'] = phq_data['encounter_id'].astype(str)
phq_data['encounter_datetime'] = pd.to_datetime(phq_data['encounter_datetime'])
phq_data['total_score'] = phq_data['total_score'].astype(int)

diagnosis_data['patient_id'] = diagnosis_data['patient_id'].astype(str)
diagnosis_data['encounter_datetime'] = pd.to_datetime(diagnosis_data['encounter_datetime'])
diagnosis_data['diagnosis'] = diagnosis_data['diagnosis'].astype(str)

demographic_data['patient_id'] = demographic_data['patient_id'].astype(str)
demographic_data['race'] = demographic_data['race'].astype(str)
demographic_data['ethnicity'] = demographic_data['ethnicity'].astype(str)

insurance_data['patient_id'] = insurance_data['patient_id'].astype(str)
insurance_data['insurace'] = insurance_data['insurace'].astype(str)
insurance_data['start_datetime'] = pd.to_datetime(insurance_data['start_datetime'])
insurance_data['end_datetime'] = pd.to_datetime(insurance_data['end_datetime'])
```

#### - Step 4: Calculate Dep-Rem

```sh
submeasure_data = [phq_data,diagnosis_data,demographic_data,insurance_data]
measure = ccbhc.DEP_REM(submeasure_data)
results = measure.get_all_submeasures()
for name, data in results.items():
    data.to_excel(name+".xlsx", index=False)
    # OR
    data.to_sql(name,DB_connection)
    # OR 
    # any other desired way to save Dataframes
```

## Notes

In the output data, "numerator_reason" can be 1 of 4 values
- Has Remission : Indicates that the client scored less than five on a follow up PHQ9
- Remission Period not Reached : Indicates that the client scored above nine too recently to have a follow up PHQ9 given
- No PHQ-9 Follow Up : Indicates that the client above nine six months ago, but no follow up PHQ9 was given
- No Remission : Indicates that the client above nine six months ago, a follow up PHQ9 was given but the client did not score under five

In the output data, "delta_phq9" is calculated by subtracting the most recent phq9 score within the remission period (6 months +/- 60 days) from the index phq9 score. **So if the recent phq9 has a higher score, the delta will be negative.**

<hr>

[Back to Top](#ccbhc-measurements)
