import random

from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFileData, ConfigVariableManager, Shader


class ELF_RUNTIME(ShowBase):
    def __init__(self):
        super().__init__()

    def update(self, task):
        print("hello!")
        return task.cont


ELF_SHOW_BASE: ELF_RUNTIME = None
ELF_OBJECTS = {}
ELF_SHADERS = {}


def elf_enable_mouse():
    ELF_SHOW_BASE.enableMouse()


def elf_init_show_base():
    global ELF_SHOW_BASE
    elf_win_title('ELF')
    elf_use_assimp()
    ELF_SHOW_BASE = ELF_RUNTIME()
    ELF_SHOW_BASE.disableMouse()


def elf_win_size(w, h):
    if ELF_SHOW_BASE != None:
        print("ELF: failed to change win-size because this function is special, and needs to be called before "
              "'elf_init_show_base'")
    loadPrcFileData('', 'win-size ' + str(w) + ' ' + str(h))


def elf_win_title(title):
    if ELF_SHOW_BASE != None:
        print("ELF: failed to change window-title because this function is special, and needs to be called before "
              "'elf_init_show_base'")
    loadPrcFileData('', 'window-title ' + title)


def elf_show_fps(fps):
    if ELF_SHOW_BASE != None:
        print("ELF: failed to change show-frame-rate-meter because this function is special, and needs to be called "
              "before "
              "'elf_init_show_base'")
    loadPrcFileData('', 'show-frame-rate-meter ' + str(fps))


def elf_show_scene_graph_analyzer_meter(analyzer):
    if ELF_SHOW_BASE != None:
        print(
            "ELF: failed to change show-scene-graph-analyzer-meter because this function is special, and needs to be called "
            "before "
            "'elf_init_show_base'")
    loadPrcFileData('', 'show-scene-graph-analyzer-meter ' + str(int(analyzer)))


def elf_use_assimp():
    if ELF_SHOW_BASE != None:
        print("ELF: failed to change load-file-type because this function is special, and needs to be called "
              "before "
              "'elf_init_show_base'")
    loadPrcFileData('', 'load-file-type p3assimp')


def elf_parse_glsl(vertex, fragment):
    shader = Shader.load(Shader.SL_GLSL, vertex=vertex, fragment=fragment)
    id = elf_gen_id()
    ELF_SHADERS[id] = shader
    return id


def elf_attach_shader_to_model(model_id, shader_id):
    ELF_OBJECTS[model_id].setShader(ELF_SHADERS[shader_id])
    return model_id


def elf_set_in_glsl(model_id, uniform_name, value):
    ELF_OBJECTS[model_id].setShaderInput(uniform_name, value)
    return model_id


def elf_debug_config():
    ConfigVariableManager.getGlobalPtr().listVariables()


def elf_gen_id():
    return random.randint(0, 1000000000000000000)


def elf_loader():
    return ELF_SHOW_BASE.loader


def elf_draw(path, position=(0, 0, 0), scale=(1.0, 1.0, 1.0), rotation=(0, 0, 0)):
    id = elf_gen_id()
    ELF_OBJECTS[id] = elf_loader().loadModel(path)
    ELF_OBJECTS[id].setPos(position[0], position[1], position[2])
    ELF_OBJECTS[id].setScale(scale[0], scale[1], scale[2])
    ELF_OBJECTS[id].setHpr(rotation[0], rotation[1], rotation[2])
    ELF_OBJECTS[id].reparentTo(ELF_SHOW_BASE.render)
    return id


def elf_wireframe(wireframe):
    ELF_SHOW_BASE.render.setRenderModeWireframe(wireframe)


def elf_set_update(function):
    ELF_SHOW_BASE.taskMgr.add(function, "update")


def elf_win_w():
    return ELF_SHOW_BASE.win.getXSize()


def elf_win_h():
    return ELF_SHOW_BASE.win.getYSize()


def elf_add_task(task, task_name):
    ELF_SHOW_BASE.taskMgr.add(task, task_name)


def elf_render_window():
    ELF_SHOW_BASE.run()
