# MIT License
# Copyright (c) 2018 Devang Thakkar
# https://home.iitb.ac.in/~devangthakkar
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# PEP-8 format: Limit all lines to a maximum of 79 characters ----------------|

# Python Standard Modules
import os
import re
import sys

# Import Graphviz
from graphviz import Digraph


class FlowChart():
	"""
	This FlowChart class helps create user-friendly flow charts when a
	pipeline is executed (either in its entirety or partially). This script
	needs the user to select steps that are linked to each other; in other
	words, a step can not be executed unless its predecessor is executed.

	Requirements:

	- a hierarchy file, specifying the predecessor(s) for each node. The
	format for the hierarchy file is specified in the sample hierarchy file.

	- steps, specified in the execution of the pipeline.

	"""

	def __init__(self, steps, hierarchy_file_name):
		self.parse_steps(steps)
		self.parse_hierarchy(hierarchy_file_name)
		self.create_flowchart(self.check_validity())

	def parse_steps(self, steps):
		"""
		This functions parses the steps selected when a pipeline is executed
		into a list.

		Example:

		"1-4" becomes [1,2,3,4]
		"1,2,3,4" becomes [1,2,3,4]
		"1,3-5,7" becomes [1,3,4,5,7]

		Parameters
		----------
		steps: string
			String describing the steps being executed

		Modifies
		----------
		self.step_list: list
			List of steps being executed
		"""

		self.steps = steps
		self.step_list = []
		comma_delimited_steps = steps.strip().split(",")
		for step in comma_delimited_steps:
			if "-" in step:
				low = int(step.strip().split("-")[0])
				high = int(step.strip().split("-")[1])
				for i in range(low, high + 1):
					self.step_list.append(str(i))
			else:
				self.step_list.append(step.strip())

		# sort elements of step as if they were integers
		def natural_key(string_):
			return [int(s) if s.isdigit() else s
					for s in re.split(r'(\d+)', string_)]

		self.step_list = list(set(self.step_list))

		self.step_list.sort(key=natural_key)

	def parse_hierarchy(self, hierarchy_file_name):
		"""
		This function parses the hierarchy file in order to identify the
		relation between nodes.

		Parameters
		----------
		hierarchy_file_name: path
			Name of file containing the relations between nodes

		Modifies
		----------
		self.links: dict
			Dictionary of links between steps
		self.name_list: list
			List of names of steps

		"""
		self.links = dict()
		self.name_list = []
		self.hierarchy_file = hierarchy_file_name

		with open(hierarchy_file_name, "r") as f:
			for line in f:

				# ignoring commented lines
				if line[0] != "#":

					# replacing multiple intercolumnar tabs by a single tab
					line = "\t".join(line.split())
					splitted = line.split("\t")

					predecessor_term = splitted[0]
					step_term = splitted[1]
					step_number = step_term.split(":")[0]
					step_name = step_term.split(":")[1]
					self.name_list.append(step_name)
					self.links[step_number] = predecessor_term

	def check_validity(self):
		"""
		This function checks if the steps inputted are continuous or not. The
		flowchart is created only if the steps are interconnected.

		Parameters
		----------

		Modifies
		----------

		"""
		# make a copy of the list of steps
		temp_list = self.step_list[:]

		# add data to the copy of list of steps to account for top nodes
		temp_list.append("DATA")

		for step in temp_list:
			# ignore the validation for dummy value "DATA"
			if step == "DATA":
				continue

			# pred = predecessor(s) of step
			pred = self.links[step]

			# if step has only one predecessor
			if "," not in pred and "+" not in pred:
				if pred not in temp_list:
					return False

			else:
				# if pred has multiple predecessors
				separator_list = [",", "+"]
				for separator in separator_list:
					if separator in pred:
						pred_list = pred.strip().split(separator)

						# initialize flag to false, set flag to true if any
						# one of the mandated predecessors exists in the list
						flag = False
						for item in pred_list:
							if item in temp_list:
								flag = True

						if not flag:
							return False

		return True

	def create_flowchart(self, verity):
		"""
		This function uses the consecution module and builds a flowchart of
		the steps involved in the process.

		Parameters
		----------
		verity: boolean
			Indicates whether a connected pipeline can be made or not

		Modifies
		----------

		"""

		# if graph is disconnected, create dummy file and exit
		if not verity:

			# create a graph using Graphviz
			dot = Digraph(comment='Flowchart', node_attr={'shape': 'plaintext'})

			# add error node
			dot.node("0", "Graph not created as some nodes are disconnected")

			try:
				# create folder if not exists
				dir_name = "flowcharts/"
				if not os.path.exists(dir_name):
					os.makedirs(dir_name)

				# save graph
				dot.render(dir_name + self.hierarchy_file + "-" + self.steps +
							".error")
			except Exception as inst:
				# raise exception if file is open and can not be modified
				print("The target file seems to be open already. Please" +
						" close the file before proceeding.")

			return

		# store all the nodes that have been added so far
		added_nodes = []

		# store all the edges that have been added so far
		added_tuples = []

		# hard code the "DATA" node
		data_name = "DATA"
		added_nodes.append(data_name)

		# creating a copy of self.step_list with "DATA" in it
		temp_list = self.step_list[:]
		temp_list.append(data_name)

		for step in temp_list:
			if step == data_name:
				continue

			# if step has only one predecessor
			if "," not in self.links[step] and "+" not in self.links[step]:

				# if step is not added, add a node for step
				if step not in added_nodes:
					added_nodes.append(step)

				# if link[step] is not added, add a node for link[step]
				if self.links[step] not in added_nodes:
					added_nodes.append(self.links[step])

				added_tuples.append((self.links[step], step))

			# if step has multiple predecessors of which one has to be chosen
			if "," in self.links[step]:

				# if step is not added, add a node for step
				if step not in added_nodes:
					added_nodes.append(step)

				pred_list = self.links[step].strip().split(",")
				for item in pred_list:

					# if there actually exists a link between this predecessor
					# and step, proceed
					if item in temp_list:

						added_tuples.append((item, step))

						# if item is not added, add a node for item
						if item not in added_nodes:
							added_nodes.append(item)

						# since only one link needs to considered, break
						break

			# if step has multiple predecessors of which all can chosen
			if "+" in self.links[step]:

				# if step is not added, add a node for step
				if step not in added_nodes:
					added_nodes.append(step)

				pred_list = self.links[step].strip().split("+")
				for item in pred_list:

					# if there actually exists a link between this predecessor
					# and step, proceed
					if item in temp_list:

						added_tuples.append((item, step))

						# if item is not added, add a node for item
						if item not in added_nodes:
							added_nodes.append(item)

		# create a graph using Graphviz
		dot = Digraph(comment='Flowchart', node_attr={'shape': 'rectangle'})

		# add nodes
		for i in added_nodes:
			if i == "DATA":
				dot.node(i, "READSET DATA")
			else:
				dot.node(i, i + ":" + self.name_list[int(i)-1])

		# add edges
		for (i, j) in added_tuples:
			dot.edge(i, j)

		dot.edge_attr.update(arrowhead='normal')

		try:
			# create folder if not exists
			dir_name = "flowcharts/"
			if not os.path.exists(dir_name):
				os.makedirs(dir_name)

			# save graph
			dot.render(dir_name + self.hierarchy_file + "-" + self.steps +
						".txt")
		except Exception as inst:
			# raise exception if file is open and can not be modified
			print("The target file seems to be open already. Please" +
					" close the file before proceeding.")


if __name__ == "__main__":
	FlowChart("5-10,17-20", "hierarchy_dnaseq.tsv")