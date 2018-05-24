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
import argparse
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

    def __init__(self, steps, hierarchy_file_name, if_bam, if_fastq):
        """
        Parameters
        ----------
        steps: string
            Steps of the pipeline being run
        hierarchy_file_name: string
            Path to hierarchy_file
        if_bam: boolean
            Stores if READSET has BAM data or not
        if_fastq: boolean
            Stores if READSET has FASTQ data or not

        Modifies
        ----------
        self.if_bam: boolean
            Stores if READSET has BAM data or not
        self.if_fastq: boolean
            Stores if READSET has FASTQ data or not
        """

        self.if_bam = if_bam
        self.if_fastq = if_fastq

        self.parse_hierarchy(hierarchy_file_name)
        self.parse_steps(steps)
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
        self.steps: string
            String passed to the function
        self.step_list: list
            List of steps being executed
        """

        if steps == "":
            print("Error: STEPS can not be empty. Please try again.")
            sys.exit(0)
        self.steps = steps
        self.step_list = []

        comma_delimited_steps = steps.strip().split(",")
        for step in comma_delimited_steps:
            if "-" in step:
                low = step.strip().split("-")[0]
                high = step.strip().split("-")[1]

                # if either of high or low is empty -> negative integer, exit
                if low == "" or high == "":
                    print("Error: The steps entered seem to be incorrect.")
                    sys.exit(0)

                low = int(low)
                high = int(high)

                # if there's a zero, exit
                if low <= 0:
                    print("Error: steps start from 1, not 0.")
                    sys.exit(0)

                for i in range(low, high + 1):
                    self.step_list.append(str(i))
            else:
                # if there's a zero, exit
                if int(step.strip()) <= 0:
                    print("Error: steps start from 1, not 0.")
                    sys.exit(0)

                self.step_list.append(step.strip())

        # sort elements of step as if they were integers
        def natural_key(string_):
            return [int(s) if s.isdigit() else s
                    for s in re.split(r"(\d+)", string_)]

        self.step_list = list(set(self.step_list))

        self.step_list.sort(key=natural_key)

        # ensure all steps in STEP are <= self.max_step
        if int(self.step_list[len(self.step_list)-1]) > self.max_step:
            print("Error: You're trying to access a step which doesn't exist.")
            sys.exit(0)

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
        self.hierarchy_file: string
            Stores the path to the hierarchy_file
        self.max_step: int
            Stores the id of the final step in the pipeline
        """

        self.links = dict()
        self.name_list = []
        self.hierarchy_file = hierarchy_file_name
        self.max_step = 1

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

                    # identify the final step
                    if int(step_number) > self.max_step:
                        self.max_step = int(step_number)

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

        # add BAM/FASTQ to the copy of list of steps to account for top nodes
        if self.if_bam:
            temp_list.append("BAM")
        if self.if_fastq:
            temp_list.append("FASTQ")

        for step in temp_list:
            # ignore the validation for dummy values BAM and FASTQ
            if step == "BAM" or step == "FASTQ":
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

        # if graph is erroneous, create dummy file and exit
        if not verity:

            # create a graph using Graphviz
            dot = Digraph(comment="Flowchart",
                          node_attr={"shape": "plaintext"})

            # add error node
            dot.node("0", "Graph not created: some nodes don't have a source")

            try:
                # create folder if not exists
                dir_name = "flowcharts/"
                if not os.path.exists(dir_name):
                    os.makedirs(dir_name)

                if self.if_bam and self.if_fastq:
                    dot.render(dir_name + self.hierarchy_file + "-" +
                               self.steps + ".bam.fastq.error")

                if self.if_bam and not self.if_fastq:
                    dot.render(dir_name + self.hierarchy_file + "-" +
                               self.steps + ".bam.error")

                if not self.if_bam and self.if_fastq:
                    dot.render(dir_name + self.hierarchy_file + "-" +
                               self.steps + ".fastq.error")
            except Exception as inst:

                # raise exception if file is open and can not be modified
                print("The target file seems to be open already. Please" +
                      " close the file before proceeding.")

            return

        # store all the nodes that have been added so far
        added_nodes = []

        # store all the edges that have been added so far
        added_tuples = []

        # creating a copy of self.step_list with BAM/FASTQ in it
        temp_list = self.step_list[:]

        # hard code the BAM, FASTQ node if present
        if self.if_bam:
            added_nodes.append("BAM")
            temp_list.append("BAM")
        if self.if_fastq:
            added_nodes.append("FASTQ")
            temp_list.append("FASTQ")

        for step in temp_list:
            if step == "BAM" or step == "FASTQ":
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
        dot = Digraph(comment="Flowchart", node_attr={"shape": "rectangle"})

        # add nodes
        for i in added_nodes:
            if i == "BAM":
                dot.node(i, "BAM")
            if i == "FASTQ":
                dot.node(i, "FASTQ")
            if i != "BAM" and i != "FASTQ":
                dot.node(i, i + ":" + self.name_list[int(i) - 1])

        # add edges
        for (i, j) in added_tuples:
            dot.edge(i, j)

        dot.edge_attr.update(arrowhead="normal")

        try:
            # create folder if not exists
            dir_name = "flowcharts/"
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)

            # save graph
            if self.if_bam and self.if_fastq:
                dot.render(dir_name + self.hierarchy_file + "-" + self.steps +
                           ".bam.fastq.flow")

            if self.if_bam and not self.if_fastq:
                dot.render(dir_name + self.hierarchy_file + "-" + self.steps +
                           ".bam.flow")

            if not self.if_bam and self.if_fastq:
                dot.render(dir_name + self.hierarchy_file + "-" + self.steps +
                           ".fastq.flow")

        except Exception as inst:
            # raise exception if file is open and can not be modified
            print("The target file seems to be open already. Please" +
                  " close the file before proceeding.")


if __name__ == "__main__":

    # description of parser
    desc_string = "Creating flowcharts for GenPipe pipeline executions"
    parser = argparse.ArgumentParser(description=desc_string)

    # add compulsory argument steps
    parser.add_argument("--steps", nargs=1, required=True,
                        help="step range e.g. \"1-5\", \"3,6,7\", \"2,4-8\"")

    # add compulsory argument hierarchy file
    parser.add_argument("--h_file", nargs=1, required=True,
                        help="path to hierarchy file for pipeline")

    # function to accept and convert values for --bam and --fastq
    def str2bool(v):
        if v.lower() in ("yes", "true", "t", "y", "1"):
            return True
        elif v.lower() in ("no", "false", "f", "n", "0"):
            return False
        else:
            raise argparse.ArgumentTypeError("Boolean value expected.")

    # add optional argument bam
    parser.add_argument("--bam", type=str2bool, nargs=1, default=True,
                        help="mention if SAM/BAM data is present in READSET")

    # add optional argument fastq
    parser.add_argument("--fastq", type=str2bool, nargs=1, default=True,
                        help="mention if FASTQ is present in READSET")

    args = parser.parse_args()

    # convert args to usable format
    steps = repr(args.steps).replace("['", "").replace("']", "")
    h_file = repr(args.h_file).replace("['", "").replace("']", "")
    bam = repr(args.bam).replace("[", "").replace("]", "")
    fastq = repr(args.fastq).replace("[", "").replace("]", "")
    bam = True if bam == "True" else False
    fastq = True if fastq == "True" else False

    # start the program logic
    FlowChart(steps, h_file, bam, fastq)
