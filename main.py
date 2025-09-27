import pandas as pd
import googlemaps
import json
import tkinter as tk
from tkinter import filedialog, messagebox
import webbrowser
from flask import Flask, render_template

# Initialize Flask app
app = Flask(__name__)

# Google Maps API key
api_key = ''
gmaps = googlemaps.Client(key=api_key)

# Global variable to store address markers
address_markers = []

def display_message_and_select_file():
    """Display a message and open a file dialog to select an Excel file."""
    root = tk.Tk()
    root.withdraw()  # Hide the main Tkinter window

    # Display the message
    messagebox.showinfo(
        "Choose File",
        "Choose File to Import to the Map. It must contain the 'Address' column."
    )

    # Open the file dialog
    file_path = filedialog.askopenfilename(
        title="Select an Excel File",
        filetypes=[("Excel Files", "*.xlsx *.xls")]
    )

    if not file_path:
        raise FileNotFoundError("No file selected.")

    return file_path

def read_addresses(file_path):
    """Read addresses from the selected Excel file."""
    df = pd.read_excel(file_path)
    if 'Address' not in df.columns:
        raise ValueError("The selected file does not contain an 'Address' column.")
    return df['Address'].tolist()

def geocode_addresses(addresses):
    """Geocode a list of addresses."""
    locations = []
    for address in addresses:
        geocode_result = gmaps.geocode(address)
        if geocode_result:
            lat_lng = geocode_result[0]['geometry']['location']
            print(f"Address: {address}, Lat/Lng: {lat_lng}")
            locations.append((lat_lng['lat'], lat_lng['lng']))
        else:
            print(f"Geocoding failed for address: {address}")
    return locations

def get_address_markers(locations):
    """Convert geocoded locations to marker format."""
    markers = []
    for location in locations:
        markers.append({'lat': location[0], 'lng': location[1]})
    return markers

@app.route('/')
def home():
    """Render the HTML template with address markers."""
    return render_template('index.html', address_markers=address_markers)

def main():
    global address_markers  # Make address_markers global so it can be used in the Flask route

    try:
        # Display message and let the user choose the file
        file_path = display_message_and_select_file()

        # Read addresses from the file
        addresses = read_addresses(file_path)

        # Geocode addresses to get latitude and longitude
        locations = geocode_addresses(addresses)

        # Convert locations to marker format
        address_markers = get_address_markers(locations)

        # Show success message
        messagebox.showinfo(
            "File Upload Status",
            "File uploaded and processed successfully! The map will now open in your browser."
        )

        print("Address markers processed successfully!")

        # Start the Flask server
        webbrowser.open('http://127.0.0.1:5000')  # Open the browser automatically
        app.run(debug=False)  # Disable debug mode to prevent double execution

    except FileNotFoundError:
        messagebox.showerror(
            "File Upload Status",
            "No file was selected. Please try again."
        )
    except ValueError as e:
        messagebox.showerror(
            "File Upload Status",
            f"Error: {e}"
        )
    except Exception as e:
        messagebox.showerror(
            "File Upload Status",
            f"An unexpected error occurred: {e}"
        )
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
