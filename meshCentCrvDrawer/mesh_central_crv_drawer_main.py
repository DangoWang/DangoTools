#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: Dango Wang
# time : 2019/3/19

# necessary modules
import sys
import os
import logging
import numpy
# maya modules
import maya.cmds as mc
import pymel.core as pm
import maya.mel as mel
# other
import loadUiType
# pyside
try:
    from PySide2 import QtWidgets, QtCore
    from shiboken2 import wrapInstance
except ImportError:
    from PySide import QtGui as QtWidgets
    from PySide import QtCore
    from shiboken import wrapInstance


filepath = str(os.path.split(os.path.realpath(__file__))[0])
form_class, base_class = loadUiType.loadUiType(filepath+'\\mesh_central_crv_drawer_ui.ui')


def undoable(function):
    """A decorator that will make commands undoable in maya"""
    def decoratorCode(*args, **kwargs):
        mc.undoInfo(openChunk=True)
        functionReturn = None
        try:
            functionReturn = function(*args, **kwargs)
        except:
            print sys.exc_info()[1]

        finally:
            mc.undoInfo(closeChunk=True)
            return functionReturn
    return decoratorCode


class MeshCentrCrvDrawer(base_class, form_class):
    def __init__(self):
        super(MeshCentrCrvDrawer, self).__init__(parent=loadUiType.getMayaWindow())
        self.setupUi(self)

    @QtCore.Slot()
    def on_input_poly_pb_clicked(self):
        selected = mc.ls(sl=1)
        if not selected:
            logging.error(u'请先选择物体！')
            return False
        self.input_poly_le.setText(selected[0])
        return selected[0]

    @QtCore.Slot()
    def on_face_count_pb_clicked(self):
        selected = pm.ls(sl=1)
        if not selected:
            logging.error(u'请先选择环边！')
            return False
        if not pm.nodeType(selected[0]) == 'mesh':
            logging.error(u'选择类型错误！')
            return False
        if len(selected) > 2:
            self.face_count_sb.setValue(len(selected)+1)
        elif ':' in selected[0]:
            min_ = int(selected[0].split("[")[-1].split(":")[0])
            max_ = int(selected[0].split("]")[0].split(":")[-1])
            self.face_count_sb.setValue(max_-min_+1)
        return True

    @property
    def mesh_name(self):
        return self.input_poly_le.text()

    @property
    def face_count(self):
        return self.face_count_sb.value()

    @property
    def crv_step(self):
        return self.crv_step_sb.value()

    @property
    def rebuild_crv_num(self):
        return self.rebuild_crv_sb.value()

    @QtCore.Slot(name='on_rebuild_crv_pb_clicked')
    @undoable
    def on_rebuild_crv_pb_clicked(self):
        selected = mc.ls(sl=1)
        if not selected:
            logging.error(u'请选择曲线！')
            return False
        mc.rebuildCurve(selected[0], rpo=1, ch=1, end=1, kr=0, kcp=0, kt=0, d=3, tol=0.01, rt=0, s=self.rebuild_crv_num)
        return True

    @QtCore.Slot(name='on_reverse_pb_clicked')
    @undoable
    def on_reverse_pb_clicked(self):
        selected = mc.ls(sl=1)
        if not selected:
            logging.error(u'请选择曲线！')
            return False
        mc.reverseCurve(selected[0], ch=1, rpo=1)
        return True

    @QtCore.Slot(name='on_draw_crv_pb_clicked')
    @undoable
    def on_draw_crv_pb_clicked(self):
        print 'starting drawing...'
        mesh_pm_node = pm.PyNode(self.mesh_name)
        mesh_pm_shape = mesh_pm_node.getShape()
        all_points = mesh_pm_shape.getPoints(space='world')
        i = 0
        final_pos = []
        while True:
            each_span_points = all_points[i:i+self.face_count]
            points_array = numpy.array(each_span_points)
            pos_list = points_array.mean(0).tolist()
            try:
                if len(pos_list) == 3:
                    final_pos.append(pos_list)
            except:
                pass
            if i >= len(all_points):
                break
            i += self.face_count * self.crv_step
        crv = pm.curve(d=3, p=final_pos)
        pm.select(crv, r=1)
        mel.eval('CenterPivot')
        return crv

