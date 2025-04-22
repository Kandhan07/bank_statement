from flask import Flask, render_template, request, send_from_directory, url_for
from generate_pdf import create_statement_pdf
import os

app = Flask(__name__, static_url_path='/static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    customer_id = request.form.get('customer_id')
    try:
        customer_id = int(customer_id)
        if 1 <= customer_id <= 3:
            create_statement_pdf(customer_id)
            return render_template('success.html', customer_id=customer_id)
        else:
            return render_template('error.html', message="Please enter a valid customer ID (1-3)")
    except ValueError:
        return render_template('error.html', message="Please enter a valid number")

@app.route('/download/<customer_id>')
def download(customer_id):
    statements_dir = os.path.join(os.path.dirname(__file__), 'statements')
    return send_from_directory(statements_dir, f'statement_customer_{customer_id}.pdf')

if __name__ == '__main__':
    app.run(debug=True)