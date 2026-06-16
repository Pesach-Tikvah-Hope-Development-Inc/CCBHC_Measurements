import pandas as pd
from datetime import datetime
from ccbhc_measurements.compat.typing_compat import override
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
        dataframes
            0 - Populace
            1 - Diagnoses
            2 - Demographics
            3 - Insurance
        """
        self.__DATA__ = dataframes[0].copy() 
        self.__DIAGNOSIS__ = dataframes[1].copy()
        self.__DEMOGRAPHICS__ = dataframes[2].copy()
        self.__INSURANCE__ = dataframes[3].copy()

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
        Gets the stratification dataframe 

        Returns 
        -------
        pd.DataFrame
            The stratification dataframe
        """
        return self.__stratification__.copy()
    
    @override 
    def _set_populace(self) -> None:
        """
        Sets all possible eligible clients for the denominator
        """
        self.__initialize_populace()
        self.__populace__['patient_measurement_year_id'] = self.__create_measurement_year_id(self.__populace__['patient_id'], self.__populace__['encounter_datetime'])

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
        Calculates age and excludes everyone not between 12 and 17 years old
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
        b = self.__get_bipolars()
        self.__filter_mental_exclusions(b)

    def __get_bipolars(self) -> pd.DataFrame:
        """
        Gets all bipolar diagnoses

        Returns
        -------
        pd.DataFrame
            The dataframe containing all bipolar diagnoses
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
        Removes all patients whose first diagnosis (depression or bipolar) occurred
        before their eligible encounter

        Parameters
        ----------
        exclusions
            The dataframe containing all diagnoses to be excluded
        """
        # for each patient, find the date of their first-ever diagnosis
        first_diag = (
            exclusions
            .sort_values(by=['patient_id', 'encounter_datetime'])
            .drop_duplicates(subset='patient_id', keep='first')
            .loc[:, ['patient_id', 'encounter_datetime']]
            .rename(columns={'encounter_datetime': 'first_diag_date'})
        )
        # merge first-diagnosis date into the current denominator (self.__populace__)
        pop = self.__populace__.merge(first_diag, how='left', on='patient_id')
        # keep only those encounters that happened before the first diagnosis,
        # or any patient who never had a diagnosis (first_diag_date is NaN)
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
        self.__ensure_screening_types()
        self.__assign_screening_encounter_id()
        self.__determine_screenings_results()
        self.__match_follow_ups_to_screenings()
        self.__create_numerator_desc()
        self.__get_numerator_encounter()

    def __ensure_screening_types(self) -> None:
        """
        Voids any screening that was not administered with an approved depression tool
 
        Notes
        -----
        Only PHQ-9, PHQA, and PSC-17 are valid depression screening tools for this measure.
        """
        # make all screenings uppercase to avoid input differences
        self.__populace__['screening_type'] = self.__populace__['screening_type'].str.upper()
        # keep the rows with valid screening types, void everything else
        valid_screening_types = ('PHQ9', 'PHQA', 'PSC-17')
        is_valid_screening = self.__populace__['screening_type'].isin(valid_screening_types)
        self.__populace__.loc[~is_valid_screening, ['screening_type', 'total_score']] = None

    def __assign_screening_encounter_id(self) -> None:
        """
        Assigns screening_encounter_id to the encounter_id where the total_score is not null in order to find screenings
        """
        self.__populace__['screening_encounter_id'] = (
            self.__populace__['encounter_id']
            .where(self.__populace__['total_score'].notna()) 
        )

    def __determine_screenings_results(self) -> None:
        """
        For each screening type, determine if it is positive or negative based on the total_score
        """
        def is_positive(r):
            if pd.isna(r['total_score']):
                return False
            if r['screening_type'] in ('PHQ9', 'PHQA'):
                return r['total_score'] > 9
            if r['screening_type'] == 'PSC-17':
                return r['total_score'] > 14 
            return False

        self.__populace__['positive_screening'] = self.__populace__.apply(is_positive, axis=1)

    def __match_follow_ups_to_screenings(self) -> None:
        """
        Flags positive screenings that have a qualifying follow up encounter within 14 days
        """
        populace = self.__initialize_follow_up_flag(self.__populace__.copy())
        positive_screenings = self.__get_positive_screenings(populace)
        follow_up_encounters = self.__get_follow_up_encounters(self.__DATA__.copy())
        matched_screening_ids = self.__find_matched_screening_ids(positive_screenings, follow_up_encounters)
        self.__populace__ = self.__set_matched_follow_ups(populace, matched_screening_ids)

    def __initialize_follow_up_flag(self, populace:pd.DataFrame) -> pd.DataFrame:
        """
        Ensures the has_matched_follow_up column exists

        Parameters
        ----------
        populace
            The deduped denominator set (one row per patient measurement year)

        Returns
        -------
        pd.DataFrame
            The populace with a boolean has_matched_follow_up column

        Notes
        -----
        Every screening starts unmatched and only flips to True once a qualifying follow up is found,
        so unmatched screenings fall through to numerator=False without any extra handling
        """
        if 'has_matched_follow_up' not in populace.columns:
            populace['has_matched_follow_up'] = False
        return populace

    def __get_positive_screenings(self, populace:pd.DataFrame) -> pd.DataFrame:
        """
        Gets the positive screenings that need a follow up matched to them

        Parameters
        ----------
        populace
            The deduped denominator set

        Returns
        -------
        pd.DataFrame
            The positive screenings (the anchors of the match)
        """
        is_positive = populace['positive_screening'] == True
        return populace[is_positive][['patient_id','encounter_id','encounter_datetime']].copy()

    def __get_follow_up_encounters(self, encounters:pd.DataFrame) -> pd.DataFrame:
        """
        Gets every encounter where a follow up plan was documented

        Parameters
        ----------
        encounters
            The full encounter set coming from the starting data (includes the follow_up flag per encounter)

        Returns
        -------
        pd.DataFrame
            Encounters flagged as follow ups
        """
        # without the flag there is nothing to match against, so return an empty frame
        # giving the empty frame a real datetime dtype keeps the date math
        # in __find_matched_screening_ids from breaking on this path
        if 'follow_up' not in encounters.columns:
            return pd.DataFrame({
                'patient_id':pd.Series(dtype=str),
                'encounter_id':pd.Series(dtype=str),
                'encounter_datetime':pd.Series(dtype='datetime64[ns]')
            })
        # upstream can send the flag as 0/1, so force it into a real boolean before masking
        encounters['follow_up'] = encounters['follow_up'].astype(bool)
        is_follow_up = encounters['follow_up']
        return encounters[is_follow_up][['patient_id','encounter_id','encounter_datetime']].copy()

    def __find_matched_screening_ids(self, positive_screenings:pd.DataFrame, follow_up_encounters:pd.DataFrame) -> pd.Series:
        """
        Finds which positive screenings have a follow up encounter within the 14 day window

        Parameters
        ----------
        positive_screenings
            The positive screenings needing a follow up
        follow_up_encounters
            Encounters where a follow up plan was documented

        Returns
        -------
        pd.Series
            The encounter ids of every matched screening

        Notes
        -----
        The window is forward only per the SAMHSA FAQ update,
        so the follow up must land 0 to 14 days AFTER the screening
        """
        WINDOW_DAYS = 14
        # pair every positive screening with all of that patient's follow up encounters
        # the left merge keeps unmatched screenings around as NaT rows, which fail the window masks below
        paired = positive_screenings.merge(
            follow_up_encounters,
            on='patient_id',
            how='left',
            suffixes=('_screening','_follow_up')
        )
        days_between = paired['encounter_datetime_follow_up'] - paired['encounter_datetime_screening']
        follow_up_is_after_screening = days_between >= pd.Timedelta(days=0)
        follow_up_is_within_window = days_between <= pd.Timedelta(days=WINDOW_DAYS)
        # NOTE this mask is what rejects follow ups documented at the screening encounter itself (bug CA-02/CH-05)
        # removing it from the filter below credits same encounter follow ups per the spec
        follow_up_is_separate_encounter = paired['encounter_id_follow_up'] != paired['encounter_id_screening']
        # matched = paired[follow_up_is_after_screening & follow_up_is_within_window & follow_up_is_separate_encounter]
        matched = paired[follow_up_is_after_screening & follow_up_is_within_window]
        # a screening only needs one qualifying follow up, so drop the extra matches
        return matched['encounter_id_screening'].drop_duplicates()

    def __set_matched_follow_ups(self, populace:pd.DataFrame, matched_screening_ids:pd.Series) -> pd.DataFrame:
        """
        Marks the matched screenings in the populace

        Parameters
        ----------
        populace
            The deduped denominator set
        matched_screening_ids
            The encounter ids of every matched screening

        Returns
        -------
        pd.DataFrame
            The populace with has_matched_follow_up set

        Notes
        -----
        Only the boolean flag is persisted,
        the follow up encounters themselves never enter the populace
        """
        is_matched = populace['encounter_id'].isin(matched_screening_ids)
        populace.loc[is_matched,'has_matched_follow_up'] = True
        return populace

    def __create_numerator_desc(self) -> None:
        """
        Assigns numerator and numerator_desc for multiple False-reason cases
        """

        df = self.__populace__.copy()

        # normalize flags
        df['positive_screening']    = df.get('positive_screening', False)
        df['positive_screening']    = df['positive_screening'].fillna(False).astype(bool)
        df['has_matched_follow_up'] = df.get('has_matched_follow_up', False)
        df['has_matched_follow_up'] = df['has_matched_follow_up'].fillna(False).astype(bool)

        # 1) no screening
        no_screen = df[df['total_score'].isna()].copy()
        no_screen['numerator'] = False
        no_screen['numerator_desc'] = 'No screening recorded'

        # remaining
        rem = df.drop(index=no_screen.index)

        # 2) negatives
        neg = self.__set_negative_numerators(rem[rem['positive_screening'] == False].copy())

        # 3) positives
        pos = self.__set_positive_numerators(rem[rem['positive_screening'] == True].copy())

        # recombine
        self.__populace__ = pd.concat([no_screen, neg, pos], ignore_index=True)
    
    def __set_positive_numerators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Positive screenings only: numerator is driven by has_matched_follow_up.
        
        Parameters
        ----------
        df
            The dataframe containing only positive screenings

        Returns 
        -------
        pd.DataFrame
            The dataframe with numerator and numerator_desc set
        """
     
        df = df.copy()
        df['numerator'] = df['has_matched_follow_up']
        df['numerator_desc'] = df['has_matched_follow_up'].map({
            True:  'Positive screening with follow up',
            False: 'Positive screening without matched follow-up'
        })
        return df
    
    def __set_negative_numerators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Negative screenings count in the numerator.
        
        Parameters
        ----------
        df
            The dataframe containing only Negative screenings

        Returns 
        -------
        pd.DataFrame
            The dataframe with numerator and numerator_desc set
        """
        df = df.copy()
        df['numerator'] = True
        df['numerator_desc'] = 'Negative screening'
        return df

    def __get_numerator_encounter(self) -> None:
        """
        Resolves multiple encounters per patient within a measurement year down
        to a single representative encounter based on numerator priority.
        """
        # create a priority for patients with multiple encounters/numerator possibilities throughout the measurement year
        priority = [
            "Positive screening with follow up",
            "Positive screening without matched follow-up",
            "Negative screening",
            "No screening recorded",
        ]

        self.__populace__["numerator_desc"] = pd.Categorical(
            self.__populace__["numerator_desc"],
            categories=priority,
            ordered=True
        )
        # keep the highest occuring priority per patient per year
        self.__populace__ = self.__populace__.sort_values(
            by="numerator_desc"
        ).drop_duplicates(
            subset='patient_measurement_year_id',
            keep='first'
        )

    @override
    def _apply_time_constraint(self) -> None:
        """
        Checks to see if the follow up happened after the screening
        """
        # NOTE this is not needed, as counseling should happen in the same session as the screening
        # which is checked in __set_positive_numerator by last_encounter > screening_datetime
        pass

    @override
    def _set_stratification(self) -> None:
        """
        Initializes stratification by filtering populace.
        """
        self.__stratification__ = (
            self.__populace__[[
                'patient_measurement_year_id',
                'patient_id',
                'encounter_id',
                'encounter_datetime',
                'follow_up'
            ]]
            .sort_values(['patient_measurement_year_id', 'encounter_id'])
            .drop_duplicates('patient_measurement_year_id')
        )

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
        # merge on patient_id so we don’t accidentally multiply rows
        self.__stratification__ = self.__stratification__.merge(
            to_merge,
            on='patient_id',
            how='left'
        )

    @override
    def _set_encounter_stratification(self) -> None:
        """
        Sets encounter stratifications from dataframe (medicaid)
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

    def __get_medicaid_from_df(self) -> pd.DataFrame: 
        """
        Gets patients' relevant insurance information

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

        Parameters
        ----------
        medicaid_data
            Insurance data

        Returns 
        -------
        pd.DataFrame
            The dataframe containing all patients' insurance information and stratification data
        """
        return medicaid_data.merge(
            self.__stratification__[["patient_id", "encounter_datetime"]],
            on=["patient_id"],
            how="left"
            )
    
    def __filter_insurance_dates(self, medicaid_data:pd.DataFrame) -> pd.DataFrame:
        """
        Keeps only those insurance rows whose coverage window includes the encounter_datetime.
        """
        # Fill null end dates with today
        medicaid_data['end_datetime'] = medicaid_data['end_datetime'].fillna(datetime.now())

        # A plan is valid if start <= encounter_datetime <= end
        mask = (
            (medicaid_data['start_datetime'] <= medicaid_data['encounter_datetime']) &
            (medicaid_data['end_datetime']   >= medicaid_data['encounter_datetime'])
        )
        return medicaid_data.loc[mask].copy()

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
        return plan.str.contains('medicaid',case=False)
    
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
        Keeps only the required columns (including follow_up and medicaid) in the populace.
        """
        self.__populace__ = self.__populace__[
            [
                "patient_measurement_year_id",
                "patient_id",
                "encounter_id",
                "screening_encounter_id",
                "numerator",
                "numerator_desc",
                "follow_up",
                "medicaid",
            ]
        ].drop_duplicates(subset="patient_measurement_year_id")

    @override
    def _trim_unnecessary_stratification_data(self) -> None:
        """
        Keeps one row per patient_id in the stratification dataframe
        """
        self.__stratification__ = self.__stratification__[['patient_id', 'ethnicity', 'race']].drop_duplicates(subset='patient_id')

    @override
    def _sort_final_data(self) -> None:
        """
        Sorts the Populace and Stratification dataframes
        """
        self.__populace__ = self.__populace__.sort_values('patient_measurement_year_id')
        self.__stratification__ = self.__stratification__.sort_values('patient_id')

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
        self.__sub1__: Submeasure = _Sub_1(self.name + "_sub_1", sub1_data)

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
