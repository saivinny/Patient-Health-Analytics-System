# ============================================================
# query_module.py
# ============================================================

import csv
from statistics_module import StatisticsCalculator
from typing import List, Dict, Optional


class BaseQueryEngine:
    """
    The foundation for any query engine.
    Stores the dataset, provides helper methods, and handles CSV export.
    """

    def __init__(self, patient_data: List[Dict]):
        if not patient_data:
            raise ValueError("patient_data must be a non-empty list of records.")
        self._data  = patient_data
        self._stats = StatisticsCalculator()

    def _col(self, feature: str) -> List:
        return [row[feature] for row in self._data if row.get(feature) is not None]

    def _filter(self, predicate) -> List[Dict]:
        return [row for row in self._data if predicate(row)]

    def export_to_csv(self, results, filepath: str) -> str:
        if results is None:
            raise ValueError("Results are None — nothing to export.")

        if isinstance(results, dict):
            rows = [results]
        elif isinstance(results, list):
            if not results:
                raise ValueError("Results list is empty — nothing to export.")
            if not isinstance(results[0], dict):
                rows = [{"value": r} for r in results]
            else:
                rows = results
        else:
            rows = [{"value": str(results)}]

        try:
            with open(filepath, "w", newline="", encoding="utf-8") as fh:
                writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)
        except (IOError, OSError) as exc:
            raise IOError(f"Could not write CSV to '{filepath}': {exc}") from exc

        return f"Exported {len(rows)} row(s) to '{filepath}'."


class PatientQueryEngine(BaseQueryEngine):
    """
    Inherits all tools from BaseQueryEngine and adds
    specific analysis methods for the stroke/health dataset.
    """

    # ----------------------------------------------------------
    # 1. Smokers with hypertension — age statistics
    # ----------------------------------------------------------

    def smokers_hypertension_age_stats(self) -> Dict:
        filtered = self._filter(
            lambda row: (
                row.get("Smoking Status") in ["Smokes", "Formerly smoked"]
                and row.get("Hypertension") == 1
            )
        )
        ages = [row["Age"] for row in filtered if row.get("Age") is not None]

        if not ages:
            return {"count": 0, "average_age": None, "modal_age": None, "median_age": None}

        return {
            "count":       len(filtered),
            "average_age": round(self._stats.mean(ages), 2),
            "modal_age":   self._stats.mode(ages),
            "median_age":  self._stats.median(ages),
        }

    # ----------------------------------------------------------
    # 2. Heart disease patients — age + glucose statistics
    # ----------------------------------------------------------

    def heart_disease_age_glucose_stats(self) -> Dict:
        subset  = self._filter(lambda r: r.get("Heart Disease") == 1)
        ages    = [r["Age"] for r in subset if r.get("Age") is not None]
        glucose = [r["Average Glucose Level"] for r in subset if r.get("Average Glucose Level") is not None]

        return {
            "count":                 len(subset),
            "average_age":           round(self._stats.mean(ages), 2)    if ages    else None,
            "modal_age":             self._stats.mode(ages),
            "median_age":            self._stats.median(ages),
            "average_glucose_level": round(self._stats.mean(glucose), 2) if glucose else None,
        }

    # ----------------------------------------------------------
    # 3. Hypertension + stroke, broken down by gender
    # ----------------------------------------------------------

    def hypertension_stroke_by_gender(self) -> Dict:
        results = {}
        genders = {r.get("Gender") for r in self._data if r.get("Gender")}

        for gender in sorted(genders):
            results[gender] = {}
            for stroke_val, label in [(1, "had_stroke"), (0, "no_stroke")]:
                subset = self._filter(
                    lambda r, g=gender, s=stroke_val: (
                        r.get("Gender") == g
                        and r.get("Hypertension") == 1
                        and r.get("Stroke Occurrence") == s
                    )
                )
                ages = [r["Age"] for r in subset if r.get("Age") is not None]
                results[gender][label] = {
                    "count":       len(subset),
                    "average_age": round(self._stats.mean(ages), 2) if ages else None,
                    "modal_age":   self._stats.mode(ages),
                    "median_age":  self._stats.median(ages),
                }

        return results

    # ----------------------------------------------------------
    # 4. BMI, glucose, and stroke risk — by physical activity
    # ----------------------------------------------------------

    def health_metrics_by_activity(self) -> List[Dict]:
        activity_levels = ["Sedentary", "Light", "Moderate", "Active"]
        results = []

        for level in activity_levels:
            subset  = self._filter(lambda r, lv=level: r.get("Physical Activity") == lv)
            bmi     = [r["BMI"] for r in subset if r.get("BMI") is not None]
            glucose = [r["Average Glucose Level"] for r in subset if r.get("Average Glucose Level") is not None]
            risk    = [r["Stroke Risk Score"] for r in subset if r.get("Stroke Risk Score") is not None]

            results.append({
                "physical_activity":         level,
                "count":                     len(subset),
                "average_bmi":               round(self._stats.mean(bmi),     2) if bmi     else None,
                "average_glucose_level":     round(self._stats.mean(glucose), 2) if glucose else None,
                "average_stroke_risk_score": round(self._stats.mean(risk),    2) if risk    else None,
            })

        return results

    # ----------------------------------------------------------
    # 5. Stroke patients — age stats by urban vs rural
    # ----------------------------------------------------------

    def stroke_age_by_residence(self) -> Dict:
        results = {}

        for area in ("Urban", "Rural"):
            subset = self._filter(
                lambda r, a=area: (
                    r.get("Residence Type") == a
                    and r.get("Stroke Occurrence") == 1
                )
            )
            ages = [r["Age"] for r in subset if r.get("Age") is not None]
            results[area] = {
                "count":       len(subset),
                "average_age": round(self._stats.mean(ages), 2) if ages else None,
                "modal_age":   self._stats.mode(ages),
                "median_age":  self._stats.median(ages),
            }

        return results

    # ----------------------------------------------------------
    # 6. Dietary habits — stroke vs no stroke
    # ----------------------------------------------------------

    def dietary_habits_stroke_comparison(self) -> Dict:
        from collections import Counter
        result = {}

        for stroke_val, label in [(1, "had_stroke"), (0, "no_stroke")]:
            subset = self._filter(lambda r, s=stroke_val: r.get("Stroke Occurrence") == s)
            habits = [r["Dietary Habits"] for r in subset if r.get("Dietary Habits") is not None]
            result[label] = dict(Counter(habits))

        return result

    # ----------------------------------------------------------
    # 7. All patients with hypertension AND a stroke
    # ----------------------------------------------------------

    def hypertension_stroke_patients(self) -> List[Dict]:
        return self._filter(
            lambda r: r.get("Hypertension") == 1 and r.get("Stroke Occurrence") == 1
        )

    # ----------------------------------------------------------
    # 8. All patients with heart disease AND a stroke
    # ----------------------------------------------------------

    def heart_disease_stroke_patients(self) -> List[Dict]:
        return self._filter(
            lambda r: r.get("Heart Disease") == 1 and r.get("Stroke Occurrence") == 1
        )

    # ----------------------------------------------------------
    # 9. Average sleep hours — stroke vs no stroke
    # ----------------------------------------------------------

    def sleep_hours_stroke_comparison(self) -> Dict:
        result = {}

        for stroke_val, label in [(1, "had_stroke"), (0, "no_stroke")]:
            subset = self._filter(lambda r, s=stroke_val: r.get("Stroke Occurrence") == s)
            hours  = [r["Sleep Hours"] for r in subset if r.get("Sleep Hours") is not None]
            result[label] = {
                "count":               len(subset),
                "average_sleep_hours": round(self._stats.mean(hours), 2) if hours else None,
            }

        return result

    # ----------------------------------------------------------
    # 10. Flexible multi-criteria patient filter
    # ----------------------------------------------------------

    def filter_patients(
        self,
        age_min:           Optional[int] = None,
        age_max:           Optional[int] = None,
        gender:            Optional[str] = None,
        smoking_status:    Optional[str] = None,
        region:            Optional[str] = None,
        hypertension:      Optional[int] = None,
        heart_disease:     Optional[int] = None,
        stroke_occurrence: Optional[int] = None,
        residence_type:    Optional[str] = None,
        physical_activity: Optional[str] = None,
    ) -> List[Dict]:
        """
        Flexible search — only filters by criteria you actually pass in.
        Any parameter left as None is ignored.
        """
        def predicate(r):
            if age_min           is not None and (r.get("Age") is None or r["Age"] < age_min):
                return False
            if age_max           is not None and (r.get("Age") is None or r["Age"] > age_max):
                return False
            if gender            is not None and r.get("Gender")            != gender:
                return False
            if smoking_status    is not None and r.get("Smoking Status")    != smoking_status:
                return False
            if region            is not None and r.get("Region")            != region:
                return False
            if hypertension      is not None and r.get("Hypertension")      != hypertension:
                return False
            if heart_disease     is not None and r.get("Heart Disease")     != heart_disease:
                return False
            if stroke_occurrence is not None and r.get("Stroke Occurrence") != stroke_occurrence:
                return False
            if residence_type    is not None and r.get("Residence Type")    != residence_type:
                return False
            if physical_activity is not None and r.get("Physical Activity") != physical_activity:
                return False
            return True

        return self._filter(predicate)

    # ----------------------------------------------------------
    # 11. Categorise every patient by stroke risk level
    # ----------------------------------------------------------

    def stroke_risk_categories(self) -> Dict:
        categories = {"Low": 0, "Medium": 0, "High": 0}
        total = 0

        for row in self._data:
            score = row.get("Stroke Risk Score")
            if score is None:
                continue
            total += 1
            if score <= 33:
                categories["Low"] += 1
            elif score <= 66:
                categories["Medium"] += 1
            else:
                categories["High"] += 1

        result = {}
        for category, count in categories.items():
            result[category] = {
                "count":      count,
                "percentage": round((count / total) * 100, 2) if total > 0 else 0.0,
            }

        return result

    # ----------------------------------------------------------
    # 12. Regional health report — one summary row per region
    # ----------------------------------------------------------

    def regional_health_report(self) -> List[Dict]:
        regions = ["North", "South", "East", "West"]
        report  = []

        for region in regions:
            subset = self._filter(lambda r, reg=region: r.get("Region") == reg)

            if not subset:
                continue

            ages    = [r["Age"] for r in subset if r.get("Age") is not None]
            bmi     = [r["BMI"] for r in subset if r.get("BMI") is not None]
            glucose = [r["Average Glucose Level"] for r in subset if r.get("Average Glucose Level") is not None]

            stroke_count = sum(1 for r in subset if r.get("Stroke Occurrence") == 1)
            stroke_rate  = (stroke_count / len(subset)) * 100

            report.append({
                "region":                   region,
                "patient_count":            len(subset),
                "average_age":              round(self._stats.mean(ages),    2) if ages    else None,
                "average_bmi":              round(self._stats.mean(bmi),     2) if bmi     else None,
                "average_glucose_level":    round(self._stats.mean(glucose), 2) if glucose else None,
                "stroke_count":             stroke_count,
                "stroke_occurrence_rate_%": round(stroke_rate, 2),
            })

        return report