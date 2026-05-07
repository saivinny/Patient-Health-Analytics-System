""" load data structure :
we load the data structure in the list of dictnories
"""
import csv
import os
from typing import List, Dict
class DatasetLoader:
    def __init__(self,filepath:str):
        """Parameters 
        filepathstr 
        we found errors 
        FileNotFoundError
            If the file does not exist at the given path.
        ValueError
            If the file is empty or contains no data rows.
        """
        if not os.path.isfile(filepath):
            raise FileNotFoundError(f"Dataset file not found: '{filepath}'")
        self.filepath=filepath
        self._raw_data: List[dict]=[]
    def load_raw(self) -> List[dict]:
        """
        Reads each CSV row as a dictionary of raw strings.
        Returns:
        list[dict]: Each dictionary represents a row with column headers as keys.
        Raises:
        IOError: If the file cannot be opened.
        ValueError: If the CSV file is empty or has no header.
        """
        try:
            with open(self.filepath, newline="", encoding="utf-8") as fh:
                reader = csv.DictReader(fh)

                if not reader.fieldnames:
                    raise ValueError("CSV file appears to have no header row.")

                self._raw_data = [dict(row) for row in reader]

        except (IOError, OSError) as exc:
            raise IOError(f"Could not read file '{self.filepath}': {exc}") from exc

        if not self._raw_data:
            raise ValueError("CSV file contains no data rows.")
        return self._raw_data
    
    @property
    def raw_data(self) -> List[dict]:
        return self._raw_data

#_______________________________
#Domain-specific subclass
#-------------------------------
#Maping of column names -> target Python type
_COLUMN_TYPES: Dict[str,type]={
    "ID":                      int,
    "Age":                     int,
    "Gender":                  str,
    "Hypertension":            int,
    "Heart Disease":           int,
    "Ever Married":            int,
    "Work Type":               str,
    "Residence Type":          str,
    "Average Glucose Level":   float,
    "BMI":                     float,
    "Smoking Status":          str,
    "Physical Activity":       str,
    "Dietary Habits":          str,
    "Alcohol Consumption":     int,
    "Chronic Stress":          int,
    "Sleep Hours":             int,
    "Family History of Stroke": int,
    "Education Level":         str,
    "Income Level":            str,
    "Stroke Risk Score":       int,
    "Region":                  str,
    "Stroke Occurrence":       int,
}
class PatientDataSet(DatasetLoader):
    """ 
    Loads and type-converts the patient health CSV dataset.

    Attributes
    ______________
    patient_data : list[dict]
        Cleaned list of patient records with correct Python types.
    column_names : list[str]
        Ordered list of column names in the dataset.
    """    
    def __init__(self, filepath: str):
        super().__init__(filepath)
        self.patient_data: List[Dict] = []
        self.column_names: List[str] = []
        self._skipped_rows: int = 0
#_____________________Public Interface_______________________

    def load(self) -> List[Dict]:
        """
        Load the CSV and apply type conversions.

        Returns
        -------
        list[dict]
            Converted patient records.

        Raises
        ------
        FileNotFoundError / IOError / ValueError
            Propagated from the parent class or raised here on bad data.
        """
        self.load_raw()
        self.column_names = list(self._raw_data[0].keys()) if self._raw_data else []
        self.patient_data = []
        self._skipped_rows = 0

        for row_index, row in enumerate(self._raw_data, start=2):  # row 1 = header
            try:
                converted = self._convert_row(row)
                self.patient_data.append(converted)
            except (ValueError, KeyError) as exc:
                # Log and skip malformed rows rather than crashing
                self._skipped_rows += 1

        if not self.patient_data:
            raise ValueError(
                "No valid patient records could be loaded. "
                "Check that the CSV format matches the expected schema."
            )

        return self.patient_data
    
    @property
    def record_count(self) -> int:
        """Number of successfully loaded patient records."""
        return len(self.patient_data)

    @property
    def skipped_rows(self) -> int:
        """Number of rows skipped due to conversion errors."""
        return self._skipped_rows 
    
#_____________________Private Helpers_____________
    @staticmethod
    def _convert_row(row: dict) -> dict:
        """
        Apply type conversions defined in _COLUMN_TYPES.

        Parameters
        ----------
        row : dict Single raw patient record (string values).

        Returns
        -------
        dict: The same record with values cast to their target types.

        Raises
        ------
        ValueError: If a numeric field cannot be parsed.
        """
        converted: dict = {}
        for col, target_type in _COLUMN_TYPES.items():
            raw_value = (row.get(col, "")or "").strip()

            if target_type in (int, float):
                if raw_value == "" or raw_value.lower() in ("nan", "null", "none"):
                    converted[col] = None
                else:
                    try:
                        converted[col] = target_type(raw_value)
                    except ValueError:
                        raise ValueError(
                            f"Cannot convert '{raw_value}' to {target_type.__name__} "
                            f"for column '{col}'."
                        )
            else:
                # string columns – keep as-is; empty → None
                converted[col] = raw_value if raw_value else None

        return converted

    