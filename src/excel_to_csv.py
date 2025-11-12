import pandas as pd
import os

def to_filename(string):
    return "_".join(string.split())

def process_survey_responses(df):
    # Question categories
    RATING_QUESTIONS = ['Satisfaction', 'Cleanliness', 'Service', 'Price', 'Checkout', 'Store Atmosphere', 'Merchandise']
    BINARY_QUESTIONS = ['Contact?', 'Purchase All']
    MULTI_SELECT = ['MCX_Products Purchased', 'MCX_Program Awareness']
    DEMOGRAPHIC = ['Military Affiliation', 'Demos: Branch of Service', 'Demos: Gender']

    # Process answer columns based on question type
    for idx, row in df.iterrows():
        question_label = row['questionLabel']

        # Handle Rating Questions (1-5 scale)
        if any(qt in question_label for qt in RATING_QUESTIONS):
            for col in ['answerLabels', 'answerDisplayLabels', 'answerTexts']:
                value = str(row[col])
                if '1=' in value or 'Poor' in value or 'Very unlikely' in value or 'Falls short' in value:
                    df.loc[idx, col] = 1
                elif '5=' in value or 'Excellent' in value or 'Very Likely' in value or 'Strongly Agree' in value:
                    df.loc[idx, col] = 5
                elif value.isdigit():
                    df.loc[idx, col] = int(value)

        # Handle Binary Questions
        elif any(qt in question_label for qt in BINARY_QUESTIONS):
            for col in ['answerLabels', 'answerDisplayLabels', 'answerTexts']:
                df.loc[idx, col] = 1 if row[col] == 'Yes' else 0

        # Handle Multi-select Questions
        elif any(qt in question_label for qt in MULTI_SELECT):
            # Keep original text values
            continue

        # Handle Demographics
        elif any(qt in question_label for qt in DEMOGRAPHIC):
            # Keep original text values
            continue

    # Convert responseTime to datetime
    df['responseTime'] = pd.to_datetime(df['responseTime'])

    return df

def main():
    # Use relative paths that work from any directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)  # Go up 1 level from src/ to project root

    # Input file path
    excel_file_path = os.path.join(project_root, 'data', 'rawdata', 'CustomerSurveyResponses.xlsx')

    # Output directory
    output_dir = os.path.join(project_root, 'data', 'convertedcsv')
    os.makedirs(output_dir, exist_ok=True)

    # Check if input file exists
    if not os.path.exists(excel_file_path):
        print(f"Error: Excel file not found at: {excel_file_path}")
        return

    print(f"Processing Excel file: {excel_file_path}")
    xls = pd.ExcelFile(excel_file_path)

    for sheet_name in xls.sheet_names:
        print(f"Processing sheet: {sheet_name}")

        # Read sheet
        df = pd.read_excel(xls, sheet_name=sheet_name)

        # Remove last column
        df = df.iloc[:, :-1]

        # Process survey responses
        df = process_survey_responses(df)

        # Process data types
        for col in df.columns:
            if col.endswith("Rate") or col.endswith("Diff") or col.startswith("%") or col.endswith("%"):
                df[col] = df[col].astype(str)
            elif col in ["responseTime"]:
                df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d')
            elif col in ["Email Domain", "Audience Name", "Audience Type", "Message Name",
                        "Campaign", "Social Network", "Outbound Post", "Media Type",
                        "Email Content Name", "Day Of Week", "Time Of Day", "Email Subject",
                        "respondentId", "questionId", "questionName", "questionPhrase",
                        "questionType", "questionLabel"]:
                df[col] = df[col].astype(str)
            else:
                try:
                    df[col] = df[col].astype(int)
                except:
                    df[col] = df[col].astype(str)

        # Create output filename
        excel_basename = os.path.splitext(os.path.basename(excel_file_path))[0]
        sheet_filename = to_filename(sheet_name)
        output_filename = os.path.join(output_dir, f"{excel_basename}-{sheet_filename}.csv")

        # Export to CSV
        df.to_csv(output_filename, index=False)
        print(f"Exported {sheet_name} to {output_filename}")

if __name__ == "__main__":
    main()
