from abc import ABC, abstractmethod
from typing import override
import pandas as pd

class Screening_Strategy(ABC):
    @abstractmethod
    def __call__(self,screenings:pd.DataFrame) -> pd.Series:
        """
        Dynamic strategies for checking alcohol screening results

        Parameters
        ----------
        screenings
            Dataframe of alcohol screenings

        Returns
        -------
        pd.Series[bool]
            Unhealthy alcohol usage
        """
        pass

class Audit_Screening(Screening_Strategy):
    @override
    def __call__(self,screenings:pd.DataFrame) -> pd.Series:
        """
        Audit screening logic

        Checks if the score is greater or equal to eight

        Parameters
        ----------
        screenings
            Dataframe of alcohol screenings

        Returns
        -------
        pd.Series[bool]
            Unhealthy alcohol usage
        """
        return screenings['score'] >= 8

class Audit_C_Screening(Screening_Strategy):
    @override
    def __call__(self,screenings:pd.DataFrame) -> pd.Series:
        """
        Audit-C screening logic

        Checks if the score is greater or equal to four (male) or three (female)

        Parameters
        ----------
        screenings
            Dataframe of alcohol screenings

        Returns
        -------
        pd.Series[bool]
            Unhealthy alcohol usage
        """
        # splitting a df doesn't change the index
        # this allows for a concat() + sort_index() to keep the integrity of the original df
        men = screenings[screenings['sex'] == 'male'].copy()
        men['unhealthy_alcohol_use'] = men['score'] >= 4
        women = screenings[screenings['sex'] == 'female'].copy()
        women['unhealthy_alcohol_use'] = women['score'] >= 3
        return pd.concat([men,women]).sort_index()['unhealthy_alcohol_use']

class Single_Question_Screening(Screening_Strategy):
    @override
    def __call__(self,screenings:pd.DataFrame) -> pd.Series:
        """
        Single question screening screening logic

        Checks if the score is greater or equal to one

        Parameters
        ----------
        screenings
            Dataframe of alcohol screenings

        Returns
        -------
        pd.Series[bool]
            Unhealthy alcohol usage
        """
        return screenings['score'] >= 1


def get_screening_strategy(screening_type:str) -> Screening_Strategy:
    """
    Gets the screening strategy for the screening type

    Parameters
    ----------
    screening_type
        Screening type

    Returns
    -------
    Screening_Strategy
        Corresponding strategy for the screening_type
    """
    match screening_type:
        case 'audit':
            return Audit_Screening()
        case 'audit-c':
            return Audit_C_Screening()
        case 'single question screening':
            return Single_Question_Screening()
        
alcohol_screeners = [
    'audit',
    'audit-c',
    'single question screening'
]