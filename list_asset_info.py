#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: Dango Wang
# time : 2019/3/15

import re


def get_shot_asset(shot_path):
    pattern = re.compile('file[\S\s]*requires maya')
    with open(shot_path, "r") as f:
        data = f.read()
    result = pattern.search(data)
    if not result:
        return None
    result2 = [i for i in result.group().split(" ") if "/" in i]
    final_result = list()
    for k in result2:
        f = [j for j in k.split('"') if "/" in j]
        final_result.extend(f)
    return list(set(final_result))
