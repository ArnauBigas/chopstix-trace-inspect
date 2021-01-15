import numpy as np
from struct import iter_unpack
from multiprocessing import Pool
from math import ceil
import os

def process_work(trace, start, end, n, distance_function):
    matrix = np.zeros((end - start, n), 'float32')
    for i in range(start, end):
        for j in range(0, n):
            matrix[i-start, j] = distance_function(trace.invocations[i], trace.invocations[j])
    return matrix

class Trace:
    distance_matrix_generated = False

    def __init__(self, filename, dmatrix_nproc = os.cpu_count()):
        f = open(filename, 'rb')
        raw_data = f.read()
        f.close()

        pages = iter_unpack('<q', raw_data)
        self.invocations = []
        current_invocation = None
        for page, in pages:
            if page == -3:
                if current_invocation is not None:
                    current_invocation.generate_pages()
                    self.invocations.append(current_invocation)

                current_invocation = Invocation()
            elif page == -1:
                current_subtrace = SubTrace()
            elif page == -2:
                current_invocation.add_subtrace(current_subtrace)
            else:
                current_subtrace.add_page(page)

        if current_invocation is not None:
            current_invocation.generate_pages()
            self.invocations.append(current_invocation)

        if dmatrix_nproc == None:
            dmatrix_nproc = os.cpu_count()

        self.dmatrix_nproc = dmatrix_nproc

    def get_subtrace_count(self):
        return sum(len(invocation.subtraces) for invocation in self.invocations)

    def get_invocation_count(self):
        return len(self.invocations)

    def get_distance_matrix(self, distance_function):
        if self.distance_matrix_generated == False:
            n = self.get_invocation_count()
            nprocs = min(n, self.dmatrix_nproc)

            # Generate distance matrix in parallel
            print("Generating distance matrix with %d threads" % nprocs)
            bs = ceil(n/nprocs)
            pool = Pool(nprocs)
            submatrices = pool.starmap(process_work, ((self, i, min(i + bs, n), n, distance_function) for i in range(0, n, bs)))

            # Concatenate submatrices
            self.distance_matrix = np.bmat(list(map(lambda x: [x], submatrices)))
            self.distance_matrix_generated = True

        return self.distance_matrix

class Invocation:
    def __init__(self):
        self.subtraces = []

    def add_subtrace(self, subtrace):
        self.subtraces.append(subtrace)

    def generate_pages(self):
        pages = set()

        for trace in self.subtraces:
            for page in trace.pages:
                pages.add(page)

        self.pages = list(pages)

class SubTrace:
    def __init__(self):
        self.pages = []

    def add_page(self, address):
        self.pages.append(address)
