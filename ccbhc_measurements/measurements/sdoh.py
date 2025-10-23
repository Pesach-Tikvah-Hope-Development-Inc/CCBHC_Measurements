import pandas as pd
from ccbhc_measurements.compat.typing_compat import override
from ccbhc_measurements.abstractions.submeasure import Submeasure
from ccbhc_measurements.abstractions.measurement import Measurement
from datetime import datetime

class _Sub_1(Submeasure):
    """
    The Percentage of clients 18 years and older screened for food
    insecurity, housing instability, transportation needs,
    utility difficulties, and interpersonal safety
    """

    @override 
    def _set_dataframes(self, dataframes:list[pd.DataFrame]) -> None:
        """
        Sets private attributes to the validated dataframes that get used to calculate the submeasure

        Parameters
        ----------
        dataframes
            A list of dataframes in the following order
            0 - SDOH_Populace
            1 - SDOH_Screenings
            2 - Demographic_Data
            3 - Insurance_History
        """
        self.__DATA__ = dataframes[0].copy()
        self.__DEMOGRAPHICS__ = dataframes[1].copy()
        self.__INSURANCE__ = dataframes[2].copy()

    @override
    def get_populace_dataframe(self) -> pd.DataFrame:
        """
        Gets the populace dataframe 

        Returns
        -------
        pd.DataFrame
            The populace dataframe
        """
        return self.__populace__.copy()

    @override
    def get_stratify_dataframe(self) -> pd.DataFrame:
        """
        Gets the stratify dataframe

        Returns
        -------
        pd.DataFrame
            The stratify dataframe
        """
        return self.__stratification__.copy()

    @override
    def _set_populace(self) -> None:
        """
        Sets all possible eligible clients for the denominator
        """
        self.__initialize_populace()
        self.__populace__['patient_measurement_year_id'] = self.__create_measurement_year_id(
            self.__populace__['patient_id'],
            self.__populace__['encounter_datetime']
        )

    def __initialize_populace(self) -> None:
        """
        Sets populace data from the init's data
        """
        self.__populace__ = self.__DATA__.copy()

    def __create_measurement_year_id(self, patient_id:pd.Series, date:pd.Series) -> pd.Series:
        """
        Creates a unique id per patient per year

        Paramaters
        ----------
        ids
            Patient IDs
        dates
            Encountes dates

        Returns
        -------
        pd.Series
            patient_measurement_year_id
        """
        return patient_id.astype(str) + '-' + (date.dt.year).astype(str)

    @override
    def _remove_exclusions(self) -> None:
        """
        Filters exclusions from populace
        """
        # Denominator Exclusions:
        # All clients aged 17 years or younger
        self.__remove_age_exclusion()

    def __remove_age_exclusion(self) -> None:
        """
        Finds and reomves all encounters of clients aged 17 years or younger
        """
        self.__calculate_age()
        self.__filter_age()
        self.__get_first_encounter()

    def __calculate_age(self) -> None:
        """
        Calculates age of client at the date of service
        """
        self.__populace__['age'] = (self.__populace__['encounter_datetime'] - self.__populace__['patient_DOB']).dt.days // 365.25

    def __filter_age(self) -> None:
        """
        Removes all clients aged 17 or younger at the date of service
        """
        self.__populace__ = self.__populace__[self.__populace__['age'] >= 18]

    def __get_first_encounter(self) -> None:
        """
        Filters down all encounters to the first encounter per client per year
        """
        # needed for clients who turned 18 in the middle of the measurement year, as screening while they were 17 in that measurement year wouldn't count
        self.__populace__ = self.__populace__.sort_values(by=['patient_measurement_year_id','encounter_datetime']).drop_duplicates('patient_measurement_year_id',keep='first')
        
    @override
    def calculate_numerator(self) -> None:
        """
        Calculates the numerator for the SDOH measure
        """
        try:
            self._find_performance_met()
            # self._apply_time_constraint()
        except Exception:
            raise ValueError("Failed to calculate numerator")

    @override
    def _find_performance_met(self) -> None:
        """
        Derive last SDOH encounter via helper methods, then apply the time constraint
        """
        screenings = self.__get_screenings()
        last       = self.__get_last_screening(screenings)
        self.__merge_screenings_into_populace(last)
        self._apply_time_constraint()    
        self.__create_numerator_desc()

    def __get_screenings(self) -> pd.DataFrame:
        """
        Build the table of all TRUE is_sdoh encounters from __DATA__
        """
        full = self.__DATA__.copy()
        full['patient_measurement_year_id'] = self.__create_measurement_year_id(
            full['patient_id'], full['encounter_datetime']
        )
        return (
            full.loc[full['is_sdoh'],
                     ['patient_measurement_year_id','encounter_id','encounter_datetime']]
                .rename(columns={
                    'encounter_id':       'screening_id',
                    'encounter_datetime': 'screening_date'
                })
        )

    def __get_last_screening(self, screenings: pd.DataFrame) -> pd.DataFrame:
        """
        From the screening table, pick the most recent per patient-year
        """
        return (
            screenings
              .sort_values('screening_date', ascending=False)
              .drop_duplicates('patient_measurement_year_id', keep='first')
        )

    def __merge_screenings_into_populace(self, last: pd.DataFrame) -> None:
        """
        Left join the last screening_id and screening_date back into __populace__
        """
        self.__populace__ = self.__populace__.merge(
            last[['patient_measurement_year_id','screening_id','screening_date']],
            on='patient_measurement_year_id',
            how='left'
        )

    @override
    def _apply_time_constraint(self) -> None:
        """
        Applies the time constraint to the numerator
        """
        self.__set_numerator()

    def __set_numerator(self) -> None:
        """
        Sets the numerator for the SDOH measure
        """
        age_18 = self.__populace__[self.__populace__['age'] == 18].copy()
        age_18['numerator'] = (age_18['screening_date'] >= (age_18['patient_DOB'] + pd.DateOffset(years=18)))
        # for patients that are over 18 can have the screening at any point
        over_18 = self.__populace__[self.__populace__['age'] > 18].copy()
        over_18['numerator'] = over_18['screening_date'].notna()
        self.__populace__ = pd.concat([age_18,over_18])
    
    def __create_numerator_desc(self) -> None:
        """
        Assigns numerator_desc based on screening presence, age logic, and measurement year rules.
        """
        descs = []
        for _, row in self.__populace__.iterrows():
            # No screening at all!
            if pd.isna(row['screening_date']):
                descs.append("No screening recorded")
            # Screening exists but occurred before the 18th birthday (not valid for 18-year-olds)
            elif row['age'] == 18 and row['screening_date'] < row['patient_DOB'] + pd.DateOffset(years=18):
                descs.append("Screening occurred before 18th birthday")
            # Valid screening: 
            # age > 18 with any screening 
            # or
            # (b) age 18 and screening was after birthday
            elif row['numerator']:
                descs.append("Screened with valid standardized tool")
            else:
                descs.append("No screening recorded")
        self.__populace__['numerator_desc'] = descs

    @override
    def _set_stratification(self) -> None:
        """
        Initializes stratification by filtering populace
        """
        # Use populace to initialize stratification, keeping relevant columns
        self.__stratification__ = self.__populace__[['patient_measurement_year_id', 'patient_id', 'encounter_id', 'encounter_datetime', 'screening_date', 'age']].sort_values(['patient_measurement_year_id']).copy()
        # Compute measurement_year from patient_measurement_year_id
        self.__stratification__['measurement_year'] = self.__stratification__['patient_measurement_year_id'].str.split('-').str[1]

    @override
    def _set_patient_stratification(self) -> None:
        """
        Sets stratification data that is patient dependant
        """
        self.__set_patient_demographics()

    def __set_patient_demographics(self) -> None:
        """
        Merges DEMOGRAPHICS into stratification
        """
        self.__stratification__ = self.__stratification__.merge(self.__DEMOGRAPHICS__,how='left')
    
    @override
    def _set_encounter_stratification(self) -> None:
        """
        Sets stratification data that is encounter dependant
        """
        self.__set_age_stratifcation()
        self.__set_insurance_data()
  
    def __set_age_stratifcation(self) -> None:
        """
        Resets the age val to the age group 
        """
        self.__stratification__['age'] = self.__stratification__['age'].apply(lambda age: '18+' if age >= 18 else '12-18')

    def __set_insurance_data(self) -> None:
        """
        Sets insurance stratification at the time of the index visit
        """
        medicaid_data = self.__INSURANCE__.merge(self.__stratification__[['patient_id','encounter_datetime','screening_date']], how='right')
        medicaid_data = self.__filter_insurance_dates(medicaid_data) # gets insurances at time of encounter, "losing" patients
        medicaid_data['patient_measurement_year_id'] = self.__create_measurement_year_id(medicaid_data['patient_id'],medicaid_data['encounter_datetime'])
        results = self.__determine_medicaid_stratify(medicaid_data)
        self.__stratification__ = self.__stratification__.merge(results,how='left')
        self.__stratification__['medicaid'] = self.__stratification__['medicaid'].fillna(False) # replace all the "lost" patients from above without insurance
        # add medicaid to the populace
        self.__populace__ = self.__populace__.merge(
            self.__stratification__[['patient_measurement_year_id', 'medicaid']],
            on='patient_measurement_year_id',
            how='left'
        )

    def __filter_insurance_dates(self, medicaid_data:pd.DataFrame) -> pd.DataFrame:
        """
        Removes insurances that weren't active at the time of the patient's visit

        Paramaters
        ----------
        medicaid_data
            Insurance data for all patients
        
        Returns
        ------
        pd.Dataframe
            Encounters that had active medicaid insurance
        """
        # Replace nulls with today so ongoing insurances aren’t filtered out
        medicaid_data['end_datetime'] = medicaid_data['end_datetime'].fillna(datetime.now())
        # Split into screening and non-screening encounters
        screening_visits = medicaid_data[medicaid_data['screening_date'].notna()].copy()
        encounter_visits = medicaid_data[medicaid_data['screening_date'].isna()].copy()
        # Check validity: insurance active at screening date if present, otherwise encounter date
        screening_visits['valid'] = (
            (screening_visits['start_datetime'] <= screening_visits['screening_date']) &
            (screening_visits['end_datetime'] >= screening_visits['screening_date'])
        )
        encounter_visits['valid'] = (
            (encounter_visits['start_datetime'] <= encounter_visits['encounter_datetime']) &
            (encounter_visits['end_datetime'] >= encounter_visits['encounter_datetime'])
        )
        medicaid_data = pd.concat([screening_visits, encounter_visits]).sort_values(['patient_id', 'encounter_datetime'])
        return medicaid_data[medicaid_data['valid']].copy()
 
    def __determine_medicaid_stratify(self, medicaid_data:pd.DataFrame) -> pd.DataFrame:
        """
        Finds patients that have medicaid only for insurance

        Paramaters
        ----------
        medicaid_data
            Insurance data for all patients

        Returns
        -------
        pd.Dataframe
            Medicaid_data with a new column for medicaid stratification
        """
        medicaid_data['medicaid'] = self.__find_plans_with_medicaid(medicaid_data['insurance'])
        medicaid_data['medicaid'] = self.__replace_medicaid_values(medicaid_data['medicaid'])
        medicaid_data = self.__find_patients_with_only_medicaids(medicaid_data)
        return medicaid_data
    
    def __find_plans_with_medicaid(self, plan:pd.Series) -> pd.Series:
        """
        Checks if the insurance name contains medicaid
        
        Paramaters
        ----------
        plan
            Insurance name

        Returns
        -------
        pd.Series
            A bool represtning if the plan is medicaid
        """
        return plan.str.contains('medicaid',case=False)

    def __replace_medicaid_values(self, col:pd.Series) -> pd.Series:
        """
        Replaces Boolean values with numerical values
        
        Paramaters
        ----------
        col
            Boolean represnting if insurance is medicaid

        Returns
        -------
        pd.Series
            Numerical representaion of the bool
        """
        return col.map({True:1,False:2})

    def __find_patients_with_only_medicaids(self,medicaid_data:pd.DataFrame) -> pd.DataFrame:
        """
        Calcutlates whether a patient has medicaid only or other insurance
        
        Paramaters
        ----------
        medicaid_data
            Insurance data for all patients

        Returns
        -------
        pd.Dataframe
            medicaid_data properly stratified for insurance
        """
        medicaid_data = medicaid_data.merge(self.__stratification__,on=['patient_measurement_year_id'],how='left')
        return (medicaid_data.groupby(['patient_measurement_year_id'])['medicaid'].sum() == 1).reset_index()
        
    @override
    def _fill_blank_stratification(self) -> None:
        """
        Fill in all null values with Unknown
        """
        self.__stratification__ = self.__stratification__.fillna('Unknown')

    @override
    def _set_final_denominator_data(self) -> None:
        """
        Sets the populace data to the unique data points that are needed for the denominator
        """
        self.__remove_unneeded_populace_columns()

    def __remove_unneeded_populace_columns(self) -> None:
        """ 
        Removes all columns that were used to calculate data points
        """
        self.__populace__ = self.__populace__[['patient_measurement_year_id', 'patient_id', 'numerator', 'numerator_desc','screening_id', 'screening_date', 'medicaid']].drop_duplicates(subset='patient_measurement_year_id')

    @override
    def _trim_unnecessary_stratification_data(self) -> None:
        self.__stratification__ = self.__stratification__[['patient_id', 'ethnicity', 'race']].drop_duplicates(subset='patient_id')

    @override
    def _sort_final_data(self) -> None:
        """
        Sorts the Populace and Stratification dataframes
        """
        self.__populace__ = self.__populace__.sort_values('patient_measurement_year_id')
        self.__stratification__ = self.__stratification__.sort_values('patient_id')

class SDOH(Measurement):
    """
    The SDOH measure calculates the Percentage of clients 18 years and older screened for food
    insecurity, housing instability, transportation needs, utility difficulties, and interpersonal safety
    
    Parameters
    ----------
    sub1_data
        List of dataframes containing all needed data to calculate submeasure 1

    Notes
    -----
    sub1_data must follow the its `Schema` as defined by the `Validation_Factory` in order to ensure the `submeasure` can run properly

    >>> SDOH_sub_1 = [
    >>>     "Populace",
    >>>     "SDOH_Screenings",
    >>>     "Demographic_Data",
    >>>     "Insurance_History"
    >>> ]
 
    >>> Populace = {
    >>>     "patient_id": (str, 'object'),
    >>>     "encounter_id": (str, 'object'),
    >>>     "encounter_datetime": ("datetime64[ns]",),  
    >>>     "patient_DOB": ("datetime64[ns]",),
    >>>     "is_sdoh": (bool,)
    >>> }

    >>> Demographic_Data = {
    >>>     "patient_id": (str, 'object'),
    >>>     "race": (str, 'object'),
    >>>     "ethnicity": (str, 'object')
    >>> }
 
    >>> Insurance_History = {
    >>>     "patient_id": (str, 'object'),
    >>>     "insurance": (str, 'object'),
    >>>     "start_datetime": ("datetime64[ns]",),
    >>>     "end_datetime": ("datetime64[ns]",)
    >>> }
    """

    def __init__(self, sub1_data:list[pd.DataFrame]):
        super().__init__("SDOH")
        self.__sub1__: Submeasure = _Sub_1(self.name + "_sub_1", sub1_data)

    @override
    def get_all_submeasures(self) -> dict[str:pd.DataFrame]:
        """
        Calculates all the data for the DEP REM 6 Measurement and its Submeasures

        Returns
        -------
        dict[str:pd.DataFrame]
            str
                Submeasure name
            pd.DataFrame
                Submeasure Data

        Raises
        ------
        ValueError
            When the submeasure data isn't properly formatted
        """
        try:
            return self.__sub1__.get_submeasure_data()
        except Exception:
            raise
