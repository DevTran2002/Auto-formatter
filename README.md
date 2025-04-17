# Document Formatter

A web application that allows users to upload document files, formats them using spaCy NLP, and provides the formatted versions for download.

## Features

- Upload document files (supports .doc, .docx, .txt)
- Format documents using spaCy for academic documents
- Advanced text analysis with spaCy NLP
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

4. Install spaCy language model:
   ```
   python setup_spacy.py
   ```
   Or manually:
   ```
   python -m spacy download en_core_web_sm
   ```

5. Run the application:
   ```
   python app.py
   ```

6. Open your browser and navigate to `http://127.0.0.1:5000`

## Text Analysis Features

The application includes advanced text analysis features powered by spaCy:

- Entity recognition (people, organizations, locations, etc.)
- Key phrase extraction
- Sentence and token analysis
- Noun chunk identification

## Academic Formatting Features

The application uses spaCy to intelligently format academic documents:

1. Automatically identifies headings and paragraphs
2. Formats citations based on selected style (APA, MLA, Chicago, IEEE)
3. Generates table of contents based on detected headings
4. Adds proper formatting for sections, references, and bibliography
5. Applies academic styling rules (font, spacing, margins)

## Technologies Used

- Flask: Web framework
- Requests: API communication
- Python-dotenv: Environment variable management
- python-docx: Word document handling
- spaCy: Natural Language Processing for both analysis and formatting

## License

MIT 

document-formatter/
│
├── app/                          # Thư mục chính của ứng dụng
│   ├── __init__.py               # Khởi tạo ứng dụng Flask
│   ├── templates/                # Các template HTML
│   │   └── index.html            # Giao diện người dùng
│   ├── static/                   # Tài nguyên tĩnh (CSS, JS)
│   │   └── style.css             # CSS cho giao diện
│   └── src/                      # Mã nguồn Python
│       ├── __init__.py           # Định nghĩa package
│       ├── config.py             # Cấu hình ứng dụng
│       ├── document_processor.py # Xử lý tài liệu và spaCy
│       └── routes.py             # Các route của Flask
│
├── uploads/                      # Thư mục lưu file tải lên
├── app.py                        # Điểm khởi chạy ứng dụng
├── requirements.txt              # Các thư viện cần thiết
├── setup_spacy.py                # Script cài đặt spaCy
└── README.md                     # Hướng dẫn sử dụng