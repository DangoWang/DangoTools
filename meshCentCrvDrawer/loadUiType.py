#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: Dango Wang
# time : 2019/1/7

import xml.etree.ElementTree as xml
from cStringIO import StringIO
import maya.OpenMayaUI as mui

try:
    from shiboken2 import wrapInstance
    import pyside2uic as uic
    from PySide2 import QtWidgets
except ImportError:
    from shiboken import wrapInstance
    from PySide import QtGui as QtWidgets
    import pysideuic as uic


def loadUiType(uiFile):
    parsed = xml.parse(uiFile)
    widget_class = parsed.find('widget').get('class')
    form_class = parsed.find('class').text

    with open(uiFile, 'r') as f:
        o = StringIO()
        frame = {}

        uic.compileUi(f, o, indent=0)
        pyc = compile(o.getvalue(), '<string>', 'exec')
        exec pyc in frame
        # Fetch the base_class and form class based on their type in the xml from designer
        form_class = frame['Ui_%s' % form_class]
        base_class = getattr(QtWidgets, widget_class)
        return form_class, base_class


def getMayaWindow():
    main_window_ptr = mui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)
