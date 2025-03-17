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

The goal of this package is to simplify the process for calculating CCBHC measurements for all CCBHCs. It does this by taking in all the relevant data for a measurement and outputing whether the data meets the measurements' criteria. Here's the DEP-REM-6 as an example:

![simple example of how the package works](https://github.com/Pesach-Tikvah-Hope-Development-Inc/CCBHC_Measurements/blob/main/ccbhc_measurements/diagrams/Simple%20CCBHC_Measurements%20Example.png?raw=true)
[Click here for the more detailed DEP-REM-6 example pdf][Dep Rem 6 Diagram]

### 1. Data Processing
Our code is simple:
1. Import the Measurement you want to calculate.
2. Give it the required data (downloaded excel reports from your EHR, query data from SQL, or whatever)
3. Run ```get_all_submeasures()```. Under the hood, ```get_all_submeasures()``` determines which data meets the Measurments criteria and which does not.
4. Export your data to your preferred tool for analysis. If you want to keep it in pandas, you already have it. If you want to use Excel, or Power BI, you can export it there as well!

### 2. Dashboard Display
We've also created a base Power BI file as a foundation for a dashboard. [Check out the dashboard folder here.](CCBHC_Measurements/ccbhc_measurements/dashboard/)

![Dashboard Picture](ccbhc_measurements/diagrams/Dashboard_Example.jpg)

## Currently Supported Measurements

 - **DEP REM 6 -** Depression Remission at Six Months 
    - [DEP-REM-6 Detailed Data Input and Output Diagram][Dep Rem 6 Diagram]
    - [DEP-REM-6 Submeasure 1 README][DEP-REM-6 Submeasure 1 README]
 - **ASC Submeasure 1-** Preventive Care and Screening: Unhealthy Alcohol Use: Screening & Brief Counseling 
    - [ASC Submeasure 1 Detailed Data Input and Output Diagram][ASC Submeasure 1 Detailed Data Input and Output Diagram]
    - [ASC Submeasure 1 README][ASC Submeasure 1 README]


The definition for these Measurements can be found at <https://www.samhsa.gov/sites/default/files/ccbhc-quality-measures-technical-specifications-manual.pdf>  

At the moment we only have these Measurements, but we plan on releasing a new Measurement every two weeks.

[Dep Rem 6 Diagram]:https://github.com/Pesach-Tikvah-Hope-Development-Inc/CCBHC_Measurements/blob/main/ccbhc_measurements/diagrams/DEP%20REM%20Input-Output%20Example.pdf
[DEP-REM-6 Submeasure 1 README]:https://github.com/Pesach-Tikvah-Hope-Development-Inc/CCBHC_Measurements/blob/main/ccbhc_measurements/demos/DEP-REM.md
[ASC Submeasure 1 Detailed Data Input and Output Diagram]:https://github.com/Pesach-Tikvah-Hope-Development-Inc/CCBHC_Measurements/blob/main/ccbhc_measurements/diagrams/ASC%20Input%20Output%20Requirements.pdf
[ASC Submeasure 1 README]:https://github.com/Pesach-Tikvah-Hope-Development-Inc/CCBHC_Measurements/blob/main/ccbhc_measurements/demos/ASC.md

## Code Demonstration

This is a demonstration for the Dep-Rem-6 Measurement, see [here](https://github.com/Pesach-Tikvah-Hope-Development-Inc/CCBHC_Measurements/blob/main/ccbhc_measurements/demos) for more demonstrations

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
results = measure.get_all_submeasures()
for name, data in results.items():
    data.to_excel(name+".xlsx", index=False)
```
##### Example Data Output:

| patient_id | patient_measurement_year_id | encounter_id | age | medicaid | numerator | numerator_reason            |
| ---------- | --------------------------- | ------------ | --- | -------- | --------- | ---------------------------- |
| 1          | 1-2024                      | 1            | 18+ | FALSE    | **TRUE**      | <mark>**Has Remission**</mark>                |
| 2          | 1-2025                      | 3            | 18+ | FALSE    | **FALSE**     | <mark>**Remission Period not Reached**</mark> |
| 3          | 3-2024                      | 4            | 18+ | FALSE    | **FALSE**     | <mark>**No PHQ-9 Follow Up**</mark>           |
| 4          | 4-2024                      | 5            | 18+ | FALSE    | **FALSE**     | <mark>**No Remission**</mark>                 |

#### - Step 4: Create a Dashboard in Power BI (Optional)
We've created an example dashboard in Power BI for easy implementation but feel free to use the analysis tool of your choice. Feel free to download it from [the dashboard folder](CCBHC_Measurements/ccbhc_measurements/dashboard/).

## De-panda-cies

 - [pandas - Powerful data structures for data analysis, time series, and statistics](https://pandas.pydata.org/)

## License

[CC BY-NC-SA 4.0](LICENSE)

## Installation

Binary installers for the latest released version are available at the [Python
Package Index (PyPI)](https://pypi.org/project/ccbhc-measurements/)

```sh
# PyPI
pip install ccbhc_measurements
```

## Contributors

 - Alex Gursky - Data Engineer
 - Yisroel Len - Director of Data Analytics & CCBHC Project Evaluator

## Contributions and Discussions

Feel free to add and create you own ```Measurements```. All ```Measurements``` should follow [this uml][uml] and you can use [this guide][measurement creation guide] to show you how to do it!.

Send us your recomendations, bugs, questions or feedback at [agursky@pesachtikvah.com](mailto:agursky@pesachtikvah.com)

[measurement creation guide]:https://github.com/Pesach-Tikvah-Hope-Development-Inc/CCBHC_Measurements/blob/main/ccbhc_measurements/measurements/MEASUREMENTS.md
[uml]:https://github.com/Pesach-Tikvah-Hope-Development-Inc/CCBHC_Measurements/blob/main/ccbhc_measurements/diagrams/Measurements%20UML.pdf

<hr>

[Back to Top](#ccbhc-measurements)
