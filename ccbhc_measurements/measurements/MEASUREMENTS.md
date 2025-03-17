# Measurement Creation

## Table of Contents

- [Creating a Measurement](#creating-a-measurement)
- [Adding Validation](#adding-validation)
- [Creating Submeasures](#creating-submeasures)
- [Adding Demo Data](#adding-demo-data)
- [Code Demonstration](#code-demonstration)
- [Notes](#notes)

## Creating a Measurement

```Measurement``` is an Abstract Class designed for front end users to have an easy way to calculate measurements and their submeasures.

```Mesaurement``` is an Abstract Class, it is composed of ```Submeasure```s and has an abstract method ```get_all_submeasures()``` which need to be overridden in the concrete ```Measurement```. [More details here][Measurement]

Concrete ```Measurement```s should be created within ccbhc_measurements->measurements->new_measurement.py.

[Measurement]:https://github.com/Pesach-Tikvah-Hope-Development-Inc/CCBHC_Measurements/blob/main/ccbhc_measurements/abstractions/measurement.py

## Adding Validation

When a ```Submeasure``` is initialized, it creates a ```Validator``` to ensure the dataframes exist, have the proper column names and the proper column types.

Within ccbhc_measurements->validation->required_data.py create a list where the name of the list  is ```Your_Measurement_sub_1``` and the values are of type ```str``` reflecting what Dataframes are needed. Then add the ```list``` to ```get_required_dataframes()```. [More details here](https://github.com/Pesach-Tikvah-Hope-Development-Inc/CCBHC_Measurements/blob/main/ccbhc_measurements/validation/required_data.py)

Within ccbhc_measurements->validation->schemas.py create dictionaries where the name of the dictionary is ```Your_Measurement_dataframe```, the keys are ```column_name```s and the values are an iterable of ```column_data_type```. Then add the ```dict``` to ```get_schema()```. [More details here](https://github.com/Pesach-Tikvah-Hope-Development-Inc/CCBHC_Measurements/blob/main/ccbhc_measurements/validation/schemas.py)

## Creating Submeasures

```Submeasure``` is an Abstract Class designed as the component(s) for ```Measurement```. ```Submeasure``` inherits from ```Denominator```, ```Numerator``` and ```Stratification```.

```Submeasure``` is an Abstract Class and has the following abstract methods ```_set_dataframes()```, ```_set_final_denominator_data()```, ```_trim_unnecessary_stratification_data()```, and ```_sort_final_data()``` which need to be overridden in the concrete ```Submeasure```. [More details here][Submeasure]

```Denominator``` is an Abstract Class and has the following abstract methods ```_set_populace()``` and ```_remove_exclusions()``` which need to be overridden in the concrete ```Submeasure```. [More details here][Denominator]

```Numerator``` is an Abstract Class and has the following abstract methods ```_apply_time_constraint()``` and ```_find_performance_met()``` which need to be overridden in the concrete ```Submeasure```. [More details here][Numerator]

```Stratification``` is an Abstract Class and has the following abstract methods ```_set_stratification()```, ```_set_patient_stratification()```, ```_set_encounter_stratification()``` and ```_fill_blank_stratification()``` which need to be overridden in the concrete ```Submeasure```. [More details here][Stratification]

[Submeasure]:https://github.com/Pesach-Tikvah-Hope-Development-Inc/CCBHC_Measurements/blob/main/ccbhc_measurements/abstractions/submeasure.py
[Denominator]:https://github.com/Pesach-Tikvah-Hope-Development-Inc/CCBHC_Measurements/blob/main/ccbhc_measurements/abstractions/denominator.py
[Numerator]:https://github.com/Pesach-Tikvah-Hope-Development-Inc/CCBHC_Measurements/blob/main/ccbhc_measurements/abstractions/numerator.py
[Stratification]:https://github.com/Pesach-Tikvah-Hope-Development-Inc/CCBHC_Measurements/blob/main/ccbhc_measurements/abstractions/stratification.py

## Adding Demo Data

In order to test the acccuracy of the code and to create the dashboard, demo files are used for non-HIPPA demonstrations. [More details here][DEP-REM demo]

In addition to the demo data, there should also be a NEW_MEASUREMENT.md which tells the front end user what data is needed and how it should be formatted. [More details here][DEP-REM read me]

These files should be made within ccbhc_measurements->demos and added to main_demo.py.

[DEP-REM demo]:https://github.com/Pesach-Tikvah-Hope-Development-Inc/CCBHC_Measurements/blob/main/ccbhc_measurements/demos/dep_rem_demo.py
[DEP-REM read me]:https://github.com/Pesach-Tikvah-Hope-Development-Inc/CCBHC_Measurements/blob/main/ccbhc_measurements/demos/DEP-REM.md

## Code Demonstration

#### Required Data
```sh
DEP_REM_sub_1 = [
    "PHQ9",
    "Diagnostic_History",
    "Demographic_Data",
    "Insurance_History"
]

def get_required_dataframes(submeasure_name: str) -> list[str]:
    ...
    match submeasure_name:
        case "DEP_REM_sub_1":
            return DEP_REM_sub_1
```

#### Schemas
```sh
PHQ9 = {
    "patient_id": (str, 'object'),
    "patient_DOB": ("datetime64[ns]",),
    "encounter_id": (str, 'object'),
    "encounter_datetime": ("datetime64[ns]",),
    "total_score": (int, float)
}
Diagnostic_History = {
    "patient_id": (str, 'object'),
    "encounter_datetime": ("datetime64[ns]",),
    "diagnosis": (str, 'object')
}
Demographic_Data = {
    "patient_id": (str, 'object'),
    "race": (str, 'object'),
    "ethnicity": (str, 'object')
}
Insurance_History = {
    "patient_id": (str, 'object'),
    "insurance": (str, 'object'),
    "start_datetime": ("datetime64[ns]",),
    "end_datetime": ("datetime64[ns]",)
}

def get_schema(df_name:str) -> dict[str:type]:
    ...
    match df_name:
        case "PHQ9":
            return PHQ9
        case "Demographic_Data":
            return Demographic_Data
        case "Diagnostic_History":
            return Diagnostic_History
        case "Insurance_History":
            return Insurance_History
```

#### new_measurement.py

```sh
class _Sub_1(Submeasure):
    """
    Doc String
    """

    # Submeasure Method
    @override
    def _set_dataframes(self, dataframes: list[pd.DataFrame]) -> None:
        """
        Doc String
        """
        # Sets private attributes to the validated dataframes that get used to calculate the submeasure
    
    # Denominator Method
    @override
    def _set_populace(self) -> None:
        """
        Doc String
        """
        # This method should sets all possible eligible clients for the denominator
    
    # Denominator Method
    @override
    def _remove_exclusions(self) -> None:
        """
        Doc String
        """
        # This method should filter or call other methods needed to remove all exclusions from the populace

    # Numerator Method
    @override
    def _apply_time_constraint(self) -> None:
        """
        Doc String
        """
        # This method should set a min and max time boundries for the numerator criteria to happen within

    # Numerator Method
    @override
    def _find_performance_met(self) -> None:
        """
        Doc String
        """
        # Checks if the numerator criteria happened within the correct time frame

    # Stratification Method
    @override
    def _set_stratification(self) -> None:
        """
        Doc String
        """
        # This method should set the initial population for the stratification from the Submeasure's populace

    # Stratification Method
    @override
    def _set_patient_stratification(self) -> None:
        """
        Doc String
        """
        # This method should set stratification data that is patient dependant

    # Stratification Method
    @override
    def _set_encounter_stratification(self) -> None:
        """
        Doc String
        """
        # This method should set stratification data that is encounter dependant

    # Stratification Method
    @override
    def _fill_blank_stratification(self) -> None:
        """
        Doc String
        """
        # This method should fill all blank values in the stratification

    # Submeasure Method
    @override
    def _set_final_denominator_data(self) -> None:
        """
        Doc String
        """
        # This method should set all data that is needed and unique to the Submeasure's denominator populace

    # Submeasure Method
    @override
    def _trim_unnecessary_stratification_data(self) -> None:
        """
        Doc String
        """
        # This method should remove all data that isn't needed to calculate the Submeasure's stratification

    # Submeasure Method
    @override
    def _sort_final_data(self) -> None:
        """
        Doc String
        """
        # This method should sort the Populace and Stratification dataframes
```

```sh
class New_Measurement(Measurement):
    """
    Doc String
    """

    def __init__(self,sub1_data:list[pd.DataFrame]):
        super().__init__("New_Measurement")
        self.__sub1__: Submeasure = _Sub_1(self.get_name() + "_sub_1",sub1_data)
    
    @override
    def get_all_submeasures(self) -> dict[str:pd.DataFrame]:
        """
        Doc String
        """
            # Using a try except to not break someone's main.py if an exception is raised,
            # this should call the Submeasure's get_submeasure_data()
```

## Notes

Doc strings should follow the NumPy Style. [More details here][Doc Strings]

[Doc Strings]:https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_numpy.html

<hr>

[Back to Top](#ccbhc-measurements)
