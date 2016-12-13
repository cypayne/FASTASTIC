'''
############################## FASTASTIC V1.0.0 ##############################

FASTASTIC is a script that takes a .fastq file of prokaryotic genome reads and 
automatically runs it through FastQC for quality check and SPAdes to be 
assembled. The resulting FASTA file from SPAdes is then run through QUAST 
to check assembly quality and Prokka to annotate the assembly.

Before running script:
 - Download the following into your working directory:
      SPAdes
      FastQC
      QUAST 
      Prokka
 - Ensure that your input file is .fastq format
 - Ensure that you have Python v3.5

To run:

    python3 fastastic.py --fq1 <input_file_1>
        
        (must set correct paths to each tool used)

#############################################################################
'''

import argparse
import subprocess, os

def fastq_check(path):
    ''' Checks that file type is .fastq '''
    if not path.lower().endswith('.fastq') and not path.lower().endswith('.fq'):
        raise argparse.ArgumentTypeError('Only .fastq or .fq input files allowed')

''' 
Function that renames contigs in SPAdes contigs.fasta output file so that
they are <= 20 characters long (so they are compatible with Prokka) 
--> PROVIDED BY NIEMA MOSHIRI
'''
def rename_contigs(contig_file):
    ''' Rewrites the contigs file to have shorter header names, and returns
        a dictionary mapping new names to old names '''
    name_map = {}

    # Strip the directory info from the contigs.fasta path
    contigs_dir = contig_file[:-len('contigs.fasta')]
    new_contig_file = contigs_dir + 'contigs_short.fasta'

    print('FASTASTIC: Renaming headers in old file ({}) to new file ({})'.format(contig_file, new_contig_file))

    with open(contig_file, 'r') as fin, open(new_contig_file, 'w') as fout:
        for line in fin:
            if line[0] == '>':
                new_name = 'contig{}'.format(len(name_map))
                name_map[new_name] = line[1:]
                # modify the header with a shorter name
                fout.write('>{}\n'.format(new_name))
            else:
                fout.write(line)

    return name_map

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    # Non-optional arguments
    # parser.add_argument('spades_input',
    parser.add_argument('-fq1','--spades_input',
                        required=True,
                        help='input file')

    # Optional arguments
    parser.add_argument('-fq2', '--fastq2',
                        default=None,
                        help='second input file')
                        
    parser.add_argument('-r', '--ref',
                        default=False,
                        action='store',
                        dest='ref')
    parser.add_argument('-s', '--spades',
                        help='path to spades.py',
                        default='./spades.py', # defaults to local file
                        action='store', 
                        dest='spades_path')
    parser.add_argument('-q', '--quast',
                        help='path to quast.py',
                        default='./quast.py', # defaults to local file
                        action='store', 
                        dest='quast_path')
    parser.add_argument('-p', '--prokka',
                        help='path to prokka executable',
                        default='./prokka', # defaults to local file
                        action='store', 
                        dest='prokka_path')
    parser.add_argument('--verbose',
                        help='displays stdout of external commands',
                        action='store_true')
    
    
    args = parser.parse_args()
    
    # Check to make sure user provided fastiq file
    path = './' + args.spades_input
    fastq_check(path)

    # Create folders in current directory for FASTASTIC ouptput files
    dirs = ['', '/FastQC', '/SPAdes', '/QUAST', '/Prokka']
    for d in dirs:
        dir_path = 'FASTASTIC{}'.format(d)
        # Create necessary DIRs if they don't already exist
        if not os.path.isdir(dir_path):
            try:
                print('Creating directory {}...'.format(dir_path))
                l = subprocess.check_output('mkdir ' + dir_path, shell=True)
            except subprocess.CalledProcessError as e:
                print('An error occured while trying to create the directory \
                      {}'.format(dir_path))
                exit(1)
   
    ### Run FastQ file through SPAdes ###

    # Note: this program ONLY accepts one single-read paired-end library
    #cmd = '{} --s1 {} -o ./FASTASTIC/SPAdes'.format(
    #        args.spades_path, args.spades_input)
    cmd = '{} --s1 {} '.format(args.spades_path, args.spades_input)
    if args.fastq2 != None:
        cmd += '--s2 {} '.format(args.fastq2)
    cmd += '-o ./FASTASTIC/SPAdes'

    try:
        print('FASTASTIC: Running SPAdes...')
        l = subprocess.check_output(cmd,
                                    stderr=subprocess.STDOUT,
                                    shell=True)
        if args.verbose:
            print(l.decode('utf-8'))
    except subprocess.CalledProcessError as e:
        print('An error occured while trying to run spades.py')
        print('See error output below:')
        print(e)
    
    ### Run input FastQ file through FastQC ###
    
    # Note: this program ONLY accepts one single-read paired-end library
    #cmd = 'fastqc {} --outdir=./FASTASTIC/FastQC'.format(args.spades_input)
    cmd = 'fastqc {} '.format(args.spades_input)
    if args.fastq2 != None:
        cmd += args.fastq2 + ' '
    cmd += '--outdir=./FASTASTIC/FastQC'

    try:
        print('FASTASTIC: Running FastQC...')
        l = subprocess.check_output(cmd,
                                    stderr=subprocess.STDOUT,
                                    shell=True)
        if args.verbose:
            print(l.decode('utf-8'))
    except subprocess.CalledProcessError as e:
        print('An error occured while trying to run fastqc')
        print('See error output below:')
        print(e)
    
    ### Run SPAdes contigs.fasta output through QUAST ###
    
    cmd = '{} ./FASTASTIC/SPAdes/contigs.fasta -o ./FASTASTIC/QUAST'.format(
            args.quast_path)
    
    try:
        print('FASTASTIC: Running QUAST...')
        l = subprocess.check_output(cmd,
                                    stderr=subprocess.STDOUT,
                                    shell=True)
        if args.verbose:
            print(l.decode('utf-8'))
    except subprocess.CalledProcessError as e:
        print('An error occured while trying to run quast.py')
        print('See error output below:')
        print(e)
    
    ### Take FASTA output of SPAdes and run through Prokka ###
    
    # First modify SPAdes output contigs.fasta file so that contig names are
    # always shorter than 20 characters long (requirement for Prokka)
    name_map = rename_contigs('./FASTASTIC/SPAdes/contigs.fasta')    
    with open('./FASTASTIC/SPAdes/name_map.txt','w') as f:
        f.write('new,old\n')
        for new, old in name_map.items():
            f.write('{},{}\n'.format(new, old))

    # Notify the user that they should have prokka/bin in their path
    full_path_to_prokka = (os.path.abspath(args.prokka_path))[:-len('/prokka')]

    print('FASTASTIC: Adding DB file to temporary path')
    new_env = os.environ.copy()
    new_env['PATH'] = full_path_to_prokka + ':' + new_env['PATH']
    print('New $PATH is: {}'.format(new_env['PATH']))

    # Need to setup the Prokka database first (every time you open new terminal)
    cmd = '{} --setupdb'.format(args.prokka_path)
   
    # set db_setup to False if you don't need to run prokka --setupdb
    db_setup = True
    if db_setup:
        try:
            print('FASTASTIC: Setting up Prokka DB...')
            l = subprocess.check_output(cmd,
                                        stderr=subprocess.STDOUT,
                                        shell=True,
                                        env=new_env)
            if args.verbose:
                print(l.decode('utf-8'))
        except subprocess.CalledProcessError as e:
            print('An error occured while trying to run Prokka')
            print('See error output below:')
            print(e)
     
    cmd = '{} --outdir ./FASTASTIC/Prokka --force ./FASTASTIC/SPAdes/contigs_short.fasta'.format(args.prokka_path)
        
    try:
        print('FASTASTIC: Running Prokka...')
        l = subprocess.check_output(cmd,
                                    stderr=subprocess.STDOUT,
                                    shell=True,
                                    env=new_env)
        if args.verbose:
            print(l.decode('utf-8'))
    except subprocess.CalledProcessError as e:
        print('An error occured while trying to run Prokka')
        print('See error output below:')
        print(e)
 
    print('FANTASTIC: Finished!')
