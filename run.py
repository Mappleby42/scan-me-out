from app import create_app, db
from app.auth.models import User
import sqlite3 as sql

#connect to SQLite
con = sql.connect('instance/db_employees.db')

#Create a Connection
cur = con.cursor()

#Drop users table if already exsist.
cur.execute("DROP TABLE IF EXISTS users")

#Create users table  in db_employees database
sql ='''CREATE TABLE "users" (
	"UID"	INTEGER PRIMARY KEY AUTOINCREMENT,
	"UNAME"	TEXT,
	"CODE"	TEXT,
	"ADMIN_ID"	INTEGER,
	"ONSITE"	BOOLEAN,
	"CONTACT"	TEXT
)'''
cur.execute(sql)

#commit changes
con.commit()

#close the connection
con.close()


#if __name__ == '__main__':
flask_app = create_app('prod')
with flask_app.app_context():
    db.create_all()
    if not User.query.filter_by(user_name='Admin').first():
        User.create_user(user='Admin',
                         email='matthew.appleby@peters-research.com',
                         super_user=True,
                         password='z6hfQ9MDV9UFsFZ')
flask_app.run()
#flask_app.run(ssl_context=('cert.pem', 'key.pem'))
