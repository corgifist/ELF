import random

from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFileData, ConfigVariableManager

ELF_SHOW_BASE = None
ELF_MODELS = {}


def elf_init_show_base():
    global ELF_SHOW_BASE
    elf_win_title('ELF')
    elf_use_assimp()
    ELF_SHOW_BASE = ShowBase()
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
        print("ELF: failed to change show-scene-graph-analyzer-meter because this function is special, and needs to be called "
              "before "
              "'elf_init_show_base'")
    loadPrcFileData('', 'show-scene-graph-analyzer-meter ' + str(int(analyzer)))


def elf_use_assimp():
    if ELF_SHOW_BASE != None:
        print("ELF: failed to change load-file-type because this function is special, and needs to be called "
              "before "
              "'elf_init_show_base'")
    loadPrcFileData('', 'load-file-type p3assimp')


def elf_debug_config():
    ConfigVariableManager.getGlobalPtr().listVariables()


def elf_gen_id():
    return random.randint(0, 1000000000000000000)


def elf_loader():
    return ELF_SHOW_BASE.loader


def elf_draw(path, coords=(0, 0, 0), scale=(1.0, 1.0, 1.0)):
    id = elf_gen_id()
    ELF_MODELS[id] = elf_loader().loadModel(path)
    ELF_MODELS[id].setPos(coords[0], coords[1], coords[2])
    ELF_MODELS[id].reparentTo(ELF_SHOW_BASE.render)
    ELF_MODELS[id].setScale(scale)
    return id


def elf_render_window():
    ELF_SHOW_BASE.run()
