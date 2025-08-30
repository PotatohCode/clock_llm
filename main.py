import csv
import argparse
import os
from compliance_checker.analyzer import analyze_feature_description

def process_csv(input_filepath: str, output_filepath: str):
    """
    Reads a CSV file with feature descriptions, analyzes each feature,
    and writes the results to a new CSV file.

    Args:
        input_filepath: Path to the input CSV file.
        output_filepath: Path to the output CSV file.
    """
    # No API key check needed for Ollama
    print("Using Ollama with DeepSeek-R1 model...")
    print("Make sure Ollama is running locally (ollama serve)")
    print("And that you have pulled the model (ollama pull deepseek-r1)\n")

    try:
        with open(input_filepath, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames + [
                'is_geo_compliance_needed',
                'reasoning',
                'relevant_regulation'
            ]

            rows = list(reader) # Read all rows into memory to handle progress

            results = []
            total_rows = len(rows)

            print(f"Starting analysis of {total_rows} features...")

            for i, row in enumerate(rows):
                feature_name = row.get('feature_name', 'N/A')
                description = row.get('feature_description', '')

                print(f"[{i+1}/{total_rows}] Analyzing feature: '{feature_name}'...")

                if not description.strip():
                    print(f"  -> Skipping feature '{feature_name}' due to empty description.")
                    analysis_result = {
                        'is_geo_compliance_needed': None,
                        'reasoning': 'Skipped: Empty feature description.',
                        'relevant_regulation': 'N/A'
                    }
                else:
                    analysis_result = analyze_feature_description(description)

                # Combine original row with analysis results
                row.update(analysis_result)
                results.append(row)

            # Write results to the output file
            with open(output_filepath, mode='w', encoding='utf-8', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)

            print(f"\nAnalysis complete. Results saved to '{output_filepath}'")

    except FileNotFoundError:
        print(f"Error: Input file not found at '{input_filepath}'")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Analyze feature descriptions for geo-specific compliance requirements."
    )
    parser.add_argument(
        "--input",
        type=str,
        default="sample_data.csv",
        help="Path to the input CSV file. (default: sample_data.csv)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="analysis_results.csv",
        help="Path to the output CSV file. (default: analysis_results.csv)"
    )
    args = parser.parse_args()

    process_csv(args.input, args.output)