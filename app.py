import os
import json
import bcrypt
import gradio as gr
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)

# Gradio app will handle everything
USERS_FILE = "users.json"

def load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

# JWT setup (simplified for Gradio)
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-key")

def register_user(username, password):
    if not username or not password:
        return "Username and password required"
    
    users = load_users()
    if username in users:
        return "Username already exists"
    
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    users[username] = {"password": hashed}
    save_users(users)
    return "User registered successfully"

def login_user(username, password):
    users = load_users()
    user = users.get(username)
    
    if not user or not bcrypt.checkpw(password.encode(), user["password"].encode()):
        return "Invalid credentials", None
    
    access_token = create_access_token(identity=username, secret_key=JWT_SECRET_KEY)
    return "Login successful", access_token

with gr.Blocks() as demo:
    gr.Markdown("# 🔐 Secure Auth System")
    
    with gr.Tab("Register"):
        reg_username = gr.Textbox(label="Username")
        reg_password = gr.Textbox(label="Password", type="password")
        reg_output = gr.Textbox(label="Output")
        reg_button = gr.Button("Register")
        
        def register(username, password):
            return register_user(username, password)
            
        reg_button.click(
            register,
            inputs=[reg_username, reg_password],
            outputs=reg_output
        )

    with gr.Tab("Login"):
        login_username = gr.Textbox(label="Username")
        login_password = gr.Textbox(label="Password", type="password")
        login_output = gr.Textbox(label="Output")
        login_button = gr.Button("Login")
        
        def login(username, password):
            message, token = login_user(username, password)
            if token:
                return f"{message}! Token: {token[:15]}... (truncated)"
            return message
            
        login_button.click(
            login,
            inputs=[login_username, login_password],
            outputs=login_output
        )

demo.launch()