import pandas as pd
import numpy as np

FILE_PATH = "/Users/albarka/Desktop/GRA/data/Copy_of_ib_Test_data.csv"


def load_and_clean_data(filepath):
    print(f"Loading {filepath}...")
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        print("Error: File not found.")
        return None

    # 1. Clean Column Names (Strip hidden spaces)
    df.columns = df.columns.str.strip()

    # 2. Rename columns to standard names
    # Your specific file has columns: "Dates", "Rainfall (in)", "Runoff (in)"
    df.rename(
        columns={
            "Dates": "Date",
            "Rainfall (in)": "Rainfall",
            "Runoff (in)": "Measured_Runoff",
        },
        inplace=True,
    )

    # 3. FIX DATES (The Critical Part)
    # We use dayfirst=True because your data is 13-01-2008 (Day-Month-Year)
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")

    # 4. Clean Numbers
    df["Rainfall"] = pd.to_numeric(df["Rainfall"], errors="coerce").fillna(0)
    df["Measured_Runoff"] = pd.to_numeric(
        df["Measured_Runoff"], errors="coerce"
    ).fillna(0)

    # Check if dates loaded correctly
    print(
        f"Success! Date Range: {df['Date'].min().date()} to {df['Date'].max().date()}"
    )
    return df


# Run the loader
df = load_and_clean_data(FILE_PATH)
# Save the clean data to a new file
df.to_csv(
    "/Users/albarka/Desktop/GRA/data/Cleaned_Data.csv",
    index=False,
    date_format="%Y-%m-%d",
)

print("Saved clean file to: Cleaned_Data.csv")
