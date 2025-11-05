from flask import Flask, request, jsonify, Response
import os
import zipfile
import pandas as pd
import logging
import input_file_generation # your existing script
from flask_cors import CORS
from io import BytesIO
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
# -------------------------------
# Configuration
# -------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
BASE_DIR = os.path.join(os.path.dirname(__file__), "generated_files")
os.makedirs(BASE_DIR, exist_ok=True)
# -------------------------------
# Health Check Endpoint
# -------------------------------
@app.route('/health', methods=['GET'])
def health_check():
  """Simple health check endpoint"""
  try:
    return jsonify({"status": "healthy"}), 200
  except Exception as e:
    logging.exception("Health check failed")
    return jsonify({"status": "unhealthy", "error": str(e)}), 500
# -------------------------------
# Generate File Endpoint
# -------------------------------
@app.route('/generate', methods=['POST'])
def generate_file():
  try:
    # :one: Get uploaded files
    excel_file = request.files.get('excel_file')
    folder_zip = request.files.get('folder_zip')
    if not excel_file or not folder_zip:
      logging.error("Missing required files.")
      return jsonify({"error": "Missing required files (excel_file or folder_zip)"}), 400
    # :two: Save Excel file
    excel_path = os.path.join(BASE_DIR, excel_file.filename)
    excel_file.save(excel_path)
    logging.info(f"Excel saved at: {excel_path}")
    # :three: Save and unzip folder
    zip_path = os.path.join(BASE_DIR, folder_zip.filename)
    folder_zip.save(zip_path)
    folder_path = os.path.join(BASE_DIR, "folder")
    os.makedirs(folder_path, exist_ok=True)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
      zip_ref.extractall(folder_path)
    logging.info(f"Folder unzipped at: {folder_path}")
    # :four: Create an empty DFF Excel file
    dff_path = os.path.join(BASE_DIR, "empty_dff.xlsx")
    pd.DataFrame(columns=[
      "DESCRIPTIVE_FLEXFIELD_NAME",
      "END_USER_COLUMN_NAME",
      "FORM_LEFT_PROMPT"
    ]).to_excel(dff_path, index=False)
    logging.info(f"Empty DFF created at: {dff_path}")
    # :five: Output file path
    output_path = os.path.join(BASE_DIR, "output.xlsx")
    # :six: Call your generation script with error logging
    try:
      input_file_generation.main(
        input_path=excel_path,
        config_folder=folder_path,
        dff_path=dff_path,
        output_path=output_path,
        is_xml=False
      )
    except Exception as e:
      logging.exception("Error in input_file_generation.main")
      return jsonify({"error": f"Generation failed: {e}"}), 500
    # :seven: Verify output file
    if not os.path.exists(output_path):
      logging.error("Output file not generated")
      return jsonify({"error": "Output file not generated"}), 500
    logging.info(f"Returning generated Excel file: {output_path}")
    # :eight: Return file as response
    with open(output_path, 'rb') as f:
      file_data = f.read()
    resp = Response(file_data)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Expose-Headers'] = 'Content-Disposition'
    resp.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    resp.headers['Content-Disposition'] = f'attachment; filename="{os.path.basename(output_path)}"'
    resp.headers['Content-Length'] = str(len(file_data))
    resp.headers['Cache-Control'] = 'no-store'
    return resp
  except Exception as e:
    logging.exception("Server error")
    return jsonify({"error": str(e)}), 500
if __name__ == '__main__':
  # Use 0.0.0.0 for external access
  app.run(host='0.0.0.0', port=5001, debug=False)