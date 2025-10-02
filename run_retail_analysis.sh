#!/bin/bash

# Retail Sales Data Analysis Setup and Run Script

# Display header
echo "====================================================="
echo "  MCCS Retail Sales Data Analysis Tools"
echo "====================================================="
echo

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if Python is installed
if ! command_exists python; then
    echo "Error: Python is not installed. Please install Python 3.7 or higher."
    exit 1
fi

# Check Python version
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "Detected Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment. Please install venv package."
        exit 1
    fi
    echo "Virtual environment created successfully."
else
    echo "Using existing virtual environment."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Error: Failed to activate virtual environment."
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r retail_analysis_requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies."
    exit 1
fi
echo "Dependencies installed successfully."

# Check if the data files exist
csv_path="data/convertedcsv/MCCS_RetailData.csv"
parquet_path="data/rawdata/MCCS_RetailData.parquet"
sample_parquet_path="retail_data_sample.parquet"

if [ -f "$csv_path" ]; then
    echo "Found retail data CSV file at: $csv_path"
elif [ -f "$parquet_path" ]; then
    echo "Found retail data Parquet file at: $parquet_path"
elif [ -f "$sample_parquet_path" ]; then
    echo "Found sample retail data Parquet file at: $sample_parquet_path"
else
    echo "Warning: Could not find the retail data files."
    echo "Please ensure one of these files exists:"
    echo "  - $csv_path"
    echo "  - $parquet_path"
    echo "  - $sample_parquet_path"
fi

echo
echo "====================================================="
echo "  Setup Complete"
echo "====================================================="
echo

# Display menu
while true; do
    echo "What would you like to do?"
    echo "1. Run static analysis (generates visualizations and report)"
    echo "2. Launch interactive dashboard"
    echo "3. Generate AI insights from analysis results"
    echo "4. Exit"
    echo
    read -p "Enter your choice (1-4): " choice
    
    case $choice in
        1)
            echo "Running static analysis script..."
            echo "This may take several minutes due to the large dataset size."
            echo
            python retail_trends_analysis.py
            echo
            echo "Analysis complete! Results saved to 'retail_analysis_results' directory."
            ;;
        2)
            echo "Launching interactive dashboard..."
            echo "Press Ctrl+C to stop the dashboard when finished."
            echo
            streamlit run retail_trends_dashboard.py
            ;;
        3)
            echo "Generate AI insights from analysis results..."
            if [ ! -f "retail_analysis_results/summary_report.txt" ]; then
                echo "Error: Summary report not found. Please run the static analysis first (option 1)."
            else
                read -p "Enter your OpenAI API key: " api_key
                if [ -z "$api_key" ]; then
                    echo "Error: API key is required to generate insights."
                else
                    echo "Would you like to ask a specific question or get general insights?"
                    echo "1. General insights"
                    echo "2. Ask a specific question"
                    read -p "Enter your choice (1-2): " insight_choice
                    
                    if [ "$insight_choice" == "1" ]; then
                        echo "Generating general insights..."
                        python retail_llm_insights.py --api_key "$api_key"
                    elif [ "$insight_choice" == "2" ]; then
                        read -p "Enter your question about the retail data: " question
                        echo "Generating insights for your question..."
                        python retail_llm_insights.py --api_key "$api_key" --question "$question"
                    else
                        echo "Invalid choice. Generating general insights..."
                        python retail_llm_insights.py --api_key "$api_key"
                    fi
                    
                    echo "Insights generated and saved to 'retail_analysis_results/llm_insights.md'"

                    # Ask if user wants to generate PDF
                    read -p "Would you like to generate a PDF version of the insights? (y/n): " generate_pdf
                    if [[ "$generate_pdf" == "y" || "$generate_pdf" == "Y" ]]; then
                        echo "Generating PDF version of insights..."
                        python retail_llm_insights.py --pdf_only
                        echo "PDF generated and saved to 'retail_analysis_results/llm_insights.pdf'"
                    fi
                fi
            fi
            ;;
        4)
            echo "Exiting..."
            deactivate
            exit 0
            ;;
        *)
            echo "Invalid choice. Please enter 1, 2, 3, or 4."
            ;;
    esac
    
    echo
done
