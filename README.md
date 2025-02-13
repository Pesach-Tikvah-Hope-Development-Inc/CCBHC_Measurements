# CCBHC Measurements

## Table of Contents

 - [Purpose](#purpose)
 - [Currently Supported Measurements](#currently-supported-measurements)
 - [Code Demonstration](#code-demonstration)
 - [De-panda-cies](#de-panda-cies)
 - [License](#license)
 - [Installation](#installation)
 - [Contributors](#contributors)
 - [Contributions and Discussions](#contributions-and-discussions)

## Purpose

All CCBHCs are required to report Quality Measurements. The goal of this package is to simplify the process for calculating CCBHC measurements for all CCBHCs.

Our code is simple:
1. Import the Measurement you want to calculate.
2. Give it the required data (downloaded excel reports from your EHR, query data from SQL, or whatever)
3. Run ```get_all_submeasures()```. Under the hood, ```get_all_submeasures()``` determines which data meets the Measurments criteria and which does not.
4. Export your data to your preferred tool for analysis. If you want to keep it in pandas, you already have it. If you want to use Excel, or Power BI, you can export it there as well!

## Currently Supported Measurements

 - **DEP REM 6 -** Depression Remission at Six Months - [Dep Rem 6 Required Data Input and Output Diagram][Dep Rem 6 Diagram]

The definition for these Measurements can be at <https://www.samhsa.gov/sites/default/files/ccbhc-quality-measures-technical-specifications-manual.pdf>  
At the moment we only have these Measurements, but more will be added in the future

[Dep Rem 6 Diagram]:ccbhc_measurements/diagrams/DEP%20REM%20Input-Output%20Example.pdf

## Code Demonstration

```sh
import pandas as pd
import ccbhc_measurements as ccbhc
```

#### - Step 1: Load in the data into Pandas Dataframes

```sh
all_inclusive_excel_file = r"../file/path/to/Dep Rem Data.xlsx"
phq_data = pd.read_xlsx(all_inclusive_excel_file, sheet_name = "phq9")
diagnosis_data = pd.read_xlsx(all_inclusive_excel_file, sheet_name = "diagnosis")
demographic_data = pd.read_xlsx(all_inclusive_excel_file, sheet_name = "demographic")
insurance_data = pd.read_xlsx(all_inclusive_excel_file, sheet_name = "insurance")
```

#### - Step 2: Ensure that the dataframes follows the correct schema

[Dep Rem 6 Required Data Input and Output Diagram][Dep Rem 6 Diagram]

```sh
phq_data = phq_data[["patient_id","patient_DOB","encounter_id","encounter_datetime","total_score"]].copy()
diagnosis_data = diagnosis_data[["patient_id","encounter_datetime","diagnosis"]].copy()
demographic_data = demographic_data[["patient_id","race","ethnicity"]].copy()
insurance_data = insurance_data[["patient_id","insurance","start_datetime","end_datetime"]].copy()
```

#### - Step 3: Calculate Dep-Rem

```sh
submeasure_data = [phq_data,diagnosis_data,demographic_data,insurance_data]
measure = ccbhc.Dep_Rem(submeasure_data)
results = measure.get_all_submeasures()s
for name, data in results.items():
    data.to_excel(name+".xlsx", index=False)
```

## De-panda-cies

 - [pandas - Powerful data structures for data analysis, time series, and statistics](https://pandas.pydata.org/)
 - [python-dateutil - Extensions to the standard Python datetime module](https://dateutil.readthedocs.io/en/stable/index.html)
 - [pytz - Brings the Olson tz database into Python which allows accurate and cross platform timezone calculations](https://github.com/stub42/pytz)

## License

[CC BY-NC-SA 4.0](LICENSE)

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

## Contributions and Discussions

Feel free to add and create you own ```Measurements```. All ```Measurements``` should follow [this uml][uml].
Send us your recomendations, bugs, questions or feedback at [agursky@pesachtikvah.com](mailto:agursky@pesachtikvah.com)

[uml]:ccbhc_measurements/diagrams/Measurements%20UML.pdf

<hr>

[Back to Top](#ccbhc-measurements)