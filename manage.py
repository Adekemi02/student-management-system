import getpass
from flask.cli import FlaskGroup
from .api import create_app
from api.models.users import Admin
from werkzeug.security import generate_password_hash


app = create_app()
cli = FlaskGroup(create_app=create_app)

# Create admin user from the command line
@cli.command("create_admin")
def create_admin():
    first_name = input("Enter first name: ")
    last_name = input("Enter last name: ")
    email = input("Enter email: ")
    phone = input("Enter phone number: ")
    password = getpass.getpass("Enter password: ")
    confirm_password = getpass.getpass("Confirm password: ")
    role = input("Enter role: ")

    if password != confirm_password:
        print("Passwords do not match")
        return 1
    
    try:

        user = Admin(
            first_name = first_name,
            last_name = last_name,
            email = email,
            phone = phone,
            password_hash = generate_password_hash(password),
            user_type = 'admin',
            role = role,
            is_admin = True
        )

        # admin = User(user=user)

        user.save()

    except Exception as e:
        print("Error creating admin")
        print(e)
        # return 1
    print("Admin created successfully")

if __name__ == '__main__':
    cli()
