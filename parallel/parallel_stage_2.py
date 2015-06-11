# For parallelization
import math
import sys
import pp

# For generation
from random import randrange


def has_essential(row):
    if(sum(row) == 1):
        return True
    else:
        return False


def get_essentials(mat):
    essential_I = set([])
    for row in mat:
        if(has_essential(row)):
            essential_I.add(row.index(1))
    return essential_I
    
'''
   Simple function that generates random 3SAT UCP Matrix of given order of size
   with a minterm that covers the clauses represented by the rows of the given
   matrix. Useful for testing parallelization applications to SAT problems of
   larger order
'''

def gen_rand_SAT_UCP(r,c):
    matrix = [0]*r
    for i in range(r):
        temp_row = [0]*c
        row_lits = randrange(1,13)
        if(row_lits < 5): row_lits = 1
        else: row_lits = randrange(2,4)
        #print row_lits
        for j in range(row_lits):
            rand_index = randrange(0,c)
            temp_row[rand_index] = 1
        matrix[i] = temp_row    
    return matrix

'''
   Given a list of essential literals and the matrix. This function computes the
   set of clauses covered by the ltierals and returns the indexes of those rows
   as a set
'''
def get_clauses_covered(myarg):
    matrix = myarg[0] 
    lit_list = myarg[1]
    clauses_covered = set([]) 
    for lit in lit_list:
        for i in range(len(matrix)):
            if(matrix[i][lit] == 1):
                clauses_covered.add(i)
    return clauses_covered 
                
if __name__ == "__main__":

    print """Usage: python [scriptname.py] [ncpus]
        [ncpus] - the number of workers to run in parallel,
        if omitted it will be set to the number of processors in the system"""

    # tuple of all parallel python servers to connect with
    ppservers = ()
    #ppservers = ("127.0.0.1:60000", )

    if len(sys.argv) > 1:
        ncpus = int(sys.argv[1])
        # Creates jobserver with ncpus workers
        job_server = pp.Server(ncpus, ppservers=ppservers)
    else:
        # Creates jobserver with automatically detected number of workers
        job_server = pp.Server(ppservers=ppservers)

    # Prints out the stats about the number of worker threads
    print "Starting pp with", job_server.get_ncpus(), "workers"


    # Retrieving the random 3SAT Instance with given 
    # $rows clauses and $cols variables  
    rows = 10000
    cols = 4000
    matrix = gen_rand_SAT_UCP(rows,cols)
    
    # Splitting the matrix into $ncpus number of parts
    matrices = []
    div_height = rows/ncpus
    for i in range(ncpus):
        matrix_cur = matrix[i*div_height:(i+1)*div_height]
        matrices.append(matrix_cur)
    # print len(matrices)
    
    
    # The following submits 8 jobs and then retrieves the results
    # inputs = (100000, 100010, 100200, 100300, 100040, 100500, 100060, 100700)
    jobs = [job_server.submit(get_essentials, (mat, ), (has_essential, ),
            ("math", )) for mat in matrices]

    results = set([])
    #max_len = 0
    for job in jobs:  
        result = job() 
        # Debugger statements
        #print "Essentials in is : ", result
        #max_len += len(result)
        results = results | result
    
    # Printing stats after stage 1 [Getting essential literals]   
    job_server.print_stats()
    #print "All essentials are : ", results
    #print len(results) <= max_len
    
    # Now all essential literals are stored in the set results. We now proceed on
    # to parallelize the calculation of clauses covered. We use the strategy of 
    # splitting the matrix as before and computing clauses covered
    results_list = list(results)
    arg_list = [(matrix,results_list) for matrix in matrices]

    # Creating the job queue    
    jobs = [job_server.submit(get_clauses_covered, (mat, ), (),
             ("math", )) for mat in arg_list]

    clauses_covered = set([])
    for job in jobs:
        clauses_covered = clauses_covered | job()    

    #print clauses_covered
    job_server.print_stats()

