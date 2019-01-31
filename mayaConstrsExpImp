 
#!/usr/bin/env python
 
# -*- coding: utf-8 -*-
 
# author: Dango Wang
 
# time : 2019/1/29
 
 
 
__author__ = "dango wang"
 
"""
maya约束节点的批量导出导入
"""
 
 
import pymel.core as pm
 
import maya.cmds as mc
 
import json
 
import codecs
 
import os
 
import shutil
 
import logging
 
 
 
 
 
def get_all_constr():
 
    """
    返回场景中所有的非引用类别的约束节点，返回list
    """
 
    all_constraints = [constraint for constraint in pm.ls(type="constraint") if not pm.referenceQuery(constraint, inr=1)]
 
    return all_constraints
 
 
 
 
 
def get_parent_transform(node):
 
    """
    返回给定的节点的父节点,返回tuple
    """
 
    return node.name(), pm.listRelatives(node, p=True)[0].name()
 
 
 
 
 
def get_source_constr(constraint_node):
 
    """
    返回约束节点的约束源:类型为list
    """
 
    return pm.PyNode(constraint_node).getTargetList()
 
 
 
 
 
def get_s_connections(constraint_node):
 
    """
    获取所有上游连接，要排出1W0这个节点，因为它是自个儿连自个儿
    """
 
    all_s = pm.listConnections(constraint_node,d=0,s=1,c=1,p=1)
 
    connections_dict = dict()
 
    for each_connection in all_s:
 
        if 'W0' not in each_connection[1].name() and 'W0' not in each_connection[0].name():
 
            connections_dict[each_connection[1].name()] = each_connection[0].name()
 
    return connections_dict
 
 
 
 
 
def get_d_connections(constraint_node):
 
    all_d = pm.listConnections(constraint_node,d=1,s=0,c=1,p=1)
 
    connections_dict = dict()
 
    for each_connection in all_d:
 
        if 'W0' not in each_connection[1].name() and 'W0' not in each_connection[0].name():
 
            connections_dict[each_connection[0].name()] = each_connection[1].name()
 
    return connections_dict
 
 
 
 
 
def get_all_connections(constraint_node):
 
    """
    返回与该约束节点所有有关的连接，返回类型[‘上游连接’：‘被连接体’,...]
    """
 
    connections_dict = dict()
 
    all_s = get_s_connections(constraint_node)
 
    all_d = get_d_connections(constraint_node)
 
    connections_dict.update(all_s)
 
    connections_dict.update(all_d)
 
    return connections_dict
 
 
 
 
 
def remove_anicrv_nodes(connections_dict):
 
    """
    将所有的连接信息中的动画曲线节点排除，因为动画曲线可以跟随约束导出。返回类型dict
    """
 
    if not connections_dict:
 
        return False
 
    new_connections_dict = dict()
 
    anicrv_list = ['animCurveTL', 'animCurveTA', 'animCurveTU']
 
    # print connections_dict
 
    for k, v in connections_dict.items():
 
        # print k, v
 
        if (pm.nodeType(k) in anicrv_list) or (pm.nodeType(v) in anicrv_list):
 
            continue
 
        else:
 
            new_connections_dict[k] = v
 
    if new_connections_dict:
 
        return new_connections_dict
 
    else:
 
        return False
 
 
 
 
 
def break_s_connections(connections_dict):
 
    """
    打断跟约束节点有关的非动画曲线的连接.这里踩了很多坑，直接打断的话约束节点有些属性会丢失，
    只能再创建个节点代替之前的连接跟随约束节点一起导出
    """
 
    if not connections_dict:
 
        return False
 
    new_node = mc.createNode("transform", n="dango_constraints_record_temp_node")
 
    for k, v in connections_dict.items():
 
        try:
 
            # print k,v
 
            s_node_name = k.split(".")[0]
 
            attr = k.split(".")[1]
 
            if not mc.objExists(new_node+'.'+attr):
 
                mc.addAttr(new_node, shortName=attr, longName=attr)
 
            new_k = k.replace(s_node_name, new_node)
 
            print mc.connectAttr(new_k, v, f=1)    
 
            try:        
 
                mc.disconnectAttr(k, v)
 
            except:
 
                pass
 
        except RuntimeError:
 
            continue
 
    return True
 
 
 
 
 
def break_d_connections(connections_dict):
 
    """
    同上
    """
 
    if not connections_dict:
 
        return False
 
    new_node = mc.createNode("transform", n="dango_constraints_record_temp_node")
 
    for k, v in connections_dict.items():
 
        try:
 
            # print k,v
 
            s_node_name = v.split(".")[0]
 
            attr = v.split(".")[1]
 
            if not mc.objExists(new_node+'.'+attr):
 
                mc.addAttr(new_node, shortName=attr, longName=attr)
 
            new_v = v.replace(s_node_name, new_node)
 
            print mc.connectAttr(k, new_v, f=1)            
 
            try:        
 
                mc.disconnectAttr(k, v)
 
            except:
 
                pass
 
        except RuntimeError:
 
            continue
 
    return True
 
 
 
 
 
def add_connections(connections_dict):
 
    """
    重新建立字典中两个节点之间的连接
    """
 
    if not connections_dict:
 
        return False
 
    not_found_connections = list()
 
    for k, v in connections_dict.items():
 
        if not pm.objExists(k):
 
            not_found_connections.append(k)
 
            continue
 
        if not pm.objExists(v):
 
            not_found_connections.append(v)
 
            continue
 
        try:
 
            # print k,v
 
            mc.connectAttr(k, v, f=1)
 
        except RuntimeError:
 
            try:
 
                mc.connectAttr(v, k, f=1)
 
            except RuntimeError:                
 
                # print k, v
 
                continue
 
    if not_found_connections:
 
        return not_found_connections
 
    else:
 
        return False
 
 
 
def get_pos(transform):
 
    translate = mc.getAttr(transform+".t")
 
    rotate = mc.getAttr(transform+".r")
 
    translate.extend(rotate)
 
    return translate
 
 
 
 
 
def get_all_positions(constraint_nodes):
 
    # 获取所有约束相关的物体的位置，在重建约束之前要先把位置打回去
 
    mc.currentTime(101)
 
    all_transforms = list()
 
    all_positions = dict()
 
    all_sources = map(get_source_constr, constraint_nodes)
 
    all_destis = [get_parent_transform(each_info)[1] for each_info in constraint_nodes]
 
    for i in all_sources:
 
        all_transforms.extend(i)
 
    all_transforms = [k.name() for k in all_transforms]
 
    all_transforms.extend(all_destis)
 
    for each_transform in all_transforms:
 
        all_positions[each_transform] = get_pos(each_transform)
 
    return all_positions
 
 
 
 
 
def export_constraints(path):
 
    """
    将场景中所有处理完之后的约束节点导出，同时输出连接及父子信息
    """
 
    # 创建输出文件
 
    parent_info_path = path + '/parent_info.json'
 
    connections_dict_path = path + '/connections_dict.json'
 
    offset_info_path = path + '/offset.json'
 
    constraints_ma = path + '/constraints.ma'
 
    # 获取相关信息
 
    all_constraints = get_all_constr()
 
    if not all_constraints:
 
        return False
 
    parent_info = map(get_parent_transform, all_constraints)
 
    all_connections_info_temp = map(get_all_connections, all_constraints)
 
    all_connections_info = map(remove_anicrv_nodes, all_connections_info_temp)
 
    all_positions_info = get_all_positions(all_constraints)
 
    print all_connections_info
 
    # 打断连接及unparent
 
    # map(break_connections, all_connections_info)
 
    all_s = map(get_s_connections, all_constraints)
 
    all_d = map(get_d_connections, all_constraints)
 
    map(break_s_connections, all_s)
 
    map(break_d_connections, all_d)
 
    # print all_constraints
 
    # 这里有一个坑，如果直接pm.Unparent(all_constraints)的话会提示找不到目标
 
    mc.select(all_constraints, r=True)
 
    if mc.ls(sl=True):
 
        mc.Unparent()
 
    # 写入文件
 
    with codecs.open(parent_info_path, 'w', 'utf-8') as p:
 
        json.dump(parent_info, p)
 
    with codecs.open(connections_dict_path, 'w', 'utf-8') as c:
 
        json.dump(all_connections_info, c)
 
    with codecs.open(offset_info_path, 'w', 'utf-8') as t:
 
        json.dump(all_positions_info, t)
 
    # 导出约束节点
 
    mc.file(constraints_ma, es=1, force=1, typ="mayaAscii", options="v=0;p=17;f=0")
 
    pm.delete(all_constraints)
 
    pm.delete("dango_constraints_record_temp_node*")
 
    logging.info(u'成功导出文件：{}{}{}{}'.format(parent_info_path, connections_dict_path, constraints_ma,offset_info_path))
 
 
 
 
 
def import_constraints(path):
 
    """
    导入所有的约束节点以及连接信息并重新进行连接
    parent_info长这样：[(node,parent),(node,parent),(node,parent),...]
    all_connections_info长这样：[{k:v,k:v,...},{k:v,k:v,...},{k:v,...},...]
    """
 
    # 读入信息
 
    mc.currentTime(101)
 
    parent_info_path = path + '/parent_info.json'
 
    connections_dict_path = path + '/connections_dict.json'
 
    constraints_ma = path + '/constraints.ma'
 
    offset_info_path = path + '/offset.json'
 
    with codecs.open(parent_info_path, 'r', 'utf-8') as p:
 
        parent_info = json.load(p)
 
        # print parent_info
 
    with codecs.open(connections_dict_path, 'r', 'utf-8') as c:
 
        # print type(c)
 
        all_connections_info = json.load(c)
 
    with codecs.open(offset_info_path, 'r', 'utf-8') as t:
 
        all_positions_info = json.load(t)
 
    # 判断一下约束节点的父节点在不在，重新parent
 
    all_parents = [each[1] for each in parent_info]
 
    not_found_parents = [notfound for notfound in all_parents if not pm.objExists(notfound)]
 
    if not_found_parents:
 
        error_info = [error for error in not_found_parents]
 
        logging.error(u'以下节点未找到！请确保文件整理前后命名一致：%s' % error_info)
 
        return 
 
    mc.file(constraints_ma,i=True)
 
    for each_tuple in parent_info:
 
        mc.parent(each_tuple[0], each_tuple[1])
 
    #  将所有约束相关的物体放到原位
 
    for each_obj, each_pos in all_positions_info.items():
 
        # print  each_pos
 
        mc.setAttr(each_obj+".t", each_pos[0][0], each_pos[0][1], each_pos[0][2])
 
        mc.setAttr(each_obj+".r", each_pos[1][0], each_pos[1][1], each_pos[1][2])
 
    # 增加连接，找不到的连接节点将被返回
 
    connections = map(add_connections, all_connections_info)
 
    # print connections
 
    error_connections = list()
 
    for each_connect in connections:
 
        if each_connect:
 
            error_connections.extend(each_connect)
 
    if error_connections:
 
        error_info2 = [error2 for error2 in error_connections]
 
        logging.error(u'以下节点未找到！请确保文件整理前后命名一致：%s' % error_info2)
 
        return False
 
    # if mc.objExists("dango_constraints_record_temp_node*"):
 
    #     mc.delete("dango_constraints_record_temp_node*")
 
    return True
 
 
 
 
 
if __name__ == '__main__':
 
    # 导出场景中所有的约束节点和相关信息
 
    export_constraints("D:/dango_repo/constraint_exp_imp/test")
 
    # 导入所有的约束节点和重建相关连接
 
    import_constraints("D:/dango_repo/constraint_exp_imp/test")
 
 
 
    # 删除临时节点（直接写在import_constraints中的话不成功，可能因为map执行效率低导致）：
 
    if mc.objExists("dango_constraints_record_temp_node*"):
 
         mc.delete("dango_constraints_record_temp_node*")
 
 
 
     # 删除导出的文件（将整个文件夹删除）
 
     shutil.rmtree("D:/dango_repo/constraint_exp_imp/test")
