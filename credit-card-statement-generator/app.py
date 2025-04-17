from flask import Flask, render_template, request, send_from_directory
from pdf import fetch_customer_data, generate_pdf
import os

app = Flask(__name__)
# Define absolute path for statements folder
STATEMENTS_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'statements')

# Ensure the statements directory exists
if not os.path.exists(STATEMENTS_FOLDER):
    os.makedirs(STATEMENTS_FOLDER)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            customer_id = request.form['customer_id']
            
            # Fetch data from DB
            customer_info, transactions, rewards = fetch_customer_data(int(customer_id))
            
            if customer_info:
                filename = f"statement_{customer_id}.pdf"
                output_path = os.path.join(STATEMENTS_FOLDER, filename)
                generate_pdf(customer_info, transactions, rewards, output_path)
                # Add debug print to verify file creation
                print(f"PDF generated at: {output_path}")
                print(f"File exists: {os.path.exists(output_path)}")
                return render_template('success.html', filename=filename)
            else:
                return "Customer not found", 404
        except Exception as e:
            print(f"Error processing request: {e}")
            return f"An error occurred: {str(e)}", 500
    
    return render_template('index.html')

# Make sure this route matches what's expected in success.html
@app.route('/download/<filename>')
def download(filename):
    # Add debug prints
    print(f"Download requested for: {filename}")
    print(f"From directory: {STATEMENTS_FOLDER}")
    print(f"Full path: {os.path.join(STATEMENTS_FOLDER, filename)}")
    print(f"File exists: {os.path.exists(os.path.join(STATEMENTS_FOLDER, filename))}")
    
    # Ensure file exists before trying to send it
    if not os.path.exists(os.path.join(STATEMENTS_FOLDER, filename)):
        return "File not found", 404
    
    return send_from_directory(directory=STATEMENTS_FOLDER, path=filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)