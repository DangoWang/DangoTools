#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: Dango Wang
# time : 2019/1/8

__author__ = 'Dango Wang'
__license__ = "MIT"
__doc__ = 'this script inherits oct_playblast_win and is to add functions to the main window'

import os
import subprocess
import codecs
# import getpass
import shutil
import logging
import time
from .ui import oct_playblast_win, gridLayoutMethods
from .lib import yaml
from .utils import loadUiType, listMayaInfo, maya_multi_processing
import playBlastCMD
import pymel.core as pm
import maya.mel as mel
import maya.cmds as cmds

try:
    from PySide2 import QtWidgets, QtCore
except ImportError:
    from PySide import QtCore
    import PySide.QtGui as QtWidgets
reload(oct_playblast_win)
reload(listMayaInfo)
reload(gridLayoutMethods)
reload(playBlastCMD)

# necessary global param
file_path = str(os.path.split(os.path.realpath(__file__))[0])
default_config = os.path.join(file_path, 'config\\oct_play_blast_settings.yaml')
default_hud_config = os.path.join(file_path, 'config\\HUD_config.yaml')
user_config = cmds.internalVar(userAppDir=True) + "oct_play_blast_settings.yaml"
user_hud_config = cmds.internalVar(userAppDir=True) + "HUD_config.yaml"
ffmpeg_path = cmds.internalVar(userAppDir=True) + "ffmpeg.exe"
proj_dic = {'dsf': 0}  # record the item index of the window for changing
dep_dic = {'Layout': 0, 'Animation': 1, 'VFX': 2, 'Lighting': 3}
form_class, base_class = loadUiType.loadUiType(file_path + '\\ui\\oct_playBlast_ui.ui')


class OctPlayBlastMain(oct_playblast_win.OctPlayBlastWin):
    def __init__(self, parent=None):
        super(OctPlayBlastMain, self).__init__()
        self.setupUi(self)
        # private param
        self._config_data = self.read_config()
        self._hud_config_data = self.read_hud_config()
        # all_hud_info = list()
        # self.drawed_hud_info = list()
        # self.stop_drawing = 0
        # method
        self.add_hud_pushButton.clicked.connect(self.on_add_hud_pushButton_clicked)
        self.reduce_hud_pushButton.clicked.connect(self.on_reduce_hud_pushButton_clicked)
        self.label_color_pushButton.clicked.connect(self.on_label_color_pushButton_clicked)
        self.value_color_pushButton.clicked.connect(self.on_value_color_pushButton_clicked)
        self.board_color_pushButton.clicked.connect(self.on_board_color_pushButton_clicked)
        self.proj_comboBox.currentIndexChanged.connect(self.proj_dep_comboBox_value_changed)
        self.dep_comboBox.currentIndexChanged.connect(self.proj_dep_comboBox_value_changed)
        self.scene_path_pushButton.clicked.connect(self.on_scene_path_pushButton_clicked)
        self.select_path_pushButton.clicked.connect(self.on_select_path_pushButton_clicked)
        self.input_cam_pushButton.clicked.connect(self.on_input_cam_pushButton_clicked)
        self.input_video_pushButton.clicked.connect(self.on_input_video_pushButton_clicked)
        self.input_range_pushButton.clicked.connect(self.on_input_range_pushButton_clicked)
        self.settings_tabWidget.currentChanged.connect(self.on_settings_tabWidget_clicked)
        self.add_hud_doit_pushButton.clicked.connect(self.add_hud_unit)
        self.reduce_hud_doit_pushButton.clicked.connect(self.delete_hud_unit)
        self.font_comboBox.currentIndexChanged.connect(self.set_hud_font)
        self.font_size_comboBox.currentIndexChanged.connect(self.set_hud_font)
        self.display_mask_checkBox.stateChanged.connect(self.set_board_color)
        self.input_hud_label_comboBox.currentIndexChanged.connect(self.add_hud_info)
        self.playBlast_doit_pushButton.clicked.connect(self.on_playBlast_doit_pushButton_clicked)
        # QAction
        self.save_action.triggered.connect(self.save_settings)
        self.import_settings_action.triggered.connect(self.import_settings)
        self.export_settings_action.triggered.connect(self.export_settings)
        self.reset_action.triggered.connect(self.reset_settings)

        self.import_hud_action.triggered.connect(self.import_hud_settings)
        self.export_hud_action.triggered.connect(self.export_hud_settings)
        self.reset_hud_action.triggered.connect(self.reset_hud_settings)

        self.quit_action.triggered.connect(self.close)

    #
    def on_playBlast_doit_pushButton_clicked(self):
        """
        :return:None
        """
        width = int(self.size_X_spinBox.value())
        # print width
        height = int(self.size_Y_spinBox.value())
        quality = self.quality_spinBox.value()
        format = self.format_comboBox.currentText()
        codec = self.codec_comboBox.currentText()
        fps = self.fps_spinBox.value()
        percent = self.scale_doubleSpinBox.value() * 100
        # print percent
        mov_name = self.video_name_lineEdit.text()
        mov_path = self.file_path_lineEdit.text()
        if not (mov_name and mov_path):
            logging.error("Plz input all info needed!!")
            return
        jpg_path = mov_path + "/oct_playblast_cache" + mov_name
        start_frame = self.start_frame_spinBox.value()
        end_frame = self.end_frame_spinBox.value()
        time_duation = (end_frame - start_frame + 1) / float(fps)
        off_screen = self.off_screen_checkBox.isChecked()
        frame = start_frame
        playbackSlider = mel.eval("$temp = $gPlayBackSlider")
        sound_path = "no_sound"
        if not os.path.isfile(ffmpeg_path):
            if not os.path.isdir(ffmpeg_path.strip('/ffmpeg.exe')):
                try:
                    os.mkdir(ffmpeg_path.strip('/ffmpeg.exe'))
                except:
                    logging.error(u"请确保我的文档中有maya文件夹！")
            shutil.copyfile(file_path + "/bin/ffmpeg.exe", ffmpeg_path)
        try:
            soundStr = pm.PyNode(pm.timeControl(playbackSlider, q=1, sound=1, fpn=1))
            sound_path = soundStr.getAttr("filename")
        except:
            pass
        # sound_offset = soundStr.getAttr("offset") / fps
        mov_file = mov_path + "/" + mov_name + ".mov"
        if os.path.isfile(mov_file):
            if_cast = cmds.confirmDialog(t="warning", m="File:\" %s \" exists, replace it?" % mov_file, b=['Yes', 'No'])
            if if_cast == "Yes":
                try:
                    os.remove(mov_file)
                except WindowsError:
                    logging.error(u"This file has been opened and cannot be replaced!Please close it and try again!")
                    return
            else:
                return
        if os.path.isdir(jpg_path):
            shutil.rmtree(jpg_path)
        while frame < (end_frame + 1):
            cmds.currentTime(frame)
            picture = playBlastCMD.capture(panel=self._playblast_panel, width=width, height=height, percent=percent,
                                           filename=jpg_path + "/" + mov_name, frame=frame,
                                           quality=quality, off_screen=off_screen, framePadding=4)
            # print picture
            seq = str(frame).zfill(4)
            # all_hud_info.append(self.hud_text(picture.replace("####", "%s" % seq)))
            if self.draw_hud_checkBox.isChecked():
                self.draw_hud_text(self.hud_text(picture.replace("####", "%s" % seq)))
            frame += 1
        # if all_hud_info:
        #     print "================================="
        #     print "Drawing HUD...please wait..."
        #     map(self.draw_hud_text, all_hud_info)
        start_number = str(start_frame).zfill(4)
        time.sleep(0.5)
        # if self.stop_drawing and not all_hud_info:
        #     backstage_drawing.stop()
        print "Drawing HUD down.\nCompressing Video..."
        pic_format = '.png'
        if self.draw_hud_checkBox.isChecked():
            pic_format = '.jpg'
        self.compress_video(fps=str(fps), time_duation=str(time_duation), start_number=start_number,
                            ffmpeg_path="\"" + ffmpeg_path + "\"",
                            input_path="\"" + jpg_path + "/%s" % (mov_name + ".%04d"+pic_format) + "\"",
                            output_path="\"" + mov_path + "/%s" % (mov_name + ".mov") + "\"",
                            sound="\"" + sound_path + "\"", jpg_path=jpg_path)

    def compress_video(self, fps, time_duation, start_number, ffmpeg_path, input_path, output_path, jpg_path, sound=None):
        if sound == "\"no_sound\"":
            compress_word = [ffmpeg_path, "-y -framerate", fps, u"-start_number", start_number, "-i", input_path,
                             "-c:v libx264 -profile:v baseline -vf \"pad=ceil(iw/2)*2:ceil(ih/2)*2\" -pix_fmt yuv420p", output_path]
        # print compress_word
        else:
            compress_word = [ffmpeg_path, "-y -framerate", fps, u"-start_number", start_number, "-i", input_path,
                             "-i", sound, "-ss 0:0:0", "-t", time_duation,
                             "-c:v libx264 -profile:v baseline -vf \"pad=ceil(iw/2)*2:ceil(ih/2)*2\" -pix_fmt yuv420p", output_path]
        compress_cmd = " ".join(compress_word)
        # print compress_cmd
        subprocess.call(compress_cmd, shell=True)
        subprocess.Popen("explorer \"%s\"" % os.path.abspath(output_path.strip("\"")))
        if os.path.isdir(jpg_path):
            timer = maya_multi_processing.Timer(5, lambda: shutil.rmtree(jpg_path), repeat=False)
            timer.start()

    # print output_path.strip("\"")

    # def scan_files(self, path, postfix):
    #     return playBlastCMD.scan_file(path, postfix)

    # def scan_drawing(self):
    #     fresh_hud_info = [hud for hud in all_hud_info if hud not in self.drawed_hud_info]
    #     if fresh_hud_info:
    #         print 1
    #         for each_info in fresh_hud_info:
    #             self.draw_hud_text(each_info)
    #             all_hud_info.pop(each_info)
    #             self.drawed_hud_info.append(each_info)
    #     else:
    #         print 0
    #     return

    def hud_text(self, input_path):
        """
        draw text using ffmpeg
        :return:
        """
        size = [self.size_X_spinBox.value(), self.size_Y_spinBox.value()]
        scale = self.scale_doubleSpinBox.value()
        camera_name = self.cam_name_lineEdit.text()
        text_info = playBlastCMD.get_text_info(self.hud_gridLayout, size, scale, camera_name,
                                               self.margin_doubleSpinBox.value(), self.gap_doubleSpinBox.value())
        # print text_info
        label_color = playBlastCMD.convert_color(playBlastCMD.get_rgb(self.label_color_pushButton.styleSheet()))
        value_color = playBlastCMD.convert_color(playBlastCMD.get_rgb(self.value_color_pushButton.styleSheet()))
        font = self.font_comboBox.currentText()
        font_size = self.font_size_comboBox.currentText()
        unit_opacity = self.font_opacity_doubleSpinBox.value()
        board_display = self.display_mask_checkBox.isChecked()
        board_color = playBlastCMD.convert_color(playBlastCMD.get_rgb(self.board_color_pushButton.styleSheet()))
        board_opacity = self.board_opacity_doubleSpinBox.value()
        # print all_files
        return {"input_pic": input_path,
                "output_pic": input_path.replace(".png", ".jpg"),
                "text_content": text_info,
                "label_color": label_color,
                "value_color": value_color,
                "font": font,
                "font_size": font_size,
                "unit_opacity": unit_opacity,
                "board_display": board_display,
                "board_color": board_color,
                "board_opacity": board_opacity}
        # playBlastCMD.draw_all_text_cmd(input_pic=input_path, output_pic=input_path.replace(".png", ".jpg"),
        #                                text_content=text_info,
        #                                label_color=label_color, value_color=value_color,
        #                                font=font, font_size=font_size, unit_opacity=unit_opacity,
        #                                board_display=board_display, board_color=board_color,
        #                                board_opacity=board_opacity)

    def draw_hud_text(self, hud_text):
        return playBlastCMD.draw_all_text_cmd(**hud_text)
        # return playBlastCMD.draw_all_text_cmd(input_pic=hud_text["input_pic"],
        #                                        output_pic=hud_text["output_pic"],
        #                                        text_content=hud_text["text_content"],
        #                                        label_color=hud_text["label_color"],
        #                                        value_color=hud_text["value_color"],
        #                                        font=hud_text["font"],
        #                                        font_size=hud_text["font_size"],
        #                                        unit_opacity=hud_text["unit_opacity"],
        #                                        board_display=hud_text["board_display"],
        #                                        board_color=hud_text["board_color"],
        #                                        board_opacity=hud_text["board_opacity"]
        #                                        )

    """
    PlayBlast settings
    """

    def on_settings_tabWidget_clicked(self):
        if self.playblast_stackedWidget.currentIndex() == 0:
            self.playblast_stackedWidget.setCurrentIndex(1)
        else:
            self.playblast_stackedWidget.setCurrentIndex(0)

    def on_input_range_pushButton_clicked(self):
        self.start_frame_spinBox.setValue(listMayaInfo.get_timeslider_time()[1])
        self.end_frame_spinBox.setValue(listMayaInfo.get_timeslider_time()[2])
        return listMayaInfo.get_timeslider_time()[1], listMayaInfo.get_timeslider_time()[2]

    def on_input_video_pushButton_clicked(self):
        self.video_name_lineEdit.setText(listMayaInfo.get_current_file_name().split(".")[0])
        return listMayaInfo.get_current_file_name().split(".")[0]

    def on_input_cam_pushButton_clicked(self):
        selected_obj = cmds.ls(sl=True)
        if not selected_obj:
            logging.error("Please select the camera!!")
            return False
        selected_cam = selected_obj[0]
        cam_transform = None
        if cmds.objectType(selected_cam) in ['camera']:
            cam_transform = cmds.listRelatives(selected_cam, p=1)[0]
        # self.cam_name_lineEdit.setText(cam_transform)
        elif cmds.objectType(selected_cam) in ['transform']:
            cam_transform = selected_cam
        else:
            logging.error("Please select at least one camera node!(Including shape node and transform node)")
        if cam_transform:
            self.cam_name_lineEdit.setText(cam_transform)
            cmds.modelEditor("playBlast_panel", e=True, camera=cam_transform)
        else:
            logging.error("No camera selected!")
        return True

    def on_scene_path_pushButton_clicked(self):
        # set file path
        scene_path = listMayaInfo.get_current_file_name(full_path=True, dir_path=True)
        try:
            self.file_path_lineEdit.setText(scene_path)
            return True
        except (AttributeError, NameError, TypeError, RuntimeError):
            return False

    def select_path_dialog(self, dialogStyle, fileMode, dir):
        try:
            selected_path = str(cmds.fileDialog2(dialogStyle=dialogStyle, fileMode=fileMode, dir=dir)).split('\'')[1]
            return selected_path
        except IndexError:
            logging.error("Please select a directory!")
            return ""

    def on_select_path_pushButton_clicked(self):
        # select file path
        current_path = self.file_path_lineEdit.text()
        selected_path = self.select_path_dialog(1, 3, current_path)
        self.file_path_lineEdit.setText(selected_path)
        return True

    def proj_dep_comboBox_value_changed(self):
        """
        Change settings for every time changing project or department.
        :return:
        """
        default_proj = self.proj_comboBox.currentText()
        default_dep = self.dep_comboBox.currentText()
        self.set_settings(default_proj, default_dep)
        self.set_hud_settings()

    # self.write_config()

    def closeEvent(self, event):
        """
        Save config before closed if chose to.
        :param event:
        :return:
        """
        if self.save_checkBox.isChecked():
            self.save_settings()
            event.accept()
        else:
            event.accept()

    def save_settings(self):
        self.write_config()
        self.write_hud_config()
        logging.info("Successfully saved configuration!")

    def import_settings(self):
        import_path = self.select_path_dialog(1, 1, default_config)
        if not import_path:
            return
        self.read_config(import_path)
        default_proj = self.proj_comboBox.currentText()
        default_dep = self.dep_comboBox.currentText()
        self.set_settings(default_proj, default_dep)
        return True

    def import_hud_settings(self):
        import_path = self.select_path_dialog(1, 1, default_config)
        if not import_path:
            return
        self.read_hud_config(import_path)
        self.set_hud_settings()
        return True

    def export_settings(self):
        export_path = self.select_path_dialog(1, 1, default_config)
        if not export_path:
            return
        self.write_config(export_path)
        return True

    def export_hud_settings(self):
        export_path = self.select_path_dialog(1, 1, default_config)
        if not export_path:
            return
        self.write_hud_config(export_path)
        return True

    def reset_settings(self):
        self.read_config(default_config)
        default_proj = self.proj_comboBox.currentText()
        default_dep = self.dep_comboBox.currentText()
        self.set_settings(default_proj, default_dep)
        return True

    def reset_hud_settings(self):
        self.read_hud_config(default_hud_config)
        self.set_hud_settings()
        return True

    def on_add_hud_pushButton_clicked(self):
        """
        :return:
        """
        self.stackedWidget.setCurrentIndex(0)
        return True

    def on_reduce_hud_pushButton_clicked(self):
        self.stackedWidget.setCurrentIndex(1)
        return True

    def on_label_color_pushButton_clicked(self):
        # add color panel for users to select color
        label_color = QtWidgets.QColorDialog.getColor()
        if label_color.isValid():
            style_sheet = 'background-color: rgb({}, {}, {});'.format(label_color.getRgb()[0],
                                                                      label_color.getRgb()[1], label_color.getRgb()[2])
            self.label_color_pushButton.setStyleSheet(style_sheet)
            self.set_label_color(style_sheet.replace('background-color', 'color'))
        return label_color

    def on_value_color_pushButton_clicked(self):
        value_color = QtWidgets.QColorDialog.getColor()
        if value_color.isValid():
            style_sheet = 'background-color: rgb({}, {}, {});'.format(value_color.getRgb()[0],
                                                                      value_color.getRgb()[1], value_color.getRgb()[2])
            self.value_color_pushButton.setStyleSheet(style_sheet)
            self.set_value_color(style_sheet.replace('background-color', 'color'))
            print style_sheet.replace('background-color', 'color')
        return value_color

    def on_board_color_pushButton_clicked(self):
        board_color = QtWidgets.QColorDialog.getColor()
        if board_color.isValid():
            self.board_color_pushButton.setStyleSheet(
                'background-color: rgb({}, {}, {});'.format(board_color.getRgb()[0], board_color.getRgb()[1],
                                                            board_color.getRgb()[2]))
            self.set_board_color(board_color=board_color)
        return board_color

    def read_config(self, config_path=None):
        """
        Read the config file from disk. The default config path is on the top of this module.
        :return: config data
        """
        setting_data = dict()
        if config_path is None:
            config_path = user_config if os.path.isfile(user_config) else default_config
        with codecs.open(config_path, 'r', encoding='utf-8') as f:
            setting_data = yaml.load(f)
        # pprint(setting_data.items())
        if setting_data:
            return setting_data
        else:
            logging.warning("Failed to load config, read default config instead...")
            self.read_hud_config(default_config)

    def set_settings(self, default_proj, default_dep):
        """
        set all settings from config to window
        :return: True if successful.
        """
        setting_datas = self._config_data
        # pprint(setting_datas[default_proj][default_dep])
        for each_control in setting_datas[default_proj][default_dep]:
            # convert the string to obj first.
            control_widget = self.findChild(QtWidgets.QPushButton, each_control["ControlName"])
            # if this is a pushButton, we should fix it separately for the stylesheet.
            if control_widget:
                try:
                    eval("control_widget.{}(\"{}\")".format(each_control["SetMethod"], each_control["Value"]))
                    continue
                except NameError:
                    pass
                # print("error111!")
            control_widget = self.findChild(QtWidgets.QSpinBox, each_control["ControlName"]) \
                             or self.findChild(QtWidgets.QDoubleSpinBox, each_control["ControlName"]) \
                             or self.findChild(QtWidgets.QFontComboBox, each_control["ControlName"]) \
                             or self.findChild(QtWidgets.QComboBox, each_control["ControlName"]) \
                             or self.findChild(QtWidgets.QLineEdit, each_control["ControlName"]) \
                             or self.findChild(QtWidgets.QCheckBox, each_control["ControlName"])
            try:
                eval("control_widget.{}({})".format(each_control["SetMethod"], each_control["Value"]))
            # print each_control["Value"]
            except (NameError, TypeError, SyntaxError):
                # For lineEdit, we should fix it separately.
                # print 1111
                # print each_control["Value"]
                if each_control["Value"]:
                    eval("control_widget.{}(\'{}\')".format(each_control["SetMethod"], each_control["Value"]))
            except (SyntaxError, RuntimeError, AttributeError):
                #     print"error!333"
                continue
        return True

    def get_current_settings(self):
        """
        Allows you to export your configurations
        :param config_path: assign the export path if needed
        :return: True
        """
        setting_datas = self._config_data
        default_proj = self.proj_comboBox.currentText()
        default_dep = self.dep_comboBox.currentText()
        setting_datas["DefaultProj"] = default_proj
        setting_datas["DefaultDep"] = default_dep
        i = 0
        for each_control in setting_datas[default_proj][default_dep]:
            # print each_control
            control_widget = self.findChild(QtWidgets.QSpinBox, each_control["ControlName"]) \
                             or self.findChild(QtWidgets.QDoubleSpinBox, each_control["ControlName"]) \
                             or self.findChild(QtWidgets.QFontComboBox, each_control["ControlName"]) \
                             or self.findChild(QtWidgets.QComboBox, each_control["ControlName"]) \
                             or self.findChild(QtWidgets.QLineEdit, each_control["ControlName"]) \
                             or self.findChild(QtWidgets.QPushButton, each_control["ControlName"]) \
                             or self.findChild(QtWidgets.QCheckBox, each_control["ControlName"])
            try:
                new_value = eval("control_widget.{}()".format(each_control["ReadMethod"]))
                setting_datas[default_proj][default_dep][i]["Value"] = new_value
                i += 1
            except (SyntaxError, RuntimeError, TypeError, AttributeError):
                pass
        return setting_datas

    def write_config(self, config_path=None):
        """
        write config to local disk
        :param config_path: given path
        :return:
        """
        if config_path is None:
            if not os.path.isfile(user_config):
                try:
                    shutil.copy(default_config, user_config)
                except IOError:
                    logging.error("Invalid file path!Please assign a new directory to save your configuration!")
                    return False
            config_path = user_config
        current_config = self.get_current_settings()
        with codecs.open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(current_config, f)
        return True

    """
    HUD Settings
    """

    def align_together(self):
        all_units = gridLayoutMethods.all_units(self.hud_gridLayout)
        for each in all_units:
            if each[1][1] % 2:
                # each[0].setAlignment(QtCore.Qt.AlignRight)
                each[0].setAlignment(QtCore.Qt.AlignHCenter)
            else:
                # each[0].setAlignment(QtCore.Qt.AlignLeft)
                each[0].setAlignment(QtCore.Qt.AlignHCenter)
        return True

    def read_hud_config(self, hud_config_path=None):
        setting_data = dict()
        if hud_config_path is None:
            hud_config_path = user_hud_config if os.path.isfile(user_hud_config) else default_hud_config
        with codecs.open(hud_config_path, 'r', encoding="utf-8") as f:
            setting_data = yaml.load(f)
        # pprint(setting_data.items())
        if setting_data:
            return setting_data
        else:
            logging.warning("Failed to load config, read default config instead...")
            self.read_hud_config(default_hud_config)

    def write_hud_config(self, hud_config_path=None):
        if hud_config_path is None:
            if not os.path.isfile(user_hud_config):
                try:
                    shutil.copy(default_hud_config, user_hud_config)
                except IOError:
                    logging.error("Invalid file path!Please assign a new directory to save your configuration!")
                    return False
            hud_config_path = user_hud_config
        current_hud_config = self.get_hud_settings()
        current_proj = self.proj_comboBox.currentText()
        current_dep = self.dep_comboBox.currentText()
        self._hud_config_data[current_proj][current_dep] = current_hud_config
        with codecs.open(hud_config_path, "w", encoding="utf-8") as f:
            yaml.dump(self._hud_config_data, f)
            logging.info("Successfully write into config %s" % hud_config_path)
        return True

    def get_hud_settings(self):
        """
        For saving config
        :return:
        """
        all_units = gridLayoutMethods.all_units(self.hud_gridLayout)
        hud_info = list()
        for each_widget in all_units:
            text = each_widget[0].text()
            pos = each_widget[1]
            each_dict = {"Label": text, "Pos": pos}
            hud_info.append(each_dict)
        # current_proj = self.proj_comboBox.currentText()
        # current_dep = self.dep_comboBox.currentText()
        # hud_contents = {current_dep: hud_info}
        return hud_info

    def add_hud_label(self, label_text, pos):
        if not gridLayoutMethods.find_unit(self.hud_gridLayout, pos):
            label = QtWidgets.QLabel()
            label.setText(label_text)
            self.hud_gridLayout.addWidget(label, pos[0], pos[1])
        else:
            gridLayoutMethods.find_unit(self.hud_gridLayout, pos).setText(label_text)
        return pos

    def set_hud_settings(self):
        """
        Set settings to hud window
        :return:
        """
        gridLayoutMethods.clear_all_units(self.hud_gridLayout)
        current_proj = self.proj_comboBox.currentText()
        current_dep = self.dep_comboBox.currentText()
        hud_info = self._hud_config_data[current_proj][current_dep]
        for each_label in hud_info:
            label_text = each_label["Label"]
            pos = each_label["Pos"]
            self.add_hud_label(label_text, pos)
        self.set_hud_font()
        self.set_label_color()
        self.set_value_color()
        self.set_board_color()
        self.align_together()
        return hud_info

    def add_hud_unit(self):
        section = int(self.add_section_comboBox.currentText())
        block = int(self.add_block_comboBox.currentText())
        label = self.hud_label_add_lineEdit.text() or " "
        value = self.hud_value_add_lineEdit.text() or " "
        self.add_hud_label(label, [block, 2 * section - 1])
        self.add_hud_label(value, [block, 2 * section])
        self.set_value_color()
        self.set_label_color()
        self.set_hud_font()
        self.set_board_color()
        return [block, section]

    def delete_hud_unit(self):
        section = int(self.delete_section_comboBox.currentText())
        block = int(self.delete_block_comboBox.currentText())
        gridLayoutMethods.delete_hud_unit(self.hud_gridLayout, [block, 2 * section - 1])
        gridLayoutMethods.delete_hud_unit(self.hud_gridLayout, [block, 2 * section])
        return [block, section]

    def set_hud_font(self):
        font = self.font_comboBox.currentText()
        font_size = self.font_size_comboBox.currentText()
        all_units = gridLayoutMethods.all_units(self.hud_gridLayout)
        # print all_units
        for each_unit in all_units:
            style_sheet = each_unit[0].styleSheet()
            new_style_sheet = style_sheet + u"font: {}pt \"{}\";".format(font_size, font)
            each_unit[0].setStyleSheet(new_style_sheet)
        # font_to_set = QtGui.QFont(family=font, pointSize=int(font_size))
        # # print font_to_set
        # each_unit[0].setFont(font_to_set)

    def set_label_color(self, style_sheet=None):
        # print 1
        if not style_sheet:
            label_style_sheet = self.label_color_pushButton.styleSheet()
            new_style_sheet = label_style_sheet.replace("background-color", "color")
        else:
            new_style_sheet = style_sheet
        all_labels = gridLayoutMethods.all_labels(self.hud_gridLayout)
        # print all_labels
        for each_unit in all_labels:
            style_sheet = each_unit.styleSheet()
            new_style_sheet2 = style_sheet + new_style_sheet
            each_unit.setStyleSheet(new_style_sheet2)

    def set_value_color(self, style_sheet=None):
        if not style_sheet:
            label_style_sheet = self.value_color_pushButton.styleSheet()
            new_style_sheet = label_style_sheet.replace("background-color", "color")
        else:
            new_style_sheet = style_sheet
        all_values = gridLayoutMethods.all_values(self.hud_gridLayout)
        for each_unit in all_values:
            style_sheet = each_unit.styleSheet()
            new_style_sheet2 = style_sheet + new_style_sheet
            each_unit.setStyleSheet(new_style_sheet2)

    def set_board_color(self, board_color=None):
        if self.display_mask_checkBox.isChecked():
            opacity = str(self.board_opacity_doubleSpinBox.value())
            board_color = self.board_color_pushButton.styleSheet().replace("rgb", "rgba") \
                .replace(")", ("," + opacity + ");"))
        else:
            board_color = ';background-color: rgb();'
        all_units = gridLayoutMethods.all_units(self.hud_gridLayout)
        for each in all_units:
            style_sheet = each[0].styleSheet()
            new_style = style_sheet + board_color.strip("'")
            each[0].setStyleSheet(new_style)
        return True

    def add_hud_info(self):
        label = self.input_hud_label_comboBox.currentText()
        if label == "<< Artist":
            self.hud_label_add_lineEdit.setText("Artist:")
            self.hud_value_add_lineEdit.setText(listMayaInfo.get_user_name())
        elif label == "<< FrameCount":
            self.hud_label_add_lineEdit.setText("Frame:")
            self.hud_value_add_lineEdit.setText(
                str(int(cmds.currentTime(q=True))) + "/" + str(listMayaInfo.get_timeslider_time()[2]))
        elif label == "<< FocalLength":
            self.hud_label_add_lineEdit.setText("FocalLength:")
            self.hud_value_add_lineEdit.setText(
                str(listMayaInfo.get_focal_length(camera_name=self.cam_name_lineEdit.text())))
        elif label == "<< Date":
            self.hud_label_add_lineEdit.setText("Date:")
            self.hud_value_add_lineEdit.setText(str(listMayaInfo.get_current_date()).decode('utf-8'))
        elif label == "<< SceneName":
            self.hud_label_add_lineEdit.setText("SceneName:")
            self.hud_value_add_lineEdit.setText(listMayaInfo.get_current_file_name())
        elif label == "<< CamName":
            self.hud_label_add_lineEdit.setText("Cam:")
            self.hud_value_add_lineEdit.setText(self.cam_name_lineEdit.text())
        elif label == "<< Size":
            self.hud_label_add_lineEdit.setText("Size:")
            self.hud_value_add_lineEdit.setText(str(listMayaInfo.get_proj_size()))
        elif label == "<< TimeCode":
            self.hud_label_add_lineEdit.setText("TimeCode:")
            # print listMayaInfo.get_time_code(current_frame=cmds.currentTime(q=True))
            offset = listMayaInfo.get_timeslider_time()[1]-1
            self.hud_value_add_lineEdit.setText(listMayaInfo.get_time_code(current_frame=cmds.currentTime(q=True),
                                                                           offset=offset))
        else:
            pass

    def initialize_settings(self):
        """
        initialize settings when this window first opened
        :return:
        """
        default_proj = self._config_data['DefaultProj']
        default_dep = self._config_data['DefaultDep']
        self.proj_comboBox.setCurrentIndex(proj_dic[default_proj])
        self.dep_comboBox.setCurrentIndex(dep_dic[default_dep])
        self.set_settings(default_proj, default_dep)
        self.cam_name_lineEdit.setText(listMayaInfo.get_camera()[0])
        self.start_frame_spinBox.setValue(listMayaInfo.get_timeslider_time()[1])
        self.end_frame_spinBox.setValue(listMayaInfo.get_timeslider_time()[2])
        self.video_name_lineEdit.setText(listMayaInfo.get_current_file_name().split(".")[0])
        self.on_input_range_pushButton_clicked()
        self.fps_spinBox.setValue(listMayaInfo.get_current_fps())
        self.set_hud_settings()
        #  这里是qt的一个坑，必须这么做，否则信息不能正确被拍出
        self.on_settings_tabWidget_clicked()
        self.on_settings_tabWidget_clicked()
        return True


def main():
    oct_playblast_tool = OctPlayBlastMain()
    oct_playblast_tool.add_playBlast_panel(camera_name=listMayaInfo.get_camera()[0])
    oct_playblast_tool.show()
    # oct_playblast_tool.set_hud_settings()
    # print oct_playblast_tool.get_hud_settings()
    # oct_playblast_tool.write_hud_config()
    timer = maya_multi_processing.Timer(0.001, oct_playblast_tool.initialize_settings, repeat=False)
    timer.start()


# oct_playblast_tool.on_settings_tabWidget_clicked()


# if __name__ == "__main__":
#     initialize_settings()
