# Geo-Compliance Feature Flagging System Prototype

This project is a prototype system that utilizes LLM capabilities to automatically flag features that require geo-specific compliance logic. It is designed to reduce manual effort, mitigate regulatory risk, and provide a clear, auditable trail for compliance checks.

## How It Works

The system uses a Python script to read a list of features from a CSV file. For each feature, it sends the description to the OpenAI GPT-4.1 mini API with a specialized prompt. The LLM then analyzes the text and returns a structured JSON object indicating whether geo-specific compliance is needed, the reasoning behind the decision, and any specific regulation mentioned. The results are then compiled into a new CSV file.

## Getting Started

Follow these instructions to set up and run the project on your local machine.

### Prerequisites

- Python 3.7+
- An OpenAI API key

### Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up your OpenAI API Key:**
    The application loads the API key from an environment variable. You can set it in your terminal session like this:
    ```bash
    export OPENAI_API_KEY='your-secret-api-key'
    ```
    *Note: For a more permanent solution, you can add this line to your shell's profile file (e.g., `~/.bashrc` or `~/.zshrc`).*

### Usage

The main application is run from the command line.

-   **To run the analysis on the default `sample_data.csv`:**
    ```bash
    python main.py
    ```
    This will generate an `analysis_results.csv` file in the same directory.

-   **To specify a custom input and output file:**
    ```bash
    python main.py --input path/to/your/data.csv --output path/to/your/results.csv
    ```

## Data Files

This project includes two key CSV files:

-   `sample_data.csv`: This file contains the primary input data for the analysis. It includes a list of feature names and their detailed descriptions, which often contain internal acronyms and project codenames.
-   `data_set.csv`: This file serves as a glossary or data dictionary for the terms and acronyms found in `sample_data.csv`. It provides explanations for internal codenames like `GH`, `CDS`, `Jellybean`, etc., which is essential context for understanding the feature descriptions.

## Project Structure

```
.
├── compliance_checker/
│   ├── __init__.py
│   └── analyzer.py       # Contains the core logic for calling the OpenAI API.
├── main.py               # The main CLI application script.
├── sample_data.csv       # Sample input data.
├── requirements.txt      # Project dependencies.
├── README.md             # This file.
└── DESCRIPTION.md        # Detailed project description.
