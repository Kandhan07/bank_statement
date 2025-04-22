from flask import Flask, render_template, request, send_from_directory, url_for, redirect
from generate_pdf import create_statement_pdf, get_data_from_db
import os
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_url_path='/static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/bank_statement')
def bank_statement():
    return render_template('bank_statement.html')

@app.route('/generate', methods=['POST'])
def generate():
    customer_id = request.form.get('customer_id')
    try:
        customer_id = int(customer_id)
        logger.debug(f"Processing request for customer_id: {customer_id}")
        
        # Check if logo exists
        logo_path = os.path.join(os.path.dirname(__file__), 'static', 'images', 'logo.png')
        if not os.path.exists(logo_path):
            logger.error(f"Logo not found at: {logo_path}")
            return render_template('error.html', message="Missing required assets")
            
        # Check statements directory
        statements_dir = os.path.join(os.path.dirname(__file__), 'statements')
        if not os.path.exists(statements_dir):
            os.makedirs(statements_dir)
            logger.debug(f"Created statements directory at: {statements_dir}")
        
        if 1 <= customer_id <= 3:
            data = get_data_from_db(customer_id)
            logger.debug(f"Database response: {data is not None}")
            
            if data and len(data) > 0:
                logger.debug("Generating PDF...")
                pdf_path = create_statement_pdf(customer_id)
                
                if pdf_path:
                    logger.debug(f"PDF generated successfully at: {pdf_path}")
                    if os.path.exists(pdf_path):
                        logger.debug("PDF file exists")
                        return render_template('success.html', customer_id=customer_id)
                    else:
                        logger.error("PDF file not found after generation")
                        return render_template('error.html', message="PDF generation failed")
                else:
                    logger.error("PDF generation returned None")
                    return render_template('error.html', message="Failed to generate statement")
            else:
                logger.error("No customer data found")
                return render_template('error.html', message="Customer data not found")
        else:
            logger.error(f"Invalid customer ID: {customer_id}")
            return render_template('error.html', message="Please enter a valid customer ID (1-3)")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return render_template('error.html', message=f"An error occurred: {str(e)}")

@app.route('/download/<customer_id>')
def download(customer_id):
    try:
        statements_dir = os.path.join(os.path.dirname(__file__), 'statements')
        return send_from_directory(statements_dir, f'statement_customer_{customer_id}.pdf')
    except:
        return render_template('error.html', message="File not found")

# Add these test routes after your existing routes

@app.route('/test-logo')
def test_logo():
    logo_path = os.path.join(os.path.dirname(__file__), 'static', 'images', 'logo.png')
    if os.path.exists(logo_path):
        return f"Logo found at: {logo_path}"
    return "Logo not found"

@app.route('/test-db/<int:customer_id>')
def test_db(customer_id):
    data = get_data_from_db(customer_id)
    if data:
        return f"Found data for customer {customer_id}"
    return "No data found"

@app.route('/test-pdf/<int:customer_id>')
def test_pdf(customer_id):
    try:
        # Get data first
        data = get_data_from_db(customer_id)
        if not data:
            return "No data found for PDF generation"
            
        # Try to create PDF
        logger.debug("Starting PDF generation...")
        pdf_path = create_statement_pdf(customer_id)
        logger.debug(f"PDF path returned: {pdf_path}")
        
        if pdf_path:
            if os.path.exists(pdf_path):
                file_size = os.path.getsize(pdf_path)
                return f"PDF created at: {pdf_path} (Size: {file_size} bytes)"
            else:
                return f"PDF path returned but file not found: {pdf_path}"
        return "PDF creation failed - no path returned"
    except Exception as e:
        logger.error(f"PDF generation error: {str(e)}")
        return f"Error creating PDF: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)