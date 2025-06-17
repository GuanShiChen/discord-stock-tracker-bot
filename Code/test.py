import re
from datetime import datetime
from bs4 import BeautifulSoup
import os # Import the os module to help with file paths if needed

# --- Configuration ---
file_path = 'website.html' # Name of your HTML file
# Or provide a full path:
# file_path = '/path/to/your/folder/inventory.html' 
# For example on Windows: file_path = 'C:\\Users\\YourUser\\Documents\\inventory.html'

userid = "user123"
msg = ""

# --- Read HTML content from the file ---
html_content = ""
try:
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    print(f"Successfully read content from: {file_path}")
except FileNotFoundError:
    print(f"Error: The file '{file_path}' was not found.")
    # You might want to exit or handle this error gracefully
    exit() 
except Exception as e:
    print(f"An error occurred while reading the file: {e}")
    exit()

# --- Process the HTML content (same as before) ---
if html_content: # Only proceed if content was successfully read
    soup = BeautifulSoup(html_content, 'html.parser')
    inventory_span = soup.find('span', class_='inventoryCnt')

    if inventory_span:
        inventory_count_full_text = inventory_span.get_text(strip=True)
        
        # Use a regular expression to find all digits
        numbers = re.findall(r'\d+', inventory_count_full_text)
        
        if numbers:
            inventory_count = numbers[0] # Take the first number found
        else:
            inventory_count = "N/A" # Or handle cases where no number is found
            
        msg += userid + " " + datetime.now().strftime("%Y-%m-%d, %H:%M:%S") + " --> Inventory Count: " + inventory_count
    else:
        msg += userid + " " + datetime.now().strftime("%Y-%m-%d, %H:%M:%S") + " --> Inventory Span not found."
else:
    msg += userid + " " + datetime.now().strftime("%Y-%m-%d, %H:%M:%S") + " --> No HTML content to process."

print(msg)