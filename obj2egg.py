"""
Modified from: https://github.com/treeform/obj2egg.
Licensed under WTFPL (http://sam.zoy.org/wtfpl/).
Usage:
    python3 obj2egg.py [n##][b][t][s] filename1.obj ...
        -n regenerate normals with # degree smoothing
            exaple -n30  (normals at less 30 degrees will be smoothed)
        -b make binarmals
        -t make tangents
        -s show in pview
Original forum discussion: http://panda3d.org/phpbb2/viewtopic.php?t=3378.
"""

import getopt
import os, sys

from panda3d.core import Filename, GlobPattern, Point2D, Point3D, Vec3D, Vec4
from panda3d.egg import (
    EggData,
    EggGroup,
    EggLine,
    EggMaterial,
    EggPolygon,
    EggTexture,
    EggVertex,
    EggVertexPool,
)


def floats(float_list):
    """coerce a list of strings that represent floats into a list of floats"""
    return [float(number) for number in float_list]


def ints(int_list):
    """coerce a list of strings that represent integers into a list of integers"""
    return [int(number) for number in int_list]


class ObjMaterial:
    """a wavefront material"""

    def __init__(self):
        self.filename = None
        self.name = "default"
        self.eggdiffusetexture = None
        self.eggmaterial = None
        self.attrib = {
            "Ns": 100.0,
            "d": 1.0,
            "illum": 2,
            "Kd": [1.0, 0.0, 1.0],
            "Ka": [0.0, 0.0, 0.0],
            "Ks": [0.0, 0.0, 0.0],
            "Ke": [0.0, 0.0, 0.0],
        }

    def put(self, key, value):
        self.attrib[key] = value
        return self

    def get(self, key):
        return self.attrib.get(key, None)

    def has_key(self, key):
        return key in self.attrib

    def isTextured(self):
        # for k in ("map_Kd", "map_Bump", "map_Ks"):    <-- NOT YET
        return "map_Kd" in self.attrib

    def getEggTexture(self):
        if self.eggdiffusetexture:
            return self.eggdiffusetexture

        if not self.isTextured():
            return None

        m = EggTexture(self.name + "_diffuse", self.get("map_Kd"))
        m.setFormat(EggTexture.FRgb)
        m.setMagfilter(EggTexture.FTLinearMipmapLinear)
        m.setMinfilter(EggTexture.FTLinearMipmapLinear)
        m.setWrapU(EggTexture.WMRepeat)
        m.setWrapV(EggTexture.WMRepeat)
        self.eggdiffusetexture = m
        return self.eggdiffusetexture

    def getEggMaterial(self):
        if self.eggmaterial:
            return self.eggmaterial

        m = EggMaterial(self.name + "_mat")
        # XXX TODO: add support for specular, and obey illum setting
        # XXX as best as we can
        rgb = self.get("Kd")
        if rgb is not None:
            m.setDiff(Vec4(rgb[0], rgb[1], rgb[2], 1.0))

        rgb = self.get("Ka")
        if rgb is not None:
            m.setAmb(Vec4(rgb[0], rgb[1], rgb[2], 1.0))

        rgb = self.get("Ks")
        if rgb is not None:
            m.setSpec(Vec4(rgb[0], rgb[1], rgb[2], 1.0))

        ns = self.get("Ns")
        if ns is not None:
            m.setShininess(ns)

        self.eggmaterial = m
        return self.eggmaterial


class MtlFile:
    """an object representing all Wavefront materials in a .mtl file"""

    def __init__(self, filename=None):
        self.filename = None
        self.materials = {}
        self.comments = {}
        if filename is not None:
            self.read(filename)

    def read(self, filename):
        self.filename = filename
        self.materials = {}
        self.comments = {}

        light_scalars = {"Ns", "d", "Tr"}
        k_colors = {"Kd", "Ka", "Ks", "Ke"}
        tex_maps = {"map_Kd", "map_Bump", "map_Ks", "map_bump", "bump"}
        file = open(filename)
        linenumber = 0
        mat = None
        for line in file.readlines():
            line = line.strip()
            linenumber += 1
            if not line:
                continue

            if line[0] == "#":
                self.comments[linenumber] = line
                continue

            tokens = line.split()
            if not tokens:
                continue

            if tokens[0] == "newmtl":
                mat = ObjMaterial()
                mat.filename = filename
                mat.name = tokens[1]
                self.materials[mat.name] = mat
                continue

            if tokens[0] in light_scalars:
                # "d factor" - specifies the dissovle for the current material,
                #              1.0 is full opaque
                # "Ns exponent" - specifies the specular exponent.  A high exponent
                #               results in a tight, concentrated highlight.
                mat.put(tokens[0], float(tokens[1]))
                continue

            if tokens[0] == "illum":
                # according to http://www.fileformat.info/format/material/
                # 0 = Color on and Ambient off
                # 1 = Color on and Ambient on
                # 2 = Highlight on
                # 3 = Reflection on and Ray trace on
                # 4 = Transparency: Glass on, Reflection: Ray trace on
                # 5 = Reflection: Fesnel on and Ray trace on
                # 6 = Transparency: Refraction on, Reflection: Fresnel off and Ray trace on
                # 7 = Transparency: Refraction on, Refelction: Fresnel on and Ray Trace on
                # 8 = Reflection on and Ray trace off
                # 9 = Transparency: Glass on, Reflection: Ray trace off
                # 10 = Casts shadows onto invisible surfaces
                mat.put(tokens[0], int(tokens[1]))
                continue

            if tokens[0] in k_colors:
                mat.put(tokens[0], floats(tokens[1:]))
                continue

            if tokens[0] in tex_maps:
                # Ultimate Unwrap 3D Pro emits these:
                # map_Kd == diffuse
                # map_Bump == bump
                # map_Ks == specular
                mat.put(tokens[0], pathify(tokens[1]))
                continue

            if tokens[0] == "Ni":
                # blender's .obj exporter can emit this "Ni 1.000000"
                mat.put(tokens[0], float(tokens[1]))
                continue

        file.close()


class ObjFile:
    """a representation of a wavefront .obj file"""

    def __init__(self, filename=None):
        self.filename = None
        self.objects = ["defaultobject"]
        self.groups = ["defaultgroup"]
        self.points = []
        self.uvs = []
        self.normals = []
        self.faces = []
        self.polylines = []
        self.matlibs = []
        self.materialsbyname = {}
        self.comments = {}
        self.currentobject = self.objects[0]
        self.currentgroup = self.groups[0]
        self.currentmaterial = None
        if filename is not None:
            self.read(filename)

    def read(self, filename):
        self.filename = filename
        self.objects = ["defaultobject"]
        self.groups = ["defaultgroup"]
        self.points = []
        self.uvs = []
        self.normals = []
        self.faces = []
        self.polylines = []
        self.matlibs = []
        self.materialsbyname = {}
        self.comments = {}
        self.currentobject = self.objects[0]
        self.currentgroup = self.groups[0]
        self.currentmaterial = None
        file = open(filename)
        linenumber = 0
        for line in file.readlines():
            line = line.strip()
            linenumber += 1
            if not line:
                continue

            if line[0] == "#":
                self.comments[linenumber] = line
                continue

            tokens = line.split()
            if not tokens:
                continue

            if tokens[0] == "mtllib":
                mtllib = MtlFile(tokens[1])
                self.matlibs.append(mtllib)
                self.indexmaterials(mtllib)
                continue

            if tokens[0] == "g":
                self.__newgroup("".join(tokens[1:]))
                continue

            if tokens[0] == "o":
                self.__newobject("".join(tokens[1:]))
                continue

            if tokens[0] == "usemtl":
                self.__usematerial(tokens[1])
                continue

            if tokens[0] == "v":
                self.__newv(tokens[1:])
                continue

            if tokens[0] == "vn":
                self.__newnormal(tokens[1:])
                continue

            if tokens[0] == "vt":
                self.__newuv(tokens[1:])
                continue

            if tokens[0] == "f":
                self.__newface(tokens[1:])
                continue

            if tokens[0] == "s":
                # apparently, this enables/disables smoothing
                continue

            if tokens[0] == "l":
                self.__newpolyline(tokens[1:])
                continue

        file.close()

    def __vertlist(self, lst):
        res = []
        for vert in lst:
            vinfo = vert.split("/")
            vlen = len(vinfo)
            vertex = {"v": None, "vt": None, "vn": None}
            if vlen == 1:
                vertex["v"] = int(vinfo[0])

            elif vlen == 2:
                if vinfo[0] != "":
                    vertex["v"] = int(vinfo[0])

                if vinfo[1] != "":
                    vertex["vt"] = int(vinfo[1])

            elif vlen == 3:
                if vinfo[0] != "":
                    vertex["v"] = int(vinfo[0])

                if vinfo[1] != "":
                    vertex["vt"] = int(vinfo[1])

                if vinfo[2] != "":
                    vertex["vn"] = int(vinfo[2])

            else:
                raise ValueError("Face has more than three vertices")

            res.append(vertex)

        return res

    def __enclose(self, lst):
        mdata = (self.currentobject, self.currentgroup, self.currentmaterial)
        return (lst, mdata)

    def __newpolyline(self, l):
        polyline = self.__vertlist(l)
        self.polylines.append(self.__enclose(polyline))

    def __newface(self, f):
        face = self.__vertlist(f)
        self.faces.append(self.__enclose(face))

    def __newuv(self, uv):
        self.uvs.append(floats(uv))

    def __newnormal(self, normal):
        self.normals.append(floats(normal))

    def __newv(self, v):
        # capture the current metadata with vertices
        vdata = floats(v)
        mdata = (self.currentobject, self.currentgroup, self.currentmaterial)
        vinfo = (vdata, mdata)
        self.points.append(vinfo)

    def indexmaterials(self, mtllib):
        # traverse the materials defined in mtllib, indexing
        # them by name.
        for mname in mtllib.materials:
            mobj = mtllib.materials[mname]
            self.materialsbyname[mobj.name] = mobj

    def __closeobject(self):
        self.currentobject = "defaultobject"

    def __newobject(self, object):
        self.__closeobject()
        self.currentobject = object
        self.objects.append(object)

    def __closegroup(self):
        self.currentgroup = "defaultgroup"

    def __newgroup(self, group):
        self.__closegroup()
        self.currentgroup = group
        self.groups.append(group)

    def __usematerial(self, material):
        if material in self.materialsbyname:
            self.currentmaterial = material
        else:
            print(f"{material} not in known materials.")

    def __itemsby(self, itemlist, objname, groupname):
        res = []
        for item in itemlist:
            (vlist, mdata) = item
            (wobj, wgrp, wmat) = mdata
            if (wobj == objname) and (wgrp == groupname):
                res.append(item)

        return res

    def __facesby(self, objname, groupname):
        return self.__itemsby(self.faces, objname, groupname)

    def __linesby(self, objname, groupname):
        return self.__itemsby(self.polylines, objname, groupname)

    def __eggifyverts(self, eprim, evpool, vlist):
        for vertex in vlist:
            ixyz = vertex["v"]
            vinfo = self.points[ixyz - 1]
            (vxyz, vmeta) = vinfo
            ev = EggVertex()
            ev.setPos(Point3D(vxyz[0], vxyz[1], vxyz[2]))
            iuv = vertex["vt"]
            if iuv is not None:
                vuv = self.uvs[iuv - 1]
                ev.setUv(Point2D(vuv[0], vuv[1]))

            inormal = vertex["vn"]
            if inormal is not None:
                vn = self.normals[inormal - 1]
                ev.setNormal(Vec3D(vn[0], vn[1], vn[2]))

            evpool.addVertex(ev)
            eprim.addVertex(ev)

    def __eggifymats(self, eprim, wmat):
        if wmat in self.materialsbyname:
            mtl = self.materialsbyname[wmat]
            if mtl.isTextured():
                eprim.setTexture(mtl.getEggTexture())
                # NOTE: it looks like you almost always want to setMaterial()
                #       for textured polys.... [continued below...]
                eprim.setMaterial(mtl.getEggMaterial())

            rgb = mtl.get("Kd")
            if rgb is not None:
                # ... and some untextured .obj's store the color of the
                # material # in the Kd settings...
                eprim.setColor(Vec4(rgb[0], rgb[1], rgb[2], 1.0))

            # [continued...] but you may *not* always want to assign
            # materials to untextured polys...  hmmmm.

        return self

    def __facestoegg(self, egg, objname, groupname):
        selectedfaces = self.__facesby(objname, groupname)
        if len(selectedfaces) == 0:
            return

        eobj = EggGroup(objname)
        egg.addChild(eobj)
        egrp = EggGroup(groupname)
        eobj.addChild(egrp)
        evpool = EggVertexPool(groupname)
        egrp.addChild(evpool)
        for face in selectedfaces:
            (vlist, mdata) = face
            (wobj, wgrp, wmat) = mdata
            epoly = EggPolygon()
            egrp.addChild(epoly)
            self.__eggifymats(epoly, wmat)
            self.__eggifyverts(epoly, evpool, vlist)

    def __polylinestoegg(self, egg, objname, groupname):
        selectedlines = self.__linesby(objname, groupname)
        if len(selectedlines) == 0:
            return

        eobj = EggGroup(objname)
        egg.addChild(eobj)
        egrp = EggGroup(groupname)
        eobj.addChild(egrp)
        evpool = EggVertexPool(groupname)
        egrp.addChild(evpool)
        for line in selectedlines:
            (vlist, mdata) = line
            (wobj, wgrp, wmat) = mdata
            eline = EggLine()
            egrp.addChild(eline)
            self.__eggifymats(eline, wmat)
            self.__eggifyverts(eline, evpool, vlist)

    def toEgg(self):
        # make a new egg
        egg = EggData()
        # convert polygon faces
        if len(self.faces) > 0:
            for objname in self.objects:
                for groupname in self.groups:
                    self.__facestoegg(egg, objname, groupname)

        # convert polylines
        if len(self.polylines) > 0:
            for objname in self.objects:
                for groupname in self.groups:
                    self.__polylinestoegg(egg, objname, groupname)

        return egg


def pathify(path):
    if os.path.isfile(path):
        return path

    # if it was written on win32, it may have \'s in it, and
    # also a full rather than relative pathname (Hexagon does this... ick)
    path = path.lower()
    path = path.replace("\\", "/")
    (h, t) = os.path.split(path)
    return t


def main(argv=None):
    if argv is None:
        argv = sys.argv

    try:
        opts, args = getopt.getopt(
            argv[1:], "hn:bs", ["help", "normals", "binormals", "show"]
        )
    except getopt.error as msg:
        print(msg)
        print(__doc__)

    show = False
    for (o, a) in opts:
        if o in ("-h", "--help"):
            print(__doc__)
        elif o in ("-s", "--show"):
            show = True

    for infile in args:
        obj = ObjFile(infile)
        egg = obj.toEgg()
        (f, e) = os.path.splitext(infile)
        outfile = f + ".egg"
        for o, a in opts:
            if o in ("-n", "--normals"):
                egg.recomputeVertexNormals(float(a))
            elif o in ("-b", "--binormals"):
                egg.recomputeTangentBinormal(GlobPattern(""))

        egg.removeUnusedVertices(GlobPattern(""))
        if True:
            egg.triangulatePolygons(EggData.TConvex & EggData.TPolygon)

        if True:
            egg.recomputePolygonNormals()

        egg.writeEgg(Filename(outfile))
        if show:
            os.system("pview " + outfile)


if __name__ == "__main__":
    main()
