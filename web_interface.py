#!/usr/bin/env python3
"""
Monster Hunter Frontier G - Web Interface & Admin Panel
Real-time server monitoring, player management, and admin controls
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
import hashlib
import secrets
from functools import wraps

# Import our server systems
from enhanced_auth import MHFEnhancedAuth
from item_equipment_system import ItemDatabase, PlayerInventory
from advanced_quest_system import QuestManager
from advanced_guild_system import GuildManager
from monster_ai_system import MonsterSpawner

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mhf-frontier-secret-key-2024'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize server systems
auth_system = MHFEnhancedAuth()
item_db = ItemDatabase()
quest_manager = QuestManager()
guild_manager = GuildManager()
monster_spawner = MonsterSpawner()

# Server statistics
server_stats = {
    'start_time': datetime.now(),
    'total_players': 0,
    'online_players': 0,
    'total_quests_completed': 0,
    'total_monsters_defeated': 0,
    'server_uptime': 0,
    'active_connections': 0
}

# Active sessions
active_sessions = {}
admin_users = {
    'admin': hashlib.sha256('admin123'.encode()).hexdigest()
}

def admin_required(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def get_server_status():
    """Get current server status"""
    uptime = datetime.now() - server_stats['start_time']
    server_stats['server_uptime'] = str(uptime).split('.')[0]
    
    return {
        'uptime': server_stats['server_uptime'],
        'online_players': server_stats['online_players'],
        'total_players': server_stats['total_players'],
        'active_connections': server_stats['active_connections'],
        'total_quests': server_stats['total_quests_completed'],
        'total_monsters': server_stats['total_monsters_defeated'],
        'cpu_usage': '45%',  # Placeholder
        'memory_usage': '2.1 GB',  # Placeholder
        'network_traffic': '1.2 MB/s'  # Placeholder
    }

@app.route('/')
def index():
    """Main server status page"""
    status = get_server_status()
    return render_template('index.html', status=status)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        if username in admin_users and admin_users[username] == password_hash:
            session['admin_logged_in'] = True
            session['admin_username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials!', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    status = get_server_status()
    
    # Get recent activity
    recent_activity = get_recent_activity()
    
    # Get player statistics
    player_stats = get_player_statistics()
    
    return render_template('admin_dashboard.html', 
                         status=status, 
                         activity=recent_activity,
                         player_stats=player_stats)

@app.route('/admin/players')
@admin_required
def admin_players():
    """Player management page"""
    players = get_all_players()
    return render_template('admin_players.html', players=players)

@app.route('/admin/quests')
@admin_required
def admin_quests():
    """Quest management page"""
    quests = get_all_quests()
    return render_template('admin_quests.html', quests=quests)

@app.route('/admin/guilds')
@admin_required
def admin_guilds():
    """Guild management page"""
    guilds = get_all_guilds()
    return render_template('admin_guilds.html', guilds=guilds)

@app.route('/admin/monsters')
@admin_required
def admin_monsters():
    """Monster management page"""
    monsters = get_active_monsters()
    return render_template('admin_monsters.html', monsters=monsters)

@app.route('/admin/settings')
@admin_required
def admin_settings():
    """Server settings page"""
    settings = get_server_settings()
    return render_template('admin_settings.html', settings=settings)

# API endpoints
@app.route('/api/status')
def api_status():
    """Get server status API"""
    return jsonify(get_server_status())

@app.route('/api/players')
@admin_required
def api_players():
    """Get all players API"""
    players = get_all_players()
    return jsonify(players)

@app.route('/api/player/<player_id>')
@admin_required
def api_player_details(player_id):
    """Get player details API"""
    player = get_player_details(player_id)
    if player:
        return jsonify(player)
    return jsonify({'error': 'Player not found'}), 404

@app.route('/api/player/<player_id>/ban', methods=['POST'])
@admin_required
def api_ban_player(player_id):
    """Ban a player"""
    reason = request.json.get('reason', 'No reason provided')
    success = ban_player(player_id, reason)
    return jsonify({'success': success})

@app.route('/api/player/<player_id>/unban', methods=['POST'])
@admin_required
def api_unban_player(player_id):
    """Unban a player"""
    success = unban_player(player_id)
    return jsonify({'success': success})

@app.route('/api/quests')
@admin_required
def api_quests():
    """Get all quests API"""
    quests = get_all_quests()
    return jsonify(quests)

@app.route('/api/quest/create', methods=['POST'])
@admin_required
def api_create_quest():
    """Create a new quest"""
    quest_data = request.json
    success = create_custom_quest(quest_data)
    return jsonify({'success': success})

@app.route('/api/guilds')
@admin_required
def api_guilds():
    """Get all guilds API"""
    guilds = get_all_guilds()
    return jsonify(guilds)

@app.route('/api/monsters')
@admin_required
def api_monsters():
    """Get active monsters API"""
    monsters = get_active_monsters()
    return jsonify(monsters)

@app.route('/api/monster/spawn', methods=['POST'])
@admin_required
def api_spawn_monster():
    """Spawn a monster"""
    monster_data = request.json
    success = spawn_monster_admin(monster_data)
    return jsonify({'success': success})

@app.route('/api/server/restart', methods=['POST'])
@admin_required
def api_restart_server():
    """Restart the server"""
    # This would trigger a server restart
    return jsonify({'success': True, 'message': 'Server restart initiated'})

@app.route('/api/server/backup', methods=['POST'])
@admin_required
def api_backup_server():
    """Create server backup"""
    success = create_server_backup()
    return jsonify({'success': success})

# WebSocket events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    server_stats['active_connections'] += 1
    emit('server_status', get_server_status())

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    server_stats['active_connections'] -= 1

@socketio.on('join_admin')
def handle_join_admin():
    """Join admin room for real-time updates"""
    if 'admin_logged_in' in session:
        join_room('admin')
        emit('admin_joined', {'message': 'Connected to admin panel'})

@socketio.on('request_player_update')
def handle_player_update():
    """Handle player update request"""
    players = get_all_players()
    emit('player_update', players)

@socketio.on('request_monster_update')
def handle_monster_update():
    """Handle monster update request"""
    monsters = get_active_monsters()
    emit('monster_update', monsters)

# Helper functions
def get_recent_activity():
    """Get recent server activity"""
    # This would query the database for recent activity
    return [
        {
            'time': datetime.now() - timedelta(minutes=5),
            'type': 'player_login',
            'message': 'Player hunter001 logged in',
            'player_id': 'hunter001'
        },
        {
            'time': datetime.now() - timedelta(minutes=10),
            'type': 'quest_completed',
            'message': 'Quest "Hunt Great Jaggi" completed by dragon_slayer',
            'player_id': 'dragon_slayer'
        },
        {
            'time': datetime.now() - timedelta(minutes=15),
            'type': 'monster_defeated',
            'message': 'Rathian defeated by party of 3 hunters',
            'player_id': 'party_001'
        }
    ]

def get_player_statistics():
    """Get player statistics"""
    return {
        'total_registered': 150,
        'active_today': 45,
        'new_this_week': 12,
        'premium_users': 23,
        'average_playtime': '2.5 hours',
        'top_hunter': 'dragon_slayer'
    }

def get_all_players():
    """Get all players"""
    # This would query the database
    return [
        {
            'id': 'hunter001',
            'username': 'hunter001',
            'level': 15,
            'hr': 5,
            'last_login': datetime.now() - timedelta(hours=2),
            'status': 'online',
            'guild': 'Dragon Slayers',
            'quests_completed': 25
        },
        {
            'id': 'dragon_slayer',
            'username': 'dragon_slayer',
            'level': 25,
            'hr': 8,
            'last_login': datetime.now() - timedelta(hours=1),
            'status': 'online',
            'guild': 'Dragon Slayers',
            'quests_completed': 45
        }
    ]

def get_player_details(player_id):
    """Get detailed player information"""
    # This would query the database for detailed player info
    return {
        'id': player_id,
        'username': 'hunter001',
        'level': 15,
        'hr': 5,
        'experience': 15000,
        'zenny': 50000,
        'created_date': datetime.now() - timedelta(days=30),
        'last_login': datetime.now() - timedelta(hours=2),
        'total_playtime': '45 hours',
        'quests_completed': 25,
        'monsters_defeated': 150,
        'guild': 'Dragon Slayers',
        'guild_rank': 'member',
        'equipment': {
            'weapon': 'Iron Sword',
            'armor': 'Leather Set'
        },
        'inventory': {
            'items': 45,
            'max_capacity': 50
        }
    }

def ban_player(player_id, reason):
    """Ban a player"""
    # This would update the database to ban the player
    print(f"Banning player {player_id} for reason: {reason}")
    return True

def unban_player(player_id):
    """Unban a player"""
    # This would update the database to unban the player
    print(f"Unbanning player {player_id}")
    return True

def get_all_quests():
    """Get all quests"""
    # This would query the quest database
    return [
        {
            'id': 'quest_001',
            'name': 'Hunt Great Jaggi',
            'type': 'hunt',
            'rank': 'Low Rank',
            'location': 'Forest',
            'time_limit': 50,
            'rewards': '1000 zenny, 500 exp',
            'completion_rate': '85%'
        },
        {
            'id': 'quest_002',
            'name': 'Gather Herbs',
            'type': 'gathering',
            'rank': 'Low Rank',
            'location': 'Forest',
            'time_limit': 30,
            'rewards': '500 zenny, 200 exp',
            'completion_rate': '95%'
        }
    ]

def create_custom_quest(quest_data):
    """Create a custom quest"""
    # This would create a new quest in the database
    print(f"Creating custom quest: {quest_data}")
    return True

def get_all_guilds():
    """Get all guilds"""
    # This would query the guild database
    return [
        {
            'id': 'guild_001',
            'name': 'Dragon Slayers',
            'leader': 'GuildLeader',
            'members': 15,
            'max_members': 30,
            'level': 5,
            'experience': 2500,
            'created_date': datetime.now() - timedelta(days=60)
        }
    ]

def get_active_monsters():
    """Get active monsters"""
    # This would get monsters from the spawner
    return [
        {
            'id': 'monster_001',
            'name': 'Great Jaggi',
            'type': 'Great Jaggi',
            'health': 600,
            'max_health': 800,
            'location': 'Forest',
            'position': {'x': 10, 'y': 0, 'z': 15},
            'status': 'patrolling',
            'target_player': None
        },
        {
            'id': 'monster_002',
            'name': 'Rathian',
            'type': 'Rathian',
            'health': 1800,
            'max_health': 2000,
            'location': 'Volcano',
            'position': {'x': -5, 'y': 0, 'z': 20},
            'status': 'chasing',
            'target_player': 'hunter001'
        }
    ]

def spawn_monster_admin(monster_data):
    """Spawn a monster via admin command"""
    # This would spawn a monster using the spawner
    print(f"Spawning monster via admin: {monster_data}")
    return True

def get_server_settings():
    """Get server settings"""
    return {
        'max_players': 100,
        'quest_timeout': 300,
        'monster_spawn_rate': 30,
        'experience_multiplier': 1.0,
        'drop_rate_multiplier': 1.0,
        'maintenance_mode': False,
        'auto_backup': True,
        'backup_interval': 24
    }

def create_server_backup():
    """Create server backup"""
    # This would create a backup of all databases
    print("Creating server backup...")
    return True

# Create templates directory and basic templates
def create_templates():
    """Create basic HTML templates"""
    templates_dir = Path("templates")
    templates_dir.mkdir(exist_ok=True)
    
    # Create base template
    base_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}MHF Server{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .sidebar { min-height: 100vh; background: #2c3e50; }
        .sidebar .nav-link { color: #ecf0f1; }
        .sidebar .nav-link:hover { background: #34495e; }
        .main-content { background: #f8f9fa; }
        .status-card { border-left: 4px solid #28a745; }
        .status-card.warning { border-left-color: #ffc107; }
        .status-card.danger { border-left-color: #dc3545; }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            {% if session.admin_logged_in %}
            <nav class="col-md-2 sidebar p-0">
                <div class="p-3">
                    <h4 class="text-white">MHF Admin</h4>
                </div>
                <ul class="nav flex-column">
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('admin_dashboard') }}">
                            <i class="fas fa-tachometer-alt"></i> Dashboard
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('admin_players') }}">
                            <i class="fas fa-users"></i> Players
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('admin_quests') }}">
                            <i class="fas fa-tasks"></i> Quests
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('admin_guilds') }}">
                            <i class="fas fa-shield-alt"></i> Guilds
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('admin_monsters') }}">
                            <i class="fas fa-dragon"></i> Monsters
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('admin_settings') }}">
                            <i class="fas fa-cog"></i> Settings
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('admin_logout') }}">
                            <i class="fas fa-sign-out-alt"></i> Logout
                        </a>
                    </li>
                </ul>
            </nav>
            <main class="col-md-10 main-content">
            {% else %}
            <main class="col-12 main-content">
            {% endif %}
                {% with messages = get_flashed_messages(with_categories=true) %}
                    {% if messages %}
                        {% for category, message in messages %}
                            <div class="alert alert-{{ 'danger' if category == 'error' else category }} alert-dismissible fade show" role="alert">
                                {{ message }}
                                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                            </div>
                        {% endfor %}
                    {% endif %}
                {% endwith %}
                
                {% block content %}{% endblock %}
            </main>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    {% block scripts %}{% endblock %}
</body>
</html>'''
    
    with open(templates_dir / "base.html", "w") as f:
        f.write(base_template)
    
    # Create index template
    index_template = '''{% extends "base.html" %}
{% block title %}MHF Server Status{% endblock %}
{% block content %}
<div class="container-fluid p-4">
    <h1 class="mb-4">🐉 Monster Hunter Frontier G Server</h1>
    
    <div class="row">
        <div class="col-md-3">
            <div class="card status-card">
                <div class="card-body">
                    <h5 class="card-title">Online Players</h5>
                    <h2 class="text-primary">{{ status.online_players }}</h2>
                    <small class="text-muted">Total: {{ status.total_players }}</small>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card status-card">
                <div class="card-body">
                    <h5 class="card-title">Server Uptime</h5>
                    <h2 class="text-success">{{ status.uptime }}</h2>
                    <small class="text-muted">Since {{ status.start_time }}</small>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card status-card">
                <div class="card-body">
                    <h5 class="card-title">Active Connections</h5>
                    <h2 class="text-info">{{ status.active_connections }}</h2>
                    <small class="text-muted">Real-time</small>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card status-card">
                <div class="card-body">
                    <h5 class="card-title">Quests Completed</h5>
                    <h2 class="text-warning">{{ status.total_quests }}</h2>
                    <small class="text-muted">Today</small>
                </div>
            </div>
        </div>
    </div>
    
    <div class="row mt-4">
        <div class="col-md-6">
            <div class="card">
                <div class="card-header">
                    <h5>Server Performance</h5>
                </div>
                <div class="card-body">
                    <p><strong>CPU Usage:</strong> {{ status.cpu_usage }}</p>
                    <p><strong>Memory Usage:</strong> {{ status.memory_usage }}</p>
                    <p><strong>Network Traffic:</strong> {{ status.network_traffic }}</p>
                </div>
            </div>
        </div>
        <div class="col-md-6">
            <div class="card">
                <div class="card-header">
                    <h5>Quick Actions</h5>
                </div>
                <div class="card-body">
                    <a href="{{ url_for('admin_login') }}" class="btn btn-primary">Admin Login</a>
                    <button class="btn btn-info" onclick="refreshStatus()">Refresh Status</button>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
{% block scripts %}
<script>
function refreshStatus() {
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            // Update status display
            console.log('Status updated:', data);
        });
}

// Auto-refresh every 30 seconds
setInterval(refreshStatus, 30000);
</script>
{% endblock %}'''
    
    with open(templates_dir / "index.html", "w") as f:
        f.write(index_template)
    
    # Create admin login template
    login_template = '''{% extends "base.html" %}
{% block title %}Admin Login{% endblock %}
{% block content %}
<div class="container mt-5">
    <div class="row justify-content-center">
        <div class="col-md-6">
            <div class="card">
                <div class="card-header">
                    <h3>Admin Login</h3>
                </div>
                <div class="card-body">
                    <form method="POST">
                        <div class="mb-3">
                            <label for="username" class="form-label">Username</label>
                            <input type="text" class="form-control" id="username" name="username" required>
                        </div>
                        <div class="mb-3">
                            <label for="password" class="form-label">Password</label>
                            <input type="password" class="form-control" id="password" name="password" required>
                        </div>
                        <button type="submit" class="btn btn-primary">Login</button>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}'''
    
    with open(templates_dir / "admin_login.html", "w") as f:
        f.write(login_template)
    
    # Create admin dashboard template
    dashboard_template = '''{% extends "base.html" %}
{% block title %}Admin Dashboard{% endblock %}
{% block content %}
<div class="container-fluid p-4">
    <h1 class="mb-4">Admin Dashboard</h1>
    
    <div class="row">
        <div class="col-md-3">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">Total Players</h5>
                    <h2>{{ player_stats.total_registered }}</h2>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">Active Today</h5>
                    <h2>{{ player_stats.active_today }}</h2>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">New This Week</h5>
                    <h2>{{ player_stats.new_this_week }}</h2>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">Premium Users</h5>
                    <h2>{{ player_stats.premium_users }}</h2>
                </div>
            </div>
        </div>
    </div>
    
    <div class="row mt-4">
        <div class="col-md-8">
            <div class="card">
                <div class="card-header">
                    <h5>Recent Activity</h5>
                </div>
                <div class="card-body">
                    <div class="list-group">
                        {% for item in activity %}
                        <div class="list-group-item">
                            <div class="d-flex w-100 justify-content-between">
                                <h6 class="mb-1">{{ item.message }}</h6>
                                <small>{{ item.time.strftime('%H:%M') }}</small>
                            </div>
                            <small class="text-muted">{{ item.type }}</small>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card">
                <div class="card-header">
                    <h5>Quick Actions</h5>
                </div>
                <div class="card-body">
                    <button class="btn btn-warning btn-sm mb-2" onclick="restartServer()">Restart Server</button><br>
                    <button class="btn btn-info btn-sm mb-2" onclick="createBackup()">Create Backup</button><br>
                    <button class="btn btn-success btn-sm mb-2" onclick="spawnMonster()">Spawn Monster</button>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
{% block scripts %}
<script>
function restartServer() {
    if (confirm('Are you sure you want to restart the server?')) {
        fetch('/api/server/restart', {method: 'POST'})
            .then(response => response.json())
            .then(data => alert(data.message));
    }
}

function createBackup() {
    fetch('/api/server/backup', {method: 'POST'})
        .then(response => response.json())
        .then(data => alert('Backup created successfully!'));
}

function spawnMonster() {
    const monsterData = {
        type: 'great_jaggi',
        location: 'Forest',
        position: {x: 0, y: 0, z: 0}
    };
    
    fetch('/api/monster/spawn', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(monsterData)
    })
    .then(response => response.json())
    .then(data => alert('Monster spawned!'));
}
</script>
{% endblock %}'''
    
    with open(templates_dir / "admin_dashboard.html", "w") as f:
        f.write(dashboard_template)

def start_web_interface():
    """Start the web interface"""
    print("🌐 Starting MHF Web Interface...")
    create_templates()
    
    # Start the Flask app
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)

if __name__ == "__main__":
    start_web_interface() 