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

def transpose(matrix):
    return zip(*matrix)
    
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
        

'''
    Function to print the matrix of our choice.
'''
def print_matrix(matrix):
    if(len(matrix) == 0): return
    if(len(matrix[0]) == 0): return
    [r,c] = [len(matrix),len(matrix[0])]
    for i in range(r):
        row_str = ""
        for j in range(c):
            row_str += str(matrix[i][j]) + " "
        print row_str
    return

           
'''
    Greedy Cover Algorithm
'''     
def elim_greedy(matrix):
    cover = set([])
    if(len(matrix) != 0):
        new_matrix = matrix
        cols = len(matrix[0])
        while(len(new_matrix) != 0):
            new_matrix_t = transpose(new_matrix)
            col_sums = [sum(row) for row in new_matrix_t]
            max_col = col_sums.index(max(col_sums))
            cover.add(max_col)
            next_matrix = []
            for row in new_matrix:
                #Implies this row is not covered by the greedily chosen literal
                if(row[max_col] != 1):    
                    next_matrix.append(row) 
            new_matrix = next_matrix
    return cover 
        
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
    rows = 1000
    cols = 5000
    matrix = gen_rand_SAT_UCP(rows,cols)
   
    # Splitting the matrix into $ncpus number of parts
    matrices = []
    div_height = rows/ncpus
    if(div_height > 0):
        for i in range(ncpus):
            if(i!=ncpus-1):
                matrix_cur = matrix[i*div_height:(i+1)*div_height]
            else:
                matrix_cur = matrix[i*div_height:rows]
            matrices.append(matrix_cur)
    else:
        matrices.append(matrix)

    #print "Matrices ", matrices
    
    
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

    #print "Results : ", results    
    # Printing stats after stage 1 [Getting essential literals]   
    job_server.print_stats()
    #print "All essentials are : ", results
    #print len(results) <= max_len
    
    # Now all essential literals are stored in the set results. We now proceed on
    # to parallelize the calculation of clauses covered. We use the strategy of 
    # splitting the matrix as before and computing clauses covered
    results_list = list(results)
    arg_list = [(mati,results_list) for mati in matrices]

    # Creating the job queue    
    jobs = [job_server.submit(get_clauses_covered, (mat, ), (),
             ("math", )) for mat in arg_list]

    clauses_covered = set([])
    for i in range(len(jobs)):
        job = jobs[i]
        result = job()
        # This needs to be done since the job returns indices relative to its
        # own matrix
        true_set = set([])
        for lit in result:
            true_set.add(lit + i* div_height) 
        clauses_covered = clauses_covered | true_set     

    #print "Clauses_covered : ", len(list(clauses_covered))
    #print clauses_covered
    job_server.print_stats()

    # Showing the old matrix before removing clauses covered   
    # print "ORIGINAL MATRIX" 
    # print_matrix(matrix)

    print "Original matrix len ", len(matrix)
    print "Clauses covered len ", len(clauses_covered)
    # Computing the new matrix length
    new_matrix = []
    for i in range(len(matrix)):
        if(i not in clauses_covered):
            new_matrix.append(matrix[i])

    # Showing the new matrix 
    # print "MATRIX AFTER REMOVING COVERED CLAUSES"   
    # print_matrix(new_matrix)

    # Splitting the new matrix according to the no of processors
    new_rows = len(new_matrix) 
    matrices = []
    div_height = int(math.floor(new_rows*1.0/ncpus))
    
    # Division Height Debug Statements
    # print "New Matrix "
    # print_matrix(new_matrix)
    print "D height : ", div_height
    print "Matrix Height : ", len(new_matrix)
    
    for i in range(ncpus):
        if(i != ncpus-1): 
            matrix_cur = new_matrix[i*div_height:(i+1)*div_height]
        else: 
            matrix_cur = new_matrix[i*div_height:new_rows]
        matrices.append(matrix_cur)
     
    
    ''' Debug statements
    print "Matrices : " 
    for m in matrices:
        print_matrix(m)
        print "----"
    '''

    jobs = [job_server.submit(elim_greedy, (mat, ), (transpose,),
             ("math", )) for mat in matrices]
    
    cube_cover = set([])
    for i in range(len(jobs)):
        job = jobs[i]
        result = job()
        #k = list(result)  
        #k.sort()
        #print k 
        # This needs to be done since the job returns indices relative to its
        # own matrix
        true_set = set([])
        for lit in result:
            true_set.add(lit + i* div_height) 
        #mylist = list(true_set)
        #mylist.sort()
        #print mylist
        cube_cover = cube_cover | true_set     


    #print cube_cover
    # The final set of literals that cover the matrix
    final_cover = cube_cover | results
    
    # Printing parallelizations stats of stage 3
    job_server.print_stats()

    print "ESSENTIAL LITERAL OF LENGTH : ", len(results) #,"IS : ",results
    print "GREEDY COVER OF LENGTH : ",len(cube_cover) #,"IS : ",cube_cover
    print "FINAL COVER OF LENGTH", len(final_cover) # ,"IS : ", final_cover


    

