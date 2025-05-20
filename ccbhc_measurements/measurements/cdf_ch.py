from typing import override
from datetime import datetime
import pandas as pd
from ccbhc_measurements.abstractions.measurement import Measurement
from ccbhc_measurements.abstractions.submeasure import Submeasure

class _Sub_1(Submeasure):
    """
    Percentage of minors screened for depression during the measurement year
    using an age-appropriate standardized depression screening tool,
    and if positive, a follow-up plan is documented on the date of the eligible encounter
    """

    @override 
    def _set_dataframes(self, dataframes:list[pd.DataFrame]) -> None:
        """
        Sets private attributes to the validated dataframes that get used to calculate the submeasure

        Parameters
        ----------
        dataframse
            0 - Populace
            1 - Diagnoses
            2 - Screenings
            3 - Demographics
            4 - Insurance
        """
        self.__DATA__ = dataframes[0].copy() 
        self.__DIAGNOSIS__ = dataframes[1].copy()
        self.__SCREENINGS__ = dataframes[2].copy()
        self.__DEMOGRAPHICS__ = dataframes[3].copy()
        self.__INSURANCE__ = dataframes[4].copy()

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
        self.__populace__['patient_measurement_year_id'] = self.__create_measurement_year_id(self.__populace__['patient_id'],self.__populace__['encounter_datetime'])
        self.__populace__ = self.__populace__.sort_values(by=['patient_measurement_year_id','encounter_datetime']).drop_duplicates('patient_measurement_year_id',keep='first')

    def __initialize_populace(self) -> None:
        """
        Sets populace data from the init's data
        """
        self.__populace__ = self.__DATA__.copy()

    def __create_measurement_year_id(self, patient_id:pd.Series, date:pd.Series) -> pd.Series:
        """
        Creates a unique id to match patients to their coresponding measurement year

        Parameters
        ----------
        patient_id
            The patient id of the client
        date
            The date of the encounter
            
        Returns
        -------
        pd.Series
            The unique measurement year id
        """
        return patient_id.astype(str) + '-' + date.dt.year.astype("Int64").astype(str)
    
    @override
    def _remove_exclusions(self) -> None:
        """
        Filters exclusions from populace
        """
        # Denominator Exclusions:
        # All clients aged 17 years or younger 
        # All clients who have been diagnosed with depression or bipolar disorder
        self.__remove_age_exclusion()
        self.__remove_mental_exclusions()
    
    def __remove_age_exclusion(self) -> None:
        """
        Calculates and removes all clients older then 18 years
        """
        self.__calculate_age()
        self.__filter_age()

    def __calculate_age(self) -> None:
        """
        Calculates age of client at the date of service
        """
        self.__populace__['age'] = (self.__populace__['encounter_datetime'] - self.__populace__['patient_DOB']).dt.days // 365.25

    def __filter_age(self) -> None:
        """
        Removes all clients aged 18 or older
        """
        self.__populace__ = self.__populace__[(self.__populace__['age'] >= 12) & (self.__populace__['age'] <= 17)]

    def __remove_mental_exclusions(self) -> None:
        """
        Finds and removes all patients with a diagnosis of depression or bipolar
        prior to their measurement year
        """
        # get first‐ever diagnosis date per patient for each condition
        d = self.__get_depressions()
        b = self.__get_bipolars()
        # apply the same exclusion logic twice, once for depression, once for bipolar
        self.__filter_mental_exclusions(d)
        self.__filter_mental_exclusions(b)

    def __get_depressions(self) -> pd.DataFrame:
        """
        Return all depression diagnoses
        
        Returns
        -------
        pd.Dataframe
            Patients with depression ICD 10 codes
        """
        depression_codes = [
            'F01.51',
            'F32.A','F32.0','F32.1','F32.2','F32.3','F32.4','F32.5','F32.89','F32.9',
            'F33.0','F33.1','F33.2','F33.3','F33.40','F33.41','F33.42','F33.8','F33.9',
            'F34.1','F34.81','F34.89',
            'F43.21','F43.23',
            'F53.0','F53.1',
            'O90.6',
            'O99.340','O99.341','O99.342','O99.343','O99.345'
        ]
        return self.__DIAGNOSIS__[
            self.__DIAGNOSIS__['diagnosis'].isin(depression_codes)
        ].copy()

    def __get_bipolars(self) -> pd.DataFrame:
        """
        Return all bipolar diagnoses
        
        Returns
        -------
        pd.Dataframe
            Patients with bipolar ICD 10 codes
        """
        bipolar_codes = [
            'F31.10','F31.11','F31.12','F31.13',
            'F31.2',
            'F31.30','F31.31','F31.32',
            'F31.4',
            'F31.5',
            'F31.60','F31.61','F31.62','F31.63','F31.64',
            'F31.70','F31.71','F31.72','F31.73','F31.74','F31.75','F31.76','F31.77','F31.78',
            'F31.81','F31.89',
            'F31.9'
        ]
        return self.__DIAGNOSIS__[
            self.__DIAGNOSIS__['diagnosis'].isin(bipolar_codes)
        ].copy()

    def __filter_mental_exclusions(self, exclusions:pd.DataFrame) -> None:
        """
        Removes all patients whose first exclusion date is before their encounter

        Parameters
        ----------
        exclusions
            Dataframe with encounters that have exclusuionary ICD 10 codes
        """
        # for each patient, find the date of their first-ever diagnosis
        first_diag = (
            exclusions
            .sort_values(by=['patient_id', 'encounter_datetime'])
            .drop_duplicates(subset='patient_id', keep='first')
            .loc[:, ['patient_id', 'encounter_datetime']]
            .rename(columns={'encounter_datetime': 'first_diag_date'})
        )

        # merge that first-diagnosis date into the current denominator (self.__populace__)
        pop = self.__populace__.merge(first_diag, how='left', on='patient_id')

        # keep only those encounters that happened on or before the first diagnosis,
        #    or any patient who never had a diagnosis (first_diag_date is NaN)
        mask = (
            (pop['encounter_datetime'] <= pop['first_diag_date'])
            | pop['first_diag_date'].isna()
        )
        self.__populace__ = pop.loc[mask].drop(columns=['first_diag_date'])

    @override
    def get_numerator(self) -> None:
        """
        [Clients] screened for depression on the date of the encounter or 14 days prior to the
        date of the encounter using an age-appropriate standardized depression screening tool AND, if
        positive, a follow-up plan is documented on the date of the eligible encounter
        """
        # NOTE IMPORTANT the screening date has been since updated to being required once per measurement year, independent of an encounter date
        # https://www.samhsa.gov/sites/default/files/ccbhc-quality-measures-faq.pdf see p. 22 "At which encounters would screening need to occur?"
        try:
            super().get_numerator()
        except Exception:
            raise
    
    @override
    def _find_performance_met(self) -> None:
        """
        Assigns numerator and numerator_desc for multiple False-reason cases.
        """
        self.__add_screenings_to_populace() 
        self.__determine_screenings_results()
        self.__create_numerator_desc()

    def __add_screenings_to_populace(self) -> None:
        """
        Gets all screenings and adds them to populace
        """
        screenings = self.__get_screenings()
        screenings = self.__prep_screenings_for_merge(screenings)
        self.__populace__ = self.__populace__.merge(screenings, on='patient_measurement_year_id', how='left')

    def __get_screenings(self) -> pd.DataFrame:
        """
        Gets all screenings

        Returns
        -------
        pd.DataFrame
            The dataframe containing all clients screening results
        """
        return self.__SCREENINGS__.copy()

    def __prep_screenings_for_merge(self, screenings:pd.DataFrame) -> pd.DataFrame:
        """
        Fixes up screenings so that it can be merged into populace
        
        Parameters
        ----------
        screenings
            The screenings data
        
        Returns
        -------
        pd.DataFrame
            Prepped screenings data for merge
        """
        screenings['patient_measurement_year_id'] = self.__create_measurement_year_id(screenings['patient_id'],screenings['screening_date'])
        screenings = screenings.rename(columns={'encounter_id':'screening_encounter_id',
                                                'total_score':'screening_score'})
        # "The measure assesses the most recent depression screening completed..."
        screenings = screenings.sort_values(['patient_measurement_year_id','screening_date']).drop_duplicates('patient_measurement_year_id',keep='last')
        screenings = screenings.drop(columns={'patient_id'})
        screenings['screening_score'] = pd.to_numeric(screenings['screening_score'],errors='coerce')
        return screenings

    def __determine_screenings_results(self) -> None:
        """
        Creates a column showing if clients scored positive or negative on thier screening
        """
        # Having a score of 9- does not require a follow up plan
        # https://www.hiv.uw.edu/page/mental-health-screening/phq-9
        self.__populace__['positive_screening'] = self.__populace__['screening_score'] > 9
    
    def __create_numerator_desc(self) -> None:
        """
        Creates a numerator description column for populace
        """
        df = self.__populace__.copy()
        # No screening record
        no_screen = df[df['screening_date'].isna()].copy()
        no_screen['numerator'] = False
        no_screen['numerator_desc'] = 'No screening recorded'
        # Invalid or missing screening score
        invalid = df[df['screening_date'].notna() &df['screening_score'].isna()].copy()
        invalid['numerator'] = False
        invalid['numerator_desc'] = 'Invalid or missing screening score'
        # combine indexes of rows already marked as no_screen or invalid so they can be excluded
        used_idx = no_screen.index.union(invalid.index)
        # now we can select the remaining rows (not in used_idx) for later
        rem = df.loc[~df.index.isin(used_idx)].copy()
        # neg screenings (score <= 9)
        neg = rem[~rem['positive_screening']].copy()
        neg = self.__set_negative_numerators(neg)
        # pos screenings (score > 9)
        pos = rem[rem['positive_screening']].copy()
        pos = self.__set_positive_numerators(pos)
        self.__populace__ = pd.concat([no_screen, invalid, neg, pos], ignore_index=True)

    def __set_positive_numerators(self, positive_screenings:pd.DataFrame) -> pd.DataFrame: 
        """
        Adds numerator fields for patients with positive screening results,
        tagging those without follow-up with a descriptive reason

        Parameters
        ----------
        positive_screenings
            The screenings data
        
        Returns
        -------
        pd.DataFrame
            Positive screenings with numerator fields
        """
        follow_ups = self.__find_follow_ups()
        df = positive_screenings.merge(follow_ups, how='left')
        # Numerator = (patient has a lest encounter) & (the last encounter is more recent than the screening)
        df['numerator'] = (df['last_encounter'].notna() & (df['last_encounter'] > df['screening_date']))
        # Met: True
        met = df[df['numerator']].copy()
        met['numerator_desc'] = 'Positive screening with follow up'
        # Unmet: False
        unmet = df[~df['numerator']].copy()
        unmet['numerator_desc'] = 'Positive screening without follow-up'
        return pd.concat([met, unmet], ignore_index=True)
    
    def __set_negative_numerators(self, negative_screenings:pd.DataFrame) -> pd.DataFrame:
        """
        Adds numerator fields for patients with negative screening results

        Returns
        -------
        pd.DataFrame
            The dataframe containing all patients with negative screening results 
        """
        negative_screenings['numerator'] = True
        negative_screenings['numerator_desc'] = 'Negative screening'
        return negative_screenings

    def __find_follow_ups(self) -> pd.DataFrame: 
        """
        Finds the most recent encounter for clients with a positve screening

        Returns
        -------
        pd.DataFrame
            The dataframe with follow ups
        """
        # Referral to a provider for additional evaluation.
        # Pharmacological interventions.
        # Other interventions for the treatment of depression.
        last_encounters = self.__populace__.groupby('patient_id')['encounter_datetime'].max().to_frame().reset_index()
        last_encounters = last_encounters.rename(columns={'encounter_datetime':'last_encounter'})
        return last_encounters

    @override
    def _apply_time_constraint(self) -> None:
        """
        Checks to see if the follow up happened after the screening
        """
        # NOTE this is not needed, as counseling should happen in the same session as the screening
        # which is checked in __set_positive_numerator by last_encounter > screening_date
        pass

    @override 
    def _set_stratification(self) -> None:
        """
        Initializes stratify by filtering populace
        """
        self.__stratification__ = self.__populace__[[
                                                    'patient_measurement_year_id',
                                                    'patient_id',
                                                    'encounter_id',
                                                    'encounter_datetime',
                                                    'screening_date',
                                                    'last_encounter'
                                                ]].sort_values([
                                                    'patient_measurement_year_id',
                                                    'encounter_id'
                                                ]).drop_duplicates(
                                                    'patient_measurement_year_id'
                                                )
        self.__stratification__['measurement_year'] = self.__stratification__['patient_measurement_year_id'].str.split('-',expand=True)[1]
   
    @override
    def _set_encounter_stratification(self) -> None:
        """
        Sets stratification data that is encounter dependant 
        """
        medicaid_data = self.__get_medicaid_from_df()
        medicaid_data = self.__merge_mediciad_with_stratify(medicaid_data)
        medicaid_data = self.__filter_insurance_dates(medicaid_data)
        medicaid_data['patient_measurement_year_id'] = self.__create_measurement_year_id(medicaid_data['patient_id'],medicaid_data['encounter_datetime'])
        results = self.__determine_medicaid_stratify(medicaid_data)
        self.__stratification__ = self.__stratification__.merge(results,how='left')
        # patients that don't have any valid insurtance at their encounter date get completly filtered out and have a NaN instead of False
        # and would otherwise be filled with 'Unknown' by __fill_blank_stratify()
        self.__stratification__['medicaid'] = self.__stratification__['medicaid'].fillna(False).copy()

    @override
    def _set_patient_stratification(self) -> None:
        """
        Sets stratification data that is patient dependant
        """
        self.__set_patient_demographics()

    def __set_patient_demographics(self) -> None:
        """
        Merges demographics into stratification
        """
        # only keep one row per patient in the demographics table
        to_merge = (
            self.__DEMOGRAPHICS__
            [self.__DEMOGRAPHICS__['patient_id'].isin(self.__stratification__['patient_id'])]
            .drop_duplicates(subset=['patient_id'], keep='last')
        )
        self.__stratification__ = self.__stratification__.merge(to_merge,on='patient_id',how='left')

    def __get_medicaid_from_df(self) -> pd.DataFrame: 
        """
        Gets all relevant patients' insurance information

        Returns
        -------
        pd.DataFrame
            The dataframe containing all patients' insurance information
        """
        valid_patient_ids = self.__stratification__['patient_id'].astype(str).unique()
        # filter insurance to just those patients, then dedupe identical date ranges
        filtered_medicaid = (
            self.__INSURANCE__
            [self.__INSURANCE__['patient_id'].isin(valid_patient_ids)]
            .drop_duplicates(subset=['patient_id', 'start_datetime', 'end_datetime'], keep='last')
            .copy()
        )
        return filtered_medicaid

    def __merge_mediciad_with_stratify(self, medicaid_data:pd.DataFrame) -> pd.DataFrame: 
        """
        Merges stratify data on top of the medicaid data

        Returns 
        -------
        pd.DataFrame
            The dataframe containing all patients' insurance information and stratification data
        """
        return medicaid_data.merge(self.__stratification__[['patient_id','screening_date','encounter_datetime']],how='left')

    def __filter_insurance_dates(self, medicaid_data:pd.DataFrame) -> pd.Series:
        """
        Removes insurances that weren't active at the time of the patient's visit

        Parameters
        ----------
        medicaid_data
            Insurance data
        
        Returns
        -------
        pd.DataFrame
            Filtered insurance data
        """
        # replace nulls with today so that they don't get filtered out
        medicaid_data['end_datetime'] = medicaid_data['end_datetime'].fillna(datetime.now())
        # split medicaid in half so that patients without screenings don't get filtered out
        # the date comparison should use the screening date if it exists else use encounter date
        # by spliting the df O(n) remains constant and avoids df.apply()
        screening_visits = medicaid_data[medicaid_data['screening_date'].notna()].copy()
        encounter_visits = medicaid_data[medicaid_data['screening_date'].isna()].copy()
        screening_visits['valid'] = (screening_visits['start_datetime'] <= screening_visits['screening_date']) & (screening_visits['end_datetime'] >= screening_visits['screening_date']) # checks if the insurance is valid at time of screenimg
        encounter_visits['valid'] = (encounter_visits['start_datetime'] <= encounter_visits['encounter_datetime']) & (encounter_visits['end_datetime'] >= encounter_visits['encounter_datetime']) # checks if the insurance is valid at time of encounter
        medicaid_data = pd.concat([screening_visits,encounter_visits]).sort_values(['patient_id','encounter_datetime']).copy()
        return medicaid_data[medicaid_data['valid']].copy()

    def __determine_medicaid_stratify(self, medicaid_data:pd.DataFrame) -> pd.DataFrame:
        """
        Finds patients that have medicaid only for insurance

        Parameters
        ----------
        medicaid_data
            Insurance data
        
        Returns
        -------
        pd.DataFrame
            Insurance data with a column showing if the patient has medicaid only
        """
        medicaid_data['medicaid'] = self.__find_plans_with_medicaid(medicaid_data['insurance']) 
        medicaid_data['medicaid'] = self.__replace_medicaid_values(medicaid_data['medicaid'])
        medicaid_data = self.__find_patients_with_only_medicaids(medicaid_data)
        return medicaid_data

    def __find_plans_with_medicaid(self, plan:pd.Series) -> pd.Series:
        """
        Checks if the insurance name contains medicaid

        Parameters
        ----------
        plan
            The insurance plan name
        
        Returns
        -------
        pd.Series
            A boolean series showing if the insurance plan contains medicaid
        """
        return plan.str.contains('medicaid')
    
    def __replace_medicaid_values(self, col:pd.Series) -> pd.Series:
        """
        Replaces Boolean values with numerical values

        Parameters
        ----------
        col
            The column to be replaced

        Returns
        -------
        pd.Series
            The column with replaced values
        """
        return col.map({True:1,False:2})

    def __find_patients_with_only_medicaids(self, medicaid_data:pd.DataFrame) -> pd.DataFrame:
        """
        Calcutlates whether a patient has medicaid only or other insurance

        Parameters
        ----------
        medicaid_data
            The insurance data
        
        Returns
        -------
        pd.DataFrame
            The insurance data with a column showing if the patient has medicaid only
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

        self.__add_in_stratification_columns()
        self.__remove_unneeded_populace_columns()

    def __add_in_stratification_columns(self) -> None:
        """
        Merges in stratification columns that are unique to the measurement year
        """
        self.__populace__ = self.__populace__.merge(
            self.__stratification__[["patient_measurement_year_id", "medicaid"]],
            on="patient_measurement_year_id",
            how="left"
        )
  
    def __remove_unneeded_populace_columns(self) -> None:
        """
        Removes unneeded populace columns
        """
        self.__populace__ = self.__populace__[
            [
                "patient_measurement_year_id",
                "patient_id",
                "encounter_id",
                "screening_encounter_id",
                "last_encounter",
                "numerator",
                "numerator_desc",
                "medicaid",
            ]
        ].drop_duplicates(subset="patient_measurement_year_id")

    @override
    def _sort_final_data(self) -> None:
        """
        Sorts the populace and stratification dataframes
        """
        self.__populace__ = self.__populace__.sort_values('patient_measurement_year_id')
        self.__stratification__ = self.__stratification__.sort_values('patient_id')

    def _trim_unnecessary_stratification_data(self) -> None:
        """
        Removes unneeded stratification columns
        """
        self.__stratification__ = self.__stratification__[['patient_id','ethnicity','race']].drop_duplicates()

class CDF_CH(Measurement):
    """
    Percentage of beneficiaries [clients] ages 12 to 17 screened for depression on the date of the
    encounter or 14 days prior to the date of the encounter using an age-appropriate standardized
    depression screening tool, and if positive, a follow-up plan is documented on the date of the eligible encounter
    
    Parameters
    ----------
    sub1_data
        List of dataframes containing all needed data to calculate submeasure 1

    Notes
    -----
    sub1_data must follow the its `Schema` as defined by the `Validation_Factory` in order to ensure the `submeasure` can run properly

    Example
    -------
    >>> CDF_CH_sub_1 = [
    >>>     "Populace",
    >>>     "Diagnostic_History",
    >>>     "CDF_Screenings",
    >>>     "Demographic_Data",
    >>>     "Insurance_History"
    >>> ]

    >>> Populace = {
    >>>     "patient_id": (str, 'object'),
    >>>     "encounter_id": (str, 'object'),
    >>>     "encounter_datetime": ("datetime64[ns]",),
    >>>     "patient_DOB": ("datetime64[ns]",)
    >>> }

    >>> Diagnostic_History = {
    >>>     "patient_id": (str, 'object'),
    >>>     "encounter_datetime": ("datetime64[ns]",),
    >>>     "diagnosis": (str, 'object')
    >>> }

    >>> CDF_Screenings = {
    >>>     "patient_id": (str, 'object'),
    >>>     "encounter_id": (str, 'object'),
    >>>     "screening_date": ("datetime64[ns]",),
    >>>     "total_score": (int, float)
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
        super().__init__("CDF_CH")
        self.__sub1__: Submeasure = _Sub_1(self.get_name() + "_sub_1", sub1_data)

    @override
    def get_all_submeasures(self) -> dict[str,pd.DataFrame]:
        """
        Calculates all the data for the CDF_CH Measurement and its Submeasures

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
