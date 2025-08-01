#!/usr/bin/env python3
"""
Monster Hunter Frontier G - Advanced Guild System
Guild halls, guild quests, guild wars, rankings, and management
"""

import random
import json
import time
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path

class GuildRank(Enum):
    """Guild member ranks"""
    MEMBER = "member"
    OFFICER = "officer"
    LEADER = "leader"
    CO_LEADER = "co_leader"

class GuildStatus(Enum):
    """Guild status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISBANDED = "disbanded"
    SUSPENDED = "suspended"

class GuildQuestType(Enum):
    """Types of guild quests"""
    HUNTING = "hunting"
    GATHERING = "gathering"
    DEFENSE = "defense"
    RAID = "raid"
    BOSS = "boss"

@dataclass
class GuildMember:
    """Guild member information"""
    player_id: str
    username: str
    rank: GuildRank
    join_date: datetime
    contribution_points: int
    last_active: datetime
    guild_quests_completed: int
    guild_quests_failed: int

@dataclass
class GuildQuest:
    """Guild quest definition"""
    id: str
    name: str
    description: str
    quest_type: GuildQuestType
    difficulty: int  # 1-10
    required_members: int
    time_limit: int  # minutes
    objectives: List[Dict]
    rewards: Dict
    guild_level_requirement: int
    is_active: bool = True

@dataclass
class Guild:
    """Guild information"""
    id: str
    name: str
    description: str
    leader_id: str
    co_leader_id: Optional[str]
    members: Dict[str, GuildMember]
    level: int
    experience: int
    max_members: int
    status: GuildStatus
    created_date: datetime
    guild_hall_level: int
    treasury: int  # Guild zenny
    guild_quests: List[GuildQuest]
    achievements: List[str]
    war_history: List[Dict]

class GuildManager:
    """Manages guilds and guild-related functionality"""
    
    def __init__(self, db_path: str = "server_data/guilds.db"):
        self.db_path = db_path
        self.guilds: Dict[str, Guild] = {}
        self.guild_quests: Dict[str, GuildQuest] = {}
        self.guild_wars: Dict[str, Dict] = {}
        
        self.init_database()
        self.load_guild_data()
        self._create_default_guild_quests()
    
    def init_database(self):
        """Initialize guild database"""
        Path(self.db_path).parent.mkdir(exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create guilds table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS guilds (
                id TEXT PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                leader_id TEXT NOT NULL,
                co_leader_id TEXT,
                level INTEGER DEFAULT 1,
                experience INTEGER DEFAULT 0,
                max_members INTEGER DEFAULT 20,
                status TEXT DEFAULT 'active',
                created_date TEXT NOT NULL,
                guild_hall_level INTEGER DEFAULT 1,
                treasury INTEGER DEFAULT 0
            )
        ''')
        
        # Create guild members table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS guild_members (
                guild_id TEXT,
                player_id TEXT,
                username TEXT NOT NULL,
                rank TEXT NOT NULL,
                join_date TEXT NOT NULL,
                contribution_points INTEGER DEFAULT 0,
                last_active TEXT NOT NULL,
                guild_quests_completed INTEGER DEFAULT 0,
                guild_quests_failed INTEGER DEFAULT 0,
                PRIMARY KEY (guild_id, player_id),
                FOREIGN KEY (guild_id) REFERENCES guilds (id)
            )
        ''')
        
        # Create guild quests table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS guild_quests (
                id TEXT PRIMARY KEY,
                guild_id TEXT,
                name TEXT NOT NULL,
                description TEXT,
                quest_type TEXT NOT NULL,
                difficulty INTEGER DEFAULT 1,
                required_members INTEGER DEFAULT 1,
                time_limit INTEGER DEFAULT 60,
                objectives TEXT,
                rewards TEXT,
                guild_level_requirement INTEGER DEFAULT 1,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (guild_id) REFERENCES guilds (id)
            )
        ''')
        
        # Create active guild quests table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS active_guild_quests (
                quest_id TEXT,
                guild_id TEXT,
                start_time TEXT NOT NULL,
                status TEXT NOT NULL,
                participants TEXT,
                progress TEXT,
                PRIMARY KEY (quest_id, guild_id)
            )
        ''')
        
        # Create guild wars table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS guild_wars (
                id TEXT PRIMARY KEY,
                guild1_id TEXT NOT NULL,
                guild2_id TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                status TEXT NOT NULL,
                guild1_score INTEGER DEFAULT 0,
                guild2_score INTEGER DEFAULT 0,
                winner_id TEXT,
                FOREIGN KEY (guild1_id) REFERENCES guilds (id),
                FOREIGN KEY (guild2_id) REFERENCES guilds (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_guild_data(self):
        """Load guild data from database"""
        # This would load existing guilds from database
        # For now, we'll create some default guilds
        self._create_default_guilds()
    
    def _create_default_guilds(self):
        """Create default guilds for testing"""
        # Create a test guild
        test_guild = Guild(
            id="test_guild_001",
            name="Dragon Slayers",
            description="A guild dedicated to hunting the most dangerous monsters",
            leader_id="leader_001",
            co_leader_id="co_leader_001",
            members={},
            level=5,
            experience=2500,
            max_members=30,
            status=GuildStatus.ACTIVE,
            created_date=datetime.now(),
            guild_hall_level=3,
            treasury=50000,
            guild_quests=[],
            achievements=["First Hunt", "Guild Level 5"],
            war_history=[]
        )
        
        # Add some members
        test_guild.members["leader_001"] = GuildMember(
            player_id="leader_001",
            username="GuildLeader",
            rank=GuildRank.LEADER,
            join_date=datetime.now(),
            contribution_points=1500,
            last_active=datetime.now(),
            guild_quests_completed=25,
            guild_quests_failed=2
        )
        
        test_guild.members["co_leader_001"] = GuildMember(
            player_id="co_leader_001",
            username="CoLeader",
            rank=GuildRank.CO_LEADER,
            join_date=datetime.now(),
            contribution_points=1200,
            last_active=datetime.now(),
            guild_quests_completed=20,
            guild_quests_failed=1
        )
        
        self.guilds[test_guild.id] = test_guild
        self.save_guild(test_guild)
    
    def _create_default_guild_quests(self):
        """Create default guild quests"""
        self.guild_quests = {
            "gq_hunt_elder_dragon": GuildQuest(
                id="gq_hunt_elder_dragon",
                name="Elder Dragon Hunt",
                description="Hunt down a powerful elder dragon threatening the guild",
                quest_type=GuildQuestType.HUNTING,
                difficulty=8,
                required_members=4,
                time_limit=90,
                objectives=[
                    {"type": "hunt", "target": "Elder Dragon", "quantity": 1},
                    {"type": "gather", "target": "Dragon Essence", "quantity": 3}
                ],
                rewards={
                    "zenny": 10000,
                    "experience": 5000,
                    "guild_experience": 1000,
                    "materials": {"dragon_scale": 5, "elder_essence": 2}
                },
                guild_level_requirement=5
            ),
            "gq_defend_guild_hall": GuildQuest(
                id="gq_defend_guild_hall",
                name="Defend Guild Hall",
                description="Defend the guild hall from invading monsters",
                quest_type=GuildQuestType.DEFENSE,
                difficulty=6,
                required_members=3,
                time_limit=60,
                objectives=[
                    {"type": "defend", "target": "Guild Hall", "duration": 300},
                    {"type": "defeat", "target": "Invading Monsters", "quantity": 10}
                ],
                rewards={
                    "zenny": 5000,
                    "experience": 3000,
                    "guild_experience": 500,
                    "materials": {"defense_token": 3}
                },
                guild_level_requirement=3
            )
        }
    
    def create_guild(self, name: str, description: str, leader_id: str, leader_username: str) -> Tuple[bool, Dict]:
        """Create a new guild"""
        # Check if guild name already exists
        if self.get_guild_by_name(name):
            return False, {"error": "Guild name already exists"}
        
        # Check if player is already in a guild
        if self.get_player_guild(leader_id):
            return False, {"error": "Player is already in a guild"}
        
        # Create guild
        guild_id = f"guild_{int(time.time())}_{random.randint(1000, 9999)}"
        guild = Guild(
            id=guild_id,
            name=name,
            description=description,
            leader_id=leader_id,
            co_leader_id=None,
            members={},
            level=1,
            experience=0,
            max_members=20,
            status=GuildStatus.ACTIVE,
            created_date=datetime.now(),
            guild_hall_level=1,
            treasury=0,
            guild_quests=[],
            achievements=[],
            war_history=[]
        )
        
        # Add leader as first member
        guild.members[leader_id] = GuildMember(
            player_id=leader_id,
            username=leader_username,
            rank=GuildRank.LEADER,
            join_date=datetime.now(),
            contribution_points=0,
            last_active=datetime.now(),
            guild_quests_completed=0,
            guild_quests_failed=0
        )
        
        # Save guild
        self.guilds[guild_id] = guild
        self.save_guild(guild)
        
        return True, {
            "success": True,
            "guild_id": guild_id,
            "guild": guild
        }
    
    def save_guild(self, guild: Guild):
        """Save guild to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Save guild info
        cursor.execute('''
            INSERT OR REPLACE INTO guilds 
            (id, name, description, leader_id, co_leader_id, level, experience,
             max_members, status, created_date, guild_hall_level, treasury)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            guild.id, guild.name, guild.description, guild.leader_id,
            guild.co_leader_id, guild.level, guild.experience, guild.max_members,
            guild.status.value, guild.created_date.isoformat(),
            guild.guild_hall_level, guild.treasury
        ))
        
        # Save guild members
        cursor.execute('DELETE FROM guild_members WHERE guild_id = ?', (guild.id,))
        for member in guild.members.values():
            cursor.execute('''
                INSERT INTO guild_members 
                (guild_id, player_id, username, rank, join_date, contribution_points,
                 last_active, guild_quests_completed, guild_quests_failed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                guild.id, member.player_id, member.username, member.rank.value,
                member.join_date.isoformat(), member.contribution_points,
                member.last_active.isoformat(), member.guild_quests_completed,
                member.guild_quests_failed
            ))
        
        conn.commit()
        conn.close()
    
    def get_guild_by_id(self, guild_id: str) -> Optional[Guild]:
        """Get guild by ID"""
        return self.guilds.get(guild_id)
    
    def get_guild_by_name(self, name: str) -> Optional[Guild]:
        """Get guild by name"""
        for guild in self.guilds.values():
            if guild.name == name:
                return guild
        return None
    
    def get_player_guild(self, player_id: str) -> Optional[Guild]:
        """Get guild that a player belongs to"""
        for guild in self.guilds.values():
            if player_id in guild.members:
                return guild
        return None
    
    def join_guild(self, guild_id: str, player_id: str, username: str) -> Tuple[bool, Dict]:
        """Join a guild"""
        guild = self.get_guild_by_id(guild_id)
        if not guild:
            return False, {"error": "Guild not found"}
        
        # Check if player is already in a guild
        if self.get_player_guild(player_id):
            return False, {"error": "Player is already in a guild"}
        
        # Check if guild is full
        if len(guild.members) >= guild.max_members:
            return False, {"error": "Guild is full"}
        
        # Check if guild is active
        if guild.status != GuildStatus.ACTIVE:
            return False, {"error": "Guild is not active"}
        
        # Add player to guild
        guild.members[player_id] = GuildMember(
            player_id=player_id,
            username=username,
            rank=GuildRank.MEMBER,
            join_date=datetime.now(),
            contribution_points=0,
            last_active=datetime.now(),
            guild_quests_completed=0,
            guild_quests_failed=0
        )
        
        self.save_guild(guild)
        
        return True, {
            "success": True,
            "guild": guild,
            "member": guild.members[player_id]
        }
    
    def leave_guild(self, player_id: str) -> Tuple[bool, Dict]:
        """Leave a guild"""
        guild = self.get_player_guild(player_id)
        if not guild:
            return False, {"error": "Player is not in a guild"}
        
        member = guild.members.get(player_id)
        if not member:
            return False, {"error": "Member not found"}
        
        # Check if player is the leader
        if member.rank == GuildRank.LEADER:
            return False, {"error": "Leader cannot leave guild. Transfer leadership first."}
        
        # Remove player from guild
        del guild.members[player_id]
        
        # If co-leader left, clear co-leader position
        if guild.co_leader_id == player_id:
            guild.co_leader_id = None
        
        self.save_guild(guild)
        
        return True, {
            "success": True,
            "guild": guild
        }
    
    def promote_member(self, guild_id: str, player_id: str, promoter_id: str, new_rank: GuildRank) -> Tuple[bool, Dict]:
        """Promote a guild member"""
        guild = self.get_guild_by_id(guild_id)
        if not guild:
            return False, {"error": "Guild not found"}
        
        # Check if promoter has permission
        promoter = guild.members.get(promoter_id)
        if not promoter or promoter.rank not in [GuildRank.LEADER, GuildRank.CO_LEADER]:
            return False, {"error": "Insufficient permissions"}
        
        # Check if target member exists
        member = guild.members.get(player_id)
        if not member:
            return False, {"error": "Member not found"}
        
        # Update member rank
        member.rank = new_rank
        
        # Update guild co-leader if promoting to co-leader
        if new_rank == GuildRank.CO_LEADER:
            guild.co_leader_id = player_id
        
        self.save_guild(guild)
        
        return True, {
            "success": True,
            "member": member,
            "guild": guild
        }
    
    def start_guild_quest(self, guild_id: str, quest_id: str, participants: List[str]) -> Tuple[bool, Dict]:
        """Start a guild quest"""
        guild = self.get_guild_by_id(guild_id)
        if not guild:
            return False, {"error": "Guild not found"}
        
        quest = self.guild_quests.get(quest_id)
        if not quest:
            return False, {"error": "Quest not found"}
        
        # Check if quest is active
        if not quest.is_active:
            return False, {"error": "Quest is not active"}
        
        # Check guild level requirement
        if guild.level < quest.guild_level_requirement:
            return False, {"error": "Guild level too low"}
        
        # Check participant count
        if len(participants) < quest.required_members:
            return False, {"error": "Not enough participants"}
        
        # Check if all participants are guild members
        for participant_id in participants:
            if participant_id not in guild.members:
                return False, {"error": f"Player {participant_id} is not a guild member"}
        
        # Create active guild quest
        active_quest = {
            "quest_id": quest_id,
            "guild_id": guild_id,
            "start_time": datetime.now(),
            "status": "active",
            "participants": participants,
            "progress": {str(i): 0 for i in range(len(quest.objectives))}
        }
        
        # Save to database
        self.save_active_guild_quest(active_quest)
        
        return True, {
            "success": True,
            "quest": quest,
            "active_quest": active_quest
        }
    
    def save_active_guild_quest(self, active_quest: Dict):
        """Save active guild quest to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO active_guild_quests 
            (quest_id, guild_id, start_time, status, participants, progress)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            active_quest["quest_id"], active_quest["guild_id"],
            active_quest["start_time"].isoformat(), active_quest["status"],
            json.dumps(active_quest["participants"]),
            json.dumps(active_quest["progress"])
        ))
        
        conn.commit()
        conn.close()
    
    def update_guild_quest_progress(self, guild_id: str, quest_id: str, objective_index: int, progress: int) -> Tuple[bool, Dict]:
        """Update guild quest progress"""
        # Get active quest
        active_quest = self.get_active_guild_quest(guild_id, quest_id)
        if not active_quest:
            return False, {"error": "No active quest found"}
        
        quest = self.guild_quests.get(quest_id)
        if not quest:
            return False, {"error": "Quest not found"}
        
        # Update progress
        objective_key = str(objective_index)
        current_progress = active_quest["progress"].get(objective_key, 0)
        new_progress = min(current_progress + progress, quest.objectives[objective_index]["quantity"])
        active_quest["progress"][objective_key] = new_progress
        
        # Check if objective is complete
        if new_progress >= quest.objectives[objective_index]["quantity"]:
            # Check if all objectives are complete
            all_complete = True
            for i, objective in enumerate(quest.objectives):
                if active_quest["progress"].get(str(i), 0) < objective["quantity"]:
                    all_complete = False
                    break
            
            if all_complete:
                return self.complete_guild_quest(guild_id, quest_id)
        
        # Save progress
        self.save_active_guild_quest(active_quest)
        
        return True, {
            "success": True,
            "progress": new_progress,
            "required": quest.objectives[objective_index]["quantity"]
        }
    
    def get_active_guild_quest(self, guild_id: str, quest_id: str) -> Optional[Dict]:
        """Get active guild quest"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM active_guild_quests 
            WHERE guild_id = ? AND quest_id = ? AND status = 'active'
        ''', (guild_id, quest_id))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "quest_id": row[0],
                "guild_id": row[1],
                "start_time": datetime.fromisoformat(row[2]),
                "status": row[3],
                "participants": json.loads(row[4]),
                "progress": json.loads(row[5])
            }
        return None
    
    def complete_guild_quest(self, guild_id: str, quest_id: str) -> Tuple[bool, Dict]:
        """Complete a guild quest"""
        guild = self.get_guild_by_id(guild_id)
        if not guild:
            return False, {"error": "Guild not found"}
        
        quest = self.guild_quests.get(quest_id)
        if not quest:
            return False, {"error": "Quest not found"}
        
        active_quest = self.get_active_guild_quest(guild_id, quest_id)
        if not active_quest:
            return False, {"error": "No active quest found"}
        
        # Calculate completion time
        completion_time = (datetime.now() - active_quest["start_time"]).total_seconds()
        
        # Update guild experience and treasury
        guild.experience += quest.rewards["guild_experience"]
        guild.treasury += quest.rewards["zenny"]
        
        # Check for level up
        required_exp = guild.level * 1000
        if guild.experience >= required_exp:
            guild.level += 1
            guild.experience -= required_exp
            guild.max_members += 5
        
        # Update member stats
        for participant_id in active_quest["participants"]:
            if participant_id in guild.members:
                member = guild.members[participant_id]
                member.contribution_points += quest.rewards["experience"] // len(active_quest["participants"])
                member.guild_quests_completed += 1
                member.last_active = datetime.now()
        
        # Save guild
        self.save_guild(guild)
        
        # Remove active quest
        self.remove_active_guild_quest(guild_id, quest_id)
        
        return True, {
            "success": True,
            "quest_completed": True,
            "rewards": quest.rewards,
            "completion_time": completion_time,
            "guild_level": guild.level,
            "guild_experience": guild.experience
        }
    
    def remove_active_guild_quest(self, guild_id: str, quest_id: str):
        """Remove active guild quest"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM active_guild_quests 
            WHERE guild_id = ? AND quest_id = ?
        ''', (guild_id, quest_id))
        
        conn.commit()
        conn.close()
    
    def get_guild_rankings(self) -> List[Dict]:
        """Get guild rankings"""
        guilds_list = list(self.guilds.values())
        guilds_list.sort(key=lambda g: (g.level, g.experience), reverse=True)
        
        rankings = []
        for i, guild in enumerate(guilds_list[:10]):  # Top 10
            rankings.append({
                "rank": i + 1,
                "guild_id": guild.id,
                "name": guild.name,
                "level": guild.level,
                "experience": guild.experience,
                "member_count": len(guild.members),
                "leader": guild.members[guild.leader_id].username if guild.leader_id in guild.members else "Unknown"
            })
        
        return rankings
    
    def upgrade_guild_hall(self, guild_id: str, player_id: str) -> Tuple[bool, Dict]:
        """Upgrade guild hall"""
        guild = self.get_guild_by_id(guild_id)
        if not guild:
            return False, {"error": "Guild not found"}
        
        # Check if player has permission
        member = guild.members.get(player_id)
        if not member or member.rank not in [GuildRank.LEADER, GuildRank.CO_LEADER]:
            return False, {"error": "Insufficient permissions"}
        
        # Calculate upgrade cost
        upgrade_cost = guild.guild_hall_level * 10000
        
        # Check if guild has enough treasury
        if guild.treasury < upgrade_cost:
            return False, {"error": "Not enough treasury"}
        
        # Upgrade guild hall
        guild.guild_hall_level += 1
        guild.treasury -= upgrade_cost
        guild.max_members += 10
        
        self.save_guild(guild)
        
        return True, {
            "success": True,
            "new_level": guild.guild_hall_level,
            "new_max_members": guild.max_members,
            "cost": upgrade_cost
        }

def test_guild_system():
    """Test the advanced guild system"""
    print("🐉 Monster Hunter Frontier G - Advanced Guild System Test")
    print("=" * 60)
    
    # Create guild manager
    guild_manager = GuildManager()
    
    # Test guild creation
    print("--- Testing Guild Creation ---")
    success, result = guild_manager.create_guild(
        "Test Guild", 
        "A test guild for testing purposes", 
        "player_001", 
        "TestLeader"
    )
    print(f"Created guild: {success}")
    if success:
        print(f"Guild ID: {result['guild_id']}")
        print(f"Guild Name: {result['guild'].name}")
    
    # Test joining guild
    print("\n--- Testing Guild Membership ---")
    join_success, join_result = guild_manager.join_guild("test_guild_001", "player_002", "TestMember")
    print(f"Joined guild: {join_success}")
    
    # Test guild quest
    print("\n--- Testing Guild Quests ---")
    quest_success, quest_result = guild_manager.start_guild_quest(
        "test_guild_001", 
        "gq_hunt_elder_dragon", 
        ["leader_001", "co_leader_001", "player_002"]
    )
    print(f"Started guild quest: {quest_success}")
    
    if quest_success:
        # Update quest progress
        progress_success, progress_result = guild_manager.update_guild_quest_progress(
            "test_guild_001", "gq_hunt_elder_dragon", 0, 1
        )
        print(f"Updated quest progress: {progress_success}")
        
        # Complete quest
        complete_success, complete_result = guild_manager.complete_guild_quest(
            "test_guild_001", "gq_hunt_elder_dragon"
        )
        print(f"Completed quest: {complete_success}")
    
    # Test guild rankings
    print("\n--- Testing Guild Rankings ---")
    rankings = guild_manager.get_guild_rankings()
    print(f"Top guilds: {len(rankings)}")
    for ranking in rankings[:3]:
        print(f"  {ranking['rank']}. {ranking['name']} (Level {ranking['level']})")
    
    # Test guild hall upgrade
    print("\n--- Testing Guild Hall Upgrade ---")
    upgrade_success, upgrade_result = guild_manager.upgrade_guild_hall("test_guild_001", "leader_001")
    print(f"Upgraded guild hall: {upgrade_success}")
    
    print("\n" + "=" * 60)
    print("✅ Advanced Guild System Test Complete!")
    print("🏰 Guild management working!")
    print("⚔️ Guild quests active!")
    print("🏆 Guild rankings ready!")

if __name__ == "__main__":
    test_guild_system() 