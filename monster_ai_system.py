#!/usr/bin/env python3
"""
Monster Hunter Frontier G - Monster AI & Combat System
Advanced monster behavior, combat mechanics, and status effects
"""

import random
import math
import time
import json
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import threading
import logging

class MonsterType(Enum):
    """Monster types and their characteristics"""
    GREAT_JAGGI = "Great Jaggi"
    QURUPECO = "Qurupeco"
    BARROTH = "Barroth"
    RATHIAN = "Rathian"
    RATHALOS = "Rathalos"
    DIABLOS = "Diablos"
    TIGREX = "Tigrex"
    NARGACUGA = "Nargacuga"
    BARIOTH = "Barioth"

class StatusEffect(Enum):
    """Status effects that can be applied to monsters"""
    POISON = "poison"
    PARALYSIS = "paralysis"
    SLEEP = "sleep"
    STUN = "stun"
    MOUNT = "mount"
    TRAP = "trap"

class AttackType(Enum):
    """Types of monster attacks"""
    PHYSICAL = "physical"
    FIRE = "fire"
    ICE = "ice"
    THUNDER = "thunder"
    WATER = "water"
    DRAGON = "dragon"
    POISON = "poison"

@dataclass
class MonsterStats:
    """Monster statistics and attributes"""
    name: str
    monster_type: MonsterType
    health: int
    max_health: int
    attack: int
    defense: int
    speed: float
    size: str  # small, medium, large
    elemental_weakness: List[AttackType]
    elemental_resistance: List[AttackType]
    status_weakness: List[StatusEffect]
    status_resistance: List[StatusEffect]
    rage_threshold: float  # Percentage of health when monster becomes enraged
    enrage_multiplier: float  # Attack multiplier when enraged

@dataclass
class Position:
    """3D position in the world"""
    x: float
    y: float
    z: float
    
    def distance_to(self, other: 'Position') -> float:
        """Calculate distance to another position"""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2 + (self.z - other.z)**2)
    
    def move_towards(self, target: 'Position', speed: float) -> 'Position':
        """Move towards a target position"""
        distance = self.distance_to(target)
        if distance == 0:
            return self
        
        ratio = min(speed / distance, 1.0)
        return Position(
            self.x + (target.x - self.x) * ratio,
            self.y + (target.y - self.y) * ratio,
            self.z + (target.z - self.z) * ratio
        )

@dataclass
class StatusEffectInstance:
    """Active status effect on a monster"""
    effect: StatusEffect
    duration: float
    intensity: float
    start_time: float

class MonsterAI:
    """Advanced monster AI system"""
    
    def __init__(self, monster_stats: MonsterStats, initial_position: Position):
        self.stats = monster_stats
        self.position = initial_position
        self.target_position = initial_position
        self.current_health = monster_stats.health
        self.is_enraged = False
        self.is_stunned = False
        self.is_sleeping = False
        self.is_trapped = False
        self.is_mounted = False
        self.status_effects: List[StatusEffectInstance] = []
        self.last_attack_time = 0
        self.attack_cooldown = 2.0  # Seconds between attacks
        self.state = "idle"  # idle, chasing, attacking, fleeing, sleeping
        self.target_player = None
        self.rage_timer = 0
        self.last_movement = time.time()
        
        # AI behavior patterns
        self.aggression_level = random.uniform(0.7, 1.3)
        self.intelligence = random.uniform(0.8, 1.2)
        self.patience = random.uniform(0.6, 1.4)
        
        # Combat patterns
        self.attack_patterns = self._generate_attack_patterns()
        self.current_pattern_index = 0
        
        self.logger = logging.getLogger(f"MonsterAI_{monster_stats.name}")
    
    def _generate_attack_patterns(self) -> List[Dict]:
        """Generate attack patterns based on monster type"""
        base_patterns = {
            MonsterType.GREAT_JAGGI: [
                {"name": "Tail Swipe", "damage": 15, "range": 3.0, "cooldown": 1.5},
                {"name": "Charge", "damage": 25, "range": 5.0, "cooldown": 2.0},
                {"name": "Bite", "damage": 20, "range": 2.0, "cooldown": 1.0}
            ],
            MonsterType.RATHIAN: [
                {"name": "Fire Breath", "damage": 30, "range": 4.0, "cooldown": 3.0, "type": AttackType.FIRE},
                {"name": "Tail Flip", "damage": 35, "range": 3.5, "cooldown": 2.5, "status": StatusEffect.POISON},
                {"name": "Charge", "damage": 25, "range": 6.0, "cooldown": 2.0}
            ],
            MonsterType.TIGREX: [
                {"name": "Roar", "damage": 10, "range": 8.0, "cooldown": 4.0, "status": StatusEffect.STUN},
                {"name": "Claw Swipe", "damage": 40, "range": 3.0, "cooldown": 1.5},
                {"name": "Rush Attack", "damage": 50, "range": 7.0, "cooldown": 3.0}
            ]
        }
        
        return base_patterns.get(self.stats.monster_type, [
            {"name": "Basic Attack", "damage": 20, "range": 2.0, "cooldown": 1.5}
        ])
    
    def update(self, delta_time: float, nearby_players: List[Dict]) -> Dict:
        """Update monster AI and return current state"""
        current_time = time.time()
        
        # Update status effects
        self._update_status_effects(delta_time)
        
        # Check if monster should be enraged
        health_percentage = self.current_health / self.stats.max_health
        if health_percentage <= self.stats.rage_threshold and not self.is_enraged:
            self._become_enraged()
        
        # Find nearest player
        nearest_player = self._find_nearest_player(nearby_players)
        
        if nearest_player:
            self.target_player = nearest_player
            player_distance = self.position.distance_to(nearest_player['position'])
            
            # Determine behavior based on distance and state
            if player_distance <= 2.0 and not self.is_stunned and not self.is_sleeping:
                # Attack player
                return self._perform_attack(nearest_player, current_time)
            elif player_distance <= 15.0 and not self.is_stunned and not self.is_sleeping:
                # Chase player
                return self._chase_player(nearest_player, delta_time)
            else:
                # Idle behavior
                return self._idle_behavior(delta_time)
        else:
            # No players nearby, idle behavior
            return self._idle_behavior(delta_time)
    
    def _update_status_effects(self, delta_time: float):
        """Update active status effects"""
        current_time = time.time()
        active_effects = []
        
        for effect in self.status_effects:
            if current_time - effect.start_time < effect.duration:
                active_effects.append(effect)
                
                # Apply effect
                if effect.effect == StatusEffect.POISON:
                    self.current_health -= effect.intensity * delta_time
                elif effect.effect == StatusEffect.PARALYSIS:
                    self.is_stunned = True
                elif effect.effect == StatusEffect.SLEEP:
                    self.is_sleeping = True
                elif effect.effect == StatusEffect.TRAP:
                    self.is_trapped = True
                elif effect.effect == StatusEffect.MOUNT:
                    self.is_mounted = True
            else:
                # Effect expired
                if effect.effect == StatusEffect.PARALYSIS:
                    self.is_stunned = False
                elif effect.effect == StatusEffect.SLEEP:
                    self.is_sleeping = False
                elif effect.effect == StatusEffect.TRAP:
                    self.is_trapped = False
                elif effect.effect == StatusEffect.MOUNT:
                    self.is_mounted = False
        
        self.status_effects = active_effects
    
    def _find_nearest_player(self, players: List[Dict]) -> Optional[Dict]:
        """Find the nearest player to the monster"""
        if not players:
            return None
        
        nearest = None
        min_distance = float('inf')
        
        for player in players:
            distance = self.position.distance_to(player['position'])
            if distance < min_distance:
                min_distance = distance
                nearest = player
        
        return nearest
    
    def _become_enraged(self):
        """Monster becomes enraged"""
        self.is_enraged = True
        self.rage_timer = time.time()
        self.logger.info(f"{self.stats.name} has become ENRAGED!")
        
        # Increase attack speed and damage
        self.attack_cooldown *= 0.7
        self.stats.attack = int(self.stats.attack * self.stats.enrage_multiplier)
    
    def _perform_attack(self, player: Dict, current_time: float) -> Dict:
        """Perform an attack on a player"""
        if current_time - self.last_attack_time < self.attack_cooldown:
            return {"action": "cooldown", "position": self.position}
        
        # Select attack pattern
        attack_pattern = self.attack_patterns[self.current_pattern_index]
        self.current_pattern_index = (self.current_pattern_index + 1) % len(self.attack_patterns)
        
        # Calculate damage
        base_damage = attack_pattern["damage"]
        if self.is_enraged:
            base_damage = int(base_damage * self.stats.enrage_multiplier)
        
        # Check if attack hits
        player_distance = self.position.distance_to(player['position'])
        if player_distance <= attack_pattern["range"]:
            self.last_attack_time = current_time
            
            # Calculate final damage with player defense
            final_damage = max(1, base_damage - player.get('defense', 0))
            
            attack_result = {
                "action": "attack",
                "attack_name": attack_pattern["name"],
                "damage": final_damage,
                "position": self.position,
                "target_player": player['id'],
                "attack_type": attack_pattern.get("type", AttackType.PHYSICAL),
                "status_effect": attack_pattern.get("status")
            }
            
            self.logger.info(f"{self.stats.name} attacks {player['name']} with {attack_pattern['name']} for {final_damage} damage!")
            return attack_result
        else:
            return {"action": "miss", "position": self.position}
    
    def _chase_player(self, player: Dict, delta_time: float) -> Dict:
        """Chase a player"""
        if self.is_trapped or self.is_stunned or self.is_sleeping:
            return {"action": "stunned", "position": self.position}
        
        # Move towards player
        movement_speed = self.stats.speed * delta_time
        if self.is_enraged:
            movement_speed *= 1.3
        
        new_position = self.position.move_towards(player['position'], movement_speed)
        self.position = new_position
        
        return {
            "action": "chase",
            "position": self.position,
            "target": player['id'],
            "speed": movement_speed
        }
    
    def _idle_behavior(self, delta_time: float) -> Dict:
        """Idle behavior when no players are nearby"""
        if self.is_sleeping:
            return {"action": "sleep", "position": self.position}
        
        # Random movement
        if time.time() - self.last_movement > random.uniform(3.0, 8.0):
            # Move to random position
            random_offset = Position(
                random.uniform(-5.0, 5.0),
                0,
                random.uniform(-5.0, 5.0)
            )
            self.target_position = Position(
                self.position.x + random_offset.x,
                self.position.y,
                self.position.z + random_offset.z
            )
            self.last_movement = time.time()
        
        # Move towards target position
        if self.position.distance_to(self.target_position) > 0.5:
            movement_speed = self.stats.speed * 0.3 * delta_time  # Slower when idle
            self.position = self.position.move_towards(self.target_position, movement_speed)
            return {"action": "patrol", "position": self.position}
        else:
            return {"action": "idle", "position": self.position}
    
    def take_damage(self, damage: int, attack_type: AttackType = AttackType.PHYSICAL, 
                   status_effect: Optional[StatusEffect] = None, status_duration: float = 0) -> Dict:
        """Take damage from a player attack"""
        # Check elemental resistance/weakness
        damage_multiplier = 1.0
        if attack_type in self.stats.elemental_weakness:
            damage_multiplier = 1.5
        elif attack_type in self.stats.elemental_resistance:
            damage_multiplier = 0.7
        
        # Apply status resistance
        if status_effect and status_effect in self.stats.status_resistance:
            status_duration *= 0.5
        
        final_damage = int(damage * damage_multiplier)
        self.current_health = max(0, self.current_health - final_damage)
        
        # Apply status effect
        if status_effect and status_duration > 0:
            self.status_effects.append(StatusEffectInstance(
                effect=status_effect,
                duration=status_duration,
                intensity=1.0,
                start_time=time.time()
            ))
        
        # Check if monster is defeated
        if self.current_health <= 0:
            return {
                "action": "defeated",
                "damage": final_damage,
                "health": 0,
                "status": "dead"
            }
        
        # Check if monster should flee
        if self.current_health < self.stats.max_health * 0.2 and random.random() < 0.3:
            self.state = "fleeing"
            return {
                "action": "flee",
                "damage": final_damage,
                "health": self.current_health,
                "status": "fleeing"
            }
        
        return {
            "action": "damaged",
            "damage": final_damage,
            "health": self.current_health,
            "status": "alive"
        }
    
    def get_state(self) -> Dict:
        """Get current monster state"""
        return {
            "name": self.stats.name,
            "type": self.stats.monster_type.value,
            "health": self.current_health,
            "max_health": self.stats.max_health,
            "position": {
                "x": self.position.x,
                "y": self.position.y,
                "z": self.position.z
            },
            "is_enraged": self.is_enraged,
            "is_stunned": self.is_stunned,
            "is_sleeping": self.is_sleeping,
            "is_trapped": self.is_trapped,
            "is_mounted": self.is_mounted,
            "state": self.state,
            "status_effects": [effect.effect.value for effect in self.status_effects],
            "target_player": self.target_player['id'] if self.target_player else None
        }

class MonsterSpawner:
    """Manages monster spawning and world population"""
    
    def __init__(self):
        self.monster_templates = self._create_monster_templates()
        self.active_monsters: Dict[str, MonsterAI] = {}
        self.spawn_points: List[Position] = []
        self.max_monsters = 10
        self.spawn_timer = 0
        self.spawn_interval = 30.0  # Seconds between spawns
        
    def _create_monster_templates(self) -> Dict[str, MonsterStats]:
        """Create monster templates with different stats"""
        return {
            "great_jaggi": MonsterStats(
                name="Great Jaggi",
                monster_type=MonsterType.GREAT_JAGGI,
                health=800,
                max_health=800,
                attack=45,
                defense=20,
                speed=3.0,
                size="medium",
                elemental_weakness=[AttackType.FIRE],
                elemental_resistance=[AttackType.WATER],
                status_weakness=[StatusEffect.PARALYSIS],
                status_resistance=[StatusEffect.POISON],
                rage_threshold=0.3,
                enrage_multiplier=1.5
            ),
            "rathian": MonsterStats(
                name="Rathian",
                monster_type=MonsterType.RATHIAN,
                health=2000,
                max_health=2000,
                attack=80,
                defense=35,
                speed=4.0,
                size="large",
                elemental_weakness=[AttackType.THUNDER],
                elemental_resistance=[AttackType.FIRE],
                status_weakness=[StatusEffect.STUN],
                status_resistance=[StatusEffect.POISON],
                rage_threshold=0.4,
                enrage_multiplier=1.8
            ),
            "tigrex": MonsterStats(
                name="Tigrex",
                monster_type=MonsterType.TIGREX,
                health=3000,
                max_health=3000,
                attack=120,
                defense=50,
                speed=5.0,
                size="large",
                elemental_weakness=[AttackType.THUNDER],
                elemental_resistance=[AttackType.FIRE, AttackType.ICE],
                status_weakness=[StatusEffect.STUN],
                status_resistance=[StatusEffect.PARALYSIS],
                rage_threshold=0.5,
                enrage_multiplier=2.0
            )
        }
    
    def add_spawn_point(self, position: Position):
        """Add a spawn point for monsters"""
        self.spawn_points.append(position)
    
    def spawn_monster(self, monster_type: str, position: Position) -> Optional[str]:
        """Spawn a monster at the specified position"""
        if len(self.active_monsters) >= self.max_monsters:
            return None
        
        if monster_type not in self.monster_templates:
            return None
        
        monster_id = f"{monster_type}_{int(time.time())}_{random.randint(1000, 9999)}"
        monster_stats = self.monster_templates[monster_type]
        monster_ai = MonsterAI(monster_stats, position)
        
        self.active_monsters[monster_id] = monster_ai
        return monster_id
    
    def update_monsters(self, delta_time: float, nearby_players: List[Dict]) -> List[Dict]:
        """Update all active monsters"""
        updates = []
        monsters_to_remove = []
        
        for monster_id, monster in self.active_monsters.items():
            try:
                update = monster.update(delta_time, nearby_players)
                update["monster_id"] = monster_id
                updates.append(update)
                
                # Check if monster should be removed
                if update.get("action") == "defeated":
                    monsters_to_remove.append(monster_id)
                    
            except Exception as e:
                logging.error(f"Error updating monster {monster_id}: {e}")
                monsters_to_remove.append(monster_id)
        
        # Remove defeated monsters
        for monster_id in monsters_to_remove:
            del self.active_monsters[monster_id]
        
        # Spawn new monsters if needed
        self.spawn_timer += delta_time
        if self.spawn_timer >= self.spawn_interval and len(self.active_monsters) < self.max_monsters:
            self._spawn_random_monster()
            self.spawn_timer = 0
        
        return updates
    
    def _spawn_random_monster(self):
        """Spawn a random monster at a random spawn point"""
        if not self.spawn_points:
            return
        
        spawn_point = random.choice(self.spawn_points)
        monster_types = list(self.monster_templates.keys())
        monster_type = random.choice(monster_types)
        
        monster_id = self.spawn_monster(monster_type, spawn_point)
        if monster_id:
            logging.info(f"Spawned {monster_type} at {spawn_point}")
    
    def get_monster_state(self, monster_id: str) -> Optional[Dict]:
        """Get the state of a specific monster"""
        if monster_id in self.active_monsters:
            return self.active_monsters[monster_id].get_state()
        return None
    
    def damage_monster(self, monster_id: str, damage: int, attack_type: AttackType = AttackType.PHYSICAL,
                      status_effect: Optional[StatusEffect] = None, status_duration: float = 0) -> Optional[Dict]:
        """Damage a specific monster"""
        if monster_id in self.active_monsters:
            return self.active_monsters[monster_id].take_damage(damage, attack_type, status_effect, status_duration)
        return None

def test_monster_ai():
    """Test the monster AI system"""
    print("🐉 Monster Hunter Frontier G - Monster AI Test")
    print("=" * 60)
    
    # Create spawner
    spawner = MonsterSpawner()
    
    # Add spawn points
    spawner.add_spawn_point(Position(0, 0, 0))
    spawner.add_spawn_point(Position(10, 0, 10))
    spawner.add_spawn_point(Position(-10, 0, -10))
    
    # Spawn some monsters
    monster_id1 = spawner.spawn_monster("great_jaggi", Position(5, 0, 5))
    monster_id2 = spawner.spawn_monster("rathian", Position(-5, 0, -5))
    
    print(f"Spawned monsters: {monster_id1}, {monster_id2}")
    
    # Simulate players
    players = [
        {"id": "player1", "name": "Hunter1", "position": Position(6, 0, 6), "defense": 15},
        {"id": "player2", "name": "Hunter2", "position": Position(-6, 0, -6), "defense": 20}
    ]
    
    # Simulate combat
    for i in range(10):
        print(f"\n--- Round {i+1} ---")
        
        # Update monsters
        updates = spawner.update_monsters(1.0, players)
        
        for update in updates:
            print(f"Monster {update['monster_id']}: {update['action']}")
        
        # Damage monsters
        if monster_id1 in spawner.active_monsters:
            damage_result = spawner.damage_monster(monster_id1, 50, AttackType.FIRE)
            if damage_result:
                print(f"Great Jaggi took {damage_result['damage']} damage!")
        
        time.sleep(0.5)
    
    print("\n" + "=" * 60)
    print("✅ Monster AI System Test Complete!")
    print("🤖 Advanced monster behavior implemented!")
    print("⚔️ Ready for real-time combat!")

if __name__ == "__main__":
    test_monster_ai() 