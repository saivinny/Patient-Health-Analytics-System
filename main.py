"""Main entry point for Patient Health Analysis System"""

import sys
from load_dataset_module import PatientDataSet
from statistics_module import FeatureStatistics
from query_module import PatientQueryEngine


def main():
    try:
        # Load dataset
        loader = PatientDataSet("data.csv")
        data = loader.load()

        print(f"Loaded {len(data)} records successfully.")

        # Initialize modules
        stats_engine = FeatureStatistics(data)
        query_engine = PatientQueryEngine(data)

    except (FileNotFoundError, IOError, ValueError) as exc:
        print(f"Error loading dataset: {exc}")
        return

    # Initialize GUI
    try:
        from user_interface_module import PatientHealthAnalytics

        app = PatientHealthAnalytics(
            patient_data=data,
            query_engine=query_engine,
            stats_engine=stats_engine,
        )
        app.run()

    except ImportError as exc:
        print(f"[ERROR] GUI module unavailable: {exc}")
        sys.exit(1)

    except Exception as exc:
        print(f"[ERROR] Application error: {exc}")
        raise


if __name__ == "__main__":
    main()