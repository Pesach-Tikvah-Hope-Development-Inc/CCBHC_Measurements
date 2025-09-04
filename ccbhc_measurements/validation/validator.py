import pandas as pd

class Validator:
    """
    Validate dataframes against predefined column requirements

    Attributes
    ----------
    schema : dict
        A dictionary where keys are dataframe names and values are expected column specifications
    """
    def __init__(self, schemas:dict):
        self.SCHEMAS = schemas

    def validate(self, dataframes:list[pd.DataFrame]) -> tuple[bool,ValueError]:
        """
        Validates the given list of dataframes based on expected columns and data types

        Parameters
        ----------
        dataframes
            List of dataframes to be validated

        Returns
        ------
        bool
            Do the dataframes fit the schema
        ValueError
            When the number of dataframes is incorrect
            OR if any dataframes are missing columns            
            OR if any dataframes have columns not properly formatted
        """
        # submeasure 2s that are subsets of submeasure 1s don't need validation
        if dataframes == None:
            return True, None
        
        errors = {}

        if len(dataframes) != len(self.SCHEMAS):
            return False, ValueError(f"Expected {len(self.SCHEMAS)} dataframes, got {len(dataframes)}.")

        for i, (df_name, col_specs) in enumerate(self.SCHEMAS.items()):
            df = dataframes[i]
            errors[df_name] = []
            for col, dtype in col_specs.items():
                if col not in df.columns:
                    errors[df_name].append(f"Missing column: {col}")
                else:
                    actual_dtype = df[col].dtype
                    if not any(pd.api.types.is_dtype_equal(actual_dtype, pd.api.types.pandas_dtype(dt)) for dt in dtype):
                        errors[df_name].append(
                            f"Column {col} has incorrect data type. Expected: {dtype}, Found: {actual_dtype}"
                        )

        all_errors = "\n".join(
            f"{df_name}:\n\t{'\n\t'.join(err_list)}" for df_name, err_list in errors.items() if err_list
        )

        if all_errors:
            return False, ValueError(f"Validation errors found \n{all_errors}")
        return True, None
    
