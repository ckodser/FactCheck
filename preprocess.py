import os
import json
from hazm import Normalizer

def load_data(folder_path):
    data = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                try:
                    json_data = json.load(file)  # Load the JSON data
                    if isinstance(json_data, list):  # Ensure it's a list
                        data.extend(json_data)
                    else:
                        print(f"File {filename} does not contain a list. Skipping...")
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON in file {filename}: {e}")
    return data

# Path to your data folder
data_folder_path = 'ndata'

# Load the data
data = load_data(data_folder_path)

# Initialize Persian text normalizer
normalizer = Normalizer()

# Function to clean Persian text
def clean_text(text):
    text = text.replace('ي', 'ی').replace('ك', 'ک')  # Normalize Persian characters
    text = normalizer.normalize(text)  # Normalize Persian characters
    return text

# Extract relevant fields and clean them
processed_data = []
for entry in data:
    if "text" in entry:  # Ensure the "text" field exists
        processed_entry = {
            "key": entry.get("key", ""),  # Use the key or default to an empty string
            "text": clean_text(entry["text"]),  # Clean and normalize the text
            "persian_date": entry.get("persian_date", "Unknown Date"),  # Use the date or default to "Unknown Date"
            "url": entry.get("url", "No URL"),  # Use the URL or default to "No URL"
        }
        processed_data.append(processed_entry)

print("Number of processed entries:", len(processed_data))

# Save processed data to a new file
output_file_path = 'processed_data.json'

# Save the processed data as JSON
with open(output_file_path, 'w', encoding='utf-8') as output_file:
    json.dump(processed_data, output_file, ensure_ascii=False, indent=4)

print(f"Processed data saved to {output_file_path}")
