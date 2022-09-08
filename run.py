from app import create_app, db
from app.auth.models import User

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
