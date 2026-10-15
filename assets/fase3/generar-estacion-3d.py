import math
import os

import bpy
from mathutils import Vector


ROOT = os.path.dirname(os.path.abspath(__file__))
BLEND_PATH = os.path.join(ROOT, "estacion-ecohuella.blend")
RENDER_PATH = os.path.join(ROOT, "estacion-3d.webp")


def srgb_channel(value):
    value = value / 255.0
    return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4


def rgba(hex_color):
    color = hex_color.lstrip("#")
    return tuple(srgb_channel(int(color[index:index + 2], 16)) for index in (0, 2, 4)) + (1.0,)


def make_material(name, color, metallic=0.0, roughness=0.5, emission=None, emission_strength=0.0):
    material = bpy.data.materials.new(name)
    material.diffuse_color = rgba(color)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    shader = next((node for node in nodes if node.bl_idname == "ShaderNodeBsdfPrincipled"), None)
    output = next((node for node in nodes if node.bl_idname == "ShaderNodeOutputMaterial"), None)
    shader = shader or nodes.new("ShaderNodeBsdfPrincipled")
    output = output or nodes.new("ShaderNodeOutputMaterial")
    if not any(link.from_node == shader and link.to_node == output for link in material.node_tree.links):
        material.node_tree.links.new(shader.outputs["BSDF"], output.inputs["Surface"])
    shader.inputs["Base Color"].default_value = rgba(color)
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    if emission:
        if "Emission Color" in shader.inputs:
            shader.inputs["Emission Color"].default_value = rgba(emission)
            shader.inputs["Emission Strength"].default_value = emission_strength
        elif "Emission" in shader.inputs:
            shader.inputs["Emission"].default_value = rgba(emission)
    return material


def collection(name):
    group = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(group)
    return group


def organize(obj, group):
    for old_group in list(obj.users_collection):
        old_group.objects.unlink(obj)
    group.objects.link(obj)
    return obj


def add_box(name, location, dimensions, material, group, bevel=0.0, rotation=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    if rotation:
        obj.rotation_euler = rotation
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material:
        obj.data.materials.append(material)
    if bevel > 0:
        modifier = obj.modifiers.new("Soft manufactured edges", "BEVEL")
        modifier.width = min(bevel, min(dimensions) * 0.45)
        modifier.segments = 3
        modifier.affect = "EDGES"
        obj.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    return organize(obj, group)


def add_cylinder(name, location, radius, depth, material, group, rotation=(math.pi / 2, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=radius, depth=depth, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    if material:
        obj.data.materials.append(material)
    bevel = obj.modifiers.new("Machined edge", "BEVEL")
    bevel.width = min(0.004, depth * 0.2)
    bevel.segments = 2
    obj.modifiers.new("Weighted normals", "WEIGHTED_NORMAL")
    return organize(obj, group)


def add_uv_sphere(name, location, scale, material, group):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material:
        obj.data.materials.append(material)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    return organize(obj, group)


def add_text(name, text, location, size, material, group, rotation=(math.pi / 2, 0, 0), align="CENTER"):
    bpy.ops.object.text_add(location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.data.body = text
    obj.data.size = size
    obj.data.align_x = align
    obj.data.align_y = "CENTER"
    obj.data.extrude = 0.0005
    obj.data.bevel_depth = 0.00015
    if material:
        obj.data.materials.append(material)
    return organize(obj, group)


def add_area_light(name, location, energy, size, target, group, color=(1.0, 1.0, 1.0)):
    data = bpy.data.lights.new(name, type="AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    data.color = color
    obj = bpy.data.objects.new(name, data)
    group.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()
    return obj


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.collections, bpy.data.materials, bpy.data.cameras, bpy.data.lights, bpy.data.curves, bpy.data.meshes):
        for datablock in list(datablocks):
            if datablock.users == 0:
                datablocks.remove(datablock)


clear_scene()
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.length_unit = "METERS"

body_group = collection("01 | Carcasa y bastidor")
front_group = collection("02 | Interfaz y tres fracciones")
solar_group = collection("03 | Cubierta solar")
studio_group = collection("04 | Cámara, luces y estudio")

graphite = make_material("Grafito satinado | carcasa", "252A2B", metallic=0.48, roughness=0.3)
graphite_panel = make_material("Grafito medio | paneles", "343A3A", metallic=0.34, roughness=0.34)
edge_dark = make_material("Negro profundo | ranuras", "0D1112", metallic=0.2, roughness=0.24)
aluminum = make_material("Aluminio anodizado", "89958E", metallic=0.72, roughness=0.26)
green = make_material("Verde orgánico EcoHuella", "25B83D", metallic=0.12, roughness=0.32)
yellow = make_material("Amarillo reciclable EcoHuella", "E6AE18", metallic=0.14, roughness=0.3)
red = make_material("Rojo no reciclable EcoHuella", "D83C35", metallic=0.12, roughness=0.33)
white = make_material("Blanco cálido | rotulación", "F3F6F2", roughness=0.35)
screen_glass = make_material("Vidrio de pantalla", "071326", metallic=0.26, roughness=0.14)
screen_blue = make_material("Interfaz azul", "174778", metallic=0.16, roughness=0.26)
screen_muted = make_material("Interfaz gris azulada", "7C9CA9", metallic=0.04, roughness=0.5)
solar_blue = make_material("Celdas fotovoltaicas", "10234A", metallic=0.42, roughness=0.22)
led_white = make_material("Luz LED blanca", "EAF9F3", roughness=0.2, emission="C9FFF1", emission_strength=2.2)
led_green = make_material("Indicador verde encendido", "1FE35C", roughness=0.2, emission="21FF68", emission_strength=2.6)
stage = make_material("Fondo verde niebla", "E7F1EB", roughness=0.84)

# Base cabinet: 1450 x 600 x 1550 mm, with a 50 mm canopy bringing total height to 1600 mm.
cabinet = add_box("Carcasa principal | 1450 x 600 x 1495 mm", (0, 0, 0.8025), (1.45, 0.60, 1.495), graphite, body_group, 0.022)
cabinet["reference_dimensions_mm"] = "1450 W x 600 D x 1550 H body; 1600 H including cover"
cabinet["model_status"] = "Esquema conceptual basado en planos entregados"

# Four low feet and the overhanging lid.
for x in (-0.62, 0.62):
    for y in (-0.22, 0.22):
        add_box("Pata niveladora", (x, y, 0.027), (0.115, 0.13, 0.054), edge_dark, body_group, 0.012)
        add_box("Placa de apoyo", (x, y, 0.006), (0.13, 0.145, 0.012), aluminum, body_group, 0.004)

add_box("Cubierta superior | 1500 x 650 x 50 mm", (0, 0, 1.575), (1.50, 0.65, 0.05), graphite, body_group, 0.018)
add_box("Canto frontal verde", (0, -0.329, 1.598), (1.36, 0.012, 0.012), green, front_group, 0.004)

# Front fascia, flush screen bezel and glass.
add_box("Fascia superior", (0, -0.311, 1.356), (1.37, 0.036, 0.355), graphite_panel, front_group, 0.018, rotation=(math.radians(-4), 0, 0))
add_box("Marco de pantalla", (0, -0.339, 1.345), (0.49, 0.025, 0.285), edge_dark, front_group, 0.022, rotation=(math.radians(-4), 0, 0))
add_box("Pantalla TFT", (0, -0.355, 1.345), (0.448, 0.008, 0.239), screen_glass, front_group, 0.017, rotation=(math.radians(-4), 0, 0))
add_text("Marca EcoHuella en pantalla", "ECOHUELLA", (0, -0.361, 1.424), 0.027, white, front_group)
add_text("Mensaje de interfaz", "SEPARA TU RESIDUO", (0, -0.361, 1.389), 0.015, screen_muted, front_group)

for index, (x, material) in enumerate(zip((-0.13, 0.0, 0.13), (green, yellow, red)), 1):
    add_box(f"Indicador de pantalla {index}", (x, -0.362, 1.292), (0.088, 0.004, 0.028), material, front_group, 0.008)
    add_box(f"Barra de acción {index}", (x, -0.362, 1.261), (0.078, 0.004, 0.008), screen_muted, front_group, 0.003)

# Central camera and protected light bars just below the roof.
add_cylinder("Aro exterior de cámara", (0, -0.326, 1.502), 0.038, 0.035, edge_dark, front_group)
add_cylinder("Aro metálico de cámara", (0, -0.347, 1.502), 0.028, 0.012, aluminum, front_group)
add_cylinder("Lente RGB", (0, -0.356, 1.502), 0.021, 0.008, screen_glass, front_group)
add_cylinder("Reflejo de lente", (-0.006, -0.361, 1.51), 0.005, 0.002, screen_muted, front_group)

for side in (-1, 1):
    add_box("Difusor LED superior", (side * 0.265, -0.329, 1.502), (0.31, 0.012, 0.025), led_white, front_group, 0.012)
    for index in range(8):
        x = side * 0.265 + (index - 3.5) * 0.033
        add_uv_sphere("Punto LED", (x, -0.338, 1.502), (0.008, 0.004, 0.008), white, front_group)

add_text("Marca de la estación", "ECOHUELLA  |  IA-BIO", (-0.47, -0.337, 1.475), 0.018, white, front_group, align="LEFT")

# Three independent front doors, each with its own color-coded deposit mouth.
fractions = [
    ("ORGANICO", -0.49, green),
    ("RECICLABLE", 0.0, yellow),
    ("NO RECICLABLE", 0.49, red),
]

for index, (label, x, accent) in enumerate(fractions, 1):
    add_box(f"Panel frontal de bahía {index}", (x, -0.313, 0.651), (0.435, 0.026, 0.965), graphite_panel, front_group, 0.012)
    add_box(f"Marco de boca {label}", (x, -0.333, 0.995), (0.292, 0.022, 0.126), accent, front_group, 0.044)
    add_box(f"Interior oscuro de boca {label}", (x, -0.347, 0.995), (0.262, 0.009, 0.092), edge_dark, front_group, 0.034)
    add_box(f"Guía interior de boca {label}", (x, -0.354, 0.958), (0.19, 0.006, 0.006), aluminum, front_group, 0.002)
    add_uv_sphere(f"Estado de bahía {index}", (x, -0.338, 1.105), (0.014, 0.006, 0.014), led_green, front_group)
    add_text(f"Etiqueta {label}", label, (x, -0.334, 0.58), 0.026 if index < 3 else 0.023, accent, front_group)
    add_box(f"Tirador de servicio {index}", (x, -0.333, 0.225), (0.105, 0.012, 0.012), edge_dark, front_group, 0.005)
    add_box(f"Refuerzo vertical izquierdo {index}", (x - 0.204, -0.331, 0.65), (0.006, 0.008, 0.90), aluminum, front_group, 0.002)
    add_box(f"Refuerzo vertical derecho {index}", (x + 0.204, -0.331, 0.65), (0.006, 0.008, 0.90), aluminum, front_group, 0.002)

# A restrained category marker on each door: leaf, recycling loop and residual bin.
add_uv_sphere("Hoja | orgánico", (-0.49, -0.334, 0.39), (0.055, 0.008, 0.028), green, front_group)
add_box("Nervadura de hoja", (-0.49, -0.344, 0.39), (0.003, 0.003, 0.045), edge_dark, front_group, 0.001, rotation=(0, math.radians(24), 0))
for angle in (0, 120, 240):
    rad = math.radians(angle)
    px = 0.0 + math.cos(rad) * 0.037
    pz = 0.39 + math.sin(rad) * 0.037
    add_box("Segmento del símbolo de reciclaje", (px, -0.338, pz), (0.034, 0.008, 0.008), yellow, front_group, 0.003, rotation=(0, 0, rad))
add_box("Cuerpo de cesto | no reciclable", (0.49, -0.338, 0.39), (0.055, 0.009, 0.051), red, front_group, 0.006)
add_box("Borde de cesto", (0.49, -0.344, 0.421), (0.067, 0.008, 0.008), red, front_group, 0.003)

# Slim side service panel and cooling slots, visible in the three-quarter render.
add_box("Panel lateral de servicio", (0.731, 0.015, 0.77), (0.018, 0.34, 0.88), graphite_panel, body_group, 0.015)
add_box("Junta de puerta lateral", (0.742, 0.015, 0.77), (0.004, 0.30, 0.83), aluminum, body_group, 0.012)
add_box("Superficie de puerta lateral", (0.745, 0.015, 0.77), (0.006, 0.286, 0.816), graphite_panel, body_group, 0.01)
for index in range(7):
    z = 0.93 + index * 0.035
    add_box("Ranura de ventilación lateral", (0.75, 0.015, z), (0.004, 0.12, 0.009), edge_dark, body_group, 0.003)
add_box("Tirador lateral", (0.751, -0.10, 0.62), (0.006, 0.014, 0.09), aluminum, body_group, 0.005)

# Solar module on the overhanging top: dark blue cells and fine silver dividers.
add_box("Marco del panel solar", (0, 0.015, 1.608), (0.91, 0.355, 0.016), aluminum, solar_group, 0.012)
add_box("Laminado fotovoltaico", (0, 0.015, 1.618), (0.875, 0.32, 0.008), solar_blue, solar_group, 0.008)
for index in range(1, 6):
    x = -0.4375 + index * (0.875 / 6)
    add_box("Separador de celda solar", (x, 0.015, 1.623), (0.002, 0.31, 0.002), aluminum, solar_group, 0.0005)
for index in range(1, 3):
    y = -0.145 + index * (0.32 / 3)
    add_box("Línea de celda solar", (0, y + 0.015, 1.623), (0.86, 0.002, 0.002), aluminum, solar_group, 0.0005)

# Ground, studio camera and softboxes.
add_box("Piso de estudio", (0, 0, -0.025), (200, 200, 0.05), stage, studio_group, 0.0)
camera_data = bpy.data.cameras.new("Cámara de producto")
camera = bpy.data.objects.new("Cámara de producto", camera_data)
studio_group.objects.link(camera)
camera.location = (2.55, -4.25, 2.55)
target = Vector((0, 0, 0.82))
camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
camera_data.type = "ORTHO"
camera_data.ortho_scale = 2.70
camera_data.lens = 50
scene.camera = camera

add_area_light("Luz principal suave", (-3.4, -4.2, 5.0), 520, 3.6, (0, 0, 0.8), studio_group, (1.0, 0.91, 0.79))
add_area_light("Relleno frontal", (3.8, -2.3, 3.2), 360, 3.0, (0, 0, 0.85), studio_group, (0.78, 0.89, 1.0))
add_area_light("Luz de contorno", (1.0, 2.6, 4.2), 650, 2.8, (0, 0, 0.9), studio_group, (0.76, 1.0, 0.85))

world = bpy.data.worlds.new("Estudio verde suave") if not bpy.data.worlds else bpy.data.worlds[0]
scene.world = world
world.use_nodes = True
background = next(node for node in world.node_tree.nodes if node.bl_idname == "ShaderNodeBackground")
background.inputs["Color"].default_value = rgba("DDE9E2")
background.inputs["Strength"].default_value = 0.45

scene.render.engine = "BLENDER_EEVEE"
scene.eevee.taa_render_samples = 48
scene.render.resolution_x = 1600
scene.render.resolution_y = 1400
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "WEBP"
scene.render.image_settings.color_mode = "RGB"
scene.render.image_settings.quality = 90
scene.render.filepath = RENDER_PATH
scene.render.film_transparent = False
scene.render.resolution_percentage = 100
scene.view_settings.view_transform = "AgX"
scene.world.color = (0.72, 0.78, 0.74)

readme = bpy.data.texts.new("LEEME - Modelo EcoHuella")
readme.write(
    "ECOHUELLA IA-BIO | ESQUEMA 3D CONCEPTUAL\n"
    "\n"
    "Modelo construido a partir de los planos compartidos y la imagen principal del sitio.\n"
    "Dimensiones de referencia: cuerpo 1450 x 600 x 1550 mm; cubierta 1500 x 650 x 50 mm.\n"
    "La carcasa grafito, los acentos verde/amarillo/rojo y el panel solar siguen la referencia visual.\n"
    "La geometría sirve para comunicar la propuesta; no sustituye planos de fabricación ni validación mecánica.\n"
    "Para regenerar: ejecutar generar-estacion-3d.py con Blender 5.2 o posterior.\n"
)

bpy.ops.object.select_all(action="DESELECT")
bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
scene.render.filepath = RENDER_PATH
bpy.ops.render.render(write_still=True)
print("Saved Blender model:", BLEND_PATH)
print("Saved render:", RENDER_PATH)
