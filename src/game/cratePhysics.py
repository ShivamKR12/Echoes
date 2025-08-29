from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

player = FirstPersonController()
player.cursor.visible = True

crate = Entity(model='cube', color=color.brown, collider='box', scale=(1, 1, 1), position=(3, 0.5, 0))

ground = Entity(model='plane', scale=20, texture='white_cube', texture_scale=(20, 20), collider='box')

wall = Entity(model='cube', color=color.gray, scale=(1, 3, 10), position=(6, 1.5, 0), collider='box')

crate_target_position = crate.position

crate_fall_speed = 0
crate_gravity = 50
crate_grounded = False

def update():
    global crate_target_position, crate_fall_speed, crate_grounded

    move_direction = Vec3(0, 0, 0)
    if held_keys['w']:
        move_direction += player.forward
    if held_keys['s']:
        move_direction -= player.forward
    if held_keys['a']:
        move_direction -= player.right
    if held_keys['d']:
        move_direction += player.right

    move_direction = move_direction.normalized()

    distance_to_crate = distance(player.position, crate.position)
    if distance_to_crate < 1.5 and move_direction != Vec3(0, 0, 0):
        push_dir = Vec3(move_direction.x, 0, move_direction.z).normalized()

        to_crate = Vec3(crate.position.x - player.position.x, 0, crate.position.z - player.position.z).normalized()
        if push_dir.dot(to_crate) > 0.5:
            push_distance = 0.3
            hit_info = raycast(crate.world_position, push_dir, distance=1, ignore=(player, crate))
            if not hit_info.hit:
                crate_target_position += push_dir * push_distance

    crate.position = lerp(crate.position, Vec3(crate_target_position.x, crate.position.y, crate_target_position.z), 6 * time.dt)

    down_hit = raycast(crate.world_position, direction=Vec3(0, -1, 0), distance=5, ignore=(crate,))

    if down_hit.hit:
        if down_hit.distance > 0.6:
            crate_fall_speed += crate_gravity * time.dt
            crate.y -= crate_fall_speed * time.dt
            crate_grounded = False
        else:
            crate.y = down_hit.world_point.y + 0.5
            crate_fall_speed = 0
            crate_grounded = True
    else:
        crate_fall_speed += crate_gravity * time.dt
        crate.y -= crate_fall_speed * time.dt

app.run()
