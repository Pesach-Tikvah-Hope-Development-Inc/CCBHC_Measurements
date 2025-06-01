# Screening for Social Drivers of Health (SDOH)

## Table of Contents

- [Measurement Definition](#measurement-definition)  
- [Required Data](#required-data)  
- [Output Data](#output-data)  
- [Code Demonstration](#code-demonstration)  
- [Notes](#notes)

## Measurement Definition

The SDOH measure calculates the Percentage of clients 18 years and older screened for food insecurity, housing instability, transportation needs, utility difficulties, and interpersonal safety.

[Click here to see SAMHSA's definitions](https://www.samhsa.gov/sites/default/files/ccbhc-quality-measures-technical-specifications-manual.pdf)

### SubMeasure 1

Percentage of clients aged 18 years and older who were screened for social drivers of health least once during the measurement year

## Required Data

[Click here to see the Input and Output Diagram](https://github.com/Pesach-Tikvah-Hope-Development-Inc/CCBHC_Measurements/blob/main/ccbhc_measurements/diagrams/SDOH%20Input%20Output%20Requirements.pdf)

### SubMeasure 1

The following dataframes are required to calculate the SDOH SubMeasure 1:

- Populace  
- Demographic Data  
- Insurance History  

#### Populace

Populace must have the following columns and datatypes:
- patient_id : str — Unique Patient Identifier  
- patient_DOB : datetime64[ns] — Patient's Date of Birth  
- encounter_id : str — Unique Visit Identifier  
- encounter_datetime : datetime64[ns] — Date of Qualifying Encounter 
- is_sdoh : bool — Whether that encounter was an SDOH screening  


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
- SDOH_sub_1
- SDOH_sub_1_stratification

### SDOH_sub_1

- patient_id : Unique Patient Identifier
- patient_measurement_year_id : An ID created to match patients to their measurement year  
- encounter_id : Unique Visit Identifier (first qualifying encounter of the Measurement Year)  
- numerator : Whether the patient received a complete screening (True/False)  
- screening_id : ID of the associated screening if applicable  
- screening_date : Date of screening if applicable  
- medicaid : Whether the patient had Medicaid ONLY at the time of the encounter (True/False)

### SDOH_sub_1_stratification

- patient_measurement_year_id : An ID created to match patients to their measurement year  
- measurement_year : The measurement year 
- ethnicity : Patient's ethnicity  
- race : Patient's race  

## Code Demonstration

```sh
import pandas as pd
import ccbhc_measurements as ccbhc
```

#### - Step 1: Load in the data into Pandas Dataframes

```sh
all_inclusive_excel_file = r"../file/path/to/SDOH Sub 1 Data.xlsx"
populace = pd.read_excel(all_inclusive_excel_file, sheet_name="populace")
demographics = pd.read_excel(all_inclusive_excel_file, sheet_name="demographic_data")
insurance = pd.read_excel(all_inclusive_excel_file, sheet_name="insurance_history")
```
#### - Step 2: Ensure that the dataframes have the correct columns

```sh
populace = populace[["patient_id", "patient_DOB", "encounter_id","encounter_datetime","is_sdoh"]].copy()
demographics = demographics[["patient_id", "race", "ethnicity"]].copy()
insurance = insurance[["patient_id", "insurance", "start_datetime", "end_datetime"]].copy()
```

#### - Step 3: Ensure that the columns are the correct data types

```sh
populace["patient_id"] = populace["patient_id"].astype(str)
populace["patient_DOB"] = pd.to_datetime(populace["patient_DOB"])
populace["encounter_id"] = populace["encounter_id"].astype(str)
populace["encounter_datetime"] = pd.to_datetime(populace["encounter_datetime"])
populace["is_sdoh"] = populace["is_sdoh"].astype(bool)


demographics["patient_id"] = demographics["patient_id"].astype(str)
demographics["race"] = demographics["race"].astype(str)
demographics["ethnicity"] = demographics["ethnicity"].astype(str)

insurance["patient_id"] = insurance["patient_id"].astype(str)
insurance["insurance"] = insurance["insurance"].astype(str)
insurance["start_datetime"] = pd.to_datetime(insurance["start_datetime"])
insurance["end_datetime"] = pd.to_datetime(insurance["end_datetime"])
```

#### - Step 4: Calculate SDOH

```sh
submeasure_data = [populace, demographics, insurance]
measure = ccbhc.SDOH(submeasure_data)
results = measure.get_all_submeasures()
for name, data in results.items():
    data.to_excel(name + ".xlsx", index=False)
    # OR
    data.to_sql(name, DB_connection)
    # OR
    # any other desired way to save DataFrames
```

## Notes

- Medicaid
    - Any patient not included in the medicaid dataframe will be marked as "other" in the final data.

<hr>

[Back to Top](#ccbhc-measurements)