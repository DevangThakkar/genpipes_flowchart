# Automating Flowchart creation for GenPipes pipelines

This project allows for automatic creation of flowcharts whenever a GenPipes pipeline is executed, either partially or wholly. The only requisite for this script to run is a hierarchy file that lists down the relationship between the steps. The format for the hierarchy file is as follows:

The predecessor(s) for each node are described using a certain set of schema. The numbers refer to the steps indicated by the number whereas the term "DATA" refers to external data being used. There are two types of connectors relating the predecessors for a certain node:

 * ",": The node considers exactly one of the mentioned predecessors. 

Example: Step 2:trimmomatic needs exactly one of either (i) the FASTQ files or (ii) the converted FASTQ files from step 1, with (i) preferred over (ii).

* "+": The node needs at least one of the predecessors but considers multiple predecessors, if present.

Example: Step 9:picard_mark_duplicates considers as input, all of the output files created in step 5, 6, and 8 - at least one of them being necessary.

Notes:
* Any line beginning with a hash (#) is considered to be a comment.
* Do not use spaces/tabs between the step number and step name

## Sample from hierarchy_dnaseq.tsv, the linkage document for the dnaseq pipeline:

| Predecessor			|	Node							| Explanation		|
|	----------			|	----------						|	----------		|
| BAM					|	1:picard_sam_to_fastq			|	(1) uses BAM data	|
| FASTQ,1				|	2:trimmomatic					|	(2) uses FASTQ data if available, else (1)	|
| 2						|	3:merge_trimmomatic_stats		|	(3) uses (2)	|
| 3,FASTQ,1				|	4:bwa_mem_picard_sort_sam		|	(4) uses (3) if available, else FASTQ if available, else (1)	|
| 4,BAM					|	5:picard_merge_sam_files		|	(5) uses (4) if available, else BAM	|
| 5						|	6:gatk_indel_realigner			|	(6) uses (5)	|
| 6						|	7:merge_realigned				|	(7) uses (6)	|
| 6						|	8:fix_mate_by_coordinate		|	(8) uses (6)	|
| 5+6+8					|	9:picard_mark_duplicates		|	(9) uses as many of (5), (6), and (8) as available	|


## Usage:

usage: flowchart.py [-h] --steps STEPS --h_file H_FILE [--bam BAM]
                    [--fastq FASTQ]

Creating flowcharts for GenPipe pipeline executions

optional arguments:
  -h, --help       show this help message and exit
  --steps STEPS    step range e.g. "1-5", "3,6,7", "2,4-8"
  --h_file H_FILE  path to hierarchy file for pipeline
  --bam BAM        mention if SAM/BAM data is present in READSET
  --fastq FASTQ    mention if FASTQ is present in READSET