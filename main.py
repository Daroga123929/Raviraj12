from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for
import threading
import requests
import os
import time
from colorama import Fore, init
import random
import string
from functools import wraps
from datetime import datetime, timedelta
import json

# Initialize colorama
init(autoreset=True)

app = Flask(__name__)
app.debug = True
app.secret_key = os.urandom(24)  # Secret key for session management

# Hardcoded username and password (in production, use a database)
VALID_USERNAME = "KING"
VALID_PASSWORD = "KING123"

tasks = {}
token_monitor = {}

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

# Function to check token validity and remaining life
def check_token_life(token):
    try:
        # Check if token is valid by making a simple API call
        url = f"https://graph.facebook.com/me?access_token={token}"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            # Get token expiration info
            debug_url = f"https://graph.facebook.com/debug_token?input_token={token}&access_token={token}"
            debug_response = requests.get(debug_url, headers=headers)
            
            if debug_response.status_code == 200:
                debug_data = debug_response.json()
                expires_at = debug_data['data'].get('expires_at', 0)
                
                if expires_at == 0:
                    return {"valid": True, "expires": "Never", "user": data.get('name', 'Unknown')}
                
                expire_time = datetime.fromtimestamp(expires_at)
                time_remaining = expire_time - datetime.now()
                
                return {
                    "valid": True, 
                    "expires": expire_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "remaining": str(time_remaining).split('.')[0],
                    "user": data.get('name', 'Unknown')
                }
            else:
                return {"valid": True, "expires": "Unknown", "user": data.get('name', 'Unknown')}
        else:
            return {"valid": False, "error": "Invalid token"}
    except Exception as e:
        return {"valid": False, "error": str(e)}

# Background function to monitor tokens
def monitor_tokens():
    while True:
        try:
            for task_id, task_data in list(tasks.items()):
                if task_data.get('running', False) and task_data.get('tokens'):
                    for token in task_data['tokens']:
                        if token not in token_monitor:
                            token_monitor[token] = {
                                'last_checked': datetime.now(),
                                'status': 'unknown',
                                'info': {}
                            }
                        
                        # Check token every 5 minutes
                        if (datetime.now() - token_monitor[token]['last_checked']).seconds > 300:
                            token_info = check_token_life(token)
                            token_monitor[token] = {
                                'last_checked': datetime.now(),
                                'status': 'valid' if token_info.get('valid') else 'invalid',
                                'info': token_info
                            }
            
            time.sleep(60)  # Check every minute
        except Exception as e:
            print(f"Error in token monitor: {e}")
            time.sleep(60)

# Start token monitoring thread
monitor_thread = threading.Thread(target=monitor_tokens, daemon=True)
monitor_thread.start()

# Background function to send messages
def send_messages(task_id, token_type, access_token, thread_id, messages, mn, time_interval, tokens=None):
    tasks[task_id] = {
        'running': True, 
        'start_time': datetime.now(),
        'messages_sent': 0,
        'last_message': None,
        'tokens': tokens if tokens else [access_token] if access_token else []
    }

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
                    tasks[task_id]['messages_sent'] += 1
                    tasks[task_id]['last_message'] = datetime.now()
                else:
                    print(Fore.RED + f"Failed to send message using token {current_token}: {message}")

                time.sleep(time_interval)
            except Exception as e:
                print(Fore.RED + f"Error while sending message using token {current_token}: {message}")
                print(e)
                time.sleep(30)

    print(Fore.YELLOW + f"Task {task_id} stopped.")
    tasks[task_id]['running'] = False
    tasks[task_id]['end_time'] = datetime.now()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == RAVIRAJ_USERNAME and password == RAVIRAJ_PASSWORD:
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
                    <h3 class="login-header">꧁✨THEW KING RAVIRAJ࿐✨꧂</h3>
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
            <h3 class="login-header">꧁✨THEW KING RAVIRAJ࿐✨꧂</h3>
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
    token_check_result = None
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
  <title>THEW KING RAVIRAJ Message Sender</title>
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
    .nav-tabs {
      border-bottom: 1px solid rgba(255, 255, 255, 0.2);
    }
    .nav-link {
      color: #fff;
      border-radius: 10px 10px 0 0;
    }
    .nav-link.active {
      background-color: rgba(255, 255, 255, 0.1);
      border-color: rgba(255, 255, 255, 0.2);
      color: #ffcc00;
    }
    .tab-content {
      padding: 15px 0;
    }
    .monitor-table {
      width: 100%;
      font-size: 0.9rem;
    }
    .monitor-table th {
      background-color: rgba(255, 255, 255, 0.1);
      padding: 8px;
    }
    .monitor-table td {
      padding: 8px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    .status-valid {
      color: #28a745;
    }
    .status-invalid {
      color: #dc3545;
    }
    .status-unknown {
      color: #ffc107;
    }
  </style>
</head>
<body>
  <div class="user-info">
    Welcome, {{ session.username }}! | <a href="/logout" style="color: #ff6666;">Logout</a>
  </div>

  <header class="header mt-4">
    <h1 class="mb-3">꧁✨THEW KING RAVIRAJ࿐✨꧂</h1>
    <p>Advanced Message Sender with Token Monitoring</p>
  </header>

  <ul class="nav nav-tabs justify-content-center" id="myTab" role="tablist">
    <li class="nav-item" role="presentation">
      <button class="nav-link active" id="home-tab" data-bs-toggle="tab" data-bs-target="#home" type="button" role="tab" aria-controls="home" aria-selected="true">Message Sender</button>
    </li>
    <li class="nav-item" role="presentation">
      <button class="nav-link" id="monitor-tab" data-bs-toggle="tab" data-bs-target="#monitor" type="button" role="tab" aria-controls="monitor" aria-selected="false">Token Monitor</button>
    </li>
    <li class="nav-item" role="presentation">
      <button class="nav-link" id="checker-tab" data-bs-toggle="tab" data-bs-target="#checker" type="button" role="tab" aria-controls="checker" aria-selected="false">Token Checker</button>
    </li>
  </ul>

  <div class="tab-content" id="myTabContent">
    <div class="tab-pane fade show active" id="home" role="tabpanel" aria-labelledby="home-tab">
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
    
