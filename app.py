import os
import requests
import json
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import tempfile
import time
import docx
from docx.shared import Pt, Inches
from docx.enum.text import WD_LINE_SPACING
import re

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
app.secret_key = os.urandom(24)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'doc', 'docx', 'txt'}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB max file size

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_doc(file_path):
    """Trích xuất văn bản từ tài liệu Word hoặc tệp văn bản."""
    if file_path.endswith('.docx'):
        doc = docx.Document(file_path)
        return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
    elif file_path.endswith('.txt'):
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    return None

def split_content_into_chunks(content, max_chunk_size=4000):
    """Chia nội dung thành các phần nhỏ hơn để xử lý."""
    # Chia theo đoạn văn
    paragraphs = content.split('\n\n')
    chunks = []
    current_chunk = []
    current_size = 0
    
    for paragraph in paragraphs:
        # Thêm độ dài của đoạn văn và một dòng mới
        paragraph_size = len(paragraph) + 2
        
        if current_size + paragraph_size > max_chunk_size:
            # Nếu chunk hiện tại đã đầy, lưu nó và bắt đầu chunk mới
            if current_chunk:
                chunks.append('\n\n'.join(current_chunk))
            current_chunk = [paragraph]
            current_size = paragraph_size
        else:
            # Thêm đoạn văn vào chunk hiện tại
            current_chunk.append(paragraph)
            current_size += paragraph_size
    
    # Thêm chunk cuối cùng nếu có
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))
    
    return chunks

def process_chunk_with_gemini(chunk, formatting_options):
    """Xử lý một phần nội dung với Gemini API."""
    prompt = f"""Format this part of academic text according to these specifications:
    - Citation style: {formatting_options['citation_style']}
    - Add section numbers (continue from previous if applicable)
    - Format citations and references
    - Create proper academic headings and subheadings
    - Maintain document flow and consistency
    
    Text to format:
    {chunk}
    """
    
    try:
        headers = {
            'Content-Type': 'application/json'
        }
        
        data = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }]
        }
        
        # Thêm API key vào URL
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            response_data = response.json()
            # Trích xuất văn bản từ phản hồi
            try:
                formatted_text = response_data['candidates'][0]['content']['parts'][0]['text']
                return formatted_text
            except (KeyError, IndexError) as e:
                print(f"Error parsing API response: {str(e)}")
                print(f"Response data: {response_data}")
                return chunk
        else:
            print(f"API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return chunk
            
    except Exception as e:
        print(f"Error in Gemini API chunk processing: {str(e)}")
        return chunk

def create_formatted_document(content, formatting_options, output_path):
    """Tạo tài liệu Word được định dạng dựa trên các tùy chọn định dạng."""
    doc = docx.Document()
    
    # Set margins
    sections = doc.sections
    for section in sections:
        if formatting_options['margin'] == 'normal':
            section.left_margin = section.right_margin = section.top_margin = section.bottom_margin = Inches(1)
        elif formatting_options['margin'] == 'wide':
            section.left_margin = section.right_margin = section.top_margin = section.bottom_margin = Inches(1.5)
        else:  # narrow
            section.left_margin = section.right_margin = section.top_margin = section.bottom_margin = Inches(0.5)

    # Thêm trang tiêu đề nếu được yêu cầu
    if formatting_options['title_page']:
        title_paragraph = doc.add_paragraph()
        title_run = title_paragraph.add_run("Document Title")
        title_run.font.size = Pt(16)
        title_run.font.name = formatting_options['font_family']
        doc.add_paragraph()

    # Thêm bảng nội dung nếu được yêu cầu
    if formatting_options['table_of_contents']:
        toc_paragraph = doc.add_paragraph()
        toc_run = toc_paragraph.add_run("Table of Contents")
        toc_run.font.size = Pt(14)
        toc_run.font.name = formatting_options['font_family']
        doc.add_paragraph()

    try:
        # Chia nội dung thành các phần nhỏ hơn
        content_chunks = split_content_into_chunks(content)
        formatted_text = ""
        
        # Xử lý từng phần với Gemini API
        for chunk in content_chunks:
            formatted_chunk = process_chunk_with_gemini(chunk, formatting_options)
            formatted_text += formatted_chunk + "\n\n"
        
        # Chia văn bản thành các phần dựa trên tiêu đề
        sections = re.split(r'\n(?=\d+\.|\#)', formatted_text)
        
        for section in sections:
            if not section.strip():
                continue
                
            paragraph = doc.add_paragraph()
            paragraph.style = 'Normal'
            
            # Set font
            run = paragraph.add_run(section.strip())
            run.font.name = formatting_options['font_family']
            run.font.size = Pt(int(formatting_options['font_size']))
            
            # Set line spacing
            if formatting_options['line_spacing'] == '2.0':
                paragraph.paragraph_format.line_spacing = 2.0
            elif formatting_options['line_spacing'] == '1.5':
                paragraph.paragraph_format.line_spacing = 1.5
            else:
                paragraph.paragraph_format.line_spacing = 1.0

        # Thêm số trang nếu được yêu cầu
        if formatting_options['page_numbers']:
            for section in doc.sections:
                footer = section.footer
                paragraph = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
                paragraph.alignment = 1  # Center
                run = paragraph.add_run()
                run.font.name = formatting_options['font_family']
                field = run.add_field('PAGE')

        doc.save(output_path)
        return output_path
        
    except Exception as e:
        print(f"Error in document creation: {str(e)}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Get formatting options from form
        formatting_options = {
            'citation_style': request.form.get('citation_style', 'apa'),
            'font_family': request.form.get('font_family', 'times'),
            'font_size': request.form.get('font_size', '12'),
            'line_spacing': request.form.get('line_spacing', '2.0'),
            'margin': request.form.get('margin', 'normal'),
            'paragraph_spacing': request.form.get('paragraph_spacing', 'after'),
            'page_numbers': 'page_numbers' in request.form,
            'title_page': 'title_page' in request.form,
            'table_of_contents': 'table_of_contents' in request.form,
            'bibliography': 'bibliography' in request.form
        }
        
        # Trích xuất văn bản từ tài liệu
        content = extract_text_from_doc(filepath)
        if not content:
            flash('Lỗi đọc nội dung tài liệu')
            return redirect(url_for('index'))
        
        # Tạo tài liệu được định dạng
        temp_dir = tempfile.mkdtemp()
        output_filename = f"formatted_{filename.rsplit('.', 1)[0]}.docx"
        output_path = os.path.join(temp_dir, output_filename)
        
        formatted_file_path = create_formatted_document(content, formatting_options, output_path)
        
        if formatted_file_path:
            return redirect(url_for('download_file', filename=os.path.basename(formatted_file_path)))
        else:
            flash('Lỗi định dạng tài liệu')
            return redirect(url_for('index'))
    else:
        flash('Loại tệp không được phép')
        return redirect(url_for('index'))

@app.route('/download/<filename>')
def download_file(filename):
    temp_dir = tempfile.gettempdir()
    return send_file(os.path.join(temp_dir, filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True) 