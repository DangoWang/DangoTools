#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: Dango Wang
# time : 2019/3/1
from pymel.core import PyNode

__author__ = "dango wang"
__license__ = "MIT"
__doc__ = 'this script is to generate nightmare\'s motion path with the given curve'
import os
import sys
import logging
import loadUiType
import maya.cmds as mc
import pymel.core as pm
import maya.mel as mel
from collections import OrderedDict
import re
import math
import maya_curves
reload(maya_curves)
try:
    from PySide2 import QtWidgets, QtCore
except ImportError:
    from PySide import QtCore
    import PySide.QtGui as QtWidgets

file_path = str(os.path.split(os.path.realpath(__file__))[0])
form_class, base_class = loadUiType.loadUiType(file_path + '\curve_rigging.ui')


def undoable(function):
    '''A decorator that will make commands undoable in maya'''
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


class MoPathCvp(object):
    def __init__(self,
                 crvstr,
                 index,
                 span_points_num,
                 is_start=False,
                 is_end=False,
                 ):
        self.return_dict = self.get_span_points(crvstr=crvstr, index=index,
                                                span_points_num=span_points_num, is_start=is_start, is_end=is_end)

    def get_span_points(self, crvstr, index, span_points_num, is_start, is_end):
        """
        :param crvstr: str
        :param index:
        :param span_points_num:
        :param is_start:
        :param is_end:
        :return: {py_cv_node:{0:[], 1:[], 2:[],...}...}
        """
        crvstr_cv_format = crvstr+".cv[{}]"
        return_dict = dict()
        if is_start:
            for i in xrange(span_points_num):
                # start_point = crvstr_cv_format.format(index)
                if mc.objExists(crvstr_cv_format.format(str(index+i))):
                    return_dict[i] = [crvstr_cv_format.format(str(index+i))]
            return {crvstr_cv_format.format(str(index)): return_dict}
        if is_end:
            for i in xrange(span_points_num):
                # start_point = crvstr_cv_format.format(index)
                if mc.objExists(crvstr_cv_format.format(str(index-i))):
                    return_dict[i] = [crvstr_cv_format.format(str(index-i))]
            return {crvstr_cv_format.format(str(index)): return_dict}
        for each in xrange(span_points_num):
            return_dict[each] = [crvstr_cv_format.format(str(index - each)),
                                 crvstr_cv_format.format(str(index + each))]
            if each == 0:
                return_dict[each] = [crvstr_cv_format.format(str(index - each))]
            # for point in return_dict[each]:
            #     if not mc.objExists(point):
            #         return_dict[each].pop(point)
        return {crvstr_cv_format.format(str(index)): return_dict}


class MoPathCrv(object):
    def __init__(self,
                 pmcrvnode,
                 spans,
                 ):
        self.point_num = self.get_points_num(pmcrvnode)
        self.points = self.all_points(pmcrvnode)
        self.crv_name = pmcrvnode.name()
        # self.point = self.get_cv(pmcrvnode, index=index, space=space)
        self.points_in_spans = self.get_span_points(pmcrvnode, spans=spans)
        self.points_with_ends = self.get_points_with_both_ends()
        # self._each_span_points_num = int()

    @staticmethod
    def get_points_num(pmcvnode):
        return pmcvnode.numCVs()

    @staticmethod
    def all_points(pmcvnode):
        return pmcvnode.cv

    def get_points_with_both_ends(self):
        points_ends = dict()
        for i in xrange(len(self.points_in_spans)):
            # print i
            the_one_in_dict = list(self.points_in_spans)[i]
            print the_one_in_dict
            try:
                except_points = [the_one_in_dict, list(self.points_in_spans)[i+1]]
            except IndexError:
                continue
            zero_weight_points = [self.crv_name+'_crv_jnt_'+re.findall("\d+", each)[-1]
                                  for each in self.points_in_spans.keys() if each not in except_points]
            each_span_points = list()
            # print type(self.points_in_spans[the_one_in_dict])
            for k, v in self.points_in_spans[the_one_in_dict].iteritems():
                each_span_points.append(v[-1])
            mc.select(each_span_points, r=True)
            each_span_point_str = mc.ls(sl=True)[0]
            points_ends[each_span_point_str] = zero_weight_points
        return points_ends

    def get_span_points(self, pmcvnode, spans):
        """
        get each span points
        :param pmcvnode: nurbsCurve
        :param spans: spans
        :return: [{0:[centerP], 1:[left1,right1]...},{}...]
        """
        span_points = OrderedDict()  # return
        all_cvs = self.all_points(pmcvnode)
        cv_start_index = int(all_cvs.name().split("[")[-1].split(":")[0])
        cv_end_index = int(all_cvs.name().split("]")[0].split(":")[-1])
        num_cvs = self.get_points_num(pmcvnode)
        each_span_points_num = int(num_cvs / spans)
        # self._each_span_points_num = each_span_points_num
        start_cv_point = MoPathCvp(pmcvnode.name(), cv_start_index, each_span_points_num, is_start=True)
        end_cv_point = MoPathCvp(pmcvnode.name(), cv_end_index, each_span_points_num, is_end=True)
        span_points.update(start_cv_point.return_dict)
        index = cv_start_index
        while index < cv_end_index-each_span_points_num:
            next_index = index + each_span_points_num
            next_cv_point = MoPathCvp(pmcvnode.name(), next_index, each_span_points_num)
            span_points.update(next_cv_point.return_dict)
            index += each_span_points_num
        span_points.update(end_cv_point.return_dict)
        return span_points


class MakeCrvControls(MoPathCrv):
    def __init__(self, pmcrvnode, spans):
        super(MakeCrvControls, self).__init__(pmcrvnode, spans)
        self.spans = spans
        self._crv_node = pmcrvnode
        self._crv_node_name = pmcrvnode.name()
        self._joints_list = list()
        self._skin_cluster = str()
        self._weight_list = list()

    def _get_jnts_pos(self):
        all_pos = {}
        for each_point in self.points_in_spans.keys():
            # print each_point.name()
            point_number = re.findall("\d+", each_point)[-1]
            # print point_number
            point_pos = pm.PyNode(each_point).getPosition(space='world')
            all_pos[point_number] = point_pos
        return all_pos

    def _create_jnt(self, point_num, pos):
        jnt_name = self._crv_node_name + '_crv_jnt_' + point_num
        return mc.joint(name=jnt_name, p=pos)

    def create_jnts(self):
        jnts_grp = mc.createNode('transform', name=self._crv_node_name + '_crv_jnt_grp')
        all_joints_dict = self._get_jnts_pos()
        for k, v in all_joints_dict.items():
            jnt_name = self._create_jnt(k, v)
            self._joints_list.append(jnt_name)
            mc.Unparent(jnt_name)
            mc.parent(jnt_name, jnts_grp)
        print 'creating jnts ...'
        return jnts_grp

    def bind_skin(self):
        skin_cluster = mc.skinCluster(self._joints_list, self._crv_node_name)[0]
        self._skin_cluster = skin_cluster
        print 'binding skin ...'
        return skin_cluster

    def wipe_weights(self):
        skin_cluster = self._skin_cluster
        if self.points_with_ends:
            for k, v in self.points_with_ends.items():
                transform_value = [(each, 0) for each in v]  # k是点
                mc.skinPercent(skin_cluster, k, transformValue=transform_value)
        print 'wiping weights ...'
        return True

    def draw_weights(self, weight, max_weight):
        each_span_points_num = self.point_num / float(self.spans)
        # print each_span_points_num
        for k, v in self.points_in_spans.iteritems():
            jnt_name = self._crv_node_name + '_crv_jnt_' + re.findall("\d+", k)[-1]
            for i in xrange(int(each_span_points_num)):
                for each in v[i]:
                    j = i
                    span_points_num = each_span_points_num
                    x = float(j)/span_points_num
                    t = abs(x - 0.5)
                    y1 = float(-2*t+1)
                    y2 = float((2*t-1)**max_weight)
                    if x <= 0.5:
                        draw_weight = 1-((y1-y2)/(weight+1) + y2)/2
                    elif x > 0.5:
                        draw_weight = ((y1 - y2) / (weight + 1) + y2) / 2
                    # if draw_mode == "x":
                    #     draw_weight = 1 - (j / span_points_num)
                    # elif draw_mode == "xx":
                    #     draw_weight = 1 - ((j * j) / (span_points_num * span_points_num))
                    # elif draw_mode == 'cosx':
                    #     j = i * math.pi / (2*span_points_num)  # j ∈ [0, π/2]
                    #     draw_weight = (math.cos(2*j)+1) / 2
                    transform_value = [(jnt_name, draw_weight)]
                    # print each, transform_value
                    mc.skinPercent(self._skin_cluster, each, transformValue=transform_value)
        print 'drawing weights ...'

    def build_controls(self):
        control_grps = list()
        for each_jnt in self._joints_list:
            control_name = each_jnt.replace('jnt', 'ctrl')
            jnt_pos = pm.getAttr(each_jnt+'.t')
            mel.eval(maya_curves.cross_crv.format(**{'jnt_control': control_name}))
            pm.setAttr(control_name+'.t', jnt_pos)
            mc.select(control_name, r=True)
            mel.eval('FreezeTransformations;')
            mc.parentConstraint(control_name, each_jnt, mo=True, name=each_jnt+'constr')
            grp0 = mc.group(control_name, name=control_name+'_grp_0')
            grp1 = mc.group(grp0, name=control_name+'_grp_1')
            control_grps.append(grp1)
        controls_grp = mc.group(control_grps, name=self._crv_node_name+'_controls_grp')
        nurbs_curve_main = self._crv_node_name + '_curve_main'
        nurbs_curve_master = self._crv_node_name + '_curve_master'
        control_pos = pm.PyNode(self._crv_node_name).getRotatePivot()
        # print control_pos
        mel.eval(maya_curves.main_crv.format(**{'main_crv_name': nurbs_curve_main}))
        pm.setAttr(nurbs_curve_main + '.t', control_pos)
        mc.parent(controls_grp, nurbs_curve_main)
        mel.eval(maya_curves.master_crv.format(**{'master_crv_name': nurbs_curve_master}))
        pm.setAttr(nurbs_curve_master + '.t', control_pos)
        mc.select(nurbs_curve_master, r=True)
        mc.group(self._crv_node_name+'_crv_jnt_grp', nurbs_curve_master, name=self._crv_node_name+'_ctrl_grp')
        if not mc.objExists(self._crv_node_name + '_rig_grp'):
            mc.createNode('transform', name=self._crv_node_name + '_rig_grp')
        mc.parent(self._crv_node_name+'_ctrl_grp', self._crv_node_name + '_rig_grp')
        mc.select(nurbs_curve_main, nurbs_curve_master, r=True)
        mel.eval('FreezeTransformations;')
        mc.parent(nurbs_curve_main, nurbs_curve_master)
        print 'building controls ...'


class Main(base_class, form_class):
    def __init__(self, parent=None):
        super(Main, self).__init__(parent=loadUiType.getMayaWindow())
        self.setupUi(self)
        # self._ctrl_name = str()
        # self._locator_ctl = str()
        # self._first_jnt_name = str()
        # self._last_jnt_name = str()
        self._crv_name = str()
        # self._crv_points_num = str()
        # self._crv_roll_name = str()
        # self.ctrLweight_sl.sliderReleased.connect(self.on_create_crv_ctrl_pb_clicked)
        # self.controls_num_sb.editingFinished .connect(self.on_create_crv_ctrl_pb_clicked)

    # @QtCore.Slot(name="on_input_ctrl_attr_pb_clicked")
    # def on_input_ctrl_attr_pb_clicked(self):
    #     selected_attr = mc.channelBox("mainChannelBox", q=1, selectedMainAttributes=1)[0]
    #     selected_crv = self.get_selected()
    #     selected_crv_attr = selected_crv + "." + selected_attr
    #     self.input_ctrl_attr_le.setText(selected_crv_attr)
    #     self._ctrl_name = selected_crv_attr
    #     return selected_crv_attr

    # @QtCore.Slot(name="on_input_ctrl_roll_pb_clicked")
    # def on_input_ctrl_roll_pb_clicked(self):
    #     selected_attr = mc.channelBox("mainChannelBox", q=1, selectedMainAttributes=1)[0]
    #     selected_crv = self.get_selected()
    #     selected_crv_attr = selected_crv + "." + selected_attr
    #     self.input_ctrl_roll_le.setText(selected_crv_attr)
    #     self._crv_roll_name = selected_crv_attr
    #     return selected_crv_attr
    # @QtCore.Slot(name="on_locator_control_pb_clicked")
    # def on_locator_control_pb_clicked(self):
    #     selected_crv = self.get_selected()
    #     self.locator_control_le.setText(selected_crv)
    #     self._locator_ctl = selected_crv
    #     return selected_crv

    # @QtCore.Slot(name="on_input_first_jnt_name_pb_clicked")
    # def on_input_first_jnt_name_pb_clicked(self):
    #     selected_jnt = self.get_selected()
    #     if not mc.nodeType(selected_jnt) == 'joint':
    #         print selected_jnt
    #         logging.error(u'请选择骨骼！')
    #         return
    #     self.input_first_jnt_name_le.setText(selected_jnt)
    #     self._first_jnt_name = selected_jnt
    #     return selected_jnt

    # @staticmethod
    # def get_end_jnt_name(jnt):
    #     return mc.listRelatives(jnt, c=1, ad=1)[0]

    # @QtCore.Slot(name="on_input_last_jnt_name_pb_clicked")
    # def on_input_last_jnt_name_pb_clicked(self):
    #     selected_jnt = self.get_selected()
    #     if not mc.nodeType(selected_jnt) == 'joint':
    #         logging.error(u'请选择骨骼！')
    #         return
    #     self.input_last_jnt_name_le.setText(selected_jnt)
    #     self._last_jnt_name = selected_jnt
    #     self.input_first_jnt_name_le.setText(self.get_end_jnt_name(selected_jnt))
    #     self._first_jnt_name = self.get_end_jnt_name(selected_jnt)
    #     return selected_jnt

    @QtCore.Slot(name="on_input_crv_name_pb_clicked")
    def on_input_crv_name_pb_clicked(self):
        selected_crv = self.get_selected()
        if not pm.PyNode(selected_crv).getShape().nodeType() == 'nurbsCurve':
            logging.error(u'请选择曲线！')
            return
        self.input_crv_name_le.setText(selected_crv)
        self._crv_name = selected_crv
        return selected_crv

    # @QtCore.Slot(name='on_doit_pb_clicked')
    # @undoable
    # def on_doit_pb_clicked(self):
    #     self.rebuild_crv()
    #     self.create_ik_handle()

    @staticmethod
    def get_selected():
        selection = mc.ls(sl=True)
        if len(selection) != 1:
            logging.error(u"请只选择一个物体！")
            return
        return selection[0]

    # @QtCore.Slot(name="on_reverse_crv_pb_clicked")
    # def on_reverse_crv_pb_clicked(self):
    #     if self._crv_name:
    #         mc.reverseCurve(self._crv_name, ch=1, rpo=1)
    #     return

    @property
    def weight(self):
        return self.controls_weight_sb.value()

    @property
    def max_weight(self):
        return self.controls_max_weight_sb.value()

    def rebuild_crv(self):
        if_rebuild = self.if_rebuild_cb.isChecked()
        if if_rebuild:
            spans = self.crv_points_num_sb.value()
            mc.rebuildCurve(self._crv_name, rpo=1, ch=1, end=1, kr=0, kcp=0, kt=0, d=3, tol=0.01, rt=0, s=spans)

    # def create_ik_handle(self):
    #     #  create locator
    #     control_name = self._ctrl_name.split(".")[0]
    #     locator_name = self._crv_name + "_motionPath_locator"
    #     locator_pos = [mc.getAttr(control_name+".tx"),
    #                    mc.getAttr(control_name+".ty") + 999999,
    #                    mc.getAttr(control_name+".tz")]
    #     motion_path_locator = mc.spaceLocator(name=locator_name)[0]
    #     mc.select(locator_name, r=True)
    #     if self.cp_cb.isChecked():
    #         mc.CenterPivot()
    #     mc.setAttr(pm.PyNode(locator_name).getShape().name()+".localScale", 10, 10, 10)
    #     mel.eval("channelBoxCommand -freezeScale")
    #     locator_grp = mc.createNode("transform", name=locator_name+"_Grp")
    #     mc.parent(locator_name, locator_grp)
    #     #  create IK handle
    #     mc.select(self._first_jnt_name, self._last_jnt_name, self._crv_name, r=True)
    #     ik_handle = mc.ikHandle(sol="ikSplineSolver", ccv=False, pcv=False)
    #     mc.setAttr(ik_handle[0]+".dTwistControlEnable", 1)
    #     mc.setAttr(ik_handle[0]+".dWorldUpType", 1)
    #     # print ik_handle[0], motion_path_locator
    #     mc.setAttr(motion_path_locator+".t", locator_pos[0], locator_pos[1], locator_pos[2])
    #     mc.connectAttr(motion_path_locator+".worldMatrix[0]", ik_handle[0]+".dWorldUpMatrix")
    #     mc.connectAttr(self._ctrl_name, ik_handle[0] + ".offset", f=True)
    #     mc.connectAttr(self._crv_roll_name, ik_handle[0] + ".roll", f=True)
    #     # mc.parentConstraint(self._locator_ctl, locator_grp, mo=1)
    #     mc.group(ik_handle[0], locator_grp, name=self._crv_name+'_rig_grp')

    @QtCore.Slot(name='on_create_crv_ctrl_pb_clicked')
    @undoable
    def on_create_crv_ctrl_pb_clicked(self):
        self.rebuild_crv()
        crv_name = self.input_crv_name_le.text()
        mc.select(crv_name, r=True)
        if self.if_keep_shape_cb.isChecked():
            mel.eval('DeleteHistory;')
        if self.cp_cb.isChecked():
            mel.eval('CenterPivot;')
        if mc.objExists(crv_name+'_ctrl_grp'):
            mc.delete(crv_name+'_ctrl_grp')
        spans = self.controls_num_sb.value()-1
        pmcrv = pm.PyNode(crv_name)
        crv = MakeCrvControls(pmcrv, spans)
        crv.create_jnts()
        crv.bind_skin()
        crv.draw_weights(self.weight, self.max_weight)
        crv.wipe_weights()
        crv.build_controls()















