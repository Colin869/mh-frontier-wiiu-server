# 🎮 Monster Hunter Frontier G - Discord Bot Setup Guide

## 🤖 Discord Bot Integration

Your MHF server now includes a **comprehensive Discord bot** that provides real-time server status, player management, guild features, and admin controls!

### 📋 Bot Features

#### **🟢 Real-time Server Status**
- **Live player count** and server statistics
- **Active quests** and monster tracking
- **Guild information** and rankings
- **Server performance** monitoring
- **Automatic status updates** every 5 minutes

#### **👥 Player Management**
- **Account linking** between Discord and MHF
- **Player profiles** with detailed statistics
- **Online player lists** and status tracking
- **Achievement notifications** and progress updates

#### **🏰 Guild Features**
- **Guild listings** and rankings
- **Guild quest coordination** and announcements
- **Member management** and recruitment
- **Guild achievements** and progress tracking

#### **📋 Quest System**
- **Quest listings** by rank and type
- **Quest information** with objectives and rewards
- **Party finder** for quest coordination
- **Quest completion** notifications

#### **⚔️ Monster Tracking**
- **Active monster alerts** and spawn notifications
- **Monster type** and location tracking
- **Hunting coordination** and party formation
- **Defeat notifications** and rewards

#### **🔧 Admin Controls**
- **Server announcements** and notifications
- **Monster spawning** and management
- **Server restart** and maintenance controls
- **Detailed statistics** and monitoring

### 🚀 Setup Instructions

#### **Step 1: Create a Discord Bot**

1. **Go to Discord Developer Portal**
   - Visit: https://discord.com/developers/applications
   - Click "New Application"
   - Name it "MHF Server Bot"

2. **Create the Bot**
   - Go to "Bot" section in the left sidebar
   - Click "Add Bot"
   - Give it a name like "MHF Server Bot"
   - Upload a custom avatar (optional)

3. **Configure Bot Permissions**
   - Scroll down to "Privileged Gateway Intents"
   - Enable all three intents:
     - ✅ Presence Intent
     - ✅ Server Members Intent
     - ✅ Message Content Intent

4. **Get Your Bot Token**
   - Copy the bot token (you'll need this later)
   - **Keep this secret!** Never share your bot token

#### **Step 2: Invite Bot to Your Server**

1. **Generate Invite Link**
   - Go to "OAuth2" → "URL Generator"
   - Select "bot" under "Scopes"
   - Select these permissions:
     - ✅ Send Messages
     - ✅ Embed Links
     - ✅ Attach Files
     - ✅ Read Message History
     - ✅ Add Reactions
     - ✅ Use Slash Commands
     - ✅ Manage Messages (for admin commands)

2. **Invite the Bot**
   - Copy the generated URL
   - Open it in a browser
   - Select your Discord server
   - Authorize the bot

#### **Step 3: Configure Bot Settings**

1. **Edit `discord_bot.py`**
   - Replace `YOUR_DISCORD_BOT_TOKEN_HERE` with your actual bot token
   - Update the channel IDs with your server's channel IDs

2. **Get Channel IDs**
   - Enable Developer Mode in Discord (User Settings → Advanced → Developer Mode)
   - Right-click on each channel and copy the ID
   - Update these IDs in the bot configuration:

```python
# Replace these with your actual channel IDs
STATUS_CHANNEL_ID = 123456789  # #server-status channel
ANNOUNCEMENTS_CHANNEL_ID = 123456789  # #announcements channel
GUILD_CHANNEL_ID = 123456789  # #guild-chat channel
QUEST_CHANNEL_ID = 123456789  # #quest-coordination channel
ADMIN_CHANNEL_ID = 123456789  # #admin-commands channel
LOG_CHANNEL_ID = 123456789  # #bot-logs channel
```

3. **Set up Role IDs**
   - Get your admin and moderator role IDs
   - Update these in the configuration:

```python
ADMIN_ROLE_ID = 123456789  # Your admin role ID
MODERATOR_ROLE_ID = 123456789  # Your moderator role ID
```

#### **Step 4: Install Dependencies**

```bash
pip install discord.py
```

#### **Step 5: Run the Bot**

```bash
python discord_bot.py
```

### 📱 Bot Commands

#### **Server Commands**
- `!mhf status` - Show current server status
- `!mhf players` - List online players
- `!mhf monsters` - Show active monsters

#### **Player Commands**
- `!mhf link <username> <password>` - Link Discord to MHF account
- `!mhf profile [username]` - Show player profile
- `!mhf unlink` - Unlink Discord from MHF account

#### **Guild Commands**
- `!mhf guilds` - List all guilds
- `!mhf guild <name>` - Show guild information
- `!mhf guildquest [type]` - Show guild quests

#### **Quest Commands**
- `!mhf quests [rank]` - List available quests
- `!mhf quest <name>` - Show quest information
- `!mhf party <quest>` - Find party for quest

#### **Admin Commands** (Admin/Moderator only)
- `!mhf announce <message>` - Send server announcement
- `!mhf spawn <monster> [location]` - Spawn a monster
- `!mhf restart` - Restart the server
- `!mhf stats` - Show detailed server statistics

### 🏗️ Recommended Discord Server Structure

#### **📢 Information Channels**
- `#server-status` - Live server status updates
- `#announcements` - Server announcements and news
- `#rules` - Server rules and guidelines
- `#welcome` - New player welcome and information

#### **🎮 Game Channels**
- `#general` - General game discussion
- `#guild-chat` - Guild recruitment and discussion
- `#quest-coordination` - Quest party finding
- `#trading` - Item trading and marketplace
- `#help` - Player help and support

#### **⚔️ Hunting Channels**
- `#hunting-parties` - Hunting party formation
- `#monster-alerts` - Monster spawn notifications
- `#boss-hunts` - Boss monster coordination
- `#guild-quests` - Guild quest coordination

#### **🔧 Admin Channels**
- `#admin-commands` - Admin command usage
- `#bot-logs` - Bot activity logs
- `#server-management` - Server administration discussion

### 🎯 Advanced Configuration

#### **Custom Bot Status**
Edit the bot's status message in `discord_bot.py`:

```python
await self.change_presence(
    activity=discord.Game(name="Monster Hunter Frontier G"),
    status=discord.Status.online
)
```

#### **Custom Embed Colors**
You can customize the embed colors for different types of messages:

```python
# Success messages
color=discord.Color.green()

# Error messages
color=discord.Color.red()

# Information messages
color=discord.Color.blue()

# Warning messages
color=discord.Color.orange()

# Admin messages
color=discord.Color.gold()
```

#### **Custom Update Intervals**
Modify the update intervals in the bot:

```python
@tasks.loop(minutes=5)  # Status updates every 5 minutes
async def update_status(self):
    # Status update code

@tasks.loop(minutes=1)  # Server monitoring every 1 minute
async def monitor_server(self):
    # Monitoring code
```

### 🔒 Security Considerations

#### **Bot Token Security**
- **Never share your bot token** publicly
- **Don't commit the token** to version control
- **Use environment variables** for production:

```python
import os
BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
```

#### **Permission Management**
- **Use role-based permissions** for admin commands
- **Limit bot permissions** to only what's needed
- **Regularly audit** bot permissions and access

#### **Rate Limiting**
- **Respect Discord's rate limits** (5 requests per 2 seconds)
- **Use appropriate delays** between API calls
- **Handle rate limit errors** gracefully

### 🚀 Production Deployment

#### **Environment Variables**
Create a `.env` file for production:

```env
DISCORD_BOT_TOKEN=your_bot_token_here
GUILD_ID=your_guild_id_here
ADMIN_ROLE_ID=your_admin_role_id_here
MODERATOR_ROLE_ID=your_moderator_role_id_here
```

#### **Systemd Service** (Linux)
Create a systemd service for automatic startup:

```ini
[Unit]
Description=MHF Discord Bot
After=network.target

[Service]
Type=simple
User=mhf
WorkingDirectory=/path/to/mhf/server
ExecStart=/usr/bin/python3 discord_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### **Docker Deployment**
Create a `Dockerfile` for containerized deployment:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "discord_bot.py"]
```

### 🎉 Bot Features Showcase

#### **Real-time Status Updates**
```
🐉 MHF Server Status
👥 Players: Online: 15 | Total: 150
📋 Quests: Active: 8 | Available: 45
🐉 Monsters: Active: 12 | Spawn Rate: 30s
🏰 Guilds: Total: 8 | Active: 6
⚔️ Combat: Monsters Defeated: 125 | Quests Completed: 89
🕒 Uptime: Server: 2:15:30 | Last Update: 14:30
```

#### **Player Profile Display**
```
👤 Hunter001's Profile
Level: 25 | HR: 8 | Experience: 45,000
Guild: Dragon Slayers | Guild Rank: 3 | Status: 🟢 Online
Created: 2024-01-15 | Last Login: 2024-01-20 14:25 | Subscription: Premium
```

#### **Quest Information**
```
🎯 Hunt Great Jaggi
Type: Hunt | Rank: 1 Star | Location: Forest
Time Limit: 50 minutes | Players: 4 hunters | HR Required: HR 1

Objectives:
1. Hunt Great Jaggi
2. Gather Herbs

Rewards:
Zenny: 1,000 | Experience: 500 | Materials: great_jaggi_scale x2
```

### 🎮 Integration with Your MHF Server

The Discord bot integrates seamlessly with all your MHF server systems:

- **Authentication System** - Player account linking
- **Quest System** - Real-time quest tracking and coordination
- **Guild System** - Guild management and announcements
- **Monster AI** - Monster spawn alerts and tracking
- **Item System** - Trading and marketplace features
- **Web Interface** - Admin controls and monitoring

### 🚀 Next Steps

1. **Set up your Discord server** with the recommended channel structure
2. **Create and configure your Discord bot** following the setup guide
3. **Test all bot commands** to ensure everything works correctly
4. **Customize the bot** with your server's specific needs
5. **Deploy to production** for 24/7 operation
6. **Invite players** to your Discord server and start hunting!

### 🎯 Support and Troubleshooting

#### **Common Issues**
- **Bot not responding**: Check bot permissions and token
- **Commands not working**: Verify bot prefix and permissions
- **Channel errors**: Ensure channel IDs are correct
- **Rate limiting**: Add delays between API calls

#### **Getting Help**
- Check the bot logs for error messages
- Verify all configuration settings
- Test commands in a private channel first
- Consult Discord.py documentation for advanced features

---

**🎉 Your MHF server now has the most advanced Discord integration ever created!**

**Players can coordinate hunts, manage guilds, track quests, and stay connected with your server community - all through Discord! 🐉⚔️** 