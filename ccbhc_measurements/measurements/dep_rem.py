from dateutil.relativedelta import relativedelta
from typing import override
from datetime import datetime
import pandas as pd
from ccbhc_measurements.abstractions.submeasure import Submeasure
from ccbhc_measurements.abstractions.measurement import Measurement

class _Sub_1(Submeasure):
    """
    The Percentage of clients (12 years of age or older)
    with Major Depression or Dysthymia who reach Remission Six Months
    after an Index Event
    """

    @override
    def _set_dataframes(self, dataframes:list[pd.DataFrame]) -> None:
        """
        Sets private attributes to the validated dataframes that get used to calculate the submeasure

        Paramaters
        ----------
        dataframes
            A validated list of dataframes
        """
        self.__DATA__ = dataframes[0].sort_values('encounter_datetime').copy()
        self.__DIAGNOSIS__ = dataframes[1].sort_values('encounter_datetime').copy()
        self.__DEMOGRAPHICS__ = dataframes[2].sort_values('patient_id').copy()
        self.__INSURANCE__ = dataframes[3].sort_values('patient_id').copy()

    @override
    def _set_populace(self) -> None:
        """
        Sets all possible eligible clients for the denominator
        """
        self.__initilize_populace()
        self.__set_index_visits()
        self.__index_visits__['patient_measurement_year_id'] = self.__create_patient_measurement_year_id(self.__index_visits__['patient_id'],self.__index_visits__['encounter_datetime'])

    def __initilize_populace(self) -> None:
        """
        Sets populace data from the init's data
        """
        self.__populace__ = self.__DATA__.sort_values(by=['patient_id','encounter_datetime']).copy()

    def __set_index_visits(self) -> None:
        """
        Filters populace and finds the index visit for every patient
        """
        # Index Event Date:
        # The date on which the first instance of elevated PHQ-9 or PHQ-9M greater than nine
        # AND diagnosis of Depression or Dysthymia occurs during the Measurement Year
        index_visits = self.__populace__[self.__populace__['total_score'] > 9].copy() # get visits with scores greater than 9
        index_visits['measurement_year'] = index_visits['encounter_datetime'].dt.year # create year field to track returning patients across multiple years
        index_visits['patient_measurement_year_id'] = index_visits['patient_id'].astype(str) + '-' + index_visits['measurement_year'].astype(str)
        index_visits = index_visits.sort_values('encounter_datetime') # reorder visits by date
        index_visits = index_visits.drop_duplicates('patient_measurement_year_id',keep='first') # keep the first index visit per patient per year
        self.__index_visits__ = index_visits

    def __create_patient_measurement_year_id(self, ids:pd.Series, dates:pd.Series) -> pd.Series:
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
        return ids + '-' + (dates.dt.year).astype(str)

    @override
    def _remove_exclusions(self) -> None:
        """
        Filters exclusions from index visits
        """
        self.__filter_age()
        self.__filter_diagnoses()

    def __filter_age(self):
        """
        Calculates and removes patients under 12 at the date of their index visit
        """
        self.__calculate_age()
        self.__remove_under_age()

    def __calculate_age(self) -> None:
        """
        Calculates patient age at the date of index visit
        """
        self.__index_visits__['age'] = (self.__index_visits__['encounter_datetime'] - self.__index_visits__['patient_DOB']).apply(lambda val: val.days//365.25)
    
    def __remove_under_age(self) -> None:
        """
        Removes all patients who were under 12 at the date of index visit
        """
        self.__index_visits__ = self.__index_visits__[self.__index_visits__['age'] >= 12].copy()

    def __filter_diagnoses(self) -> None:
        """
        Finds and removes all patients with an invalid ICD10 code prior to the end of thier remission period
        """
        exclusions = self.__get_all_exclusions()
        self.__determine_exclusion_date_range()
        exclusions = self.__compare_exclusions_with_range(exclusions)
        self.__filter_out_exclusions(exclusions)

    def __get_all_exclusions(self) -> pd.DataFrame:
        """
        Filters DIAGNOISIS by icd10 codes that would exclude a patient from the denominator
        
        Returns
        -------
        pd.Dataframe
            All patient encounters with a diagnoses that makes them invalid for the denominator
        """
        icd10_exclusion_codes = [
            # Bipolar Disorder
            "F30.10", "F30.11", "F30.12", "F30.13", "F30.2", "F30.3", "F30.4", "F30.8", "F30.9",
            "F31.0", "F31.10", "F31.11", "F31.12", "F31.13", "F31.2", "F31.30", "F31.31", "F31.32",
            "F31.4", "F31.5", "F31.60", "F31.61", "F31.62", "F31.63", "F31.64", "F31.70", "F31.71",
            "F31.72", "F31.73", "F31.74", "F31.75", "F31.76", "F31.77", "F31.78", "F31.81", "F31.89",
            "F31.9",
            # Personality Disorder
            "F34.0", "F60.3", "F60.4", "F68.10", "F68.11", "F68.12", "F68.13",
            # Schizophrenia or Psychotic Disorder
            "F20.0", "F20.1", "F20.2", "F20.3", "F20.5", "F20.81", "F20.89",
            "F20.9", "F21", "F23", "F25.0", "F25.1", "F25.8", "F25.9", "F28", "F29",
            # Parvasion Development
            "F84.0", "F84.3", "F84.8", "F84.9",
            # palliative care service
            "Z51.1"
        ]
        return self.__DIAGNOSIS__[self.__DIAGNOSIS__['diagnosis'].isin(icd10_exclusion_codes)].copy()

    def __determine_exclusion_date_range(self) -> None:
        """
        Calculates the exclusion date range for all index visits
        """
        # an exclusion can occur any time prior to the end of a patient's numerator Measurement Period (index visit date + 6 months + 60 days)
        self.__index_visits__['end_exclusion_range'] = self.__index_visits__.apply(lambda visit: datetime(
                                                                                (visit['encounter_datetime'] + pd.DateOffset(months=6) + pd.DateOffset(days=60)).year,
                                                                                (visit['encounter_datetime'] + pd.DateOffset(months=6) + pd.DateOffset(days=60)).month,
                                                                                (visit['encounter_datetime'] + pd.DateOffset(months=6) + pd.DateOffset(days=60)).day
                                                                            ).date() ,axis=1)

    def __compare_exclusions_with_range(self, exclusions:pd.DataFrame) -> list:
        """
        Finds patient measurement year ids with exclusions that occured during the exclusion range

        Paramaters
        ----------
        exclusions
            Encounters with a diagnosis that invalidates them from the submeasure
        
        Returns
        -------
        list
            Patient measurement year ids
        """
        # a visit is only excluded if the exclusion happened before the index visit's remission year/range
        # therefore it's needed to filter the exclusions to only the ones that occured durring that period
        exclusions.rename(columns={'encounter_datetime':'exclusion_date'},inplace=True)
        self.__index_visits__ = self.__index_visits__.merge(exclusions,how ='left', on='patient_id')
        exclusion_ids = self.__index_visits__[self.__index_visits__['exclusion_date'] <= self.__index_visits__['end_exclusion_range']]['patient_measurement_year_id'].drop_duplicates().to_list()
        return exclusion_ids

    def __filter_out_exclusions(self, exclusions:list) -> None:
        """
        Filters out all index groups from populace that have a valid exclusion 

        Parameters
        ----------
        exclusions
            Patient measurement year ids to exclude
        """
        self.__index_visits__['exclusion'] = self.__index_visits__['patient_measurement_year_id'].isin(exclusions) # check if the patient_measurement_year_id is in the exclusion list
        self.__index_visits__ = self.__index_visits__[~self.__index_visits__['exclusion']].copy() # filter out all invalid visits

    @override
    def _apply_time_constraint(self) -> None:
        """
        Doc String
        """
        pass
    
    @override
    def _find_performance_met(self) -> None:
        """
        All clients in the denominator who achieved Remission at Six Months
        as demonstrated by a Six Month (+/- 60 days) PHQ-9 score of less than five
        """
        frequency = relativedelta(months=6)
        range = relativedelta(days=60)
        self.__index_visits__['earliest_remission'] = self.__index_visits__['encounter_datetime'].dt.date + frequency - range
        self.__index_visits__['latest_remission'] = self.__index_visits__['encounter_datetime'].dt.date + frequency + range
        self.__index_visits__[['numerator','numerator_reason']] = self.__index_visits__.apply(lambda row:(pd.Series(self.__remission_check(row))),axis=1)
        self.__overwrite_populace()

    def __remission_check(self,iv:pd.Series) -> tuple[bool,str]:
        """
        Checks if a remission occured within the remmission period for all index visits

        Parameters
        ----------
        index_visit
            Patient's index visit

        Returns
        -------
        tuple[bool,str]
            bool
                numerator value
            str
                numerator description
        """
        index_group = self.__populace__[self.__populace__['patient_id'] == iv['patient_id']].copy()
        remission_group = index_group[(index_group['encounter_datetime'].dt.date >= iv['earliest_remission']) & (index_group['encounter_datetime'].dt.date <= (iv['latest_remission']))]
        has_remission = len(remission_group[remission_group['total_score'] < 5]) >= 1
        if has_remission:
            reason = "Has Remission"
        elif remission_group.empty: # the df could be empty b/c eiter the date filter OR nothing was given after the earliest remission date
            if datetime.now().date() < iv['earliest_remission']:
                reason = "Remission Period not Reached"
            else:
                reason = "No PHQ-9 Follow Up"
        else: # must have given a follow up, but scored too high
            reason = "No Remission"
        return has_remission,reason

    def __overwrite_populace(self) -> None:
        """
        Overwrites populace to the current index visits
        """
        self.__populace__ = self.__index_visits__.copy()

    @override
    def _set_stratification(self) -> None:
        """
        Initializes stratify by filtering populace
        """
        self.__stratification__ = self.__populace__[['patient_measurement_year_id','patient_id','patient_DOB','age','encounter_datetime']].sort_values(['encounter_datetime']).copy()

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
        self.__populace__['age'] = self.__populace__['age'].apply(lambda age: '18+' if age >= 18 else '12-18')

    def __set_insurance_data(self) -> None:
        """
        Sets insurance stratification at the time of the index visit
        """
        medicaid_data = self.__INSURANCE__.merge(self.__stratification__[['patient_id','encounter_datetime']], how='right')
        medicaid_data = self.__filter_insurance_dates(medicaid_data) # gets insurances at time of encounter, "losing" patients
        medicaid_data['patient_measurement_year_id'] = self.__create_patient_measurement_year_id(medicaid_data['patient_id'],medicaid_data['encounter_datetime'])
        results = self.__determine_medicaid_stratify(medicaid_data)
        self.__stratification__ = self.__stratification__.merge(results,how='left')
        self.__stratification__['medicaid'] = self.__stratification__['medicaid'].fillna(False) # replace all the "lost" patients from above without insurance

    def __filter_insurance_dates(self,medicaid_data:pd.DataFrame) -> pd.DataFrame:
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
        medicaid_data['end_datetime'] = medicaid_data['end_datetime'].fillna(datetime.now()) # replace nulls with today so that they don't get filtered out
        medicaid_data['valid'] = (medicaid_data['start_datetime'] <= medicaid_data['encounter_datetime']) & (medicaid_data['end_datetime'] >= medicaid_data['encounter_datetime']) # checks if the insurance is valid at time of encounter
        return medicaid_data[medicaid_data['valid']]

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
        return plan.str.lower().str.contains('medicaid')

    def __replace_medicaid_values(self, col:pd.Series) -> pd.Series:
        """
        Replaces Boolean values with numerical values
        
        Paramaters
        ----------
        col
            Is insurance medicaid

        Returns
        -------
        pd.Series
            Numerical representaion of the bool
        """
        return col.map({True:1,False:2})

    def __find_patients_with_only_medicaids(self, medicaid_data:pd.DataFrame) -> pd.DataFrame:
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
        medicaid_data = medicaid_data.merge(self.__stratification__[['patient_id','encounter_datetime']],on=['patient_id','encounter_datetime'],how='right')
        return (medicaid_data.groupby(['patient_measurement_year_id'])['medicaid'].sum() == 1).reset_index()

    @override
    def _fill_blank_stratification(self) -> None:
        """
        Fills all null values with 'Unknown'
        """
        self.__stratification__ = self.__stratification__.fillna('Unknown')

    @override
    def _set_final_denominator_data(self) -> None:
        """
        Sets the populace data to the unique data points that are needed for the denominator
        """
        self.__add_in_stratification_columns()
        self.__remove_unneeded_populace_columns()

    def __add_in_stratification_columns(self) -> None:
        """
        Merges in stratification columns that are unique to the measurement year
        """
        self.__populace__ = pd.merge(self.__populace__,self.__stratification__[['patient_measurement_year_id','medicaid']])

    def __remove_unneeded_populace_columns(self) -> None:
        """
        Removes all columns that were used to calculate data points 
        """
        self.__populace__ = self.__populace__[['patient_id','patient_measurement_year_id','age','encounter_id','numerator','numerator_reason']].drop_duplicates()

    @override
    def _trim_unnecessary_stratification_data(self) -> None:
        """
        Removes all data that isn't needed for the Submeasure's stratification 
        """
        self.__stratification__ = self.__stratification__[['patient_id','ethnicity','race']].drop_duplicates()

    @override
    def _sort_final_data(self) -> None:
        """
        Sorts the Populace and Stratification dataframes
        """
        self.__populace__ = self.__populace__.sort_values('patient_measurement_year_id')
        self.__stratification__ = self.__stratification__.sort_values('patient_id')

class Dep_Rem(Measurement):
    """
    The DEP-REM-6 measure calculates the Percentage of clients (12 years of age or older) with
    Major Depression or Dysthymia who reach Remission Six Months (+/- 60 days) after an Index
    Event Date

    Parameters
    ----------
    sub1_data
        List of dataframes containing all needed data to calculate submeasure 1

    Notes
    -----
    sub1_data must follow the its `Schema` as defined by the `Validation_Factory` in order to ensure the `submeasure` can run properly

    >>> DEP_REM_sub_1 = [
    >>>     "PHQ9",
    >>>     "Diagnostic_History",
    >>>     "Demographic_Data",
    >>>     "Insurance_History"
    >>> ]

    >>> PHQ9 = {
    >>>     "patient_id": (str, 'object'),
    >>>     "patient_DOB": ("datetime64[ns]",),
    >>>     "encounter_id": (str, 'object'),
    >>>     "encounter_datetime": ("datetime64[ns]",),
    >>>     "total_score": (int, float)
    >>> }

    >>> Diagnostic_History = {
    >>>     "patient_id": (str, 'object'),
    >>>     "encounter_datetime": ("datetime64[ns]",),
    >>>     "diagnosis": (str, 'object')
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
        super().__init__("DEP_REM")
        self.__sub1__: Submeasure = _Sub_1(self.get_name() + "_sub_1",sub1_data)
    
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
    