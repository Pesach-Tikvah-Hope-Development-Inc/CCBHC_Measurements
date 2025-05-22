import logging
import pandas as pd
from abc import abstractmethod
from ccbhc_measurements.abstractions.denominator import Denominator
from ccbhc_measurements.abstractions.numerator import Numerator
from ccbhc_measurements.abstractions.stratification import Stratification
from ccbhc_measurements.validation.validation_factory import build

class Submeasure(Denominator,Numerator,Stratification):
    """
    A base class for all submeasure calculations

    This class defines the core methods that must be implemented 
    by any concrete measurement class

    Parameters
    ----------
    name
        Name of the submeasure
    dataframes
        All dataframes needed to calculate the submeasure

    Inherits
    --------
    Denominator
        Provides methods for retrieving and processing the denominator data
    Numerator
        Provides methods for retrieving and processing the numerator data

    Notes
    -----
    All dataframes must follow their `Schema` as defined by the `Validation_Factory` in order to ensure the `submeasure` can run properly
    """

    def __init__(self,name:str, dataframes: list[pd.DataFrame]):
        super().__init__()
        self.__NAME__:str = name
        self.__LOGGER__ = logging.getLogger(name)
        self.__DATA__:pd.DataFrame = None
        self.__DIAGNOSIS__:pd.DataFrame = None
        self.__DEMOGRAPHICS__:pd.DataFrame = None
        self.__INSURANCE__:pd.DataFrame = None
        self.__validified__ = False
        self.__IS_VALID__, self.__VALIDATION_DETAILS__ = self.__validate_dataframes(dataframes)
        if self.__IS_VALID__:
            self._set_dataframes(dataframes)
        self.__populace__:pd.DataFrame = None
        self.__stratification__:pd.DataFrame = None
        self.__is_calculated__ = False

    def get_name(self) -> str:
        """
        Returns
        -------
        str
            Submeasure name
        """
        return self.__NAME__
    
    def get_populace_dataframe(self) -> pd.DataFrame:
        """
        Returns
        -------
        pd.Dataframe
            Populace dataframe
        """
        return self.__populace__.copy()

    def get_stratification_dataframe(self) -> pd.DataFrame:
        """
        Returns
        -------
        pd.Dataframe
            Stratification dataframe
        """
        return self.__stratification__.copy()

    def __validate_dataframes(self,dataframes:list[pd.DataFrame]) -> tuple[bool,ValueError]:
        """
        Validates the given list of dataframes based on expected columns and data types

        Parameters
        ----------
        dataframes
            List of dataframes to be validated

        Returns
        ------
        tuple[bool,ValueError]
            bool
                Do the dataframes fit the schema
            ValueError
                When the number of dataframes is incorrect
                OR if any dataframes are missing columns            
                OR if any dataframes have columns not properly formatted
        """
        try:
            validator = build(self.get_name())
            return validator.validate(dataframes)
        except Exception:
            self.__LOGGER__.error("Failed to Validate",exc_info=True)

    @abstractmethod
    def _set_dataframes(self, dataframes:list[pd.DataFrame]) -> None:
        """
        Sets private attributes to the validated dataframes that get used to calculate the submeasure

        Paramaters
        ----------
        dataframes
            List of dataframes
        """
        pass

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
        ValueError
            When the number of dataframes is incorrect
            OR if any dataframes are missing columns            
            OR if any dataframes have columns not properly formatted
        """
        try:
            if not self.__IS_VALID__:
                raise self.__VALIDATION_DETAILS__
            self.calculate_denominator()
            self.calculate_numerator()
            self.stratify_data()
            data = self.get_final_data()
            self.__LOGGER__.info("Successfully Calculated Submeasure Data")
            return data
        except Exception as e:
            # all exceptions raised in other methods log themselves already
            # but since all exceptions get excepted in this method, it's needed to check which exception is being caught
            # in order to avoid double logging
            if e == self.__VALIDATION_DETAILS__:
                self.__LOGGER__.error(msg="Failed to Validate Dataframes",exc_info=True)
            raise

    def calculate_denominator(self) -> None:
        """
        Processes the data for the denominator of the submeasure.
        """
        try:
            self._set_populace()
            self._remove_exclusions()
        except Exception:
            self.__LOGGER__.error("Failed to Calculate Denominator",exc_info=True)
            raise

    def calculate_numerator(self) -> None:
        """
        Processes the data for the numerator of the submeasure
        """
        try:
            self._apply_time_constraint()
            self._find_performance_met()
        except Exception:
            self.__LOGGER__.error("Failed to Calculate Numerator",exc_info=True)
            raise
    
    def stratify_data(self) -> None:
        """
        Stratifies the data for the submeasure

        This method must be implemented by the concrete class 
        to define how the data is stratified (e.g., by age, gender).
        """
        try:
            self._set_stratification()
            self._set_patient_stratification()
            self._set_encounter_stratification()
            self._fill_blank_stratification()
        except Exception:
            self.__LOGGER__.error("Failed to Stratify Data",exc_info=True)
            raise

    def get_final_data(self)-> dict[str:pd.DataFrame]:
        """
        Formats the final data into concise dataframes

        Returns
        -------
        dict[str:pd.DataFrame]
            str
                Submeasure name
            pd.DataFrame
                Submeasure data
        """
        try:
            self._set_final_denominator_data()
            self._trim_unnecessary_stratification_data()
            self._sort_final_data()
            self.__is_calculated__ = True
            return {
                self.get_name() : self.__populace__.copy(),
                self.get_name() + '_stratification' : self.__stratification__.copy()
            }
        except Exception:
            self.__LOGGER__.error("Failed to Get Final Data",exc_info=True)
            raise

    @abstractmethod
    def _set_final_denominator_data(self) -> None:
        """
        Sets all data that is needed and unique to the Submeasure's denominator populace

        This method must be implemented by the concrete class 
        to define how the populace data is trimmed
        """
        pass

    @abstractmethod
    def _trim_unnecessary_stratification_data(self) -> None:
        """
        Removes all data that isn't needed for the Submeasure's stratification

        This method must be implemented by the concrete class 
        to define how the stratification data is trimmed
        """
        pass

    @abstractmethod
    def _sort_final_data(self) -> None:
        """
        Sorts the Populace and Stratification dataframes

        This method must be implemented by the concrete class 
        to define how the dataframes is trimmed
        """
        pass

    def __str__(self) -> str:
        if not self.__is_calculated__:
            return f'{self.__NAME__} has not been calculated'
        return f'{self.__NAME__} has a denominator of {len(self.__populace__)} and a numerator of {len(self.__populace__[self.__populace__['numerator']])}'
    