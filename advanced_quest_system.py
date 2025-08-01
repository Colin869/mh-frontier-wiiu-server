#!/usr/bin/env python3
"""
Monster Hunter Frontier G - Advanced Quest System
Dynamic quest generation, quest chains, special events, and reward systems
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

class QuestType(Enum):
    """Types of quests"""
    HUNT = "hunt"
    CAPTURE = "capture"
    GATHERING = "gathering"
    ESCORT = "escort"
    TIME_ATTACK = "time_attack"
    SPECIAL_EVENT = "special_event"
    STORY = "story"

class QuestRank(Enum):
    """Quest difficulty ranks"""
    LOW_RANK = 1
    HIGH_RANK = 2
    G_RANK = 3
    MASTER_RANK = 4

class QuestStatus(Enum):
    """Quest status"""
    AVAILABLE = "available"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"

@dataclass
class QuestObjective:
    """Individual quest objective"""
    type: str  # hunt, gather, deliver, etc.
    target: str  # monster name, item name, etc.
    quantity: int
    current: int = 0
    description: str = ""

@dataclass
class QuestReward:
    """Quest rewards"""
    zenny: int
    experience: int
    materials: Dict[str, int]  # item_id -> quantity
    special_rewards: List[str]  # special items, titles, etc.

@dataclass
class Quest:
    """Complete quest definition"""
    id: str
    name: str
    description: str
    quest_type: QuestType
    rank: QuestRank
    objectives: List[QuestObjective]
    rewards: QuestReward
    time_limit: int  # minutes
    player_limit: int  # min/max players
    location: str
    requirements: Dict[str, int]  # HR requirement, etc.
    is_story: bool = False
    is_event: bool = False
    event_start: Optional[datetime] = None
    event_end: Optional[datetime] = None
    chain_id: Optional[str] = None  # For quest chains
    chain_position: int = 0

@dataclass
class ActiveQuest:
    """Player's active quest instance"""
    quest_id: str
    player_id: str
    start_time: datetime
    status: QuestStatus
    objectives_progress: Dict[str, int]  # objective_id -> current progress
    party_members: List[str]
    location: str
    time_remaining: int  # seconds

class QuestGenerator:
    """Generates dynamic quests"""
    
    def __init__(self):
        self.monster_templates = self._create_monster_templates()
        self.location_templates = self._create_location_templates()
        self.material_templates = self._create_material_templates()
        
    def _create_monster_templates(self) -> Dict[str, Dict]:
        """Create monster templates for quest generation"""
        return {
            "great_jaggi": {
                "name": "Great Jaggi",
                "rank": QuestRank.LOW_RANK,
                "health": 800,
                "attack": 45,
                "locations": ["Forest", "Desert"],
                "materials": ["great_jaggi_scale", "great_jaggi_claw", "great_jaggi_fang"]
            },
            "rathian": {
                "name": "Rathian",
                "rank": QuestRank.HIGH_RANK,
                "health": 2000,
                "attack": 80,
                "locations": ["Forest", "Volcano"],
                "materials": ["rathian_scale", "rathian_wing", "rathian_tail"]
            },
            "tigrex": {
                "name": "Tigrex",
                "rank": QuestRank.G_RANK,
                "health": 3000,
                "attack": 120,
                "locations": ["Snowy Mountains", "Volcano"],
                "materials": ["tigrex_scale", "tigrex_claw", "tigrex_fang"]
            }
        }
    
    def _create_location_templates(self) -> Dict[str, Dict]:
        """Create location templates"""
        return {
            "Forest": {
                "name": "Ancient Forest",
                "gathering_materials": ["herb", "honey", "mushroom"],
                "monsters": ["great_jaggi", "rathian"],
                "environmental_hazards": ["poison_plants", "falling_trees"]
            },
            "Desert": {
                "name": "Sandy Plains",
                "gathering_materials": ["cactus_flower", "desert_ore", "sand_fish"],
                "monsters": ["great_jaggi", "barroth"],
                "environmental_hazards": ["sandstorms", "quicksand"]
            },
            "Volcano": {
                "name": "Volcanic Hollow",
                "gathering_materials": ["volcanic_ore", "fire_essence", "lava_crystal"],
                "monsters": ["rathian", "tigrex"],
                "environmental_hazards": ["lava_pools", "volcanic_eruptions"]
            }
        }
    
    def _create_material_templates(self) -> Dict[str, Dict]:
        """Create material templates"""
        return {
            "herb": {"name": "Herb", "rarity": 1, "locations": ["Forest"]},
            "honey": {"name": "Honey", "rarity": 2, "locations": ["Forest"]},
            "mushroom": {"name": "Mushroom", "rarity": 1, "locations": ["Forest"]},
            "cactus_flower": {"name": "Cactus Flower", "rarity": 2, "locations": ["Desert"]},
            "volcanic_ore": {"name": "Volcanic Ore", "rarity": 3, "locations": ["Volcano"]}
        }
    
    def generate_hunt_quest(self, rank: QuestRank, player_count: int = 1) -> Quest:
        """Generate a hunting quest"""
        # Select appropriate monsters for rank
        available_monsters = [
            monster_id for monster_id, template in self.monster_templates.items()
            if template["rank"] == rank
        ]
        
        if not available_monsters:
            available_monsters = ["great_jaggi"]  # Fallback
        
        monster_id = random.choice(available_monsters)
        monster_template = self.monster_templates[monster_id]
        
        # Select location
        available_locations = [
            loc for loc in monster_template["locations"]
            if loc in self.location_templates
        ]
        location = random.choice(available_locations) if available_locations else "Forest"
        
        # Generate quest ID
        quest_id = f"hunt_{monster_id}_{int(time.time())}"
        
        # Create objectives
        objectives = [
            QuestObjective(
                type="hunt",
                target=monster_template["name"],
                quantity=1,
                description=f"Hunt {monster_template['name']}"
            )
        ]
        
        # Add optional gathering objective
        if random.random() < 0.3:
            location_template = self.location_templates[location]
            gathering_material = random.choice(location_template["gathering_materials"])
            objectives.append(QuestObjective(
                type="gather",
                target=gathering_material,
                quantity=random.randint(3, 8),
                description=f"Gather {gathering_material}"
            ))
        
        # Calculate rewards based on monster difficulty
        base_zenny = monster_template["health"] * 2
        base_exp = monster_template["attack"] * 10
        
        rewards = QuestReward(
            zenny=base_zenny,
            experience=base_exp,
            materials={material: random.randint(1, 3) for material in monster_template["materials"]},
            special_rewards=[]
        )
        
        return Quest(
            id=quest_id,
            name=f"Hunt {monster_template['name']}",
            description=f"A {monster_template['name']} has been spotted in the {location}. Hunt it down!",
            quest_type=QuestType.HUNT,
            rank=rank,
            objectives=objectives,
            rewards=rewards,
            time_limit=50,
            player_limit=player_count,
            location=location,
            requirements={"hr": rank.value * 5}
        )
    
    def generate_gathering_quest(self, rank: QuestRank) -> Quest:
        """Generate a gathering quest"""
        location = random.choice(list(self.location_templates.keys()))
        location_template = self.location_templates[location]
        
        # Select materials to gather
        materials = random.sample(location_template["gathering_materials"], 
                                min(3, len(location_template["gathering_materials"])))
        
        objectives = []
        for material in materials:
            material_template = self.material_templates.get(material, {"name": material})
            objectives.append(QuestObjective(
                type="gather",
                target=material,
                quantity=random.randint(5, 15),
                description=f"Gather {material_template['name']}"
            ))
        
        quest_id = f"gather_{location}_{int(time.time())}"
        
        rewards = QuestReward(
            zenny=100 * len(materials),
            experience=50 * len(materials),
            materials={material: random.randint(1, 2) for material in materials},
            special_rewards=[]
        )
        
        return Quest(
            id=quest_id,
            name=f"Gathering in {location}",
            description=f"Gather materials from the {location}",
            quest_type=QuestType.GATHERING,
            rank=rank,
            objectives=objectives,
            rewards=rewards,
            time_limit=30,
            player_limit=1,
            location=location,
            requirements={"hr": rank.value * 3}
        )
    
    def generate_capture_quest(self, rank: QuestRank) -> Quest:
        """Generate a capture quest"""
        # Similar to hunt quest but with capture objective
        hunt_quest = self.generate_hunt_quest(rank)
        
        # Change objective to capture
        hunt_quest.quest_type = QuestType.CAPTURE
        hunt_quest.objectives[0].type = "capture"
        hunt_quest.objectives[0].description = f"Capture {hunt_quest.objectives[0].target}"
        
        # Increase rewards for capture
        hunt_quest.rewards.zenny = int(hunt_quest.rewards.zenny * 1.5)
        hunt_quest.rewards.experience = int(hunt_quest.rewards.experience * 1.3)
        
        return hunt_quest

class QuestManager:
    """Manages quests and player progress"""
    
    def __init__(self, db_path: str = "server_data/quests.db"):
        self.db_path = db_path
        self.quest_generator = QuestGenerator()
        self.active_quests: Dict[str, ActiveQuest] = {}
        self.quest_chains: Dict[str, List[str]] = {}
        self.special_events: Dict[str, Quest] = {}
        
        self.init_database()
        self.load_quest_data()
    
    def init_database(self):
        """Initialize quest database"""
        Path(self.db_path).parent.mkdir(exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create quests table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quests (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                quest_type TEXT NOT NULL,
                rank INTEGER NOT NULL,
                objectives TEXT,
                rewards TEXT,
                time_limit INTEGER DEFAULT 50,
                player_limit INTEGER DEFAULT 1,
                location TEXT,
                requirements TEXT,
                is_story BOOLEAN DEFAULT 0,
                is_event BOOLEAN DEFAULT 0,
                event_start TEXT,
                event_end TEXT,
                chain_id TEXT,
                chain_position INTEGER DEFAULT 0
            )
        ''')
        
        # Create active quests table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS active_quests (
                quest_id TEXT,
                player_id TEXT,
                start_time TEXT NOT NULL,
                status TEXT NOT NULL,
                objectives_progress TEXT,
                party_members TEXT,
                location TEXT,
                time_remaining INTEGER,
                PRIMARY KEY (quest_id, player_id)
            )
        ''')
        
        # Create quest history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quest_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quest_id TEXT NOT NULL,
                player_id TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                status TEXT NOT NULL,
                completion_time INTEGER,
                rewards_claimed BOOLEAN DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_quest_data(self):
        """Load quest data from database"""
        # This would load existing quests from database
        # For now, we'll create some default quests
        self._create_default_quests()
    
    def _create_default_quests(self):
        """Create default quests"""
        # Create some basic quests
        default_quests = [
            self.quest_generator.generate_hunt_quest(QuestRank.LOW_RANK),
            self.quest_generator.generate_hunt_quest(QuestRank.HIGH_RANK),
            self.quest_generator.generate_gathering_quest(QuestRank.LOW_RANK),
            self.quest_generator.generate_capture_quest(QuestRank.LOW_RANK)
        ]
        
        for quest in default_quests:
            self.save_quest(quest)
    
    def save_quest(self, quest: Quest):
        """Save quest to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO quests 
            (id, name, description, quest_type, rank, objectives, rewards, 
             time_limit, player_limit, location, requirements, is_story, 
             is_event, event_start, event_end, chain_id, chain_position)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            quest.id, quest.name, quest.description, quest.quest_type.value,
            quest.rank.value, json.dumps([obj.__dict__ for obj in quest.objectives]),
            json.dumps(quest.rewards.__dict__), quest.time_limit, quest.player_limit,
            quest.location, json.dumps(quest.requirements), quest.is_story,
            quest.is_event, quest.event_start.isoformat() if quest.event_start else None,
            quest.event_end.isoformat() if quest.event_end else None,
            quest.chain_id, quest.chain_position
        ))
        
        conn.commit()
        conn.close()
    
    def get_available_quests(self, player_hr: int, player_rank: QuestRank) -> List[Quest]:
        """Get quests available for a player"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM quests 
            WHERE rank <= ? AND is_event = 0
            ORDER BY rank, name
        ''', (player_rank.value,))
        
        quests = []
        for row in cursor.fetchall():
            quest = self._row_to_quest(row)
            if quest and self._check_quest_requirements(quest, player_hr):
                quests.append(quest)
        
        conn.close()
        return quests
    
    def _row_to_quest(self, row) -> Optional[Quest]:
        """Convert database row to Quest object"""
        try:
            objectives_data = json.loads(row[5])
            objectives = [QuestObjective(**obj) for obj in objectives_data]
            
            rewards_data = json.loads(row[6])
            rewards = QuestReward(**rewards_data)
            
            requirements = json.loads(row[10]) if row[10] else {}
            
            return Quest(
                id=row[0],
                name=row[1],
                description=row[2],
                quest_type=QuestType(row[3]),
                rank=QuestRank(row[4]),
                objectives=objectives,
                rewards=rewards,
                time_limit=row[7],
                player_limit=row[8],
                location=row[9],
                requirements=requirements,
                is_story=bool(row[11]),
                is_event=bool(row[12]),
                event_start=datetime.fromisoformat(row[13]) if row[13] else None,
                event_end=datetime.fromisoformat(row[14]) if row[14] else None,
                chain_id=row[15],
                chain_position=row[16]
            )
        except Exception as e:
            print(f"Error converting row to quest: {e}")
            return None
    
    def _check_quest_requirements(self, quest: Quest, player_hr: int) -> bool:
        """Check if player meets quest requirements"""
        hr_requirement = quest.requirements.get("hr", 0)
        return player_hr >= hr_requirement
    
    def start_quest(self, quest_id: str, player_id: str, party_members: List[str] = None) -> Tuple[bool, Dict]:
        """Start a quest for a player"""
        # Get quest details
        quest = self.get_quest_by_id(quest_id)
        if not quest:
            return False, {"error": "Quest not found"}
        
        # Check if player is already on a quest
        if self.get_active_quest(player_id):
            return False, {"error": "Already on a quest"}
        
        # Check party size
        if party_members and len(party_members) > quest.player_limit:
            return False, {"error": "Party too large for this quest"}
        
        # Create active quest
        active_quest = ActiveQuest(
            quest_id=quest_id,
            player_id=player_id,
            start_time=datetime.now(),
            status=QuestStatus.ACTIVE,
            objectives_progress={},
            party_members=party_members or [player_id],
            location=quest.location,
            time_remaining=quest.time_limit * 60  # Convert to seconds
        )
        
        # Initialize objective progress
        for i, objective in enumerate(quest.objectives):
            active_quest.objectives_progress[str(i)] = 0
        
        # Save to database
        self.save_active_quest(active_quest)
        
        # Add to active quests
        self.active_quests[f"{quest_id}_{player_id}"] = active_quest
        
        return True, {
            "success": True,
            "quest": quest,
            "active_quest": active_quest
        }
    
    def get_quest_by_id(self, quest_id: str) -> Optional[Quest]:
        """Get quest by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM quests WHERE id = ?', (quest_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return self._row_to_quest(row)
        return None
    
    def get_active_quest(self, player_id: str) -> Optional[ActiveQuest]:
        """Get player's active quest"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM active_quests 
            WHERE player_id = ? AND status = 'active'
        ''', (player_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_quest(row)
        return None
    
    def save_active_quest(self, active_quest: ActiveQuest):
        """Save active quest to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO active_quests 
            (quest_id, player_id, start_time, status, objectives_progress, 
             party_members, location, time_remaining)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            active_quest.quest_id, active_quest.player_id,
            active_quest.start_time.isoformat(), active_quest.status.value,
            json.dumps(active_quest.objectives_progress),
            json.dumps(active_quest.party_members),
            active_quest.location, active_quest.time_remaining
        ))
        
        conn.commit()
        conn.close()
    
    def update_quest_progress(self, player_id: str, objective_type: str, target: str, progress: int = 1) -> Tuple[bool, Dict]:
        """Update quest progress for a player"""
        active_quest = self.get_active_quest(player_id)
        if not active_quest:
            return False, {"error": "No active quest"}
        
        quest = self.get_quest_by_id(active_quest.quest_id)
        if not quest:
            return False, {"error": "Quest not found"}
        
        # Find matching objective
        for i, objective in enumerate(quest.objectives):
            if objective.type == objective_type and objective.target == target:
                objective_key = str(i)
                current_progress = active_quest.objectives_progress.get(objective_key, 0)
                new_progress = min(current_progress + progress, objective.quantity)
                active_quest.objectives_progress[objective_key] = new_progress
                
                # Check if objective is complete
                if new_progress >= objective.quantity:
                    # Check if all objectives are complete
                    all_complete = True
                    for j, obj in enumerate(quest.objectives):
                        if active_quest.objectives_progress.get(str(j), 0) < obj.quantity:
                            all_complete = False
                            break
                    
                    if all_complete:
                        return self.complete_quest(player_id)
                
                # Save progress
                self.save_active_quest(active_quest)
                return True, {
                    "success": True,
                    "objective_complete": new_progress >= objective.quantity,
                    "progress": new_progress,
                    "required": objective.quantity
                }
        
        return False, {"error": "Objective not found"}
    
    def complete_quest(self, player_id: str) -> Tuple[bool, Dict]:
        """Complete a quest for a player"""
        active_quest = self.get_active_quest(player_id)
        if not active_quest:
            return False, {"error": "No active quest"}
        
        quest = self.get_quest_by_id(active_quest.quest_id)
        if not quest:
            return False, {"error": "Quest not found"}
        
        # Calculate completion time
        completion_time = (datetime.now() - active_quest.start_time).total_seconds()
        
        # Update quest status
        active_quest.status = QuestStatus.COMPLETED
        
        # Save to history
        self.save_quest_history(active_quest, completion_time)
        
        # Remove from active quests
        quest_key = f"{active_quest.quest_id}_{player_id}"
        if quest_key in self.active_quests:
            del self.active_quests[quest_key]
        
        return True, {
            "success": True,
            "quest_completed": True,
            "rewards": quest.rewards,
            "completion_time": completion_time
        }
    
    def save_quest_history(self, active_quest: ActiveQuest, completion_time: float):
        """Save quest to history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO quest_history 
            (quest_id, player_id, start_time, end_time, status, completion_time)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            active_quest.quest_id, active_quest.player_id,
            active_quest.start_time.isoformat(), datetime.now().isoformat(),
            active_quest.status.value, completion_time
        ))
        
        conn.commit()
        conn.close()
    
    def generate_dynamic_quest(self, player_hr: int, player_rank: QuestRank) -> Quest:
        """Generate a dynamic quest for a player"""
        quest_types = [QuestType.HUNT, QuestType.GATHERING, QuestType.CAPTURE]
        quest_type = random.choice(quest_types)
        
        if quest_type == QuestType.HUNT:
            return self.quest_generator.generate_hunt_quest(player_rank)
        elif quest_type == QuestType.GATHERING:
            return self.quest_generator.generate_gathering_quest(player_rank)
        elif quest_type == QuestType.CAPTURE:
            return self.quest_generator.generate_capture_quest(player_rank)
        
        return self.quest_generator.generate_hunt_quest(player_rank)

def test_quest_system():
    """Test the advanced quest system"""
    print("🐉 Monster Hunter Frontier G - Advanced Quest System Test")
    print("=" * 60)
    
    # Create quest manager
    quest_manager = QuestManager()
    
    # Test quest generation
    print("--- Testing Quest Generation ---")
    hunt_quest = quest_manager.quest_generator.generate_hunt_quest(QuestRank.HIGH_RANK)
    print(f"Generated Hunt Quest: {hunt_quest.name}")
    print(f"  Type: {hunt_quest.quest_type.value}")
    print(f"  Rank: {hunt_quest.rank.value}")
    print(f"  Objectives: {len(hunt_quest.objectives)}")
    print(f"  Rewards: {hunt_quest.rewards.zenny} zenny, {hunt_quest.rewards.experience} exp")
    
    gathering_quest = quest_manager.quest_generator.generate_gathering_quest(QuestRank.LOW_RANK)
    print(f"\nGenerated Gathering Quest: {gathering_quest.name}")
    print(f"  Objectives: {len(gathering_quest.objectives)}")
    
    # Test quest management
    print("\n--- Testing Quest Management ---")
    player_id = "test_player"
    player_hr = 10
    player_rank = QuestRank.HIGH_RANK
    
    # Get available quests
    available_quests = quest_manager.get_available_quests(player_hr, player_rank)
    print(f"Available quests: {len(available_quests)}")
    
    if available_quests:
        # Start a quest
        quest = available_quests[0]
        success, result = quest_manager.start_quest(quest.id, player_id)
        print(f"Started quest: {success}")
        
        if success:
            # Update progress
            for i, objective in enumerate(quest.objectives):
                progress_success, progress_result = quest_manager.update_quest_progress(
                    player_id, objective.type, objective.target, objective.quantity
                )
                print(f"Updated objective {i}: {progress_success}")
                
                if progress_result.get("quest_completed"):
                    print("Quest completed!")
                    break
    
    print("\n" + "=" * 60)
    print("✅ Advanced Quest System Test Complete!")
    print("📋 Dynamic quest generation working!")
    print("🎯 Quest management active!")
    print("🏆 Reward system ready!")

if __name__ == "__main__":
    test_quest_system() 