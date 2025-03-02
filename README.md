# UI Code Generator

## Description
The UI Code Generator is a Python-based tool that generates HTML layouts based on bounding box annotations. It utilizes Tailwind CSS for styling and provides a flexible way to create responsive web layouts.

## Features
- Generates HTML layouts from JSON annotations.
- Supports various UI components like buttons, headers, icons, and more.
- Utilizes Tailwind CSS for modern styling.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/prabhatpushp/UI-Code-Generator
   cd UI Code Generator
   ```
2. Set up a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use .venv\Scripts\activate
   ```
3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
1. Prepare your annotations in `annotations.json` format.
2. Run the main script to generate HTML:
   ```bash
   python generate_html.py
   ```
3. The output will be saved in `output.html`.

## File Structure
- `generate_html.py`: Main script for generating HTML.
- `output.html`: Generated HTML output.
- `annotations.json`: Input annotations for UI components.
- `classes.txt`: List of UI component classes.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any suggestions or improvements.

## License
This project is licensed under the MIT License. 
