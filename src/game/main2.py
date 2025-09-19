from setup_ursina_android import setup_ursina_android
setup_ursina_android()

from ursina import *
from ursina.prefabs.health_bar import HealthBar
from ursina.sequence import Sequence
from ursina.ursinamath import lerp, distance
import random
import time
import math

app = Ursina()
window.vsync = False

# Global variables
main_menu = None
pause_menu = None
settings_menu = None
pause_button = None
settings_button = None
game_started = False
player_alive = True
menu_background = None

speed_slider = None
jump_slider = None
sensx_slider = None
sensy_slider = None
volume_slider = None

ai_bots = []
bot_tasks = []
sequences  = []

joystick_move = None
joystick_look = None
button_jump = None
button_shoot = None

# Preload models (copied exactly to avoid runtime freezes)
preload = {}
preload['bullet'] = load_model('assets/bullet.gltf')
preload['gunshot'] = Audio('assets/gunshot.wav', loop=False, autoplay=False, volume=0.2)

preload['house1'] = load_model('assets/building_01.gltf')
preload['house2'] = load_model('assets/building_01.gltf')
preload['house3'] = load_model('assets/building_01.gltf')
preload['house4'] = load_model('assets/building_01.gltf')

preload['wall_n1'] = load_model('assets/wall_03.gltf')
preload['wall_n2'] = load_model('assets/wall_03.gltf')
preload['wall_n3'] = load_model('assets/wall_03.gltf')

preload['wall_s1'] = load_model('assets/wall_03.gltf')
preload['wall_s2'] = load_model('assets/wall_03.gltf')
preload['wall_s3'] = load_model('assets/wall_03.gltf')

preload['wall_w1'] = load_model('assets/wall_03.gltf')
preload['wall_w2'] = load_model('assets/wall_03.gltf')
preload['wall_w3'] = load_model('assets/wall_03.gltf')

preload['wall_e1'] = load_model('assets/wall_03.gltf')
preload['wall_e2'] = load_model('assets/wall_03.gltf')
preload['wall_e3'] = load_model('assets/wall_03.gltf')

preload['north_fw1'] = load_model('assets/wall_01.gltf')
preload['north_fw2'] = load_model('assets/wall_01.gltf')
preload['north_fw3'] = load_model('assets/wall_01.gltf')

preload['south_fw1'] = load_model('assets/wall_01.gltf')
preload['south_fw2'] = load_model('assets/wall_01.gltf')
preload['south_fw3'] = load_model('assets/wall_01.gltf')

preload['west_fw1'] = load_model('assets/wall_01.gltf')
preload['west_fw2'] = load_model('assets/wall_01.gltf')
preload['west_fw3'] = load_model('assets/wall_01.gltf')

preload['east_fw1'] = load_model('assets/wall_01.gltf')
preload['east_fw2'] = load_model('assets/wall_01.gltf')
preload['east_fw3'] = load_model('assets/wall_01.gltf')

class Draggable(Button):
    def __init__(self, model='circle', color=color.white, **kwargs):
        print("Draggable __init__ called")
        super().__init__(model=model, color=color, **kwargs)
        print("Draggable super().__init__ called")
        self.dragging = False
        self.lock = Vec3(0,0,0)
        self.min_x = -inf
        self.max_x = inf
        self.min_y = -inf
        self.max_y = inf
        self.min_z = -inf
        self.max_z = inf
        print("Draggable initialized with lock =", self.lock, "min_x =", self.min_x, "max_x =", self.max_x, "min_y =", self.min_y, "max_y =", self.max_y, "min_z =", self.min_z, "max_z =", self.max_z)

    def input(self, key):
        if key == 'left mouse down' and self.hovered:
            self.dragging = True
        if key == 'left mouse up':
            self.dragging = False

    def update(self):
        if self.dragging:
            if not self.lock[0]:
                self.x = mouse.x - self.parent.x
            if not self.lock[1]:
                self.y = mouse.y - self.parent.y
            if not self.lock[2]:
                self.z = mouse.z - self.parent.z
            self.x = clamp(self.x, self.min_x, self.max_x) * 2
            self.y = clamp(self.y, self.min_y, self.max_y) * 2
            self.z = clamp(self.z, self.min_z, self.max_z) * 2

class VirtualJoystick(Entity):
    """
    On-screen joystick with constrained knob using Draggable.
    """
    def __init__(self, radius=50, knob_factor=2.5, position=(-.7, -.4), **kwargs):
        print("VirtualJoystick __init__ called")
        super().__init__(parent=camera.ui, position=position, **kwargs)
        print("VirtualJoystick super().__init__ called")
        self.knob_factor = knob_factor
        self.diameter_px = radius * 2
        self.radius_px = radius
        self._init_w, self._init_h = window.size
        h = self._init_h or 1
        self._base_ui_diam = (self.diameter_px / h) * 2
        self._base_ui_radius = (self.radius_px / h) * 2
        self.radius = self._base_ui_radius
        print("VirtualJoystick _calculated : _base_ui_diam =", self._base_ui_diam, "_base_ui_radius =", self._base_ui_radius, "radius =", self.radius)

        self.bg = Entity(parent=self, model='circle', color=color.rgba32(64,64,64,150), name='joystick_bg')
        self.knob = Draggable(parent=self, model='circle', color=color.white, name='joystick_knob')
        self.knob.always_on_top = True
        self.knob.start_position = Vec2(0,0)
        self.knob.lock = Vec3(0,0,1)
        self.knob.min_x = -self.radius
        self.knob.max_x = self.radius
        self.knob.min_y = -self.radius
        self.knob.max_y = self.radius
        self.knob.min_z = -inf
        self.knob.max_z = inf
        print("VirtualJoystick knob configured with : always_on_top =", self.knob.always_on_top, "lock =", self.knob.lock, "min_x =", self.knob.min_x, "max_x =", self.knob.max_x, "min_y =", self.knob.min_y, "max_y =", self.knob.max_y, "min_z =", self.knob.min_z, "max_z =", self.knob.max_z)

        self.value = Vec2(0,0)
        self._apply_scale(1.0)

    def _apply_scale(self, ratio):
        ui_d = self._base_ui_diam * ratio
        ui_r = self._base_ui_radius * ratio

        self.scale = Vec2(ui_d, ui_d)
        self.bg.scale = Vec2(1,1)
        self.knob.scale = Vec2(ui_r * self.knob_factor, ui_r * self.knob_factor)

        self.max_offset = (ui_r * self.knob_factor) / 2
        self.radius = self.max_offset

    def update(self):
        cur_w, _ = window.size
        ratio = cur_w / (self._init_w or cur_w)
        self._apply_scale(ratio)

        if held_keys['left mouse'] and mouse.hovered_entity == self.knob:
            self.knob.dragging = True
        else:
            self.knob.dragging = False

        if self.knob.dragging:
            self.value = Vec2(self.knob.x, self.knob.y) / self.radius
        else:
            self.knob.position = Vec3(0,0,0)
            self.value = Vec2(0,0)

# Modified VirtualButton to trigger on hover (on_mouse_enter)
class VirtualButton(Button):
    def __init__(self, key_name='space', size_px=40, position=(.7,-.4), color=color.azure, **kwargs):
        print("VirtualButton __init__ called")
        super().__init__(parent=camera.ui, model='circle', collider='box', position=position, color=color, **kwargs)
        print("VirtualButton super().__init__ called")
        self.key_name = key_name
        self.size_px = size_px
        self._init_w, self._init_h = window.size
        h = self._init_h or 1
        self._base_ui_size = (self.size_px / h) * 2
        self.scale = self._base_ui_size
        print("VirtualButton _calculated : key_name =", self.key_name, "size_px =", self.size_px, "_init_h =", self._init_h, "_base_ui_size =", self._base_ui_size, "scale =", self.scale)

    def update(self):
        cur_w, _ = window.size
        ratio = cur_w / (self._init_w or cur_w)
        self.scale = self._base_ui_size * ratio

    def on_mouse_enter(self):
        # simulate "key down"
        held_keys[self.key_name] = 1
        # call input with key down semantics
        self.input(f'{self.key_name} down')

    def on_mouse_exit(self):
        # simulate "key up"
        held_keys[self.key_name] = 0
        self.input(f'{self.key_name} up')

    def input(self, key):
        # your existing logic can respond to "key up" or "key down"
        if key == f'{self.key_name} up':
            held_keys[self.key_name] = 0
        elif key == f'{self.key_name} down':
            held_keys[self.key_name] = 1

# HealthMixin unchanged
class HealthMixin:
    def __init__(self, health=100, **kwargs):
        self.health = health
        super().__init__(**kwargs)
        print("HealthMixin __init__ called with health =", health)

    def take_damage(self, amount):
        self.health -= amount
        print(f"{self} took {amount} damage, health now {self.health}")
        if self.health <= 0:
            print(f"{self} has died.")
            self.die()

    def die(self):
        pass

# DynamicCrosshair unchanged
class DynamicCrosshair(Entity):
    def __init__(self, player=None, line_length=0.03, line_thickness=0.002,
                 reticle_speed=5, reticle_distance=0.02, dot_scale=0.01, **kwargs):
        super().__init__(parent=camera.ui, position=(0,0))
        self.player = player
        self.reticle_speed = reticle_speed
        self.reticle_distance = reticle_distance
        self.shoot_offset = 0
        self.dot = Entity(parent=self, model='circle', color=color.white, scale=dot_scale, position=(0,0), name='crosshair_dot')
        self.lines = {}
        self.lines['top'] = Entity(parent=self, model='quad', color=color.white,
                                   scale=(line_thickness, line_length), position=(0, line_length/2 + 0.01), name='crosshair_top')
        self.lines['bottom'] = Entity(parent=self, model='quad', color=color.white,
                                      scale=(line_thickness, line_length), position=(0, -line_length/2 - 0.01), name='crosshair_bottom')
        self.lines['left'] = Entity(parent=self, model='quad', color=color.white,
                                    scale=(line_length, line_thickness), position=(-line_length/2 - 0.01, 0), name='crosshair_left')
        self.lines['right'] = Entity(parent=self, model='quad', color=color.white,
                                     scale=(line_length, line_thickness), position=(line_length/2 + 0.01, 0), name='crosshair_right')
        self.original_positions = {k: v.position for k,v in self.lines.items()}
        print("DynamicCrosshair initialized with player =", player, "line_length =", line_length, "line_thickness =", line_thickness, "reticle_speed =", reticle_speed, "reticle_distance =", reticle_distance, "dot_scale =", dot_scale)

    def update(self):
        speed = getattr(self.player, 'velocity', Vec3(0,0,0)).length() if self.player else 1
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
            line.position = lerp(line.position, Vec3(x, y, 0), time.dt * self.reticle_speed)
        self.shoot_offset = lerp(self.shoot_offset, 0, time.dt * 10)

# FSM base class
class FSM:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.state = None

    def change_state(self, new_state):
        if self.state and hasattr(self.state, 'exit'):
            self.state.exit()
        self.state = new_state
        if self.state and hasattr(self.state, 'enter'):
            self.state.enter()

    def update(self):
        if self.state and hasattr(self.state, 'update'):
            self.state.update()

# FirstPersonController with FSM
class FirstPersonController(Entity, HealthMixin, FSM):
    def __init__(self, **kwargs):
        Entity.__init__(self)
        HealthMixin.__init__(self, health=100)
        FSM.__init__(self)
        print("FirstPersonController __init__ called")

        self.speed = 5
        self.height = 2
        self.camera_pivot = Entity(parent=self, y=self.height, name='camera_pivot')
        camera.parent = self.camera_pivot
        camera.position = (0,0,0)
        camera.rotation = (0,0,0)
        camera.fov = 90

        self.use_touch = True
        mouse.locked = False
        mouse.visible = True
        self.mouse_sensitivity = Vec2(40,40)

        self.gravity = 1
        self.grounded = False
        self.jump_height = 2
        self.jump_up_duration = 0.5
        self.fall_after = 0.35
        self.air_time = 0
        self.max_step_height = 0.5

        self.traverse_target = scene
        self.ignore_list = [self]
        self.gun = None

        self._next_fire_time = 0

        self.headbob_amplitude = 0.05
        self.headbob_frequency = 2.0
        self.headbob_timer = 0.0
        self.camera_original_pos = camera.position

        self.recoil_pitch = 0.0
        self.recoil_yaw = 0.0
        self.recoil_recover_speed = 5.0
        self.recoil_amount = Vec2(0.5, 0.1)
        print("FirstPersonController recoil configured with : recoil_recover_speed =", self.recoil_recover_speed, "recoil_amount =", self.recoil_amount, "recoil_pitch =", self.recoil_pitch, "recoil_yaw =", self.recoil_yaw, "camera_original_pos =", self.camera_original_pos, "headbob_amplitude =", self.headbob_amplitude, "headbob_frequency =", self.headbob_frequency, "headbob_timer =", self.headbob_timer, "gun =", self.gun, "_next_fire_time =", self._next_fire_time, "ignore_list =", self.ignore_list, "traverse_target =", self.traverse_target, "max_step_height =", self.max_step_height, "air_time =", self.air_time, "fall_after =", self.fall_after, "jump_up_duration =", self.jump_up_duration, "jump_height =", self.jump_height, "grounded =", self.grounded, "gravity =", self.gravity, "mouse_sensitivity =", self.mouse_sensitivity, "use_touch =", self.use_touch, "height =", self.height, "speed =", self.speed)

        self.crosshair = DynamicCrosshair(player=self)

        self.damage_overlay = Entity(
            parent=camera.ui,
            model='quad',
            color=color.rgba(255,0,0,0),
            scale=(2,2),
            z=-1
        )

        for key, value in kwargs.items():
            setattr(self, key, value)

        if self.gravity:
            ray = raycast(self.world_position + (0, self.height, 0), self.down, traverse_target=self.traverse_target, ignore=self.ignore_list)
            if ray.hit:
                self.y = ray.world_point.y

        self.change_state(self.IdleState(self))

    def update(self):
        self.update_state()
        self.crosshair.update()
        if self.damage_overlay.color.a > 0:
            new_alpha = max(0, self.damage_overlay.color.a - time.dt)
            self.damage_overlay.color = color.rgba(255,0,0,new_alpha)

    def update_state(self):
        if self.state:
            self.state.update()

    def input(self, key):
        if self.state:
            self.state.input(key)

    def jump(self):
        if self.grounded:
            print("FirstPersonController jump: Called")
            self.change_state(self.JumpingState(self))

    def shoot(self):
        if self.gun and time.time() >= self._next_fire_time:
            self._next_fire_time = time.time() + 0.25
            # gunshot.play()
            preload['gunshot'].play()
            self.gun.blink(color.gray)
            self.recoil_pitch += self.recoil_amount.x
            self.recoil_yaw += random.uniform(-self.recoil_amount.y, self.recoil_amount.y)
            hit = raycast(camera.world_position, camera.forward, distance=100, traverse_target=scene, ignore=[self, self.gun])
            bullet = Entity(parent=self.gun, model=preload['bullet'], scale=0.2, position=(0.2,0.1,0), color=color.gold, name='player_bullet')
            bullet.world_parent = scene
            seq = bullet.animate_position(bullet.position + (camera.forward * 50), curve=curve.linear, duration=1)
            sequences.append(seq)
            destroy(bullet, delay=1)
            if hit.hit and hasattr(hit.entity, 'take_damage'):
                print(f"Hit {hit.entity} at {hit.world_point}, applying damage.")
                hit.entity.take_damage(50)

    def take_damage(self, amount):
        super().take_damage(amount)
        if hasattr(self, 'health_bar'):
            self.health_bar.value = self.health
            print(f"Player health updated: {self.health}")
        self.damage_overlay.color = color.rgba(255,0,0,0.3)
        if self.health <= 0:
            self.change_state(self.DeadState(self))

    def land(self) -> None:
        """Reset air_time on landing."""
        print("FirstPersonController land: Called")
        self.air_time = 0
        self.grounded = True

    class IdleState:
        def __init__(self, controller):
            self.controller = controller

        def enter(self):
            self.controller.velocity = Vec3(0,0,0)

        def update(self):
            self.handle_movement()
            self.handle_look()

        def input(self, key):
            if key in ('space', 'gamepad a'):
                self.controller.jump()
            if key == 'left mouse down' and not self.controller.use_touch:
                self.controller.shoot()
            if key == 'gamepad x':
                self.controller.shoot()
            if key == 't':
                self.controller.use_touch = not self.controller.use_touch
                mouse.locked = not self.controller.use_touch
                mouse.visible = self.controller.use_touch
                if joystick_move:
                    joystick_move.enabled = self.controller.use_touch
                    joystick_move.visible = self.controller.use_touch
                if joystick_look:
                    joystick_look.enabled = self.controller.use_touch
                    joystick_look.visible = self.controller.use_touch
                if button_jump:
                    button_jump.enabled = self.controller.use_touch
                    button_jump.visible = self.controller.use_touch
                if button_shoot:
                    button_shoot.enabled = self.controller.use_touch
                    button_shoot.visible = self.controller.use_touch

        def handle_look(self):
            if self.controller.use_touch:
                rot = joystick_look.value
                yaw_gain = 100
                pitch_gain = 100
                self.controller.rotation_y += rot.x * time.dt * yaw_gain
                self.controller.camera_pivot.rotation_x = clamp(self.controller.camera_pivot.rotation_x - rot.y * time.dt * pitch_gain, -90, 90)
            else:
                if mouse.locked:
                    self.controller.rotation_y += mouse.velocity[0] * self.controller.mouse_sensitivity[1]
                    self.controller.camera_pivot.rotation_x -= mouse.velocity[1] * self.controller.mouse_sensitivity[0]
                    self.controller.camera_pivot.rotation_x = clamp(self.controller.camera_pivot.rotation_x, -90, 90)

        def handle_movement(self):
            if self.controller.use_touch:
                move_x = joystick_move.value.x
                move_y = joystick_move.value.y
            else:
                move_x = held_keys['d'] - held_keys['a']
                move_y = held_keys['w'] - held_keys['s']
            direction = Vec3(self.controller.forward * move_y + self.controller.right * move_x).normalized()
            self.controller.velocity = direction * self.controller.speed
            if direction:
                feet = raycast(self.controller.position + Vec3(0, 0.5, 0), direction, traverse_target=self.controller.traverse_target, ignore=self.controller.ignore_list, distance=0.5)
                head = raycast(self.controller.position + Vec3(0, self.controller.height - 0.1, 0), direction, traverse_target=self.controller.traverse_target, ignore=self.controller.ignore_list, distance=0.5)
                if feet.hit and not head.hit:
                    step_height = min(self.controller.max_step_height, feet.world_point.y - self.controller.y)
                    self.controller.y += step_height
                if not (feet.hit or head.hit):
                    self.controller.position += direction * self.controller.speed * time.dt
            # Gravity & landing
            if self.controller.gravity:
                down_ray = raycast(self.controller.world_position + (0, self.controller.height, 0), self.controller.down, traverse_target=self.controller.traverse_target, ignore=self.controller.ignore_list)
                if down_ray.distance <= self.controller.height + 0.1 and down_ray.world_normal.y > 0.7:
                    if not self.controller.grounded:
                        self.controller.land()
                    self.controller.grounded = True
                    self.controller.y = down_ray.world_point.y
                else:
                    self.controller.grounded = False
                    self.controller.y -= min(self.controller.air_time, down_ray.distance - 0.05) * time.dt * 100
                    self.controller.air_time += time.dt * 0.25 * self.controller.gravity
            displacement = self.controller.velocity.length()
            if self.controller.grounded and displacement > 0.01:
                self.controller.headbob_timer += time.dt * self.controller.headbob_frequency * (displacement / self.controller.speed)
                bob_offset = math.sin(self.controller.headbob_timer * math.pi * 2) * self.controller.headbob_amplitude
                sway_offset = math.sin(self.controller.headbob_timer * math.pi * 4) * (self.controller.headbob_amplitude / 2)
                camera.position = self.controller.camera_original_pos + Vec3(sway_offset, bob_offset, 0)
            else:
                camera.position = lerp(camera.position, self.controller.camera_original_pos, time.dt * 8)
            # Recoil recovery
            if self.controller.recoil_pitch != 0 or self.controller.recoil_yaw != 0:
                self.controller.recoil_pitch = lerp(self.controller.recoil_pitch, 0, time.dt * self.controller.recoil_recover_speed)
                self.controller.recoil_yaw = lerp(self.controller.recoil_yaw, 0, time.dt * self.controller.recoil_recover_speed)
                self.controller.camera_pivot.rotation_x -= self.controller.recoil_pitch
                self.controller.rotation_y += self.controller.recoil_yaw
            self.controller.crosshair.shoot_offset = self.controller.recoil_pitch * 0.05

    class JumpingState:
        def __init__(self, controller):
            self.controller = controller
            self.seq = None

        def enter(self):
            self.controller.grounded = False
            self.seq = self.controller.animate_y(
                self.controller.y + self.controller.jump_height,
                self.controller.jump_up_duration,
                resolution=int(1 // time.dt),
                curve=curve.out_expo
            )
            sequences.append(self.seq)
            invoke(self.start_fall, delay=self.controller.fall_after)

        def start_fall(self):
            self.controller.air_time += time.dt

        def update(self):
            # Gravity & landing handled similarly to IdleState
            if self.controller.gravity:
                down_ray = raycast(self.controller.world_position + (0, self.controller.height, 0), self.controller.down, traverse_target=self.controller.traverse_target, ignore=self.controller.ignore_list)
                if down_ray.distance <= self.controller.height + 0.1 and down_ray.world_normal.y > 0.7:
                    self.controller.land()
                    self.controller.change_state(self.controller.IdleState(self.controller))
                else:
                    self.controller.y -= min(self.controller.air_time, down_ray.distance - 0.05) * time.dt * 100
                    self.controller.air_time += time.dt * 0.25 * self.controller.gravity

        def input(self, key):
            pass

    class DeadState:
        def __init__(self, controller):
            self.controller = controller

        def enter(self):
            self.controller.health_bar.value = 0
            global player_alive
            player_alive = False
            
            # Detach camera so it’s not destroyed with the controller
            camera.parent = scene

            # Hide the player instead of destroying immediately
            self.controller.enabled = False
            self.controller.visible = False

            # Schedule proper cleanup a bit later
            def delayed_cleanup():
                destroy(self.controller)  # safe now, no mid-frame destroy
                game_over()

            invoke(delayed_cleanup, delay=2)  # wait so player sees the death message

        def update(self):
            pass

        def input(self, key):
            pass

# DummyTarget unchanged
class DummyTarget(Entity, HealthMixin):
    def __init__(self, **kwargs):
        super().__init__(health=100, model='cube', color=color.orange, collider='box', scale=(1,2,1), name='dummy_target', **kwargs)
        print("DummyTarget __init__ called")
        self.spawn_point = self.position
        self.visible = True
        self.enabled = True
        self.health_bar = HealthBar(max_value=100, value=100, scale=(.3,.02), bar_color=color.red.tint(-.2), roundness=.5, show_text=False, parent=self)
        self.health_bar.x = 0.1
        self.health_bar.y = 1
        self.health_bar.billboard = True
        self.original_color = self.color
        self.flash_intensity = 0
        print("DummyTarget initialized with health =", self.health, "spawn_point =", self.spawn_point, "visible =", self.visible, "enabled =", self.enabled)

    def take_damage(self, amount):
        if not self.enabled:
            return
        super().take_damage(amount)
        try:
            if self.health_bar and self.health_bar.enabled:
                self.health_bar.value = self.health
        except AssertionError:
            pass
        self.flash_intensity = 1

    def update(self):
        if self.flash_intensity > 0:
            self.flash_intensity = max(0, self.flash_intensity - time.dt * 2)
            self.color = color.rgb32(
                lerp(255, self.original_color[0]*255, 1 - self.flash_intensity),
                lerp(0, self.original_color[1]*255, 1 - self.flash_intensity),
                lerp(0, self.original_color[2]*255, 1 - self.flash_intensity)
            )

    def die(self):
        destroy(self)

# AIBot with FSM
class AIBot(FSM, DummyTarget):
    def __init__(self, patrol_area=(10,10), chase_range=5, speed=1, **kwargs):
        super().__init__(**kwargs)
        print("AIBot __init__ called")
        self.patrol_area = patrol_area
        self.chase_range = chase_range
        self.speed = speed

        # --- new tuning parameters (cheap/simple avoidance) ---
        self._target_cooldown = 1.5          # seconds between choosing a new random target
        self._last_target_time = 0
        self._avoid_distance = 0.9           # distance to check for frontal obstacle
        self._avoid_side_distance = 0.7      # lateral feeler length
        self._avoid_strength = 1.0           # how strongly to steer away from obstacles
        self._neighbor_avoid_radius = 1.4
        self._fov_dot_threshold = 0.65       # cos(angle) threshold for "in front" check (~49 degrees)
        self._sight_distance = 50
        
        self.fire_interval = 3
        self._next_fire_time = 0
        self.alive = True
        self.is_chasing = False
        print("AIBot initialized with patrol_area =", patrol_area, "chase_range =", chase_range, "speed =", speed, "fire_interval =", self.fire_interval, "_next_fire_time =", self._next_fire_time, "alive =", self.alive, "is_chasing =", self.is_chasing)
        self.gun = Entity(parent=self, model='assets/pistol.gltf', color=color.gray.tint(-.2), position=Vec3(.2,.1,.8), rotation=Vec3(0,0,0), scale=0.1, name='ai_gun')
        self.target_pos = self.get_valid_ground_position()
        ai_bots.append(self)
        self.change_state(self.PatrolState(self))
        self.update_task = invoke(self.update_state, delay=1)
        bot_tasks.append(self.update_task)

    def update_state(self):
        if not self.enabled:
            return
        self.update()
        if self.update_task:
            self.update_task.finish()
            if self.update_task in bot_tasks:
                bot_tasks.remove(self.update_task)
        self.update_task = invoke(self.update_state, delay=0.1)
        bot_tasks.append(self.update_task)

    def get_valid_ground_position(self, max_attempts=8, initial=False):
        """
        Cheap sampling of ground points within patrol_area, but only run when needed (caller should respect cooldown).
        Returns a Vec3; if nothing valid found quickly, returns a nearby fallback position.
        """
        # If not initial call, respect cooldown and return current target if it's still valid
        if not initial and time.time() - self._last_target_time < self._target_cooldown:
            return self.target_pos

        for _ in range(max_attempts):
            x = random.uniform(-self.patrol_area[0], self.patrol_area[0])
            z = random.uniform(-self.patrol_area[1], self.patrol_area[1])
            test_pos = Vec3(x, 20, z)
            ground_ray = raycast(test_pos, direction=Vec3(0,-1,0), distance=50, ignore=[self], traverse_target=scene)
            if ground_ray.hit:
                y = ground_ray.world_point.y + 1
                self._last_target_time = time.time()
                return Vec3(x,y,z)

        # fallback: small jitter from current position (cheap)
        self._last_target_time = time.time()
        return self.position + Vec3(random.uniform(-2,2), 0, random.uniform(-2,2))

    def avoid_obstacles(self, desired_dir):
        """
        Simple steering-based obstacle avoidance:
        - one front feeler
        - two side feelers to choose a sidestep direction
        - neighbor avoidance (other bots / player closeness)
        Returns an adjusted normalized direction.
        """
        if desired_dir.length() == 0:
            return desired_dir

        origin = self.position + Vec3(0, 0.5, 0)
        # frontal check
        front_hit = raycast(origin, desired_dir, distance=self._avoid_distance, ignore=[self], traverse_target=scene)

        # compute neighbor avoidance vector (push away from close bots / player)
        away = Vec3(0,0,0)
        for other in ai_bots:
            if other is not self and distance(self.position, other.position) < self._neighbor_avoid_radius:
                away_dir = (self.position - other.position).normalized()
                away += away_dir * (self._neighbor_avoid_radius - distance(self.position, other.position))
        # optionally also avoid player if super close
        if player and player in scene.entities and distance(self.position, player.position) < 1.0:
            away += (self.position - player.position).normalized() * 0.8

        if not front_hit.hit:
            # no obstacle directly ahead -> mild steering from neighbors only
            new_dir = (desired_dir + away * 0.6).normalized()
            return new_dir
        
        lateral = Vec3(-desired_dir.z, 0, desired_dir.x).normalized()
        left_hit = raycast(origin, (desired_dir + lateral * 0.8).normalized(), distance=self._avoid_side_distance, ignore=[self], traverse_target=scene)
        right_hit = raycast(origin, (desired_dir - lateral * 0.8).normalized(), distance=self._avoid_side_distance, ignore=[self], traverse_target=scene)

        # choose the side with no hit; if both hit, try backing up / random sidestep
        if not left_hit.hit and right_hit.hit:
            steer = (desired_dir + lateral * self._avoid_strength).normalized()
        elif not right_hit.hit and left_hit.hit:
            steer = (desired_dir - lateral * self._avoid_strength).normalized()
        elif not left_hit.hit and not right_hit.hit:
            steer = (desired_dir + lateral * (0.6 if random.random() < 0.5 else -0.6)).normalized()
        else:
            # both sides blocked -> back up a little then pick a new target (cheap)
            steer = (-desired_dir * 0.5 + lateral * (0.5 if random.random() < 0.5 else -0.5)).normalized()
            # also set a new target soon (cooldown overridden)
            self._last_target_time = 0  # allow immediate new target on next get_valid_ground_position()

        # apply neighbor avoidance
        steer = (steer + away * 0.8).normalized()
        return steer


    def can_see_player(self):
        if not player or player not in scene.entities:
            return False

        eye_pos = self.position + Vec3(-.1, .5, .3)
        dir_to_player = (player.position - eye_pos)
        if dir_to_player.length() == 0:
            return True
        dir_to_player = dir_to_player.normalized()

        # FOV check (XZ plane only)
        forward = Vec3(self.forward.x, 0, self.forward.z).normalized()
        player_dir_xz = Vec3(dir_to_player.x, 0, dir_to_player.z).normalized()
        dot = forward.dot(player_dir_xz)
        if dot < self._fov_dot_threshold:
            return False

        # Raycast LOS
        ignore_list = [self] + [b for b in ai_bots if b is not self]
        hit = raycast(
            origin=eye_pos,
            direction=dir_to_player,
            distance=self._sight_distance,
            ignore=ignore_list,
            traverse_target=scene
        )
        print("AIBot can_see_player: Raycast hit =", hit.entity)

        if not hit.hit:
            return False

        hit_entity = hit.entity

        # Check if hit is player, player's child, or player's parent
        if hit_entity == player or hit_entity == player.gun:
            return True
        if hit_entity in player.children:
            return True
        if player in hit_entity.children:
            return True

        return False


    class PatrolState:
        def __init__(self, bot):
            self.bot = bot

        def enter(self):
            self.bot.is_chasing = False
            if distance(self.bot.position, self.bot.target_pos) < 0.6 or time.time() - self.bot._last_target_time > self.bot._target_cooldown:
                self.bot.target_pos = self.bot.get_valid_ground_position()

        def update(self):
            # quick guard: ensure objects still in the scene
            if self.bot not in scene.entities or player not in scene.entities:
                return
            try:
                dist_to_player = distance(self.bot.position, player.position)
            except AssertionError:
                return
            if dist_to_player < self.bot.chase_range:
                self.bot.change_state(self.bot.ChaseState(self.bot))
                return
            # compute movement toward target_pos
            desired_dir = (self.bot.target_pos - self.bot.position)
            # zero out y component for planar movement
            desired_dir.y = 0
            if desired_dir.length() == 0 or distance(self.bot.position, self.bot.target_pos) < 0.5:
                # reached or no direction: pick a new target (but remember get_valid_ground_position has cooldown)
                self.bot.target_pos = self.bot.get_valid_ground_position()
                desired_dir = (self.bot.target_pos - self.bot.position)
                desired_dir.y = 0
                if desired_dir.length() == 0:
                    return
            desired_dir = desired_dir.normalized()
            # obstacle avoidance steering
            move_dir = self.bot.avoid_obstacles(desired_dir)
            blocked = False
            for other in ai_bots:
                if other is not self.bot and distance(self.bot.position, other.position) < 1.5:
                    blocked = True
                    break
            if distance(self.bot.position, player.position) < 1.5:
                blocked = True
            if not blocked:
                self.bot.position += move_dir * self.bot.speed * time.dt
            down_ray = raycast(self.bot.position + Vec3(0,0.5,0), Vec3(0,-1,0), ignore=[self.bot], traverse_target=scene)
            if down_ray.hit:
                self.bot.y = down_ray.world_point.y + 1
            self.bot.look_at(player.position)
            self.bot.rotation_x = 0
            self.bot.rotation_z = 0

        def exit(self):
            pass

    class ChaseState:
        def __init__(self, bot):
            self.bot = bot
            self.bot.is_chasing = True

        def enter(self):
            pass

        def update(self):
            # quick guard: ensure objects still in the scene
            if self.bot not in scene.entities or player not in scene.entities:
                return
            try:
                dist_to_player = distance(self.bot.position, player.position)
            except AssertionError:
                return
            if dist_to_player > self.bot.chase_range:
                self.bot.change_state(self.bot.PatrolState(self.bot))
                return
            if dist_to_player < 4:   # when close enough
                self.bot.change_state(self.bot.AttackState(self.bot))
                return
            desired_dir = (player.position - self.bot.position)
            desired_dir.y = 0
            if desired_dir.length() == 0:
                return
            desired_dir = desired_dir.normalized()
            # avoid obstacles while moving toward player
            move_dir = self.bot.avoid_obstacles(desired_dir)
            blocked = False
            for other in ai_bots:
                if other is not self.bot and distance(self.bot.position, other.position) < 1.5:
                    blocked = True
                    break
            if distance(self.bot.position, player.position) < 1.5:
                blocked = True
            if not blocked:
                self.bot.position += move_dir * self.bot.speed * time.dt
            down_ray = raycast(self.bot.position + Vec3(0,0.5,0), Vec3(0,-1,0), ignore=[self.bot], traverse_target=scene)
            if down_ray.hit:
                self.bot.y = down_ray.world_point.y + 1
            self.bot.look_at(player.position)
            self.bot.rotation_x = 0
            self.bot.rotation_z = 0

        def exit(self):
            pass

    class AttackState:
        def __init__(self, bot):
            self.bot = bot
        def enter(self):
            self.bot.is_chasing = False
        def update(self):
            if distance(self.bot.position, player.position) > self.bot.chase_range:
                self.bot.change_state(self.bot.PatrolState(self.bot))
                return
            self.bot.look_at(player.position)
            self.bot.rotation_x = 0
            self.bot.rotation_z = 0
            self.bot.shoot()

    def shoot(self):
        if not self.alive or not player or not self.enabled or time.time() < self._next_fire_time:
            return
        # do a FOV + line-of-sight check; only shoot if both pass
        if not self.can_see_player():
            return
        self._next_fire_time = time.time() + self.fire_interval
        # gunshot.play()
        preload['gunshot'].play()
        dir_to_player = (player.position - self.position).normalized()
        eye_pos = self.position + Vec3(-.1, .5, .3)
        bullet = Entity(model=preload['bullet'], color=color.gold, scale=0.2, position=eye_pos, collider='box', speed=30, name='ai_bullet')
        bullet.world_parent = scene
        bullet.look_at(player.position)
        def bullet_update(b=bullet):
            if not b or not b.enabled:
                return
            if not player or not hasattr(player, 'position') or player in scene.entities and player.enabled == False:
                destroy(b)
                return
            if not self or not hasattr(self, 'position') or not self.enabled:
                destroy(b)
                return
            hit_info = raycast(origin=b.position, direction=b.forward, distance=b.speed * time.dt, ignore=[b, self] + ai_bots, traverse_target=scene)
            if hit_info.hit:
                print(f"AIBot bullet hit {hit_info.entity} at {hit_info.world_point}")
                if hit_info.entity == player:
                    if hasattr(player, 'take_damage'):
                        player.take_damage(10)
                destroy(b)
                return
            b.position += b.forward * b.speed * time.dt
            if player and hasattr(player, 'position') and distance(b.position, player.position) < 1.0:
                if hasattr(player, 'take_damage'):
                    player.take_damage(10)
                destroy(b)
                return
            if self and hasattr(self, 'position') and distance(b.position, self.position) > 50:
                destroy(b)
                return
        bullet.update = bullet_update
        hit = raycast(origin=eye_pos, direction=dir_to_player, distance=50, ignore=[self], traverse_target=scene)
        if hit.hit and hit.entity == player:
            player.take_damage(10)
            self._next_fire_time = time.time() + self.fire_interval

    def die(self):
        # Mark dead and disable immediately so other logic stops early
        self.alive = False
        self.enabled = False

        # Pause scheduled updates BEFORE we destroy node/visuals
        if hasattr(self, 'update_task'):
            try:
                self.update_task.pause()
            except Exception:
                pass

        # Remove from global lists BEFORE destruction (avoid other code iterating over it)
        if self in ai_bots:
            ai_bots.remove(self)
        if hasattr(self, 'update_task') and self.update_task in bot_tasks:
            bot_tasks.remove(self.update_task)

        # Now run superclass cleanup, which will destroy visuals and health etc.
        super().die()

        # Do NOT call destroy(self) again here — super().die() already did it.
        if game_started and player_alive and len(ai_bots) == 0:
            Text("You Win!", origin=(0,0), scale=3, color=color.green, parent=camera.ui)
            invoke(quit_to_main_menu, delay=2)

# Game functions
def show_main_menu():
    global main_menu, menu_background
    print("Showing main menu")
    application.resume()
    mouse.visible = True
    mouse.locked = False
    lst1 = list(Sky.instances)
    for s in lst1:
        if s:
            print("Destroying sky instance:", s)
            destroy(s)
    Sky.instances.clear()
    menu_background = Entity(parent=camera.ui, model='quad', texture='assets/label.jpg', scale=(2,1), z=1)
    main_menu = Entity(name="main_menu", parent=camera.ui)
    Text(name="main_menu_title", text="Main Menu", scale=2, x=-0.125, y=0.4, parent=main_menu)
    singleplayer_button = Button(text='Singleplayer', scale=(.3,.1), y=0.15, parent=main_menu, on_click=start_singleplayer)
    multiplayer_button = Button(text='Multiplayer', scale=(.3,.1), y=-0.05, parent=main_menu, on_click=lambda: print("Multiplayer not implemented."))
    exit_button = Button(text='Exit', scale=(.3,.1), y=-0.25, parent=main_menu, on_click=application.quit)
    # Enable hover activation for touch devices
    singleplayer_button.on_mouse_enter = singleplayer_button.on_click
    multiplayer_button.on_mouse_enter = multiplayer_button.on_click
    exit_button.on_mouse_enter = exit_button.on_click
    print("Main menu displayed with buttons.")

def show_pause_menu():
    global pause_menu, resume_button, setting_button, quit_button, joystick_move, joystick_look, button_jump, button_shoot, player
    print("Showing pause menu")
    application.pause()
    pause_menu = Entity(name="pause_menu", parent=camera.ui)
    Text(name="pause_menu_title", text="Paused", scale=2, x=-0.1, y=0.3, parent=pause_menu)
    resume_button = Button(text='Resume', scale=(.3,.1), y=0.2, parent=pause_menu, on_click=resume_game)
    setting_button = Button(text='Setting', scale=(.3,.1), y=0, parent=pause_menu, on_click=setting_menu)
    quit_button = Button(text='Quit to Menu', scale=(.3,.1), y=-0.2, parent=pause_menu, on_click=quit_to_main_menu)
    # Enable hover activation for touch devices
    resume_button.on_mouse_enter = resume_button.on_click
    setting_button.on_mouse_enter = setting_button.on_click
    quit_button.on_mouse_enter = quit_button.on_click
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
    print("Pause menu displayed with buttons.")

def start_singleplayer():
    global game_started, menu_background, main_menu, player_alive, joystick_move, joystick_look, button_jump, button_shoot, pause_button, player, settings_menu, speed_slider, jump_slider, sensx_slider, sensy_slider, volume_slider
    print("Starting singleplayer game")
    application.resume()
    player_alive = True
    for t in bot_tasks:
        print("Finishing bot task:", t)
        t.finish()
    bot_tasks.clear()
    for b in ai_bots:
        print("Destroying AI bot:", b)
        destroy(b)
    ai_bots.clear()
    for seq in sequences:
        print("Finishing sequence:", seq)
        if isinstance(seq, Sequence):
            seq.finish()
    sequences.clear()
    destroy(main_menu)
    destroy(menu_background)
    # Cleanup previous game entities
    lst1 = list(scene.entities)
    for e in lst1:
        if e and e != camera:
            destroy(e)
    lst2 = list(camera.ui.children)
    for e in lst2:
        if e:
            destroy(e)
    lst3 = list(Sky.instances)
    for s in lst3:
        if s:
            destroy(s)
    Sky.instances.clear()
    # Set globals to None
    joystick_move = None
    joystick_look = None
    button_jump = None
    button_shoot = None
    pause_button = None
    player = None
    settings_menu = None
    speed_slider = None
    jump_slider = None
    sensx_slider = None
    sensy_slider = None
    volume_slider = None
    game_started = True
    setup_game()

def pause_game():
    global pause_button
    pause_button.enabled = False
    show_pause_menu()

def resume_game():
    global pause_menu, joystick_move, joystick_look, button_jump, button_shoot, player
    destroy(pause_menu)
    application.resume()
    pause_button.enabled = True
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
    print("Resumed game from pause menu")

def close_settings():
    global settings_menu, speed_slider, jump_slider, sensx_slider, sensy_slider
    print("Closing settings menu and applying settings")
    application.pause()
    destroy(settings_menu)
    settings_menu = None
    speed_slider = None
    jump_slider = None
    sensx_slider = None
    sensy_slider = None
    if pause_menu:
        pause_menu.enabled = True

def setting_menu():
    global pause_menu, settings_menu, speed_slider, jump_slider, sensx_slider, sensy_slider
    print("Opening settings menu")
    application.resume()
    if pause_menu:
        pause_menu.enabled = False
    settings_menu = Entity(name="settings_menu", parent=camera.ui)
    Text(name="settings_title", text="Settings", scale=2, x=-0.1, y=0.45, parent=settings_menu)
    Text(text="Player Speed", scale=1, x=-0.3, y=0.35, parent=settings_menu)
    speed_slider = Slider(min=1, max=10, default=player.speed if player else 5, step=0.1, x=0.1, y=0.35, parent=settings_menu)
    Text(text="Jump Height", scale=1, x=-0.3, y=0.25, parent=settings_menu)
    jump_slider = Slider(min=0.5, max=5, default=player.jump_height if player else 2, step=0.1, x=0.1, y=0.25, parent=settings_menu)
    Text(text="Mouse Sens X", scale=1, x=-0.3, y=0.15, parent=settings_menu)
    sensx_slider = Slider(min=10, max=100, default=player.mouse_sensitivity.x if player else 40, step=1, x=0.1, y=0.15, parent=settings_menu)
    Text(text="Mouse Sens Y", scale=1, x=-0.3, y=0.05, parent=settings_menu)
    sensy_slider = Slider(min=10, max=100, default=player.mouse_sensitivity.y if player else 40, step=1, x=0.1, y=0.05, parent=settings_menu)
    close_button = Button(text='Close', scale=(0.2,0.1), y=-0.35, parent=settings_menu, on_click=close_settings)
    # Enable hover activation for touch devices
    close_button.on_mouse_enter = close_button.on_click
    print("Settings menu displayed with sliders and close button.")

def quit_to_main_menu():
    print("Quitting to main menu")
    def cleanup():
        print("Cleaning up game entities and returning to main menu")
        global player, bot_tasks, ai_bots, sequences, pause_menu, main_menu, menu_background, joystick_move, joystick_look, button_jump, button_shoot, pause_button, settings_menu, speed_slider, jump_slider, sensx_slider, sensy_slider, volume_slider
        application.pause()
        for seq in list(sequences):
            print("Finishing sequence before quiting to main menu:", seq)
            if isinstance(seq, Sequence):
                seq.finish()
        sequences.clear()
        for t in list(bot_tasks):
            print("Finishing bot task before quiting to main menu:", t)
            t.finish()
        bot_tasks.clear()
        for b in list(ai_bots):
            print("Destroying AI bot before quiting to main menu:", b)
            destroy(b)
        ai_bots.clear()
        if player:
            if hasattr(player, 'children'):
                lst1 = list(player.children)
                for child in lst1:
                    if child:
                        print("Destroying player child entity before quiting to main menu:", child)
                        destroy(child)
            print("Destroying player before quiting to main menu:", player)
            destroy(player)
            player = None
        lst2 = list(scene.entities)
        for e in lst2:
            if e and e != camera:
                if hasattr(e, 'children'):
                    lst3 = list(e.children)
                    for child in lst3:
                        if child:
                            print("Destroying player child entity before quiting to main menu:", child)
                            destroy(child)
                print("Destroying scene entity before quiting to main menu:", e)
                destroy(e)
        lst4 = list(camera.ui.children)
        for e in lst4:
            if e:
                print("Destroying camera UI entity before quiting to main menu:", e)
                destroy(e)
        lst5 = list(Sky.instances)
        for s in lst5:
            if s:
                print("Destroying sky instance before quiting to main menu:", s)
                destroy(s)
        Sky.instances.clear()
        for ui_root in (main_menu, menu_background, pause_menu):
            if ui_root:
                print("Destroying UI root before quiting to main menu:", ui_root)
                destroy(ui_root)
        main_menu = None
        menu_background = None
        pause_menu = None
        joystick_move = None
        joystick_look = None
        button_jump = None
        button_shoot = None
        pause_button = None
        player = None
        settings_menu = None
        speed_slider = None
        jump_slider = None
        sensx_slider = None
        sensy_slider = None
        volume_slider = None
        sequences.clear()
        bot_tasks.clear()
        ai_bots.clear()
        application.resume()
        show_main_menu()
    invoke(cleanup, delay=0)

def game_over():
    global pause_button, bot_tasks, ai_bots, sequences, player_alive
    print("Game Over - cleaning up and returning to main menu")
    application.pause()
    if pause_button and hasattr(pause_button, 'enabled') and pause_button.enabled:
        try:
            pause_button.enabled = False
        except Exception as e:
            print(f"Could not disable pause_button: {e}")
    death_msg = Text("Game Over", origin=(0,0), scale=3, color=color.red, parent=camera.ui)
    for t in list(bot_tasks):
        print("Finishing bot task on game over:", t)
        t.finish()
    bot_tasks.clear()
    for b in list(ai_bots):
        print("Destroying AI bot on game over:", b)
        destroy(b)
    ai_bots.clear()
    for item in list(sequences):
        print("Finishing sequence on game over:", item)
        if isinstance(item, Sequence):
            item.finish()
    sequences.clear()

    def cleanup():
        global player, joystick_move, joystick_look, button_jump, button_shoot, pause_button, settings_menu, speed_slider, jump_slider, sensx_slider, sensy_slider, volume_slider, main_menu, menu_background, pause_menu, player_alive
        print("Cleaning up after death")
        # Remove player
        if player:
            destroy(player)
        lst1 = list(scene.entities)
        for e in lst1:
            if e and e != camera:
                if hasattr(e, 'children'):
                    lst2 = list(e.children)
                    for child in lst2:
                        if child:
                            print("Destroying player child entity before quiting to main menu:", child)
                            destroy(child)
                print("Destroying scene entity before quiting to main menu:", e)
                destroy(e)
        for e in camera.ui.children:
            if e != death_msg:
                print("Destroying camera UI entity on game over:", e)
                destroy(e)
        player_alive = False
        joystick_move = None
        joystick_look = None
        button_jump = None
        button_shoot = None
        pause_button = None
        player = None
        settings_menu = None
        speed_slider = None
        jump_slider = None
        sensx_slider = None
        sensy_slider = None
        volume_slider = None
        main_menu = None
        menu_background = None
        pause_menu = None
        Sky.instances.clear()
        # Go back to main menu
        destroy(death_msg)
        show_main_menu()
    application.resume()
    invoke(cleanup, delay=3)  # wait 3 seconds before cleaning up

def setup_game():
    global player, pause_button, joystick_move, joystick_look, button_jump, button_shoot
    print("Setting up game environment")
    application.resume()
    joystick_move = VirtualJoystick(name="joystick_move", position=(-.7,-.3))
    joystick_look = VirtualJoystick(name="joystick_look", position=(.3,-.3))
    button_jump = VirtualButton(name="button_jump", key_name='gamepad a', position=(.6,-.1), color=color.lime)
    button_shoot = VirtualButton(name="button_shoot", key_name='gamepad x', position=(.8,-.2), color=color.red)
    pause_button = Button(name="pause_button", texture='cog', scale=(.08,.08), position=(-0.85,0.45), origin=(-0.5,0.5), parent=camera.ui, color=color.gray, on_click=pause_game)
    player = FirstPersonController(y=2, origin_y=-.5, collider='box')
    print("Player collider: ", player.collider)
    joystick_move.visible = player.use_touch
    joystick_look.visible = player.use_touch
    button_jump.visible = player.use_touch
    button_shoot.visible = player.use_touch
    joystick_move.enabled = True
    joystick_look.enabled = True
    button_jump.enabled = True
    button_shoot.enabled = True
    pause_button.enabled = True
    ground = Entity(name="ground", model='cube', scale=(30,1,30), color=color.rgb(0.9294117647058824,0.7882352941176471,0.6862745098039216), texture='white_cube', texture_scale=(30,30), collider='box')
    house1 = Entity(name="house1", model=preload['house1'], position=(-4,0.5,-4), collider='box')
    house2 = Entity(name="house2", model=preload['house2'], position=(4,0.5,-4), collider='box')
    house3 = Entity(name="house3", model=preload['house3'], position=(-4,0.5,4), collider='box')
    house4 = Entity(name="house4", model=preload['house4'], position=(4,0.5,4), collider='box')
    wall_n1 = Entity(name="wall_n1", model=preload['wall_n1'], position=(-10,0.5,15), collider='box')
    wall_n2 = Entity(name="wall_n2", model=preload['wall_n2'], position=(0,0.5,15), collider='box')
    wall_n3 = Entity(name="wall_n3", model=preload['wall_n3'], position=(10,0.5,15), collider='box')
    wall_s1 = Entity(name="wall_s1", model=preload['wall_s1'], position=(-10,0.5,-15), collider='box')
    wall_s2 = Entity(name="wall_s2", model=preload['wall_s2'], position=(0,0.5,-15), collider='box')
    wall_s3 = Entity(name="wall_s3", model=preload['wall_s3'], position=(10,0.5,-15), collider='box')
    wall_w1 = Entity(name="wall_w1", model=preload['wall_w1'], position=(-15,0.5,-10), rotation=(0,90,0), collider='box')
    wall_w2 = Entity(name="wall_w2", model=preload['wall_w2'], position=(-15,0.5,0), rotation=(0,90,0), collider='box')
    wall_w3 = Entity(name="wall_w3", model=preload['wall_w3'], position=(-15,0.5,10), rotation=(0,90,0), collider='box')
    wall_e1 = Entity(name="wall_e1", model=preload['wall_e1'], position=(15,0.5,-10), rotation=(0,90,0), collider='box')
    wall_e2 = Entity(name="wall_e2", model=preload['wall_e2'], position=(15,0.5,0), rotation=(0,90,0), collider='box')
    wall_e3 = Entity(name="wall_e3", model=preload['wall_e3'], position=(15,0.5,10), rotation=(0,90,0), collider='box')
    north_fw1 = Entity(name="north_fw1", model=preload['north_fw1'], position=(-6,0.5,10), collider='box')
    north_fw2 = Entity(name="north_fw2", model=preload['north_fw2'], position=(0,0.5,11), collider='box')
    north_fw3 = Entity(name="north_fw3", model=preload['north_fw3'], position=(6,0.5,10), collider='box')
    south_fw1 = Entity(name="south_fw1", model=preload['south_fw1'], position=(-6,0.5,-10), collider='box')
    south_fw2 = Entity(name="south_fw2", model=preload['south_fw2'], position=(0,0.5,-11), collider='box')
    south_fw3 = Entity(name="south_fw3", model=preload['south_fw3'], position=(6,0.5,-10), collider='box')
    west_fw1 = Entity(name="west_fw1", model=preload['west_fw1'], position=(-10,0.5,-6), rotation=(0,90,0), collider='box')
    west_fw2 = Entity(name="west_fw2", model=preload['west_fw2'], position=(-11,0.5,0), rotation=(0,90,0), collider='box')
    west_fw3 = Entity(name="west_fw3", model=preload['west_fw3'], position=(-10,0.5,6), rotation=(0,90,0), collider='box')
    east_fw1 = Entity(name="east_fw1", model=preload['east_fw1'], position=(10,0.5,-6), rotation=(0,90,0), collider='box')
    east_fw2 = Entity(name="east_fw2", model=preload['east_fw2'], position=(11,0.5,0), rotation=(0,90,0), collider='box')
    east_fw3 = Entity(name="east_fw3", model=preload['east_fw3'], position=(10,0.5,6), rotation=(0,90,0), collider='box')
    player.health_bar = HealthBar(name="health_bar", max_value=100, value=100, bar_color=color.green.tint(-.2), scale=(.4,.03), position=(-.5,.45), roundness=.5, show_text=True, parent=camera.ui)
    gun = Button(name="gun_pickup", parent=scene, model='assets/pistol.gltf', position=(1,1,1), collider='box', scale=0.1, color=color.gray.tint(-.2))
    gun.on_click = lambda: (setattr(gun, 'parent', camera), setattr(gun, 'position', Vec3(0.2,-0.2,2)), setattr(gun, 'rotation', Vec3(0,0,0)), setattr(gun, 'scale', Vec3(0.3,0.3,0.3)), setattr(player, 'gun', gun))
    gun.on_mouse_enter = gun.on_click
    AIBot(position=(-10,2,10), patrol_area=(4,4), chase_range=20, speed=1)
    AIBot(position=(10,2,-10), patrol_area=(4,4), chase_range=20, speed=1)
    AIBot(position=(-10,2,0), patrol_area=(3,5), chase_range=20, speed=1)
    AIBot(position=(10,2,0), patrol_area=(3,5), chase_range=20, speed=1)
    AIBot(position=(0,2,-12), patrol_area=(5,3), chase_range=20, speed=1)
    button_jump.on_click = player.jump
    button_shoot.on_click = player.shoot
    # Enable hover activation for virtual buttons
    button_jump.on_mouse_enter = button_jump.on_click
    button_shoot.on_mouse_enter = button_shoot.on_click
    pause_button.on_mouse_enter = pause_button.on_click
    Sky()
    print("Game environment setup complete")

def update():
    global settings_menu, speed_slider, jump_slider, sensx_slider, sensy_slider, player
    if mouse.left and isinstance(mouse.hovered_entity, Button):
        return
    if settings_menu and player:
        if speed_slider:
            player.speed = speed_slider.value
        if jump_slider:
            player.jump_height = jump_slider.value
        if sensx_slider:
            player.mouse_sensitivity.x = sensx_slider.value
        if sensy_slider:
            player.mouse_sensitivity.y = sensy_slider.value

show_main_menu()
app.run()
