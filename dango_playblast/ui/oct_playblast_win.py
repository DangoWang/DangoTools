#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: Dango Wang
# time : 2019/1/7

__author__ = "Dango Wang"
__doc__ = "this script is to create a window with no functions for oct_playblast_main to inherit"


import os
from ..utils import loadUiType
from PySide2.QtWidgets import QWidget
from shiboken2 import wrapInstance
import maya.cmds as cmds
import maya.OpenMayaUI as omui

file_path = str(os.path.split(os.path.realpath(__file__))[0])
form_class, base_class = loadUiType.loadUiType(file_path+'\\oct_playBlast_ui.ui')


class OctPlayBlastWin(base_class, form_class):
    def __init__(self, parent=None):
        super(OctPlayBlastWin, self).__init__(parent=loadUiType.getMayaWindow())
        self.setupUi(self)
        # self.hud_layout = HUDLayout()
        # self.hud_gridLayout.addLayout(self.hud_layout, 0, 0)

    def add_playBlast_panel(self, camera_name="persp"):
        """
        :param camera_name: input camera attached to the panel
        :return: model_editor_widget for adding hud info
        """
        try:
            cmds.deleteUI("layout_temp")
            cmds.deleteUI("playBlast_panel", panel=1)
        except RuntimeError:
            pass
        layout_temp = cmds.paneLayout("layout_temp")
        playBlast_panel_temp = cmds.modelPanel("playBlast_panel",
                                          camera = camera_name,
                                          parent = layout_temp)
        camera_panel = omui.MQtUtil.findControl(layout_temp)
        camera_widget = wrapInstance(long(camera_panel), QWidget)
        self.playblast_gridLayout.addWidget(camera_widget)
        cmds.modelEditor("playBlast_panel", e=True, hud=False)
        return True
        # self.verticalLayout.addWidget(camera_widget)
        # self.playBlast_widget.setMinimumSize(600, 450)
        # camera_widget.setMinimumSize(600, 450)
        # model_editor_name = cmds.modelPanel("playBlast_panel", q=True, me=True)
        # model_editor = omui.MQtUtil.findControl(model_editor_name)
        # model_editor_widget = wrapInstance(long(model_editor), QWidget)
        # # print model_editor_widget
        # return model_editor_widget

    # def add_HUD_info( self ):

# if __name__ == '__main__':
    # playBlast_win = playBlast_window("camera1")
    # playBlast_win.show()



