#! /opt/stack/bin/python
# 
# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@

def str2bool(s):
	"""Converts an on/off, yes/no, true/false string to
	True/False."""
	if type(s) == bool:
		return s
	if s and s.upper() in [ 'ON', 'YES', 'Y', 'TRUE', '1' ]:
		return True
	else:
		return False

def bool2str(b):
	"""Converts an 1/0 to a yes/no"""
	if type(b) in [ bool, int ]:
                if b:
                        return 'yes'
                else:
                        return 'no'
	return None