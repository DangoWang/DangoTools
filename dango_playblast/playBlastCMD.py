#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: Dango Wang
# time : 2019/1/20

import maya.cmds as cmds
import os
import locale
import subprocess
from utils import listMayaInfo
from ui import gridLayoutMethods
import time

__license__ = "MIT"
__author__ = "dango wang"
file_path = str(os.path.split(os.path.realpath(__file__))[0])


def capture(panel=None, width=None, height=None, percent=50, filename=None, frame=None,
                form='image', compression='png', quality=100, clear_cache=1, off_screen=False, viewer=False,
                show_ornaments=True,overwrite=True, framePadding=4):
    try:
        return cmds.playblast(editorPanelName=panel, width=width, height=height, percent=percent, filename=filename,
                    startTime=frame, endTime=frame, format=form, compression=compression, quality=quality,
                    clearCache=clear_cache, offScreen=off_screen, viewer=viewer, showOrnaments=show_ornaments,
                    forceOverwrite=overwrite, framePadding=framePadding)
    except TypeError:
        return cmds.playblast(width=width, height=height, percent=percent, filename=filename,
                    startTime=frame, endTime=frame, format=form, compression=compression, quality=quality,
                    clearCache=clear_cache, offScreen=off_screen, viewer=viewer, showOrnaments=show_ornaments,
                    forceOverwrite=overwrite, framePadding=framePadding)


def draw_text(drawed_text, file_name=None, output_name=None):

    # draw_text = \
    #     '\"fontfile={}.ttf: text=\"{}\": x={}: y={}: fontsize={}: fontcolor={}@{}: box={}: boxcolor={}@{}\"'\
    #         .format(font, text, pos[0], pos[1], font_size, label_color, unit_opacity, board_display,
    #                 board_color, board_opacity)
    ffmpeg_path = file_path + "/bin/ffmpeg.exe"
    input_file = file_name
    output_file = output_name
    cmd = [ffmpeg_path, "-y", "-i", "%s" % input_file, "-vf", "%s" % drawed_text, "%s" % output_file]
    command = " ".join(cmd)
    # print command
    subprocess.Popen(command, shell=True)
    return True


def draw_all_text_cmd(input_pic, output_pic, text_content=None, label_color=None, value_color=None, font="simhei",
                    font_size=20, unit_opacity=1, board_display=0, board_color=None, board_opacity=0.5):
    """
    draw text on one pic
    """
    all_text_info = text_content
    # print all_text_info
    # print all_text_info
    drawed_text = str()
    for each in all_text_info:
        # pass
        text = each[0]
        color = value_color if each[1] else label_color
        pos = each[2]
        # print pos
        drawed_text = \
            'drawtext=fontfile={}.ttf:text=\"{}\":x={}:y={}:fontsize={}:fontcolor={}@{}:box={}:boxcolor={}@{}'\
                .format(font, text, pos[0], pos[1], font_size, color, unit_opacity, board_display,
                        board_color, board_opacity) + "," + drawed_text
    new_draw_text = drawed_text.rstrip(',')
    # print new_draw_text
    draw_text(new_draw_text, input_pic, output_pic)
    return draw_text


def get_text_info(grid_layout, size, scale, camera_name, margin=0):
    """
    :param margin: 0 by default
    :param scale: like 0.5
    :param grid_layout: QGridLayout
    :param size: the final size of the mov file: [2048,858]
    :param camera_name:
    :return: all text info
    """
    text_info = list()  # every unit text info form like this: [(text, color_mode, pos())...]
    all_units = gridLayoutMethods.all_units_with_margin(grid_layout, margin)
    # print all_units
    for each in all_units:
        text = get_unit_text(grid_layout, each[1], camera_name)
        color_mode = 0 if each[1][1] % 2 else 1  # "each" is like this (widget, each_pos, (percent_x, percent_y))
        pos = (each[2][0] * size[0] * scale, each[2][1] * size[1] * scale)
        text_info.append((text, color_mode, pos))
    # print text_info
    final_info = [each_info for each_info in text_info if each_info[0]]
    # print final_info
    return final_info


def get_unit_text(grid_layout, pos, camera_name):
    label = grid_layout.itemAtPosition(pos[0], pos[1]).widget().text()
    if pos[1] % 2:
        return label
    else:
        label = grid_layout.itemAtPosition(pos[0], pos[1]-1).widget().text()
        if label == "Artist:":
            return listMayaInfo.get_user_name()
        elif label == "Frame:":
            return str(int(cmds.currentTime(q=True)))+"/"+str(listMayaInfo.get_timeslider_time()[2])
        elif label == "FocalLength:":
            return str(listMayaInfo.get_focal_length(camera_name))
        elif label == "Date:":
            return str(listMayaInfo.get_current_date())
        elif label == "SceneName:":
            return listMayaInfo.get_current_file_name()
        elif label == "Cam:":
            return camera_name
        elif label == "Size:":
            return str(listMayaInfo.get_proj_size())
        elif label == "TimeCode:":
            # print listMayaInfo.get_time_code(current_frame=cmds.currentTime(q=True))
            return listMayaInfo.get_time_code(current_frame=cmds.currentTime(q=True))
        else:
            return grid_layout.itemAtPosition(pos[0], pos[1]).widget().text()


def convert_color(rgb):
    def convert_0(hex_color):
        if hex_color == "0":
            return "00"
        else:
            return hex_color
    # print R,G,B
    return convert_0(hex(rgb[0]).split("0x")[1]) + convert_0(hex(rgb[1]).split("0x")[1]) + convert_0(hex(rgb[2]).split("0x")[1])


def get_rgb(style_sheet):
    rgb_string = style_sheet.split("(")[1].split(")")[0].split(",")
    # print int(rgb_string[0]), int(rgb_string[1]), int(rgb_string[2])
    return int(rgb_string[0]), int(rgb_string[1]), int(rgb_string[2])


def scan_file(dirname, postfix):
    result = []
    for maindir, subdir, file_name_list in os.walk(dirname):
        for filename in file_name_list:
            apath = os.path.join(maindir, filename)
            ext = os.path.splitext(apath)[1]
            if ext in postfix:
                result.append(apath)
    return result

