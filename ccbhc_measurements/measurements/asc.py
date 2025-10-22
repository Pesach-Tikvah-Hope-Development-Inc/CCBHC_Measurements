import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from ccbhc_measurements.compat.typing_compat import override
from ccbhc_measurements.abstractions.measurement import Measurement
from ccbhc_measurements.abstractions.submeasure import Submeasure
from ccbhc_measurements.strategies.alcohol_screening_strategies import alcohol_screeners, get_screening_strategy

class _Sub_1(Submeasure):
    """
    Percentage of clients aged 18 years and older who were screened for unhealthy alcohol use
    using a Systematic Screening Method at least once within the last 12 months
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
        # NOTE this is a quick fix to make the front end nicer, the back end needs refactoring
        self.__DATA__ = dataframes[0].sort_values('encounter_datetime').copy()
        self.__REGULAR_VISITS__ = self.__get_regular_visits()
        self.__PREVENTIVE_VISITS__ = self.__get_preventitive_visits()
        screening_df = self.__get_screenings(dataframes[0].sort_values('encounter_datetime'))
        screening_df['patient_measurement_year_id'] = self.__create_patient_measurement_year_id(screening_df['patient_id'],screening_df['screening_datetime'])
        self.__SCREENINGS__ = screening_df.copy()
        self.__DIAGNOSIS__ = dataframes[1].sort_values('encounter_datetime').copy()
        self.__DEMOGRAPHICS__ = dataframes[2].sort_values('patient_id').copy()
        self.__INSURANCE__ = dataframes[3].sort_values('patient_id').copy()

    def __get_regular_visits(self) -> pd.DataFrame:
        """
        Returns
        -------
        pd.Dataframe
            Encounter details
        """
        return self.__DATA__[['patient_id','patient_DOB','encounter_id','encounter_datetime']].copy()

    def __get_preventitive_visits(self) -> pd.DataFrame:
        """
        Returns
        -------
        pd.Dataframe
            Preventitive encounter details
        """
        return self.__DATA__[['patient_id','patient_DOB','encounter_id','encounter_datetime','cpt_code']].copy()

    def __get_screenings(self, df:pd.DataFrame) -> pd.DataFrame:
        """
        Finds encounters that are valid screenings

        Parameters
        ----------
        df
            Dataframe containing all encounters

        Returns
        -------
        pd.Dataframe
            Screening details
        """
        df['screening_datetime'] = df['encounter_datetime'].copy()
        # create a mask for all valid screening types, alcohol_screeners is already in lower case
        df['screening'] = df['screening'].str.lower()
        valid_screenings = df['screening'].isin(alcohol_screeners)
        return df[valid_screenings][['patient_id','encounter_id','screening_datetime','screening','score']].sort_values('screening_datetime',ascending=False).copy()

    @override
    def _set_populace(self) -> None:
        """
        Sets all possible eligible clients for the denominator
        """
        self.__set_two_or_more_visits()
        self.__set_preventive_visits()
        self.__populace__['measurement_year'] = self.__get_year(self.__populace__['encounter_datetime'])

    def __set_two_or_more_visits(self) -> None:
        """
        Sets all patients who've had 2 or more visits per measurement year
        """
        visits = self.__REGULAR_VISITS__.copy()
        visits['patient_measurement_year_id'] = self.__create_patient_measurement_year_id(visits['patient_id'],visits['encounter_datetime'])
        multiple_visits = (visits.groupby('patient_measurement_year_id')['patient_id'].size() >= 2).reset_index()['patient_measurement_year_id'].to_list()
        self.__populace__ = visits[visits['patient_measurement_year_id'].isin(multiple_visits)].copy()

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

    def __set_preventive_visits(self) -> None:
        """
        Adds all patients who've had preventive visits during the measurement year to populace
        """
        if self.__PREVENTIVE_VISITS__.empty: # break out early if there are no preventive visits
            return
        preventive_visits = self.__get_preventive_visits()
        preventive_visits['patient_measurement_year_id'] = self.__create_patient_measurement_year_id(preventive_visits['patient_id'],preventive_visits['encounter_datetime'])
        self.__add_preventive_visits_to_populace(preventive_visits)

    def __get_preventive_visits(self) -> pd.DataFrame:
        """
        Gets all patients who've had preventive visits during the measurement year

        Returns
        -------
        pd.Dataframe
            Patients with a preventitive encounter
        """
        # preventive CPT Codes can be found at https://www.samhsa.gov/sites/default/files/ccbhc-quality-measures-technical-specifications-manual.pdf, pages 54,55
        preventive_cpt_codes = [
            '99385', '99386', '99387', '99395', '99396',
            '99397', '99401', '99402', '99403', '99404',
            '99411', '99412', '99429', 'G0438', 'G0439'
        ]
        df = self.__PREVENTIVE_VISITS__[self.__PREVENTIVE_VISITS__['cpt_code'].isin(preventive_cpt_codes)].copy()
        df = df.drop('cpt_code',axis=1).copy() # makes the columns parralel to those in REGUAR_VISITS, allowing for a smooth concat to populace
        return df

    def __add_preventive_visits_to_populace(self, preventive_visits:pd.DataFrame) -> None:
        """
        Adds preventive visits to populace
        """
        preventive_visits = preventive_visits[~preventive_visits['patient_measurement_year_id'].isin(self.__populace__['patient_measurement_year_id'])] # only need to add those without 2+ visits
        preventive_visits = preventive_visits.drop_duplicates(['patient_measurement_year_id']).copy()
        self.__populace__ = pd.concat([self.__populace__,preventive_visits])

    def __get_year(self, encounter_datetime:pd.Series) -> pd.Series:
        """
        Gets the year part of a date

        Parameters
        ----------
        Date
            Full date

        Returns
        -------
        pd.Series
            Year
        """
        return encounter_datetime.dt.year
    
    @override
    def _remove_exclusions(self) -> None:
        """
        Filters exclusions from populace
        """
        # Denominator Exclusions:
        # All clients aged 17 years or younger
        # OR Clients with dementia at any time during the patient’s history through the end of the Measurement Year
        # OR Clients who use hospice services any time during the Measurement Year
        self.__remove_age_exclusions()
        self.__remove_dementia_exclusions()
        # NOTE This is something we don't track, therefore it is commented out as I don't know how EHRs store this data and what it looks like
        # If someone can make a pull request and write this code, Thanks :)
        # self.__remove_hospice_exclusions() 

    def __remove_age_exclusions(self) -> None:
        """
        Calculates and removes all clients who are under 18
        """
        self.__calculate_age()
        self.__populace__ = self.__populace__[self.__populace__['age'] >= 18].copy()

    def __calculate_age(self) -> None:
        """
        Calculates age stratification at the time of encounter
        """
        self.__populace__['age'] = (self.__populace__['encounter_datetime'] - self.__populace__['patient_DOB']).apply(lambda val: val.days//365.25)

    def __remove_dementia_exclusions(self) -> None:
        """
        Finds all clients who have had dementia prior to the end of their measurement year and removes them
        """
        # Clients with dementia at any time during the patient’s history until the end of the Measurement Year
        dementia = self.__get_dementia_exclusions()
        dementia['patient_measurement_year_id'] = self.__create_patient_measurement_year_id(dementia['patient_id'], dementia['encounter_datetime'])
        dementia['exclusion_year'] = self.__get_year(dementia['encounter_datetime'])
        exclusion_ids = self.__compare_dementia_year_to_populace(dementia)
        self.__filter_dementia_exclusions(exclusion_ids)

    def __get_dementia_exclusions(self) -> pd.DataFrame:
        """
        Gets all patients with a dementia ICD diagnosis

        Returns
        -------
        pd.Dataframe
            Dementia diagnoses
        """
        # ICD codes for dementia can be found at https://www.icd10data.com/ICD10CM/Codes/F01-F99/F01-F09
        demantia_mask = self.__DIAGNOSIS__['diagnosis'].str.contains('F01|F02|F03')
        return self.__DIAGNOSIS__[demantia_mask].drop_duplicates() # use a generic drop_duplicates just to shave excess data

    def __compare_dementia_year_to_populace(self, dementia:pd.DataFrame) -> list:
        """
        Finds clients who've had dementia prior to the end of their measurement year
        
        Parameters
        ----------
        dementia
            All dementia diagnoses

        Returns
        -------
        list
            Patient IDs of patients with dementia 
        """
        unique_denominators = self.__populace__[['patient_id','measurement_year','patient_measurement_year_id']].drop_duplicates('patient_measurement_year_id')
        unique_denominators = unique_denominators.merge(dementia[['patient_id','exclusion_year']],how='left',left_on='patient_id',right_on='patient_id')
        unique_denominators['to_exclude'] = unique_denominators['measurement_year'] >= unique_denominators['exclusion_year']
        exclusion_ids = unique_denominators[unique_denominators['to_exclude']]['patient_measurement_year_id'].drop_duplicates().to_list()
        return exclusion_ids

    def __filter_dementia_exclusions(self, exclusion_ids:list) -> None:
        """
        Removes clients who've had dementia
        
        Parameters
        ----------
        exclusion_ids
            Patient IDs to be removed
        """
        self.__populace__ = self.__populace__[~self.__populace__['patient_measurement_year_id'].isin(exclusion_ids)].copy()

    @override
    def _apply_time_constraint(self) -> None:
        """
        Finds the most recent encounter per client per measurement year to be used for screening range
        """
        # For the purposes of the measure, the most recent denominator eligible encounter should
        # be used to determine if the numerator action for the submeasure was performed within
        # the 12-month look back period.
        self.__populace__ = self.__populace__.sort_values(['patient_measurement_year_id','encounter_datetime']).drop_duplicates(subset=['patient_measurement_year_id'],keep='last').copy()
        self.__populace__['earliest_screening_date'] = self.__populace__['encounter_datetime'].dt.date - relativedelta(months=12)
        self.__populace__['latest_screening_date'] = self.__populace__['encounter_datetime'].dt.date.copy()

    @override
    def _find_performance_met(self) -> None: 
        """
        Finds clients that have been screened within their screening range
        """
        screenings = self.__get_systematic_screenings()
        screening_groups = screenings.groupby('patient_id')
        # split populace into yes/no screenings allowing for screening_groups.get_group to not break on patients without screenings
        screening_mask = self.__populace__['patient_id'].isin(screenings['patient_id'])
        has_no_screening = self.__populace__[~screening_mask].copy()
        has_no_screening[['numerator','encounter_id']] = False, None
        has_screening = self.__populace__[screening_mask].copy()
        has_screening[['numerator','encounter_id']] = has_screening.apply(lambda row: self.__get_screening_details(row,screening_groups.get_group(row['patient_id'])),axis=1)
        self.__populace__ = pd.concat([has_screening,has_no_screening])

    def __get_systematic_screenings(self) -> pd.DataFrame:
        """
        Returns
        -------
        pd.Dataframe
            All screenings
        """
        return self.__SCREENINGS__.copy()

    def __get_screening_details(self, patient_data:pd.Series, screening_group:pd.Series) -> pd.Series:
        """
        Checks if the screening was during the screening date range

        Parameters
        ----------
        patient_data
            Data containing the patient's earliest and latest screening date
        sreening_group
            All screenings for the patient
        
        Returns
        -------
        pd.Series
            bool
                Was there a screening given within the screening date range
            str
                Id of the screening
        """
        screening_mask = (screening_group['screening_datetime'].dt.date >= patient_data['earliest_screening_date']) & (screening_group['screening_datetime'].dt.date <= patient_data['latest_screening_date'])
        valid_screenings = screening_group[screening_mask].copy()
        if len(valid_screenings) >= 1:
            return pd.Series({
                'numerator':True,
                'screening_id':valid_screenings['encounter_id'].iat[0]
            })
        return pd.Series({
                'numerator':False,
                'screening_id':None
            })

    @override
    def _set_stratification(self) -> None:
        """
        Initializes stratify by filtering populace
        """
        self.__stratification__ = self.__populace__[['patient_measurement_year_id','patient_id','patient_DOB','encounter_datetime']].sort_values(['encounter_datetime']).copy()

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
        self.__set_insurance_data()

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
            medicaid_data with a new column for medicaid stratification
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
        self.__remove_unneeded_populace_columns()
        self.__add_in_stratification_columns()

    def __remove_unneeded_populace_columns(self) -> None:
        """
        Removes all columns that were used to calculate data points 
        """
        self.__populace__ = self.__populace__[['patient_id','patient_measurement_year_id','encounter_id','numerator']].drop_duplicates() 

    def __add_in_stratification_columns(self) -> None:
        """
        Merges in stratification columns that are unique to the measurement year
        """
        self.__populace__ = pd.merge(self.__populace__,self.__stratification__[['patient_measurement_year_id','medicaid']])

    @override
    def _trim_unnecessary_stratification_data(self) -> None:
        """
        Removes all data that isn't needed to calculate the Submeasure's stratification 
        """
        self.__stratification__ = self.__stratification__[['patient_id','ethnicity','race']].drop_duplicates()

    @override
    def _sort_final_data(self) -> None:
        """
        Sorts the Populace and Stratification dataframes
        """
        self.__populace__ = self.__populace__.sort_values('patient_measurement_year_id')
        self.__stratification__ = self.__stratification__.sort_values('patient_id')

    def _get_sub2_subset(self) -> dict[str:pd.DataFrame]:
        """
        Gets the starting submeasure 2 populace and stratification data

        Retrurns
        --------
        Dictionary[str,pd.DataFrame]
            str
                Name of the data subset
            pd.Dataframe
                Data

        Notes
        -----
        Sub2 subset includes:
            - POPULACE
            - COUNSELINGS
            - STRATIFICATION
        """
        sub2_pop = self.__get_sub2_populace()
        sub2_counselings = self.__get_counselings()
        sub2_strat = self.__get_sub2_stratification(sub2_pop['patient_id'])
        return {
            'POPULACE':sub2_pop,
            'COUNSELINGS':sub2_counselings,
            'STRATIFICATION':sub2_strat
        } # return in capitals b/c the keys from sub2_subset.items() get used for __sub2__.__setattr__('__'+key+'__',val)

    def __get_sub2_populace(self) -> pd.DataFrame:
        """
        Gets the starting submeasure 2 populace

        Returns
        -------
        pd.Dataframe
            Initial submeasure 2 populace
        """
        sub2_pop = self.__initialize_sub2_populace()
        sub2_pop = self.__merge_sub2_patient_data(sub2_pop)
        sub2_pop = self.__merge_sub2_encounter_data(sub2_pop)
        sub2_pop['screening'] = sub2_pop['screening'].str.lower()
        sub2_pop['sex'] = sub2_pop['sex'].str.lower()
        return sub2_pop

    def __initialize_sub2_populace(self) -> pd.DataFrame:
        """
        Gets all patients who've had alcohol screenings

        Returns
        -------
        pd.Dataframe
            Patient screenings
        """
        screenings = self.__get_systematic_screenings()
        screenings['patient_measurement_year_id'] = self.__create_patient_measurement_year_id(screenings['patient_id'],screenings['screening_datetime'])
        sub2_ids = screenings['patient_measurement_year_id'].isin(self.__populace__['patient_measurement_year_id'])
        screenings = screenings[sub2_ids].copy()
        return screenings

    def __merge_sub2_patient_data(self, sub2_pop:pd.DataFrame) -> pd.DataFrame:
        """
        Merges in patient demographics

        Returns
        -------
        pd.Dataframe
            Populace
        """
        # merge in sex as it's needed for the screening strategy
        sub2_pop = sub2_pop.merge(self.__DEMOGRAPHICS__[['patient_id','sex']].drop_duplicates(),how='left')
        return sub2_pop

    def __merge_sub2_encounter_data(self, sub2_pop:pd.DataFrame) -> pd.DataFrame:
        """
        Merges in encounter stratification

        Returns
        -------
        pd.Dataframe
            Populace
        """
        # merge in medicaid as it's needed for the government's stratification
        sub2_pop = sub2_pop.merge(self.__populace__[['patient_measurement_year_id','medicaid']].drop_duplicates(),how='left')
        return sub2_pop

    def __get_counselings(self) -> pd.DataFrame:
        """
        Returns all brief counselings

        Note
        ----
        Brief counselings are defined by CPT code 'G2200'
        """
        counselings = self.__DATA__.copy()
        mask = counselings['cpt_code'].map(lambda row: 'G2200' in str(row))
        counselings = counselings[mask].copy()
        counselings = counselings[['patient_id','encounter_id','encounter_datetime']].copy()
        return counselings

    def __get_sub2_stratification(self, sub2_ids:pd.Series) -> pd.DataFrame:
        """
        Gets the starting submeasure 2 stratification

        Parameters
        ----------
        sub2_ids
            All submeasure 2 partient IDs

        Returns
        -------
        pd.Dataframe
            Initial submeasure 2 stratification
        """
        return self.__stratification__[self.__stratification__['patient_id'].isin(sub2_ids)].copy()

class _Sub_2(Submeasure):
    """
    Percentage of clients who were identified as unhealthy alcohol users and who recieved brief counseling
    """

    @override
    def get_submeasure_data(self) -> dict[str:pd.DataFrame]:
        """
        Calls all functions of the submeasure

        Returns
        -------
        Dictionary[pd.DataFrame:pd.DataFrame]
            str
                Name of the data
            pd.Dataframe
                Calculated data
        
        Raises
        ------
        AttributeError
            When the sub1 data is not set
        """
        if not self.__sub1_subset__:
            raise AttributeError("ASC Sub 2 is a subset of ASC Sub 1. Do not call ASC.__sub2__.get_submeasure_data() directly!")
        else:
            return super().get_submeasure_data()

    @override
    def _set_dataframes(self, dataframes:list[pd.DataFrame]) -> None:
        """
        Sets private attributes to the validated dataframes that get used to calculate the submeasure

        Paramaters
        ----------
        dataframes
            List of dataframes
        """
        # not sure what to do with this b/c sub2 piggy backs off of sub1's final data
        pass
    
    @override
    def _set_populace(self) -> None:
        """
        Sets the initial population for the denominator
        """
        self.__initialize_populace()
        self.__calculate_screening_results()
        self.__filter_unhealthy_alcohol_users()
        self.__get_most_recent_screening()

    def __initialize_populace(self) -> None:
        """
        Sets populace data from the init's data
        """
        self.__populace__ = self.__POPULACE__.copy()

    def __calculate_screening_results(self) -> None:
        """
        Calculates if patients are healthy or unhealthy alcohol users
        """
        for screener in alcohol_screeners:
            df = self.__populace__[self.__populace__['screening'] == screener].copy()
            screening_logic = get_screening_strategy(screener)
            df['unhealthy_alcohol_use'] = screening_logic(df)
            df = df[['patient_measurement_year_id','unhealthy_alcohol_use']].copy()
            self.__populace__ = self.__populace__.combine_first(df)

    def __filter_unhealthy_alcohol_users(self) -> None:
        """
        Filters populace to unhealthy alcohol users
        """
        self.__populace__ = self.__populace__[self.__populace__['unhealthy_alcohol_use']].copy()

    def __get_most_recent_screening(self) -> None:
        """
        Filters populace to the most recent unhealthy screening result
        """
        # for patients with multiple screenings, the most recent unhealthty screening should be used 
        # this is per patient, per measurement year
        self.__populace__ = self.__populace__.sort_values(['patient_measurement_year_id','screening_datetime'],ascending=True).copy()
        self.__populace__ = self.__populace__.drop_duplicates('patient_measurement_year_id',keep='last').copy()

    @override
    def _remove_exclusions(self) -> None:
        """
        Removes any exclusions from the population
        """
        # not sure what to do with this b/c sub2 piggy backs off of sub1's final data
        pass

    @override
    def _apply_time_constraint(self) -> None:
        """
        Applies time constraints to the denominator populace
        """
        # not sure what to do with this b/c sub2 piggy backs off of sub1's final data
        pass

    @override
    def _find_performance_met(self) -> None:
        """
        Checks if patients received brief counseling
        """
        counselings = self.__get_counselings().sort_values('encounter_datetime')
        self.__check_counselings(counselings)

    def __get_counselings(self) -> pd.DataFrame:
        """
        Returns
        -------
        pd.Dataframe
            Brief counselings
        """
        return self.__COUNSELINGS__.copy()

    def __check_counselings(self, counselings:pd.DataFrame) -> None:
        """
        Checks if the a counseling happened and how close it was to the screening

        Parameters
        ----------
        counselings
            Brief counselings
        """
        # in case the counseling was in the next measurement year use group_by('patient_id')
        # instead of creating/merging on patient_measurement_year_id for counselings for the reason column
        # split populace into 2 groups so the groups.get_group(patient_id) doesn't break on patients without counselings
        groups = counselings.groupby('patient_id')
        has_counseling = counselings['patient_id'].unique()
        numerator_candidates = self.__populace__['patient_id'].isin(has_counseling)
        if numerator_candidates.sum() >= 1:
            possible_numerators = self.__populace__[numerator_candidates].copy()
            denominators = self.__populace__[~numerator_candidates].copy()
            
            possible_numerators[['numerator','numerator_desc','counseling_id']] = possible_numerators.apply(lambda row: (pd.Series(self.__create_numerator_values(row,groups.get_group(row['patient_id'])))),axis=1)
            denominators[['numerator','numerator_desc','counseling_id']] = [False,'Counseling did not happen',None]

            self.__populace__ = pd.concat([possible_numerators,denominators])
        else:
            self.__populace__[['numerator','numerator_desc','counseling_id']] = [False,'Counseling did not happen',None]

    def __create_numerator_values(self, row:pd.Series, counselings:pd.DataFrame) -> tuple[bool,str,str]:
        """
        Creates a numerator value and an offset of how soon after the counseling happened

        Parameters
        ----------
        row
            Patient screening details
        counselings
            Patient counseling details

        Returns
        -------
        tuple[bool,str,str]
            bool
                Was there a counseling
            str
                When was the counseling
            str
                Counseling id

        Notes
        -----
        Ideally brief counselling should occur at the same encounter (or at the encounter most closely following 
        the positive screening if it was administered in advance of the visit) but that may not always happen

        The numerator value will only be `True` if the counseling happened on the same day as the screening screening
        therefore, there is a `reason` column to show if there was a counseling soon after the screening
        """
        screening = row['screening_datetime']
        numerator = False
        counseling_after_screening = screening <= counselings['encounter_datetime']
        counseling_within_2_months = screening + pd.DateOffset(months=2) >= counselings['encounter_datetime']
        # allow some flexibility for the counseling but try to keep the time frame reasonable
        counseling_mask = counseling_after_screening & counseling_within_2_months
        valid_counselings = counselings[counseling_mask]
        if not len(valid_counselings): # break out if there are no valid counselings
            return False,'Counseling did not happen',None
        first_counseling_date = valid_counselings['encounter_datetime'].head(1).item() # counselings are sorted by datetime in _find_performance_met()
        first_counseling_id = valid_counselings['encounter_id'].head(1).item()
        offset = (first_counseling_date - screening).days
        if offset == 0:
            numerator = True
            time_delay = 'Counseling happened immediately'
        elif offset <= 7:
            time_delay = 'Counseling happened within a week'
        elif offset <= 30:
            time_delay = 'Counseling happened within a month'
        else:
            time_delay = 'Counseling happened within two months'
        return numerator, time_delay, first_counseling_id

    @override
    def _set_stratification(self) -> None:
        """
        Sets initial population for the stratification
        """
        self.__stratification__ = self.__STRATIFICATION__.copy()

    @override
    def _set_patient_stratification(self) -> None:
        """
        Sets stratification data that is patient dependant
        """
        # not sure what to do with this b/c sub2 piggy backs off of sub1's final data
        pass

    @override
    def _set_encounter_stratification(self) -> None:
        """
        Sets stratification data that is encounter dependant
        """
        # not sure what to do with this b/c sub2 piggy backs off of sub1's final data
        pass

    @override
    def _fill_blank_stratification(self) -> None:
        """
        Fills all blank values in the stratification
        """
        # not sure what to do with this b/c sub2 piggy backs off of sub1's final data
        pass

    @override
    def _set_final_denominator_data(self) -> None:
        """
        Sets all data that is needed and unique to the Submeasure's denominator populace
        """
        self.__remove_unneeded_populace_columns()
        
    def __remove_unneeded_populace_columns(self) -> None:
        """
        Removes all columns that were used to calculate data points 
        """
        self.__populace__ = self.__populace__[['patient_id','patient_measurement_year_id','counseling_id','numerator','numerator_desc','medicaid']].copy()

    @override
    def _trim_unnecessary_stratification_data(self) -> None:
        """
        Removes all data that isn't needed for the Submeasure's stratification
        """
        self.__stratification__ = self.__stratification__[self.__stratification__['patient_id'].isin(self.__populace__['patient_id'])].copy()

    @override
    def _sort_final_data(self) -> None:
        """
        Sorts the Populace and Stratification dataframes

        """
        self.__populace__ = self.__populace__.sort_values('patient_measurement_year_id').copy()
        self.__stratification__ = self.__stratification__.sort_values('patient_id').copy()

class ASC(Measurement):
    """
    The ASC measure calculates the Percentage of clients aged 18 years and older who were
    screened for unhealthy alcohol use using a Systematic Screening Method at least once within the
    last 12 months AND who received brief counseling if identified as an unhealthy alcohol user

    Parameters
    ----------
    sub1_data
        List of dataframes containing all needed data to calculate submeasure 1

    Notes
    -----
    sub1_data must follow its `Schema` as defined by the `Validation_Factory` in order to ensure the `submeasure` can run properly
    
    >>> ASC_sub_1 = [
    >>>     "Alcohol_Encounters",
    >>>     "Diagnostic_History",
    >>>     "ASC_Demographic_Data",
    >>>     "Insurance_History"
    >>> ]

    >>> Alcohol_Encounters = {
    >>>     "patient_id": (str, 'object'),
    >>>     "patient_DOB": ("datetime64[ns]",),
    >>>     "encounter_id": (str, 'object'),
    >>>     "encounter_datetime": ("datetime64[ns]",),
    >>>     "screening": (str, 'object'),
    >>>     "score": (int, float),
    >>> }
    
    >>> Diagnostic_History = {
    >>>     "patient_id": (str, 'object'),
    >>>     "encounter_datetime": ("datetime64[ns]",),
    >>>     "diagnosis": (str, 'object')
    >>> }
    
    >>> ASC_Demographic_Data = {
    >>>     "patient_id": (str, 'object'),
    >>>     "sex": (str, 'object'),
    >>>     "race": (str, 'object'),
    >>>     "ethnicity": (str, 'object')
    >>> }
    
    >>> Insurance_History = {
    >>>     "patient_id": (str, 'object'),
    >>>     "insurance": (str, 'object'),
    >>>     "start_datetime": ("datetime64[ns]",),
    >>>     "end_datetime": ("datetime64[ns]",)
    >>> }

    SAMHSA allows for multiple systematic screening methods to be used (AUDIT, AUDIT-C, Single Question Screening)

    Submeasure 2 is calculated off of a subset of submeasure 1, so there aren't any parameters for it.
    """

    def __init__(self,sub1_data:list[pd.DataFrame]):
        super().__init__("ASC")
        self.__sub1__: Submeasure = _Sub_1(self.name + '_sub_1', sub1_data)
        self.__sub2__: Submeasure = _Sub_2(self.name + '_sub_2', None)
        self.__sub2__.__setattr__("__sub1_subset__",False)

    @override
    def get_all_submeasures(self) -> dict[str,pd.DataFrame]:
        """
        Calculates all the data for the ASC Measurement and its Submeasures

        Returns
        -------
        Dictionary[str,pd.DataFrame]
            str
                The name of the submeasure data
            pd.DataFrame
                The data corresponding to that submeasure
        """
        try:
            sub1_results = self.__sub1__.get_submeasure_data()
            sub2_subset = self.__sub1__._get_sub2_subset()
            for key,val in sub2_subset.items():
                self.__sub2__.__setattr__('__'+key+'__',val)
            self.__sub2__.__setattr__("__sub1_subset__",True)
            sub2_results = self.__sub2__.get_submeasure_data()
            full_results = sub1_results | sub2_results
            return full_results
        except Exception:
            raise
