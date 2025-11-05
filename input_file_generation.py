import pandas as pd
import os
import logging
from typing import Optional

def read_excel_file(file_path: str) -> pd.DataFrame:
    """Read the input Excel file."""
    try:
        return pd.read_excel(file_path)
    except Exception as e:
        logging.error(f"Error reading Excel file {file_path}: {e}")
        raise

def read_config_files(config_folder: str) -> dict:
    """Read configuration files from the folder."""
    config_data = {}
    try:
        # Read all configuration files in the folder
        for file_name in os.listdir(config_folder):
            file_path = os.path.join(config_folder, file_name)
            if file_path.endswith('.txt'):
                with open(file_path, 'r') as f:
                    # Store file content with filename as key
                    config_data[file_name] = f.read().strip()
    except Exception as e:
        logging.error(f"Error reading config files from {config_folder}: {e}")
        raise
    return config_data

def read_dff_file(dff_path: str) -> pd.DataFrame:
    """Read the DFF Excel file."""
    try:
        return pd.read_excel(dff_path)
    except Exception as e:
        logging.error(f"Error reading DFF file {dff_path}: {e}")
        raise

def process_data(input_df: pd.DataFrame, config_data: dict, dff_df: pd.DataFrame, is_xml: bool) -> pd.DataFrame:
    """Process the input data using configuration and DFF information."""
    try:
        # Create a copy of input dataframe to avoid modifying original
        result_df = input_df.copy()
        
        # Add DFF information if available
        if not dff_df.empty:
            result_df = pd.merge(
                result_df,
                dff_df,
                how='left',
                left_on='DESCRIPTIVE_FLEXFIELD_NAME',
                right_on='DESCRIPTIVE_FLEXFIELD_NAME'
            )
        
        # Apply configuration rules
        for config_name, config_value in config_data.items():
            # Add configuration as new column
            col_name = f"CONFIG_{config_name.replace('.txt', '')}"
            result_df[col_name] = config_value
        
        # If XML processing is required
        if is_xml:
            # Add XML-specific processing here
            result_df['XML_PROCESSED'] = 'Yes'
        
        return result_df
        
    except Exception as e:
        logging.error(f"Error processing data: {e}")
        raise

def save_output(df: pd.DataFrame, output_path: str) -> None:
    """Save the processed data to output Excel file."""
    try:
        df.to_excel(output_path, index=False)
        logging.info(f"Output saved successfully to {output_path}")
    except Exception as e:
        logging.error(f"Error saving output to {output_path}: {e}")
        raise

def main(input_path: str, config_folder: str, dff_path: str, output_path: str, is_xml: Optional[bool] = False) -> None:
    """Main function to orchestrate the file generation process."""
    try:
        # Step 1: Read input Excel file
        input_df = read_excel_file(input_path)
        logging.info(f"Input file read successfully: {input_path}")

        # Step 2: Read configuration files
        config_data = read_config_files(config_folder)
        logging.info(f"Configuration files read successfully from: {config_folder}")

        # Step 3: Read DFF file
        dff_df = read_dff_file(dff_path)
        logging.info(f"DFF file read successfully: {dff_path}")

        # Step 4: Process the data
        result_df = process_data(input_df, config_data, dff_df, is_xml)
        logging.info("Data processed successfully")

        # Step 5: Save output
        save_output(result_df, output_path)
        logging.info(f"Process completed successfully. Output saved to: {output_path}")

    except Exception as e:
        logging.error(f"Error in main process: {e}")
        raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Example usage
    main(
        input_path="input.xlsx",
        config_folder="config",
        dff_path="dff.xlsx",
        output_path="out1.xls",
        is_xml=False
    )