
import csv
from pathlib import Path

DATA_FILE = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "raw"
    / "Day-ahead_prices_202312312100_202512312100_Hour.csv"
)


def main() -> None:
    if not DATA_FILE.exists():
        print(f"File not found: {DATA_FILE}")
        return

    with DATA_FILE.open("r", encoding="utf-8-sig", newline="") as file:
        sample = file.read(4096)
        file.seek(0)

        print("File:", DATA_FILE.name)
        print("\nFirst lines:")
        print(sample[:1000])

        file.seek(0)
        dialect = csv.Sniffer().sniff(sample, delimiters=";,\t")
        reader = csv.DictReader(file, dialect=dialect)

        print("\nColumns:", reader.fieldnames)

        rows = list(reader)
        print("Data rows:", len(rows))

        if rows:
            print("\nFirst 3 records:")
            for row in rows[:3]:
                print(row)

            print("\nLast record:")
            print(rows[-1])


if __name__ == "__main__":
    main()
