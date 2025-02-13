# CCBHC Measurements

## Table of Contents

 - [Purpose](#purpose)
 - [Currently Supported Measurements](#currently-supported-measurements)
 - [Code Demonstration](#code-demonstration)
 - [Dependancies](#dependancies)
 - [License](#license)
 - [Installation](#installation)
 - [Contributors](#contributors)

## Purpose

All CCBHCs are required to report Quality Measurements. The goal of this package is designed to make the calculations of those Measurements a simplified proccess for all CCBHCs.


## Currently Supported Measurements

 - **DEP REM 6 -** Depression Remission at Six Months

The definition for these Measurements can be at <https://www.samhsa.gov/sites/default/files/ccbhc-quality-measures-technical-specifications-manual.pdf>  
At the moment we only have these Measurements, but more will be added in the future

## Code Demonstration

```
import pandas as pd
import ccbhc_measurements as ccbhc

# Step 1: Load in the data into Pandas Dataframes

all_inclusive_excel_file = r'../file/path/to/Dep Rem Data.xlsx'
phq_data = pd.read_xlsx(all_inclusive_excel_file, sheet_name = 'phq9')
diagnosis_data = pd.read_xlsx(all_inclusive_excel_file, sheet_name = 'diagnosis')
demographic_data = pd.read_xlsx(all_inclusive_excel_file, sheet_name = 'demographic')
insurance_data = pd.read_xlsx(all_inclusive_excel_file, sheet_name = 'insurance')

# Step 2: Ensure that the dataframes contain the correct columns and the column names are correct

phq_data = phq_data[["patient_id","patient_DOB","encounter_id","encounter_datetime","total_score"]].copy()
diagnosis_data = diagnosis_data[["patient_id","encounter_datetime","diagnosis"]].cop()
demographic_data = demographic_data[["patient_id","race","ethnicity"]].copy()
insurance_data = insurance_data[["patient_id","insurance","start_datetime","end_datetime"]].copy()


```

## Depandacies

 - [pandas - Powerful data structures for data analysis, time series, and statistics](https://pandas.pydata.org/)
 - [python-dateutil - Extensions to the standard Python datetime module](https://dateutil.readthedocs.io/en/stable/index.html)
 - [pytz - Brings the Olson tz database into Python which allows accurate and cross platform timezone calculations](https://github.com/stub42/pytz)

## License



## Installation

Binary installers for the latest released version are available at the [Python
Package Index (PyPI)](https://test.pypi.org/project/ccbhc-measurements/)

```sh
# PyPI
pip install -i https://test.pypi.org/simple/ ccbhc-measurements
```

## Contributors

 - Alex Gursky
 - Yisroel Len

<hr>

[Back to Top](#ccbhc-measurements)