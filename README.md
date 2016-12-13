FASTASTIC V1.0.0 README
=======================

**FASTASTIC** is a program that takes a .fastq prokaryotic genome read file and 
automatically runs it through FastQC for quality check of reads and SPAdes 
to be assembled. The resulting FASTA file from SPAdes is then run through 
QUAST to check assembly quality and Prokka to annotate the assembly.

Dependencies
------------
**FASTASTIC** requires the following dependencies:

1.    SPAdes
2.    FastQC
3.    QUAST 
4.    Prokka

By default, **FASTASTIC** will assume the executable (driver) files are located
in the root project directory. If you have the dependencies downloaded
elsewhere, pass the locations of the executables using arguments
`-s`, `-p` and `-q`. 

Usage
-----

1. Ensure that you have Python v3.5
2. Ensure that your input file is .fastq format
3. Run using `python3 fastastic.py` with the appropriate arguments

Check the appropriate parameters using `python3 fastastic.py --help`.

Example
-------

Below is an example use case, utilizing the example test.fastq file provided
in the repository:

~~~~
python3 fastastic.py -s SPAdes-3.8.1-Darwin/bin/spades.py -q quast-4.3/quast.py -p prokka-1.11/bin/prokka test.fastq
~~~~

Contact
-------

For questions regarding the code, please contact the repository owner
