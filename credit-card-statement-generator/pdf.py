import pymysql
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import os
import datetime

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

def generate_pdf(customer_info, transactions, rewards, output_path='credit_card_statement.pdf'):
    try:
        # Load HTML template
        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template('statement_template.html')

        html_out = template.render(
            customer=customer_info,
            transactions=transactions,
            rewards=rewards,
            date=datetime.date.today().strftime('%B %d, %Y')
        )

        # Create PDF
        HTML(string=html_out).write_pdf(output_path)
        print(f"PDF generated: {output_path}")

    except Exception as e:
        print(f"PDF generation error: {e}")

if __name__ == "__main__":
    customer_id = int(input("Enter Your Customer ID"))  # Change as needed
    customer_info, transactions, rewards = fetch_customer_data(customer_id)
    
    if customer_info:
        generate_pdf(customer_info, transactions, rewards)
