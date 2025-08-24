from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.prefabs.health_bar import HealthBar
from direct.actor.Actor import Actor
import simplepbr

app = Ursina()

simplepbr.init()

class HealthMixin:
    def __init__(self, health=100, **kwargs):
        super().__init__(**kwargs)
        self.health = health

    def take_damage(self, amount):
        self.health -= amount
        print(f'{self} took {amount} damage. Remaining health: {self.health}')
        if self.health <= 0:
            self.die()

    def die(self):
        print(f'{self} died.')
        destroy(self)

class DummyTarget(Entity, HealthMixin):
    def __init__(self, **kwargs):
        super().__init__(
            collider='box',
            scale=0.005,
            name='dummy_target',
            **kwargs
        )
        HealthMixin.__init__(self, health=100)
        self.spawn_point = self.position
        self.visible = True
        self.enabled = True

        self.health_bar = HealthBar(
            max_value=100,
            value=100,
            scale=(.3, .02),
            bar_color=color.red.tint(-.2),
            roundness=.5,
            show_text=False,
            parent=self
        )
        self.health_bar.x = 0.1
        self.health_bar.y = 1  # position it above the target
        # self.health_bar.z = -0.01  # prevent z-fighting
        self.health_bar.billboard=True

    def take_damage(self, amount):
        if not self.enabled:             # ignore damage if already “dead”
            return
        super().take_damage(amount)
        # only update the bar if it still exists in the scene graph
        try:
            if hasattr(self, 'health_bar') and self.health_bar and self.health_bar.enabled:
                self.health_bar.value = self.health
        except AssertionError as e:
            # health_bar node no longer valid—ignore
            print(f"Health bar error: {e}")
            pass
    
    def die(self):
        print(f'{self} died.')
        self.alive = False
        self.set_animation('Death', loop=False)
        invoke(lambda: destroy(self), delay=2.0)
        # if you had any generic respawning here, drop it
        # also destroy any bullets that are children or tracked globally
        for b in scene.entities:
            if isinstance(b, Entity) and getattr(b, 'collider', None) == 'box' and b.model.name == 'cube':
                destroy(b)

class AIBot(DummyTarget):
    def __init__(self, patrol_area=(10, 10), chase_range=5, speed = 5, **kwargs):
        super().__init__(**kwargs)
        self.patrol_area = patrol_area
        self.chase_range = chase_range
        self.speed = speed
        self.fire_interval = 3     # seconds between shots
        self._next_fire_time = 0
        self.alive = True
        self.is_chasing = False
        self.state = 'idle'

        # Replace normal model with Actor
        self.actor = Actor('assets/newcharact.glb')
        self.actor.reparent_to(self)
        self.actor.loop('RifleIdle')

        self.gun = Entity(
            parent=self,
            model='assets/pistol.gltf',
            color= color.gray.tint(-.2),
            position=Vec3(.2, .1, .8),  # adjust for hand offset
            rotation=Vec3(0, 0, 0),
            scale=0.1,
            name='ai_gun'
        )

        self.target_pos = self.get_valid_ground_position()
        self.update_task = invoke(self.patrol, delay=1)

    def set_animation(self, anim_name, loop=True):
        """Change animation only if different from current."""
        current_anim = self.actor.getCurrentAnim()
        if current_anim != anim_name:
            if loop:
                self.actor.loop(anim_name)
            else:
                self.actor.play(anim_name)
    
    def patrol(self):
        if not getattr(self, 'enabled', False) or not getattr(self, 'alive', False):
            return
        if not self.alive:
            return
        if not player or not player.enabled:
            return

        # 1. Determine target: chase player or patrol
        dist_to_player = distance(self.position, player.position)
        if dist_to_player < self.chase_range:
            self.target_pos = player.position
            self.is_chasing = True
        else:
            self.is_chasing = False
            if distance(self.position, self.target_pos) < 0.5:
                self.target_pos = self.get_valid_ground_position()

        move_dir = (self.target_pos - self.position).normalized()

        # Determine animation state
        if self.is_chasing:
            self.set_animation('RifleRun')
        else:
            if distance(self.position, self.target_pos) > 0.5:
                self.set_animation('RifleWalk')
            else:
                self.set_animation('RifleIdle')

        # 2. Wall detection
        front_ray = raycast(
            self.position + Vec3(0, 0.5, 0),
            move_dir,
            distance=0.6,
            ignore=[self],
            traverse_target=scene
        )
        if front_ray.hit and not self.is_chasing:
            # print("Wall ahead. Choosing new target.")
            self.target_pos = self.get_valid_ground_position()
            move_dir = (self.target_pos - self.position).normalized()
            # Recalculate front ray with new direction
            front_ray = raycast(
                self.position + Vec3(0, 0.5, 0),
                move_dir,
                distance=0.6,
                ignore=[self],
                traverse_target=scene
            )

        # 3. Avoid player and other bots
        blocked = False
        if distance(self.position, player.position) < 1.5:
            blocked = True

        # 4. Move if clear
        if not blocked and not front_ray.hit:
            self.position += move_dir * self.speed * time.dt

        # 5. Keep grounded
        down_ray = raycast(
            self.position + Vec3(0, 0.5, 0),
            direction=Vec3(0, -1, 0),
            ignore=[self],
            traverse_target=scene
        )
        if down_ray.hit:
            self.y = down_ray.world_point.y + 1

        if self.is_chasing:
            # Rotate the bot to look at the player
            self.look_at(player.position)
            self.rotation_x = 0  # keep upright
            self.rotation_z = 0
            self.shoot()

        self.update_task = invoke(self.patrol, delay=0.1)

    def get_valid_ground_position(self, max_attempts=10):
        for _ in range(max_attempts):
            x = random.uniform(-self.patrol_area[0], self.patrol_area[0])
            z = random.uniform(-self.patrol_area[1], self.patrol_area[1])
            test_pos = Vec3(x, 20, z)
            # print(f"Trying position: ({x}, 20, {z})")
            ground_ray = raycast(
                test_pos,
                direction=Vec3(0, -1, 0),
                distance=50,
                ignore=[self],
                traverse_target=scene
            )
            # print(f"Ground ray: {ground_ray}")
            # print(f"Ground ray hit: {ground_ray.hit}, world point: {ground_ray.world_point}")
            if ground_ray.hit:
                y = ground_ray.world_point.y + 1
                # print(f"Valid ground found at: ({x}, {y}, {z})")
                return Vec3(x, y, z)
        print("Failed to find valid ground. Returning origin.")
        print(f"Last attempted position: ({x}, 20, {z})")
        return Vec3(0, 1, 0)
    
    def shoot(self):
        if not self.alive or not player or not self.enabled or time.time() < self._next_fire_time:
            return
        
        self._next_fire_time = time.time() + self.fire_interval

        # Play shooting animation once
        self.set_animation('FiringRifle', loop=False)

        # After shooting, return to correct movement animation
        def reset_anim():
            if self.is_chasing:
                self.set_animation('RifleRun')
            else:
                self.set_animation('RifleWalk')
        invoke(reset_anim, delay=0.9)  # delay matches shooting animation duration

        # Raycast toward player
        dir_to_player = (player.position - self.position).normalized()
        eye_pos = self.position + Vec3(-.1, .5, .3)  # AI eye height

        bullet = Entity(
            model='cube',
            color=color.gold,
            scale=0.2,
            position=eye_pos,
            collider='box',
            speed=30,
            name='ai_bullet'
        )
        bullet.world_parent = scene
        # Make the bullet face the direction to player
        bullet.look_at(player.position)

        def bullet_update(b=bullet):
            if not b or not b.enabled:
                return
            # Check if player exists and is not destroyed
            if not player or not hasattr(player, 'position') or player in scene.entities and player.enabled == False:
                destroy(b)
                return
            # Check if AI (self) still exists and is enabled
            if not self or not hasattr(self, 'position') or not self.enabled:
                destroy(b)
                return
            # Raycast ahead of the bullet's current path
            hit_info = raycast(
                origin=b.position,
                direction=b.forward,
                distance=b.speed * time.dt,
                ignore=[b, self],
                traverse_target=scene
            )
            if hit_info.hit:
                if hit_info.entity == player:
                    if hasattr(player, 'take_damage'):
                        player.take_damage(10)
                    print("Bullet hit the player")
                else:
                    print(f"Bullet hit: {hit_info.entity}")
                destroy(b)
                return
            b.position += b.forward * b.speed * time.dt

            # Check bullet proximity to player safely
            if player and hasattr(player, 'position') and distance(b.position, player.position) < 1.0:
                if hasattr(player, 'take_damage'):
                    player.take_damage(10)
                destroy(b)
                return

            # Check if bullet is too far from AI
            if self and hasattr(self, 'position') and distance(b.position, self.position) > 50:
                destroy(b)
                return

        bullet.update = bullet_update

        hit = raycast(
            origin=eye_pos,
            direction=dir_to_player,
            distance=50,
            ignore=[self],
            traverse_target=scene
        )

        if hit.hit and hit.entity == player:
            print(f"{self} shot the player!")
            player.take_damage(10)
            self._next_fire_time = time.time() + self.fire_interval
    
    def die(self):
        print(f'{self} died.')
        super().die()
        # stop its patrol task
        if hasattr(self, 'update_task'):
            self.update_task.pause()
        # destroy this instance
        destroy(self)
        # spawn a brand-new bot after 3 seconds at the same spawn_point
        invoke(lambda: AIBot(
            patrol_area=self.patrol_area,
            chase_range=self.chase_range,
            speed=self.speed,
            position=self.spawn_point
        ), delay=3)


# Double-size open map — 60 × 60 (simple, direct expansion)

# ground (make one big ground)
ground = Entity(name='ground', model='cube', scale=(60,1,60), position=(0,0,0),
                texture='white_cube', texture_scale=(60,60), collider='box')

# outer walls: horizontal segments length 10 each.
# Top and bottom at z = +30 / -30 (centers). To cover -30..+30 need 6 segments at x = -25,-15,-5,5,15,25.
for cx in (-25,-15,-5,5,15,25):
    Entity(model='assets/wall_03.gltf', position=(cx,0.5,30), rotation=(0,0,0), scale=1, collider='box')
    Entity(model='assets/wall_03.gltf', position=(cx,0.5,-30), rotation=(0,0,0), scale=1, collider='box')

# Left/Right vertical outer walls: rotate 90 degrees; centers at x = ±30, z = -25..25 (same centers)
for cz in (-25,-15,-5,5,15,25):
    Entity(model='assets/wall_03.gltf', position=(-30,0,5,cz)[0:3], rotation=(0,90,0), scale=1, collider='box')
    # above line is shorthand; in practice:
    Entity(model='assets/wall_03.gltf', position=(-30,0.5,cz), rotation=(0,90,0), scale=1, collider='box')
    Entity(model='assets/wall_03.gltf', position=( 30,0.5,cz), rotation=(0,90,0), scale=1, collider='box')

# Houses: a 3×3 grid centered in the middle, centers at x,z = -10,0,10
for hx in (-10, 0, 10):
    for hz in (-10, 0, 10):
        Entity(name=f'house_{hx}_{hz}', model='assets/building_01.gltf',
            position=(hx,0.5,hz), rotation=(0,0,0), scale=1, collider='box')

# Flank walls (short 5-unit pieces) placed as inner fences between outer bounds and houses.
# Example: north row at z = +20, centers x = -20,-10,0,10,20  (creates passable ~1-unit gaps)
for cx in (-20,-10,0,10,20):
    Entity(model='assets/wall_01.gltf', position=(cx,0.5,20), rotation=(0,0,0), scale=1, collider='box')
    Entity(model='assets/wall_01.gltf', position=(cx,0.5,-20), rotation=(0,0,0), scale=1, collider='box')

# West/East flank walls (vertical orientation): centers at x = -20 and 20, z = -20,-10,0,10,20
for cz in (-20,-10,0,10,20):
    Entity(model='assets/wall_01.gltf', position=(-20,0.5,cz), rotation=(0,90,0), scale=1, collider='box')
    Entity(model='assets/wall_01.gltf', position=( 20,0.5,cz), rotation=(0,90,0), scale=1, collider='box')

# ──────────────── AI Bots ────────────────

# Top left corner (free of houses/walls)
AIBot(position=(-10, 10, 10), patrol_area=(4, 4), chase_range=12, speed=7)

# Bottom right corner
AIBot(position=(10, 10, -10), patrol_area=(4, 4), chase_range=8, speed=4)
  
# Middle-left flank area
AIBot(position=(-10, 10, 0), patrol_area=(3, 5), chase_range=10, speed=6)

# Middle-right flank area
AIBot(position=(10, 10, 0), patrol_area=(3, 5), chase_range=13, speed=8)

# Bottom-center between houses and wall
AIBot(position=(0, 10, -12), patrol_area=(5, 3), chase_range=15, speed=10)

player = FirstPersonController()

app.run()