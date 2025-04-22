import mysql.connector

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Kandhan$2103',
    'database': 'hsbc_cc_db'
}

def test_connection():
    try:
        # Try to establish connection
        conn = mysql.connector.connect(**db_config)
        
        if conn.is_connected():
            print("Successfully connected to MySQL database!")
            
            # Test query
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM customers")
            customers = cursor.fetchall()
            print("\nCustomers in database:")
            for customer in customers:
                print(f"ID: {customer['customer_id']} - Name: {customer['full_name']}")
            
            cursor.close()
            conn.close()
            print("\nConnection closed.")
            
    except mysql.connector.Error as err:
        print(f"Error: {err}")

if __name__ == "__main__":
    test_connection()