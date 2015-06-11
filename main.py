# Importing the standard libraries
import minisolvers
# Relevant to the parallel module
import pp
import sys
import time

'''
    Function : parse_SAT(stream)
    Function to parse and forumlate a SAT Instance object that has methods such 
    as .solve and .get_model to solve the sat instance. Parses the SAT problem
    from the standard DIMACS format for SAT Benchmarks
'''
def parse_SAT(stream):
    lines = stream.readlines()
    nVars = 0
    nClauses = 0
    S = minisolvers.MinisatSolver()
    cList = []
    for line in lines:
        line = line.rstrip()
        if(line.startswith('c') or 
            line.startswith('%') or 
            line.startswith('0') or
            line == ""):
            # The current line is boilerplate code
            pass
        elif(line.startswith('p')):
            # The current line the problems definition
            line = line.split()
            nVars = int(line[2])
            nClauses = int(line[3]) 
            for i in range(nVars): 
                S.new_var()  
        else:
            # The current line is a clause 
            clause = set([int(x) for x in line.split() if not(x == '0')])
            clause_list_form = list(clause)
            cList.append(clause)
            S.add_clause(clause_list_form)
    # Return the SAT Instance
    return [S,cList]
        
'''
    Function : get_ucp_matrix(m_i,cList)
    Returns the UCP Matrix for the minterm. This function is a part of formulat
    -ing the Hitting Set problem for the project and checks membership in the
    clause list that is provided
'''            
def get_ucp_matrix(m_i,cList):

    # Transforming minterm to indicate the values of the terms
    m_i = [(i+1) if m_i[i] == 1 else -(i+1) for i in range(len(m_i))]
    
    # Part of failed strategy #1
    '''
    len_cList = len(cList) 
    len_1 = len_cList/2
    len_2 = len_cList - len_cList/2
    job1 = job_server.submit(get_ucp_matrix_part,(m_i,cList[:len_1],len_1),(get_ucp_row,),())     
    job2 = job_server.submit(get_ucp_matrix_part,(m_i,cList[len_1:len_1 + len_2],len_2),(get_ucp_row,),())
    ucp_matrix_1 = job1()
    ucp_matrix_2 = job2()
    ucp_matrix = ucp_matrix_1 + ucp_matrix_2
    '''

    # Populating the UCP Matrix
    ucp_matrix = [0]*len(cList)
    for i in range(len(cList)):
        ucp_row = get_ucp_row(m_i,cList[i])
	ucp_matrix[i] = ucp_row

    return [m_i,ucp_matrix] 

# Part of Failed Stragegy #1.   
'''    
def get_ucp_matrix_part(m_i,cList,len_p):
    ucp_matrix = [0]*len_p
    for i in range(len_p):
	ucp_row = get_ucp_row(m_i,cList[i])    
        ucp_matrix[i] = ucp_row
    return ucp_matrix
'''
    
def get_ucp_row(m_i,clause):
    ucp_row = [0]*len(m_i) 
    for i in range(len(m_i)):
        if(m_i[i] in clause):
            ucp_row[i] = 1
    return ucp_row

'''
    Function : get_essential_literals_and_modify(m_i,matrix)
    Function returns the set of essential literals that are required for the
    set of clauses to be covered. Also modifies the matrix to eliminate the 
    covered set of clauses and returns it
'''
def get_essential_literals_and_modify(m_i,matrix):
    essentialI = get_essential_literals(matrix)
    clauses_covered_I = get_clauses_covered_I(essentialI,matrix)
    ucp_matrix_new = get_pruned_matrix(clauses_covered_I,matrix)            
    return [set([m_i[x] for x in essentialI]),
            ucp_matrix_new]

'''
    SubFunction : get_essential_literals(matrix)
    Returns the set of essential literals by checking the row sum of each of 
    the rows. Each row here is a clause in the SAT Instance     
'''
# Parallelizable function 
def get_essential_literals(matrix):
    essentialI = set([])
    for row in matrix:
        if(sum(row) == 1):  
            essentialI.add(row.index(1))            
    return essentialI

'''
    SubFunction : get_clauses_covered(essentialI,matrix)
    Returns the clauses covered by the essential literals since the essential
    literal will cover many clauses and not only the the clause that makes it 
    essential 
'''                                    
def get_clauses_covered_I(essentialI,matrix):
    clauses_covered = set([])
    for index in essentialI:
        for rowI in range(len(matrix)):
            if(matrix[rowI][index] == 1):
                clauses_covered.add(rowI)
    return clauses_covered                

'''
    Function : get_pruned_matrix(clauses_covered_I,ucp_matrix)
    Returns a new matrix by pruning the existing matrix by eliminating the 
    clauses that have already been covered        
'''            
def get_pruned_matrix(clauses_covered_I,ucp_matrix):
    ucp_matrix_new = []    
    for i in range(len(ucp_matrix)):
        if(i not in clauses_covered_I):
            ucp_matrix_new.append(ucp_matrix[i])
    return ucp_matrix_new
                
'''
    Function : prune_implied(matrix)
    Determines implied clauses and eliminates them. Note that this function 
    assumes that there are no repeated(same) clauses in the input instance. This
    should be the case as per the DIMACS guidelines
'''                
def prune_implied(matrix):
    row_elims = get_implied_rows(matrix)
    matrix = elim(matrix,row_elims)
    return matrix                
  
'''
    Function : elim(matrix,row_elims)
    Eliminates the particular set of rows from the matrix as per the reference
'''    
def elim(matrix,row_elims):
    new_matrix = []
    for i in range(len(matrix)):
        if(i not in row_elims):
            new_matrix.append(matrix[i])
    return new_matrix    

'''
    Function : get_implied_rows(matrix)
    Returns the set of implied rows or clauses from the given matrix. Performs
    the simple boolean implication test
'''            
def get_implied_rows(matrix):
    rows_I = set([])
    for i in range(len(matrix)):
        other_set = set(range(len(matrix))) - set([i])
        for index in other_set:
            if(implied(index,i,matrix)):
                rows_I.add(index)            
    return rows_I

'''
    Function : implied(index,i,matrix)
    Returns if row indexed by 'i' implied row indexed by 'index'
'''
def implied(index,i,matrix):
    row1 = matrix[i]
    row2 = matrix[index]
    for i in range(len(row1)):
        if(row1[i] == 1):
            if(row2[i] == 0):
                return False    
    return True
    
def transpose(matrix):
    return zip(*matrix)
	
'''
    Function : get_greedy_cover(m_i,ucp_matrix)
    This function returns the greedy set cover for the set cover problem. In 
    the current scenario, we prune the exiting ucp_matrix after every greedy 
    literal pick, until all the clauses have been exhausted
'''    
def get_greedy_cover(m_i,ucp_matrix):
    cover_vars = set([])
    while(len(ucp_matrix) > 0):
        ucp_T = transpose(ucp_matrix)
        sumList = [sum(row) for row in ucp_T]
        max_val = max(sumList)
        max_val_I = sumList.index(max_val)
        cover_vars.add(max_val_I)
        ucp_matrix = prune_literal(max_val_I,ucp_matrix)       
    return set([m_i[i] for i in cover_vars])
    
def prune_literal(max_val_I,ucp_matrix):
    ucp_new = []
    for row in ucp_matrix:
        if(row[max_val_I] != 1):
            ucp_new.append(row)
    return ucp_new

'''
    Function : get_cube_cover(minterm,cList)
    Returns the cube cover of a particular minterm and the associated blocking
    clause. Uses the SAT Instance defined by cList as the base for computing 
    the cube cover for the particular minterm
'''            
def get_cube_cover(minterm,cList):
    [m_i,ucp_matrix] = get_ucp_matrix(minterm,cList)
    [e_lit,ucp_matrix] = get_essential_literals_and_modify(m_i,ucp_matrix)
    ucp_matrix = prune_implied(ucp_matrix)
    greedy_terms = get_greedy_cover(m_i,ucp_matrix)
    cube_cover = e_lit | greedy_terms
    blocking_clause = set([-x for x in cube_cover])
    return [cube_cover,blocking_clause]

def print_result(i,Q):
    if(i == 1):
        print "UNSATISFIABLE"
    else:
        print "SATISFIABLE"

def get_cur_problem_stream(i):
    file_string = "input/Industrial/set3/" + str(i)
    print file_string
    stream = open(file_string)
    return stream
        
        
def get_all_sat(S,cList):
    # F is updated every iteration while the initial clause list as in
    # cList remains the same. This is the crucial change that creates the 
    # DNF Cover faster. If we update cList each iteration, it will produce
    # disjoing cubes
    j = 1
    F = S
    Q = []
    while(F.solve()):
        # Break in case of a time out
        cur_time = time.time()
        if(cur_time - cur_start > 5400): 
            break
        minterm = list(F.get_model())
        [cube_cover,blocking_clause] = get_cube_cover(minterm,cList)
        Q.append(list(cube_cover))
        F.add_clause(blocking_clause)
        # Previous technique Used to produce disjoint cubes by uncommenting
        # the following line: - 
        # cList.append(blocking_clause) 

        '''
        # Failed Strategy number 2
        minterm_1 = list(F.get_model())
        m_1 = [(i+1) if minterm_1[i] == 1 else -(i+1) for i in range(len(minterm_1))]
        [cube_cover_1,blocking_clause_1] = get_cube_cover(minterm_1,cList)
        S.add_clause([-i for i in m_1])
        S.solve()
        minterm_2 = list(S.get_model())
        m_2 =  [(i+1) if minterm_2[i] == 1 else -(i+1) for i in range(len(minterm_2))]
        [cube_cover_2,blocking_clause_2] = get_cube_cover(minterm_2,cList)
        Q.append(list(cube_cover_1))
        Q.append(list(cube_cover_2))
        F.add_clause(blocking_clause_1)
        F.add_clause(blocking_clause_2)       
        '''
        j = j + 1 
    return [j,Q]
  

# Global parallel vars being assigned defaults
job_server = None  
ncpus = 1
cur_start = 0

'''
    Main Program for the SAT Instance algorithm. This function is incharge of
    which SAT Benchmark the algorithm is tried upon and produces the required 
    results
'''    
if __name__ == "__main__":

    # Global variables
    global job_server
    global ncpus
    global cur_start

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

    print "Starting pp with", job_server.get_ncpus(), "workers"

    
    # Parsing the Input in cnf form and forming a SAT Instance
    # Crafted problem file list
    random_list = range(1,101)
    crafted_list_1 = ["hwb-n26-01-S1957858365.shuffled-as.sat03-1622.used-as.sat04-859",
                    "hwb-n26-02-S1189729474.shuffled-as.sat03-1623.used-as.sat04-848",
                    "hwb-n26-03-S540351185.shuffled-as.sat03-1624.used-as.sat04-849",
		    "hwb-n28-01-S136611085.shuffled-as.sat03-1627.used-as.sat04-850",
                    "hwb-n28-02-S818962541.shuffled-as.sat03-1628.used-as.sat04-851",
                    "hwb-n28-03-S1967922763.shuffled-as.sat03-1629.used-as.sat04-852",
                    "hwb-n30-01-S682466202.shuffled-as.sat03-1632.used-as.sat04-853",
                    "hwb-n30-02-S77299857.shuffled-as.sat03-1633.used-as.sat04-854",
                    "hwb-n30-03-S44661219.shuffled-as.sat03-1634.used-as.sat04-855",
                    "hwb-n30-03-S44661219.shuffled-as.sat03-1634.used-as.sat04-856",
                    "hwb-n30-03-S44661219.shuffled-as.sat03-1634.used-as.sat04-857",
                    "hwb-n30-03-S44661219.shuffled-as.sat03-1634.used-as.sat04-858"]
    crafted_list_2 = [1,7,201,204,205,209,207,210,212,213,217,218,220,301]
    industrial_list_1 = ["0432-003","2670-130","2670-141","6288-047","7552-038","7552-158","7552-159","7552-160"]
    industrial_list_2 = ["ferry10_ks99a.renamed-as.sat05-3992.cnf",
"ferry7_ks99i.renamed-as.sat05-4001.cnf",
"ferry10_v01a.renamed-as.sat05-3993.cnf" ,  
"ferry7_v01a.renamed-as.sat05-4002.cnf",
"ferry5_ks99i.renamed-as.sat05-3994.cnf",   
"ferry7_v01i.renamed-as.sat05-4003.cnf",
"ferry5_v01i.renamed-as.sat05-3995.cnf",
"ferry8_ks99a.renamed-as.sat05-4004.cnf",
"ferry6_ks99a.renamed-as.sat05-3996.cnf" ,  
"ferry8_ks99i.renamed-as.sat05-4005.cnf",
"ferry6_ks99i.renamed-as.sat05-3997.cnf" ,  
"ferry8_v01a.renamed-as.sat05-4006.cnf",
"ferry6_v01a.renamed-as.sat05-3998.cnf" ,   
"ferry8_v01i.renamed-as.sat05-4007.cnf",
"ferry6_v01i.renamed-as.sat05-3999.cnf" ,   
"ferry9_ks99a.renamed-as.sat05-4008.cnf",
"ferry7_ks99a.renamed-as.sat05-4000.cnf" ,  
"ferry9_v01a.renamed-as.sat05-4009.cnf"]
    industrial_list_3 = ["ferry10_ks99a.shuffled-as.sat05-4059.cnf",
"ferry10_v01a.shuffled-as.sat05-4060.cnf",
"ferry5_ks99i.shuffled-as.sat05-4061.cnf",
"ferry5_v01i.shuffled-as.sat05-4062.cnf",
"ferry6_ks99a.shuffled-as.sat05-4063.cnf",
"ferry6_ks99i.shuffled-as.sat05-4064.cnf",
"ferry6_v01a.shuffled-as.sat05-4065.cnf",
"ferry6_v01i.shuffled-as.sat05-4066.cnf",
"ferry7_ks99a.shuffled-as.sat05-4067.cnf",
"ferry7_ks99i.shuffled-as.sat05-4068.cnf",
"ferry7_v01a.shuffled-as.sat05-4069.cnf",
"ferry7_v01i.shuffled-as.sat05-4070.cnf",
"ferry8_ks99a.shuffled-as.sat05-4071.cnf",
"ferry8_ks99i.shuffled-as.sat05-4072.cnf",
"ferry8_v01a.shuffled-as.sat05-4073.cnf",
"ferry8_v01i.shuffled-as.sat05-4074.cnf",
"ferry9_ks99a.shuffled-as.sat05-4075.cnf",
"ferry9_v01a.shuffled-as.sat05-4076.cnf"
]

  
    # Change to random_list for Random3SAT and industrial_list for Industrial problems
    # NOTE : Also need to make changes in get_cur_problem_stream
    for i in industrial_list_3:
        cur_start = time.time()
        print "Current problem : " + str(i)
        stream = get_cur_problem_stream(i)
        [S,cList] = parse_SAT(stream)
        [j,Q] = get_all_sat(S,cList)
        print_result(j,Q)
    
 
    # Debugger stream
    '''
    [S,cList] = parse_SAT(open("input/input.cnf"))
    [j,Q] = get_all_sat(S,cList)
    print_result(j,Q)              
    '''

