import streamlit as st
from datetime import datetime, timedelta
import hashlib
import json
import random
import string
from pathlib import Path
from PIL import Image
import base64
from io import BytesIO
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
import os
import threading
import queue
import uuid

# WebRTC imports for real calls
try:
    from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
    import av
    WEBRTC_AVAILABLE = True
except ImportError:
    WEBRTC_AVAILABLE = False

# QR code import
try:
    import qrcode
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False

# ============ PAGE CONFIG ============
st.set_page_config(
    page_title="✨ School Community Hub ✨",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ ENHANCED CSS WITH BETTER TEXT VISIBILITY ============
st.markdown("""
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=yes">
<style>
    /* Global text visibility improvements */
    .main .block-container {
        background: rgba(0, 0, 0, 0.65) !important;
        backdrop-filter: blur(12px) !important;
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        border: 2px solid rgba(255, 215, 0, 0.4);
    }
    
    /* All text elements with enhanced contrast */
    .main p, .main span, .main div, .main li, .stMarkdown, .stText {
        color: #FFFFFF !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.9) !important;
        font-weight: 500 !important;
    }
    
    .main h1, .main h2, .main h3, .main h4, .main h5, .main h6 {
        color: #FFD700 !important;
        text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.95) !important;
        font-weight: 700 !important;
    }
    
    /* Card backgrounds */
    .golden-card, .class-card, .member-card, .chat-bubble, .profile-card {
        background: rgba(0, 0, 0, 0.7) !important;
        backdrop-filter: blur(12px) !important;
        border: 2px solid #FFD700 !important;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 10px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
    }
    
    .golden-card h1, .golden-card h2, .golden-card h3, .golden-card h4, .golden-card p {
        color: #FFFFFF !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.9) !important;
    }
    
    /* Input fields */
    .stTextInput input, .stTextArea textarea, .stSelectbox div, .stDateInput input {
        background: rgba(255, 255, 255, 0.98) !important;
        color: #000000 !important;
        border: 2px solid #FFD700 !important;
        border-radius: 8px;
        font-weight: 500 !important;
    }
    
    .stTextInput label, .stTextArea label, .stSelectbox label, .stDateInput label {
        color: #FFD700 !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.9) !important;
        font-weight: 600 !important;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(135deg, #1a1a1a, #2a2a2a) !important;
        border-right: 3px solid #FFD700 !important;
    }
    
    section[data-testid="stSidebar"] > div {
        background: rgba(0, 0, 0, 0.5) !important;
    }
    
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] .stRadio label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] div {
        color: #FFD700 !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.95) !important;
        font-weight: 600 !important;
    }
    
    /* Metrics */
    .stMetric label, .stMetric div {
        color: #FFFFFF !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.9) !important;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: #FFD700 !important;
        font-size: 2rem !important;
    }
    
    /* Tables */
    .dataframe {
        background: rgba(0, 0, 0, 0.7) !important;
        color: #FFFFFF !important;
        border: 2px solid #FFD700 !important;
    }
    
    .dataframe th {
        background: rgba(255, 215, 0, 0.3) !important;
        color: #FFD700 !important;
        font-weight: 700 !important;
    }
    
    .dataframe td {
        color: #FFFFFF !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(0, 0, 0, 0.5) !important;
        border-radius: 10px;
        padding: 5px;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #FFFFFF !important;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8) !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: rgba(255, 215, 0, 0.3) !important;
        color: #FFD700 !important;
    }
    
    /* Chat */
    .chat-container {
        background: rgba(0, 0, 0, 0.7);
        backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 20px;
        height: 400px;
        overflow-y: auto;
        border: 2px solid #FFD700;
    }
    
    .chat-bubble {
        background: rgba(0, 0, 0, 0.8) !important;
        border: 2px solid #FFD700;
        color: #FFFFFF !important;
        padding: 12px 16px;
        border-radius: 20px;
        max-width: 70%;
    }
    
    .chat-bubble-sent {
        background: rgba(255, 215, 0, 0.2) !important;
    }
    
    .chat-sender-name {
        color: #FFD700 !important;
        font-weight: 600;
    }
    
    .chat-time {
        color: rgba(255, 255, 255, 0.7) !important;
    }
    
    /* Call interface */
    .call-container {
        background: rgba(0, 0, 0, 0.8);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        padding: 20px;
        border: 3px solid #FFD700;
        box-shadow: 0 0 30px rgba(255, 215, 0, 0.3);
    }
    
    .participant-video {
        border: 3px solid #FFD700;
        border-radius: 15px;
        overflow: hidden;
        background: rgba(0, 0, 0, 0.5);
    }
    
    .call-controls {
        background: rgba(0, 0, 0, 0.7);
        backdrop-filter: blur(10px);
        border-radius: 50px;
        padding: 15px;
        border: 2px solid #FFD700;
        margin-top: 20px;
    }
    
    .incoming-call-card {
        background: rgba(0, 0, 0, 0.9);
        border: 3px solid #FFD700;
        border-radius: 15px;
        padding: 30px;
        text-align: center;
        animation: pulse 1.5s infinite;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(255, 215, 0, 0.7); }
        70% { box-shadow: 0 0 0 20px rgba(255, 215, 0, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 215, 0, 0); }
    }
    
    .ringing-icon {
        font-size: 4rem;
        animation: ring 1s infinite;
    }
    
    @keyframes ring {
        0% { transform: rotate(0deg); }
        10% { transform: rotate(15deg); }
        20% { transform: rotate(-15deg); }
        30% { transform: rotate(10deg); }
        40% { transform: rotate(-10deg); }
        50% { transform: rotate(5deg); }
        60% { transform: rotate(-5deg); }
        70% { transform: rotate(2deg); }
        80% { transform: rotate(-2deg); }
        90% { transform: rotate(1deg); }
        100% { transform: rotate(0deg); }
    }
    
    /* Performance badges */
    .performance-excellent {
        background: linear-gradient(135deg, #00ff00, #00cc00);
        color: #000000 !important;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: 700;
        border: 2px solid #FFD700;
    }
    
    .performance-good {
        background: linear-gradient(135deg, #00ffff, #0099ff);
        color: #000000 !important;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: 700;
        border: 2px solid #FFD700;
    }
    
    .performance-average {
        background: linear-gradient(135deg, #ffff00, #ffcc00);
        color: #000000 !important;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: 700;
        border: 2px solid #FFD700;
    }
    
    .performance-needs-improvement {
        background: linear-gradient(135deg, #ff4444, #ff0000);
        color: #FFFFFF !important;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: 700;
        border: 2px solid #FFD700;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .main .block-container { padding: 0.8rem !important; }
        h1 { font-size: 1.8rem !important; }
        h2 { font-size: 1.3rem !important; }
    }
</style>
""", unsafe_allow_html=True)

# ============ KENYAN CURRICULUM DATA ============
PRIMARY_SUBJECTS = [
    "Mathematics", "English", "Kiswahili", "Science and Technology",
    "Social Studies", "CRE / IRE / HRE", "Agriculture", "Home Science",
    "Art and Craft", "Music", "Physical Education"
]

JUNIOR_SECONDARY_SUBJECTS = [
    "Mathematics", "English", "Kiswahili", "Integrated Science",
    "Social Studies", "CRE / IRE / HRE", "Business Studies",
    "Agriculture", "Home Science", "Computer Science",
    "Pre-Technical Studies", "Visual Arts", "Performing Arts",
    "Physical Education"
]

SENIOR_SECONDARY_SUBJECTS = {
    "Mathematics": ["Mathematics"],
    "English": ["English"],
    "Kiswahili": ["Kiswahili"],
    "Sciences": ["Biology", "Chemistry", "Physics", "General Science"],
    "Humanities": ["History", "Geography", "CRE", "IRE", "HRE"],
    "Technical": ["Computer Studies", "Business Studies", "Agriculture", "Home Science"],
    "Languages": ["French", "German", "Arabic", "Sign Language"]
}

KENYAN_GRADES = [
    "Grade 1 (7 subjects)", "Grade 2 (7 subjects)", "Grade 3 (7 subjects)",
    "Grade 4 (7 subjects)", "Grade 5 (7 subjects)", "Grade 6 (7 subjects)",
    "Grade 7 (12 subjects)", "Grade 8 (12 subjects)", "Grade 9 (12 subjects)",
    "Form 1 (11 subjects)", "Form 2 (11 subjects)", "Form 3 (11 subjects)", "Form 4 (11 subjects)"
]

# ============ THEMES ============
THEMES = {
    "Sunrise Glow": {
        "primary": "#ff6b6b",
        "secondary": "#feca57",
        "accent": "#48dbfb",
        "background": "linear-gradient(135deg, #ff6b6b, #feca57, #ff9ff3, #48dbfb)",
        "text": "#ffffff",
        "sidebar": "linear-gradient(135deg, #cfa668, #e5b873, #f5d742)"
    },
    "Ocean Breeze": {
        "primary": "#00d2ff",
        "secondary": "#3a1c71",
        "accent": "#00ff00",
        "background": "linear-gradient(135deg, #00d2ff, #3a1c71, #d76d77, #ffaf7b)",
        "text": "#ffffff",
        "sidebar": "linear-gradient(135deg, #4facfe, #00f2fe, #43e97b)"
    },
    "Purple Haze": {
        "primary": "#8E2DE2",
        "secondary": "#4A00E0",
        "accent": "#a044ff",
        "background": "linear-gradient(135deg, #8E2DE2, #4A00E0, #6a3093, #a044ff)",
        "text": "#ffffff",
        "sidebar": "linear-gradient(135deg, #c471ed, #f64f59, #c471ed)"
    }
}

WALLPAPERS = {
    "None": "",
    "Abstract Waves": "https://images.unsplash.com/photo-1557682250-33bd709cbe85",
    "Geometric Pattern": "https://images.unsplash.com/photo-1557683311-eac922347aa1",
    "Nature Leaves": "https://images.unsplash.com/photo-1557683316-973673baf926",
    "Starry Night": "https://images.unsplash.com/photo-1557683320-2d5001d5e9c5",
    "Mountains": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b",
    "Ocean": "https://images.unsplash.com/photo-1507525425510-56b1e2d6c4f2"
}

# ============ STUN/TURN SERVERS FOR WEBRTC ============
RTC_CONFIGURATION = RTCConfiguration(
    {
        "iceServers": [
            {"urls": ["stun:stun.l.google.com:19302"]},
            {"urls": ["stun:stun1.l.google.com:19302"]},
            {"urls": ["stun:stun2.l.google.com:19302"]},
            {"urls": ["stun:stun3.l.google.com:19302"]},
            {"urls": ["stun:stun4.l.google.com:19302"]},
        ]
    }
)

# ============ CODE GENERATOR FUNCTIONS ============
def generate_id(prefix, length=8):
    chars = string.ascii_uppercase + string.digits
    random_part = ''.join(random.choices(chars, k=length))
    return f"{prefix}{random_part}"

def generate_school_code():
    chars = string.ascii_uppercase + string.digits
    return 'SCH' + ''.join(random.choices(chars, k=6))

def generate_class_code():
    return 'CLS' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def generate_group_code():
    return 'GRP' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def generate_admission_number():
    year = datetime.now().strftime("%y")
    random_num = ''.join(random.choices(string.digits, k=4))
    return f"ADM/{year}/{random_num}"

def generate_teacher_code():
    dept = random.choice(['MATH', 'ENG', 'SCI', 'SOC', 'CRE', 'BUS', 'TECH'])
    num = ''.join(random.choices(string.digits, k=3))
    return f"{dept}{num}"

def generate_book_id():
    return 'BOK' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def generate_transaction_id():
    return 'TRN' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def generate_call_id():
    return 'CAL' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def generate_notification_id():
    return 'NOT' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# ============ DATA STORAGE ============
DATA_DIR = Path("school_data")
DATA_DIR.mkdir(exist_ok=True)

SCHOOLS_FILE = DATA_DIR / "all_schools.json"

def load_all_schools():
    if SCHOOLS_FILE.exists():
        with open(SCHOOLS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_all_schools(schools):
    with open(SCHOOLS_FILE, 'w') as f:
        json.dump(schools, f, indent=2)

def load_school_data(school_code, filename, default):
    if not school_code:
        return default
    filepath = DATA_DIR / f"{school_code}_{filename}"
    if filepath.exists():
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except:
            return default
    return default

def save_school_data(school_code, filename, data):
    if school_code:
        with open(DATA_DIR / f"{school_code}_{filename}", 'w') as f:
            json.dump(data, f, indent=2)

def load_user_settings(school_code, user_email):
    settings = load_school_data(school_code, "user_settings.json", {})
    return settings.get(user_email, {"theme": "Sunrise Glow", "wallpaper": "None"})

def save_user_settings(school_code, user_email, settings):
    all_settings = load_school_data(school_code, "user_settings.json", {})
    all_settings[user_email] = settings
    save_school_data(school_code, "user_settings.json", all_settings)

# ============ NOTIFICATION SYSTEM ============
def create_notification(school_code, user_email, notification_type, title, message, data=None):
    notifications = load_school_data(school_code, "notifications.json", [])
    notification = {
        "id": generate_notification_id(),
        "user_email": user_email,
        "type": notification_type,
        "title": title,
        "message": message,
        "data": data or {},
        "read": False,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "expires_at": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    }
    notifications.append(notification)
    save_school_data(school_code, "notifications.json", notifications)
    return notification

def mark_notification_read(school_code, notification_id):
    notifications = load_school_data(school_code, "notifications.json", [])
    for n in notifications:
        if n['id'] == notification_id:
            n['read'] = True
            break
    save_school_data(school_code, "notifications.json", notifications)

def get_unread_notifications_count(school_code, user_email):
    notifications = load_school_data(school_code, "notifications.json", [])
    return len([n for n in notifications if n['user_email'] == user_email and not n['read']])

# ============ CALL SYSTEM WITH WEBRTC ============
class CallManager:
    def __init__(self):
        self.active_calls = {}
        
    def create_call(self, call_id, caller, participants, call_type):
        self.active_calls[call_id] = {
            'id': call_id,
            'caller': caller,
            'participants': participants,
            'call_type': call_type,
            'start_time': datetime.now(),
            'active': True,
            'joined': [caller]
        }
        return call_id
    
    def join_call(self, call_id, participant):
        if call_id in self.active_calls:
            if participant not in self.active_calls[call_id]['joined']:
                self.active_calls[call_id]['joined'].append(participant)
            return True
        return False
    
    def leave_call(self, call_id, participant):
        if call_id in self.active_calls:
            if participant in self.active_calls[call_id]['joined']:
                self.active_calls[call_id]['joined'].remove(participant)
            if len(self.active_calls[call_id]['joined']) == 0:
                self.end_call(call_id)
            return True
        return False
    
    def end_call(self, call_id):
        if call_id in self.active_calls:
            self.active_calls[call_id]['active'] = False
            return True
        return False
    
    def get_call(self, call_id):
        return self.active_calls.get(call_id)

call_manager = CallManager()

def initiate_webrtc_call(school_code, caller_email, recipients, call_type):
    call_id = generate_call_id()
    call_manager.create_call(call_id, caller_email, recipients, call_type)
    
    calls = load_school_data(school_code, "calls.json", [])
    call = {
        "id": call_id,
        "caller": caller_email,
        "recipients": recipients,
        "call_type": call_type,
        "status": "ringing",
        "started_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "active": True,
        "answered_by": []
    }
    calls.append(call)
    save_school_data(school_code, "calls.json", calls)
    
    users = load_school_data(school_code, "users.json", [])
    caller = next((u for u in users if u['email'] == caller_email), None)
    caller_name = caller['fullname'] if caller else caller_email
    
    call_icon = "📹" if call_type == "video" else "🎧"
    
    for recipient in recipients:
        create_notification(
            school_code,
            recipient,
            "incoming_call",
            f"{call_icon} Incoming {call_type.title()} Call",
            f"{caller_name} is calling you",
            {"call_id": call_id, "caller": caller_email, "call_type": call_type}
        )
    
    return call

def answer_webrtc_call(school_code, call_id, user_email):
    calls = load_school_data(school_code, "calls.json", [])
    
    for call in calls:
        if call['id'] == call_id and call['status'] == 'ringing':
            call['status'] = 'active'
            if user_email not in call['answered_by']:
                call['answered_by'].append(user_email)
            
            call_manager.join_call(call_id, user_email)
            save_school_data(school_code, "calls.json", calls)
            
            create_notification(
                school_code,
                call['caller'],
                "call_answered",
                "📞 Call Answered",
                f"{user_email} answered your call",
                {"call_id": call_id}
            )
            return True
    return False

def end_webrtc_call(school_code, call_id, user_email):
    calls = load_school_data(school_code, "calls.json", [])
    
    for call in calls:
        if call['id'] == call_id and call['status'] in ['ringing', 'active']:
            call['status'] = 'ended'
            call['ended_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            call_manager.leave_call(call_id, user_email)
            save_school_data(school_code, "calls.json", calls)
            
            all_participants = [call['caller']] + call['recipients']
            for participant in all_participants:
                if participant != user_email:
                    create_notification(
                        school_code,
                        participant,
                        "call_ended",
                        "📞 Call Ended",
                        f"Call ended by {user_email}",
                        {"call_id": call_id}
                    )
            return True
    return False

def get_active_webrtc_calls(school_code, user_email):
    calls = load_school_data(school_code, "calls.json", [])
    active_calls = []
    
    for call in calls:
        if call['status'] in ['ringing', 'active']:
            if user_email == call['caller'] or user_email in call['recipients']:
                manager_call = call_manager.get_call(call['id'])
                if manager_call:
                    call['active_participants'] = manager_call['joined']
                active_calls.append(call)
    
    return active_calls

# ============ CHAT & FRIENDSHIP FUNCTIONS ============
def send_friend_request(school_code, from_email, to_email):
    requests = load_school_data(school_code, "friend_requests.json", [])
    if not any(r['from'] == from_email and r['to'] == to_email and r['status'] == 'pending' for r in requests):
        request_id = generate_id("REQ")
        requests.append({
            "id": request_id,
            "from": from_email,
            "to": to_email,
            "status": "pending",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        save_school_data(school_code, "friend_requests.json", requests)
        
        users = load_school_data(school_code, "users.json", [])
        from_user = next((u for u in users if u['email'] == from_email), None)
        from_name = from_user['fullname'] if from_user else from_email
        
        create_notification(
            school_code,
            to_email,
            "friend_request",
            "🤝 New Friend Request",
            f"{from_name} sent you a friend request",
            {"request_id": request_id, "from": from_email}
        )
        return True
    return False

def accept_friend_request(school_code, request_id):
    requests = load_school_data(school_code, "friend_requests.json", [])
    friendships = load_school_data(school_code, "friendships.json", [])
    
    for req in requests:
        if req['id'] == request_id:
            req['status'] = 'accepted'
            friendships.append({
                "user1": min(req['from'], req['to']),
                "user2": max(req['from'], req['to']),
                "since": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            
            create_notification(
                school_code,
                req['from'],
                "friend_accepted",
                "✅ Friend Request Accepted",
                f"{req['to']} accepted your friend request",
                {"friend": req['to']}
            )
            break
    
    save_school_data(school_code, "friend_requests.json", requests)
    save_school_data(school_code, "friendships.json", friendships)

def decline_friend_request(school_code, request_id):
    requests = load_school_data(school_code, "friend_requests.json", [])
    for req in requests:
        if req['id'] == request_id:
            req['status'] = 'declined'
            break
    save_school_data(school_code, "friend_requests.json", requests)

def get_friends(school_code, user_email):
    friendships = load_school_data(school_code, "friendships.json", [])
    friends = []
    for f in friendships:
        if f['user1'] == user_email:
            friends.append(f['user2'])
        elif f['user2'] == user_email:
            friends.append(f['user1'])
    return friends

def get_pending_requests(school_code, user_email):
    requests = load_school_data(school_code, "friend_requests.json", [])
    return [r for r in requests if r['to'] == user_email and r['status'] == 'pending']

def send_message(school_code, sender_email, recipient_email, message, attachment=None):
    messages = load_school_data(school_code, "messages.json", [])
    message_id = generate_id("MSG")
    messages.append({
        "id": message_id,
        "sender": sender_email,
        "recipient": recipient_email,
        "message": message,
        "attachment": attachment,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "read": False,
        "deleted": False,
        "deleted_by": [],
        "conversation_id": f"{min(sender_email, recipient_email)}_{max(sender_email, recipient_email)}"
    })
    save_school_data(school_code, "messages.json", messages)
    
    users = load_school_data(school_code, "users.json", [])
    sender = next((u for u in users if u['email'] == sender_email), None)
    sender_name = sender['fullname'] if sender else sender_email
    
    create_notification(
        school_code,
        recipient_email,
        "new_message",
        "💬 New Message",
        f"{sender_name}: {message[:50]}..." if len(message) > 50 else message,
        {"message_id": message_id, "sender": sender_email}
    )
    
    return message_id

def get_conversation_messages(school_code, user_email, other_email):
    messages = load_school_data(school_code, "messages.json", [])
    conv_id = f"{min(user_email, other_email)}_{max(user_email, other_email)}"
    conv_msgs = [m for m in messages if m['conversation_id'] == conv_id and not m.get('deleted', False)]
    
    filtered_msgs = []
    for msg in conv_msgs:
        if user_email not in msg.get('deleted_by', []):
            filtered_msgs.append(msg)
    
    return sorted(filtered_msgs, key=lambda x: x['timestamp'])

def get_unread_count(user_email, school_code):
    messages = load_school_data(school_code, "messages.json", [])
    return len([m for m in messages if m['recipient'] == user_email and not m.get('read', False) and not m.get('deleted', False)])

# ============ GROUP CHAT FUNCTIONS ============
def create_group_chat(school_code, group_name, created_by, members):
    group_chats = load_school_data(school_code, "group_chats.json", [])
    group_chat = {
        "id": generate_id("GPC"),
        "name": group_name,
        "created_by": created_by,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "members": members,
        "messages": [],
        "admins": [created_by]
    }
    group_chats.append(group_chat)
    save_school_data(school_code, "group_chats.json", group_chats)
    
    users = load_school_data(school_code, "users.json", [])
    creator = next((u for u in users if u['email'] == created_by), None)
    creator_name = creator['fullname'] if creator else created_by
    
    for member in members:
        if member != created_by:
            create_notification(
                school_code,
                member,
                "group_created",
                "👥 Added to Group",
                f"{creator_name} added you to '{group_name}'",
                {"group_id": group_chat['id']}
            )
    
    return group_chat['id']

def send_group_message(school_code, group_id, sender_email, message, attachment=None):
    group_chats = load_school_data(school_code, "group_chats.json", [])
    message_id = generate_id("GPM")
    
    for group in group_chats:
        if group['id'] == group_id:
            group['messages'].append({
                "id": message_id,
                "sender": sender_email,
                "message": message,
                "attachment": attachment,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "read_by": [sender_email],
                "deleted": False
            })
            
            users = load_school_data(school_code, "users.json", [])
            sender = next((u for u in users if u['email'] == sender_email), None)
            sender_name = sender['fullname'] if sender else sender_email
            
            for member in group['members']:
                if member != sender_email:
                    create_notification(
                        school_code,
                        member,
                        "group_message",
                        f"👥 {group['name']}",
                        f"{sender_name}: {message[:50]}..." if len(message) > 50 else message,
                        {"group_id": group_id, "message_id": message_id}
                    )
            break
    
    save_school_data(school_code, "group_chats.json", group_chats)

def get_user_groups(school_code, user_email):
    groups = load_school_data(school_code, "groups.json", [])
    group_chats = load_school_data(school_code, "group_chats.json", [])
    user_groups = []
    
    for group in groups:
        if user_email in group.get('members', []):
            user_groups.append({
                "id": group['code'],
                "name": group['name'],
                "type": "regular",
                "members": group.get('members', [])
            })
    
    for chat in group_chats:
        if user_email in chat.get('members', []):
            user_groups.append({
                "id": chat['id'],
                "name": chat['name'],
                "type": "chat",
                "members": chat.get('members', [])
            })
    
    return user_groups

# ============ ATTACHMENT FUNCTIONS ============
def save_attachment(uploaded_file):
    if uploaded_file:
        bytes_data = uploaded_file.getvalue()
        b64 = base64.b64encode(bytes_data).decode()
        return {
            "name": uploaded_file.name,
            "type": uploaded_file.type,
            "data": b64,
            "size": len(bytes_data)
        }
    return None

def display_attachment(attachment):
    if attachment:
        file_ext = attachment['name'].split('.')[-1].lower()
        if file_ext in ['jpg', 'jpeg', 'png', 'gif']:
            st.image(f"data:{attachment['type']};base64,{attachment['data']}", width=200)
        else:
            st.markdown(f"📎 [{attachment['name']}](data:{attachment['type']};base64,{attachment['data']})")

# ============ ACADEMIC FUNCTIONS ============
def calculate_student_performance(grades, student_email):
    student_grades = [g for g in grades if g['student_email'] == student_email]
    if not student_grades:
        return {"average": 0, "subjects": {}, "rank": "N/A", "subject_details": []}
    
    subjects = {}
    subject_details = []
    total = 0
    for grade in student_grades:
        subjects[grade['subject']] = grade['score']
        subject_details.append({
            "subject": grade['subject'],
            "score": grade['score'],
            "term": grade['term'],
            "year": grade['year']
        })
        total += grade['score']
    
    avg = total / len(student_grades)
    
    if avg >= 80:
        rank = "Excellent"
    elif avg >= 70:
        rank = "Good"
    elif avg >= 50:
        rank = "Average"
    else:
        rank = "Needs Improvement"
    
    return {"average": round(avg, 2), "subjects": subjects, "rank": rank, "subject_details": subject_details}

def add_academic_record(school_code, student_email, subject, score, term, year, teacher_email, class_name=None):
    grades = load_school_data(school_code, "academic_records.json", [])
    grades.append({
        "id": generate_id("GRD"),
        "student_email": student_email,
        "subject": subject,
        "score": score,
        "term": term,
        "year": year,
        "teacher_email": teacher_email,
        "class_name": class_name,
        "date": datetime.now().strftime("%Y-%m-%d")
    })
    save_school_data(school_code, "academic_records.json", grades)

# ============ LIBRARY FUNCTIONS ============
def add_book(school_code, title, author, book_type, quantity, isbn=None, publisher=None, year=None):
    books = load_school_data(school_code, "library_books.json", [])
    book = {
        "id": generate_book_id(),
        "title": title,
        "author": author,
        "type": book_type,
        "quantity": quantity,
        "available": quantity,
        "isbn": isbn,
        "publisher": publisher,
        "year": year,
        "added_by": st.session_state.user['email'],
        "added_date": datetime.now().strftime("%Y-%m-%d")
    }
    books.append(book)
    save_school_data(school_code, "library_books.json", books)
    return book['id']

def add_library_member(school_code, user_email, member_type="student"):
    members = load_school_data(school_code, "library_members.json", [])
    if not any(m['email'] == user_email for m in members):
        members.append({
            "email": user_email,
            "member_type": member_type,
            "joined_date": datetime.now().strftime("%Y-%m-%d"),
            "borrowed_books": [],
            "status": "active"
        })
        save_school_data(school_code, "library_members.json", members)

def borrow_book(school_code, user_email, book_id, due_days=14):
    books = load_school_data(school_code, "library_books.json", [])
    transactions = load_school_data(school_code, "library_transactions.json", [])
    members = load_school_data(school_code, "library_members.json", [])
    
    book = next((b for b in books if b['id'] == book_id), None)
    if not book or book['available'] <= 0:
        return False, "Book not available"
    
    member = next((m for m in members if m['email'] == user_email), None)
    if not member:
        add_library_member(school_code, user_email)
        members = load_school_data(school_code, "library_members.json", [])
        member = next((m for m in members if m['email'] == user_email), None)
    
    borrow_date = datetime.now()
    due_date = borrow_date + timedelta(days=due_days)
    
    transaction = {
        "id": generate_transaction_id(),
        "book_id": book_id,
        "book_title": book['title'],
        "user_email": user_email,
        "borrow_date": borrow_date.strftime("%Y-%m-%d"),
        "due_date": due_date.strftime("%Y-%m-%d"),
        "return_date": None,
        "status": "borrowed",
        "renewals": 0
    }
    transactions.append(transaction)
    
    book['available'] -= 1
    
    member.setdefault('borrowed_books', []).append({
        "book_id": book_id,
        "transaction_id": transaction['id'],
        "borrow_date": borrow_date.strftime("%Y-%m-%d"),
        "due_date": due_date.strftime("%Y-%m-%d"),
        "status": "borrowed"
    })
    
    save_school_data(school_code, "library_books.json", books)
    save_school_data(school_code, "library_transactions.json", transactions)
    save_school_data(school_code, "library_members.json", members)
    
    return True, "Book borrowed successfully"

def return_book(school_code, transaction_id):
    books = load_school_data(school_code, "library_books.json", [])
    transactions = load_school_data(school_code, "library_transactions.json", [])
    members = load_school_data(school_code, "library_members.json", [])
    
    transaction = next((t for t in transactions if t['id'] == transaction_id), None)
    if not transaction or transaction['status'] != 'borrowed':
        return False, "Invalid transaction"
    
    transaction['return_date'] = datetime.now().strftime("%Y-%m-%d")
    transaction['status'] = 'returned'
    
    book = next((b for b in books if b['id'] == transaction['book_id']), None)
    if book:
        book['available'] += 1
    
    member = next((m for m in members if m['email'] == transaction['user_email']), None)
    if member:
        for b in member.get('borrowed_books', []):
            if b['transaction_id'] == transaction_id:
                b['status'] = 'returned'
                b['return_date'] = transaction['return_date']
                break
    
    save_school_data(school_code, "library_books.json", books)
    save_school_data(school_code, "library_transactions.json", transactions)
    save_school_data(school_code, "library_members.json", members)
    
    return True, "Book returned successfully"

# ============ TRANSLATIONS ============
TRANSLATIONS = {
    "en": {
        "welcome": "✨ School Community Hub ✨",
        "connect": "Connect • Collaborate • Manage • Shine",
        "dashboard": "Dashboard",
        "announcements": "Announcements",
        "chat": "Chat",
        "friends": "Friends",
        "profile": "Profile",
        "logout": "Logout"
    },
    "sw": {
        "welcome": "✨ Kituo cha Jumuiya ya Shule ✨",
        "connect": "Unganisha • Shirikiana • Simamia • Angaza",
        "dashboard": "Dashbodi",
        "announcements": "Matangazo",
        "chat": "Mazungumzo",
        "friends": "Marafiki",
        "profile": "Wasifu",
        "logout": "Toka"
    }
}

def get_text(key: str, **kwargs) -> str:
    if 'language' not in st.session_state:
        st.session_state.language = 'en'
    lang = st.session_state.language
    text = TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)
    if kwargs:
        text = text.format(**kwargs)
    return text

# ============ ACCESSIBILITY ============
ACCESSIBILITY_PRESETS = {
    "Default": {
        "text_size": "Medium",
        "contrast_mode": False,
        "dyslexia_font": False,
        "color_blind_mode": "None",
        "reduced_motion": False
    },
    "Large Text": {
        "text_size": "Large",
        "contrast_mode": False,
        "dyslexia_font": False,
        "color_blind_mode": "None",
        "reduced_motion": False
    },
    "High Contrast": {
        "text_size": "Medium",
        "contrast_mode": True,
        "dyslexia_font": False,
        "color_blind_mode": "None",
        "reduced_motion": False
    }
}

COLOR_BLIND_FILTERS = {
    "None": "",
    "Protanopia": "protanopia",
    "Deuteranopia": "deuteranopia",
    "Tritanopia": "tritanopia"
}

# ============ RENDER FUNCTIONS ============

def render_webrtc_video_call(call_id, user_email, call_type):
    """Render actual WebRTC video/audio call"""
    if not WEBRTC_AVAILABLE:
        st.error("WebRTC is not available. Please install: pip install streamlit-webrtc av")
        return False
    
    call = call_manager.get_call(call_id)
    if not call:
        st.error("Call not found")
        return False
    
    st.markdown(f"""
    <div class="call-container">
        <h3 style="color: #FFD700; text-align: center; margin-bottom: 20px;">
            {'📹 Video Call' if call_type == 'video' else '🎧 Audio Call'}
        </h3>
    """, unsafe_allow_html=True)
    
    if call_type == 'video':
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="participant-video">', unsafe_allow_html=True)
            st.markdown('<p style="color: #FFD700; text-align: center; margin: 5px;">You</p>', unsafe_allow_html=True)
            
            webrtc_streamer(
                key=f"call_{call_id}_self",
                mode=WebRtcMode.SENDRECV,
                rtc_configuration=RTC_CONFIGURATION,
                media_stream_constraints={"video": True, "audio": True},
                video_html_attrs={
                    "style": {"width": "100%", "height": "300px", "border-radius": "10px"},
                    "class": "participant-video"
                }
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="participant-video">', unsafe_allow_html=True)
            st.markdown('<p style="color: #FFD700; text-align: center; margin: 5px;">Remote</p>', unsafe_allow_html=True)
            
            webrtc_streamer(
                key=f"call_{call_id}_remote",
                mode=WebRtcMode.RECVONLY,
                rtc_configuration=RTC_CONFIGURATION,
                media_stream_constraints={"video": True, "audio": True},
                video_html_attrs={
                    "style": {"width": "100%", "height": "300px", "border-radius": "10px"},
                    "class": "participant-video"
                }
            )
            st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        st.markdown("""
        <div style="text-align: center; padding: 40px; background: rgba(0,0,0,0.5); border-radius: 15px; margin: 20px 0;">
            <h1 style="font-size: 5rem;">🎧</h1>
            <h3 style="color: #FFD700;">Audio Call in Progress</h3>
        </div>
        """, unsafe_allow_html=True)
        
        webrtc_streamer(
            key=f"call_{call_id}_audio",
            mode=WebRtcMode.SENDRECV,
            rtc_configuration=RTC_CONFIGURATION,
            media_stream_constraints={"video": False, "audio": True},
        )
    
    st.markdown("""
    <div style="margin: 20px 0; padding: 15px; background: rgba(0,0,0,0.5); border-radius: 10px; border: 1px solid #FFD700;">
        <h4 style="color: #FFD700;">Participants</h4>
    """, unsafe_allow_html=True)
    
    all_participants = [call['caller']] + call['participants']
    for participant in all_participants:
        status = "🟢 Connected" if participant in call.get('joined', []) else "🔴 Not connected"
        st.markdown(f"<p><span style='color: #FFD700;'>{'📞' if participant == call['caller'] else '👤'}</span> {participant} - {status}</p>", unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="call-controls">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔇 Mute", use_container_width=True):
            st.info("Use your device's microphone controls")
    
    with col2:
        if st.button("🎤 Unmute", use_container_width=True):
            st.info("Use your device's microphone controls")
    
    with col3:
        if st.button("📹 Toggle Camera", use_container_width=True) and call_type == 'video':
            st.info("Use your device's camera controls")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚫 End Call", use_container_width=True, type="primary"):
            return False
    
    st.markdown('</div>', unsafe_allow_html=True)
    return True

def render_incoming_call_alert(call, school_code):
    """Render incoming call alert"""
    call_icon = "📹" if call['call_type'] == 'video' else "🎧"
    
    st.markdown(f"""
    <div class="incoming-call-card">
        <div class="ringing-icon">{call_icon}</div>
        <h2 style="color: #FFD700; margin: 20px 0;">Incoming {call['call_type'].title()} Call</h2>
        <p style="font-size: 1.2rem; color: #FFFFFF;">From: {call['caller']}</p>
        <p style="color: #FFD700;">🔔 Ringing...</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("✅ Answer", key=f"answer_{call['id']}", use_container_width=True):
            if answer_webrtc_call(school_code, call['id'], st.session_state.user['email']):
                st.session_state.current_call = call
                st.rerun()
    
    with col2:
        if st.button("❌ Decline", key=f"decline_{call['id']}", use_container_width=True):
            end_webrtc_call(school_code, call['id'], st.session_state.user['email'])
            st.rerun()
    
    with col3:
        if st.button("🔇 Silence", key=f"silence_{call['id']}", use_container_width=True):
            st.info("Call silenced")
    
    return True

def render_video_meeting():
    """Video meeting interface"""
    st.markdown("### 🎥 Video/Audio Calls")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📞 Make a Call", "📋 Active Calls", "📅 Scheduled", "🔔 Incoming"])
    
    with tab1:
        st.markdown("#### Start a Call")
        
        if st.session_state.user and st.session_state.current_school:
            users = load_school_data(st.session_state.current_school['code'], "users.json", [])
            all_users = [u for u in users if u['email'] != st.session_state.user['email']]
            
            col1, col2 = st.columns(2)
            
            with col1:
                call_type = st.radio("Call Type", ["🎧 Audio Call", "📹 Video Call"])
                actual_call_type = "audio" if "Audio" in call_type else "video"
            
            with col2:
                call_target = st.radio("Call Target", ["Individual", "Group"])
            
            recipients = []
            
            if call_target == "Individual":
                selected_users = st.multiselect(
                    "Select recipients",
                    [f"{u['fullname']} ({u['role']})" for u in all_users],
                    max_selections=1
                )
                recipients = [u.split('(')[1].rstrip(')').strip() for u in selected_users]
            
            else:
                groups = load_school_data(st.session_state.current_school['code'], "groups.json", [])
                user_groups = [g for g in groups if st.session_state.user['email'] in g.get('members', [])]
                
                if user_groups:
                    selected_group = st.selectbox("Select Group", [g['name'] for g in user_groups])
                    group = next((g for g in user_groups if g['name'] == selected_group), None)
                    if group:
                        recipients = [m for m in group.get('members', []) if m != st.session_state.user['email']]
                        st.info(f"Calling {len(recipients)} group members")
                else:
                    st.warning("You're not in any groups")
            
            if st.button("🚀 Start Call", use_container_width=True, type="primary"):
                if recipients:
                    if WEBRTC_AVAILABLE:
                        call = initiate_webrtc_call(
                            st.session_state.current_school['code'],
                            st.session_state.user['email'],
                            recipients,
                            actual_call_type
                        )
                        st.success(f"Call initiated! Ringing {len(recipients)} participant(s)...")
                        st.session_state.current_call = call
                        st.rerun()
                    else:
                        st.error("WebRTC not available. Install: pip install streamlit-webrtc av")
                else:
                    st.error("Please select at least one recipient")
    
    with tab2:
        st.markdown("#### Active Calls")
        
        if st.session_state.user and st.session_state.current_school:
            active_calls = get_active_webrtc_calls(
                st.session_state.current_school['code'],
                st.session_state.user['email']
            )
            
            if active_calls:
                for call in active_calls:
                    with st.container():
                        call_icon = "🎧" if call['call_type'] == 'audio' else "📹"
                        
                        col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                        
                        with col1:
                            status_emoji = "🔔" if call['status'] == 'ringing' else "🟢"
                            st.markdown(f"**{status_emoji} {call_icon} Call**")
                        
                        with col2:
                            started = datetime.strptime(call['started_at'], "%Y-%m-%d %H:%M:%S")
                            duration = datetime.now() - started
                            minutes = int(duration.total_seconds() / 60)
                            st.markdown(f"Duration: {minutes} min")
                        
                        with col3:
                            if st.button("Join", key=f"join_{call['id']}", use_container_width=True):
                                if call['status'] == 'ringing':
                                    answer_webrtc_call(
                                        st.session_state.current_school['code'],
                                        call['id'],
                                        st.session_state.user['email']
                                    )
                                st.session_state.current_call = call
                                st.rerun()
                        
                        with col4:
                            if st.button("End", key=f"end_{call['id']}", use_container_width=True):
                                end_webrtc_call(
                                    st.session_state.current_school['code'],
                                    call['id'],
                                    st.session_state.user['email']
                                )
                                st.rerun()
                        
                        st.divider()
            else:
                st.info("No active calls")
    
    with tab3:
        st.markdown("#### Scheduled Meetings")
        st.info("Schedule a meeting feature coming soon!")
    
    with tab4:
        st.markdown("#### Incoming Calls")
        
        if st.session_state.user and st.session_state.current_school:
            incoming_calls = get_active_webrtc_calls(
                st.session_state.current_school['code'],
                st.session_state.user['email']
            )
            incoming_calls = [c for c in incoming_calls if c['status'] == 'ringing' and 
                            st.session_state.user['email'] in c['recipients']]
            
            if incoming_calls:
                for call in incoming_calls:
                    render_incoming_call_alert(call, st.session_state.current_school['code'])
            else:
                st.info("No incoming calls")

def render_call_room():
    """Render call room"""
    if 'current_call' not in st.session_state:
        return
    
    call = st.session_state.current_call
    
    if WEBRTC_AVAILABLE:
        if render_webrtc_video_call(call['id'], st.session_state.user['email'], call['call_type']):
            end_webrtc_call(
                st.session_state.current_school['code'],
                call['id'],
                st.session_state.user['email']
            )
            del st.session_state.current_call
            st.rerun()
    else:
        st.warning("WebRTC not available. Using simulated call.")
        st.markdown(f"""
        <div class="call-container">
            <h3 style="color: #FFD700;">{'📹 Video Call (Simulated)' if call['call_type'] == 'video' else '🎧 Audio Call (Simulated)'}</h3>
        """, unsafe_allow_html=True)
        
        if st.button("🚫 End Call", type="primary"):
            del st.session_state.current_call
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

def render_language_selector():
    st.sidebar.markdown("### 🌐 Language")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("🇬🇧 EN", key="lang_en", use_container_width=True):
            st.session_state.language = 'en'
            st.rerun()
    with col2:
        if st.button("🇰🇪 SW", key="lang_sw", use_container_width=True):
            st.session_state.language = 'sw'
            st.rerun()

def render_accessibility_panel():
    with st.sidebar.expander("♿ Accessibility", expanded=False):
        if 'accessibility' not in st.session_state:
            st.session_state.accessibility = ACCESSIBILITY_PRESETS["Default"]
        
        text_size = st.select_slider(
            "Text Size",
            options=["Small", "Medium", "Large", "Extra Large"],
            value=st.session_state.accessibility.get('text_size', 'Medium')
        )
        
        high_contrast = st.checkbox(
            "High Contrast Mode",
            value=st.session_state.accessibility.get('contrast_mode', False)
        )
        
        if st.button("💾 Save Settings", use_container_width=True):
            st.session_state.accessibility.update({
                'text_size': text_size,
                'contrast_mode': high_contrast
            })
            st.success("Settings saved!")
            st.rerun()

def render_notifications():
    if st.session_state.user and st.session_state.current_school:
        unread_count = get_unread_notifications_count(
            st.session_state.current_school['code'],
            st.session_state.user['email']
        )
        
        with st.sidebar.expander(f"🔔 Notifications {f'({unread_count})' if unread_count > 0 else ''}", expanded=False):
            notifications = load_school_data(
                st.session_state.current_school['code'],
                "notifications.json", []
            )
            user_notifications = [n for n in notifications if n['user_email'] == st.session_state.user['email'] and not n['read']]
            
            if user_notifications:
                for notification in user_notifications[:5]:
                    st.markdown(f"**{notification['title']}**")
                    st.markdown(f"<small>{notification['message']}</small>", unsafe_allow_html=True)
                    st.markdown(f"<small>{notification['created_at'][:16]}</small>", unsafe_allow_html=True)
                    if st.button("✓", key=f"read_{notification['id']}"):
                        mark_notification_read(
                            st.session_state.current_school['code'],
                            notification['id']
                        )
                        st.rerun()
                    st.divider()
            else:
                st.info("No new notifications")

def render_enhanced_sidebar_additions():
    if st.session_state.user:
        st.sidebar.divider()
        render_notifications()
        render_language_selector()
        render_accessibility_panel()
        
        st.sidebar.divider()
        st.sidebar.markdown("### 🆕 Quick Access")
        
        if st.sidebar.button("🎥 Video Calls", key="nav_video", use_container_width=True):
            st.session_state.current_feature = 'video'
            st.rerun()
        
        if st.sidebar.button("🚨 EMERGENCY", key="nav_emergency", use_container_width=True, type="primary"):
            st.warning("Emergency feature coming soon!")

def render_selected_feature():
    if 'current_feature' in st.session_state and st.session_state.current_feature:
        if st.session_state.current_feature == 'video':
            if 'current_call' in st.session_state and st.session_state.current_call:
                render_call_room()
            else:
                render_video_meeting()
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("← Back to Dashboard", key="back_to_dash", use_container_width=True):
                st.session_state.current_feature = None
                st.session_state.current_call = None
                st.rerun()
        return True
    return False

# ============ SESSION STATE ============
if 'user' not in st.session_state:
    st.session_state.user = None
if 'current_school' not in st.session_state:
    st.session_state.current_school = None
if 'page' not in st.session_state:
    st.session_state.page = 'welcome'
if 'menu_index' not in st.session_state:
    st.session_state.menu_index = 0
if 'chat_with' not in st.session_state:
    st.session_state.chat_with = None
if 'group_chat_with' not in st.session_state:
    st.session_state.group_chat_with = None
if 'main_nav' not in st.session_state:
    st.session_state.main_nav = 'School Community'
if 'theme' not in st.session_state:
    st.session_state.theme = "Sunrise Glow"
if 'wallpaper' not in st.session_state:
    st.session_state.wallpaper = "None"
if 'current_feature' not in st.session_state:
    st.session_state.current_feature = None
if 'current_call' not in st.session_state:
    st.session_state.current_call = None
if 'language' not in st.session_state:
    st.session_state.language = 'en'
if 'accessibility' not in st.session_state:
    st.session_state.accessibility = ACCESSIBILITY_PRESETS["Default"]

# ============ MAIN APP ============

# Load user settings if logged in
if st.session_state.user and st.session_state.current_school:
    settings = load_user_settings(st.session_state.current_school['code'], st.session_state.user['email'])
    st.session_state.theme = settings.get("theme", "Sunrise Glow")
    st.session_state.wallpaper = settings.get("wallpaper", "None")

# Welcome Page
if st.session_state.page == 'welcome':
    st.markdown('<h1>✨ School Community Hub ✨</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #FFD700; font-size: 1.2rem;">Connect • Collaborate • Manage • Shine</p>', unsafe_allow_html=True)
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🏫 School Community", key="nav_community", use_container_width=True):
            st.session_state.main_nav = 'School Community'
    
    with col2:
        if st.button("📊 School Management", key="nav_management", use_container_width=True):
            st.session_state.main_nav = 'School Management'
    
    with col3:
        if st.button("👤 Personal Dashboard", key="nav_personal", use_container_width=True):
            st.session_state.main_nav = 'Personal Dashboard'
    
    st.divider()
    
    if st.session_state.main_nav == 'School Community':
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["👑 Admin Login", "🏫 Create School", "👨‍🏫 Teacher", "👨‍🎓 Student", "👪 Guardian"])
        
        with tab1:
            with st.form("admin_login"):
                st.subheader("Admin Login")
                school_code = st.text_input("School Code")
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                
                if st.form_submit_button("Login", use_container_width=True):
                    if school_code and email and password:
                        all_schools = load_all_schools()
                        if school_code in all_schools:
                            school = all_schools[school_code]
                            users = load_school_data(school_code, "users.json", [])
                            hashed = hashlib.sha256(password.encode()).hexdigest()
                            for u in users:
                                if u['email'] == email and u['password'] == hashed and u['role'] == 'admin':
                                    st.session_state.current_school = school
                                    st.session_state.user = u
                                    st.session_state.page = 'dashboard'
                                    st.rerun()
                            st.error("Invalid credentials")
                        else:
                            st.error("School not found")
        
        with tab2:
            with st.form("create_school"):
                st.subheader("Create New School")
                school_name = st.text_input("School Name")
                admin_name = st.text_input("Your Full Name")
                admin_email = st.text_input("Your Email")
                password = st.text_input("Password", type="password")
                confirm = st.text_input("Confirm Password", type="password")
                
                if st.form_submit_button("Create School", use_container_width=True):
                    if school_name and admin_email and password:
                        if password != confirm:
                            st.error("Passwords don't match")
                        else:
                            all_schools = load_all_schools()
                            code = generate_school_code()
                            while code in all_schools:
                                code = generate_school_code()
                            
                            new_school = {
                                "code": code,
                                "name": school_name,
                                "created": datetime.now().strftime("%Y-%m-%d"),
                                "admin_email": admin_email,
                                "admin_name": admin_name
                            }
                            all_schools[code] = new_school
                            save_all_schools(all_schools)
                            
                            users = [{
                                "user_id": generate_id("USR"),
                                "email": admin_email,
                                "fullname": admin_name,
                                "password": hashlib.sha256(password.encode()).hexdigest(),
                                "role": "admin",
                                "joined": datetime.now().strftime("%Y-%m-%d"),
                                "school_code": code
                            }]
                            save_school_data(code, "users.json", users)
                            
                            # Initialize all data files
                            save_school_data(code, "classes.json", [])
                            save_school_data(code, "groups.json", [])
                            save_school_data(code, "announcements.json", [])
                            save_school_data(code, "messages.json", [])
                            save_school_data(code, "calls.json", [])
                            save_school_data(code, "notifications.json", [])
                            
                            st.session_state.current_school = new_school
                            st.session_state.user = users[0]
                            st.session_state.page = 'dashboard'
                            st.success(f"✅ School Created! Code: **{code}**")
                            st.rerun()
        
        with tab3:
            with st.form("teacher_login"):
                st.subheader("Teacher Login")
                school_code = st.text_input("School Code")
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                
                if st.form_submit_button("Login", use_container_width=True):
                    if school_code and email and password:
                        all_schools = load_all_schools()
                        if school_code in all_schools:
                            school = all_schools[school_code]
                            users = load_school_data(school_code, "users.json", [])
                            hashed = hashlib.sha256(password.encode()).hexdigest()
                            for u in users:
                                if u['email'] == email and u['password'] == hashed and u['role'] == 'teacher':
                                    st.session_state.current_school = school
                                    st.session_state.user = u
                                    st.session_state.page = 'dashboard'
                                    st.rerun()
                            st.error("Invalid credentials")
                        else:
                            st.error("School not found")
        
        with tab4:
            with st.form("student_login"):
                st.subheader("Student Login")
                school_code = st.text_input("School Code")
                admission = st.text_input("Admission Number")
                password = st.text_input("Password", type="password")
                
                if st.form_submit_button("Login", use_container_width=True):
                    if school_code and admission and password:
                        all_schools = load_all_schools()
                        if school_code in all_schools:
                            school = all_schools[school_code]
                            users = load_school_data(school_code, "users.json", [])
                            hashed = hashlib.sha256(password.encode()).hexdigest()
                            for u in users:
                                if u.get('admission_number') == admission and u['password'] == hashed and u['role'] == 'student':
                                    st.session_state.current_school = school
                                    st.session_state.user = u
                                    st.session_state.page = 'dashboard'
                                    st.rerun()
                            st.error("Invalid credentials")
                        else:
                            st.error("School not found")
        
        with tab5:
            with st.form("guardian_login"):
                st.subheader("Guardian Login")
                school_code = st.text_input("School Code")
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                
                if st.form_submit_button("Login", use_container_width=True):
                    if school_code and email and password:
                        all_schools = load_all_schools()
                        if school_code in all_schools:
                            school = all_schools[school_code]
                            users = load_school_data(school_code, "users.json", [])
                            hashed = hashlib.sha256(password.encode()).hexdigest()
                            for u in users:
                                if u['email'] == email and u['password'] == hashed and u['role'] == 'guardian':
                                    st.session_state.current_school = school
                                    st.session_state.user = u
                                    st.session_state.page = 'dashboard'
                                    st.rerun()
                            st.error("Invalid credentials")
                        else:
                            st.error("School not found")

# Dashboard
elif st.session_state.page == 'dashboard' and st.session_state.current_school and st.session_state.user:
    school = st.session_state.current_school
    user = st.session_state.user
    school_code = school['code']
    
    users = load_school_data(school_code, "users.json", [])
    announcements = load_school_data(school_code, "announcements.json", [])
    unread_count = get_unread_count(user['email'], school_code)
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"""
        <div class="school-header">
            <h2>{school['name']}</h2>
            <div class="school-code">
                <code>{school['code']}</code>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="profile-card">', unsafe_allow_html=True)
        
        if user.get('profile_pic'):
            st.image(user['profile_pic'], width=50)
        else:
            emoji = "👑" if user['role'] == 'admin' else "👨‍🏫" if user['role'] == 'teacher' else "👨‍🎓" if user['role'] == 'student' else "👪"
            st.markdown(f"<h1 style='font-size: 2rem;'>{emoji}</h1>", unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="color: #FFD700;">
            <strong>{user['fullname']}</strong><br>
            <span style="background: rgba(0,0,0,0.3); padding: 2px 8px; border-radius: 12px;">{user['role'].upper()}</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.divider()
        
        options = ["Dashboard", "Announcements", f"Chat 💬{f' ({unread_count})' if unread_count>0 else ''}"]
        
        if user['role'] == 'admin':
            options.extend(["Users", "Classes", "Groups"])
        elif user['role'] == 'teacher':
            options.extend(["My Classes", "Groups"])
        elif user['role'] == 'student':
            options.extend(["My Classes", "Groups"])
        else:
            options.extend(["My Students"])
        
        options.extend(["Profile", "Settings"])
        
        if st.session_state.menu_index >= len(options):
            st.session_state.menu_index = 0
        
        menu = st.radio("Navigation", options, index=st.session_state.menu_index, label_visibility="collapsed")
        st.session_state.menu_index = options.index(menu)
        
        st.divider()
        
        # Add enhanced sidebar features
        render_enhanced_sidebar_additions()
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.user = None
            st.session_state.current_school = None
            st.session_state.page = 'welcome'
            st.rerun()
    
    # Main content
    if render_selected_feature():
        pass
    
    elif menu == "Dashboard":
        st.markdown(f"<h2>Welcome, {user['fullname']}!</h2>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Members", len(users))
        with col2:
            st.metric("Announcements", len(announcements))
        with col3:
            if user['role'] == 'student':
                st.metric("Classes", len([c for c in load_school_data(school_code, "classes.json", []) if user['email'] in c.get('students', [])]))
        
        if announcements:
            st.subheader("📢 Latest Announcements")
            for ann in announcements[-3:]:
                st.markdown(f"""
                <div class="golden-card">
                    <h4>{ann['title']}</h4>
                    <p><small>By {ann['author']} • {ann['date'][:16]}</small></p>
                    <p>{ann['content'][:100]}...</p>
                </div>
                """, unsafe_allow_html=True)
    
    elif menu == "Announcements":
        st.markdown("<h2>📢 Announcements</h2>", unsafe_allow_html=True)
        
        if user['role'] in ['admin', 'teacher']:
            with st.expander("➕ New Announcement"):
                with st.form("new_announcement"):
                    title = st.text_input("Title")
                    content = st.text_area("Content")
                    
                    if st.form_submit_button("Post", use_container_width=True):
                        if title and content:
                            announcements.append({
                                "id": generate_id("ANN"),
                                "title": title,
                                "content": content,
                                "author": user['fullname'],
                                "author_email": user['email'],
                                "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                            })
                            save_school_data(school_code, "announcements.json", announcements)
                            st.success("Announcement posted!")
                            st.rerun()
        
        if announcements:
            for ann in reversed(announcements):
                st.markdown(f"""
                <div class="golden-card">
                    <h4>{ann['title']}</h4>
                    <p><small>By {ann['author']} • {ann['date'][:16]}</small></p>
                    <p>{ann['content']}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No announcements yet")
    
    elif menu.startswith("Chat"):
        st.markdown("<h2>💬 Messages</h2>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("### Chats")
            friends = get_friends(school_code, user['email'])
            
            if friends:
                for friend_email in friends:
                    friend = next((u for u in users if u['email'] == friend_email), None)
                    if friend:
                        if st.button(f"👤 {friend['fullname']}", key=f"chat_{friend_email}", use_container_width=True):
                            st.session_state.chat_with = friend_email
                            st.rerun()
            else:
                st.info("No friends yet")
            
            st.markdown("### Find Friends")
            other_users = [u for u in users if u['email'] != user['email'] and u['email'] not in friends]
            if other_users:
                for other in other_users[:5]:
                    if st.button(f"➕ {other['fullname']}", key=f"add_{other['email']}", use_container_width=True):
                        send_friend_request(school_code, user['email'], other['email'])
                        st.success("Friend request sent!")
                        st.rerun()
        
        with col2:
            if st.session_state.chat_with:
                other_email = st.session_state.chat_with
                other_user = next((u for u in users if u['email'] == other_email), None)
                
                if other_user:
                    st.markdown(f"### Chat with {other_user['fullname']}")
                    
                    # Call buttons
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("🎧 Audio Call", use_container_width=True):
                            if WEBRTC_AVAILABLE:
                                call = initiate_webrtc_call(
                                    school_code,
                                    user['email'],
                                    [other_email],
                                    "audio"
                                )
                                st.session_state.current_call = call
                                st.session_state.current_feature = 'video'
                                st.rerun()
                            else:
                                st.error("WebRTC not available")
                    
                    with col_b:
                        if st.button("📹 Video Call", use_container_width=True):
                            if WEBRTC_AVAILABLE:
                                call = initiate_webrtc_call(
                                    school_code,
                                    user['email'],
                                    [other_email],
                                    "video"
                                )
                                st.session_state.current_call = call
                                st.session_state.current_feature = 'video'
                                st.rerun()
                            else:
                                st.error("WebRTC not available")
                    
                    messages = get_conversation_messages(school_code, user['email'], other_email)
                    
                    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
                    
                    for msg in messages:
                        is_sent = msg['sender'] == user['email']
                        sender_name = "You" if is_sent else other_user['fullname']
                        
                        st.markdown(f"""
                        <div class="chat-message-wrapper {'chat-message-sent' if is_sent else 'chat-message-received'}">
                            <div class="chat-bubble {'chat-bubble-sent' if is_sent else 'chat-bubble-received'}">
                                <div class="chat-sender-info">
                                    <span class="chat-sender-name">{sender_name}</span>
                                </div>
                                <div>{msg['message']}</div>
                                <div class="chat-time">{msg['timestamp'][:16]}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    with st.form("send_message", clear_on_submit=True):
                        message = st.text_area("Message", height=60, placeholder="Type a message...")
                        if st.form_submit_button("📤 Send", use_container_width=True):
                            if message:
                                send_message(school_code, user['email'], other_email, message, None)
                                st.rerun()
            else:
                st.info("Select a chat to start messaging")
    
    elif menu == "Profile":
        st.markdown("<h2>👤 My Profile</h2>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            if user.get('profile_pic'):
                st.image(user['profile_pic'], width=150)
            else:
                emoji = "👑" if user['role'] == 'admin' else "👨‍🏫" if user['role'] == 'teacher' else "👨‍🎓" if user['role'] == 'student' else "👪"
                st.markdown(f"<h1 style='font-size: 5rem;'>{emoji}</h1>", unsafe_allow_html=True)
            
            pic = st.file_uploader("📸 Upload Photo", type=['png', 'jpg', 'jpeg'])
            if pic:
                img = Image.open(pic)
                buffered = BytesIO()
                img.save(buffered, format="PNG")
                b64 = base64.b64encode(buffered.getvalue()).decode()
                for u in users:
                    if u['email'] == user['email']:
                        u['profile_pic'] = f"data:image/png;base64,{b64}"
                save_school_data(school_code, "users.json", users)
                user['profile_pic'] = f"data:image/png;base64,{b64}"
                st.rerun()
        
        with col2:
            with st.form("edit_profile"):
                name = st.text_input("Full Name", user['fullname'])
                phone = st.text_input("Phone", user.get('phone', ''))
                bio = st.text_area("Bio", user.get('bio', ''), height=100)
                
                if st.form_submit_button("💾 Update", use_container_width=True):
                    for u in users:
                        if u['email'] == user['email']:
                            u['fullname'] = name
                            u['phone'] = phone
                            u['bio'] = bio
                    save_school_data(school_code, "users.json", users)
                    user.update({'fullname': name, 'phone': phone, 'bio': bio})
                    st.success("Profile updated!")
                    st.rerun()
    
    elif menu == "Settings":
        st.markdown("<h2>⚙️ Settings</h2>", unsafe_allow_html=True)
        
        settings_tab1, settings_tab2 = st.tabs(["🎨 Theme", "🔔 Notifications"])
        
        with settings_tab1:
            st.subheader("Theme Selection")
            
            selected_theme = st.selectbox("Choose Theme", list(THEMES.keys()), 
                                         index=list(THEMES.keys()).index(st.session_state.theme))
            
            selected_wallpaper = st.selectbox("Choose Wallpaper", list(WALLPAPERS.keys()),
                                            index=list(WALLPAPERS.keys()).index(st.session_state.wallpaper))
            
            if st.button("💾 Save Theme", use_container_width=True):
                st.session_state.theme = selected_theme
                st.session_state.wallpaper = selected_wallpaper
                save_user_settings(school_code, user['email'], {
                    "theme": selected_theme,
                    "wallpaper": selected_wallpaper
                })
                st.success("Settings saved!")
                st.rerun()
        
        with settings_tab2:
            st.subheader("Notification Settings")
            st.info("Notification settings coming soon!")

else:
    st.error("Something went wrong. Please restart.")
    if st.button("Restart"):
        st.session_state.page = 'welcome'
        st.rerun()
