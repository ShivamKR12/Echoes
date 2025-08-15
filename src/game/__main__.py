# Do not remove these lines
from setup_ursina_android import setup_ursina_android
setup_ursina_android()

from ursina import *
from ursina.prefabs.draggable import Draggable
from ursina.prefabs.health_bar import HealthBar
from ursina.sequence import Sequence
from ursina.ursinamath import lerp

app = Ursina()
window.vsync = False
window.borderless = True
window.fullscreen = True

main_menu = None
pause_menu = None
pause_button = None
game_started = False
player_alive = True
menu_background = None

ai_bots = []
bot_tasks = []
sequences  = []

joystick_move = None
joystick_look = None
button_jump = None
button_shoot = None

class VirtualJoystick(Entity):
    """
    An on-screen joystick control that:
      1. Scales its base and knob dynamically based on window size.
      2. Allows dragging within its circular radius.
      3. Reports a Vec2 value in the range [-1, +1].
    """
    def __init__(
        self,
        radius: float = 50,
        knob_factor: float = 2.5,
        position: tuple = (-.7, -.4),
        **kwargs
    ):
        super().__init__(parent=camera.ui, position=position, **kwargs)
        self.knob_factor = knob_factor

        # 1) Store pixel dimensions for base and knob
        self.diameter_px = radius * 2
        self.radius_px   = radius

        # 2) Capture initial window size for ratio calculations
        self._init_w, self._init_h = window.size

        # 3) Compute “base” UI-space scales (height-only)
        h = self._init_h or 1
        self._base_ui_diam   = (self.diameter_px / h) * 2
        self._base_ui_radius = (self.radius_px   / h) * 2

        # 4) Build visual elements
        self.bg = Entity(
            parent=self,
            model='circle',
            color=color.rgba32(64, 64, 64, 150)
        )
        self.knob = Draggable(
            parent=self,
            model='circle',
            color=color.white
        )
        self.knob.always_on_top   = True
        self.knob.start_position  = Vec2(0, 0)

        # 6) Current input value (Vec2)
        self.value = Vec2(0, 0)

        # 7) Initialize with no width-ratio scaling (ratio=1.0)
        self._apply_scale(1.0)

    def _apply_scale(self, ratio: float) -> None:
        """
        Apply dynamic scaling to:
          - self.scale    (joystick base diameter)
          - bg.scale      (fills its parent)
          - knob.scale    (knob diameter * knob_factor)
          - max_offset    (limit for dragging)
        """
        ui_d = self._base_ui_diam * ratio
        ui_r = self._base_ui_radius * ratio

        self.scale      = Vec2(ui_d, ui_d)
        self.bg.scale   = Vec2(1, 1)  # base circle fills parent Entity
        self.knob.scale = Vec2(ui_r * self.knob_factor,
                               ui_r * self.knob_factor)
        
        # update max_offset and logical radius here, once ui_r is known
        self.max_offset = (ui_r * self.knob_factor) / 2
        self.radius     = self.max_offset

    def update(self) -> None:
        # Recompute width-ratio if window width changed
        cur_w, _ = window.size
        ratio    = cur_w / (self._init_w or cur_w)
        self._apply_scale(ratio)

        # Begin dragging if mouse is held over the knob
        if held_keys['left mouse'] and mouse.hovered_entity == self.knob:
            self.knob.dragging = True

        # While dragging, clamp knob to circle and compute value
        if self.knob.dragging:
            offset = Vec2(self.knob.position.x, self.knob.position.y)
            if offset.length() > self.radius:
                offset = offset.normalized() * self.radius
            self.knob.position = offset
            self.value = offset / self.radius
        else:
            # Reset knob when released
            self.knob.position = self.knob.start_position
            self.value = Vec2(0, 0)

class VirtualButton(Button):
    """
    An on-screen button that:
      1. Scales dynamically with window width.
      2. Sets held_keys[key_name] on click and release.
    """
    def __init__(
        self,
        key_name: str = 'space',
        size_px: float = 40,
        position: tuple = (.7, -.4),
        color: Color = color.azure,
        **kwargs
    ):
        super().__init__(
            parent=camera.ui,
            model='circle',
            collider='box',
            position=position,
            color=color,
            **kwargs
        )
        self.key_name = key_name
        self.size_px  = size_px

        # 1) Store initial window dimensions
        self._init_w, self._init_h = window.size

        # 2) Compute base UI scale from height
        h = self._init_h or 1
        self._base_ui_size = (self.size_px / h) * 2

        # 3) Apply initial scale with no width-ratio change
        self.scale = self._base_ui_size

    def update(self) -> None:
        # Recompute width ratio and apply to scale
        cur_w, _ = window.size
        ratio    = cur_w / (self._init_w or cur_w)
        self.scale = self._base_ui_size * ratio

    def on_click(self) -> None:
        """Called when the user clicks the button."""
        held_keys[self.key_name] = 1
        input(self.key_name)

    def input(self, key: str) -> None:
        """Called on input events—used here to reset held_keys."""
        if key == f'{self.key_name} up':
            held_keys[self.key_name] = 0

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

class DynamicCrosshair(Entity):
    def __init__(self, player=None, line_length=0.03, line_thickness=0.002,
                 reticle_speed=5, reticle_distance=0.02, dot_scale=0.01, **kwargs):
        super().__init__(parent=camera.ui, position=(0,0))
        
        self.player = player  # reference to player entity
        self.reticle_speed = reticle_speed
        self.reticle_distance = reticle_distance

        # Shooting offset
        self.shoot_offset = 0

        # Center dot
        self.dot = Entity(parent=self, model='circle', color=color.white, scale=dot_scale, position=(0,0))

        # Create crosshair lines
        self.lines = {}
        self.lines['top'] = Entity(parent=self, model='quad', color=color.white,
                                   scale=(line_thickness, line_length), position=(0, line_length/2 + 0.01))
        self.lines['bottom'] = Entity(parent=self, model='quad', color=color.white,
                                      scale=(line_thickness, line_length), position=(0, -line_length/2 - 0.01))
        self.lines['left'] = Entity(parent=self, model='quad', color=color.white,
                                    scale=(line_length, line_thickness), position=(-line_length/2 - 0.01, 0))
        self.lines['right'] = Entity(parent=self, model='quad', color=color.white,
                                     scale=(line_length, line_thickness), position=(line_length/2 + 0.01, 0))
        
        # Store original positions for interpolation
        self.original_positions = {k: v.position for k,v in self.lines.items()}

    def update(self):
        # Player speed
        speed = getattr(self.player, 'velocity', Vec3(0,0,0)).length() if self.player else 1

        # Total offset = movement + shooting
        total_offset = speed * self.reticle_distance + self.shoot_offset

        for direction, line in self.lines.items():
            x, y = 0, 0
            if direction == 'top':
                y = self.original_positions['top'].y + total_offset
            elif direction == 'bottom':
                y = self.original_positions['bottom'].y - total_offset
            elif direction == 'left':
                x = self.original_positions['left'].x - total_offset
            elif direction == 'right':
                x = self.original_positions['right'].x + total_offset

            # Smoothly interpolate
            line.position = lerp(line.position, Vec3(x, y, 0), time.dt * self.reticle_speed)

        # Gradually decay shooting offset
        self.shoot_offset = lerp(self.shoot_offset, 0, time.dt * 10)

class FirstPersonController(Entity, HealthMixin):
    """
    A basic first-person character:
      - Mouse/touch look using virtual joysticks.
      - WASD or joystick movement with collision.
      - Jump, gravity, and optional gun shooting.
    """
    def __init__(self, **kwargs):
        super().__init__()

        HealthMixin.__init__(self, health=100)

        # 2) Movement parameters
        self.speed            = 5
        self.height           = 2
        self.camera_pivot     = Entity(parent=self, y=self.height)
        camera.parent        = self.camera_pivot
        camera.position      = (0, 0, 0)
        camera.rotation      = (0, 0, 0)
        camera.fov           = 90
        self.use_touch       = True
        mouse.locked         = False
        mouse.visible        = True
        self.mouse_sensitivity = Vec2(40, 40)

        # 3) Jump & gravity
        self.gravity          = 1
        self.grounded         = False
        self.jump_height      = 2
        self.jump_up_duration = .5
        self.fall_after       = .35
        self.air_time         = 0

        # 4) Collision setup
        self.traverse_target = scene
        self.ignore_list     = [self]
        self.gun             = None

        self._next_fire_time = 0

        # Create dynamic crosshair, passing self as the player reference
        self.crosshair = DynamicCrosshair(player=self)

        # Apply any overrides passed in
        for key, value in kwargs.items():
            setattr(self, key, value)

        # Snap to ground on spawn
        if self.gravity:
            ray = raycast(
                self.world_position + (0, self.height, 0),
                self.down,
                traverse_target=self.traverse_target,
                ignore=self.ignore_list
            )
            if ray.hit:
                self.y = ray.world_point.y

    def update(self) -> None:
        # 1) Look via right joystick
        if self.use_touch:
            rot = joystick_look.value
            yaw_gain   = 100
            pitch_gain = 100
            self.rotation_y += rot.x * time.dt * yaw_gain
            self.camera_pivot.rotation_x = clamp(
                self.camera_pivot.rotation_x - rot.y * time.dt * pitch_gain,
                -90,
                90
            )

        # 2) Move via left joystick
        move      = joystick_move.value
        direction = Vec3(self.forward * move.y + self.right * move.x).normalized()
        self.velocity = direction * self.speed  # Store velocity vector

        if direction:
            # Prevent walking through walls
            feet = raycast(
                self.position + Vec3(0, .5, 0),
                direction,
                traverse_target=self.traverse_target,
                ignore=self.ignore_list,
                distance=.5
            )
            head = raycast(
                self.position + Vec3(0, self.height - .1, 0),
                direction,
                traverse_target=self.traverse_target,
                ignore=self.ignore_list,
                distance=.5
            )
            if not (feet.hit or head.hit):
                self.position += direction * self.speed * time.dt

        # 3) Gravity & landing
        if self.gravity:
            down_ray = raycast(
                self.world_position + (0, self.height, 0),
                self.down,
                traverse_target=self.traverse_target,
                ignore=self.ignore_list
            )
            if down_ray.distance <= self.height + .1 and down_ray.world_normal.y > .7:
                if not self.grounded:
                    self.land()
                self.grounded = True
                self.y = down_ray.world_point.y
            else:
                self.grounded = False
                self.y -= min(
                    self.air_time,
                    down_ray.distance - .05
                ) * time.dt * 100
                self.air_time += time.dt * .25 * self.gravity

    def input(self, key: str) -> None:
        # Toggle touch controls
        if key == 't':
            self.use_touch  = not self.use_touch
            mouse.locked    = not self.use_touch

        # Jump
        if key in ('space', 'gamepad a'):
            self.jump()

        # Shoot (if gun equipped and not clicking UI)
        if key == 'left mouse down' and self.gun \
           and mouse.hovered_entity not in (
               joystick_move.knob,
               joystick_look.knob,
               button_jump,
               button_shoot,
               mouse.hovered_entity
           ):
            self.shoot()

        if key == 'gamepad x':
            self.shoot()

    def jump(self) -> None:
        """Animate a jump if grounded."""
        if not self.grounded:
            return
        self.grounded = False
        seq=self.animate_y(
            self.y + self.jump_height,
            self.jump_up_duration,
            resolution=int(1 // time.dt),
            curve=curve.out_expo
        )
        sequences.append(seq)
        invoke(self.start_fall, delay=self.fall_after)

    def start_fall(self) -> None:
        """Begin manual gravity animation after jump peak."""
        self.air_time += time.dt

    def land(self) -> None:
        """Reset air_time on landing."""
        self.air_time = 0
        self.grounded = True

    def shoot(self) -> None:
        """Fire a bullet from the equipped gun."""
        if not self.gun:
            return
        # Firing rate limit (cooldown)
        if hasattr(self, '_next_fire_time') and time.time() < self._next_fire_time:
            return
        self._next_fire_time = time.time() + 0.25  # 0.25s cooldown
        Audio('assets/gunshot.wav', loop=False, volume=0.2)
        self.gun.blink(color.gray)
        # Raycast for hit detection
        hit = raycast(
            camera.world_position,
            camera.forward,
            distance=100,
            traverse_target=scene,
            ignore=[self, self.gun]
        )
        bullet = Entity(
            parent=self.gun,
            model='cube',
            scale=0.2,
            position=(0.2, 0.1, 0),
            color=color.gold
        )
        bullet.world_parent = scene
        seq=bullet.animate_position(
            bullet.position + (camera.forward * 50),
            curve=curve.linear,
            duration=1
        )
        sequences.append(seq)
        destroy(bullet, delay=1)
        if hit.hit:
            target = hit.entity
            if hasattr(target, 'take_damage'):
                target.take_damage(50)
        
        self.crosshair.shoot_offset = 0.03  # Temporarily increase

    def take_damage(self, amount):
        super().take_damage(amount)
        if hasattr(self, 'health_bar'):
            self.health_bar.value = self.health

    def die(self):
        print("Player died!")
        self.health_bar.value = 0
        global player_alive
        player_alive = False
        destroy(self)  # Remove player entity
        invoke(game_over, delay=1)  # Delay to allow last frame effects (e.g. sounds)

class DummyTarget(Entity, HealthMixin):
    def __init__(self, **kwargs):
        super().__init__(
            model='cube',
            color=color.orange,
            collider='box',
            scale=(1, 2, 1),
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
        # remove the entire entity (model, collider, children, etc.)
        destroy(self)
        # if you had any generic respawning here, drop it
        # also destroy any bullets that are children or tracked globally
        for b in scene.entities:
            if isinstance(b, Entity) and getattr(b, 'collider', None) == 'box' and b.model.name == 'cube':
                destroy(b)

    # def die(self):
    #     print(f'{self} died.')
    #     # properly disable the whole node (model, collider, children)
    #     self.health_bar.disable()
    #     self.disable()
    #     invoke(self.respawn, delay=3)

    # def respawn(self):
    #     # re-enable the whole node (restores transform, collider, children)
    #     self.enable()
    #     # put it back at its spawn point
    #     self.position = self.spawn_point
    #     # reset any rotations / scales (avoid leftover singular transforms)
    #     self.rotation = Vec3(0, 0, 0)
    #     self.scale    = Vec3(1, 2, 1)

    #     # reset health & health bar
    #     self.health_bar.value = 100
    #     self.health_bar.enable()
    #     self.health = 100

    #     print(f'{self} respawned at {self.position}')

class AIBot(DummyTarget):
    def __init__(self, patrol_area=(10, 10), chase_range=5, speed = 1, **kwargs):
        super().__init__(**kwargs)
        self.patrol_area = patrol_area
        self.chase_range = chase_range
        self.speed = speed
        self.fire_interval = 3     # seconds between shots
        self._next_fire_time = 0
        self.alive = True
        self.is_chasing = False

        self.gun = Entity(
            parent=self,
            model='assets/pistol.gltf',
            color= color.gray.tint(-.2),
            position=Vec3(.2, .1, .8),  # adjust for hand offset
            rotation=Vec3(0, 0, 0),
            scale=0.1,
        )

        self.target_pos = self.get_valid_ground_position()
        self.update_task = invoke(self.patrol, delay=1)
        ai_bots.append(self)
        bot_tasks.append(self.update_task)

    def patrol(self):
        if not getattr(self, 'enabled', False) or not getattr(self, 'alive', False):
            return
        if not self.alive:
            return
        if not player_alive or not player or not player.enabled:
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
        for other in ai_bots:
            if other is not self and distance(self.position, other.position) < 1.5:
                blocked = True
                break
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
        Audio('assets/gunshot.wav', loop=False, volume=0.2)

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
            # Raycast ahead of the bullet's current path
            hit_info = raycast(
                origin=b.position,
                direction=b.forward,
                distance=b.speed * time.dt,
                ignore=[b, self] + ai_bots,
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
            if distance(b.position, player.position) < 1.0:
                if hasattr(player, 'take_damage'):
                    player.take_damage(10)
                destroy(b)
            elif distance(b.position, self.position) > 50:
                destroy(b)

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
            Audio('assets/gunshot.wav', loop=False, volume=0.2)
            self._next_fire_time = time.time() + self.fire_interval
    
    def die(self):
        print(f'{self} died.')
        super().die()
        # stop its patrol task
        if hasattr(self, 'update_task'):
            self.update_task.pause()
        # remove from our global lists
        if self in ai_bots:      ai_bots.remove(self)
        if self.update_task in bot_tasks:  bot_tasks.remove(self.update_task)
        # destroy this instance
        destroy(self)
        # spawn a brand-new bot after 3 seconds at the same spawn_point
        invoke(lambda: AIBot(
            patrol_area=self.patrol_area,
            chase_range=self.chase_range,
            speed=self.speed,
            position=self.spawn_point
        ), delay=3)

    # def die(self):
    #     print(f'{self} died.')
    #     super().die()
    #     self.alive = False
    #     if hasattr(self, 'update_task'):
    #         self.update_task.finish()

    # def respawn(self):
    #     # 1) do the standard enable/transform/health reset
    #     super().respawn()

    #     # 2) restore AIBot-specific flags
    #     self.alive = True
    #     self.target_pos = self.get_valid_ground_position()

    #     # 3) re-schedule patrol
    #     self.update_task = invoke(self.patrol, delay=1)
    #     print(f'{self} patrol re-scheduled:', self.update_task)

def show_main_menu():
    global main_menu, menu_background

    for s in list(Sky.instances):
        destroy(s)
    Sky.instances.clear()

    # Create full-screen background image
    menu_background = Entity(
        parent=camera.ui,
        model='quad',
        texture='assets/label.jpg',
        scale=(2, 1),  # Full screen
        z=1  # Send it to back (higher z = farther back in UI)
    )
    
    main_menu = Entity(parent=camera.ui)

    Text("Main Menu", scale=2, x=-0.125, y=0.4, parent=main_menu)

    Button(
        text='Singleplayer',
        scale=(.3, .1),
        y=0.15,
        parent=main_menu,
        on_click=start_singleplayer
    )

    Button(
        text='Multiplayer',
        scale=(.3, .1),
        y=-0.05,
        parent=main_menu,
        on_click=lambda: print("Multiplayer not implemented.")
    )

    Button(
        text='Exit',
        scale=(.3, .1),
        y=-0.25,
        parent=main_menu,
        on_click=application.quit
    )

def show_pause_menu():
    global pause_menu
    pause_menu = Entity(parent=camera.ui)

    Text("Paused", scale=2, x=-0.1, y=0.3, parent=pause_menu)

    Button(
        text='Resume',
        scale=(.3, .1),
        y=0.1,
        parent=pause_menu,
        on_click=resume_game
    )

    Button(
        text='Quit to Menu',
        scale=(.3, .1),
        y=-0.1,
        parent=pause_menu,
        on_click=quit_to_main_menu
    )

def start_singleplayer():
    global game_started, menu_background, main_menu, player_alive

    application.resume()

    # Reset the “am I alive?” flag
    player_alive = True

    # Clean up old bots & tasks
    for t in bot_tasks:
        t.finish()
    bot_tasks.clear()
    for b in ai_bots:
        destroy(b)
    ai_bots.clear()
    for seq in sequences:
        if isinstance(seq, Sequence):
            seq.finish()
    sequences.clear()

    # Tear down menus
    destroy(main_menu)
    destroy(menu_background)

    game_started = True
    setup_game()  # existing function that sets up map, player, bots, etc.

def pause_game():
    application.pause()
    pause_button.enabled = False
    show_pause_menu()

def resume_game():
    application.resume()
    destroy(pause_menu)
    pause_button.enabled = True

def quit_to_main_menu():

    def cleanup():
        global player, bot_tasks, ai_bots, sequences, pause_menu, main_menu, menu_background

        # 1) Pause the app to stop new tasks/animations
        application.pause()

        # 2) Finish & clear *all* Sequences (including any HealthBar tweens)
        for seq in list(sequences):
            if isinstance(seq, Sequence):
                seq.finish()
        sequences.clear()

        # 3) Finish any lingering bot or AI tasks
        for t in list(bot_tasks):
            t.finish()
        bot_tasks.clear()

        # 4) Destroy every AI bot instance
        for b in list(ai_bots):
            destroy(b)
        ai_bots.clear()

        # 5) Destroy the player (and its entire sub‐hierarchy)
        if player:
            destroy(player)
            player = None

        # 6) Destroy *every* entity in the main scene
        #    (this hits ground, buildings, walls, bullets, etc.)
        for e in list(scene.entities):
            destroy(e)

        # 7) Destroy *every* UI element under camera.ui
        for e in list(camera.ui.children):
            destroy(e)

        # 8) Destroy any remaining sky instances & lights
        for s in list(Sky.instances):
            destroy(s)
        Sky.instances.clear()

        # 9) Teardown menus or background if somehow left
        for ui_root in (main_menu, menu_background, pause_menu):
            if ui_root:
                destroy(ui_root)
        main_menu = None
        menu_background = None
        pause_menu = None

        # 10) Clear any leftover application state
        sequences.clear()
        bot_tasks.clear()
        ai_bots.clear()

        # 11) Un‐pause so input works again, then show the menu
        application.resume()
        show_main_menu()

    # Schedule on next frame to avoid “half‐destroyed” warnings
    invoke(cleanup, delay=0)

def game_over():
    global pause_button
    print("Game Over - Returning to Main Menu")
    # Safely disable pause_button if it exists and is valid
    if pause_button and hasattr(pause_button, 'enabled') and pause_button.enabled:
        try:
            pause_button.enabled = False
        except Exception as e:
            print(f"Could not disable pause_button: {e}")
    # cancel all bot‑patrol invokes
    for t in bot_tasks:    t.finish()
    bot_tasks.clear()

    # destroy remaining bots
    for b in ai_bots:      destroy(b)
    ai_bots.clear()

    # cancel all animations
    for item in sequences:
        if isinstance(item, Sequence):
            item.finish()
    sequences.clear()
    # Destroy all scene entities except the camera and UI
    for e in scene.entities:
        destroy(e)
    # Clear UI except pause button (optional)
    for e in camera.ui.children:
        if e != pause_button:
            destroy(e)
    show_main_menu()

def setup_game():
    global player, pause_button
    global joystick_move, joystick_look, button_jump, button_shoot

    # Instantiate touch controls
    joystick_move  = VirtualJoystick(position=(-.7, -.3))
    joystick_look  = VirtualJoystick(position=( .3, -.3))
    button_jump    = VirtualButton('gamepad a', position=( .6, -.1), color=color.lime)
    button_shoot   = VirtualButton('gamepad x', position=( .8, -.2), color=color.red)

    pause_button = Button(texture='cog', scale=(.08, .08), position=(-0.85, 0.45), origin=(-0.5, 0.5), parent=camera.ui, color=color.gray, on_click=pause_game)

    # Touch controls
    joystick_move.enabled = True
    joystick_look.enabled = True
    button_jump.enabled = True
    button_shoot.enabled = True
    pause_button.enabled = True

    # Add environment
    ground = Entity(model='cube', scale=(30, 1, 30), color=color.rgb(237/255, 201/255, 175/255), texture='white_cube', texture_scale=(30, 30), collider='box')

    house1 = Entity(model='assets/building_01.gltf', position=(-4, 0.5, -4), rotation=(0, 0, 0), scale=(1, 1, 1), collider='box')
    house2 = Entity(model='assets/building_01.gltf', position=( 4, 0.5, -4), rotation=(0, 0, 0), scale=(1, 1, 1), collider='box')
    house3 = Entity(model='assets/building_01.gltf', position=(-4, 0.5,  4), rotation=(0, 0, 0), scale=(1, 1, 1), collider='box')
    house4 = Entity(model='assets/building_01.gltf', position=( 4, 0.5,  4), rotation=(0, 0, 0), scale=(1, 1, 1), collider='box')

    # ──────────────── Top Wall (North) ────────────────
    wall_n1 = Entity(model='assets/wall_03.gltf', position=(-10, 0.5, 15), rotation=(0, 0, 0), scale=1, collider='box')
    wall_n2 = Entity(model='assets/wall_03.gltf', position=(  0, 0.5, 15), rotation=(0, 0, 0), scale=1, collider='box')
    wall_n3 = Entity(model='assets/wall_03.gltf', position=( 10, 0.5, 15), rotation=(0, 0, 0), scale=1, collider='box')

    # ──────────────── Bottom Wall (South) ────────────────
    wall_s1 = Entity(model='assets/wall_03.gltf', position=(-10, 0.5, -15), rotation=(0, 0, 0), scale=1, collider='box')
    wall_s2 = Entity(model='assets/wall_03.gltf', position=(  0, 0.5, -15), rotation=(0, 0, 0), scale=1, collider='box')
    wall_s3 = Entity(model='assets/wall_03.gltf', position=( 10, 0.5, -15), rotation=(0, 0, 0), scale=1, collider='box')

    # ──────────────── Left Wall (West) ────────────────
    wall_w1 = Entity(model='assets/wall_03.gltf', position=(-15, 0.5, -10), rotation=(0, 90, 0), scale=1, collider='box')
    wall_w2 = Entity(model='assets/wall_03.gltf', position=(-15, 0.5,   0), rotation=(0, 90, 0), scale=1, collider='box')
    wall_w3 = Entity(model='assets/wall_03.gltf', position=(-15, 0.5,  10), rotation=(0, 90, 0), scale=1, collider='box')

    # ──────────────── Right Wall (East) ────────────────
    wall_e1 = Entity(model='assets/wall_03.gltf', position=(15, 0.5, -10), rotation=(0, 90, 0), scale=1, collider='box')
    wall_e2 = Entity(model='assets/wall_03.gltf', position=(15, 0.5,   0), rotation=(0, 90, 0), scale=1, collider='box')
    wall_e3 = Entity(model='assets/wall_03.gltf', position=(15, 0.5,  10), rotation=(0, 90, 0), scale=1, collider='box')

    # ──────────────── North Flank Walls (between top wall and top houses) ────────────────
    north_fw1 = Entity(model='assets/wall_01.gltf', position=(-6, 0.5, 10), rotation=(0, 0, 0), scale=1, collider='box')
    north_fw2 = Entity(model='assets/wall_01.gltf', position=( 0, 0.5, 11), rotation=(0, 0, 0), scale=1, collider='box')  # middle slightly forward
    north_fw3 = Entity(model='assets/wall_01.gltf', position=( 6, 0.5, 10), rotation=(0, 0, 0), scale=1, collider='box')

    # ──────────────── South Flank Walls (between bottom wall and bottom houses) ────────────────
    south_fw1 = Entity(model='assets/wall_01.gltf', position=(-6, 0.5, -10), rotation=(0, 0, 0), scale=1, collider='box')
    south_fw2 = Entity(model='assets/wall_01.gltf', position=( 0, 0.5, -11), rotation=(0, 0, 0), scale=1, collider='box')  # middle forward
    south_fw3 = Entity(model='assets/wall_01.gltf', position=( 6, 0.5, -10), rotation=(0, 0, 0), scale=1, collider='box')

    # ──────────────── West Flank Walls (between left wall and left houses) ────────────────
    west_fw1 = Entity(model='assets/wall_01.gltf', position=(-10, 0.5, -6), rotation=(0, 90, 0), scale=1, collider='box')
    west_fw2 = Entity(model='assets/wall_01.gltf', position=(-11, 0.5,  0), rotation=(0, 90, 0), scale=1, collider='box')  # middle pushed left
    west_fw3 = Entity(model='assets/wall_01.gltf', position=(-10, 0.5,  6), rotation=(0, 90, 0), scale=1, collider='box')

    # ──────────────── East Flank Walls (between right wall and right houses) ────────────────
    east_fw1 = Entity(model='assets/wall_01.gltf', position=(10, 0.5, -6), rotation=(0, 90, 0), scale=1, collider='box')
    east_fw2 = Entity(model='assets/wall_01.gltf', position=(11, 0.5,  0), rotation=(0, 90, 0), scale=1, collider='box')  # middle pushed right
    east_fw3 = Entity(model='assets/wall_01.gltf', position=(10, 0.5,  6), rotation=(0, 90, 0), scale=1, collider='box')

    # Player and gun setup
    player = FirstPersonController(y=2, origin_y=-.5)
    player.health_bar = HealthBar(max_value=100, value=100, bar_color=color.green.tint(-.2), scale=(.4, .03), position=(-.5, .45), roundness=.5, show_text=True, parent=camera.ui)

    # Gun pickup
    gun = Button(parent=scene, model='assets/pistol.gltf', position=(1, 1, 1), collider='box', scale=0.1, color=color.gray.tint(-.2))
    gun.on_click = lambda: (
        setattr(gun, 'parent', camera),
        setattr(gun, 'position', Vec3(0.2, -0.2, 2)),
        setattr(gun, 'rotation', Vec3(0, 0, 0)),
        setattr(gun, 'scale', Vec3(0.3, 0.3, 0.3)),
        setattr(player, 'gun', gun)
    )

    # ──────────────── AI Bots ────────────────

    # Top left corner (free of houses/walls)
    AIBot(position=(-10, 1, 10), patrol_area=(4, 4), chase_range=12, speed=1)

    # Bottom right corner
    AIBot(position=(10, 1, -10), patrol_area=(4, 4), chase_range=8, speed=1)

    # Middle-left flank area
    AIBot(position=(-10, 1, 0), patrol_area=(3, 5), chase_range=0, speed=1)

    # Middle-right flank area
    AIBot(position=(10, 1, 0), patrol_area=(3, 5), chase_range=4, speed=1)

    # Bottom-center between houses and wall
    AIBot(position=(0, 1, -12), patrol_area=(5, 3), chase_range=5, speed=1)

    # Bind buttons
    button_jump.on_click = player.jump
    button_shoot.on_click = player.shoot

    Sky()

def update():
    if mouse.left and isinstance(mouse.hovered_entity, Button):
        return

show_main_menu()
app.run()
