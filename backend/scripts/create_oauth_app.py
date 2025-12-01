import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onestep.settings')
django.setup()

from oauth2_provider.models import Application
from django.contrib.auth import get_user_model

User = get_user_model()

def create_oauth_app():
    # Get or create admin user
    try:
        user = User.objects.get(username='admin')
    except User.DoesNotExist:
        print("Admin user not found. Creating...")
        user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print("Created admin user.")

    # Check if app exists
    app_name = "OneStep Frontend"
    try:
        app = Application.objects.get(name=app_name)
        print(f"Application '{app_name}' already exists. Updating to Public client...")
        app.client_type = Application.CLIENT_PUBLIC
        app.save()
    except Application.DoesNotExist:
        app = Application.objects.create(
            user=user,
            name=app_name,
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_PASSWORD,
            redirect_uris="http://localhost:5173/ http://localhost:3000/"
        )
        print(f"Created application '{app_name}'.")

    print("\nOAuth2 Credentials:")
    print(f"Client ID: {app.client_id}")
    print(f"Client Secret: {app.client_secret}")
    print("\nPlease update your frontend .env file with these values.")

if __name__ == "__main__":
    create_oauth_app()
