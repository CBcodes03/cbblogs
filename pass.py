from flask_bcrypt import Bcrypt
import mysql.connector
bcrypt = Bcrypt()


hashed = bcrypt.generate_password_hash("Cb@182003").decode("utf-8")
print(hashed)


#INSERT INTO users (name, email, password, is_admin)
#VALUES ('chirag', 'chiragbudakoti12334@gmail.com', '$2b$12$bFem6gU4I3wKBMP/5mtHkO/y/CjJasSLMgIu5yUVataPhGsiREA4i', 1);

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345678",
    database="ecomdb"
)
cursor = conn.cursor()
cursor.execute(
    "SELECT is_admin FROM users WHERE name = %s",
    ("chirag",)
)
row = cursor.fetchone()

if row and row[0] == 1:
    print(True)
else:
    print(False)
