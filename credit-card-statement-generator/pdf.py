import pymysql
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import os
import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from datetime import datetime

# Configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Kandhan$2103",
    "database": "hsbc_cc_db"
}

def fetch_customer_data(customer_id):
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        # Get customer and account info
        cursor.execute("""
            SELECT c.full_name, c.address, a.card_number, a.account_number, a.credit_limit, a.available_credit
            FROM customers c
            JOIN accounts a ON c.customer_id = a.customer_id
            WHERE c.customer_id = %s
        """, (customer_id,))
        customer_info = cursor.fetchone()

        if not customer_info:
            raise ValueError("Customer not found.")

        # Get transactions
        cursor.execute("""
            SELECT transaction_date, description, amount, transaction_type
            FROM transactions
            JOIN accounts ON transactions.account_id = accounts.account_id
            WHERE accounts.customer_id = %s
            ORDER BY transaction_date
        """, (customer_id,))
        transactions = cursor.fetchall()

        # Get rewards
        cursor.execute("""
            SELECT earned_points, redeemed_points, available_points
            FROM rewards
            JOIN accounts ON rewards.account_id = accounts.account_id
            WHERE accounts.customer_id = %s
        """, (customer_id,))
        rewards = cursor.fetchone()

        return customer_info, transactions, rewards

    except Exception as e:
        print(f"Database error: {e}")
        return None, None, None
    finally:
        if connection:
            connection.close()

def generate_pdf(customer_info, transactions, rewards, output_path):
    try:
        c = canvas.Canvas(output_path, pagesize=letter)
        
        # Header
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, 750, "Credit Card Statement")
        
        # Customer Info
        c.setFont("Helvetica", 12)
        c.drawString(50, 700, f"Name: {customer_info['name']}")
        c.drawString(50, 680, f"Address: {customer_info['address']}")
        c.drawString(50, 660, f"Card Number: {customer_info['card_number']}")
        
        # Transactions
        c.drawString(50, 620, "Transactions:")
        y = 600
        for t in transactions:
            c.drawString(50, y, f"{t['date']} - {t['description']} - ${t['amount']}")
            y -= 20
            
        # Rewards
        c.drawString(50, y-20, f"Reward Points: {rewards['points']}")
        c.drawString(50, y-40, f"Cashback: ${rewards['cashback']}")
        
        c.save()
        return True
    except Exception as e:
        print(f"PDF generation error: {str(e)}")
        return False

def generate_pdf(customer_info, transactions, rewards, language='en', output_path='credit_card_statement.pdf'):
    try:
        # Setup template loader to look inside templates folder
        env = Environment(loader=FileSystemLoader('templates'))
        
        # Load template based on selected language
        template_file = f'statement_template_{language}.html'  # e.g., statement_template_es.html for Spanish
        template = env.get_template(template_file)

        html_out = template.render(
            customer=customer_info,
            transactions=transactions,
            rewards=rewards,
            date=datetime.date.today().strftime('%B %d, %Y')
        )

        # Base URL must point to project root (where 'static/' is located)
        base_url = os.getcwd()

        # Debug info
        print(f"Generating PDF with base_url: {base_url}")
        logo_path = os.path.join(base_url, 'static', 'images', '6379114.jpg')
        print(f"Logo exists: {os.path.exists(logo_path)}")

        HTML(string=html_out, base_url=base_url).write_pdf(output_path)
        print(f"PDF generated: {output_path}")

    except Exception as e:
        print(f"PDF generation error: {e}")

if __name__ == "__main__":
    customer_id = int(input("Enter Your Customer ID: "))
    language = input("Select Language (en, es, fr, etc.): ")  # Get language selection
    customer_info, transactions, rewards = fetch_customer_data(customer_id)

    if customer_info:
        generate_pdf(customer_info, transactions, rewards, language)
