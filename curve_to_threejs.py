import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty
from bpy.types import Operator


def convertCurveToMesh(context, filepath, apply_transform, reverse_vertices, operator):
    type = context.active_object.type
    if type != 'CURVE' and type != 'MESH':
        operator.report({"ERROR"}, "active object must be a Mesh or a Curve")
        return {"CANCELED"}

    bpy.ops.object.duplicate_move()
    if apply_transform == True:
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    if type == "CURVE":
        bpy.ops.object.convert(target="MESH")

    vertices = context.active_object.data.vertices

    bpy.ops.object.delete()

    f = open(filepath, "w", encoding='utf-8')
    f.write("import {Vector3, CatmullRomCurve3} from 'three'\n")
    f.write("const curvePoints = [\n")

    if reverse_vertices:
        for vert in reversed(vertices):
            c = vert.co
            f.write("new Vector3({x}, {z}, {y}),\n".format(x=c[0], y=c[1]*-1, z=c[2]))
    else:
        for vert in vertices:
            c = vert.co
            f.write("new Vector3({x}, {z}, {y}),\n".format(x=c[0], y=c[1]*-1, z=c[2]))

    f.write("];\n")
    f.write("const curve = new CatmullRomCurve3(curvePoints);")
    f.close()

    return {"FINISHED"}


class CurveToThreeOperator(Operator, ExportHelper):
    """Tooltip"""

    bl_idname = "object.curve_to_three"
    bl_label = "Curve to Threejs"

    filename_ext = ".js"

    filter_glob: StringProperty(
        default="*.js",
        options={"HIDDEN"},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    apply_transform: BoolProperty(
            name="apply transforms",
            description="apply transform before exporting vertices",
            default=False
    )

    reverse_path: BoolProperty(
            name="reverse path",
            description="will generate the js array backward",
            default=False
    )

    # language: EnumProperty(
    #     name="language",
    #     description="use js or ts for export",
    #     items=(
    #         ("JS", "Javascript", "use vanilla javascript"),
    #         ("TS", "Typescript", "use typescript"),
    #     ),
    #     default="JS",
    # )

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        return convertCurveToMesh(context, self.filepath, self.apply_transform, self.reverse_path, self)

class CurveToThreejsPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_curve_to_threejs2"
    bl_label = "Curve to Threejs"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Curve To Threejs"

    def draw(self, context):
        layout = self.layout
        button_row = layout.row()
        button_row.operator("object.curve_to_three")


def menu_func(self):
    self.layout.operator(
        CurveToThreeOperator.bl_idname, text=CurveToThreeOperator.bl_label
    )


def register():
    bpy.utils.register_class(CurveToThreeOperator)
    bpy.types.VIEW3D_MT_object.append(menu_func)
    bpy.utils.register_class(CurveToThreejsPanel)


def unregister():
    bpy.utils.unregister_class(CurveToThreeOperator)
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    bpy.utils.unregister_class(CurveToThreejsPanel)


if __name__ == "__main__":
    register()
