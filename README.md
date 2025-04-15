# Document Formatter

A web application that allows users to upload document files, formats them using an API, and provides the formatted versions for download.

## Features

- Upload document files (supports .doc, .docx, .txt, .pdf)
- Format documents using an external API
- Download the formatted documents

## Setup

1. Clone this repository:
   ```
   git clone <repository-url>
   cd document-formatter
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On macOS/Linux
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up your API key:
   - Rename the `.env.example` file to `.env`
   - Replace `your_api_key_here` with your actual API key

5. Run the application:
   ```
   python app.py
   ```

6. Open your browser and navigate to `http://127.0.0.1:5000`

## API Configuration

The application is configured to work with a document formatting API. You need to:

1. Update the API endpoint URL in the `format_document` function in `app.py`
2. Ensure your API key is correctly set in the `.env` file
3. Adjust the API parameters in the `payload` dictionary if needed, based on your API's requirements

## Technologies Used

- Flask: Web framework
- Requests: API communication
- Python-dotenv: Environment variable management
- Werkzeug: File handling utilities

## License

MIT 