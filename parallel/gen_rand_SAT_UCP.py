'''
   Simple function that generates random 3SAT UCP Matrix of given order of size
   with a minterm that covers the clauses represented by the rows of the given
   matrix. Useful for testing parallelization applications to SAT problems of
   larger order
'''

from random import randrange

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

if __name__ == "__main__":
    matrix = gen_rand_SAT_UCP(8,1)
    print matrix
     
