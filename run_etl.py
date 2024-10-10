from extract import extract
from transform import transform


def main():
    # Step 1: Extract job links
    print("Starting extraction of job links and job description.")
    extract()

    # Step 2: Transform data
    print("Starting transformation of job data...")
    transform()

    print("ETL process completed successfully.")


if __name__ == "__main__":
    main()
