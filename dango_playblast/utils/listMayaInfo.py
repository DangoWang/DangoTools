#!/usr/bin/env python
# -*- coding: utf-8 -*-
# title       : scene_checking
# description : ''
# author      : Aaron Hui Dango
# date        : 2018/10/26
# version     : 1.0
# usage       : for scene checking
# notes       :

# Built-in modules
import os
import logging
import getpass
import time
# Third-party modules
import pymel.core as pm
import maya.cmds as mc
import maya.OpenMayaUI as mui

# Studio modules

# Local modules


logging.basicConfig(filename=os.path.join(os.environ["TMP"], 'scene_checking.txt'),
                    level=logging.WARN, filemode='a', format='%(asctime)s - %(levelname)s: %(message)s')


def get_camera(with_panel=None):
    all_cams = [cam for cam in mc.listCameras(p=1) if not mc.referenceQuery(cam, isNodeReferenced=True)]
    extra_cams = ['persp', 'left', 'right', 'top', 'side', 'bottom']
    if with_panel:
        try:
            current_cam = pm.PyNode(pm.modelPanel(pm.getPanel(wf=True), q=True, cam=True))
            return current_cam
        except RuntimeError:
            pass
    all_cam_transform = [str(cam) for cam in all_cams if str(cam) not in extra_cams]
    # print all_cam_transform
    if all_cam_transform:
        return all_cam_transform
    else:
        return ["persp"]


def get_current_file_name(full_path=False, dir_path=False):
    if full_path:
        if dir_path:
            return str(pm.sceneName().dirname())
        return str(pm.sceneName().abspath())
    return str(pm.sceneName().basename()).split(".")[0]


def get_file_type():
    maya_file_type = ['ma','mb']
    file_type = pm.sceneName().abspath().split('.')[-1].encode('utf8')
    if file_type not in maya_file_type:
        return ""
    return file_type


def get_maya_win(module="mayaUI"):
    """
    get a QMainWindow Object of maya main window
    :param module (optional): string "PySide"(default) or "PyQt4"
    :return main_window: QWidget or QMainWindow object
    """
    prt = mui.MQtUtil.mainWindow()
    if module == "Qt":
        import Qt
        if "PyQt" in Qt.__binding__:
            import sip
            import PyQt4.QtCore as QtCore
            main_window = sip.wrapinstance(long(prt), QtCore.QObject)
        elif Qt.__binding__ == "PySide":
            import shiboken
            import PySide.QtGui as QtGui
            main_window = shiboken.wrapInstance(long(prt), QtGui.QWidget)
        elif Qt.__binding__ == "PySide2":
            import shiboken2
            import PySide2.QtWidgets as QtWidgets
            main_window = shiboken2.wrapInstance(long(prt), QtWidgets.QWidget)
        else:
            raise ValueError('Qt Binding Not supported...')
    elif module == "PyQt4":
        import sip
        import PyQt4.QtCore as QtCore
        main_window = sip.wrapinstance(long(prt), QtCore.QObject)
    elif module == "PySide":
        import shiboken
        import PySide.QtGui as QtGui
        main_window = shiboken.wrapInstance(long(prt), QtGui.QWidget)
    elif module == "PySide2":
        import shiboken2
        import PySide2.QtWidgets as QtWidgets
        main_window = shiboken2.wrapInstance(long(prt), QtWidgets.QWidget)
    elif module == "mayaUI":
        main_window = "MayaWindow"
    else:
        raise ValueError('param "module" must be "mayaUI" "PyQt4" "PySide" "PySide2" or "Qt"')
    return main_window


def get_timeslider_time():
    return [int(pm.playbackOptions(ast=True, query=True)), int(pm.playbackOptions(min=True, query=True)),\
    int(pm.playbackOptions(max=True, query=True)),int(pm.playbackOptions(aet=True, query=True))]


def get_focal_length(camera_name):
    return int(mc.getAttr(camera_name+".focalLength"))


def get_proj_size():
    if mc.objExists('defaultResolution'):
        width = mc.getAttr('defaultResolution.w')
        height = mc.getAttr('defaultResolution.h')
        return str(width) + '*' + str(height)
    else:
        return '000'


def get_time_code(current_frame, offset=0):
    current_frame2 = current_frame - offset
    data = divmod(current_frame2, 24)
    return str(int(data[0])) + "s" + str(int(data[1])) + "f"


def get_current_date():
    weekDayDict = {1: u'Mon', 2: u'Tue', 3: u'Wed', 4: u'Thu', 5: u'Fri', 6: u'Sat', 7: u'Sun'}
    localTime = time.localtime()
    dayForMat = '%Y/%m/%d'
    dayValue = time.strftime(dayForMat, localTime)
    weekForMat = '%w'
    weekValue = str(time.strftime(weekForMat, localTime))
    timeForMat = '%H:%M'
    timeValue = time.strftime(timeForMat, localTime)
    timeString = dayValue + " " + weekDayDict[int(weekValue)] + " " + timeValue.replace(":", "`")
    return timeString


def get_all_wins():
    all_windows = pm.lsUI(typ = 'window')
    window_remove = ['MayaWindow']
    all_extra_windows = [_ for _ in all_windows if _ not in window_remove]
    return all_extra_windows


def get_user_name():
    return getpass.getuser()


def get_useless_anim_crvs(anim_curves=None):
    if not anim_curves:
        anim_curves = pm.ls(type="animCurve")
    useless_anim_crvs = list()
    for anim_curve in anim_curves:
        anim_curve = pm.PyNode(anim_curve)
        # 删除只有一个关键点的动画曲线
        if anim_curve.numKeys() <= 1:
            useless_anim_crvs.append(anim_curve)
            continue
        # 删除完全水平的动画曲线
        # -判断值是否有变化
        value_set = set([anim_curve.getValue(i) for i in xrange(anim_curve.numKeys())])
        is_same_value = len(value_set) == 1
        # -判断手柄是否水平
        is_horizontal = sum(pm.keyTangent(anim_curve, q=True, ia=True, oa=True)) == 0
        if is_same_value and is_horizontal:
            useless_anim_crvs.append(anim_curve)
    return useless_anim_crvs


def get_display_layers(get_ref_layers = None,get_normal_layers = None):
    all_layers = []
    all_layers.extend(
        [k for k in [k for k in mc.ls(type="displayLayer") if k != "defaultLayer"]])
    ref_layers = [k.encode('utf-8') for k in all_layers if  mc.referenceQuery(k, inr=1)]
    if get_ref_layers:
        return ref_layers
    elif get_normal_layers:
        return [_ for _ in all_layers if _ not in ref_layers]
    else:
        return all_layers


def get_all_ref_path(loaded = None,not_loded = None):
    all_ref_path = mc.ls(references=True)
    loaded_ref_path = [_ for _ in all_ref_path if mc.referenceQuery(_ , il=1)]
    if loaded:
        return loaded_ref_path
    elif not_loded:
        return [k for k in all_ref_path if k not in loaded_ref_path]
    else:
        return all_ref_path


def get_current_fps():
    format_list = {'film': 24, 'game': 15, 'pal': 25, 'ntsc': 30, 'show': 48, 'palf': 50, 'ntscf': 60}
    fpsString = mc.currentUnit(query=True, t=True)
    try:
        return format_list[fpsString]
    except:
        return False


def get_unknown_plugin():
    return mc.unknownPlugin(q=True, l=True)


def get_specific_obj(specific_string, type=None):
    return mc.ls(specific_string, type=type)


if __name__ == "__main__":
    pass
