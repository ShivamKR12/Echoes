# Do not remove these lines
from setup_ursina_android import setup_ursina_android
print("Imported setup_ursina_android module for Android configuration")
setup_ursina_android()
print("Executed setup_ursina_android to set up Ursina for mobile/Android")

from ursina import *
print("Imported all modules from ursina package")
from ursina.prefabs.draggable import Draggable
print("Imported Draggable prefab from ursina")
from ursina.prefabs.health_bar import HealthBar
print("Imported HealthBar prefab from ursina")
from ursina.sequence import Sequence
print("Imported Sequence class from ursina")
from ursina.ursinamath import lerp, distance
print("Imported lerp and distance functions from ursina.ursinamath")
import random
print("Imported random module for random number generation")

app = Ursina()
print("Created Ursina application instance")
window.vsync = False
print("Disabled VSync for window to potentially improve performance")

main_menu = None
print("Initialized main_menu to None")
pause_menu = None
print("Initialized pause_menu to None")
settings_menu = None
print("Initialized settings_menu to None")
pause_button = None
print("Initialized pause_button to None")
settings_button = None
print("Initialized settings_button to None")
game_started = False
print("Initialized game_started to False")
player_alive = True
print("Initialized player_alive to True")
menu_background = None
print("Initialized menu_background to None")

# Global slider variables for settings menu
speed_slider = None
print("Initialized speed_slider to None")
jump_slider = None
print("Initialized jump_slider to None")
sensx_slider = None
print("Initialized sensx_slider to None")
sensy_slider = None
print("Initialized sensy_slider to None")
volume_slider = None
print("Initialized volume_slider to None")
joystick_move_posx_slider = None
print("Initialized joystick_move_posx_slider to None")
joystick_move_posy_slider = None
print("Initialized joystick_move_posy_slider to None")
joystick_move_scale_slider = None
print("Initialized joystick_move_scale_slider to None")
joystick_look_posx_slider = None
print("Initialized joystick_look_posx_slider to None")
joystick_look_posy_slider = None
print("Initialized joystick_look_posy_slider to None")
joystick_look_scale_slider = None
print("Initialized joystick_look_scale_slider to None")

ai_bots = []
print("Initialized ai_bots as empty list")
bot_tasks = []
print("Initialized bot_tasks as empty list")
sequences  = []
print("Initialized sequences as empty list")

joystick_move = None
print("Initialized joystick_move to None")
joystick_look = None
print("Initialized joystick_look to None")
button_jump = None
print("Initialized button_jump to None")
button_shoot = None
print("Initialized button_shoot to None")

gunshot = Audio('assets/gunshot.wav', loop=False, autoplay=False, volume=0.2)
print("Loaded gunshot audio with volume 0.2")

# Preload models
preload = {}
preload['bullet'] = load_model('assets/bullet.gltf')
print("Preloaded bullet model")

# Buildings
preload['house1'] = load_model('assets/building_01.gltf')
print("Preloaded house1 model")
preload['house2'] = load_model('assets/building_01.gltf')
print("Preloaded house2 model")
preload['house3'] = load_model('assets/building_01.gltf')
print("Preloaded house3 model")
preload['house4'] = load_model('assets/building_01.gltf')
print("Preloaded house4 model")

# Top Wall (North)
preload['wall_n1'] = load_model('assets/wall_03.gltf')
print("Preloaded wall_n1 model")
preload['wall_n2'] = load_model('assets/wall_03.gltf')
print("Preloaded wall_n2 model")
preload['wall_n3'] = load_model('assets/wall_03.gltf')
print("Preloaded wall_n3 model")

# Bottom Wall (South)
preload['wall_s1'] = load_model('assets/wall_03.gltf')
print("Preloaded wall_s1 model")
preload['wall_s2'] = load_model('assets/wall_03.gltf')
print("Preloaded wall_s2 model")
preload['wall_s3'] = load_model('assets/wall_03.gltf')
print("Preloaded wall_s3 model")

# Left Wall (West)
preload['wall_w1'] = load_model('assets/wall_03.gltf')
print("Preloaded wall_w1 model")
preload['wall_w2'] = load_model('assets/wall_03.gltf')
print("Preloaded wall_w2 model")
preload['wall_w3'] = load_model('assets/wall_03.gltf')
print("Preloaded wall_w3 model")

# Right Wall (East)
preload['wall_e1'] = load_model('assets/wall_03.gltf')
print("Preloaded wall_e1 model")
preload['wall_e2'] = load_model('assets/wall_03.gltf')
print("Preloaded wall_e2 model")
preload['wall_e3'] = load_model('assets/wall_03.gltf')
print("Preloaded wall_e3 model")

# North Flank Walls
preload['north_fw1'] = load_model('assets/wall_01.gltf')
print("Preloaded north_fw1 model")
preload['north_fw2'] = load_model('assets/wall_01.gltf')
print("Preloaded north_fw2 model")
preload['north_fw3'] = load_model('assets/wall_01.gltf')
print("Preloaded north_fw3 model")

# South Flank Walls
preload['south_fw1'] = load_model('assets/wall_01.gltf')
print("Preloaded south_fw1 model")
preload['south_fw2'] = load_model('assets/wall_01.gltf')
print("Preloaded south_fw2 model")
preload['south_fw3'] = load_model('assets/wall_01.gltf')
print("Preloaded south_fw3 model")

# West Flank Walls
preload['west_fw1'] = load_model('assets/wall_01.gltf')
print("Preloaded west_fw1 model")
preload['west_fw2'] = load_model('assets/wall_01.gltf')
print("Preloaded west_fw2 model")
preload['west_fw3'] = load_model('assets/wall_01.gltf')
print("Preloaded west_fw3 model")

# East Flank Walls
preload['east_fw1'] = load_model('assets/wall_01.gltf')
print("Preloaded east_fw1 model")
preload['east_fw2'] = load_model('assets/wall_01.gltf')
print("Preloaded east_fw2 model")
preload['east_fw3'] = load_model('assets/wall_01.gltf')
print("Preloaded east_fw3 model")

print("Completed preloading all models")

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
        print(f"Initializing VirtualJoystick with radius={radius}, knob_factor={knob_factor}, position={position}", f"kwargs={kwargs}")
        print("VirtualJoystick __init__: Called super().__init__")
        super().__init__(parent=camera.ui, position=position, **kwargs)
        print("VirtualJoystick __init__: Set knob_factor")
        self.knob_factor = knob_factor
        print("VirtualJoystick __init__: Stored pixel dimensions")
        # 1) Store pixel dimensions for base and knob
        self.diameter_px = radius * 2
        print("VirtualJoystick __init__: Set diameter_px")
        self.radius_px   = radius
        print("VirtualJoystick __init__: Set radius_px")
        # 2) Capture initial window size for ratio calculations
        self._init_w, self._init_h = window.size
        print("VirtualJoystick __init__: Captured initial window size")
        # 3) Compute “base” UI-space scales (height-only)
        h = self._init_h or 1
        print("VirtualJoystick __init__: Computed h")
        self._base_ui_diam   = (self.diameter_px / h) * 2
        print("VirtualJoystick __init__: Set _base_ui_diam")
        self._base_ui_radius = (self.radius_px   / h) * 2
        print("VirtualJoystick __init__: Set _base_ui_radius")
        # 4) Build visual elements
        self.bg = Entity(
            parent=self,
            model='circle',
            color=color.rgba32(64, 64, 64, 150),
            name='joystick_bg'
        )
        print("VirtualJoystick __init__: Created bg Entity")
        self.knob = Draggable(
            parent=self,
            model='circle',
            color=color.white,
            name='joystick_knob'
        )
        print("VirtualJoystick __init__: Created knob Draggable")
        self.knob.always_on_top   = True
        print("VirtualJoystick __init__: Set knob always_on_top")
        self.knob.start_position  = Vec2(0, 0)
        print("VirtualJoystick __init__: Set knob start_position")
        self.knob.lock = Vec3(0, 0, 1)
        print("VirtualJoystick __init__: Set knob lock")
        # 6) Current input value (Vec2)
        self.value = Vec2(0, 0)
        print("VirtualJoystick __init__: Set initial value")
        # 7) Initialize with no width-ratio scaling (ratio=1.0)
        self._apply_scale(1.0)
        print("VirtualJoystick __init__: Called _apply_scale")

    def _apply_scale(self, ratio: float) -> None:
        """
        Apply dynamic scaling to:
          - self.scale    (joystick base diameter)
          - bg.scale      (fills its parent)
          - knob.scale    (knob diameter * knob_factor)
          - max_offset    (limit for dragging)
        """
        print("VirtualJoystick _apply_scale: Called with ratio =", ratio)
        ui_d = self._base_ui_diam * ratio
        print("VirtualJoystick _apply_scale: Computed ui_d =", ui_d)
        ui_r = self._base_ui_radius * ratio
        print("VirtualJoystick _apply_scale: Computed ui_r =", ui_r)

        self.scale      = Vec2(ui_d, ui_d)
        print("VirtualJoystick _apply_scale: Set self.scale =", self.scale)
        self.bg.scale   = Vec2(1, 1)  # base circle fills parent Entity
        print("VirtualJoystick _apply_scale: Set bg.scale =", self.bg.scale)
        self.knob.scale = Vec2(ui_r * self.knob_factor,
                               ui_r * self.knob_factor)
        print("VirtualJoystick _apply_scale: Set knob.scale =", self.knob.scale)

        # update max_offset and logical radius here, once ui_r is known
        self.max_offset = (ui_r * self.knob_factor) / 2
        print("VirtualJoystick _apply_scale: Set max_offset =", self.max_offset)
        self.radius     = self.max_offset
        print("VirtualJoystick _apply_scale: Set radius =", self.radius)
        print("VirtualJoystick _apply_scale: Completed scaling application")
        print("VirtualJoystick _apply_scale: Set max_offset =", self.max_offset)
        self.radius     = self.max_offset
        print("VirtualJoystick _apply_scale: Set radius =", self.radius)
        print("VirtualJoystick _apply_scale: Completed scaling application")
        print("VirtualJoystick _apply_scale: Computed ui_r =", ui_r)

        self.scale      = Vec2(ui_d, ui_d)
        print("VirtualJoystick _apply_scale: Set self.scale =", self.scale)
        self.bg.scale   = Vec2(1, 1)  # base circle fills parent Entity
        print("VirtualJoystick _apply_scale: Set bg.scale =", self.bg.scale)
        self.knob.scale = Vec2(ui_r * self.knob_factor,
                               ui_r * self.knob_factor)
        print("VirtualJoystick _apply_scale: Set knob.scale =", self.knob.scale)

        # update max_offset and logical radius here, once ui_r is known
        self.max_offset = (ui_r * self.knob_factor) / 2
        print("VirtualJoystick _apply_scale: Set max_offset =", self.max_offset)
        self.radius     = self.max_offset
        print("VirtualJoystick _apply_scale: Set radius =", self.radius)

    def update(self) -> None:
        print("VirtualJoystick update: Called")
        # Recompute width-ratio if window width changed
        cur_w, _ = window.size
        print("VirtualJoystick update: Current window size =", cur_w, _)
        ratio    = cur_w / (self._init_w or cur_w)
        print("VirtualJoystick update: Computed ratio =", ratio)
        self._apply_scale(ratio)

        # Begin dragging if mouse is held over the knob
        print("VirtualJoystick update: Checking for dragging start")
        if held_keys['left mouse'] and mouse.hovered_entity == self.knob:
            print("VirtualJoystick update: Starting drag")
            self.knob.dragging = True

        # While dragging, clamp knob to circle and compute value
        if self.knob.dragging:
            print("VirtualJoystick update: Dragging active")
            offset = Vec2(self.knob.x, self.knob.y)
            print("VirtualJoystick update: Offset =", offset)
            if offset.length() > self.radius:
                print("VirtualJoystick update: Clamping offset")
                offset = offset.normalized() * self.radius
            self.knob.position = Vec3(offset.x, offset.y, 0)  # ensure z=0
            print("VirtualJoystick update: Set knob position =", self.knob.position)
            self.value = offset / self.radius
            print("VirtualJoystick update: Set value =", self.value)
        else:
            print("VirtualJoystick update: Not dragging, resetting")
            self.knob.position = Vec3(0, 0, 0)
            self.value = Vec2(0, 0)
            print("VirtualJoystick update: Reset knob position and value")

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
        print(f"VirtualButton __init__: Starting initialization with key_name={key_name}, size_px={size_px}, position={position}, color={color}, kwargs={kwargs}")
        super().__init__(
            parent=camera.ui,
            model='circle',
            collider='box',
            position=position,
            color=color,
            **kwargs
        )
        print("VirtualButton __init__: Super __init__ called")
        self.key_name = key_name
        print(f"VirtualButton __init__: Set key_name to {self.key_name}")
        self.size_px  = size_px
        print(f"VirtualButton __init__: Set size_px to {self.size_px}")

        # 1) Store initial window dimensions
        self._init_w, self._init_h = window.size
        print(f"VirtualButton __init__: Stored initial window size: width={self._init_w}, height={self._init_h}")

        # 2) Compute base UI scale from height
        h = self._init_h or 1
        self._base_ui_size = (self.size_px / h) * 2
        print(f"VirtualButton __init__: Computed base UI size: {self._base_ui_size}")

        # 3) Apply initial scale with no width-ratio change
        self.scale = self._base_ui_size
        print(f"VirtualButton __init__: Applied initial scale: {self.scale}")

    def update(self) -> None:
        print("VirtualButton update: Called")
        # Recompute width ratio and apply to scale
        cur_w, _ = window.size
        print("VirtualButton update: Current window size =", cur_w, _)
        ratio    = cur_w / (self._init_w or cur_w)
        print("VirtualButton update: Computed ratio =", ratio)
        self.scale = self._base_ui_size * ratio
        print("VirtualButton update: Set scale =", self.scale)

    def on_click(self) -> None:
        """Called when the user clicks the button."""
        print("VirtualButton on_click: Called")
        held_keys[self.key_name] = 1
        print(f"VirtualButton on_click: Set held_keys[{self.key_name}] = 1")
        input(self.key_name)
        print(f"VirtualButton on_click: Called input({self.key_name})")
        print(f"VirtualButton '{self.key_name}' pressed.")

    def input(self, key: str) -> None:
        """Called on input events—used here to reset held_keys."""
        print(f"VirtualButton input: Called with key={key}")
        if key == f'{self.key_name} up':
            print(f"VirtualButton '{self.key_name}' released.")
            held_keys[self.key_name] = 0
            print(f"VirtualButton input: Set held_keys[{self.key_name}] = 0")

class HealthMixin:
    def __init__(self, health=100, **kwargs):
        print(f"HealthMixin __init__: Called with health={health}, kwargs={kwargs}")
        super().__init__(**kwargs)
        self.health = health
        print(f"HealthMixin __init__: Set health to {self.health}")

    def take_damage(self, amount):
        print(f"HealthMixin take_damage: Called with amount={amount}")
        self.health -= amount
        print(f'{self} took {amount} damage. Remaining health: {self.health}')
        if self.health <= 0:
            print("HealthMixin take_damage: Health <= 0, calling die()")
            self.die()

    def die(self):
        print(f"HealthMixin die: Called")
        print(f'{self} died.')
        destroy(self)

class DynamicCrosshair(Entity):
    def __init__(self, player=None, line_length=0.03, line_thickness=0.002,
                 reticle_speed=5, reticle_distance=0.02, dot_scale=0.01, **kwargs):
        print("DynamicCrosshair __init__: Called")
        print(f"Initializing DynamicCrosshair with player={player}, line_length={line_length}, line_thickness={line_thickness}, reticle_speed={reticle_speed}, reticle_distance={reticle_distance}, dot_scale={dot_scale}, kwargs={kwargs}")
        super().__init__(parent=camera.ui, position=(0,0))
        print("DynamicCrosshair __init__: Super init called")

        self.player = player  # reference to player entity
        print(f"DynamicCrosshair __init__: Set player to {self.player}")
        self.reticle_speed = reticle_speed
        print(f"DynamicCrosshair __init__: Set reticle_speed to {self.reticle_speed}")
        self.reticle_distance = reticle_distance
        print(f"DynamicCrosshair __init__: Set reticle_distance to {self.reticle_distance}")

        # Shooting offset
        self.shoot_offset = 0
        print("DynamicCrosshair __init__: Set shoot_offset to 0")

        # Center dot
        self.dot = Entity(parent=self, model='circle', color=color.white, scale=dot_scale, position=(0,0), name='crosshair_dot')
        print("DynamicCrosshair __init__: Created center dot")

        # Create crosshair lines
        self.lines = {}
        print("DynamicCrosshair __init__: Creating crosshair lines")
        self.lines['top'] = Entity(parent=self, model='quad', color=color.white,
                                   scale=(line_thickness, line_length), position=(0, line_length/2 + 0.01), name='crosshair_top')
        self.lines['bottom'] = Entity(parent=self, model='quad', color=color.white,
                                      scale=(line_thickness, line_length), position=(0, -line_length/2 - 0.01), name='crosshair_bottom')
        self.lines['left'] = Entity(parent=self, model='quad', color=color.white,
                                    scale=(line_length, line_thickness), position=(-line_length/2 - 0.01, 0), name='crosshair_left')
        self.lines['right'] = Entity(parent=self, model='quad', color=color.white,
                                     scale=(line_length, line_thickness), position=(line_length/2 + 0.01, 0), name='crosshair_right')
        print("DynamicCrosshair __init__: Crosshair lines created")

        # Store original positions for interpolation
        self.original_positions = {k: v.position for k,v in self.lines.items()}
        print(f"DynamicCrosshair __init__: Stored original positions: {self.original_positions}")

    def update(self):
        print("DynamicCrosshair update: Called")
        # Player speed
        speed = getattr(self.player, 'velocity', Vec3(0,0,0)).length() if self.player else 1
        print(f"DynamicCrosshair update: Player speed = {speed}")

        # Total offset = movement + shooting
        total_offset = speed * self.reticle_distance + self.shoot_offset
        print(f"DynamicCrosshair update: Total offset = {total_offset}")

        for direction, line in self.lines.items():
            print(f"DynamicCrosshair update: Updating line {direction}")
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
            print(f"DynamicCrosshair update: Set {direction} position to {line.position}")

        # Gradually decay shooting offset
        self.shoot_offset = lerp(self.shoot_offset, 0, time.dt * 10)
        print(f"DynamicCrosshair update: Decayed shoot_offset to {self.shoot_offset}")

class FirstPersonController(Entity, HealthMixin):
    """
    A basic first-person character:
      - Mouse/touch look using virtual joysticks.
      - WASD or joystick movement with collision.
      - Jump, gravity, and optional gun shooting.
    """
    def __init__(self, **kwargs):
        print("FirstPersonController __init__: Called")
        super().__init__()
        print("FirstPersonController __init__: Super init called")

        HealthMixin.__init__(self, health=100)
        print("FirstPersonController __init__: HealthMixin init called")

        # Movement parameters
        self.speed            = 5
        self.height           = 2
        self.camera_pivot     = Entity(parent=self, y=self.height, name='camera_pivot')
        camera.parent        = self.camera_pivot
        camera.position      = (0, 0, 0)
        camera.rotation      = (0, 0, 0)
        camera.fov           = 90

        # Control settings
        self.use_touch       = True
        mouse.locked         = False
        mouse.visible        = True
        self.mouse_sensitivity = Vec2(40, 40)

        # Jump & gravity
        self.gravity          = 1
        self.grounded         = False
        self.jump_height      = 2
        self.jump_up_duration = .5
        self.fall_after       = .35
        self.air_time         = 0
        self.max_step_height  = 0.5

        # Collision setup
        self.traverse_target = scene
        self.ignore_list     = [self]
        self.gun             = None

        self._next_fire_time = 0

        # # Head bob settings
        self.headbob_amplitude = 0.05   # How much the camera moves up/down
        self.headbob_frequency = 2.0    # How fast the bob cycles
        self.headbob_timer = 0.0        # Internal timer for sine wave
        self.camera_original_pos = camera.position

        self.recoil_pitch = 0.0          # Current vertical recoil offset
        self.recoil_yaw = 0.0            # Optional horizontal sway
        self.recoil_recover_speed = 5.0  # How fast camera recovers from recoil
        self.recoil_amount = Vec2(0.5, 0.1)  # (pitch, yaw) per shot

        # Create dynamic crosshair, passing self as the player reference
        self.crosshair = DynamicCrosshair(player=self)

        self.damage_overlay = Entity(
            parent=camera.ui,
            model='quad',
            color=color.rgba(255, 0, 0, 0),  # fully transparent initially
            scale=(2, 2),
            z=-1
        )

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

        print(f"Player initialized at position {self.position} with health {self.health}, use_touch={self.use_touch}, speed={self.speed}, height={self.height}, gravity={self.gravity}, gun={self.gun}, ignore_list={self.ignore_list}, mouse_sensitivity={self.mouse_sensitivity}, jump_height={self.jump_height}, jump_up_duration={self.jump_up_duration}, fall_after={self.fall_after}, max_step_height={self.max_step_height}, headbob_amplitude={self.headbob_amplitude}, headbob_frequency={self.headbob_frequency}, recoil_amount={self.recoil_amount}, recoil_recover_speed={self.recoil_recover_speed}, crosshair={self.crosshair}, damage_overlay={self.damage_overlay}, kwargs={kwargs})")

    def update(self) -> None:
        print("FirstPersonController update: Called")
        # Look via right joystick
        if self.use_touch:
            rot = joystick_look.value
            yaw_gain   = 100
            pitch_gain = 100
            print(f"FirstPersonController update: Using touch look with rot={rot}, yaw_gain={yaw_gain}, pitch_gain={pitch_gain}")
            self.rotation_y += rot.x * time.dt * yaw_gain
            print(f"FirstPersonController update: Updated rotation_y to {self.rotation_y}")
            self.camera_pivot.rotation_x = clamp(
                self.camera_pivot.rotation_x - rot.y * time.dt * pitch_gain,
                -90,
                90
            )
            print(f"FirstPersonController update: Updated camera_pivot.rotation_x to {self.camera_pivot.rotation_x}")
        else:
            # Mouse look (only when locked)
            if mouse.locked:
                print(f"FirstPersonController update: Using mouse look with velocity={mouse.velocity}, sensitivity={self.mouse_sensitivity}")
                self.rotation_y += mouse.velocity[0] * self.mouse_sensitivity[1]
                print(f"FirstPersonController update: Updated rotation_y to {self.rotation_y}")
                self.camera_pivot.rotation_x -= mouse.velocity[1] * self.mouse_sensitivity[0]
                print(f"FirstPersonController update: Updated camera_pivot.rotation_x to {self.camera_pivot.rotation_x}")
                self.camera_pivot.rotation_x = clamp(self.camera_pivot.rotation_x, -90, 90)
                print(f"FirstPersonController update: Clamped camera_pivot.rotation_x to {self.camera_pivot.rotation_x}")
        print("FirstPersonController update: Look handled")

        # Move via left joystick
        if self.use_touch:
            move_x = joystick_move.value.x
            move_y = joystick_move.value.y
            print(f"FirstPersonController update: Using touch move with move_x={move_x}, move_y={move_y}")
        else:
            move_x = held_keys['d'] - held_keys['a']
            move_y = held_keys['w'] - held_keys['s']
            print(f"FirstPersonController update: Using keyboard move with move_x={move_x}, move_y={move_y}")
        direction = Vec3(self.forward * move_y + self.right * move_x).normalized()
        self.velocity = direction * self.speed  # Store velocity vector
        print(f"FirstPersonController update: Calculated direction={direction}, velocity={self.velocity}")

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
            print(f"FirstPersonController update: Raycast feet hit={feet.hit}, head hit={head.hit}")

            if feet.hit and not head.hit:
                step_height = min(self.max_step_height, feet.world_point.y - self.y)
                self.y += step_height
                print(f"FirstPersonController update: Stepped up by {step_height}")

            if not (feet.hit or head.hit):
                self.position += direction * self.speed * time.dt
                print(f"FirstPersonController update: Moved to position {self.position}")
        print("FirstPersonController update: Move handled")

        # Gravity & landing
        if self.gravity:
            down_ray = raycast(
                self.world_position + (0, self.height, 0),
                self.down,
                traverse_target=self.traverse_target,
                ignore=self.ignore_list
            )
            print(f"FirstPersonController update: Gravity down_ray distance={down_ray.distance}, normal={down_ray.world_normal}")
            if down_ray.distance <= self.height + .1 and down_ray.world_normal.y > .7:
                if not self.grounded:
                    self.land()
                    print("FirstPersonController update: Landed")
                self.grounded = True
                self.y = down_ray.world_point.y
                print(f"FirstPersonController update: Set y to ground level {self.y}")
            else:
                self.grounded = False
                self.y -= min(
                    self.air_time,
                    down_ray.distance - .05
                ) * time.dt * 100
                self.air_time += time.dt * .25 * self.gravity
                print(f"FirstPersonController update: Falling, new y={self.y}, air_time={self.air_time}")
        print("FirstPersonController update: Gravity handled")

        displacement = self.velocity.length()  # speed player is trying to move
        print(f"FirstPersonController update: Displacement={displacement}")

        if self.grounded and displacement > 0.01:  # only bob if actually moved
            print("FirstPersonController update: Applying head bob")
            # Increment timer based on speed
            self.headbob_timer += time.dt * self.headbob_frequency * (displacement / self.speed)
            print(f"FirstPersonController update: headbob_timer={self.headbob_timer}")
            # Sine wave for vertical bob
            bob_offset = math.sin(self.headbob_timer * math.pi * 2) * self.headbob_amplitude
            print(f"FirstPersonController update: bob_offset={bob_offset}")
            # horizontal sway for a more natural effect
            sway_offset = math.sin(self.headbob_timer * math.pi * 4) * (self.headbob_amplitude / 2)
            print(f"FirstPersonController update: sway_offset={sway_offset}")
            # Apply to camera
            camera.position = self.camera_original_pos + Vec3(sway_offset, bob_offset, 0)
            print(f"FirstPersonController update: Camera position set to {camera.position}")
        else:
            # Smoothly return camera to original position
            camera.position = lerp(camera.position, self.camera_original_pos, time.dt * 8)
            print("FirstPersonController update: Head bob reset to original position")
        self._prev_position = self.position
        print("FirstPersonController update: Head bob handled")

        print("FirstPersonController update: Recoil handled")

        # Apply recoil recovery
        if self.recoil_pitch != 0 or self.recoil_yaw != 0:
            print(f"FirstPersonController update: Applying recoil recovery with pitch={self.recoil_pitch}, yaw={self.recoil_yaw}")
            # Gradually return to zero
            self.recoil_pitch = lerp(self.recoil_pitch, 0, time.dt * self.recoil_recover_speed)
            self.recoil_yaw   = lerp(self.recoil_yaw, 0, time.dt * self.recoil_recover_speed)
            print(f"FirstPersonController update: Recoil recovery applied with pitch={self.recoil_pitch}, yaw={self.recoil_yaw}")

            # Apply recoil offsets to camera pivot
            self.camera_pivot.rotation_x -= self.recoil_pitch
            self.rotation_y       += self.recoil_yaw
            print(f"FirstPersonController update: Camera rotation updated with pitch={self.camera_pivot.rotation_x}, yaw={self.rotation_y}")
        
        # Smoothly adjust crosshair spread based on recoil
        self.crosshair.shoot_offset = self.recoil_pitch * 0.05
        print(f"FirstPersonController update: Crosshair shoot_offset set to {self.crosshair.shoot_offset}")

        print("FirstPersonController update: Crosshair updated")

        if self.damage_overlay.color.a > 0:
            new_alpha = max(0, self.damage_overlay.color.a - time.dt)
            self.damage_overlay.color = color.rgba(255, 0, 0, new_alpha)
            print(f"FirstPersonController update: Damage overlay alpha updated to {new_alpha}")

        print("FirstPersonController update: Damage overlay updated")

    def input(self, key: str) -> None:
        # Toggle touch controls
        if key == 't':
            self.use_touch  = not self.use_touch
            print(f"FirstPersonController input: Toggled use_touch to {self.use_touch}")
            
            if self.use_touch:
                # Touch mode
                mouse.locked  = False
                mouse.visible = True
                print("Touch controls enabled.")
            else:
                # Keyboard/mouse mode
                mouse.locked  = True
                mouse.visible = False
                print("Keyboard/mouse controls enabled.")

            # Show/hide touch controls
            if joystick_move:
                joystick_move.enabled = self.use_touch
                joystick_move.visible = self.use_touch
            if joystick_look:
                joystick_look.enabled = self.use_touch
                joystick_look.visible = self.use_touch
            if button_jump:
                button_jump.enabled = self.use_touch
                button_jump.visible = self.use_touch
            if button_shoot:
                button_shoot.enabled = self.use_touch
                button_shoot.visible = self.use_touch

        # Jump
        if key in ('space', 'gamepad a'):
            self.jump()
            print("Jump action triggered.")

        # Shoot (if gun equipped and not clicking UI)
        if key == 'left mouse down' and self.gun and not self.use_touch:
            self.shoot()
            print("Shoot action triggered via mouse.")

        if key == 'gamepad x':
            self.shoot()
            print("Shoot action triggered via gamepad.")

    def jump(self) -> None:
        """Animate a jump if grounded."""
        print("FirstPersonController jump: Called")
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
        print("FirstPersonController start_fall: Called")
        self.air_time += time.dt

    def land(self) -> None:
        """Reset air_time on landing."""
        print("FirstPersonController land: Called")
        self.air_time = 0
        self.grounded = True

    def shoot(self) -> None:
        """Fire a bullet from the equipped gun."""
        print("FirstPersonController shoot: Called")
        if not self.gun:
            return
        # Firing rate limit (cooldown)
        if hasattr(self, '_next_fire_time') and time.time() < self._next_fire_time:
            return
        self._next_fire_time = time.time() + 0.25  # 0.25s cooldown
        gunshot.play()
        self.gun.blink(color.gray)
        self.recoil_pitch += self.recoil_amount.x
        print(f"FirstPersonController shoot: Applied recoil_pitch, new value={self.recoil_pitch}")
        self.recoil_yaw   += random.uniform(-self.recoil_amount.y, self.recoil_amount.y)
        print(f"FirstPersonController shoot: Applied recoil_yaw, new value={self.recoil_yaw}")
        # Raycast for hit detection
        hit = raycast(
            camera.world_position,
            camera.forward,
            distance=100,
            traverse_target=scene,
            ignore=[self, self.gun]
        )
        print(f"FirstPersonController shoot: Raycast hit={hit.hit}, entity={hit.entity}, point={hit.world_point}")
        bullet = Entity(
            parent=self.gun,
            model=preload['bullet'],
            scale=0.2,
            position=(0.2, 0.1, 0),
            color=color.gold,
            name='player_bullet'
        )
        print(f"FirstPersonController shoot: Bullet created at position {bullet.position}")
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
            print(f"Hit: {target}")
            if hasattr(target, 'take_damage'):
                target.take_damage(50)

    def take_damage(self, amount):
        super().take_damage(amount)
        if hasattr(self, 'health_bar'):
            self.health_bar.value = self.health

        # Flash the red overlay
        self.damage_overlay.color = color.rgba(255, 0, 0, 0.3)

    def die(self):
        print("Player died!")
        self.health_bar.value = 0
        global player_alive
        player_alive = False
        destroy(self)  # Remove player entity
        Text("Game Over", origin=(0,0), scale=3, color=color.red, parent=camera.ui)
        invoke(game_over, delay=1)  # Delay to allow last frame effects (e.g. sounds)

class DummyTarget(Entity, HealthMixin):
    def __init__(self, **kwargs):
        print("DummyTarget __init__: Called")
        super().__init__(
            model='cube',
            color=color.orange,
            collider='box',
            scale=(1, 2, 1),
            name='dummy_target',
            **kwargs
        )
        print("DummyTarget __init__: Super init called")
        HealthMixin.__init__(self, health=100)
        print("DummyTarget __init__: HealthMixin init called")
        self.spawn_point = self.position
        print(f"DummyTarget __init__: Set spawn_point to {self.spawn_point}")
        self.visible = True
        print("DummyTarget __init__: Set visible to True")
        self.enabled = True
        print("DummyTarget __init__: Set enabled to True")
        self.health_bar = HealthBar(
            max_value=100,
            value=100,
            scale=(.3, .02),
            bar_color=color.red.tint(-.2),
            roundness=.5,
            show_text=False,
            parent=self
        )
        print(f"Health bar created for {self} with initial value {self.health_bar.value}")
        self.health_bar.x = 0.1
        print("DummyTarget __init__: Set health_bar.x to 0.1")
        self.health_bar.y = 1
        print("DummyTarget __init__: Set health_bar.y to 1")
        self.health_bar.billboard=True
        print("DummyTarget __init__: Set health_bar.billboard to True")
        self.original_color = self.color
        print(f"DummyTarget __init__: Set original_color to {self.original_color}")
        self.flash_intensity = 0
        print("DummyTarget __init__: Set flash_intensity to 0")

    def take_damage(self, amount):
        print(f"DummyTarget take_damage: Called with amount={amount}")
        if not self.enabled:
            print("DummyTarget take_damage: Not enabled, returning")
            return
        print("DummyTarget take_damage: Calling super().take_damage")
        super().take_damage(amount)
        try:
            if hasattr(self, 'health_bar') and self.health_bar and self.health_bar.enabled:
                self.health_bar.value = self.health
                print(f"Updated health bar to {self.health}")
        except AssertionError as e:
            # health_bar node no longer valid—ignore
            print(f"Health bar error: {e}")
            pass
        # Flash effect
        self.flash_intensity = 1  # trigger full flash
        print("DummyTarget take_damage: Set flash_intensity to 1")

    def update(self):
        print("DummyTarget update: Called")
        if self.flash_intensity > 0:
            print(f"DummyTarget update: Flash intensity > 0, current={self.flash_intensity}")
            # Gradually reduce flash intensity
            self.flash_intensity = max(0, self.flash_intensity - time.dt * 2)  # fade speed
            print(f"DummyTarget update: New flash_intensity={self.flash_intensity}")
            # Blend between red and original color
            self.color = color.rgb32(
                lerp(255, self.original_color[0]*255, 1 - self.flash_intensity),
                lerp(0,   self.original_color[1]*255, 1 - self.flash_intensity),
                lerp(0,   self.original_color[2]*255, 1 - self.flash_intensity)
            )
            print(f"DummyTarget update: New color={self.color}")
    
    def die(self):
        print(f"DummyTarget die: Called, {self} died.")
        print("DummyTarget die: Destroying self")
        destroy(self)
        for b in scene.entities:
            if isinstance(b, Entity) and getattr(b, 'collider', None) == 'box' and b.model.name == 'cube':
                print(f"DummyTarget die: Destroying entity {b}")
                destroy(b)

class AIBot(DummyTarget):
    def __init__(self, patrol_area=(10, 10), chase_range=5, speed = 1, **kwargs):
        print(f"AIBot __init__: Called with patrol_area={patrol_area}, chase_range={chase_range}, speed={speed}, kwargs={kwargs}")
        super().__init__(**kwargs)
        print("AIBot __init__: Super init called")
        self.patrol_area = patrol_area
        print(f"AIBot __init__: Set patrol_area to {self.patrol_area}")
        self.chase_range = chase_range
        print(f"AIBot __init__: Set chase_range to {self.chase_range}")
        self.speed = speed
        print(f"AIBot __init__: Set speed to {self.speed}")
        self.fire_interval = 3     # seconds between shots
        print(f"AIBot __init__: Set fire_interval to {self.fire_interval}")
        self._next_fire_time = 0
        print("AIBot __init__: Set _next_fire_time to 0")
        self.alive = True
        print("AIBot __init__: Set alive to True")
        self.is_chasing = False
        print("AIBot __init__: Set is_chasing to False")
        self.gun = Entity(
            parent=self,
            model='assets/pistol.gltf',
            color= color.gray.tint(-.2),
            position=Vec3(.2, .1, .8),  # adjust for hand offset
            rotation=Vec3(0, 0, 0),
            scale=0.1,
            name='ai_gun'
        )
        print(f"AI gun created for {self} at position {self.gun.position}, rotation {self.gun.rotation}, scale {self.gun.scale}")
        self.target_pos = self.get_valid_ground_position()
        print(f"AIBot __init__: Set target_pos to {self.target_pos}")
        self.update_task = invoke(self.patrol, delay=1)
        print(f"AIBot __init__: Set update_task to {self.update_task}")
        ai_bots.append(self)
        print("AIBot __init__: Appended to ai_bots")
        bot_tasks.append(self.update_task)
        print("AIBot __init__: Appended update_task to bot_tasks")

    def patrol(self):
        print("AIBot patrol: Called")
        if not getattr(self, 'enabled', False) or not getattr(self, 'alive', False):
            print("AIBot patrol: Not enabled or not alive, returning")
            return
        if not self.alive:
            print("AIBot patrol: Not alive, returning")
            return
        if not player_alive or not player or not player.enabled:
            print("AIBot patrol: Player not alive or not enabled, returning")
            return
        # 1. Determine target: chase player or patrol
        dist_to_player = distance(self.position, player.position)
        print(f"AIBot patrol: Distance to player = {dist_to_player}")
        if dist_to_player < self.chase_range:
            self.target_pos = player.position
            self.is_chasing = True
            print("AIBot patrol: Chasing player")
        else:
            self.is_chasing = False
            print("AIBot patrol: Patrolling")
            if distance(self.position, self.target_pos) < 0.5:
                self.target_pos = self.get_valid_ground_position()
                print(f"New patrol target: {self.target_pos}")
        move_dir = (self.target_pos - self.position).normalized()
        print(f"AIBot patrol: Move direction = {move_dir}")
        # 2. Wall detection
        front_ray = raycast(
            self.position + Vec3(0, 0.5, 0),
            move_dir,
            distance=0.6,
            ignore=[self],
            traverse_target=scene
        )
        print(f"AIBot patrol: Front ray hit = {front_ray.hit}")
        if front_ray.hit and not self.is_chasing:
            print("AIBot patrol: Wall ahead, choosing new target")
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
                print("AIBot patrol: Blocked by other bot")
                break
        if distance(self.position, player.position) < 1.5:
            blocked = True
            print("AIBot patrol: Blocked by player")
        print(f"AIBot patrol: Blocked = {blocked}")
        # 4. Move if clear
        if not blocked and not front_ray.hit:
            self.position += move_dir * self.speed * time.dt
            print(f"AIBot patrol: Moved to position {self.position}")
        # 5. Keep grounded
        down_ray = raycast(
            self.position + Vec3(0, 0.5, 0),
            direction=Vec3(0, -1, 0),
            ignore=[self],
            traverse_target=scene
        )
        print(f"AIBot patrol: Down ray hit = {down_ray.hit}")
        if down_ray.hit:
            self.y = down_ray.world_point.y + 1
            print(f"AIBot patrol: Set y to {self.y}")
        if self.is_chasing:
            print("AIBot patrol: Chasing, looking at player")
            # Rotate the bot to look at the player
            self.look_at(player.position)
            self.rotation_x = 0  # keep upright
            self.rotation_z = 0
            self.shoot()
        self.update_task = invoke(self.patrol, delay=0.1)
        print("AIBot patrol: Scheduled next patrol")

    def get_valid_ground_position(self, max_attempts=10):
        print(f"AIBot get_valid_ground_position: Called with max_attempts={max_attempts}")
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
        return Vec3(0, 2, 0)
    
    def shoot(self):
        if not self.alive or not player or not self.enabled or time.time() < self._next_fire_time:
            return
        
        self._next_fire_time = time.time() + self.fire_interval
        gunshot.play()

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
            if (not player or not hasattr(player, 'position') or player in scene.entities and player.enabled == False):
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
        # remove from our global lists
        if self in ai_bots:      ai_bots.remove(self)
        if self.update_task in bot_tasks:  bot_tasks.remove(self.update_task)
        # destroy this instance
        destroy(self)
        if game_started and player_alive and len(ai_bots) == 0:
            Text("You Win!", origin=(0,0), scale=3, color=color.green, parent=camera.ui)
            invoke(quit_to_main_menu, delay=3)

def show_main_menu():
    global main_menu, menu_background

    print("Showing main menu...")

    # Make mouse cursor visible
    mouse.visible = True
    mouse.locked = False

    for s in list(Sky.instances):
        destroy(s)
    Sky.instances.clear()

    # Create full-screen background image
    menu_background = Entity(
        name="menu_background",
        parent=camera.ui,
        model='quad',
        texture='assets/label.jpg',
        scale=(2, 1),  # Full screen
        z=1  # Send it to back (higher z = farther back in UI)
    )
    
    main_menu = Entity(name="main_menu", parent=camera.ui)

    Text(name="main_menu_title", text="Main Menu", scale=2, x=-0.125, y=0.4, parent=main_menu)

    Button(
        name="btn_singleplayer",
        text='Singleplayer',
        scale=(.3, .1),
        y=0.15,
        parent=main_menu,
        on_click=start_singleplayer
    )

    Button(
        name="btn_multiplayer",
        text='Multiplayer',
        scale=(.3, .1),
        y=-0.05,
        parent=main_menu,
        on_click=lambda: print("Multiplayer not implemented.")
    )

    Button(
        name="btn_exit",
        text='Exit',
        scale=(.3, .1),
        y=-0.25,
        parent=main_menu,
        on_click=application.quit
    )

def show_pause_menu():
    global pause_menu

    print("Showing pause menu...")

    pause_menu = Entity(name="pause_menu", parent=camera.ui)

    Text(name="pause_menu_title", text="Paused", scale=2, x=-0.1, y=0.3, parent=pause_menu)

    Button(
        name="btn_resume",
        text='Resume',
        scale=(.3, .1),
        y=0.2,
        parent=pause_menu,
        on_click=resume_game
    )

    Button(
        name="btn_setting",
        text='Setting',
        scale=(.3, .1),
        y=0,
        parent=pause_menu,
        on_click=setting_menu
    )

    Button(
        name="btn_quit_to_menu",
        text='Quit to Menu',
        scale=(.3, .1),
        y=-0.2,
        parent=pause_menu,
        on_click=quit_to_main_menu
    )

    # Hide virtual joysticks, buttons, health bar and crosshair when pause menu is shown
    if joystick_move:
        joystick_move.enabled = False
    if joystick_look:
        joystick_look.enabled = False
    if button_jump:
        button_jump.enabled = False
    if button_shoot:
        button_shoot.enabled = False
    if player and hasattr(player, 'health_bar') and player.health_bar:
        player.health_bar.enabled = False
    if player and hasattr(player, 'crosshair') and player.crosshair:
        player.crosshair.enabled = False

def start_singleplayer():
    global game_started, menu_background, main_menu, player_alive

    print("starting singleplayr...")

    application.resume()

    # Reset the “am I alive?” flag
    player_alive = True

    # Clean up old bots & tasks
    for t in bot_tasks:
        print(f"Finishing bot task before starting singleplayer: {t}")
        t.finish()
    bot_tasks.clear()
    for b in ai_bots:
        print(f"Destroying AI bot before starting singleplayer: {b}")
        destroy(b)
    ai_bots.clear()
    for seq in sequences:
        print(f"Finishing sequence before starting singleplayer: {seq}")
        if isinstance(seq, Sequence):
            print(f"Finishing sequence instance before starting singleplayer: {seq}")
            seq.finish()
    sequences.clear()

    # Tear down menus
    destroy(main_menu)
    destroy(menu_background)

    game_started = True
    setup_game()  # existing function that sets up map, player, bots, etc.

def pause_game():

    print("pausing game...")

    # application.pause()
    pause_button.enabled = False
    show_pause_menu()

def resume_game():

    print("resuming game...")

    # application.resume()
    destroy(pause_menu)
    pause_button.enabled = True
    
    # Re-enable virtual joysticks, buttons, health bar and crosshair when resuming
    if joystick_move:
        joystick_move.enabled = True
    if joystick_look:
        joystick_look.enabled = True
    if button_jump:
        button_jump.enabled = True
    if button_shoot:
        button_shoot.enabled = True
    if player and hasattr(player, 'health_bar') and player.health_bar:
        player.health_bar.enabled = True
    if player and hasattr(player, 'crosshair') and player.crosshair:
        player.crosshair.enabled = True

def close_settings():
    global pause_menu, settings_menu, speed_slider, jump_slider, sensx_slider, sensy_slider, volume_slider, joystick_move_posx_slider, joystick_move_posy_slider, joystick_move_scale_slider, joystick_look_posx_slider, joystick_look_posy_slider, joystick_look_scale_slider
    print("Closing settings menu...")
    destroy(settings_menu)
    settings_menu = None
    speed_slider = None
    jump_slider = None
    sensx_slider = None
    sensy_slider = None
    volume_slider = None
    joystick_move_posx_slider = None
    joystick_move_posy_slider = None
    joystick_move_scale_slider = None
    joystick_look_posx_slider = None
    joystick_look_posy_slider = None
    joystick_look_scale_slider = None
    if pause_menu:
        pause_menu.enabled = True

def setting_menu():
    global pause_menu, settings_menu, speed_slider, jump_slider, sensx_slider, sensy_slider, volume_slider, joystick_move_posx_slider, joystick_move_posy_slider, joystick_move_scale_slider, joystick_look_posx_slider, joystick_look_posy_slider, joystick_look_scale_slider

    print("Opening settings menu...")

    if pause_menu:
        pause_menu.enabled = False

    settings_menu = Entity(name="settings_menu", parent=camera.ui)

    Text(name="settings_title", text="Settings", scale=2, x=-0.1, y=0.45, parent=settings_menu)

    # Slider for player speed
    Text(text="Player Speed", scale=1, x=-0.3, y=0.35, parent=settings_menu)
    speed_slider = Slider(min=1, max=10, default=player.speed if player else 5, step=0.1, x=0.1, y=0.35, parent=settings_menu)

    # Slider for jump height
    Text(text="Jump Height", scale=1, x=-0.3, y=0.25, parent=settings_menu)
    jump_slider = Slider(min=0.5, max=5, default=player.jump_height if player else 2, step=0.1, x=0.1, y=0.25, parent=settings_menu)

    # Slider for mouse sensitivity x
    Text(text="Mouse Sens X", scale=1, x=-0.3, y=0.15, parent=settings_menu)
    sensx_slider = Slider(min=10, max=100, default=player.mouse_sensitivity.x if player else 40, step=1, x=0.1, y=0.15, parent=settings_menu)

    # Slider for mouse sensitivity y
    Text(text="Mouse Sens Y", scale=1, x=-0.3, y=0.05, parent=settings_menu)
    sensy_slider = Slider(min=10, max=100, default=player.mouse_sensitivity.y if player else 40, step=1, x=0.1, y=0.05, parent=settings_menu)

    # Close button
    Button(text='Close', scale=(0.2, 0.1), y=-0.15, parent=settings_menu, on_click=close_settings)

def quit_to_main_menu():

    print("quiting to main menu....")

    def cleanup():

        print("cleaning up the scene...")

        global player, bot_tasks, ai_bots, sequences, pause_menu, main_menu, menu_background

        application.pause()

        for seq in list(sequences):
            print(f"Finishing sequence before quiting to main menu: {seq}")
            if isinstance(seq, Sequence):
                print(f"Finishing sequence instance before quiting to main menu: {seq}")
                seq.finish()
        sequences.clear()

        for t in list(bot_tasks):
            print(f"Finishing bot task before quiting to main menu: {t}")
            t.finish()
        bot_tasks.clear()

        for b in list(ai_bots):
            print(f"Destroying AI bot before quiting to main menu: {b}")
            destroy(b)
        ai_bots.clear()

        if player:
            print(f"Destroying player before quiting to main menu: {player}")
            destroy(player)
            player = None

        lst = list(scene.entities)
        for e in lst:
            if e:
                print(f"Destroying scene entity before quiting to main menu: {e}")
                destroy(e)

        lst1 = list(camera.ui.children)
        for e in lst1:
            if e:
                print(f"Destroying UI element before quiting to main menu: {e}")
                destroy(e)

        lst2 = list(Sky.instances)
        for s in lst2:
            if s:
                print(f"Destroying sky instance before quiting to main menu: {s}")
                destroy(s)
        Sky.instances.clear()

        for ui_root in (main_menu, menu_background, pause_menu):
            if ui_root:
                print(f"Destroying UI root before quiting to main menu: {ui_root}")
                destroy(ui_root)

        main_menu = None
        menu_background = None
        pause_menu = None

        sequences.clear()
        bot_tasks.clear()
        ai_bots.clear()

        application.resume()
        show_main_menu()

    invoke(cleanup, delay=0)

def game_over():
    global pause_button, player

    print("Game Over - Returning to Main Menu")

    if pause_button and hasattr(pause_button, 'enabled') and pause_button.enabled:
        try:
            pause_button.enabled = False
        except Exception as e:
            print(f"Could not disable pause_button: {e}")

    for t in list(bot_tasks):
        print(f"Finishing bot task before game over: {t}")
        t.finish()
    bot_tasks.clear()

    for b in ai_bots:
        print(f"Destroying AI bot before game over: {b}")
        destroy(b)
    ai_bots.clear()

    for item in list(sequences):
        print(f"Finishing sequence before game over: {item}")
        if isinstance(item, Sequence):
            print(f"Finishing sequence instance before game over: {item}")
            item.finish()
    sequences.clear()

    for e in scene.entities:
        print(f"Destroying scene entity before game over: {e}")
        destroy(e)

    for e in camera.ui.children:
        if e != pause_button:
            print(f"Destroying UI element before game over: {e}")
            if hasattr(e, 'children'):
                for child in list(e.children):
                    print(f"Destroying child of UI element before game over: {child}")
                    destroy(child)
            destroy(e)

    show_main_menu()

def setup_game():
    global player, pause_button, joystick_move, joystick_look, button_jump, button_shoot

    print("setting up game...")

    # Instantiate touch controls
    joystick_move  = VirtualJoystick(name="joystick_move", position=(-.7, -.3))
    joystick_look  = VirtualJoystick(name="joystick_look", position=( .3, -.3))
    button_jump    = VirtualButton(name="button_jump", input='gamepad a', position=( .6, -.1), color=color.lime)
    button_shoot   = VirtualButton(name="button_shoot", input='gamepad x', position=( .8, -.2), color=color.red)

    print(f"controls created : joystick_move={joystick_move}, joystick_look={joystick_look}, button_jump={button_jump}, button_shoot={button_shoot}")

    pause_button = Button(name="pause_button", texture='cog', scale=(.08, .08), position=(-0.85, 0.45), origin=(-0.5, 0.5), parent=camera.ui, color=color.gray, on_click=pause_game)

    print(f"pause button created: {pause_button}")

    # Player and gun setup
    player = FirstPersonController(y=2, origin_y=-.5)

    print(f"Player created: {player}")
    
    # Touch controls
    joystick_move.visible = player.use_touch
    joystick_look.visible = player.use_touch
    button_jump.visible   = player.use_touch
    button_shoot.visible  = player.use_touch
    joystick_move.enabled = True
    joystick_look.enabled = True
    button_jump.enabled   = True
    button_shoot.enabled  = True

    print(f"joystick_move.visible={joystick_move.visible}, joystick_look.visible={joystick_look.visible}, button_jump.visible={button_jump.visible}, button_shoot.visible={button_shoot.visible}")
    print(f"joystick_move.enabled={joystick_move.enabled}, joystick_look.enabled={joystick_look.enabled}, button_jump.enabled={button_jump.enabled}, button_shoot.enabled={button_shoot.enabled}")

    pause_button.enabled = True

    print("pause_button.enabled=", pause_button.enabled)

    # Add environment
    ground = Entity(name="ground", model='cube', scale=(30, 1, 30), color=color.rgb(0.9294117647058824, 0.7882352941176471, 0.6862745098039216), texture='white_cube', texture_scale=(30, 30), collider='box')
    stepup1 = Entity(name="stepup1", model='cube', scale=(1, 1, 1), position=(1, 1, 0), color=color.gray, collider='box')
    stepup2 = Entity(name="stepup2", model='cube', scale=(1, 1, 1), position=(2, 2, 0), color=color.gray, collider='box')
    print("Stepups created")

    # ──────────────── Houses (Middle) ────────────────
    house1 = Entity(name="house1", model=preload['house1'], position=(-4, 0.5, -4), collider='box')
    house2 = Entity(name="house2", model=preload['house2'], position=(4, 0.5, -4), collider='box')
    house3 = Entity(name="house3", model=preload['house3'], position=(-4, 0.5, 4), collider='box')
    house4 = Entity(name="house4", model=preload['house4'], position=(4, 0.5, 4), collider='box')
    print("Houses created!")

    # ──────────────── Top Wall (North) ────────────────
    wall_n1 = Entity(name="wall_n1", model=preload['wall_n1'], position=(-10, 0.5, 15), collider='box')
    wall_n2 = Entity(name="wall_n2", model=preload['wall_n2'], position=(0, 0.5, 15), collider='box')
    wall_n3 = Entity(name="wall_n3", model=preload['wall_n3'], position=(10, 0.5, 15), collider='box')

    # ──────────────── Bottom Wall (South) ────────────────
    wall_s1 = Entity(name="wall_s1", model=preload['wall_s1'], position=(-10, 0.5, -15), collider='box')
    wall_s2 = Entity(name="wall_s2", model=preload['wall_s2'], position=(0, 0.5, -15), collider='box')
    wall_s3 = Entity(name="wall_s3", model=preload['wall_s3'], position=(10, 0.5, -15), collider='box')

    # ──────────────── Left Wall (West) ────────────────
    wall_w1 = Entity(name="wall_w1", model=preload['wall_w1'], position=(-15, 0.5, -10), rotation=(0, 90, 0), collider='box')
    wall_w2 = Entity(name="wall_w2", model=preload['wall_w2'], position=(-15, 0.5, 0), rotation=(0, 90, 0), collider='box')
    wall_w3 = Entity(name="wall_w3", model=preload['wall_w3'], position=(-15, 0.5, 10), rotation=(0, 90, 0), collider='box')

    # ──────────────── Right Wall (East) ────────────────
    wall_e1 = Entity(name="wall_e1", model=preload['wall_e1'], position=(15, 0.5, -10), rotation=(0, 90, 0), collider='box')
    wall_e2 = Entity(name="wall_e2", model=preload['wall_e2'], position=(15, 0.5, 0), rotation=(0, 90, 0), collider='box')
    wall_e3 = Entity(name="wall_e3", model=preload['wall_e3'], position=(15, 0.5, 10), rotation=(0, 90, 0), collider='box')

    # ──────────────── North Flank Walls (between top wall and top houses) ────────────────
    north_fw1 = Entity(name="north_fw1", model=preload['north_fw1'], position=(-6, 0.5, 10), collider='box')
    north_fw2 = Entity(name="north_fw2", model=preload['north_fw2'], position=(0, 0.5, 11), collider='box')
    north_fw3 = Entity(name="north_fw3", model=preload['north_fw3'], position=(6, 0.5, 10), collider='box')

    # ──────────────── South Flank Walls (between bottom wall and bottom houses) ────────────────
    south_fw1 = Entity(name="south_fw1", model=preload['south_fw1'], position=(-6, 0.5, -10), collider='box')
    south_fw2 = Entity(name="south_fw2", model=preload['south_fw2'], position=(0, 0.5, -11), collider='box')
    south_fw3 = Entity(name="south_fw3", model=preload['south_fw3'], position=(6, 0.5, -10), collider='box')

    # ──────────────── West Flank Walls (between left wall and left houses) ────────────────
    west_fw1 = Entity(name="west_fw1", model=preload['west_fw1'], position=(-10, 0.5, -6), rotation=(0, 90, 0), collider='box')
    west_fw2 = Entity(name="west_fw2", model=preload['west_fw2'], position=(-11, 0.5, 0), rotation=(0, 90, 0), collider='box')
    west_fw3 = Entity(name="west_fw3", model=preload['west_fw3'], position=(-10, 0.5, 6), rotation=(0, 90, 0), collider='box')

    # ──────────────── East Flank Walls (between right wall and right houses) ────────────────
    east_fw1 = Entity(name="east_fw1", model=preload['east_fw1'], position=(10, 0.5, -6), rotation=(0, 90, 0), collider='box')
    east_fw2 = Entity(name="east_fw2", model=preload['east_fw2'], position=(11, 0.5, 0), rotation=(0, 90, 0), collider='box')
    east_fw3 = Entity(name="east_fw3", model=preload['east_fw3'], position=(10, 0.5, 6), rotation=(0, 90, 0), collider='box')
    print("Walls created!")

    player.health_bar = HealthBar(
        name="health_bar", 
        max_value=100, 
        value=100, 
        bar_color=color.green.tint(-.2), 
        scale=(.4, .03), 
        position=(-.5, .45), 
        roundness=.5, 
        show_text=True, 
        parent=camera.ui
    )
    print("Health bar created")

    # Gun pickup
    gun = Button(
        name="gun_pickup",
        parent=scene,
        model='assets/pistol.gltf',
        position=(1, 1, 1),
        collider='box',
        scale=0.1,
        color=color.gray.tint(-.2)
    )
    print("Gun pickup created")

    gun.on_click = lambda: (
        setattr(gun, 'parent', camera),
        setattr(gun, 'position', Vec3(0.2, -0.2, 2)),
        setattr(gun, 'rotation', Vec3(0, 0, 0)),
        setattr(gun, 'scale', Vec3(0.3, 0.3, 0.3)),
        setattr(player, 'gun', gun),
        print("Gun picked up!")
    )

    # ──────────────── AI Bots ────────────────

    # Top left corner (free of houses/walls)
    AIBot(position=(-10, 2, 10), patrol_area=(4, 4), chase_range=12, speed=1)

    # Bottom right corner
    AIBot(position=(10, 2, -10), patrol_area=(4, 4), chase_range=8, speed=1)

    # Middle-left flank area
    AIBot(position=(-10, 2, 0), patrol_area=(3, 5), chase_range=0, speed=1)

    # Middle-right flank area
    AIBot(position=(10, 2, 0), patrol_area=(3, 5), chase_range=4, speed=1)

    # Bottom-center between houses and wall
    AIBot(position=(0, 2, -12), patrol_area=(5, 3), chase_range=5, speed=1)
    print("AI Bots created")

    # Bind buttons
    button_jump.on_click = player.jump
    button_shoot.on_click = player.shoot
    print("Buttons bound")

    Sky()
    print("Sky created")

def update():
    global settings_menu, speed_slider, jump_slider, sensx_slider, sensy_slider, player

    print("Updating game state...")

    if mouse.left and isinstance(mouse.hovered_entity, Button):
        return

    # Apply settings from sliders if settings menu is open
    if settings_menu and player:
        if speed_slider:
            player.speed = speed_slider.value
            print(f"Player speed set to {player.speed}")
        if jump_slider:
            player.jump_height = jump_slider.value
            print(f"Player jump height set to {player.jump_height}")
        if sensx_slider:
            player.mouse_sensitivity.x = sensx_slider.value
            print(f"Player mouse sensitivity X set to {player.mouse_sensitivity.x}")
        if sensy_slider:
            player.mouse_sensitivity.y = sensy_slider.value
            print(f"Player mouse sensitivity Y set to {player.mouse_sensitivity.y}")

show_main_menu()
app.run()
