from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

bullet = Entity(model='bullet.gltf', scale=0.1, collider='box', position=(0,2,5), rotation=(0,180,0))

ground = Entity(model='plane', scale=20, texture='white_cube', texture_scale=(20,20), collider='box')

# EditorCamera()
player = FirstPersonController()

app.run()