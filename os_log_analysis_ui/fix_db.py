import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='NewPassword123',
    database='oslog_analysis'
)

cursor = conn.cursor()

# Add password column if it doesn't exist
try:
    cursor.execute('ALTER TABLE users ADD COLUMN password VARCHAR(255) AFTER username')
    conn.commit()
    print('✓ Password column added successfully')
except mysql.connector.Error as e:
    if 'Duplicate column name' in str(e):
        print('✓ Password column already exists')
    else:
        print(f'Error: {e}')

# Verify the column was added
cursor.execute('DESCRIBE users')
columns = cursor.fetchall()
print('\nUsers table columns after fix:')
for col in columns:
    print(f'  {col[0]}: {col[1]}')

cursor.close()
conn.close()
