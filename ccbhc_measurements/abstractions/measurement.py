from abc import ABC, abstractmethod
import pandas as pd

class Measurement(ABC):
    """
    A common base class for all Measurements

    Measurements are a standardized metric created by SAMHSA used to measure the performance of a CCBHC

    This class defines the core methods that must be implemented by any concrete measurement class

    Parameters
    ----------
    name
        Name of the measurement
    """

    def __init__(self,name:str):
        super().__init__()
        self.__NAME__: str = name
    
    @property
    def name(self) -> str:
        """
        Returns
        -------
        str
            The name of the Measurement
        """
        return self.__NAME__

    @abstractmethod
    def get_all_submeasures(self) -> dict[str:pd.DataFrame]:
        """
        Calculates all the data for the Measurement and its Submeasures

        Returns
        -------
        dict[str:pd.DataFrame]
            str
                Submeasure name
            pd.DataFrame
                Submeasure data

        Raises
        ------
        ValueError
            When the submeasure data isn't properly formatted

        This method must be implemented by the concrete class
        """
        pass
