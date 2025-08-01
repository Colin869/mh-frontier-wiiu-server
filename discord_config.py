#!/usr/bin/env python3
"""
Monster Hunter Frontier G - Discord Bot Configuration
Easy setup for your Discord bot
"""

# ========================================
# DISCORD BOT CONFIGURATION
# ========================================

# Replace this with your bot token from Discord Developer Portal
BOT_TOKEN = 'YOUR_BOT_TOKEN_HERE'

# Replace these with your Discord server (guild) ID
# Right-click your server name and "Copy Server ID" (with Developer Mode enabled)
GUILD_ID = 1337668714358636581  # Replace with your server ID

# Replace these with your role IDs
# Right-click the role and "Copy Role ID" (with Developer Mode enabled)
ADMIN_ROLE_ID = 1337669411036860496  # Replace with your admin role ID
MODERATOR_ROLE_ID = 1337669414174068816  # Replace with your moderator role ID

# Replace these with your channel IDs
# Right-click each channel and "Copy Channel ID" (with Developer Mode enabled)
STATUS_CHANNEL_ID = 1400941220896706702  # #server-status channel
ANNOUNCEMENTS_CHANNEL_ID = 1400941433795383420  # #announcements channel
GUILD_CHANNEL_ID = 1337668716665638933  # #guild-chat channel
QUEST_CHANNEL_ID = 1400937489593532490  # #quest-coordination channel
ADMIN_CHANNEL_ID = 1400942049603096697  # #admin-commands channel
LOG_CHANNEL_ID = 1400942360040308786  # #bot-logs channel

# ========================================
# HOW TO GET THESE IDs
# ========================================

"""
STEP-BY-STEP GUIDE:

1. ENABLE DEVELOPER MODE:
   - Open Discord
   - Go to User Settings (gear icon)
   - Go to "Advanced"
   - Turn on "Developer Mode"

2. GET SERVER ID:
   - Right-click your server name
   - Click "Copy Server ID"
   - Paste it as GUILD_ID

3. GET ROLE IDs:
   - Go to Server Settings > Roles
   - Right-click each role
   - Click "Copy Role ID"
   - Paste as ADMIN_ROLE_ID and MODERATOR_ROLE_ID

4. GET CHANNEL IDs:
   - Right-click each channel
   - Click "Copy Channel ID"
   - Paste as the corresponding channel ID

5. GET BOT TOKEN:
   - Go to Discord Developer Portal
   - Select your application
   - Go to "Bot" section
   - Click "Copy" under Token
   - Paste as BOT_TOKEN
"""

# ========================================
# RECOMMENDED CHANNEL STRUCTURE
# ========================================

"""
Create these channels in your Discord server:

📢 INFORMATION CHANNELS:
- #server-status (for live server updates)
- #announcements (for server announcements)
- #rules (server rules and guidelines)
- #welcome (new player information)

🎮 GAME CHANNELS:
- #general (general game discussion)
- #guild-chat (guild recruitment and discussion)
- #quest-coordination (quest party finding)
- #trading (item trading and marketplace)
- #help (player help and support)

⚔️ HUNTING CHANNELS:
- #hunting-parties (hunting party formation)
- #monster-alerts (monster spawn notifications)
- #boss-hunts (boss monster coordination)
- #guild-quests (guild quest coordination)

🔧 ADMIN CHANNELS:
- #admin-commands (admin command usage)
- #bot-logs (bot activity logs)
- #server-management (server administration)
"""

# ========================================
# TEST YOUR CONFIGURATION
# ========================================

def test_configuration():
    """Test if your configuration is set up correctly"""
    print("🤖 Testing Discord Bot Configuration")
    print("=" * 50)
    
    # Check if token is set
    if BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        print("❌ BOT_TOKEN not configured!")
        print("   Get your bot token from Discord Developer Portal")
    else:
        print("✅ BOT_TOKEN configured")
    
    # Check if guild ID is set
    if GUILD_ID == 123456789:
        print("❌ GUILD_ID not configured!")
        print("   Right-click your server name and copy Server ID")
    else:
        print("✅ GUILD_ID configured")
    
    # Check if role IDs are set
    if ADMIN_ROLE_ID == 123456789:
        print("❌ ADMIN_ROLE_ID not configured!")
        print("   Right-click your admin role and copy Role ID")
    else:
        print("✅ ADMIN_ROLE_ID configured")
    
    if MODERATOR_ROLE_ID == 123456789:
        print("❌ MODERATOR_ROLE_ID not configured!")
        print("   Right-click your moderator role and copy Role ID")
    else:
        print("✅ MODERATOR_ROLE_ID configured")
    
    # Check if channel IDs are set
    channels = {
        'STATUS_CHANNEL_ID': STATUS_CHANNEL_ID,
        'ANNOUNCEMENTS_CHANNEL_ID': ANNOUNCEMENTS_CHANNEL_ID,
        'GUILD_CHANNEL_ID': GUILD_CHANNEL_ID,
        'QUEST_CHANNEL_ID': QUEST_CHANNEL_ID,
        'ADMIN_CHANNEL_ID': ADMIN_CHANNEL_ID,
        'LOG_CHANNEL_ID': LOG_CHANNEL_ID
    }
    
    configured_channels = 0
    for name, channel_id in channels.items():
        if channel_id == 123456789:
            print(f"❌ {name} not configured!")
        else:
            print(f"✅ {name} configured")
            configured_channels += 1
    
    print(f"\n📊 Configuration Summary:")
    print(f"   Configured channels: {configured_channels}/6")
    
    if configured_channels >= 3:
        print("🎉 Basic configuration complete!")
        print("🚀 You can now run: python discord_bot.py")
    else:
        print("⚠️  Please configure more channels before running the bot")

if __name__ == "__main__":
    test_configuration() 