from pydrive.auth import GoogleAuth

# Create an instance of GoogleAuth
gauth = GoogleAuth()

# Load credentials from the JSON file
gauth.LoadCredentialsFile("client_secret.json")

# Try to authenticate using the loaded credentials
if gauth.credentials is None:
    # Authenticate using browser (local webserver) and save the credentials
    gauth.LocalWebserverAuth()
    gauth.SaveCredentialsFile("client_secret2.json")
else:
    # Use the loaded credentials
    gauth.Authorize()

# Create an instance of GoogleDrive
drive = gauth.GetDrive()

# Example: List files in the root folder of Google Drive
file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()

for file in file_list:
    print('File Title: %s, ID: %s' % (file['title'], file['id']))
