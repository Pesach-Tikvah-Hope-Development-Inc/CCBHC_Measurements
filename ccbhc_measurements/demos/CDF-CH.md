# Screening for Depression and Follow-Up Plan (CDF_CH)

## Table of Contents

- [Measurement Definition](#measurement-definition)  
- [Required Data](#required-data)  
- [Output Data](#output-data)  
- [Code Demonstration](#code-demonstration)  
- [Notes](#notes)

## Measurement Definition

The CDF_CH measure calculates the percentage of clients aged 17 and younger who were screened for depression during the measurement year using a standardized tool, and if positive, had a follow-up plan documented on the date of the eligible encounter.

[Click here to see SAMHSA's definitions](https://www.samhsa.gov/sites/default/files/ccbhc-quality-measures-technical-specifications-manual.pdf)

### SubMeasure 1

Percentage of clients aged 17 and younger who received at least one depression screening during the measurement year, and if positive, had a documented follow-up plan on the date of the screening.

## Required Data

[Click here to see the Input and Output Diagram](https://github.com/Pesach-Tikvah-Hope-Development-Inc/CCBHC_Measurements/blob/main/ccbhc_measurements/diagrams/CDF_CH%20Input%20Output%20Requirements.pdf)

### SubMeasure 1

The following dataframes are required to calculate the CDF_CH SubMeasure 1:

- Populace  
- Diagnostics
- Demographic Data  
- Insurance History  

#### Populace

Populace must have the following columns and datatypes:
- patient_id : str — Unique Patient Identifier  
- encounter_id : str — Unique Visit Identifier  
- encounter_datetime : datetime64[ns] — Date of Qualifying Encounter 
- patient_DOB : datetime64[ns] — Patient's Date of Birth  
- follow_up : bool - Was there a follow up for that encounter
- total_score : float — Screening score  
- screening_type : str — Which tool was used (While there are more options, we use the following most common cases: PHQ9, PHQA, PSC-17)

#### Diagnostics

The Diagnostics dataframe must have the following columns and datatypes:

- patient_id : str — Unique Patient Identifier  
- encounter_datetime : datetime64[ns] — Date of the encounter
- diagnosis : str — The diagnosis

#### Demographic_Data

The Demographic_Data dataframe must have the following columns and datatypes:

- patient_id : str — Unique Patient Identifier  
- ethnicity : str — Patient’s reported ethnicity  
- race : str — Patient’s reported race  

#### Insurance_History

The Insurance_History dataframe must have the following columns and datatypes:

- patient_id : str — Unique Patient Identifier  
- insurance : str — Insurance Plan Name (will only be classified as Medicaid if "medicaid" in name, case insensitive)  
- start_datetime : datetime64[ns] — Start Date of Coverage  
- end_datetime : datetime64[ns] — End Date of Coverage (blanks will be filled with today)  

## Output Data

The following dataframes are returned by the ASC Measure
- CDF_CH_sub_1
- CDF_CH_sub_1_stratification

### CDF_CH_sub_1

- patient_measurement_year_id : An ID created to match patients to their measurement year  
- patient_id : Unique Patient Identifier
- encounter_id : Unique Visit Identifier (first qualifying encounter of the Measurement Year)  
- screening_encounter_id : ID of the associated screening if applicable  
- numerator : Whether the patient received a complete screening (True/False)  
- numerator_desc : Explains what caused the numerator result
- last_encounter : Date of last encounter
- medicaid : Whether the patient had Medicaid ONLY at the time of the encounter (True/False)

### CDF_CH_sub_1_stratification

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
all_inclusive_excel_file = r"../file/path/to/CDF_CH Sub 1 Data.xlsx"
populace = pd.read_excel(all_inclusive_excel_file, sheet_name="populace")
diagnostics  = pd.read_excel(all_inclusive_excel_file, sheet_name="diagnostics")
demographics = pd.read_excel(all_inclusive_excel_file, sheet_name="demographic_data")
insurance = pd.read_excel(all_inclusive_excel_file, sheet_name="insurance_history")
```
#### - Step 2: Ensure that the dataframes have the correct columns

```sh
populace = populace[["patient_id", "patient_DOB", "encounter_id", "encounter_datetime", "follow_up", "total_score", "screening_type"]].copy()
diagnostics = diagnostics[["patient_id", "encounter_datetime", "diagnosis"]].copy()
demographics = demographics[["patient_id", "race", "ethnicity"]].copy()
insurance = insurance[["patient_id", "insurance", "start_datetime", "end_datetime"]].copy()
```

#### - Step 3: Ensure that the columns are the correct data types

```sh
populace["patient_id"] = populace["patient_id"].astype(str)
populace["patient_DOB"] = pd.to_datetime(populace["patient_DOB"])
populace["encounter_id"] = populace["encounter_id"].astype(str)
populace["encounter_datetime"] = pd.to_datetime(populace["encounter_datetime"])
populace["follow_up"] = populace["follow_up"].astype(bool)
populace["total_score"] = pd.to_numeric(populace["total_score"], errors="coerce")
populace["screening_type"] = populace["screening_type"].astype(str)

diagnostics["patient_id"] = diagnostics["patient_id"].astype(str)
diagnostics["encounter_datetime"] = pd.to_datetime(diagnostics["encounter_datetime"])
diagnostics["diagnosis"] = diagnostics["diagnosis"].astype(str)

demographics["patient_id"] = demographics["patient_id"].astype(str)
demographics["race"] = demographics["race"].astype(str)
demographics["ethnicity"] = demographics["ethnicity"].astype(str)

insurance["patient_id"] = insurance["patient_id"].astype(str)
insurance["insurance"] = insurance["insurance"].astype(str)
insurance["start_datetime"] = pd.to_datetime(insurance["start_datetime"])
insurance["end_datetime"] = pd.to_datetime(insurance["end_datetime"])
```

#### - Step 4: Calculate CDF_CH

```sh
submeasure_data = [populace, diagnostics, demographics, insurance]
measure = ccbhc.CDF_CH(submeasure_data)
results = measure.get_all_submeasures()
for name, data in results.items():
    data.to_excel(name + ".xlsx", index=False)
    # OR
    data.to_sql(name, DB_connection)
    # OR
    # any other desired way to save DataFrames
```

## Notes

- SAMHSA allows for many screening tools, however, we only use the following screenings:
    - PHQ9
    - PHQA
    - PSC-17
<hr>

[Back to Top](#ccbhc-measurements)