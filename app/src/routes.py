import os
import tempfile
from flask import render_template, request, redirect, url_for, flash, send_file, jsonify, session
from werkzeug.utils import secure_filename

from app.src.document_processor import (
    allowed_file, 
    extract_text_from_doc, 
    analyze_text, 
    create_formatted_document
)

from app.src import config


def register_routes(app):
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
        
        if file and allowed_file(file.filename, config.ALLOWED_EXTENSIONS):
            filename = secure_filename(file.filename)
            filepath = os.path.join(config.UPLOAD_FOLDER, filename)
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
            
            # In ra các tùy chọn định dạng để kiểm tra
            print(f"Các tùy chọn định dạng được chọn: {formatting_options}")
            
            # Trích xuất văn bản từ tài liệu
            content = extract_text_from_doc(filepath)
            if not content:
                flash('Lỗi đọc nội dung tài liệu')
                return redirect(url_for('index'))
            
            # Tạo tài liệu được định dạng
            # Sử dụng tempfile.mkdtemp để tạo thư mục tạm
            try:
                temp_dir = tempfile.mkdtemp()
                app.config['TEMP_FOLDER'] = temp_dir  # Lưu đường dẫn vào config để dễ truy cập
                
                output_filename = f"formatted_{filename.rsplit('.', 1)[0]}.docx"
                output_path = os.path.join(temp_dir, output_filename)
                
                print(f"Tạo file tại đường dẫn: {output_path}")
                formatted_file_path = create_formatted_document(content, formatting_options, output_path)
                
                if formatted_file_path and os.path.exists(formatted_file_path):
                    # Lưu thông tin file vào session để có thể tải xuống sau
                    session['last_formatted_file'] = formatted_file_path
                    session['last_formatted_filename'] = output_filename
                    
                    return redirect(url_for('download_file', filename=os.path.basename(formatted_file_path)))
                else:
                    flash('Lỗi định dạng tài liệu')
                    return redirect(url_for('index'))
            except Exception as e:
                print(f"Lỗi trong quá trình xử lý: {str(e)}")
                flash(f'Lỗi xử lý: {str(e)}')
                return redirect(url_for('index'))
        else:
            flash('Loại tệp không được phép')
            return redirect(url_for('index'))

    @app.route('/analyze', methods=['POST'])
    def analyze_document():
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if file and allowed_file(file.filename, config.ALLOWED_EXTENSIONS):
            filename = secure_filename(file.filename)
            filepath = os.path.join(config.UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            # Trích xuất văn bản từ tài liệu
            content = extract_text_from_doc(filepath)
            if not content:
                return jsonify({'error': 'Lỗi đọc nội dung tài liệu'}), 400
            
            # Phân tích văn bản
            analysis = analyze_text(content)
            
            return jsonify(analysis)
        else:
            return jsonify({'error': 'Loại tệp không được phép'}), 400

    @app.route('/download/<filename>')
    def download_file(filename):
        # Ưu tiên kiểm tra đường dẫn trong session nếu có
        if 'last_formatted_file' in session and session.get('last_formatted_filename') == filename:
            file_path = session.get('last_formatted_file')
            if os.path.exists(file_path):
                try:
                    return send_file(file_path, as_attachment=True)
                except Exception as e:
                    print(f"Lỗi khi tải file từ session: {str(e)}")
                    # Tiếp tục kiểm tra các vị trí khác
        
        # Kiểm tra trong thư mục tạm thời
        temp_dir = app.config.get('TEMP_FOLDER', config.TEMP_FOLDER)
        file_path = os.path.join(temp_dir, filename)
        
        # Kiểm tra nếu file tồn tại
        if os.path.exists(file_path):
            try:
                return send_file(file_path, as_attachment=True)
            except Exception as e:
                print(f"Lỗi khi tải file từ thư mục tạm: {str(e)}")
                flash(f"Lỗi khi tải file: {str(e)}")
                return redirect(url_for('index'))
        else:
            print(f"Không tìm thấy file: {file_path}")
            # Trường hợp file không tồn tại, thử tìm trong thư mục uploads
            upload_path = os.path.join(config.UPLOAD_FOLDER, filename)
            if os.path.exists(upload_path):
                try:
                    return send_file(upload_path, as_attachment=True)
                except Exception as e:
                    flash(f"Lỗi khi tải file: {str(e)}")
                    return redirect(url_for('index'))
            else:
                flash(f"Không tìm thấy file để tải xuống: {filename}")
                return redirect(url_for('index')) 