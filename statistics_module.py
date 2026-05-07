"""statistics module.py 
provides statistics functions and helps to perform operations on patient 
health dataset features
oop structure
StatisticsCalculator  – base class with all computation methods
FeatureStatistics     – subclass that applies the calculations to a
                        named feature of a dataset
"""

import statistics
import math
from collections import Counter
from typing import List,Dict, Union, Optional

#______________Base Class_________________

class StatisticsCalculator:
    
    @staticmethod
    def _clean(values):
        return sorted(float(v) for v in values if v is not None)

#_______________Core Statistical methods__________________

    def mean(self, values):
        return statistics.mean(self._clean(values))

    def median(self, values):
        return statistics.median(self._clean(values))

    
    def mode(self, values: List) -> Union[float, List[float], None]:
        """  Mode (most frequent value).  If multiple values share the
        highest frequency, all are returned as a sorted list.
"""
        data = self._clean(values)
        if not data:
            return None
        counts = Counter(data)
        max_count = max(counts.values())
        modes = sorted(k for k, v in counts.items() if v == max_count)
        return modes[0] if len(modes) == 1 else modes

    def std_dev(self, values):
        data = self._clean(values)
        return statistics.stdev(data) if len(data) > 1 else 0
    
    def variance(self, values):
        data = self._clean(values)
        return statistics.variance(data) if len(data) > 1 else 0
    
    def minimum(self,values):
        return min(values)
    
    def maximum(self,values):
        return max(values)
    
    def range(self,values):
        return max(values) - min(values)
    
    def count(self,values):
        return len(values)
    
#______________Domain SubClass______________________

class FeatureStatistics(StatisticsCalculator):
    """
    Computes and stores descriptive statistics for a specific numeric
    feature of the patient dataset.

    Parameters
    ----------
    patient_data : list[dict]
        Loaded patient records.
    """
    def __init__(self, patient_data: List[Dict]):
        super().__init__()
        self._patient_data = patient_data

    # ------------------------------------------------------------------ #
    # Public interface
    # ------------------------------------------------------------------ #

    def get_feature_values(self, feature_name: str) -> List:
        """
        Extract all values for a given feature column.

        Parameters
        ----------
        feature_name : str
            Column name (e.g., 'Age', 'BMI').

        Returns
        -------
        list
            All non-None values for the feature.

        Raises
        ------
        KeyError
            If the feature name is not found in the dataset.
        """
        if not self._patient_data:
            raise ValueError("Patient dataset is empty.")
        if feature_name not in self._patient_data[0]:
            valid_features = list(self._patient_data[0].keys())
            raise KeyError(
                f"Feature '{feature_name}' not found. "
                f"Valid features: {valid_features}"
            )
        return [row[feature_name] for row in self._patient_data]
    
    def describe(self, feature_name: str) -> Dict:
        values = self.get_feature_values(feature_name)
        numeric = self._clean(values)

        if not numeric:
            raise TypeError(
                f"Feature '{feature_name}' contains no numeric values. "
                "Only numeric features can be summarised."
            )
        
        return {
    "feature":   feature_name,
    "count":     len(numeric),
    "mean":      round(self.mean(numeric), 4),
    "median":    round(self.median(numeric), 4),
    "mode":      self.mode(numeric),
    "std_dev":   round(self.std_dev(numeric), 4),
    "variance":  round(self.variance(numeric), 4),
    "minimum":   self.minimum(numeric),
    "maximum":   self.maximum(numeric),
    "range":     round(self.range(numeric), 4),
}
    def list_numeric_features(self) -> List[str]:
        """Return names of all numeric features in the dataset."""
        if not self._patient_data:
            return []
        sample = self._patient_data[0]
        return [
        col for col, val in sample.items()
        if isinstance(val, (int, float)) and val is not None
    ]
    