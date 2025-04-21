# Validation Rules and Input Formats

## Customer ID Validation
- Must be a numeric value
- Valid range: 1-3
- No decimal points allowed
- No special characters allowed

## Database Requirements
- MySQL server must be running
- Database 'hsbc_cc_db' must exist
- Required tables:
  - customers
  - accounts
  - transactions
  - rewards

## PDF Generation Rules
- Output directory 'statements' must be writable
- PDF filename format: statement_customer_[ID].pdf
- Previous statements will be overwritten

## Error Handling
- Invalid customer ID: Returns error page
- Database connection failure: Shows error message
- PDF generation failure: Shows error message