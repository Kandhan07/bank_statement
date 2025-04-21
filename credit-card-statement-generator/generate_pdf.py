from fpdf import FPDF
import mysql.connector
from datetime import datetime
import os

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Kandhan$2103',
    'database': 'hsbc_cc_db'
}

def get_data_from_db(customer_id=1):  # Default to first customer
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # Get specific customer data
        query = """
        SELECT 
            c.full_name, c.email, c.phone, c.address,
            a.card_number, a.account_number, a.credit_limit, a.available_credit,
            t.transaction_date, t.description, t.amount, t.transaction_type,
            r.available_points
        FROM customers c
        JOIN accounts a ON c.customer_id = a.customer_id
        JOIN transactions t ON a.account_id = t.account_id
        JOIN rewards r ON a.account_id = r.account_id
        WHERE c.customer_id = %s
        ORDER BY t.transaction_date DESC
        """
        
        cursor.execute(query, (customer_id,))
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        return None

# Add this near the top of your file after imports
def ensure_statements_directory():
    statements_dir = os.path.join(os.path.dirname(__file__), 'statements')
    if not os.path.exists(statements_dir):
        os.makedirs(statements_dir)
    return statements_dir

# In your create_statement_pdf function, modify the output_file line:
def create_statement_pdf(customer_id=1):
    # Get data from database
    data = get_data_from_db(customer_id)
    if not data or len(data) == 0:
        print("No data found or database error")
        return
    
    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    
    # Get first row for customer details
    customer = data[0]
    
    # Add HSBC logo
    logo_path = os.path.join(os.path.dirname(__file__), 'static', 'images', 'logo.png')
    pdf.image(logo_path, x=10, y=10, w=30)
    
    # Header with date and statement number
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(30)  # Space for logo
    pdf.cell(0, 10, 'Credit Card Statement', 0, 1, 'C')
    
    pdf.set_font('Arial', '', 10)
    pdf.cell(30)  # Space for logo
    pdf.cell(0, 5, f'Statement Date: {datetime.now().strftime("%B %d, %Y")}', 0, 1, 'C')
    pdf.ln(15)
    
    # Add decorative line
    pdf.set_draw_color(219, 0, 17)  # HSBC Red
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(10)
    
    # Customer Information Section
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Customer Information', 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 6, f"Name: {customer['full_name']}", 0, 1)
    pdf.cell(0, 6, f"Email: {customer['email']}", 0, 1)
    pdf.cell(0, 6, f"Phone: {customer['phone']}", 0, 1)
    pdf.cell(0, 6, f"Address: {customer['address']}", 0, 1)
    pdf.ln(5)
    
    # Account Information Section
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Account Information', 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 6, f"Card Number: XXXX-XXXX-XXXX-{customer['card_number'][-4:]}", 0, 1)
    pdf.cell(0, 6, f"Account Number: {customer['account_number']}", 0, 1)
    pdf.cell(0, 6, f"Credit Limit: ${customer['credit_limit']:,.2f}", 0, 1)
    pdf.cell(0, 6, f"Available Credit: ${customer['available_credit']:,.2f}", 0, 1)
    pdf.cell(0, 6, f"Reward Points: {customer['available_points']}", 0, 1)
    pdf.ln(10)
    
    # Transaction Section
    # Modify Transaction Section styling
    pdf.set_fill_color(219, 0, 17)  # HSBC Red
    pdf.set_text_color(255, 255, 255)  # White text
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Transaction History', 0, 1, 'L', True)
    pdf.ln(5)
    
    # Transaction header with improved styling
    pdf.set_font('Arial', 'B', 10)
    pdf.set_fill_color(240, 240, 240)  # Light gray
    pdf.set_text_color(0, 0, 0)  # Black text
    pdf.cell(30, 7, 'Date', 1, 0, 'C', True)
    pdf.cell(80, 7, 'Description', 1, 0, 'C', True)
    pdf.cell(40, 7, 'Type', 1, 0, 'C', True)
    pdf.cell(40, 7, 'Amount', 1, 1, 'C', True)
    
    # Transactions with alternating colors
    pdf.set_font('Arial', '', 9)
    total_debit = 0
    total_credit = 0
    
    for i, row in enumerate(data):
        # Alternate row colors
        if i % 2 == 0:
            pdf.set_fill_color(255, 255, 255)  # White
        else:
            pdf.set_fill_color(245, 245, 245)  # Light gray
            
        pdf.cell(30, 6, row['transaction_date'].strftime('%Y-%m-%d'), 1, 0, 'L', True)
        pdf.cell(80, 6, row['description'], 1, 0, 'L', True)
        pdf.cell(40, 6, row['transaction_type'], 1, 0, 'C', True)
        
        # Color code the amounts
        amount = row['amount']
        if row['transaction_type'] == 'DEBIT':
            pdf.set_text_color(219, 0, 17)  # Red for debits
            total_debit += amount
        else:
            pdf.set_text_color(0, 102, 204)  # Blue for credits
            total_credit += amount
            
        pdf.cell(40, 6, f"${amount:,.2f}", 1, 1, 'R', True)
        pdf.set_text_color(0, 0, 0)  # Reset text color
    
    # Summary Section with improved styling
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 10)
    pdf.set_draw_color(200, 200, 200)
    pdf.set_line_width(0.1)
    pdf.line(130, pdf.get_y(), 200, pdf.get_y())
    
    # Right-aligned summary
    pdf.set_text_color(219, 0, 17)  # Red for debits
    pdf.cell(130)  # Move to right side
    pdf.cell(30, 6, "Total Debits:", 0, 0, 'L')
    pdf.cell(40, 6, f"${total_debit:,.2f}", 0, 1, 'R')
    
    pdf.set_text_color(0, 102, 204)  # Blue for credits
    pdf.cell(130)
    pdf.cell(30, 6, "Total Credits:", 0, 0, 'L')
    pdf.cell(40, 6, f"${total_credit:,.2f}", 0, 1, 'R')
    
    pdf.set_text_color(0, 0, 0)  # Black for net
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(130)
    pdf.cell(30, 8, "Net Activity:", 0, 0, 'L')
    pdf.cell(40, 8, f"${total_credit - total_debit:,.2f}", 0, 1, 'R')
    
    # Save the PDF
    statements_dir = ensure_statements_directory()
    output_file = os.path.join(statements_dir, f'statement_customer_{customer_id}.pdf')
    pdf.output(output_file)
    print(f"PDF generated successfully: {output_file}")

if __name__ == "__main__":
    try:
        customer_id = int(input("Enter customer ID to generate statement (1-3): "))
        if customer_id < 1 or customer_id > 3:
            print("Invalid customer ID. Please enter a number between 1 and 3.")
        else:
            create_statement_pdf(customer_id)
    except ValueError:
        print("Please enter a valid number.")