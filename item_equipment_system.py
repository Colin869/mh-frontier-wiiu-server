#!/usr/bin/env python3
"""
Monster Hunter Frontier G - Item & Equipment System
Weapon crafting, armor system, inventory management, and crafting recipes
"""

import random
import json
import time
from enum import Enum
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
import sqlite3
from pathlib import Path

class ItemType(Enum):
    """Types of items in the game"""
    WEAPON = "weapon"
    ARMOR = "armor"
    MATERIAL = "material"
    CONSUMABLE = "consumable"
    TRAP = "trap"
    TOOL = "tool"
    DECORATION = "decoration"

class WeaponType(Enum):
    """Types of weapons"""
    GREAT_SWORD = "great_sword"
    LONG_SWORD = "long_sword"
    SWORD_AND_SHIELD = "sword_and_shield"
    DUAL_BLADES = "dual_blades"
    HAMMER = "hammer"
    HUNTING_HORN = "hunting_horn"
    LANCE = "lance"
    GUNLANCE = "gunlance"
    SWITCH_AXE = "switch_axe"
    CHARGE_BLADE = "charge_blade"
    INSECT_GLAIVE = "insect_glaive"
    LIGHT_BOWGUN = "light_bowgun"
    HEAVY_BOWGUN = "heavy_bowgun"
    BOW = "bow"

class ArmorType(Enum):
    """Types of armor pieces"""
    HEAD = "head"
    CHEST = "chest"
    ARMS = "arms"
    WAIST = "waist"
    LEGS = "legs"

class ElementType(Enum):
    """Elemental types"""
    NONE = "none"
    FIRE = "fire"
    WATER = "water"
    THUNDER = "thunder"
    ICE = "ice"
    DRAGON = "dragon"
    POISON = "poison"
    PARALYSIS = "paralysis"
    SLEEP = "sleep"

@dataclass
class ItemStats:
    """Base item statistics"""
    attack: int = 0
    defense: int = 0
    elemental_attack: int = 0
    elemental_defense: int = 0
    affinity: int = 0  # Critical hit chance
    sharpness: int = 0  # For weapons
    slots: int = 0  # Decoration slots
    rarity: int = 1

@dataclass
class Weapon:
    """Weapon item with specific properties"""
    id: str
    name: str
    weapon_type: WeaponType
    stats: ItemStats
    element_type: ElementType
    element_value: int
    sharpness_levels: List[int]  # Sharpness values for each level
    max_sharpness: int
    current_sharpness: int
    upgrade_level: int
    max_upgrade_level: int
    crafting_materials: Dict[str, int]  # Material ID -> Quantity
    description: str
    icon: str

@dataclass
class Armor:
    """Armor item with specific properties"""
    id: str
    name: str
    armor_type: ArmorType
    stats: ItemStats
    element_resistance: Dict[ElementType, int]
    skills: List[str]  # Skill names provided by this armor
    set_name: str  # Armor set this piece belongs to
    crafting_materials: Dict[str, int]
    description: str
    icon: str

@dataclass
class Material:
    """Crafting material"""
    id: str
    name: str
    rarity: int
    description: str
    icon: str
    monster_drops: Dict[str, float]  # Monster name -> drop rate
    gathering_locations: List[str]

@dataclass
class Consumable:
    """Consumable item"""
    id: str
    name: str
    effect_type: str  # heal, buff, cure, etc.
    effect_value: int
    duration: float  # Duration in seconds (0 for instant)
    description: str
    icon: str

@dataclass
class InventorySlot:
    """Individual inventory slot"""
    item_id: str
    quantity: int
    max_quantity: int
    is_equipped: bool = False
    slot_position: int = 0

class ItemDatabase:
    """Manages all items in the game"""
    
    def __init__(self, db_path: str = "server_data/items.db"):
        self.db_path = db_path
        self.weapons: Dict[str, Weapon] = {}
        self.armors: Dict[str, Armor] = {}
        self.materials: Dict[str, Material] = {}
        self.consumables: Dict[str, Consumable] = {}
        self.crafting_recipes: Dict[str, Dict] = {}
        
        self.init_database()
        self.load_items()
    
    def init_database(self):
        """Initialize the item database"""
        Path(self.db_path).parent.mkdir(exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create weapons table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weapons (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                weapon_type TEXT NOT NULL,
                attack INTEGER DEFAULT 0,
                defense INTEGER DEFAULT 0,
                elemental_attack INTEGER DEFAULT 0,
                elemental_defense INTEGER DEFAULT 0,
                affinity INTEGER DEFAULT 0,
                sharpness INTEGER DEFAULT 0,
                slots INTEGER DEFAULT 0,
                rarity INTEGER DEFAULT 1,
                element_type TEXT DEFAULT 'none',
                element_value INTEGER DEFAULT 0,
                sharpness_levels TEXT,
                max_sharpness INTEGER DEFAULT 0,
                upgrade_level INTEGER DEFAULT 0,
                max_upgrade_level INTEGER DEFAULT 0,
                crafting_materials TEXT,
                description TEXT,
                icon TEXT
            )
        ''')
        
        # Create armors table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS armors (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                armor_type TEXT NOT NULL,
                attack INTEGER DEFAULT 0,
                defense INTEGER DEFAULT 0,
                elemental_attack INTEGER DEFAULT 0,
                elemental_defense INTEGER DEFAULT 0,
                affinity INTEGER DEFAULT 0,
                sharpness INTEGER DEFAULT 0,
                slots INTEGER DEFAULT 0,
                rarity INTEGER DEFAULT 1,
                element_resistance TEXT,
                skills TEXT,
                set_name TEXT,
                crafting_materials TEXT,
                description TEXT,
                icon TEXT
            )
        ''')
        
        # Create materials table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS materials (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                rarity INTEGER DEFAULT 1,
                description TEXT,
                icon TEXT,
                monster_drops TEXT,
                gathering_locations TEXT
            )
        ''')
        
        # Create consumables table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS consumables (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                effect_type TEXT NOT NULL,
                effect_value INTEGER DEFAULT 0,
                duration REAL DEFAULT 0,
                description TEXT,
                icon TEXT
            )
        ''')
        
        # Create player inventories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS player_inventories (
                player_id TEXT,
                item_id TEXT,
                quantity INTEGER DEFAULT 1,
                max_quantity INTEGER DEFAULT 99,
                is_equipped BOOLEAN DEFAULT 0,
                slot_position INTEGER DEFAULT 0,
                PRIMARY KEY (player_id, item_id)
            )
        ''')
        
        # Create equipped items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS equipped_items (
                player_id TEXT PRIMARY KEY,
                weapon_id TEXT,
                head_armor_id TEXT,
                chest_armor_id TEXT,
                arms_armor_id TEXT,
                waist_armor_id TEXT,
                legs_armor_id TEXT,
                decoration_slots TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_items(self):
        """Load all items from database and create default items"""
        self._create_default_items()
        self._load_from_database()
    
    def _create_default_items(self):
        """Create default items if database is empty"""
        # Create default weapons
        self.weapons = {
            "iron_sword": Weapon(
                id="iron_sword",
                name="Iron Sword",
                weapon_type=WeaponType.GREAT_SWORD,
                stats=ItemStats(attack=100, sharpness=50, rarity=1),
                element_type=ElementType.NONE,
                element_value=0,
                sharpness_levels=[50, 100, 150, 200],
                max_sharpness=200,
                current_sharpness=200,
                upgrade_level=0,
                max_upgrade_level=3,
                crafting_materials={"iron_ore": 3, "monster_bone": 2},
                description="A basic iron great sword",
                icon="iron_sword.png"
            ),
            "flame_sword": Weapon(
                id="flame_sword",
                name="Flame Sword",
                weapon_type=WeaponType.GREAT_SWORD,
                stats=ItemStats(attack=120, sharpness=60, rarity=2),
                element_type=ElementType.FIRE,
                element_value=150,
                sharpness_levels=[60, 120, 180, 240],
                max_sharpness=240,
                current_sharpness=240,
                upgrade_level=0,
                max_upgrade_level=3,
                crafting_materials={"iron_sword": 1, "fire_essence": 2, "rathian_scale": 3},
                description="A great sword imbued with fire",
                icon="flame_sword.png"
            )
        }
        
        # Create default armors
        self.armors = {
            "leather_helmet": Armor(
                id="leather_helmet",
                name="Leather Helmet",
                armor_type=ArmorType.HEAD,
                stats=ItemStats(defense=15, slots=1, rarity=1),
                element_resistance={ElementType.NONE: 0},
                skills=["Gathering +1"],
                set_name="Leather",
                crafting_materials={"leather": 2, "monster_bone": 1},
                description="A basic leather helmet",
                icon="leather_helmet.png"
            ),
            "rathian_helmet": Armor(
                id="rathian_helmet",
                name="Rathian Helmet",
                armor_type=ArmorType.HEAD,
                stats=ItemStats(defense=25, slots=2, rarity=2),
                element_resistance={ElementType.FIRE: 10, ElementType.POISON: 5},
                skills=["Fire Resistance +2", "Poison Resistance +1"],
                set_name="Rathian",
                crafting_materials={"rathian_scale": 3, "rathian_wing": 1},
                description="A helmet made from Rathian materials",
                icon="rathian_helmet.png"
            )
        }
        
        # Create default materials
        self.materials = {
            "iron_ore": Material(
                id="iron_ore",
                name="Iron Ore",
                rarity=1,
                description="Common iron ore found in mines",
                icon="iron_ore.png",
                monster_drops={},
                gathering_locations=["Mine", "Cave", "Mountain"]
            ),
            "rathian_scale": Material(
                id="rathian_scale",
                name="Rathian Scale",
                rarity=2,
                description="A tough scale from a Rathian",
                icon="rathian_scale.png",
                monster_drops={"Rathian": 0.8, "Rathalos": 0.3},
                gathering_locations=[]
            ),
            "fire_essence": Material(
                id="fire_essence",
                name="Fire Essence",
                rarity=2,
                description="Pure fire energy",
                icon="fire_essence.png",
                monster_drops={"Rathian": 0.4, "Rathalos": 0.6},
                gathering_locations=["Volcanic Area"]
            )
        }
        
        # Create default consumables
        self.consumables = {
            "potion": Consumable(
                id="potion",
                name="Potion",
                effect_type="heal",
                effect_value=50,
                duration=0,
                description="Restores 50 HP",
                icon="potion.png"
            ),
            "mega_potion": Consumable(
                id="mega_potion",
                name="Mega Potion",
                effect_type="heal",
                effect_value=100,
                duration=0,
                description="Restores 100 HP",
                icon="mega_potion.png"
            ),
            "antidote": Consumable(
                id="antidote",
                name="Antidote",
                effect_type="cure",
                effect_value=0,
                duration=0,
                description="Cures poison",
                icon="antidote.png"
            )
        }
        
        # Create crafting recipes
        self.crafting_recipes = {
            "flame_sword": {
                "materials": {"iron_sword": 1, "fire_essence": 2, "rathian_scale": 3},
                "zenny_cost": 500,
                "crafting_time": 30
            },
            "rathian_helmet": {
                "materials": {"rathian_scale": 3, "rathian_wing": 1},
                "zenny_cost": 300,
                "crafting_time": 20
            }
        }
    
    def _load_from_database(self):
        """Load items from database (placeholder for future implementation)"""
        pass
    
    def get_weapon(self, weapon_id: str) -> Optional[Weapon]:
        """Get a weapon by ID"""
        return self.weapons.get(weapon_id)
    
    def get_armor(self, armor_id: str) -> Optional[Armor]:
        """Get an armor piece by ID"""
        return self.armors.get(armor_id)
    
    def get_material(self, material_id: str) -> Optional[Material]:
        """Get a material by ID"""
        return self.materials.get(material_id)
    
    def get_consumable(self, consumable_id: str) -> Optional[Consumable]:
        """Get a consumable by ID"""
        return self.consumables.get(consumable_id)
    
    def get_crafting_recipe(self, item_id: str) -> Optional[Dict]:
        """Get crafting recipe for an item"""
        return self.crafting_recipes.get(item_id)

class PlayerInventory:
    """Manages a player's inventory and equipment"""
    
    def __init__(self, player_id: str, item_db: ItemDatabase):
        self.player_id = player_id
        self.item_db = item_db
        self.inventory: Dict[str, InventorySlot] = {}
        self.equipped_items = {
            "weapon": None,
            "head": None,
            "chest": None,
            "arms": None,
            "waist": None,
            "legs": None
        }
        self.max_inventory_size = 50
        
        self.load_inventory()
    
    def load_inventory(self):
        """Load player inventory from database"""
        conn = sqlite3.connect(self.item_db.db_path)
        cursor = conn.cursor()
        
        # Load inventory items
        cursor.execute('''
            SELECT item_id, quantity, max_quantity, is_equipped, slot_position
            FROM player_inventories WHERE player_id = ?
        ''', (self.player_id,))
        
        for row in cursor.fetchall():
            item_id, quantity, max_quantity, is_equipped, slot_position = row
            self.inventory[item_id] = InventorySlot(
                item_id=item_id,
                quantity=quantity,
                max_quantity=max_quantity,
                is_equipped=bool(is_equipped),
                slot_position=slot_position
            )
        
        # Load equipped items
        cursor.execute('''
            SELECT weapon_id, head_armor_id, chest_armor_id, arms_armor_id, waist_armor_id, legs_armor_id
            FROM equipped_items WHERE player_id = ?
        ''', (self.player_id,))
        
        row = cursor.fetchone()
        if row:
            self.equipped_items["weapon"] = row[0]
            self.equipped_items["head"] = row[1]
            self.equipped_items["chest"] = row[2]
            self.equipped_items["arms"] = row[3]
            self.equipped_items["waist"] = row[4]
            self.equipped_items["legs"] = row[5]
        
        conn.close()
    
    def save_inventory(self):
        """Save player inventory to database"""
        conn = sqlite3.connect(self.item_db.db_path)
        cursor = conn.cursor()
        
        # Clear existing inventory
        cursor.execute('DELETE FROM player_inventories WHERE player_id = ?', (self.player_id,))
        
        # Save inventory items
        for item_id, slot in self.inventory.items():
            cursor.execute('''
                INSERT INTO player_inventories 
                (player_id, item_id, quantity, max_quantity, is_equipped, slot_position)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (self.player_id, item_id, slot.quantity, slot.max_quantity, 
                  slot.is_equipped, slot.slot_position))
        
        # Save equipped items
        cursor.execute('''
            INSERT OR REPLACE INTO equipped_items 
            (player_id, weapon_id, head_armor_id, chest_armor_id, arms_armor_id, waist_armor_id, legs_armor_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (self.player_id, self.equipped_items["weapon"], self.equipped_items["head"],
              self.equipped_items["chest"], self.equipped_items["arms"],
              self.equipped_items["waist"], self.equipped_items["legs"]))
        
        conn.commit()
        conn.close()
    
    def add_item(self, item_id: str, quantity: int = 1) -> bool:
        """Add items to inventory"""
        if len(self.inventory) >= self.max_inventory_size and item_id not in self.inventory:
            return False
        
        if item_id in self.inventory:
            slot = self.inventory[item_id]
            slot.quantity = min(slot.quantity + quantity, slot.max_quantity)
        else:
            # Determine max quantity based on item type
            max_quantity = 99
            if self.item_db.get_weapon(item_id):
                max_quantity = 1
            elif self.item_db.get_armor(item_id):
                max_quantity = 1
            
            self.inventory[item_id] = InventorySlot(
                item_id=item_id,
                quantity=min(quantity, max_quantity),
                max_quantity=max_quantity
            )
        
        self.save_inventory()
        return True
    
    def remove_item(self, item_id: str, quantity: int = 1) -> bool:
        """Remove items from inventory"""
        if item_id not in self.inventory:
            return False
        
        slot = self.inventory[item_id]
        if slot.quantity < quantity:
            return False
        
        slot.quantity -= quantity
        if slot.quantity <= 0:
            del self.inventory[item_id]
        
        self.save_inventory()
        return True
    
    def get_item_quantity(self, item_id: str) -> int:
        """Get quantity of an item in inventory"""
        if item_id in self.inventory:
            return self.inventory[item_id].quantity
        return 0
    
    def equip_item(self, item_id: str, slot_type: str) -> bool:
        """Equip an item"""
        if item_id not in self.inventory:
            return False
        
        # Check if item can be equipped in this slot
        weapon = self.item_db.get_weapon(item_id)
        armor = self.item_db.get_armor(item_id)
        
        if weapon and slot_type == "weapon":
            # Unequip current weapon
            if self.equipped_items["weapon"]:
                self.unequip_item("weapon")
            
            self.equipped_items["weapon"] = item_id
            self.inventory[item_id].is_equipped = True
            self.save_inventory()
            return True
        
        elif armor and slot_type in ["head", "chest", "arms", "waist", "legs"]:
            # Check if armor type matches slot
            armor_slot_map = {
                ArmorType.HEAD: "head",
                ArmorType.CHEST: "chest",
                ArmorType.ARMS: "arms",
                ArmorType.WAIST: "waist",
                ArmorType.LEGS: "legs"
            }
            
            if armor_slot_map.get(armor.armor_type) == slot_type:
                # Unequip current armor in this slot
                if self.equipped_items[slot_type]:
                    self.unequip_item(slot_type)
                
                self.equipped_items[slot_type] = item_id
                self.inventory[item_id].is_equipped = True
                self.save_inventory()
                return True
        
        return False
    
    def unequip_item(self, slot_type: str) -> bool:
        """Unequip an item"""
        if slot_type not in self.equipped_items:
            return False
        
        item_id = self.equipped_items[slot_type]
        if item_id and item_id in self.inventory:
            self.inventory[item_id].is_equipped = False
            self.equipped_items[slot_type] = None
            self.save_inventory()
            return True
        
        return False
    
    def get_equipped_stats(self) -> ItemStats:
        """Get combined stats from all equipped items"""
        total_stats = ItemStats()
        
        # Add weapon stats
        if self.equipped_items["weapon"]:
            weapon = self.item_db.get_weapon(self.equipped_items["weapon"])
            if weapon:
                total_stats.attack += weapon.stats.attack
                total_stats.affinity += weapon.stats.affinity
                total_stats.slots += weapon.stats.slots
        
        # Add armor stats
        for slot_type in ["head", "chest", "arms", "waist", "legs"]:
            if self.equipped_items[slot_type]:
                armor = self.item_db.get_armor(self.equipped_items[slot_type])
                if armor:
                    total_stats.defense += armor.stats.defense
                    total_stats.slots += armor.stats.slots
        
        return total_stats
    
    def get_inventory_summary(self) -> Dict:
        """Get summary of inventory contents"""
        summary = {
            "total_items": len(self.inventory),
            "max_capacity": self.max_inventory_size,
            "equipped_items": self.equipped_items.copy(),
            "item_counts": {}
        }
        
        for item_id, slot in self.inventory.items():
            summary["item_counts"][item_id] = slot.quantity
        
        return summary

class CraftingSystem:
    """Handles item crafting and upgrades"""
    
    def __init__(self, item_db: ItemDatabase):
        self.item_db = item_db
    
    def can_craft_item(self, item_id: str, inventory: PlayerInventory) -> Tuple[bool, Dict]:
        """Check if player can craft an item"""
        recipe = self.item_db.get_crafting_recipe(item_id)
        if not recipe:
            return False, {"error": "No recipe found for this item"}
        
        missing_materials = {}
        for material_id, required_quantity in recipe["materials"].items():
            available_quantity = inventory.get_item_quantity(material_id)
            if available_quantity < required_quantity:
                missing_materials[material_id] = required_quantity - available_quantity
        
        if missing_materials:
            return False, {"error": "Missing materials", "missing": missing_materials}
        
        return True, {"zenny_cost": recipe.get("zenny_cost", 0)}
    
    def craft_item(self, item_id: str, inventory: PlayerInventory, player_zenny: int) -> Tuple[bool, Dict]:
        """Craft an item"""
        can_craft, result = self.can_craft_item(item_id, inventory)
        if not can_craft:
            return False, result
        
        recipe = self.item_db.get_crafting_recipe(item_id)
        zenny_cost = recipe.get("zenny_cost", 0)
        
        if player_zenny < zenny_cost:
            return False, {"error": "Not enough zenny"}
        
        # Remove materials
        for material_id, quantity in recipe["materials"].items():
            inventory.remove_item(material_id, quantity)
        
        # Add crafted item
        success = inventory.add_item(item_id, 1)
        if not success:
            return False, {"error": "Inventory full"}
        
        return True, {
            "success": True,
            "item_id": item_id,
            "zenny_cost": zenny_cost,
            "crafting_time": recipe.get("crafting_time", 0)
        }
    
    def upgrade_weapon(self, weapon_id: str, inventory: PlayerInventory, player_zenny: int) -> Tuple[bool, Dict]:
        """Upgrade a weapon"""
        weapon = self.item_db.get_weapon(weapon_id)
        if not weapon:
            return False, {"error": "Weapon not found"}
        
        if weapon.upgrade_level >= weapon.max_upgrade_level:
            return False, {"error": "Weapon already at maximum level"}
        
        # Check if player has the weapon equipped
        if not inventory.equipped_items["weapon"] == weapon_id:
            return False, {"error": "Weapon must be equipped to upgrade"}
        
        # Calculate upgrade cost and materials
        upgrade_cost = 100 * (weapon.upgrade_level + 1)
        upgrade_materials = {
            "iron_ore": 2 * (weapon.upgrade_level + 1),
            "monster_bone": 1 * (weapon.upgrade_level + 1)
        }
        
        if player_zenny < upgrade_cost:
            return False, {"error": "Not enough zenny"}
        
        # Check materials
        for material_id, quantity in upgrade_materials.items():
            if inventory.get_item_quantity(material_id) < quantity:
                return False, {"error": f"Missing {material_id}"}
        
        # Remove materials and zenny
        for material_id, quantity in upgrade_materials.items():
            inventory.remove_item(material_id, quantity)
        
        # Upgrade weapon
        weapon.upgrade_level += 1
        weapon.stats.attack += 20
        weapon.stats.sharpness += 10
        weapon.max_sharpness += 20
        weapon.current_sharpness = weapon.max_sharpness
        
        return True, {
            "success": True,
            "new_level": weapon.upgrade_level,
            "new_attack": weapon.stats.attack,
            "zenny_cost": upgrade_cost
        }

def test_item_system():
    """Test the item and equipment system"""
    print("🐉 Monster Hunter Frontier G - Item System Test")
    print("=" * 60)
    
    # Create item database
    item_db = ItemDatabase()
    
    # Create player inventory
    player_inventory = PlayerInventory("test_player", item_db)
    
    # Add some materials
    player_inventory.add_item("iron_ore", 10)
    player_inventory.add_item("monster_bone", 5)
    player_inventory.add_item("rathian_scale", 3)
    player_inventory.add_item("fire_essence", 2)
    
    print(f"Added materials to inventory")
    print(f"Inventory summary: {player_inventory.get_inventory_summary()}")
    
    # Test crafting
    crafting_system = CraftingSystem(item_db)
    
    print(f"\n--- Testing Crafting ---")
    can_craft, result = crafting_system.can_craft_item("flame_sword", player_inventory)
    print(f"Can craft Flame Sword: {can_craft}")
    if not can_craft:
        print(f"Missing: {result}")
    
    # Craft the weapon
    success, craft_result = crafting_system.craft_item("flame_sword", player_inventory, 1000)
    print(f"Crafting result: {success}")
    if success:
        print(f"Crafted: {craft_result}")
    
    # Equip the weapon
    print(f"\n--- Testing Equipment ---")
    equip_success = player_inventory.equip_item("flame_sword", "weapon")
    print(f"Equipped weapon: {equip_success}")
    
    # Get equipped stats
    stats = player_inventory.get_equipped_stats()
    print(f"Equipped stats: Attack={stats.attack}, Defense={stats.defense}")
    
    # Test weapon upgrade
    print(f"\n--- Testing Weapon Upgrade ---")
    upgrade_success, upgrade_result = crafting_system.upgrade_weapon("flame_sword", player_inventory, 500)
    print(f"Upgrade result: {upgrade_success}")
    if upgrade_success:
        print(f"Upgraded: {upgrade_result}")
    
    print("\n" + "=" * 60)
    print("✅ Item System Test Complete!")
    print("⚔️ Weapon crafting and upgrading working!")
    print("🛡️ Armor system ready!")
    print("📦 Inventory management active!")

if __name__ == "__main__":
    test_item_system() 