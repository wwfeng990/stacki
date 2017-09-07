# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@
#
# @Copyright@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @Copyright@

import sys
import socket
import stack.commands
import string
from stack.exception import *

class Command(stack.commands.remove.host.command):
	"""
	Remove a partition definitions from a host.

	<arg type='string' name='host' repeat='1'>
	A list of one or more host names.
	</arg>

	<param type='string' name='partition'>
	A single partition to remove from this host. If no partition is
	specified, then all partitions from the host are removed.
	</param>

	<param name="device" type="string">
	Device name to be removed
	</param>

	<param name="uuid" type="string">
	UUID of the mountpoint to be removed.
	</param>

	<example cmd='remove host partition compute-0-0'>
	Remove all partitions from compute-0-0.
	</example>

	<example cmd='remove host partition compute-0-0 partition=/export'>
	Remove only the /export partition from compute-0-0.
	</example>

	<example cmd='remove host partition compute-0-0 device=sdb1'>
	Remove only the partition information for /dev/sdb1 on compute-0-0
	</example>
	"""

	def run(self, params, args):
		
		if not len(args):
			raise ArgRequired(self, 'host')
			
		(partition, device, uuid) = self.fillParams([
			('partition', None),
			('device', None),
			('uuid', None)])
			
		for host in self.getHostnames(args):
			conditions = []
			sql_cmd = """delete from partitions where
				node=(select id from nodes
				where name='%s')""" % host
			if uuid:
				conditions.append("uuid='%s'" % uuid)
			if partition:
				conditions.append("mountpoint='%s'" % partition)
			if device:
				conditions.append("device='%s'" % device)
			c = ' and '.join(conditions)
			if c:
				sql_cmd = "%s and %s" % (sql_cmd, c)

			self.db.execute(sql_cmd)