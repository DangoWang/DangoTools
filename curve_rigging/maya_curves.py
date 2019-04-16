#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: Dango Wang
# time : 2019/3/6


cross_crv = 'curve -n {jnt_control} -d 1 -p 0.365446 0 -1.737246 -p 0 0 -1.979341 -p -0.365446 0 -1.737246 ' \
            '-p 0 0 -3.272918 -p 0.365446 0 -1.737246 -p 0 0 -1.979341 -p 0 0.365446 -1.737246 ' \
            '-p 0 0 -3.272918 -p 0 -0.365446 -1.737246 -p 0 0 -1.979341 -p 0 0 0 -p 0 0 1.979341 ' \
            '-p -0.365446 0 1.737246 -p 0 0 3.272918 -p 0.365446 0 1.737246 -p 0 0 1.979341 ' \
            '-p 0 -0.365446 1.737246 -p 0 0 3.272918 -p 0 0.365446 1.737246 -p 0 0 1.979341 ' \
            '-p 0 0 0 -p 1.979341 0 0 -p 1.737246 0 0.365446 -p 3.272918 0 0 -p 1.737246 0 -0.365446 ' \
            '-p 1.979341 0 0 -p 1.737246 0.365446 0 -p 3.272918 0 0 -p 1.737246 -0.365446 0 -p 1.979341 0 0 ' \
            '-p 0 0 0 -p -1.979341 0 0 -p -1.737246 0 0.365446 -p -3.272918 0 0 -p -1.737246 0 -0.365446 ' \
            '-p -1.979341 0 0 -p -1.737246 0.365446 0 -p -3.272918 0 0 -p -1.737246 -0.365446 0 ' \
            '-p -1.979341 0 0 -p 0 0 0 -p 0 1.979341 0 -p -0.365446 1.737246 0 -p 0 3.272918 0 ' \
            '-p 0.365446 1.737246 0 -p 0 1.979341 0 -p 0 1.737246 0.365446 -p 0 3.272918 0 -p 0 1.737246 -0.365446 ' \
            '-p 0 1.979341 0 -p 0 0 0 -p 0 -1.979341 0 -p -0.365446 -1.737246 0 -p 0 -3.272918 0 ' \
            '-p 0.365446 -1.737246 0 -p 0 -1.979341 0 -p 0 -1.737246 -0.365446 -p 0 -3.272918 0 ' \
            '-p 0 -1.737246 0.365446 -p 0 -1.979341 0 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 ' \
            '-k 10 -k 11 -k 12 -k 13 -k 14 -k 15 -k 16 -k 17 -k 18 -k 19 -k 20 -k 21 -k 22 -k 23 -k 24 ' \
            '-k 25 -k 26 -k 27 -k 28 -k 29 -k 30 -k 31 -k 32 -k 33 -k 34 -k 35 -k 36 -k 37 -k 38 -k 39 -k 40 ' \
            '-k 41 -k 42 -k 43 -k 44 -k 45 -k 46 -k 47 -k 48 -k 49 -k 50 -k 51 -k 52 -k 53 -k 54 -k 55 -k 56 ' \
            '-k 57 -k 58 -k 59;'

master_crv = 'circle -n "GeneralCtrl01" -ch on -o on -nr 0 1 0 -r 10 ;\
            curve -d 1 -p -1 0 11 -p 1 0 11 -p 1 0 13 -p 2 0 13 -p 0 0 15 \
            -p -2 0 13 -p -1 0 13 -p -1 0 11 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 ;\
            rename "GeneralCtrl02";\
            duplicate -n "GeneralCtrl03";\
            rotate 0 90 0;\
            makeIdentity -apply true -t 1 -r 1 -s 1 -n 0;\
            duplicate -rr -n "GeneralCtrl04";\
            rotate 0 90 0;\
            makeIdentity -apply true -t 1 -r 1 -s 1 -n 0;\
            duplicate -rr -n "GeneralCtrl05";\
            rotate 0 90 0;\
            makeIdentity -apply true -t 1 -r 1 -s 1 -n 0;\
            parent -r -s "GeneralCtrl0Shape2" "GeneralCtrl0Shape3" "GeneralCtrl0Shape4" \
                         "GeneralCtrl0Shape5" "GeneralCtrl01";\
            delete "GeneralCtrl02" "GeneralCtrl03" "GeneralCtrl04" "GeneralCtrl05";\
            select "GeneralCtrl01";\
            makeIdentity -apply true -t 1 -r 1 -s 1 -n 0;\
            delete -ch;\
            rename "{master_crv_name}";\
            scale -r 0.5 0.5 0.5;\
            makeIdentity -apply true -t 0 -r 0 -s 1 -n 0;\
            xform -os -piv 0 0 0;'

main_crv = 'circle -n {main_crv_name} -c 0 0 0 -nr 0 1 0 -sw 360 -r 3 -d 3 -ut 0 -tol 0.01 -s 8 -ch 0;'
