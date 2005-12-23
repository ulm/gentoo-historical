"""
# Copyright 1999-2005 Gentoo Foundation
# This source code is distributed under the terms of version 2 of the GNU
# General Public License as published by the Free Software Foundation, a copy
# of which can be found in the main directory of this project.
Gentoo Linux Installer

$Id: GLIPortage.py,v 1.1 2005/12/23 21:14:08 agaffney Exp $
"""

import os
import GLIUtility

class MissingPackagesError(Exception):
	pass

class depgraph:

	def __init__(self):
		self.graph = {}
	
	def add(self, node, parent=None):
		if node not in self.graph:
			self.graph[node] = [[], []]
		if parent and parent not in self.graph[node][0]:
			if parent not in self.graph:
				self.graph[parent] = [[], []]
			self.graph[node][0].append(parent)
			self.graph[parent][1].append(node)

	def remove(self, node):
		for parent in self.graph[node][0]:
			self.graph[parent][1].remove(node)
		for child in self.graph[node][1]:
			self.graph[child][0].remove(node)
		return self.graph.pop(node)
	
	def has_node(self, node):
		return node in self.graph
	
	def leaf_nodes(self):
		return [node for node in self.graph if not self.graph[node][1]]
	
	def node_count(self):
		return len(self.graph)
	
	def important_node(self):
		important_node = None
		importance = 0
		for node in self.graph:
			if len(self.graph[node][0]) > importance:
				importance = len(self.graph[node][0])
				important_node = node
		return important_node

class GLIPortage(object):

	def __init__(self, chroot_dir):
		os.environ['ROOT'] = chroot_dir
		import portage, portage_dep
		self.vdb = portage.db["/"]["vartree"].dbapi
		self.chroot_dir = chroot_dir

	def resolve_deps(self, dep_list):
		if dep_list and dep_list[0] == "||":
			for dep in dep_list[1:]:
				if isinstance(dep, list):
					try:
						atoms = resolve_deps(dep)
					except MissingPackagesError:
						continue
				else:
					atoms = [dep]
				all_found = True
				for atom in atoms:
					if not atom.startswith("!") and not self.vdb.match(atom):
						all_found = False
						break
				if all_found:
					return atoms
			raise MissingPackagesError(dep_list)
		atoms = []
		for dep in dep_list:
			if isinstance(dep, list):
				atoms.extend(resolve_deps(dep))
			elif not dep.startswith("!"):
				if not self.vdb.match(dep):
					raise MissingPackagesError([dep])
				atoms.append(dep)
		return atoms

	def calc_required_pkgs(self, atom, graph, parent=None):
		pkg = portage.best(self.vdb.match(atom))
		if not pkg:
			raise MissingPackagesError([atom])
		if pkg == parent:
			return
		already_processed = graph.has_node(pkg)
		graph.add(pkg, parent)
		if already_processed:
			return
		useflags = self.vdb.aux_get(pkg, ["USE"])[0].split()
		rdep_raw = " ".join(self.vdb.aux_get(pkg, ["RDEPEND", "PDEPEND"]))
		rdep_struct = portage_dep.use_reduce(portage_dep.paren_reduce(rdep_raw), uselist=useflags)
		rdep_struct = portage.dep_virtual(portage_dep.dep_opconvert(rdep_struct), portage.settings)
		rdep_atoms = portage.unique_array(resolve_deps(rdep_struct))
		for atom in rdep_atoms:
			calc_required_pkgs(atom, graph, pkg)

	def prune_existing(self, graph):
		db = portage.db[portage.root]["vartree"].dbapi
		for atom in db.cp_all():
			for pkg in db.match(atom):
				if graph.has_node(pkg):
					graph.remove(pkg)

	def get_deps(self, pkgs, grp_install):
		if not grp_install:
			del(os.environ['ROOT'])
			return GLIUtility.spawn("emerge -p " + pkgs + r" | grep -e '^\[[a-z]' | cut -d ']' -f2 | sed -e 's:^ ::' -e 's: .\+$::'", chroot=self.chroot_dir, return_output=True)[1].split("\n")
			os.environ['ROOT'] = self.chroot_dir
		else:
			pkglist = []
			graph = depgraph()
			for pkg in pkgs.split():
				if not self.vdb.match(pkg):
					continue
				self.calc_required_pkgs(pkg, graph)
			while graph.node_count():
				leaf_nodes = graph.leaf_nodes()
				if not leaf_nodes:
					node = graph.important_node()
					pkglist.append(node)
					graph.remove(node)
					continue
				pkglist.extend(leaf_nodes)
				for node in leaf_nodes:
					graph.remove(node)
			return pkglist
