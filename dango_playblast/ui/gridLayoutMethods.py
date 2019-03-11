#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: Dango Wang
# time : 2019/1/8

__author__ = 'Dango Wang'
__doc__ = 'Building a layout to arrange hud info'

# from PySide2 import QtWidgets
# def add_hud_unit(grid_layout, label, value, *pos):
# 	"""
# 	add unit(with a QLabel label and a QLabel value)to this grid
# 	:param pos:x, y
# 	:param label:QLabel
# 	:param value:QLabel
# 	:return:two QLabels
# 	"""
# 	i, j = pos
# 	grid_layout.addWidget(label, i, j)
# 	grid_layout.addWidget(value, i+1, j)
# 	return grid_layout.itemAtPosition(i, j).widget(), grid_layout.itemAtPosition(i+1, j).widget()


def delete_hud_unit(grid_layout, pos):
	try:
		widget = grid_layout.itemAtPosition(pos[0], pos[1]).widget()
		widget.setText("")
		widget.setStyleSheet("")
		grid_layout.removeWidget(widget)
		print pos
		return pos
	except AttributeError:
		return False


def all_units(grid_layout):
	"""
	list all existed units
	:return:all units
	"""
	# margin = grid_layout.getContentsMargins()
	# layout_size = grid_layout.geometry().getRect()
	# size_temp = list()
	# for i in range(2, 4):
	# 	j = layout_size[i] - margin[i]
	# 	size_temp.append(j)
	# h1 = grid_layout.itemAtPosition(1, 0).widget().geometry().getRect()[1]
	# h2 = grid_layout.itemAtPosition(11, 1).widget().geometry().getRect()[1]
	# w1 = grid_layout.itemAtPosition(0, 1).widget().geometry().getRect()[0]
	# w2 = grid_layout.itemAtPosition(1, 11).widget().geometry().getRect()[0]
	parent = grid_layout.parent()
	w = parent.geometry().getRect()[2]
	h = parent.geometry().getRect()[3]
	size = [float(w), float(h)]
	# print size
	# print "hi"
	pos = [(i, j) for i in range(1, 11) for j in range(1, 11)]
	# print pos
	all_units = list()
	for each_pos in pos:
		try:
			widget = grid_layout.itemAtPosition(each_pos[0], each_pos[1]).widget()
			geometry = widget.geometry().getRect()
			# print size
			percent_x = geometry[0]/size[0]
			percent_y = geometry[1]/size[1]
			all_units.extend([(widget, each_pos, (percent_x, percent_y))])
			# print percent_x, percent_y
		except AttributeError:
			continue
	return all_units


def get_pos_with_margin(pos_tuple, pos_tuple2, w1, w2, h1, h2, margin, gap):
	"""
	:param pos_tuple: (block, section)
	:param pos_tuple2: (433, 255)
	:param w1:
	:param w2:
	:param h1:
	:param h2:
	:param margin:
	:return:
	"""
	import math
	tuple_temp0 = pos_tuple2[0]
	tuple_temp1 = pos_tuple2[1]
	if pos_tuple[1] < 5:
		tuple_temp0 = pos_tuple2[0] - (w1 * margin)
	elif pos_tuple[1] > 6:
		tuple_temp0 = pos_tuple2[0] + (w2 * margin*1.5)
	if pos_tuple[0] < 5:
		h_temp = math.pow(pos_tuple[0], 1/(margin*2-0.2))
		tuple_temp1 = pos_tuple2[1] - (h1 * margin * h_temp)
	elif pos_tuple[0] > 5:
		h_temp1 = math.pow(11-pos_tuple[0], 1/(margin*2-0.2))
		tuple_temp1 = pos_tuple2[1] + (h2 * margin * h_temp1) + h2*0.7
	if pos_tuple[1] % 2 == 0:
		if pos_tuple[1] < 7:
			tuple_temp0 = tuple_temp0 - w1 * gap
	else:
		if pos_tuple[1] > 6:
			tuple_temp0 = tuple_temp0 + w1 * gap
	final_pos = (tuple_temp0, tuple_temp1)
	return final_pos


def all_units_with_margin(grid_layout, margin, gap):
	h1 = grid_layout.itemAtPosition(0, 1).widget().geometry().getRect()[3]
	h2 = grid_layout.itemAtPosition(11, 1).widget().geometry().getRect()[3]
	w1 = grid_layout.itemAtPosition(1, 0).widget().geometry().getRect()[2]
	w2 = grid_layout.itemAtPosition(1, 11).widget().geometry().getRect()[2]
	parent = grid_layout.parent()
	w = parent.geometry().getRect()[2]
	h = parent.geometry().getRect()[3]
	size = [float(w), float(h)]
	# print size
	# print "hi"
	pos = [(i, j) for i in range(1, 11) for j in range(1, 11)]
	# print pos
	all_units = list()
	for each_pos in pos:
		try:
			widget = grid_layout.itemAtPosition(each_pos[0], each_pos[1]).widget()
			geometry = widget.geometry().getRect()
			# print size
			final_pos = get_pos_with_margin(each_pos, (geometry[0], geometry[1]), w1, w2, h1, h2, margin, gap)
			percent_x = final_pos[0] / size[0]
			percent_y = final_pos[1] / size[1]
			all_units.extend([(widget, each_pos, (percent_x, percent_y))])
		# print percent_x, percent_y
		except AttributeError:
			continue
	return all_units


def all_labels(grid_layout):
	"""
	:return:all labels
	"""
	pos = [(i, j) for i in range(1, 11) for j in range(1, 11, 2)]
	# print pos
	all_labels = list()
	for each_pos in pos:
		try:
			all_labels.extend([grid_layout.itemAtPosition(each_pos[0], each_pos[1]).widget()])
		except AttributeError:
			continue
	# print all_labels
	return all_labels
	# return pos


def all_values(grid_layout):
	"""
	:return:all labels
	"""
	pos = [(i, j) for i in range(1, 11) for j in range(2, 11, 2)]
	# print pos
	all_values = list()
	for each_pos in pos:
		try:
			all_values.extend([grid_layout.itemAtPosition(each_pos[0], each_pos[1]).widget()])
		except AttributeError:
			# print 1
			continue
	return all_values


def find_unit(grid_layout, pos):
	try:
		widget = grid_layout.itemAtPosition(pos[0], pos[1]).widget()
	except AttributeError:
		return False
	return widget


def clear_all_units(grid_layout):
	pos = [(i, j) for i in range(1, 11) for j in range(1, 11)]
	for each in pos:
		try:
			widget = grid_layout.itemAtPosition(each[0], each[1]).widget()
			widget.setText("")
			widget.setStyleSheet("")
			grid_layout.removeWidget(widget)
		except AttributeError:
			continue
	return True
