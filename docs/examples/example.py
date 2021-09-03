import os
import glob
from compas.datastructures import Mesh

from compas_xr import DATA
from compas_xr.datastructures import Scene


scene = Scene(name="IDL")

path = os.path.join(DATA, "idl")
layer_name = "ceiling::projection::canvas"
folder = os.path.join(path, *(layer_name.split("::")))

# node == layer
# scene.add_layer
# layer.add_mesh
ceiling_node = scene.add_node(key="ceiling", parent=None)
projection_node = scene.add_node(key="projection", parent="ceiling")
canvas_node = scene.add_node(key="canvas", parent="projection")

for file in glob.glob('%s/*.obj' % folder):
    mesh = Mesh.from_obj(file)
    node_name = os.path.splitext(os.path.basename(file))[0]
    key = scene.add_node(key=node_name, element=mesh, parent="canvas")

print("=" * 30)

scene.to_gltf(os.path.join(DATA, "canvas.gltf"))
scene.to_usd(os.path.join(DATA, "canvas.usda"))


"""
from compas.files import GLTFContent
from compas.files import GLTFExporter
from compas.files.gltf.data_classes import AnimationData
from compas.files.gltf.data_classes import ChannelData
from compas.files.gltf.data_classes import TargetData
from compas.files.gltf.data_classes import AnimationSamplerData

def get_node_by_name(content, name):
    for key in content.nodes:
        if content.nodes[key].name == name:
            return content.nodes[key]
    return None


#
parent_node = get_node_by_name(content, "projection")
parent_node = content.add_child_to_node(parent_node, "leinwand")

layer_name = "ceiling::projection::leinwand"
folder = os.path.join(path, *(layer_name.split("::")))

files = glob.glob('%s/*.obj' % folder)
for obj in files:
    node_name = os.path.basename(obj)[:-4]
    node = content.add_child_to_node(parent_node, node_name)
    mesh = Mesh.from_obj(obj)
    mesh.quads_to_triangles()
    content.add_mesh_to_node(node, mesh)


animated_node = get_node_by_name(content, "leinwand")

print(animated_node)
print(animated_node.key)
print(animated_node.name)

channels = []
channels.append(ChannelData(0, TargetData("scale", node=animated_node.key)))
channels.append(ChannelData(1, TargetData("translation", node=animated_node.key)))

# R0=(1,0,0,0), R1=(0,1,0,0), R2=(0,0,49.3,-243.8667), R3=(0,0,0,1)

samplers_dict = {}
# scale
input = [0.0, 5.0]
output = [(1.0, 1.0, 1.0),
          (1.0, 1.0, 49.3)]
interpolation = "LINEAR"
samplers_dict[0] = AnimationSamplerData(input, output, interpolation)
# translation
input = [0.0, 5.0]
output = [(0.0, 0.0, 0.0),
          (0.0, 0.0, -243.8667)]
interpolation = "LINEAR"
samplers_dict[1] = AnimationSamplerData(input, output, interpolation)


animation = AnimationData(channels, samplers_dict, name="anim1")

content.animations = {0: animation}

exporter = GLTFExporter(filepath, content, embed_data=True)
exporter.export()

"""