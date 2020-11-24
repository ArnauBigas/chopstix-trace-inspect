import numpy as np
from struct import iter_unpack
from multiprocessing import Pool
from math import ceil
import os

def process_work(trace, start, end, n, distance_function):
    matrix = np.zeros((end - start, n), 'float32')
    for i in range(start, end):
        for j in range(0, n):
            matrix[i-start, j] = distance_function(trace.subtraces[i], trace.subtraces[j])
    return matrix

class Trace:
    distance_matrix_generated = False

    def __init__(self, filename, dmatrix_nproc = os.cpu_count()):
        f = open(filename, 'rb')
        raw_data = f.read()
        f.close()

        pages = iter_unpack('<q', raw_data)
        self.subtraces = []
        current_trace = SubTrace()
        for page, in pages:
            if page == -1:
                current_trace = SubTrace()
            elif page == -2:
                self.subtraces.append(current_trace)
            else:
                current_trace.addPage(page)

        if dmatrix_nproc == None:
            dmatrix_nproc = os.cpu_count()

        self.dmatrix_nproc = dmatrix_nproc

    def get_subtrace_count(self):
        return len(self.subtraces)

    def get_distance_matrix(self, distance_function):
        if self.distance_matrix_generated == False:
            n = len(self.subtraces)
            nprocs =  min(n, self.dmatrix_nproc)

            # Generate distance matrix in parallel
            print("Generating distance matrix with %d threads" % nprocs)
            bs = ceil(n/nprocs)
            pool = Pool(nprocs)
            submatrices = pool.starmap(process_work, ((self, i, min(i + bs, n), n, distance_function) for i in range(0, n, bs)))

            # Concatenate submatrices
            self.distance_matrix = np.bmat(list(map(lambda x: [x], submatrices)))
            self.distance_matrix_generated = True

        return self.distance_matrix

class SubTrace:
    def __init__(self):
        self.pages = []

    def addPage(self, address):
        self.pages.append(address)
