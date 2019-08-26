import openfermion
import numpy as np
import copy as cp

import random

from openfermion import *



class OperatorPool:
    def __init__(self):
        self.n_orb = 0
        self.n_occ_a = 0
        self.n_occ_b = 0
        self.n_vir_a = 0
        self.n_vir_b = 0

        self.n_spin_orb = 0

    def init(self,molecule):

        self.n_orb = molecule.n_orbitals
        print(self.n_orb)
        print(molecule.n_electrons)
        self.n_spin_orb = 2*self.n_orb 
        self.n_occ_a = molecule.get_n_alpha_electrons()
        print(self.n_occ_a)
        self.n_occ_b = molecule.get_n_beta_electrons()
        print(self.n_occ_b)
    
        self.n_vir_a = self.n_orb - self.n_occ_a
        self.n_vir_b = self.n_orb - self.n_occ_b
        
        self.n_occ = self.n_occ_a
        self.n_vir = self.n_vir_a
        self.n_ops = 0

        self.generate_SQ_Operators()

    def generate_SQ_Operators(self):
        print("Virtual: Reimplement")
        exit()

    def generate_SparseMatrix(self):
        self.spmat_ops = []
        print(" Generate Sparse Matrices for operators in pool")
        xx = 0
        for op in self.fermi_ops:
            print(op)
            print("")
            self.spmat_ops.append(transforms.get_sparse_operator(op, n_qubits = self.n_spin_orb))
        assert(len(self.spmat_ops) == self.n_ops)
        print(xx) 
        # print(self.spmat_ops[1])
        return

class singlet_GSD(OperatorPool):
    def generate_SQ_Operators(self):
        """
        n_orb is number of spatial orbitals assuming that spin orbitals are labelled
        0a,0b,1a,1b,2a,2b,3a,3b,....  -> 0,1,2,3,...
        """
        
        print(" Form singlet GSD operators")
        
        self.fermi_ops = []
        for p in range(0,self.n_orb):
            pa = 2*p
            pb = 2*p+1
 
            for q in range(p,self.n_orb):
                qa = 2*q
                qb = 2*q+1
        
                termA =  FermionOperator(((pa,1),(qa,0)))
                termA += FermionOperator(((pb,1),(qb,0)))
 
                termA -= hermitian_conjugated(termA)
               
                termA = normal_ordered(termA)
                
                #Normalize
                coeffA = 0
                for t in termA.terms:
                    coeff_t = termA.terms[t]
                    coeffA += coeff_t * coeff_t
            
                if termA.many_body_order() > 0:
                    termA = termA/np.sqrt(coeffA)
                    self.fermi_ops.append(termA)
                       
      
        pq = -1 
        for p in range(0,self.n_orb):
            pa = 2*p
            pb = 2*p+1
 
            for q in range(p,self.n_orb):
                qa = 2*q
                qb = 2*q+1
        
                pq += 1
        
                rs = -1 
                for r in range(0,self.n_orb):
                    ra = 2*r
                    rb = 2*r+1
                    
                    for s in range(r,self.n_orb):
                        sa = 2*s
                        sb = 2*s+1
                    
                        rs += 1
                    
                        if(pq > rs):
                            continue

                        termA =  FermionOperator(((ra,1),(pa,0),(sa,1),(qa,0)), 2/np.sqrt(12))
                        termA += FermionOperator(((rb,1),(pb,0),(sb,1),(qb,0)), 2/np.sqrt(12))
                        termA += FermionOperator(((ra,1),(pa,0),(sb,1),(qb,0)), 1/np.sqrt(12))
                        termA += FermionOperator(((rb,1),(pb,0),(sa,1),(qa,0)), 1/np.sqrt(12))
                        termA += FermionOperator(((ra,1),(pb,0),(sb,1),(qa,0)), 1/np.sqrt(12))
                        termA += FermionOperator(((rb,1),(pa,0),(sa,1),(qb,0)), 1/np.sqrt(12))

                        termB =  FermionOperator(((ra,1),(pa,0),(sb,1),(qb,0)),  1/2.0)
                        termB += FermionOperator(((rb,1),(pb,0),(sa,1),(qa,0)),  1/2.0)
                        termB += FermionOperator(((ra,1),(pb,0),(sb,1),(qa,0)), -1/2.0)
                        termB += FermionOperator(((rb,1),(pa,0),(sa,1),(qb,0)), -1/2.0)
 
                        termA -= hermitian_conjugated(termA)
                        termB -= hermitian_conjugated(termB)
               
                        termA = normal_ordered(termA)
                        termB = normal_ordered(termB)
                        
                        #Normalize
                        coeffA = 0

                        for t in termA.terms:
                            coeff_t = termA.terms[t]
                            coeffA += coeff_t * coeff_t

                        coeffB = 0

                        for t in termB.terms:
                            coeff_t = termB.terms[t]
                            coeffB += coeff_t * coeff_t

                        if termA.many_body_order() > 0:
                            termA = termA/np.sqrt(coeffA)
                            self.fermi_ops.append(termA)
                        
                        if termB.many_body_order() > 0:
                            termB = termB/np.sqrt(coeffB)
                            self.fermi_ops.append(termB)

        self.n_ops = len(self.fermi_ops)
        print(" Number of operators: ", self.n_ops)
        return 

class anti_com(OperatorPool):
    def generate_SQ_Operators(self):

        self.bin_pool = []

        for i in range(2 ** 4):
            b_string = [int(j) for j in bin(i)[2:].zfill(4)]
            self.bin_pool.append(b_string)

        self.z = []
        self.x = []

        for i in self.bin_pool:
            for j in self.bin_pool:
                if sum(i[k] * j[k] for k in range(4)) % 2 == 1:
                    self.z.append(i)
                    self.x.append(j)

        print("total number of antisymmetric ops :"+str(len(self.z)))

        nn = random.randint(0, 2 ** 4 - 1)

        self.z_f1 = []
        self.x_f1 = []

        self.z_f1.append(self.z[nn])
        self.x_f1.append(self.x[nn])

        for i in range(len(self.z)):
            z1 = [(self.z[i][k] + self.z[nn][k]) % 2 for k in range(4)]
            x1 = [(self.x[i][k] + self.x[nn][k]) % 2 for k in range(4)]
            if sum(z1[k] * x1[k] for k in range(4)) % 2 == 1:
                self.z_f1.append(self.z[i])
                self.x_f1.append(self.x[i])

        print(len(self.z_f1))

        for i in range(1, 2 ** 4 - 1):
            self.z_f2 = self.z_f1[:i+1]
            self.x_f2 = self.x_f1[:i+1]
            print(len(self.z_f2))
            for j in range(i+1, len(self.z_f1)):
                z1 = [(self.z_f1[i][k] + self.z_f1[j][k]) % 2 for k in range(4)]
                x1 = [(self.x_f1[i][k] + self.x_f1[j][k]) % 2 for k in range(4)]
                if sum(z1[k] * x1[k] for k in range(4)) % 2 == 1:
                    jj = 0
                    for m in range(0, i):
                        if (z1 != self.z_f2[m]) or (x1 != self.x_f2[m]):
                            jj += 1
                    if jj == 0:
                        self.z_f2.append(self.z_f1[j])
                        self.x_f2.append(self.x_f1[j])

            self.z_f1 = self.z_f2
            self.x_f1 = self.x_f2

        for i in range(len(self.z_f2)):
            print(self.z_f2[i],self.x_f2[i])

class singlet_SD(OperatorPool):
    def generate_SQ_Operators(self):
        """
        0a,0b,1a,1b,2a,2b,3a,3b,....  -> 0,1,2,3,...
        """

        print(" Form singlet SD operators")
        self.fermi_ops = [] 
       
        n_occ = self.n_occ
        n_vir = self.n_vir
       
        for i in range(0,n_occ):
            ia = 2*i
            ib = 2*i+1

            for a in range(0,n_vir):
                aa = 2*n_occ + 2*a
                ab = 2*n_occ + 2*a+1
                    
                termA =  FermionOperator(((aa,1),(ia,0)), 1/np.sqrt(2))
                termA += FermionOperator(((ab,1),(ib,0)), 1/np.sqrt(2))
                
                termA -= hermitian_conjugated(termA)
                        
                termA = normal_ordered(termA)
               
                #Normalize
                coeffA = 0
                for t in termA.terms:
                    coeff_t = termA.terms[t]
                    coeffA += coeff_t * coeff_t
                
                if termA.many_body_order() > 0:
                    termA = termA/np.sqrt(coeffA)
                    self.fermi_ops.append(termA)
       

        for i in range(0,n_occ):
            ia = 2*i
            ib = 2*i+1

            for j in range(i,n_occ):
                ja = 2*j
                jb = 2*j+1
        
                for a in range(0,n_vir):
                    aa = 2*n_occ + 2*a
                    ab = 2*n_occ + 2*a+1

                    for b in range(a,n_vir):
                        ba = 2*n_occ + 2*b
                        bb = 2*n_occ + 2*b+1

                        termA =  FermionOperator(((aa,1),(ba,1),(ia,0),(ja,0)), 2/np.sqrt(12))
                        termA += FermionOperator(((ab,1),(bb,1),(ib,0),(jb,0)), 2/np.sqrt(12))
                        termA += FermionOperator(((aa,1),(bb,1),(ia,0),(jb,0)), 1/np.sqrt(12))
                        termA += FermionOperator(((ab,1),(ba,1),(ib,0),(ja,0)), 1/np.sqrt(12))
                        termA += FermionOperator(((aa,1),(bb,1),(ib,0),(ja,0)), 1/np.sqrt(12))
                        termA += FermionOperator(((ab,1),(ba,1),(ia,0),(jb,0)), 1/np.sqrt(12))
                                                                      
                        termB  = FermionOperator(((aa,1),(bb,1),(ia,0),(jb,0)), 1/2)
                        termB += FermionOperator(((ab,1),(ba,1),(ib,0),(ja,0)), 1/2)
                        termB += FermionOperator(((aa,1),(bb,1),(ib,0),(ja,0)), -1/2)
                        termB += FermionOperator(((ab,1),(ba,1),(ia,0),(jb,0)), -1/2)
                
                        termA -= hermitian_conjugated(termA)
                        termB -= hermitian_conjugated(termB)
               
                        termA = normal_ordered(termA)
                        termB = normal_ordered(termB)
                        
                        #Normalize
                        coeffA = 0
                        coeffB = 0
                        for t in termA.terms:
                            coeff_t = termA.terms[t]
                            coeffA += coeff_t * coeff_t
                        for t in termB.terms:
                            coeff_t = termB.terms[t]
                            coeffB += coeff_t * coeff_t

                        
                        if termA.many_body_order() > 0:
                            termA = termA/np.sqrt(coeffA)
                            self.fermi_ops.append(termA)
                        
                        if termB.many_body_order() > 0:
                            termB = termB/np.sqrt(coeffB)
                            self.fermi_ops.append(termB)
        
        self.n_ops = len(self.fermi_ops)
        print(" Number of operators: ", self.n_ops)
        return 

class qubits(OperatorPool):
    def generate_SQ_Operators(self):

        self.fermi_ops = []
        
        n_occ = self.n_occ
        n_vir = self.n_vir
                
        for p in range(0,2*self.n_orb):
            X = QubitOperator('X%d'% p, 0+1j)
            Y = QubitOperator('Y%d'% p, 0+1j)

            self.fermi_ops.append(X)
        for p in range(0,2*self.n_orb):
            Z = QubitOperator('Z%d'% p, 0+1j)

            self.fermi_ops.append(Z)

        for p in range(0,2*self.n_orb):

            for q in range(p+1,2*self.n_orb):

                ZZ = QubitOperator('Z%d Z%d'% (p, q), 0+1j)
                self.fermi_ops.append(ZZ)

        for p in range(0,2*self.n_orb):
            for q in range(p+1,2*self.n_orb):

                # XX = QubitOperator('X%d X%d'% (p, q), 0+1j)
                XY = QubitOperator('X%d Y%d'% (p, q), 0+1j)
                YX = QubitOperator('Y%d X%d'% (p, q), 0+1j)
                # XZ = QubitOperator('X%d Z%d'% (p, q), 0+1j)
                # YZ = QubitOperator('Y%d Z%d'% (p, q), 0+1j)
                # YY = QubitOperator('Y%d Y%d'% (p, q), 0+1j)

                # self.fermi_ops.append(XX)
                self.fermi_ops.append(YX)
                # self.fermi_ops.append(XZ)
                # self.fermi_ops.append(YZ)
                # self.fermi_ops.append(YY)
                self.fermi_ops.append(XY) 


        for i in range(0,2*self.n_orb):
            for j in range(i+1, 2*self.n_orb):

                for k in range(j+1, 2*self.n_orb):

                    YXZ = QubitOperator('Y%d X%d Z%d'% (i, j, k), 1j)  
                    XYZ = QubitOperator('X%d Y%d Z%d'% (i, j, k), 1j)
                    XZY = QubitOperator('X%d Z%d Y%d'% (i, j, k), 1j)
                    YZX = QubitOperator('Y%d Z%d X%d'% (i, j, k), 1j)
                    ZXY = QubitOperator('Z%d X%d Y%d'% (i, j, k), 1j)
                    ZYX = QubitOperator('Z%d X%d Y%d'% (i, j, k), 1j)
                    # ZZZ = QubitOperator('Z%d Z%d Z%d'% (i, j, k), 1j)
  
                    self.fermi_ops.append(XYZ)
                    self.fermi_ops.append(YXZ)
                    self.fermi_ops.append(XZY)
                    self.fermi_ops.append(YZX)
                    self.fermi_ops.append(ZXY)
                    self.fermi_ops.append(ZYX)
                    # self.fermi_ops.append(ZZZ)

                    # XXY = QubitOperator('X%d X%d Y%d'% (i, j, k), 1j)
                    # XYY = QubitOperator('X%d Y%d Y%d'% (i, j, k), 1j)

                    # self.fermi_ops.append(XXY)
                    # self.fermi_ops.append(XYY)

        for p in range(0,2*self.n_orb):
            for q in range(p+1,2*self.n_orb):
                for r in range(q+1,2*self.n_orb):
                    for s in range(r+1,2*self.n_orb):
                        XYYY = QubitOperator('X%d Y%d Y%d Y%d'% (p, q, r, s), 1j)
                        YXYY = QubitOperator('Y%d X%d Y%d Y%d'% (p, q, r, s), 1j)
                        YYXY = QubitOperator('Y%d Y%d X%d Y%d'% (p, q, r, s), 1j)
                        YYYX = QubitOperator('Y%d Y%d Y%d X%d'% (p, q, r, s), 1j)

                        self.fermi_ops.append(XYYY)
                        self.fermi_ops.append(YXYY)
                        self.fermi_ops.append(YYXY)
                        self.fermi_ops.append(YYYX)

                        # XXXY = QubitOperator('X%d X%d X%d Y%d'% (p, q, r, s), 1j)
                        # YXXX = QubitOperator('Y%d X%d X%d X%d'% (p, q, r, s), 1j)
                        # XYXX = QubitOperator('X%d Y%d X%d X%d'% (p, q, r, s), 1j)
                        # XXYX = QubitOperator('X%d X%d Y%d X%d'% (p, q, r, s), 1j)

                        # self.fermi_ops.append(XXXY)
                        # self.fermi_ops.append(XXYX)
                        # self.fermi_ops.append(XYXX)
                        # self.fermi_ops.append(YXXX)

                        # ZZXY = QubitOperator('Z%d Z%d X%d Y%d'% (p, q, r, s), 1j)
                        # ZZYX = QubitOperator('Z%d Z%d Y%d X%d'% (p, q, r, s), 1j)
                        # XZZY = QubitOperator('X%d Z%d Z%d Y%d'% (p, q, r, s), 1j)
                        # YZZX = QubitOperator('Y%d Z%d Z%d X%d'% (p, q, r, s), 1j)
                        # ZYXZ = QubitOperator('Z%d Y%d X%d Z%d'% (p, q, r, s), 1j)
                        # ZXYZ = QubitOperator('Z%d X%d Y%d Z%d'% (p, q, r, s), 1j)
                        # XYZZ = QubitOperator('X%d Y%d Z%d Z%d'% (p, q, r, s), 1j)
                        # YXZZ = QubitOperator('Y%d X%d Z%d Z%d'% (p, q, r, s), 1j)
                        # XZYZ = QubitOperator('X%d Z%d Y%d Z%d'% (p, q, r, s), 1j)
                        # YZXZ = QubitOperator('Y%d Z%d X%d Z%d'% (p, q, r, s), 1j)
                        # ZXZY = QubitOperator('Z%d X%d Z%d Y%d'% (p, q, r, s), 1j)
                        # ZYZX = QubitOperator('Z%d Y%d Z%d X%d'% (p, q, r, s), 1j)

                        # self.fermi_ops.append(ZZXY)
                        # self.fermi_ops.append(ZZYX)
                        # self.fermi_ops.append(XZZY)
                        # self.fermi_ops.append(YZZX)
                        # self.fermi_ops.append(ZXYZ)
                        # self.fermi_ops.append(ZYXZ)
                        # self.fermi_ops.append(XYZZ)
                        # self.fermi_ops.append(YXZZ)
                        # self.fermi_ops.append(XZYZ)
                        # self.fermi_ops.append(YZXZ)
                        # self.fermi_ops.append(ZXZY)
                        # self.fermi_ops.append(ZYZX)

                        # XXYY = QubitOperator('X%d X%d Y%d Y%d'% (p, q, r, s), 1j)
                        # XYXY = QubitOperator('X%d Y%d X%d Y%d'% (p, q, r, s), 1j)
                        # XYYX = QubitOperator('X%d Y%d Y%d X%d'% (p, q, r, s), 1j)
                        # YYXX = QubitOperator('Y%d Y%d X%d X%d'% (p, q, r, s), 1j)
                        # YXXY = QubitOperator('Y%d X%d X%d Y%d'% (p, q, r, s), 1j)
                        # YXYX = QubitOperator('Y%d X%d Y%d X%d'% (p, q, r, s), 1j)

                        # self.fermi_ops.append(XXYY)
                        # self.fermi_ops.append(XYXY)
                        # self.fermi_ops.append(XYYX)
                        # self.fermi_ops.append(YYXX)
                        # self.fermi_ops.append(YXXY)
                        # self.fermi_ops.append(YXYX)

                        # XXXX = QubitOperator('X%d X%d X%d X%d'% (p, q, r, s), 1j)
                        # YYYY = QubitOperator('Y%d Y%d Y%d Y%d'% (p, q, r, s), 1j)

                        # self.fermi_ops.append(XXXX)
                        # self.fermi_ops.append(YYYY)                        
 
                
        for op in self.fermi_ops:
            print(op)

        self.n_ops = len(self.fermi_ops)
        print(" Number of operators: ", self.n_ops)        
        return

class rand_half_qubits(OperatorPool):
    def generate_SQ_Operators(self):

        self.fermi_ops_1 = []
        self.fermi_ops_2 = []
        self.fermi_ops_3 = []
        self.fermi_ops_4 = []
        self.fermi_ops = []
        
        n_occ = self.n_occ
        n_vir = self.n_vir
                
        for p in range(0,2*self.n_orb):
            X = QubitOperator('X%d'% p, 0+1j)
            Y = QubitOperator('Y%d'% p, 0+1j)

            self.fermi_ops_1.append(X)
            self.fermi_ops_1.append(Y)
        for p in range(0,2*self.n_orb):
            Z = QubitOperator('Z%d'% p, 0+1j)

            self.fermi_ops_1.append(Z)

        for p in range(0,2*self.n_orb):

            for q in range(p+1,2*self.n_orb):

                ZZ = QubitOperator('Z%d Z%d'% (p, q), 0+1j)
                self.fermi_ops_2.append(ZZ)

        for p in range(0,2*self.n_orb):
            for q in range(p+1,2*self.n_orb):

                XX = QubitOperator('X%d X%d'% (p, q), 0+1j)
                XY = QubitOperator('X%d Y%d'% (p, q), 0+1j)
                YX = QubitOperator('Y%d X%d'% (p, q), 0+1j)
                XZ = QubitOperator('X%d Z%d'% (p, q), 0+1j)
                YZ = QubitOperator('Y%d Z%d'% (p, q), 0+1j)
                YY = QubitOperator('Y%d Y%d'% (p, q), 0+1j)

                self.fermi_ops_2.append(XX)
                self.fermi_ops_2.append(YX)
                self.fermi_ops_2.append(XZ)
                self.fermi_ops_2.append(YZ)
                self.fermi_ops_2.append(YY)
                self.fermi_ops_2.append(XY) 


        for i in range(0,2*self.n_orb):
            for j in range(i+1, 2*self.n_orb):

                for k in range(j+1, 2*self.n_orb):

                    YXZ = QubitOperator('Y%d X%d Z%d'% (i, j, k), 1j)  
                    # XYZ = QubitOperator('X%d Y%d Z%d'% (i, j, k), 1j)
                    XZY = QubitOperator('X%d Z%d Y%d'% (i, j, k), 1j)
                    # YZX = QubitOperator('Y%d Z%d X%d'% (i, j, k), 1j)
                    ZXY = QubitOperator('Z%d X%d Y%d'% (i, j, k), 1j)
                    # ZYX = QubitOperator('Z%d X%d Y%d'% (i, j, k), 1j)
                    # ZZZ = QubitOperator('Z%d Z%d Z%d'% (i, j, k), 1j)
  
                    # self.fermi_ops.append(XYZ)
                    self.fermi_ops_3.append(YXZ)
                    self.fermi_ops_3.append(XZY)
                    # self.fermi_ops.append(YZX)
                    self.fermi_ops_3.append(ZXY)
                    # self.fermi_ops.append(ZYX)
                    # self.fermi_ops.append(ZZZ)

                    # XXY = QubitOperator('X%d X%d Y%d'% (i, j, k), 1j)
                    # XYY = QubitOperator('X%d Y%d Y%d'% (i, j, k), 1j)

                    # self.fermi_ops.append(XXY)
                    # self.fermi_ops.append(XYY)

        for p in range(0,2*self.n_orb):
            for q in range(p+1,2*self.n_orb):
                for r in range(q+1,2*self.n_orb):
                    for s in range(r+1,2*self.n_orb):
                        XYYY = QubitOperator('X%d Y%d Y%d Y%d'% (p, q, r, s), 1j)
                        YXYY = QubitOperator('Y%d X%d Y%d Y%d'% (p, q, r, s), 1j)
                        YYXY = QubitOperator('Y%d Y%d X%d Y%d'% (p, q, r, s), 1j)
                        YYYX = QubitOperator('Y%d Y%d Y%d X%d'% (p, q, r, s), 1j)

                        self.fermi_ops_4.append(XYYY)
                        self.fermi_ops_4.append(YXYY)
                        self.fermi_ops_4.append(YYXY)
                        self.fermi_ops_4.append(YYYX)

                        # XXXY = QubitOperator('X%d X%d X%d Y%d'% (p, q, r, s), 1j)
                        # YXXX = QubitOperator('Y%d X%d X%d X%d'% (p, q, r, s), 1j)
                        # XYXX = QubitOperator('X%d Y%d X%d X%d'% (p, q, r, s), 1j)
                        # XXYX = QubitOperator('X%d X%d Y%d X%d'% (p, q, r, s), 1j)

                        # self.fermi_ops.append(XXXY)
                        # self.fermi_ops.append(XXYX)
                        # self.fermi_ops.append(XYXX)
                        # self.fermi_ops.append(YXXX)

                        # ZZXY = QubitOperator('Z%d Z%d X%d Y%d'% (p, q, r, s), 1j)
                        # ZZYX = QubitOperator('Z%d Z%d Y%d X%d'% (p, q, r, s), 1j)
                        # XZZY = QubitOperator('X%d Z%d Z%d Y%d'% (p, q, r, s), 1j)
                        # YZZX = QubitOperator('Y%d Z%d Z%d X%d'% (p, q, r, s), 1j)
                        # ZYXZ = QubitOperator('Z%d Y%d X%d Z%d'% (p, q, r, s), 1j)
                        # ZXYZ = QubitOperator('Z%d X%d Y%d Z%d'% (p, q, r, s), 1j)
                        # XYZZ = QubitOperator('X%d Y%d Z%d Z%d'% (p, q, r, s), 1j)
                        # YXZZ = QubitOperator('Y%d X%d Z%d Z%d'% (p, q, r, s), 1j)
                        # XZYZ = QubitOperator('X%d Z%d Y%d Z%d'% (p, q, r, s), 1j)
                        # YZXZ = QubitOperator('Y%d Z%d X%d Z%d'% (p, q, r, s), 1j)
                        # ZXZY = QubitOperator('Z%d X%d Z%d Y%d'% (p, q, r, s), 1j)
                        # ZYZX = QubitOperator('Z%d Y%d Z%d X%d'% (p, q, r, s), 1j)

                        # self.fermi_ops.append(ZZXY)
                        # self.fermi_ops.append(ZZYX)
                        # self.fermi_ops.append(XZZY)
                        # self.fermi_ops.append(YZZX)
                        # self.fermi_ops.append(ZXYZ)
                        # self.fermi_ops.append(ZYXZ)
                        # self.fermi_ops.append(XYZZ)
                        # self.fermi_ops.append(YXZZ)
                        # self.fermi_ops.append(XZYZ)
                        # self.fermi_ops.append(YZXZ)
                        # self.fermi_ops.append(ZXZY)
                        # self.fermi_ops.append(ZYZX)

                        # XXYY = QubitOperator('X%d X%d Y%d Y%d'% (p, q, r, s), 1j)
                        # XYXY = QubitOperator('X%d Y%d X%d Y%d'% (p, q, r, s), 1j)
                        # XYYX = QubitOperator('X%d Y%d Y%d X%d'% (p, q, r, s), 1j)
                        # YYXX = QubitOperator('Y%d Y%d X%d X%d'% (p, q, r, s), 1j)
                        # YXXY = QubitOperator('Y%d X%d X%d Y%d'% (p, q, r, s), 1j)
                        # YXYX = QubitOperator('Y%d X%d Y%d X%d'% (p, q, r, s), 1j)

                        # self.fermi_ops.append(XXYY)
                        # self.fermi_ops.append(XYXY)
                        # self.fermi_ops.append(XYYX)
                        # self.fermi_ops.append(YYXX)
                        # self.fermi_ops.append(YXXY)
                        # self.fermi_ops.append(YXYX)

                        # XXXX = QubitOperator('X%d X%d X%d X%d'% (p, q, r, s), 1j)
                        # YYYY = QubitOperator('Y%d Y%d Y%d Y%d'% (p, q, r, s), 1j)

                        # self.fermi_ops.append(XXXX)
                        # self.fermi_ops.append(YYYY)                        
        
        np.random.shuffle(self.fermi_ops_1)
        for op in self.fermi_ops_1[:len(self.fermi_ops_1)//2]:
            self.fermi_ops.append(op)

        np.random.shuffle(self.fermi_ops_2)
        for op in self.fermi_ops_2[:len(self.fermi_ops_2)//2]:
            self.fermi_ops.append(op)

        np.random.shuffle(self.fermi_ops_3)
        for op in self.fermi_ops_3[:len(self.fermi_ops_3)//2]:
            self.fermi_ops.append(op)

        np.random.shuffle(self.fermi_ops_4)
        for op in self.fermi_ops_4[:len(self.fermi_ops_4)//2]:
            self.fermi_ops.append(op)

        for op in self.fermi_ops:
            print(op)

        self.n_ops = len(self.fermi_ops)
        print(" Number of operators: ", self.n_ops)        
        return

class rand_hh_qubits(OperatorPool):
    def generate_SQ_Operators(self):

        self.fermi_ops_1 = []
        self.fermi_ops_2 = []
        self.fermi_ops_3 = []
        self.fermi_ops_4 = []
        self.fermi_ops = []
        
        n_occ = self.n_occ
        n_vir = self.n_vir
                
        for p in range(0,2*self.n_orb):
            X = QubitOperator('X%d'% p, 0+1j)
            Y = QubitOperator('Y%d'% p, 0+1j)

            self.fermi_ops_1.append(X)
            self.fermi_ops_1.append(Y)
        for p in range(0,2*self.n_orb):
            Z = QubitOperator('Z%d'% p, 0+1j)

            self.fermi_ops_1.append(Z)

        for p in range(0,2*self.n_orb):

            for q in range(p+1,2*self.n_orb):

                ZZ = QubitOperator('Z%d Z%d'% (p, q), 0+1j)
                self.fermi_ops_2.append(ZZ)

        for p in range(0,2*self.n_orb):
            for q in range(p+1,2*self.n_orb):

                XX = QubitOperator('X%d X%d'% (p, q), 0+1j)
                XY = QubitOperator('X%d Y%d'% (p, q), 0+1j)
                YX = QubitOperator('Y%d X%d'% (p, q), 0+1j)
                XZ = QubitOperator('X%d Z%d'% (p, q), 0+1j)
                YZ = QubitOperator('Y%d Z%d'% (p, q), 0+1j)
                YY = QubitOperator('Y%d Y%d'% (p, q), 0+1j)

                self.fermi_ops_2.append(XX)
                self.fermi_ops_2.append(YX)
                self.fermi_ops_2.append(XZ)
                self.fermi_ops_2.append(YZ)
                self.fermi_ops_2.append(YY)
                self.fermi_ops_2.append(XY) 


        for i in range(0,2*self.n_orb):
            for j in range(i+1, 2*self.n_orb):

                for k in range(j+1, 2*self.n_orb):

                    YXZ = QubitOperator('Y%d X%d Z%d'% (i, j, k), 1j)  
                    # XYZ = QubitOperator('X%d Y%d Z%d'% (i, j, k), 1j)
                    XZY = QubitOperator('X%d Z%d Y%d'% (i, j, k), 1j)
                    # YZX = QubitOperator('Y%d Z%d X%d'% (i, j, k), 1j)
                    ZXY = QubitOperator('Z%d X%d Y%d'% (i, j, k), 1j)
                    # ZYX = QubitOperator('Z%d X%d Y%d'% (i, j, k), 1j)
                    # ZZZ = QubitOperator('Z%d Z%d Z%d'% (i, j, k), 1j)
  
                    # self.fermi_ops.append(XYZ)
                    self.fermi_ops_3.append(YXZ)
                    self.fermi_ops_3.append(XZY)
                    # self.fermi_ops.append(YZX)
                    self.fermi_ops_3.append(ZXY)
                    # self.fermi_ops.append(ZYX)
                    # self.fermi_ops.append(ZZZ)

                    # XXY = QubitOperator('X%d X%d Y%d'% (i, j, k), 1j)
                    # XYY = QubitOperator('X%d Y%d Y%d'% (i, j, k), 1j)

                    # self.fermi_ops.append(XXY)
                    # self.fermi_ops.append(XYY)

        for p in range(0,2*self.n_orb):
            for q in range(p+1,2*self.n_orb):
                for r in range(q+1,2*self.n_orb):
                    for s in range(r+1,2*self.n_orb):
                        XYYY = QubitOperator('X%d Y%d Y%d Y%d'% (p, q, r, s), 1j)
                        YXYY = QubitOperator('Y%d X%d Y%d Y%d'% (p, q, r, s), 1j)
                        YYXY = QubitOperator('Y%d Y%d X%d Y%d'% (p, q, r, s), 1j)
                        YYYX = QubitOperator('Y%d Y%d Y%d X%d'% (p, q, r, s), 1j)

                        self.fermi_ops_4.append(XYYY)
                        self.fermi_ops_4.append(YXYY)
                        self.fermi_ops_4.append(YYXY)
                        self.fermi_ops_4.append(YYYX)

                        # XXXY = QubitOperator('X%d X%d X%d Y%d'% (p, q, r, s), 1j)
                        # YXXX = QubitOperator('Y%d X%d X%d X%d'% (p, q, r, s), 1j)
                        # XYXX = QubitOperator('X%d Y%d X%d X%d'% (p, q, r, s), 1j)
                        # XXYX = QubitOperator('X%d X%d Y%d X%d'% (p, q, r, s), 1j)

                        # self.fermi_ops.append(XXXY)
                        # self.fermi_ops.append(XXYX)
                        # self.fermi_ops.append(XYXX)
                        # self.fermi_ops.append(YXXX)

                        # ZZXY = QubitOperator('Z%d Z%d X%d Y%d'% (p, q, r, s), 1j)
                        # ZZYX = QubitOperator('Z%d Z%d Y%d X%d'% (p, q, r, s), 1j)
                        # XZZY = QubitOperator('X%d Z%d Z%d Y%d'% (p, q, r, s), 1j)
                        # YZZX = QubitOperator('Y%d Z%d Z%d X%d'% (p, q, r, s), 1j)
                        # ZYXZ = QubitOperator('Z%d Y%d X%d Z%d'% (p, q, r, s), 1j)
                        # ZXYZ = QubitOperator('Z%d X%d Y%d Z%d'% (p, q, r, s), 1j)
                        # XYZZ = QubitOperator('X%d Y%d Z%d Z%d'% (p, q, r, s), 1j)
                        # YXZZ = QubitOperator('Y%d X%d Z%d Z%d'% (p, q, r, s), 1j)
                        # XZYZ = QubitOperator('X%d Z%d Y%d Z%d'% (p, q, r, s), 1j)
                        # YZXZ = QubitOperator('Y%d Z%d X%d Z%d'% (p, q, r, s), 1j)
                        # ZXZY = QubitOperator('Z%d X%d Z%d Y%d'% (p, q, r, s), 1j)
                        # ZYZX = QubitOperator('Z%d Y%d Z%d X%d'% (p, q, r, s), 1j)

                        # self.fermi_ops.append(ZZXY)
                        # self.fermi_ops.append(ZZYX)
                        # self.fermi_ops.append(XZZY)
                        # self.fermi_ops.append(YZZX)
                        # self.fermi_ops.append(ZXYZ)
                        # self.fermi_ops.append(ZYXZ)
                        # self.fermi_ops.append(XYZZ)
                        # self.fermi_ops.append(YXZZ)
                        # self.fermi_ops.append(XZYZ)
                        # self.fermi_ops.append(YZXZ)
                        # self.fermi_ops.append(ZXZY)
                        # self.fermi_ops.append(ZYZX)

                        # XXYY = QubitOperator('X%d X%d Y%d Y%d'% (p, q, r, s), 1j)
                        # XYXY = QubitOperator('X%d Y%d X%d Y%d'% (p, q, r, s), 1j)
                        # XYYX = QubitOperator('X%d Y%d Y%d X%d'% (p, q, r, s), 1j)
                        # YYXX = QubitOperator('Y%d Y%d X%d X%d'% (p, q, r, s), 1j)
                        # YXXY = QubitOperator('Y%d X%d X%d Y%d'% (p, q, r, s), 1j)
                        # YXYX = QubitOperator('Y%d X%d Y%d X%d'% (p, q, r, s), 1j)

                        # self.fermi_ops.append(XXYY)
                        # self.fermi_ops.append(XYXY)
                        # self.fermi_ops.append(XYYX)
                        # self.fermi_ops.append(YYXX)
                        # self.fermi_ops.append(YXXY)
                        # self.fermi_ops.append(YXYX)

                        # XXXX = QubitOperator('X%d X%d X%d X%d'% (p, q, r, s), 1j)
                        # YYYY = QubitOperator('Y%d Y%d Y%d Y%d'% (p, q, r, s), 1j)

                        # self.fermi_ops.append(XXXX)
                        # self.fermi_ops.append(YYYY)                        
        
        np.random.shuffle(self.fermi_ops_1)
        for op in self.fermi_ops_1[:len(self.fermi_ops_1)//4]:
            self.fermi_ops.append(op)

        np.random.shuffle(self.fermi_ops_2)
        for op in self.fermi_ops_2[:len(self.fermi_ops_2)//4]:
            self.fermi_ops.append(op)

        np.random.shuffle(self.fermi_ops_3)
        for op in self.fermi_ops_3[:len(self.fermi_ops_3)//4]:
            self.fermi_ops.append(op)

        np.random.shuffle(self.fermi_ops_4)
        for op in self.fermi_ops_4[:len(self.fermi_ops_4)//4]:
            self.fermi_ops.append(op)

        for op in self.fermi_ops:
            print(op)

        self.n_ops = len(self.fermi_ops)
        print(" Number of operators: ", self.n_ops)        
        return

class qubits_A_new(OperatorPool):
    def generate_SQ_Operators(self):

        self.fermi_ops = []
        
        n_occ = self.n_occ
        n_vir = self.n_vir

                
        for p in range(0,2*self.n_orb):
            X = QubitOperator('X%d'% p, 0+1j)
            Y = QubitOperator('Y%d'% p, 0+1j)

            # self.fermi_ops.append(X)
        for p in range(0,2*self.n_orb):
            Z = QubitOperator('Z%d'% p, 0+1j)

            # self.fermi_ops.append(Z)

        for p in range(0,2*self.n_orb):

            for q in range(p+1,2*self.n_orb):

                ZZ = QubitOperator('Z%d Z%d'% (p, q), 0+1j)
                # self.fermi_ops.append(ZZ)

        for p in range(0,2*self.n_orb):
            for q in range(p+1,2*self.n_orb):

                XX = QubitOperator('X%d X%d'% (p, q), 0+1j)
                XY = QubitOperator('X%d Y%d'% (p, q), 0+1j)
                YX = QubitOperator('Y%d X%d'% (p, q), 0+1j)
                XZ = QubitOperator('X%d Z%d'% (p, q), 0+1j)
                YZ = QubitOperator('Y%d Z%d'% (p, q), 0+1j)
                YY = QubitOperator('Y%d Y%d'% (p, q), 0+1j)

                self.fermi_ops.append(XX)
                self.fermi_ops.append(YX)
                self.fermi_ops.append(XZ)
                self.fermi_ops.append(YZ)
                self.fermi_ops.append(YY)
                self.fermi_ops.append(XY)

                A =  QubitOperator('X%d Y%d'% (p, q), 0+1j)
                A -= QubitOperator('Y%d X%d'% (p, q), 0+1j)

                self.fermi_ops.append(A)
 

        for i in range(0,2*self.n_orb):
            for j in range(i+1, 2*self.n_orb):

                for k in range(j+1, 2*self.n_orb):

                    YXZ = QubitOperator('Y%d X%d Z%d'% (i, j, k), 1j)  
                    # XYZ = QubitOperator('X%d Y%d Z%d'% (i, j, k), 1j)
                    XZY = QubitOperator('X%d Z%d Y%d'% (i, j, k), 1j)
                    # YZX = QubitOperator('Y%d Z%d X%d'% (i, j, k), 1j)
                    ZXY = QubitOperator('Z%d X%d Y%d'% (i, j, k), 1j)
                    # ZYX = QubitOperator('Z%d X%d Y%d'% (i, j, k), 1j)
                    # ZZZ = QubitOperator('Z%d Z%d Z%d'% (i, j, k), 1j)
  
                    # # self.fermi_ops.append(XYZ)
                    # self.fermi_ops.append(YXZ)
                    # self.fermi_ops.append(XZY)
                    # # self.fermi_ops.append(YZX)  
                    # self.fermi_ops.append(ZXY)
                    # # self.fermi_ops.append(ZYX)
                    # # self.fermi_ops.append(ZZZ) 

                    XXY = QubitOperator('X%d X%d Y%d'% (i, j, k), 1j)
                    XYY = QubitOperator('X%d Y%d Y%d'% (i, j, k), 1j)

                    # self.fermi_ops.append(XXY)
                    # self.fermi_ops.append(XYY)

        for p in range(0,2*self.n_orb):
            for q in range(p+1,2*self.n_orb):
                for r in range(q+1,2*self.n_orb):
                    for s in range(r+1,2*self.n_orb):
                        XYYY = QubitOperator('X%d Y%d Y%d Y%d'% (p, q, r, s), 1j)
                        YXYY = QubitOperator('Y%d X%d Y%d Y%d'% (p, q, r, s), 1j)
                        YYXY = QubitOperator('Y%d Y%d X%d Y%d'% (p, q, r, s), 1j)
                        YYYX = QubitOperator('Y%d Y%d Y%d X%d'% (p, q, r, s), 1j)

                        # self.fermi_ops.append(XYYY)
                        # self.fermi_ops.append(YXYY)
                        # self.fermi_ops.append(YYXY)
                        # self.fermi_ops.append(YYYX)

                        # XXXY = QubitOperator('X%d X%d X%d Y%d'% (p, q, r, s), 1j)
                        # YXXX = QubitOperator('Y%d X%d X%d X%d'% (p, q, r, s), 1j)
                        # XYXX = QubitOperator('X%d Y%d X%d X%d'% (p, q, r, s), 1j)
                        # XXYX = QubitOperator('X%d X%d Y%d X%d'% (p, q, r, s), 1j)

                        # self.fermi_ops.append(XXXY)
                        # self.fermi_ops.append(XXYX)
                        # self.fermi_ops.append(XYXX)
                        # self.fermi_ops.append(YXXX)

                        # ZZXY = QubitOperator('Z%d Z%d X%d Y%d'% (p, q, r, s), 1j)
                        # ZZYX = QubitOperator('Z%d Z%d Y%d X%d'% (p, q, r, s), 1j)
                        # XZZY = QubitOperator('X%d Z%d Z%d Y%d'% (p, q, r, s), 1j)
                        # YZZX = QubitOperator('Y%d Z%d Z%d X%d'% (p, q, r, s), 1j)
                        # ZYXZ = QubitOperator('Z%d Y%d X%d Z%d'% (p, q, r, s), 1j)
                        # ZXYZ = QubitOperator('Z%d X%d Y%d Z%d'% (p, q, r, s), 1j)
                        # XYZZ = QubitOperator('X%d Y%d Z%d Z%d'% (p, q, r, s), 1j)
                        # YXZZ = QubitOperator('Y%d X%d Z%d Z%d'% (p, q, r, s), 1j)
                        # XZYZ = QubitOperator('X%d Z%d Y%d Z%d'% (p, q, r, s), 1j)
                        # YZXZ = QubitOperator('Y%d Z%d X%d Z%d'% (p, q, r, s), 1j)
                        # ZXZY = QubitOperator('Z%d X%d Z%d Y%d'% (p, q, r, s), 1j)
                        # ZYZX = QubitOperator('Z%d Y%d Z%d X%d'% (p, q, r, s), 1j)

                        # self.fermi_ops.append(ZZXY)
                        # self.fermi_ops.append(ZZYX)
                        # self.fermi_ops.append(XZZY)
                        # self.fermi_ops.append(YZZX)
                        # self.fermi_ops.append(ZXYZ)
                        # self.fermi_ops.append(ZYXZ)
                        # self.fermi_ops.append(XYZZ)
                        # self.fermi_ops.append(YXZZ)
                        # self.fermi_ops.append(XZYZ)
                        # self.fermi_ops.append(YZXZ)
                        # self.fermi_ops.append(ZXZY)
                        # self.fermi_ops.append(ZYZX)

                        # XXYY = QubitOperator('X%d X%d Y%d Y%d'% (p, q, r, s), 1j)
                        # XYXY = QubitOperator('X%d Y%d X%d Y%d'% (p, q, r, s), 1j)
                        # XYYX = QubitOperator('X%d Y%d Y%d X%d'% (p, q, r, s), 1j)
                        # YYXX = QubitOperator('Y%d Y%d X%d X%d'% (p, q, r, s), 1j)
                        # YXXY = QubitOperator('Y%d X%d X%d Y%d'% (p, q, r, s), 1j)
                        # YXYX = QubitOperator('Y%d X%d Y%d X%d'% (p, q, r, s), 1j)

                        # self.fermi_ops.append(XXYY)
                        # self.fermi_ops.append(XYXY)
                        # self.fermi_ops.append(XYYX)
                        # self.fermi_ops.append(YYXX)
                        # self.fermi_ops.append(YXXY)
                        # self.fermi_ops.append(YXYX)

                        # XXXX = QubitOperator('X%d X%d X%d X%d'% (p, q, r, s), 1j)
                        # YYYY = QubitOperator('Y%d Y%d Y%d Y%d'% (p, q, r, s), 1j)

                        # self.fermi_ops.append(XXXX)
                        # self.fermi_ops.append(YYYY)                        
 
                
        for op in self.fermi_ops:
            print(op)

        self.n_ops = len(self.fermi_ops)
        print(" Number of operators: ", self.n_ops)        
        return

class qubits2(OperatorPool):
    def generate_SQ_Operators(self):
        """
        n_orb is number of spatial orbitals assuming that spin orbitals are labelled
        0a,0b,1a,1b,2a,2b,3a,3b,....  -> 0,1,2,3,...
        """
        
        print(" Form singlet GSD operators")
        
        self.fermi_ops = []
        for p in range(0,self.n_orb):
            pa = 2*p
            pb = 2*p+1
 
            for q in range(p,self.n_orb):
                qa = 2*q
                qb = 2*q+1


                termA = QubitOperator('X%d Y%d'% (pa,qa), 1j)
                termA -= hermitian_conjugated(termA)
                self.fermi_ops.append(termA)

                termA = QubitOperator('Y%d X%d'% (pa,qa), 1j)
                termA -= hermitian_conjugated(termA)
                self.fermi_ops.append(termA)

                termA = QubitOperator('X%d Y%d'% (pb,qb), 1j)
                termA -= hermitian_conjugated(termA)
                self.fermi_ops.append(termA)

                termA = QubitOperator('Y%d X%d'% (pb,qb), 1j)
                termA -= hermitian_conjugated(termA)
                self.fermi_ops.append(termA)  

        pq = -1 
        for p in range(0,self.n_orb):
            pa = 2*p
            pb = 2*p+1
 
            for q in range(p,self.n_orb):
                qa = 2*q
                qb = 2*q+1
        
                pq += 1
        
                rs = -1 
                for r in range(0,self.n_orb):
                    ra = 2*r
                    rb = 2*r+1
                    
                    for s in range(r,self.n_orb):
                        sa = 2*s
                        sb = 2*s+1
                    
                        rs += 1
                    
                        if(pq > rs):
                            continue

                        OA = QubitOperator('X1', 0)
                        OB = QubitOperator('X1', 0)

                        # termA =  FermionOperator(((ra,1),(pa,0),(sa,1),(qa,0)), 2/np.sqrt(12))

                        OA =  QubitOperator('Y%d X%d X%d X%d'% (ra,sa,pa,qa), 1j)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)  

                        OA =  QubitOperator('X%d Y%d X%d X%d'% (ra,sa,pa,qa), 1j)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)  

                        OA =  QubitOperator('X%d X%d Y%d X%d'% (ra,sa,pa,qa), 1j)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)  

                        OA =  QubitOperator('X%d X%d X%d Y%d'% (ra,sa,pa,qa), 1j)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)  

                        OA =  QubitOperator('X%d Y%d Y%d Y%d'% (ra,sa,pa,qa), 1j)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)  

                        OA =  QubitOperator('Y%d X%d Y%d Y%d'% (ra,sa,pa,qa), 1j)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)  

                        OA =  QubitOperator('Y%d Y%d X%d Y%d'% (ra,sa,pa,qa), 1j)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)  
                        
                        OA =  QubitOperator('Y%d Y%d Y%d X%d'% (ra,sa,pa,qa), 1)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)  
                        

                        OA =  QubitOperator('X%d X%d X%d X%d'% (ra,sa,pa,qa), 1)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)  
                        
                        OA =  QubitOperator('Y%d Y%d Y%d Y%d'% (ra,sa,pa,qa), 1)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)  
                        
                        OA =  QubitOperator('X%d X%d Y%d Y%d'% (ra,sa,pa,qa), 1)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)  
                        
                        OA =  QubitOperator('X%d Y%d X%d Y%d'% (ra,sa,pa,qa), 1)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)  
                        
                        OA =  QubitOperator('Y%d X%d X%d Y%d'% (ra,sa,pa,qa), 1)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)  
                        
                        OA =  QubitOperator('X%d Y%d Y%d X%d'% (ra,sa,pa,qa), 1)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)  
                        
                        OA =  QubitOperator('Y%d Y%d X%d X%d'% (ra,sa,pa,qa), 1)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)  
                        
                        OA =  QubitOperator('Y%d X%d Y%d X%d'% (ra,sa,pa,qa), 1)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)  
                        
 
                        # termA += FermionOperator(((rb,1),(pb,0),(sb,1),(qb,0)), 2/np.sqrt(12))

                        OA =  QubitOperator('Y%d X%d X%d X%d'% (rb,sb,pb,qb), 1j)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)

                        OA =  QubitOperator('X%d Y%d X%d X%d'% (rb,sb,pb,qb), 1j)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA =  QubitOperator('X%d X%d Y%d X%d'% (rb,sb,pb,qb), 1j)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA =  QubitOperator('X%d X%d X%d Y%d'% (rb,sb,pb,qb), 1j)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA =  QubitOperator('X%d Y%d Y%d Y%d'% (rb,sb,pb,qb), 1j)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA =  QubitOperator('Y%d X%d Y%d Y%d'% (rb,sb,pb,qb), 1j)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA =  QubitOperator('Y%d Y%d X%d Y%d'% (rb,sb,pb,qb), 1j)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA =  QubitOperator('Y%d Y%d Y%d X%d'% (rb,sb,pb,qb), 1j)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        

                        OA =  QubitOperator('X%d X%d X%d X%d'% (rb,sb,pb,qb), 1)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA =  QubitOperator('Y%d Y%d Y%d Y%d'% (rb,sb,pb,qb), 1)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA =  QubitOperator('X%d X%d Y%d Y%d'% (rb,sb,pb,qb), 1)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA =  QubitOperator('X%d Y%d X%d Y%d'% (rb,sb,pb,qb), 1)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA =  QubitOperator('Y%d X%d X%d Y%d'% (rb,sb,pb,qb), 1)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA =  QubitOperator('X%d Y%d Y%d X%d'% (rb,sb,pb,qb), 1)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA =  QubitOperator('Y%d Y%d X%d X%d'% (rb,sb,pb,qb), 1)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA =  QubitOperator('Y%d X%d Y%d X%d'% (rb,sb,pb,qb), 1)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        

                        # termA += FermionOperator(((ra,1),(pa,0),(sb,1),(qb,0)), 1/np.sqrt(12))

                        OA  = QubitOperator('Y%d X%d X%d X%d'% (ra,sb,pa,qb), 1j)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('X%d Y%d X%d X%d'% (ra,sb,pa,qb), 1j)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('X%d X%d Y%d X%d'% (ra,sb,pa,qb), 1j)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('X%d X%d X%d Y%d'% (ra,sb,pa,qb), 1j)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('X%d Y%d Y%d Y%d'% (ra,sb,pa,qb), 1j)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('Y%d X%d Y%d Y%d'% (ra,sb,pa,qb), 1j)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('Y%d Y%d X%d Y%d'% (ra,sb,pa,qb), 1j)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('Y%d Y%d Y%d X%d'% (ra,sb,pa,qb), 1j)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        

                        OA  = QubitOperator('X%d X%d X%d X%d'% (ra,sb,pa,qb), 1)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('Y%d Y%d Y%d Y%d'% (ra,sb,pa,qb), 1)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('X%d X%d Y%d Y%d'% (ra,sb,pa,qb), 1)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('X%d Y%d X%d Y%d'% (ra,sb,pa,qb), 1)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('Y%d X%d X%d Y%d'% (ra,sb,pa,qb), 1)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('X%d Y%d Y%d X%d'% (ra,sb,pa,qb), 1)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('Y%d Y%d X%d X%d'% (ra,sb,pa,qb), 1)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('Y%d X%d Y%d X%d'% (ra,sb,pa,qb), 1)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        

                        # termA += FermionOperator(((rb,1),(pb,0),(sa,1),(qa,0)), 1/np.sqrt(12))

                        OA  = QubitOperator('Y%d X%d X%d X%d'% (rb,sa,pb,qa), 1j)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('X%d Y%d X%d X%d'% (rb,sa,pb,qa), 1j)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('X%d X%d Y%d X%d'% (rb,sa,pb,qa), 1j)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('X%d X%d X%d Y%d'% (rb,sa,pb,qa), 1j)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('X%d Y%d Y%d Y%d'% (rb,sa,pb,qa), 1j)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('Y%d X%d Y%d Y%d'% (rb,sa,pb,qa), 1j)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('Y%d Y%d X%d Y%d'% (rb,sa,pb,qa), 1j)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('Y%d Y%d Y%d X%d'% (rb,sa,pb,qa), 1j)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('X%d X%d X%d X%d'% (rb,sa,pb,qa), 1)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('Y%d Y%d Y%d Y%d'% (rb,sa,pb,qa), 1)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('X%d X%d Y%d Y%d'% (rb,sa,pb,qa), 1)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('X%d Y%d X%d Y%d'% (rb,sa,pb,qa), 1)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('Y%d X%d X%d Y%d'% (rb,sa,pb,qa), 1)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('X%d Y%d Y%d X%d'% (rb,sa,pb,qa), 1)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('Y%d Y%d X%d X%d'% (rb,sa,pb,qa), 1)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('Y%d X%d Y%d X%d'% (rb,sa,pb,qa), 1)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        

                        # termA += FermionOperator(((ra,1),(pb,0),(sb,1),(qa,0)), 1/np.sqrt(12))
                        
                        OA  = QubitOperator('Y%d X%d X%d X%d'% (ra,sb,pb,qa), 1j)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('X%d Y%d X%d X%d'% (ra,sb,pb,qa), 1j)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('X%d X%d Y%d X%d'% (ra,sb,pb,qa), 1j)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('X%d X%d X%d Y%d'% (ra,sb,pb,qa), 1j)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('X%d Y%d Y%d Y%d'% (ra,sb,pb,qa), 1j)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('Y%d X%d Y%d Y%d'% (ra,sb,pb,qa), 1j)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('Y%d Y%d X%d Y%d'% (ra,sb,pb,qa), 1j)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('Y%d Y%d Y%d X%d'% (ra,sb,pb,qa), 1j)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        

                        OA  = QubitOperator('X%d X%d X%d X%d'% (ra,sb,pb,qa), 1)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('Y%d Y%d Y%d Y%d'% (ra,sb,pb,qa), 1)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('X%d X%d Y%d Y%d'% (ra,sb,pb,qa), 1)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('X%d Y%d X%d Y%d'% (ra,sb,pb,qa), 1)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('Y%d X%d X%d Y%d'% (ra,sb,pb,qa), 1)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('X%d Y%d Y%d X%d'% (ra,sb,pb,qa), 1)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('Y%d Y%d X%d X%d'% (ra,sb,pb,qa), 1)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('Y%d X%d Y%d X%d'% (ra,sb,pb,qa), 1)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        

                        # termA += FermionOperator(((rb,1),(pa,0),(sa,1),(qb,0)), 1/np.sqrt(12))
                                                                
                        OA  = QubitOperator('Y%d X%d X%d X%d'% (rb,sa,pa,qb), 1j)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('X%d Y%d X%d X%d'% (rb,sa,pa,qb), 1j)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('X%d X%d Y%d X%d'% (rb,sa,pa,qb), 1j)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('X%d X%d X%d Y%d'% (rb,sa,pa,qb), 1j)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('X%d Y%d Y%d Y%d'% (rb,sa,pa,qb), 1j)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('Y%d X%d Y%d Y%d'% (rb,sa,pa,qb), 1j)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('Y%d Y%d X%d Y%d'% (rb,sa,pa,qb), 1j)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('Y%d Y%d Y%d X%d'% (rb,sa,pa,qb), 1j)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('X%d X%d X%d X%d'% (rb,sa,pa,qb), 1)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('Y%d Y%d Y%d Y%d'% (rb,sa,pa,qb), 1)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('X%d X%d Y%d Y%d'% (rb,sa,pa,qb), 1)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('X%d Y%d X%d Y%d'% (rb,sa,pa,qb), 1)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('Y%d X%d X%d Y%d'% (rb,sa,pa,qb), 1)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('X%d Y%d Y%d X%d'% (rb,sa,pa,qb), 1)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('Y%d Y%d X%d X%d'% (rb,sa,pa,qb), 1)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
                        OA  = QubitOperator('Y%d X%d Y%d X%d'% (rb,sa,pa,qb), 1)
                        OA -= hermitian_conjugated(OA)
                        self.fermi_ops.append(OA)
                        
        for op in self.fermi_ops:
            print(op)

        self.n_ops = len(self.fermi_ops)
        print(" Number of operators: ", self.n_ops)
        return 

class qubitsZ(OperatorPool):
    def generate_SQ_Operators(self):
        """
        0a,0b,1a,1b,2a,2b,3a,3b,....  -> 0,1,2,3,...
        """
        n_occ = self.n_occ
        n_vir = self.n_vir

        print(" Form singlet SD operators")
        self.fermi_ops = [] 

        # for p in range(0,2*self.n_orb):
        #     X = QubitOperator('X%d'% p, 0+1j)
        #     Y = QubitOperator('Y%d'% p, 0+1j)

        #     self.fermi_ops.append(X)
        # for p in range(0,2*self.n_orb):
        #     Z = QubitOperator('Z%d'% p, 0+1j)

        #     self.fermi_ops.append(Z)

        # for p in range(0,2*self.n_orb):

        #     for q in range(p+1,2*self.n_orb):

        #         ZZ = QubitOperator('Z%d Z%d'% (p, q), 0+1j)
        #         self.fermi_ops.append(ZZ)

        # for p in range(0,2*self.n_orb):
        #     for q in range(p+1,2*self.n_orb):

        #         XX = QubitOperator('X%d X%d'% (p, q), 0+1j)
        #         XY = QubitOperator('X%d Y%d'% (p, q), 0+1j)
        #         YX = QubitOperator('Y%d X%d'% (p, q), 0+1j)
        #         XZ = QubitOperator('X%d Z%d'% (p, q), 0+1j)
        #         YZ = QubitOperator('Y%d Z%d'% (p, q), 0+1j)
        #         YY = QubitOperator('Y%d Y%d'% (p, q), 0+1j)

        #         self.fermi_ops.append(XX)
        #         self.fermi_ops.append(YX)
        #         self.fermi_ops.append(XZ)
        #         self.fermi_ops.append(YZ)
        #         self.fermi_ops.append(YY)
        #         self.fermi_ops.append(XY)


        # for i in range(0,2*self.n_orb):
        #     for j in range(i+1, 2*self.n_orb):

        #         for k in range(j+1, 2*self.n_orb):

        #             YXZ = QubitOperator('Y%d X%d Z%d'% (i, j, k), 1j)  
        #             XYZ = QubitOperator('X%d Y%d Z%d'% (i, j, k), 1j)
        #             XZY = QubitOperator('X%d Z%d Y%d'% (i, j, k), 1j)
        #             YZX = QubitOperator('Y%d Z%d X%d'% (i, j, k), 1j)
        #             ZXY = QubitOperator('Z%d X%d Y%d'% (i, j, k), 1j)
        #             ZYX = QubitOperator('Z%d X%d Y%d'% (i, j, k), 1j)
  
        #             self.fermi_ops.append(XYZ)
        #             self.fermi_ops.append(YXZ)
        #             self.fermi_ops.append(XZY)
        #             self.fermi_ops.append(YZX)  
        #             self.fermi_ops.append(ZXY)
        #             self.fermi_ops.append(ZYX) 

        #             XXY = QubitOperator('X%d X%d Y%d'% (i, j, k), 1j)
        #             XYY = QubitOperator('X%d Y%d Y%d'% (i, j, k), 1j)

        #             self.fermi_ops.append(XXY)
        #             self.fermi_ops.append(XYY)

        # for p in range(0,2*self.n_orb):
        #     for q in range(p+1,2*self.n_orb):
        #         for r in range(q+1,2*self.n_orb):
        #             for s in range(r+1,2*self.n_orb):
        #                 XYYY = QubitOperator('X%d Y%d Y%d Y%d'% (p, q, r, s), 1j)
        #                 YXYY = QubitOperator('Y%d X%d Y%d Y%d'% (p, q, r, s), 1j)
        #                 YYXY = QubitOperator('Y%d Y%d X%d Y%d'% (p, q, r, s), 1j)
        #                 YYYX = QubitOperator('Y%d Y%d Y%d X%d'% (p, q, r, s), 1j)

        #                 self.fermi_ops.append(XYYY)
        #                 self.fermi_ops.append(YXYY)
        #                 self.fermi_ops.append(YYXY)
        #                 self.fermi_ops.append(YYYX)

        #                 XXXY = QubitOperator('X%d X%d X%d Y%d'% (p, q, r, s), 1j)
        #                 YXXX = QubitOperator('Y%d X%d X%d X%d'% (p, q, r, s), 1j)
        #                 XYXX = QubitOperator('X%d Y%d X%d X%d'% (p, q, r, s), 1j)
        #                 XXYX = QubitOperator('X%d X%d Y%d X%d'% (p, q, r, s), 1j)

        #                 self.fermi_ops.append(XXXY)
        #                 self.fermi_ops.append(XXYX)
        #                 self.fermi_ops.append(XYXX)
        #                 self.fermi_ops.append(YXXX)

        #                 ZZXY = QubitOperator('Z%d Z%d X%d Y%d'% (p, q, r, s), 1j)
        #                 ZZYX = QubitOperator('Z%d Z%d Y%d X%d'% (p, q, r, s), 1j)
        #                 XZZY = QubitOperator('X%d Z%d Z%d Y%d'% (p, q, r, s), 1j)
        #                 YZZX = QubitOperator('Y%d Z%d Z%d X%d'% (p, q, r, s), 1j)
        #                 ZYXZ = QubitOperator('Z%d Y%d X%d Z%d'% (p, q, r, s), 1j)
        #                 ZXYZ = QubitOperator('Z%d X%d Y%d Z%d'% (p, q, r, s), 1j)
        #                 XYZZ = QubitOperator('X%d Y%d Z%d Z%d'% (p, q, r, s), 1j)
        #                 YXZZ = QubitOperator('Y%d X%d Z%d Z%d'% (p, q, r, s), 1j)
        #                 XZYZ = QubitOperator('X%d Z%d Y%d Z%d'% (p, q, r, s), 1j)
        #                 YZXZ = QubitOperator('Y%d Z%d X%d Z%d'% (p, q, r, s), 1j)
        #                 ZXZY = QubitOperator('Z%d X%d Z%d Y%d'% (p, q, r, s), 1j)
        #                 ZYZX = QubitOperator('Z%d Y%d Z%d X%d'% (p, q, r, s), 1j)

        #                 self.fermi_ops.append(ZZXY)
        #                 self.fermi_ops.append(ZZYX)
        #                 self.fermi_ops.append(XZZY)
        #                 self.fermi_ops.append(YZZX)
        #                 self.fermi_ops.append(ZXYZ)
        #                 self.fermi_ops.append(ZYXZ)
        #                 self.fermi_ops.append(XYZZ)
        #                 self.fermi_ops.append(YXZZ)
        #                 self.fermi_ops.append(XZYZ)
        #                 self.fermi_ops.append(YZXZ)
        #                 self.fermi_ops.append(ZXZY)
        #                 self.fermi_ops.append(ZYZX)
        
        for p in range(0,2*self.n_orb):
            for q in range(0,2*self.n_orb):
                    
                termA =  FermionOperator(((p,1),(q,0)), 1)
                
                termAQ = openfermion.transforms.jordan_wigner(termA)
                print(termAQ)
               
                #Normalize
                coeffA = 0
                for t in termAQ.terms:
                    self.fermi_ops.append(QubitOperator(t,1j))
                    print(t)
       
        pq = -1 
        for p in range(0,self.n_orb):
            pa = 2*p
            pb = 2*p+1
 
            for q in range(p,self.n_orb):
                qa = 2*q
                qb = 2*q+1
        
                pq += 1
        
                rs = -1 
                for r in range(0,self.n_orb):
                    ra = 2*r
                    rb = 2*r+1
                    
                    for s in range(r,self.n_orb):
                        sa = 2*s
                        sb = 2*s+1
                    
                        rs += 1
                    
                        if(pq > rs):
                            continue

                        termA =  FermionOperator(((ra,1),(pa,0),(sa,1),(qa,0)), 1)

                        termAQ = openfermion.transforms.jordan_wigner(termA)
                        print(termAQ)

                        for t in termAQ.terms:
                            self.fermi_ops.append(QubitOperator(t,1j))
                            print(t)

                        termA =  FermionOperator(((rb,1),(pb,0),(sb,1),(qb,0)), 1)

                        termAQ = openfermion.transforms.jordan_wigner(termA)
                        print(termAQ)

                        for t in termAQ.terms:
                            self.fermi_ops.append(QubitOperator(t,1j))
                            print(t)

                        termA =  FermionOperator(((ra,1),(pa,0),(sb,1),(qb,0)), 1)

                        termAQ = openfermion.transforms.jordan_wigner(termA)
                        print(termAQ)

                        for t in termAQ.terms:
                            self.fermi_ops.append(QubitOperator(t,1j))
                            print(t)

                        termA =  FermionOperator(((rb,1),(pb,0),(sa,1),(qa,0)), 1)

                        termAQ = openfermion.transforms.jordan_wigner(termA)
                        print(termAQ)

                        for t in termAQ.terms:
                            self.fermi_ops.append(QubitOperator(t,1j))
                            print(t)

                        termA =  FermionOperator(((ra,1),(pb,0),(sb,1),(qa,0)), 1)

                        termAQ = openfermion.transforms.jordan_wigner(termA)
                        print(termAQ)

                        for t in termAQ.terms:
                            self.fermi_ops.append(QubitOperator(t,1j))
                            print(t)

                        termA =  FermionOperator(((rb,1),(pa,0),(sa,1),(qb,0)), 1)

                        termAQ = openfermion.transforms.jordan_wigner(termA)
                        print(termAQ)

                        for t in termAQ.terms:
                            self.fermi_ops.append(QubitOperator(t,1j))
                            print(t)


        for op in self.fermi_ops:
            print(op)
        
        self.n_ops = len(self.fermi_ops)
        print(" Number of operators: ", self.n_ops)
        return 

class qubits_spin(OperatorPool):
    def generate_SQ_Operators(self):
        """
        n_orb is number of spatial orbitals assuming that spin orbitals are labelled
        0a,0b,1a,1b,2a,2b,3a,3b,....  -> 0,1,2,3,...
        """
        
        print(" Form singlet GSD operators")
        
        self.fermi_ops = []
        for p in range(0,self.n_orb):
            pa = 2*p
            pb = 2*p+1
 
            for q in range(p,self.n_orb):
                qa = 2*q
                qb = 2*q+1


                termA =  QubitOperator('X%d Y%d'% (pa,qa), 1j)
                termA += QubitOperator('X%d Y%d'% (pb,qb), 1j)
                termA -= hermitian_conjugated(termA)
                coeffA = 0

                for t in termA.terms:
                    coeff_t = termA.terms[t]
                    coeffA += coeff_t * coeff_t

                if np.abs(coeffA) > 1e-6:
                  self.fermi_ops.append(termA)

                termA = QubitOperator('Y%d X%d'% (pa,qa), 1j)
                termA += QubitOperator('Y%d X%d'% (pb,qb), 1j)
                termA -= hermitian_conjugated(termA)
                coeffA = 0

                for t in termA.terms:
                    coeff_t = termA.terms[t]
                    coeffA += coeff_t * coeff_t

                if np.abs(coeffA) > 1e-6:
                  self.fermi_ops.append(termA)

        pq = -1 
        for p in range(0,self.n_orb):
            pa = 2*p
            pb = 2*p+1
 
            for q in range(p,self.n_orb):
                qa = 2*q
                qb = 2*q+1
        
                pq += 1
        
                rs = -1 
                for r in range(0,self.n_orb):
                    ra = 2*r
                    rb = 2*r+1
                    
                    for s in range(r,self.n_orb):
                        sa = 2*s
                        sb = 2*s+1
                    
                        rs += 1
                    
                        if(pq > rs):
                            continue

                        OA = QubitOperator('X1', 0)
                        OB = QubitOperator('X1', 0)

                        # YXXX

                        OA += QubitOperator('Y%d X%d X%d X%d'% (ra,sa,pa,qa), 1j*2/np.sqrt(12))
                        OA += QubitOperator('Y%d X%d X%d X%d'% (rb,sb,pb,qb), 1j*2/np.sqrt(12))
                        OA += QubitOperator('Y%d X%d X%d X%d'% (ra,sb,pa,qb), 1j/np.sqrt(12))
                        OA += QubitOperator('Y%d X%d X%d X%d'% (rb,sa,pb,qa), 1j/np.sqrt(12))
                        OA += QubitOperator('Y%d X%d X%d X%d'% (ra,sb,pb,qa), 1j/np.sqrt(12))
                        OA += QubitOperator('Y%d X%d X%d X%d'% (rb,sa,pa,qb), 1j/np.sqrt(12))

                        OB += QubitOperator('Y%d X%d X%d X%d'% (ra,sb,pa,qb), 1j/2)
                        OB += QubitOperator('Y%d X%d X%d X%d'% (rb,sa,pb,qa), 1j/2)
                        OB -= QubitOperator('Y%d X%d X%d X%d'% (ra,sb,pb,qa), 1j/2)
                        OB -= QubitOperator('Y%d X%d X%d X%d'% (rb,sa,pa,qb), 1j/2)

                        OA -= hermitian_conjugated(OA)

                        OB -= hermitian_conjugated(OB)

                        coeffA = 0
                        coeffB = 0

                        for t in OA.terms:
                            coeff_t = OA.terms[t]
                            coeffA += coeff_t * coeff_t

                        if np.abs(coeffA) > 1e-6:
                          self.fermi_ops.append(OA)

                        for t in OB.terms:
                            coeff_t = OB.terms[t]
                            coeffB += coeff_t * coeff_t
                            
                        if np.abs(coeffB) > 1e-6:
                          self.fermi_ops.append(OB)

                        # XYXX

                        OA = QubitOperator('X1', 0)
                        OB = QubitOperator('X1', 0)

                        OA += QubitOperator('X%d Y%d X%d X%d'% (ra,sa,pa,qa), 1j*2/np.sqrt(12))
                        OA += QubitOperator('X%d Y%d X%d X%d'% (rb,sb,pb,qb), 1j*2/np.sqrt(12))
                        OA += QubitOperator('X%d Y%d X%d X%d'% (ra,sb,pa,qb), 1j/np.sqrt(12))
                        OA += QubitOperator('X%d Y%d X%d X%d'% (rb,sa,pb,qa), 1j/np.sqrt(12))
                        OA += QubitOperator('X%d Y%d X%d X%d'% (ra,sb,pb,qa), 1j/np.sqrt(12))
                        OA += QubitOperator('X%d Y%d X%d X%d'% (rb,sa,pa,qb), 1j/np.sqrt(12))

                        OB += QubitOperator('X%d Y%d X%d X%d'% (ra,sb,pa,qb), 1j/2)
                        OB += QubitOperator('X%d Y%d X%d X%d'% (rb,sa,pb,qa), 1j/2)
                        OB -= QubitOperator('X%d Y%d X%d X%d'% (ra,sb,pb,qa), 1j/2)
                        OB -= QubitOperator('X%d Y%d X%d X%d'% (rb,sa,pa,qb), 1j/2)

                        OA -= hermitian_conjugated(OA)

                        OB -= hermitian_conjugated(OB)

                        coeffA = 0
                        coeffB = 0

                        for t in OA.terms:
                            coeff_t = OA.terms[t]
                            coeffA += coeff_t * coeff_t

                        if np.abs(coeffA) > 1e-6:
                          self.fermi_ops.append(OA)

                        for t in OB.terms:
                            coeff_t = OB.terms[t]
                            coeffB += coeff_t * coeff_t
                            
                        if np.abs(coeffB) > 1e-6:
                          self.fermi_ops.append(OB)

                        # XXYX

                        OA = QubitOperator('X1', 0)
                        OB = QubitOperator('X1', 0)

                        OA += QubitOperator('X%d X%d Y%d X%d'% (ra,sa,pa,qa), -1j*2/np.sqrt(12))
                        OA += QubitOperator('X%d X%d Y%d X%d'% (rb,sb,pb,qb), -1j*2/np.sqrt(12))
                        OA += QubitOperator('X%d X%d Y%d X%d'% (ra,sb,pa,qb), -1j/np.sqrt(12))
                        OA += QubitOperator('X%d X%d Y%d X%d'% (rb,sa,pb,qa), -1j/np.sqrt(12))
                        OA += QubitOperator('X%d X%d Y%d X%d'% (ra,sb,pb,qa), -1j/np.sqrt(12))
                        OA += QubitOperator('X%d X%d Y%d X%d'% (rb,sa,pa,qb), -1j/np.sqrt(12))

                        OB += QubitOperator('X%d X%d Y%d X%d'% (ra,sb,pa,qb), -1j/2)
                        OB += QubitOperator('X%d X%d Y%d X%d'% (rb,sa,pb,qa), -1j/2)
                        OB -= QubitOperator('X%d X%d Y%d X%d'% (ra,sb,pb,qa), -1j/2)
                        OB -= QubitOperator('X%d X%d Y%d X%d'% (rb,sa,pa,qb), -1j/2)

                        OA -= hermitian_conjugated(OA)

                        OB -= hermitian_conjugated(OB)

                        coeffA = 0
                        coeffB = 0

                        for t in OA.terms:
                            coeff_t = OA.terms[t]
                            coeffA += coeff_t * coeff_t

                        if np.abs(coeffA) > 1e-6:
                          self.fermi_ops.append(OA)

                        for t in OB.terms:
                            coeff_t = OB.terms[t]
                            coeffB += coeff_t * coeff_t
                            
                        if np.abs(coeffB) > 1e-6:
                          self.fermi_ops.append(OB)

                        # XXXY

                        OA = QubitOperator('X1', 0)
                        OB = QubitOperator('X1', 0)

                        OA += QubitOperator('X%d X%d X%d Y%d'% (ra,sa,pa,qa), -1j*2/np.sqrt(12))
                        OA += QubitOperator('X%d X%d X%d Y%d'% (rb,sb,pb,qb), -1j*2/np.sqrt(12))
                        OA += QubitOperator('X%d X%d X%d Y%d'% (ra,sb,pa,qb), -1j/np.sqrt(12))
                        OA += QubitOperator('X%d X%d X%d Y%d'% (rb,sa,pb,qa), -1j/np.sqrt(12))
                        OA += QubitOperator('X%d X%d X%d Y%d'% (ra,sb,pb,qa), -1j/np.sqrt(12))
                        OA += QubitOperator('X%d X%d X%d Y%d'% (rb,sa,pa,qb), -1j/np.sqrt(12))

                        OB += QubitOperator('X%d X%d X%d Y%d'% (ra,sb,pa,qb), -1j/2)
                        OB += QubitOperator('X%d X%d X%d Y%d'% (rb,sa,pb,qa), -1j/2)
                        OB -= QubitOperator('X%d X%d X%d Y%d'% (ra,sb,pb,qa), -1j/2)
                        OB -= QubitOperator('X%d X%d X%d Y%d'% (rb,sa,pa,qb), -1j/2)

                        OA -= hermitian_conjugated(OA)

                        OB -= hermitian_conjugated(OB)

                        coeffA = 0
                        coeffB = 0

                        for t in OA.terms:
                            coeff_t = OA.terms[t]
                            coeffA += coeff_t * coeff_t

                        if np.abs(coeffA) > 1e-6:
                          self.fermi_ops.append(OA)

                        for t in OB.terms:
                            coeff_t = OB.terms[t]
                            coeffB += coeff_t * coeff_t
                            
                        if np.abs(coeffB) > 1e-6:
                          self.fermi_ops.append(OB)

                        # XYYY

                        OA = QubitOperator('X1', 0)
                        OB = QubitOperator('X1', 0)

                        OA += QubitOperator('X%d Y%d Y%d Y%d'% (ra,sa,pa,qa), -1j*2/np.sqrt(12))
                        OA += QubitOperator('X%d Y%d Y%d Y%d'% (rb,sb,pb,qb), -1j*2/np.sqrt(12))
                        OA += QubitOperator('X%d Y%d Y%d Y%d'% (ra,sb,pa,qb), -1j/np.sqrt(12))
                        OA += QubitOperator('X%d Y%d Y%d Y%d'% (rb,sa,pb,qa), -1j/np.sqrt(12))
                        OA += QubitOperator('X%d Y%d Y%d Y%d'% (ra,sb,pb,qa), -1j/np.sqrt(12))
                        OA += QubitOperator('X%d Y%d Y%d Y%d'% (rb,sa,pa,qb), -1j/np.sqrt(12))

                        OB += QubitOperator('X%d Y%d Y%d Y%d'% (ra,sb,pa,qb), -1j/2)
                        OB += QubitOperator('X%d Y%d Y%d Y%d'% (rb,sa,pb,qa), -1j/2)
                        OB -= QubitOperator('X%d Y%d Y%d Y%d'% (ra,sb,pb,qa), -1j/2)
                        OB -= QubitOperator('X%d Y%d Y%d Y%d'% (rb,sa,pa,qb), -1j/2)

                        OA -= hermitian_conjugated(OA)

                        OB -= hermitian_conjugated(OB)

                        coeffA = 0
                        coeffB = 0

                        for t in OA.terms:
                            coeff_t = OA.terms[t]
                            coeffA += coeff_t * coeff_t

                        if np.abs(coeffA) > 1e-6:
                          self.fermi_ops.append(OA)

                        for t in OB.terms:
                            coeff_t = OB.terms[t]
                            coeffB += coeff_t * coeff_t
                            
                        if np.abs(coeffB) > 1e-6:
                          self.fermi_ops.append(OB)

                        # YXYY

                        OA = QubitOperator('X1', 0)
                        OB = QubitOperator('X1', 0)

                        OA += QubitOperator('Y%d X%d Y%d Y%d'% (ra,sa,pa,qa), -1j*2/np.sqrt(12))
                        OA += QubitOperator('Y%d X%d Y%d Y%d'% (rb,sb,pb,qb), -1j*2/np.sqrt(12))
                        OA += QubitOperator('Y%d X%d Y%d Y%d'% (ra,sb,pa,qb), -1j/np.sqrt(12))
                        OA += QubitOperator('Y%d X%d Y%d Y%d'% (rb,sa,pb,qa), -1j/np.sqrt(12))
                        OA += QubitOperator('Y%d X%d Y%d Y%d'% (ra,sb,pb,qa), -1j/np.sqrt(12))
                        OA += QubitOperator('Y%d X%d Y%d Y%d'% (rb,sa,pa,qb), -1j/np.sqrt(12))

                        OB += QubitOperator('Y%d X%d Y%d Y%d'% (ra,sb,pa,qb), -1j/2)
                        OB += QubitOperator('Y%d X%d Y%d Y%d'% (rb,sa,pb,qa), -1j/2)
                        OB -= QubitOperator('Y%d X%d Y%d Y%d'% (ra,sb,pb,qa), -1j/2)
                        OB -= QubitOperator('Y%d X%d Y%d Y%d'% (rb,sa,pa,qb), -1j/2)

                        OA -= hermitian_conjugated(OA)

                        OB -= hermitian_conjugated(OB)

                        coeffA = 0
                        coeffB = 0

                        for t in OA.terms:
                            coeff_t = OA.terms[t]
                            coeffA += coeff_t * coeff_t

                        if np.abs(coeffA) > 1e-6:
                          self.fermi_ops.append(OA)

                        for t in OB.terms:
                            coeff_t = OB.terms[t]
                            coeffB += coeff_t * coeff_t
                            
                        if np.abs(coeffB) > 1e-6:
                          self.fermi_ops.append(OB)

                        # YYXY

                        OA = QubitOperator('X1', 0)
                        OB = QubitOperator('X1', 0)

                        OA += QubitOperator('Y%d Y%d X%d Y%d'% (ra,sa,pa,qa), 1j*2/np.sqrt(12))
                        OA += QubitOperator('Y%d Y%d X%d Y%d'% (rb,sb,pb,qb), 1j*2/np.sqrt(12))
                        OA += QubitOperator('Y%d Y%d X%d Y%d'% (ra,sb,pa,qb), 1j/np.sqrt(12))
                        OA += QubitOperator('Y%d Y%d X%d Y%d'% (rb,sa,pb,qa), 1j/np.sqrt(12))
                        OA += QubitOperator('Y%d Y%d X%d Y%d'% (ra,sb,pb,qa), 1j/np.sqrt(12))
                        OA += QubitOperator('Y%d Y%d X%d Y%d'% (rb,sa,pa,qb), 1j/np.sqrt(12))

                        OB += QubitOperator('Y%d Y%d X%d Y%d'% (ra,sb,pa,qb), 1j/2)
                        OB += QubitOperator('Y%d Y%d X%d Y%d'% (rb,sa,pb,qa), 1j/2)
                        OB -= QubitOperator('Y%d Y%d X%d Y%d'% (ra,sb,pb,qa), 1j/2)
                        OB -= QubitOperator('Y%d Y%d X%d Y%d'% (rb,sa,pa,qb), 1j/2)

                        OA -= hermitian_conjugated(OA)

                        OB -= hermitian_conjugated(OB)

                        coeffA = 0
                        coeffB = 0

                        for t in OA.terms:
                            coeff_t = OA.terms[t]
                            coeffA += coeff_t * coeff_t

                        if np.abs(coeffA) > 1e-6:
                          self.fermi_ops.append(OA)

                        for t in OB.terms:
                            coeff_t = OB.terms[t]
                            coeffB += coeff_t * coeff_t
                            
                        if np.abs(coeffB) > 1e-6:
                          self.fermi_ops.append(OB)

                        # YYYX

                        OA = QubitOperator('X1', 0)
                        OB = QubitOperator('X1', 0)

                        OA += QubitOperator('Y%d Y%d Y%d X%d'% (ra,sa,pa,qa), 1j*2/np.sqrt(12))
                        OA += QubitOperator('Y%d Y%d Y%d X%d'% (rb,sb,pb,qb), 1j*2/np.sqrt(12))
                        OA += QubitOperator('Y%d Y%d Y%d X%d'% (ra,sb,pa,qb), 1j/np.sqrt(12))
                        OA += QubitOperator('Y%d Y%d Y%d X%d'% (rb,sa,pb,qa), 1j/np.sqrt(12))
                        OA += QubitOperator('Y%d Y%d Y%d X%d'% (ra,sb,pb,qa), 1j/np.sqrt(12))
                        OA += QubitOperator('Y%d Y%d Y%d X%d'% (rb,sa,pa,qb), 1j/np.sqrt(12))

                        OB += QubitOperator('Y%d Y%d Y%d X%d'% (ra,sb,pa,qb), 1j/2)
                        OB += QubitOperator('Y%d Y%d Y%d X%d'% (rb,sa,pb,qa), 1j/2)
                        OB -= QubitOperator('Y%d Y%d Y%d X%d'% (ra,sb,pb,qa), 1j/2)
                        OB -= QubitOperator('Y%d Y%d Y%d X%d'% (rb,sa,pa,qb), 1j/2)

                        OA -= hermitian_conjugated(OA)

                        OB -= hermitian_conjugated(OB)

                        coeffA = 0
                        coeffB = 0

                        for t in OA.terms:
                            coeff_t = OA.terms[t]
                            coeffA += coeff_t * coeff_t

                        if np.abs(coeffA) > 1e-6:
                          self.fermi_ops.append(OA)

                        for t in OB.terms:
                            coeff_t = OB.terms[t]
                            coeffB += coeff_t * coeff_t
                            
                        if np.abs(coeffB) > 1e-6:
                          self.fermi_ops.append(OB)

                        # XXXX

                        OA = QubitOperator('X1', 0)
                        OB = QubitOperator('X1', 0)

                        OA += QubitOperator('X%d X%d X%d X%d'% (ra,sa,pa,qa), 2/np.sqrt(12))
                        OA += QubitOperator('X%d X%d X%d X%d'% (rb,sb,pb,qb), 2/np.sqrt(12))
                        OA += QubitOperator('X%d X%d X%d X%d'% (ra,sb,pa,qb), 1/np.sqrt(12))
                        OA += QubitOperator('X%d X%d X%d X%d'% (rb,sa,pb,qa), 1/np.sqrt(12))
                        OA += QubitOperator('X%d X%d X%d X%d'% (ra,sb,pb,qa), 1/np.sqrt(12))
                        OA += QubitOperator('X%d X%d X%d X%d'% (rb,sa,pa,qb), 1/np.sqrt(12))

                        OB += QubitOperator('X%d X%d X%d X%d'% (ra,sb,pa,qb), 1/2)
                        OB += QubitOperator('X%d X%d X%d X%d'% (rb,sa,pb,qa), 1/2)
                        OB -= QubitOperator('X%d X%d X%d X%d'% (ra,sb,pb,qa), 1/2)
                        OB -= QubitOperator('X%d X%d X%d X%d'% (rb,sa,pa,qb), 1/2)

                        OA -= hermitian_conjugated(OA)

                        OB -= hermitian_conjugated(OB)

                        coeffA = 0
                        coeffB = 0

                        for t in OA.terms:
                            coeff_t = OA.terms[t]
                            coeffA += coeff_t * coeff_t

                        if np.abs(coeffA) > 1e-6:
                          self.fermi_ops.append(OA)

                        for t in OB.terms:
                            coeff_t = OB.terms[t]
                            coeffB += coeff_t * coeff_t
                            
                        if np.abs(coeffB) > 1e-6:
                          self.fermi_ops.append(OB)

                        # YYYY

                        OA = QubitOperator('X1', 0)
                        OB = QubitOperator('X1', 0)

                        OA += QubitOperator('Y%d Y%d Y%d Y%d'% (ra,sa,pa,qa), 2/np.sqrt(12))
                        OA += QubitOperator('Y%d Y%d Y%d Y%d'% (rb,sb,pb,qb), 2/np.sqrt(12))
                        OA += QubitOperator('Y%d Y%d Y%d Y%d'% (ra,sb,pa,qb), 1/np.sqrt(12))
                        OA += QubitOperator('Y%d Y%d Y%d Y%d'% (rb,sa,pb,qa), 1/np.sqrt(12))
                        OA += QubitOperator('Y%d Y%d Y%d Y%d'% (ra,sb,pb,qa), 1/np.sqrt(12))
                        OA += QubitOperator('Y%d Y%d Y%d Y%d'% (rb,sa,pa,qb), 1/np.sqrt(12))

                        OB += QubitOperator('Y%d Y%d Y%d Y%d'% (ra,sb,pa,qb), 1/2)
                        OB += QubitOperator('Y%d Y%d Y%d Y%d'% (rb,sa,pb,qa), 1/2)
                        OB -= QubitOperator('Y%d Y%d Y%d Y%d'% (ra,sb,pb,qa), 1/2)
                        OB -= QubitOperator('Y%d Y%d Y%d Y%d'% (rb,sa,pa,qb), 1/2)

                        OA -= hermitian_conjugated(OA)

                        OB -= hermitian_conjugated(OB)

                        coeffA = 0
                        coeffB = 0

                        for t in OA.terms:
                            coeff_t = OA.terms[t]
                            coeffA += coeff_t * coeff_t

                        if np.abs(coeffA) > 1e-6:
                          self.fermi_ops.append(OA)

                        for t in OB.terms:
                            coeff_t = OB.terms[t]
                            coeffB += coeff_t * coeff_t
                            
                        if np.abs(coeffB) > 1e-6:
                          self.fermi_ops.append(OB)

                        # XXYY

                        OA = QubitOperator('X1', 0)
                        OB = QubitOperator('X1', 0)

                        OA += QubitOperator('X%d X%d Y%d Y%d'% (ra,sa,pa,qa), -2/np.sqrt(12))
                        OA += QubitOperator('X%d X%d Y%d Y%d'% (rb,sb,pb,qb), -2/np.sqrt(12))
                        OA += QubitOperator('X%d X%d Y%d Y%d'% (ra,sb,pa,qb), -1/np.sqrt(12))
                        OA += QubitOperator('X%d X%d Y%d Y%d'% (rb,sa,pb,qa), -1/np.sqrt(12))
                        OA += QubitOperator('X%d X%d Y%d Y%d'% (ra,sb,pb,qa), -1/np.sqrt(12))
                        OA += QubitOperator('X%d X%d Y%d Y%d'% (rb,sa,pa,qb), -1/np.sqrt(12))

                        OB += QubitOperator('X%d X%d Y%d Y%d'% (ra,sb,pa,qb), -1/2)
                        OB += QubitOperator('X%d X%d Y%d Y%d'% (rb,sa,pb,qa), -1/2)
                        OB -= QubitOperator('X%d X%d Y%d Y%d'% (ra,sb,pb,qa), -1/2)
                        OB -= QubitOperator('X%d X%d Y%d Y%d'% (rb,sa,pa,qb), -1/2)

                        OA -= hermitian_conjugated(OA)

                        OB -= hermitian_conjugated(OB)

                        coeffA = 0
                        coeffB = 0

                        for t in OA.terms:
                            coeff_t = OA.terms[t]
                            coeffA += coeff_t * coeff_t

                        if np.abs(coeffA) > 1e-6:
                          self.fermi_ops.append(OA)

                        for t in OB.terms:
                            coeff_t = OB.terms[t]
                            coeffB += coeff_t * coeff_t
                            
                        if np.abs(coeffB) > 1e-6:
                          self.fermi_ops.append(OB)

                        # XYXY

                        OA = QubitOperator('X1', 0)
                        OB = QubitOperator('X1', 0)

                        OA += QubitOperator('X%d Y%d X%d Y%d'% (ra,sa,pa,qa), 2/np.sqrt(12))
                        OA += QubitOperator('X%d Y%d X%d Y%d'% (rb,sb,pb,qb), 2/np.sqrt(12))
                        OA += QubitOperator('X%d Y%d X%d Y%d'% (ra,sb,pa,qb), 1/np.sqrt(12))
                        OA += QubitOperator('X%d Y%d X%d Y%d'% (rb,sa,pb,qa), 1/np.sqrt(12))
                        OA += QubitOperator('X%d Y%d X%d Y%d'% (ra,sb,pb,qa), 1/np.sqrt(12))
                        OA += QubitOperator('X%d Y%d X%d Y%d'% (rb,sa,pa,qb), 1/np.sqrt(12))

                        OB += QubitOperator('X%d Y%d X%d Y%d'% (ra,sb,pa,qb), 1/2)
                        OB += QubitOperator('X%d Y%d X%d Y%d'% (rb,sa,pb,qa), 1/2)
                        OB -= QubitOperator('X%d Y%d X%d Y%d'% (ra,sb,pb,qa), 1/2)
                        OB -= QubitOperator('X%d Y%d X%d Y%d'% (rb,sa,pa,qb), 1/2)

                        OA -= hermitian_conjugated(OA)

                        OB -= hermitian_conjugated(OB)

                        coeffA = 0
                        coeffB = 0

                        for t in OA.terms:
                            coeff_t = OA.terms[t]
                            coeffA += coeff_t * coeff_t

                        if np.abs(coeffA) > 1e-6:
                          self.fermi_ops.append(OA)

                        for t in OB.terms:
                            coeff_t = OB.terms[t]
                            coeffB += coeff_t * coeff_t
                            
                        if np.abs(coeffB) > 1e-6:
                          self.fermi_ops.append(OB)

                        # YXXY

                        OA = QubitOperator('X1', 0)
                        OB = QubitOperator('X1', 0)

                        OA += QubitOperator('Y%d X%d X%d Y%d'% (ra,sa,pa,qa), 2/np.sqrt(12))
                        OA += QubitOperator('Y%d X%d X%d Y%d'% (rb,sb,pb,qb), 2/np.sqrt(12))
                        OA += QubitOperator('Y%d X%d X%d Y%d'% (ra,sb,pa,qb), 1/np.sqrt(12))
                        OA += QubitOperator('Y%d X%d X%d Y%d'% (rb,sa,pb,qa), 1/np.sqrt(12))
                        OA += QubitOperator('Y%d X%d X%d Y%d'% (ra,sb,pb,qa), 1/np.sqrt(12))
                        OA += QubitOperator('Y%d X%d X%d Y%d'% (rb,sa,pa,qb), 1/np.sqrt(12))

                        OB += QubitOperator('Y%d X%d X%d Y%d'% (ra,sb,pa,qb), 1/2)
                        OB += QubitOperator('Y%d X%d X%d Y%d'% (rb,sa,pb,qa), 1/2)
                        OB -= QubitOperator('Y%d X%d X%d Y%d'% (ra,sb,pb,qa), 1/2)
                        OB -= QubitOperator('Y%d X%d X%d Y%d'% (rb,sa,pa,qb), 1/2)

                        OA -= hermitian_conjugated(OA)

                        OB -= hermitian_conjugated(OB)

                        coeffA = 0
                        coeffB = 0

                        for t in OA.terms:
                            coeff_t = OA.terms[t]
                            coeffA += coeff_t * coeff_t

                        if np.abs(coeffA) > 1e-6:
                          self.fermi_ops.append(OA)

                        for t in OB.terms:
                            coeff_t = OB.terms[t]
                            coeffB += coeff_t * coeff_t
                            
                        if np.abs(coeffB) > 1e-6:
                          self.fermi_ops.append(OB)

                        # XYYX

                        OA = QubitOperator('X1', 0)
                        OB = QubitOperator('X1', 0)

                        OA += QubitOperator('X%d Y%d Y%d X%d'% (ra,sa,pa,qa), 2/np.sqrt(12))
                        OA += QubitOperator('X%d Y%d Y%d X%d'% (rb,sb,pb,qb), 2/np.sqrt(12))
                        OA += QubitOperator('X%d Y%d Y%d X%d'% (ra,sb,pa,qb), 1/np.sqrt(12))
                        OA += QubitOperator('X%d Y%d Y%d X%d'% (rb,sa,pb,qa), 1/np.sqrt(12))
                        OA += QubitOperator('X%d Y%d Y%d X%d'% (ra,sb,pb,qa), 1/np.sqrt(12))
                        OA += QubitOperator('X%d Y%d Y%d X%d'% (rb,sa,pa,qb), 1/np.sqrt(12))

                        OB += QubitOperator('X%d Y%d Y%d X%d'% (ra,sb,pa,qb), 1/2)
                        OB += QubitOperator('X%d Y%d Y%d X%d'% (rb,sa,pb,qa), 1/2)
                        OB -= QubitOperator('X%d Y%d Y%d X%d'% (ra,sb,pb,qa), 1/2)
                        OB -= QubitOperator('X%d Y%d Y%d X%d'% (rb,sa,pa,qb), 1/2)

                        OA -= hermitian_conjugated(OA)

                        OB -= hermitian_conjugated(OB)

                        coeffA = 0
                        coeffB = 0

                        for t in OA.terms:
                            coeff_t = OA.terms[t]
                            coeffA += coeff_t * coeff_t

                        if np.abs(coeffA) > 1e-6:
                          self.fermi_ops.append(OA)

                        for t in OB.terms:
                            coeff_t = OB.terms[t]
                            coeffB += coeff_t * coeff_t
                            
                        if np.abs(coeffB) > 1e-6:
                          self.fermi_ops.append(OB)

                        # YYXX

                        OA = QubitOperator('X1', 0)
                        OB = QubitOperator('X1', 0)

                        OA += QubitOperator('Y%d Y%d X%d X%d'% (ra,sa,pa,qa), -2/np.sqrt(12))
                        OA += QubitOperator('Y%d Y%d X%d X%d'% (rb,sb,pb,qb), -2/np.sqrt(12))
                        OA += QubitOperator('Y%d Y%d X%d X%d'% (ra,sb,pa,qb), -1/np.sqrt(12))
                        OA += QubitOperator('Y%d Y%d X%d X%d'% (rb,sa,pb,qa), -1/np.sqrt(12))
                        OA += QubitOperator('Y%d Y%d X%d X%d'% (ra,sb,pb,qa), -1/np.sqrt(12))
                        OA += QubitOperator('Y%d Y%d X%d X%d'% (rb,sa,pa,qb), -1/np.sqrt(12))

                        OB += QubitOperator('Y%d Y%d X%d X%d'% (ra,sb,pa,qb), -1/2)
                        OB += QubitOperator('Y%d Y%d X%d X%d'% (rb,sa,pb,qa), -1/2)
                        OB -= QubitOperator('Y%d Y%d X%d X%d'% (ra,sb,pb,qa), -1/2)
                        OB -= QubitOperator('Y%d Y%d X%d X%d'% (rb,sa,pa,qb), -1/2)

                        OA -= hermitian_conjugated(OA)

                        OB -= hermitian_conjugated(OB)

                        coeffA = 0
                        coeffB = 0

                        for t in OA.terms:
                            coeff_t = OA.terms[t]
                            coeffA += coeff_t * coeff_t

                        if np.abs(coeffA) > 1e-6:
                          self.fermi_ops.append(OA)

                        for t in OB.terms:
                            coeff_t = OB.terms[t]
                            coeffB += coeff_t * coeff_t
                            
                        if np.abs(coeffB) > 1e-6:
                          self.fermi_ops.append(OB)

                        # YXYX

                        OA = QubitOperator('X1', 0)
                        OB = QubitOperator('X1', 0)

                        OA += QubitOperator('Y%d X%d Y%d X%d'% (ra,sa,pa,qa), 2/np.sqrt(12))
                        OA += QubitOperator('Y%d X%d Y%d X%d'% (rb,sb,pb,qb), 2/np.sqrt(12))
                        OA += QubitOperator('Y%d X%d Y%d X%d'% (ra,sb,pa,qb), 1/np.sqrt(12))
                        OA += QubitOperator('Y%d X%d Y%d X%d'% (rb,sa,pb,qa), 1/np.sqrt(12))
                        OA += QubitOperator('Y%d X%d Y%d X%d'% (ra,sb,pb,qa), 1/np.sqrt(12))
                        OA += QubitOperator('Y%d X%d Y%d X%d'% (rb,sa,pa,qb), 1/np.sqrt(12))

                        OB += QubitOperator('Y%d X%d Y%d X%d'% (ra,sb,pa,qb), 1/2)
                        OB += QubitOperator('Y%d X%d Y%d X%d'% (rb,sa,pb,qa), 1/2)
                        OB -= QubitOperator('Y%d X%d Y%d X%d'% (ra,sb,pb,qa), 1/2)
                        OB -= QubitOperator('Y%d X%d Y%d X%d'% (rb,sa,pa,qb), 1/2)

                        OA -= hermitian_conjugated(OA)

                        OB -= hermitian_conjugated(OB)

                        coeffA = 0
                        coeffB = 0

                        for t in OA.terms:
                            coeff_t = OA.terms[t]
                            coeffA += coeff_t * coeff_t

                        if np.abs(coeffA) > 1e-6:
                          self.fermi_ops.append(OA)

                        for t in OB.terms:
                            coeff_t = OB.terms[t]
                            coeffB += coeff_t * coeff_t
                            
                        if np.abs(coeffB) > 1e-6:
                          self.fermi_ops.append(OB)

        for op in self.fermi_ops:
            print(op)

        self.n_ops = len(self.fermi_ops)
        print(" Number of operators: ", self.n_ops)
        return 

class qubits_GP2(OperatorPool): # factorize group
    def generate_SQ_Operators(self):
        """
        n_orb is number of spatial orbitals assuming that spin orbitals are labelled
        0a,0b,1a,1b,2a,2b,3a,3b,....  -> 0,1,2,3,...
        """
        
        print(" Form singlet GSD operators")
        
        self.fermi_ops = []
        for p in range(0,self.n_orb):
            pa = 2*p
            pb = 2*p+1
 
            for q in range(p,self.n_orb):
                qa = 2*q
                qb = 2*q+1


                termA =  QubitOperator('X%d Y%d'% (pa,qa), 1j)
                termA -= QubitOperator('Y%d X%d'% (pa,qa), 1j)
                termA -= hermitian_conjugated(termA)
                coeffA = 0

                for t in termA.terms:
                    coeff_t = termA.terms[t]
                    coeffA += coeff_t * coeff_t

                if np.abs(coeffA) > 1e-6:
                  self.fermi_ops.append(termA)

                termA =  QubitOperator('X%d Y%d'% (pb,qb), 1j)
                termA -= QubitOperator('Y%d X%d'% (pb,qb), 1j)
                termA -= hermitian_conjugated(termA)
                coeffA = 0

                for t in termA.terms:
                    coeff_t = termA.terms[t]
                    coeffA += coeff_t * coeff_t

                if np.abs(coeffA) > 1e-6:
                  self.fermi_ops.append(termA)

        pq = -1 
        for p in range(0,self.n_orb):
            pa = 2*p
            pb = 2*p+1
 
            for q in range(p,self.n_orb):
                qa = 2*q
                qb = 2*q+1
        
                pq += 1
        
                rs = -1 
                for r in range(0,self.n_orb):
                    ra = 2*r
                    rb = 2*r+1
                    
                    for s in range(r,self.n_orb):
                        sa = 2*s
                        sb = 2*s+1
                    
                        rs += 1
                    
                        if(pq > rs):
                            continue

                        OA = QubitOperator('X1', 0)

                        OA += QubitOperator('Y%d X%d X%d X%d'% (ra,sa,pa,qa), 1j)
                        OA += QubitOperator('X%d Y%d X%d X%d'% (ra,sa,pa,qa), 1j)
                        OA += QubitOperator('X%d X%d Y%d X%d'% (ra,sa,pa,qa),-1j)
                        OA += QubitOperator('X%d X%d X%d Y%d'% (ra,sa,pa,qa),-1j)
                        OA += QubitOperator('X%d Y%d Y%d Y%d'% (ra,sa,pa,qa),-1j)
                        OA += QubitOperator('Y%d X%d Y%d Y%d'% (ra,sa,pa,qa),-1j)
                        OA += QubitOperator('Y%d Y%d X%d Y%d'% (ra,sa,pa,qa), 1j)
                        OA += QubitOperator('Y%d Y%d Y%d X%d'% (ra,sa,pa,qa), 1j)

                        OA += QubitOperator('X%d X%d X%d X%d'% (ra,sa,pa,qa), 1)
                        OA += QubitOperator('Y%d Y%d Y%d Y%d'% (ra,sa,pa,qa), 1)
                        OA += QubitOperator('X%d X%d Y%d Y%d'% (ra,sa,pa,qa),-1)
                        OA += QubitOperator('X%d Y%d X%d Y%d'% (ra,sa,pa,qa), 1)
                        OA += QubitOperator('Y%d X%d X%d Y%d'% (ra,sa,pa,qa), 1)
                        OA += QubitOperator('X%d Y%d Y%d X%d'% (ra,sa,pa,qa), 1)
                        OA += QubitOperator('Y%d Y%d X%d X%d'% (ra,sa,pa,qa),-1)
                        OA += QubitOperator('Y%d X%d Y%d X%d'% (ra,sa,pa,qa), 1)

                        OA -= hermitian_conjugated(OA)
                        coeffA = 0
        
                        for t in OA.terms:
                            coeff_t = OA.terms[t]
                            coeffA += coeff_t * coeff_t
        
                        if np.abs(coeffA) > 1e-6:
                          self.fermi_ops.append(OA)

                        # termA += FermionOperator(((rb,1),(pb,0),(sb,1),(qb,0)), 2/np.sqrt(12))

                        OA = QubitOperator('X1', 0)

                        OA += QubitOperator('Y%d X%d X%d X%d'% (rb,sb,pb,qb), 1j)
                        OA += QubitOperator('X%d Y%d X%d X%d'% (rb,sb,pb,qb), 1j)
                        OA += QubitOperator('X%d X%d Y%d X%d'% (rb,sb,pb,qb),-1j)
                        OA += QubitOperator('X%d X%d X%d Y%d'% (rb,sb,pb,qb),-1j)
                        OA += QubitOperator('X%d Y%d Y%d Y%d'% (rb,sb,pb,qb),-1j)
                        OA += QubitOperator('Y%d X%d Y%d Y%d'% (rb,sb,pb,qb),-1j)
                        OA += QubitOperator('Y%d Y%d X%d Y%d'% (rb,sb,pb,qb), 1j)
                        OA += QubitOperator('Y%d Y%d Y%d X%d'% (rb,sb,pb,qb), 1j)

                        OA += QubitOperator('X%d X%d X%d X%d'% (rb,sb,pb,qb), 1)
                        OA += QubitOperator('Y%d Y%d Y%d Y%d'% (rb,sb,pb,qb), 1)
                        OA += QubitOperator('X%d X%d Y%d Y%d'% (rb,sb,pb,qb),-1)
                        OA += QubitOperator('X%d Y%d X%d Y%d'% (rb,sb,pb,qb), 1)
                        OA += QubitOperator('Y%d X%d X%d Y%d'% (rb,sb,pb,qb), 1)
                        OA += QubitOperator('X%d Y%d Y%d X%d'% (rb,sb,pb,qb), 1)
                        OA += QubitOperator('Y%d Y%d X%d X%d'% (rb,sb,pb,qb),-1)
                        OA += QubitOperator('Y%d X%d Y%d X%d'% (rb,sb,pb,qb), 1)

                        OA -= hermitian_conjugated(OA)
                        coeffA = 0
        
                        for t in OA.terms:
                            coeff_t = OA.terms[t]
                            coeffA += coeff_t * coeff_t
        
                        if np.abs(coeffA) > 1e-6:
                          self.fermi_ops.append(OA)

                        # termA += FermionOperator(((ra,1),(pa,0),(sb,1),(qb,0)), 1/np.sqrt(12))

                        OA = QubitOperator('X1', 0)

                        OA += QubitOperator('Y%d X%d X%d X%d'% (ra,sb,pa,qb), 1j)
                        OA += QubitOperator('X%d Y%d X%d X%d'% (ra,sb,pa,qb), 1j)
                        OA += QubitOperator('X%d X%d Y%d X%d'% (ra,sb,pa,qb),-1j)
                        OA += QubitOperator('X%d X%d X%d Y%d'% (ra,sb,pa,qb),-1j)
                        OA += QubitOperator('X%d Y%d Y%d Y%d'% (ra,sb,pa,qb),-1j)
                        OA += QubitOperator('Y%d X%d Y%d Y%d'% (ra,sb,pa,qb),-1j)
                        OA += QubitOperator('Y%d Y%d X%d Y%d'% (ra,sb,pa,qb), 1j)
                        OA += QubitOperator('Y%d Y%d Y%d X%d'% (ra,sb,pa,qb), 1j)

                        OA += QubitOperator('X%d X%d X%d X%d'% (ra,sb,pa,qb), 1)
                        OA += QubitOperator('Y%d Y%d Y%d Y%d'% (ra,sb,pa,qb), 1)
                        OA += QubitOperator('X%d X%d Y%d Y%d'% (ra,sb,pa,qb),-1)
                        OA += QubitOperator('X%d Y%d X%d Y%d'% (ra,sb,pa,qb), 1)
                        OA += QubitOperator('Y%d X%d X%d Y%d'% (ra,sb,pa,qb), 1)
                        OA += QubitOperator('X%d Y%d Y%d X%d'% (ra,sb,pa,qb), 1)
                        OA += QubitOperator('Y%d Y%d X%d X%d'% (ra,sb,pa,qb),-1)
                        OA += QubitOperator('Y%d X%d Y%d X%d'% (ra,sb,pa,qb), 1)

                        OA -= hermitian_conjugated(OA)
                        coeffA = 0
        
                        for t in OA.terms:
                            coeff_t = OA.terms[t]
                            coeffA += coeff_t * coeff_t
        
                        if np.abs(coeffA) > 1e-6:
                          self.fermi_ops.append(OA)

                        # termA += FermionOperator(((rb,1),(pb,0),(sa,1),(qa,0)), 1/np.sqrt(12))

                        OA = QubitOperator('X1', 0)

                        OA += QubitOperator('Y%d X%d X%d X%d'% (rb,sa,pb,qa), 1j)
                        OA += QubitOperator('X%d Y%d X%d X%d'% (rb,sa,pb,qa), 1j)
                        OA += QubitOperator('X%d X%d Y%d X%d'% (rb,sa,pb,qa),-1j)
                        OA += QubitOperator('X%d X%d X%d Y%d'% (rb,sa,pb,qa),-1j)
                        OA += QubitOperator('X%d Y%d Y%d Y%d'% (rb,sa,pb,qa),-1j)
                        OA += QubitOperator('Y%d X%d Y%d Y%d'% (rb,sa,pb,qa),-1j)
                        OA += QubitOperator('Y%d Y%d X%d Y%d'% (rb,sa,pb,qa), 1j)
                        OA += QubitOperator('Y%d Y%d Y%d X%d'% (rb,sa,pb,qa), 1j)

                        OA += QubitOperator('X%d X%d X%d X%d'% (rb,sa,pb,qa), 1)
                        OA += QubitOperator('Y%d Y%d Y%d Y%d'% (rb,sa,pb,qa), 1)
                        OA += QubitOperator('X%d X%d Y%d Y%d'% (rb,sa,pb,qa),-1)
                        OA += QubitOperator('X%d Y%d X%d Y%d'% (rb,sa,pb,qa), 1)
                        OA += QubitOperator('Y%d X%d X%d Y%d'% (rb,sa,pb,qa), 1)
                        OA += QubitOperator('X%d Y%d Y%d X%d'% (rb,sa,pb,qa), 1)
                        OA += QubitOperator('Y%d Y%d X%d X%d'% (rb,sa,pb,qa),-1)
                        OA += QubitOperator('Y%d X%d Y%d X%d'% (rb,sa,pb,qa), 1)

                        OA -= hermitian_conjugated(OA)
                        coeffA = 0
        
                        for t in OA.terms:
                            coeff_t = OA.terms[t]
                            coeffA += coeff_t * coeff_t
        
                        if np.abs(coeffA) > 1e-6:
                          self.fermi_ops.append(OA)

                        # termA += FermionOperator(((ra,1),(pb,0),(sb,1),(qa,0)), 1/np.sqrt(12))

                        OA = QubitOperator('X1', 0)
                        
                        OA += QubitOperator('Y%d X%d X%d X%d'% (ra,sb,pb,qa), 1j)
                        OA += QubitOperator('X%d Y%d X%d X%d'% (ra,sb,pb,qa), 1j)
                        OA += QubitOperator('X%d X%d Y%d X%d'% (ra,sb,pb,qa),-1j)
                        OA += QubitOperator('X%d X%d X%d Y%d'% (ra,sb,pb,qa),-1j)
                        OA += QubitOperator('X%d Y%d Y%d Y%d'% (ra,sb,pb,qa),-1j)
                        OA += QubitOperator('Y%d X%d Y%d Y%d'% (ra,sb,pb,qa),-1j)
                        OA += QubitOperator('Y%d Y%d X%d Y%d'% (ra,sb,pb,qa), 1j)
                        OA += QubitOperator('Y%d Y%d Y%d X%d'% (ra,sb,pb,qa), 1j)

                        OA += QubitOperator('X%d X%d X%d X%d'% (ra,sb,pb,qa), 1)
                        OA += QubitOperator('Y%d Y%d Y%d Y%d'% (ra,sb,pb,qa), 1)
                        OA += QubitOperator('X%d X%d Y%d Y%d'% (ra,sb,pb,qa),-1)
                        OA += QubitOperator('X%d Y%d X%d Y%d'% (ra,sb,pb,qa), 1)
                        OA += QubitOperator('Y%d X%d X%d Y%d'% (ra,sb,pb,qa), 1)
                        OA += QubitOperator('X%d Y%d Y%d X%d'% (ra,sb,pb,qa), 1)
                        OA += QubitOperator('Y%d Y%d X%d X%d'% (ra,sb,pb,qa),-1)
                        OA += QubitOperator('Y%d X%d Y%d X%d'% (ra,sb,pb,qa), 1)

                        OA -= hermitian_conjugated(OA)
                        coeffA = 0
        
                        for t in OA.terms:
                            coeff_t = OA.terms[t]
                            coeffA += coeff_t * coeff_t
        
                        if np.abs(coeffA) > 1e-6:
                          self.fermi_ops.append(OA)

                        # termA += FermionOperator(((rb,1),(pa,0),(sa,1),(qb,0)), 1/np.sqrt(12))

                        OA = QubitOperator('X1', 0)
                                                                
                        OA += QubitOperator('Y%d X%d X%d X%d'% (rb,sa,pa,qb), 1j)
                        OA += QubitOperator('X%d Y%d X%d X%d'% (rb,sa,pa,qb), 1j)
                        OA += QubitOperator('X%d X%d Y%d X%d'% (rb,sa,pa,qb),-1j)
                        OA += QubitOperator('X%d X%d X%d Y%d'% (rb,sa,pa,qb),-1j)
                        OA += QubitOperator('X%d Y%d Y%d Y%d'% (rb,sa,pa,qb),-1j)
                        OA += QubitOperator('Y%d X%d Y%d Y%d'% (rb,sa,pa,qb),-1j)
                        OA += QubitOperator('Y%d Y%d X%d Y%d'% (rb,sa,pa,qb), 1j)
                        OA += QubitOperator('Y%d Y%d Y%d X%d'% (rb,sa,pa,qb), 1j)

                        OA += QubitOperator('X%d X%d X%d X%d'% (rb,sa,pa,qb), 1)
                        OA += QubitOperator('Y%d Y%d Y%d Y%d'% (rb,sa,pa,qb), 1)
                        OA += QubitOperator('X%d X%d Y%d Y%d'% (rb,sa,pa,qb),-1)
                        OA += QubitOperator('X%d Y%d X%d Y%d'% (rb,sa,pa,qb), 1)
                        OA += QubitOperator('Y%d X%d X%d Y%d'% (rb,sa,pa,qb), 1)
                        OA += QubitOperator('X%d Y%d Y%d X%d'% (rb,sa,pa,qb), 1)
                        OA += QubitOperator('Y%d Y%d X%d X%d'% (rb,sa,pa,qb),-1)
                        OA += QubitOperator('Y%d X%d Y%d X%d'% (rb,sa,pa,qb), 1)

                        OA -= hermitian_conjugated(OA)
                        coeffA = 0
        
                        for t in OA.terms:
                            coeff_t = OA.terms[t]
                            coeffA += coeff_t * coeff_t
        
                        if np.abs(coeffA) > 1e-6:
                          self.fermi_ops.append(OA)

        for op in self.fermi_ops:
            print(op)

        self.n_ops = len(self.fermi_ops)
        print(" Number of operators: ", self.n_ops)
        return 

class qubits_sym_check(OperatorPool): # factorize group all sign +
    def generate_SQ_Operators(self):
        """
        n_orb is number of spatial orbitals assuming that spin orbitals are labelled
        0a,0b,1a,1b,2a,2b,3a,3b,....  -> 0,1,2,3,...
        """
        
        print(" Form singlet GSD operators")
        
        self.fermi_ops = []
        for p in range(0,self.n_orb):
            pa = 2*p
            pb = 2*p+1
 
            for q in range(p,self.n_orb):
                qa = 2*q
                qb = 2*q+1


                termA =  QubitOperator('X%d Y%d'% (pa,qa), 1j)
                termA += QubitOperator('Y%d X%d'% (pa,qa), 1j)
                termA -= hermitian_conjugated(termA)
                coeffA = 0

                for t in termA.terms:
                    coeff_t = termA.terms[t]
                    coeffA += coeff_t * coeff_t

                if np.abs(coeffA) > 1e-6:
                  self.fermi_ops.append(termA)

                termA =  QubitOperator('X%d Y%d'% (pb,qb), 1j)
                termA += QubitOperator('Y%d X%d'% (pb,qb), 1j)
                termA -= hermitian_conjugated(termA)
                coeffA = 0

                for t in termA.terms:
                    coeff_t = termA.terms[t]
                    coeffA += coeff_t * coeff_t

                if np.abs(coeffA) > 1e-6:
                  self.fermi_ops.append(termA)

        pq = -1 
        for p in range(0,self.n_orb):
            pa = 2*p
            pb = 2*p+1
 
            for q in range(p,self.n_orb):
                qa = 2*q
                qb = 2*q+1
        
                pq += 1
        
                rs = -1 
                for r in range(0,self.n_orb):
                    ra = 2*r
                    rb = 2*r+1
                    
                    for s in range(r,self.n_orb):
                        sa = 2*s
                        sb = 2*s+1
                    
                        rs += 1
                    
                        if(pq > rs):
                            continue

                        OA = QubitOperator('X1', 0)

                        OA += QubitOperator('Y%d X%d X%d X%d'% (ra,sa,pa,qa), 1j)
                        OA += QubitOperator('X%d Y%d X%d X%d'% (ra,sa,pa,qa), 1j)
                        OA += QubitOperator('X%d X%d Y%d X%d'% (ra,sa,pa,qa), 1j)
                        OA += QubitOperator('X%d X%d X%d Y%d'% (ra,sa,pa,qa), 1j)
                        OA += QubitOperator('X%d Y%d Y%d Y%d'% (ra,sa,pa,qa), 1j)
                        OA += QubitOperator('Y%d X%d Y%d Y%d'% (ra,sa,pa,qa), 1j)
                        OA += QubitOperator('Y%d Y%d X%d Y%d'% (ra,sa,pa,qa), 1j)
                        OA += QubitOperator('Y%d Y%d Y%d X%d'% (ra,sa,pa,qa), 1j)

                        OA += QubitOperator('X%d X%d X%d X%d'% (ra,sa,pa,qa), 1)
                        OA += QubitOperator('Y%d Y%d Y%d Y%d'% (ra,sa,pa,qa), 1)
                        OA += QubitOperator('X%d X%d Y%d Y%d'% (ra,sa,pa,qa), 1)
                        OA += QubitOperator('X%d Y%d X%d Y%d'% (ra,sa,pa,qa), 1)
                        OA += QubitOperator('Y%d X%d X%d Y%d'% (ra,sa,pa,qa), 1)
                        OA += QubitOperator('X%d Y%d Y%d X%d'% (ra,sa,pa,qa), 1)
                        OA += QubitOperator('Y%d Y%d X%d X%d'% (ra,sa,pa,qa), 1)
                        OA += QubitOperator('Y%d X%d Y%d X%d'% (ra,sa,pa,qa), 1)

                        OA -= hermitian_conjugated(OA)
                        coeffA = 0
        
                        for t in OA.terms:
                            coeff_t = OA.terms[t]
                            coeffA += coeff_t * coeff_t
        
                        if np.abs(coeffA) > 1e-6:
                          self.fermi_ops.append(OA)

                        # termA += FermionOperator(((rb,1),(pb,0),(sb,1),(qb,0)), 2/np.sqrt(12))

                        OA = QubitOperator('X1', 0)

                        OA += QubitOperator('Y%d X%d X%d X%d'% (rb,sb,pb,qb), 1j)
                        OA += QubitOperator('X%d Y%d X%d X%d'% (rb,sb,pb,qb), 1j)
                        OA += QubitOperator('X%d X%d Y%d X%d'% (rb,sb,pb,qb), 1j)
                        OA += QubitOperator('X%d X%d X%d Y%d'% (rb,sb,pb,qb), 1j)
                        OA += QubitOperator('X%d Y%d Y%d Y%d'% (rb,sb,pb,qb), 1j)
                        OA += QubitOperator('Y%d X%d Y%d Y%d'% (rb,sb,pb,qb), 1j)
                        OA += QubitOperator('Y%d Y%d X%d Y%d'% (rb,sb,pb,qb), 1j)
                        OA += QubitOperator('Y%d Y%d Y%d X%d'% (rb,sb,pb,qb), 1j)

                        OA += QubitOperator('X%d X%d X%d X%d'% (rb,sb,pb,qb), 1)
                        OA += QubitOperator('Y%d Y%d Y%d Y%d'% (rb,sb,pb,qb), 1)
                        OA += QubitOperator('X%d X%d Y%d Y%d'% (rb,sb,pb,qb), 1)
                        OA += QubitOperator('X%d Y%d X%d Y%d'% (rb,sb,pb,qb), 1)
                        OA += QubitOperator('Y%d X%d X%d Y%d'% (rb,sb,pb,qb), 1)
                        OA += QubitOperator('X%d Y%d Y%d X%d'% (rb,sb,pb,qb), 1)
                        OA += QubitOperator('Y%d Y%d X%d X%d'% (rb,sb,pb,qb), 1)
                        OA += QubitOperator('Y%d X%d Y%d X%d'% (rb,sb,pb,qb), 1)

                        OA -= hermitian_conjugated(OA)
                        coeffA = 0
        
                        for t in OA.terms:
                            coeff_t = OA.terms[t]
                            coeffA += coeff_t * coeff_t
        
                        if np.abs(coeffA) > 1e-6:
                          self.fermi_ops.append(OA)

                        # termA += FermionOperator(((ra,1),(pa,0),(sb,1),(qb,0)), 1/np.sqrt(12))

                        OA = QubitOperator('X1', 0)

                        OA += QubitOperator('Y%d X%d X%d X%d'% (ra,sb,pa,qb), 1j)
                        OA += QubitOperator('X%d Y%d X%d X%d'% (ra,sb,pa,qb), 1j)
                        OA += QubitOperator('X%d X%d Y%d X%d'% (ra,sb,pa,qb), 1j)
                        OA += QubitOperator('X%d X%d X%d Y%d'% (ra,sb,pa,qb), 1j)
                        OA += QubitOperator('X%d Y%d Y%d Y%d'% (ra,sb,pa,qb), 1j)
                        OA += QubitOperator('Y%d X%d Y%d Y%d'% (ra,sb,pa,qb), 1j)
                        OA += QubitOperator('Y%d Y%d X%d Y%d'% (ra,sb,pa,qb), 1j)
                        OA += QubitOperator('Y%d Y%d Y%d X%d'% (ra,sb,pa,qb), 1j)

                        OA += QubitOperator('X%d X%d X%d X%d'% (ra,sb,pa,qb), 1)
                        OA += QubitOperator('Y%d Y%d Y%d Y%d'% (ra,sb,pa,qb), 1)
                        OA += QubitOperator('X%d X%d Y%d Y%d'% (ra,sb,pa,qb), 1)
                        OA += QubitOperator('X%d Y%d X%d Y%d'% (ra,sb,pa,qb), 1)
                        OA += QubitOperator('Y%d X%d X%d Y%d'% (ra,sb,pa,qb), 1)
                        OA += QubitOperator('X%d Y%d Y%d X%d'% (ra,sb,pa,qb), 1)
                        OA += QubitOperator('Y%d Y%d X%d X%d'% (ra,sb,pa,qb), 1)
                        OA += QubitOperator('Y%d X%d Y%d X%d'% (ra,sb,pa,qb), 1)

                        OA -= hermitian_conjugated(OA)
                        coeffA = 0
        
                        for t in OA.terms:
                            coeff_t = OA.terms[t]
                            coeffA += coeff_t * coeff_t
        
                        if np.abs(coeffA) > 1e-6:
                          self.fermi_ops.append(OA)

                        # termA += FermionOperator(((rb,1),(pb,0),(sa,1),(qa,0)), 1/np.sqrt(12))

                        OA = QubitOperator('X1', 0)

                        OA += QubitOperator('Y%d X%d X%d X%d'% (rb,sa,pb,qa), 1j)
                        OA += QubitOperator('X%d Y%d X%d X%d'% (rb,sa,pb,qa), 1j)
                        OA += QubitOperator('X%d X%d Y%d X%d'% (rb,sa,pb,qa), 1j)
                        OA += QubitOperator('X%d X%d X%d Y%d'% (rb,sa,pb,qa), 1j)
                        OA += QubitOperator('X%d Y%d Y%d Y%d'% (rb,sa,pb,qa), 1j)
                        OA += QubitOperator('Y%d X%d Y%d Y%d'% (rb,sa,pb,qa), 1j)
                        OA += QubitOperator('Y%d Y%d X%d Y%d'% (rb,sa,pb,qa), 1j)
                        OA += QubitOperator('Y%d Y%d Y%d X%d'% (rb,sa,pb,qa), 1j)

                        OA += QubitOperator('X%d X%d X%d X%d'% (rb,sa,pb,qa), 1)
                        OA += QubitOperator('Y%d Y%d Y%d Y%d'% (rb,sa,pb,qa), 1)
                        OA += QubitOperator('X%d X%d Y%d Y%d'% (rb,sa,pb,qa), 1)
                        OA += QubitOperator('X%d Y%d X%d Y%d'% (rb,sa,pb,qa), 1)
                        OA += QubitOperator('Y%d X%d X%d Y%d'% (rb,sa,pb,qa), 1)
                        OA += QubitOperator('X%d Y%d Y%d X%d'% (rb,sa,pb,qa), 1)
                        OA += QubitOperator('Y%d Y%d X%d X%d'% (rb,sa,pb,qa), 1)
                        OA += QubitOperator('Y%d X%d Y%d X%d'% (rb,sa,pb,qa), 1)

                        OA -= hermitian_conjugated(OA)
                        coeffA = 0
        
                        for t in OA.terms:
                            coeff_t = OA.terms[t]
                            coeffA += coeff_t * coeff_t
        
                        if np.abs(coeffA) > 1e-6:
                          self.fermi_ops.append(OA)

                        # termA += FermionOperator(((ra,1),(pb,0),(sb,1),(qa,0)), 1/np.sqrt(12))

                        OA = QubitOperator('X1', 0)
                        
                        OA += QubitOperator('Y%d X%d X%d X%d'% (ra,sb,pb,qa), 1j)
                        OA += QubitOperator('X%d Y%d X%d X%d'% (ra,sb,pb,qa), 1j)
                        OA += QubitOperator('X%d X%d Y%d X%d'% (ra,sb,pb,qa), 1j)
                        OA += QubitOperator('X%d X%d X%d Y%d'% (ra,sb,pb,qa), 1j)
                        OA += QubitOperator('X%d Y%d Y%d Y%d'% (ra,sb,pb,qa), 1j)
                        OA += QubitOperator('Y%d X%d Y%d Y%d'% (ra,sb,pb,qa), 1j)
                        OA += QubitOperator('Y%d Y%d X%d Y%d'% (ra,sb,pb,qa), 1j)
                        OA += QubitOperator('Y%d Y%d Y%d X%d'% (ra,sb,pb,qa), 1j)

                        OA += QubitOperator('X%d X%d X%d X%d'% (ra,sb,pb,qa), 1)
                        OA += QubitOperator('Y%d Y%d Y%d Y%d'% (ra,sb,pb,qa), 1)
                        OA += QubitOperator('X%d X%d Y%d Y%d'% (ra,sb,pb,qa), 1)
                        OA += QubitOperator('X%d Y%d X%d Y%d'% (ra,sb,pb,qa), 1)
                        OA += QubitOperator('Y%d X%d X%d Y%d'% (ra,sb,pb,qa), 1)
                        OA += QubitOperator('X%d Y%d Y%d X%d'% (ra,sb,pb,qa), 1)
                        OA += QubitOperator('Y%d Y%d X%d X%d'% (ra,sb,pb,qa), 1)
                        OA += QubitOperator('Y%d X%d Y%d X%d'% (ra,sb,pb,qa), 1)

                        OA -= hermitian_conjugated(OA)
                        coeffA = 0
        
                        for t in OA.terms:
                            coeff_t = OA.terms[t]
                            coeffA += coeff_t * coeff_t
        
                        if np.abs(coeffA) > 1e-6:
                          self.fermi_ops.append(OA)

                        # termA += FermionOperator(((rb,1),(pa,0),(sa,1),(qb,0)), 1/np.sqrt(12))

                        OA = QubitOperator('X1', 0)
                                                                
                        OA += QubitOperator('Y%d X%d X%d X%d'% (rb,sa,pa,qb), 1j)
                        OA += QubitOperator('X%d Y%d X%d X%d'% (rb,sa,pa,qb), 1j)
                        OA += QubitOperator('X%d X%d Y%d X%d'% (rb,sa,pa,qb), 1j)
                        OA += QubitOperator('X%d X%d X%d Y%d'% (rb,sa,pa,qb), 1j)
                        OA += QubitOperator('X%d Y%d Y%d Y%d'% (rb,sa,pa,qb), 1j)
                        OA += QubitOperator('Y%d X%d Y%d Y%d'% (rb,sa,pa,qb), 1j)
                        OA += QubitOperator('Y%d Y%d X%d Y%d'% (rb,sa,pa,qb), 1j)
                        OA += QubitOperator('Y%d Y%d Y%d X%d'% (rb,sa,pa,qb), 1j)

                        OA += QubitOperator('X%d X%d X%d X%d'% (rb,sa,pa,qb), 1)
                        OA += QubitOperator('Y%d Y%d Y%d Y%d'% (rb,sa,pa,qb), 1)
                        OA += QubitOperator('X%d X%d Y%d Y%d'% (rb,sa,pa,qb), 1)
                        OA += QubitOperator('X%d Y%d X%d Y%d'% (rb,sa,pa,qb), 1)
                        OA += QubitOperator('Y%d X%d X%d Y%d'% (rb,sa,pa,qb), 1)
                        OA += QubitOperator('X%d Y%d Y%d X%d'% (rb,sa,pa,qb), 1)
                        OA += QubitOperator('Y%d Y%d X%d X%d'% (rb,sa,pa,qb), 1)
                        OA += QubitOperator('Y%d X%d Y%d X%d'% (rb,sa,pa,qb), 1)

                        OA -= hermitian_conjugated(OA)
                        coeffA = 0
        
                        for t in OA.terms:
                            coeff_t = OA.terms[t]
                            coeffA += coeff_t * coeff_t
        
                        if np.abs(coeffA) > 1e-6:
                          self.fermi_ops.append(OA)

        for op in self.fermi_ops:
            print(op)

        self.n_ops = len(self.fermi_ops)
        print(" Number of operators: ", self.n_ops)
        return 

class singlet_GSD_nZs(OperatorPool):
    def generate_SQ_Operators(self):
        """
        n_orb is number of spatial orbitals assuming that spin orbitals are labelled
        0a,0b,1a,1b,2a,2b,3a,3b,....  -> 0,1,2,3,...
        """
        
        print(" Form singlet GSD operators")
        
        self.fermi_ops = []
        for p in range(0,self.n_orb):
            pa = 2*p
            pb = 2*p+1
 
            for q in range(p,self.n_orb):
                qa = 2*q
                qb = 2*q+1


                termA =  QubitOperator('X%d Y%d'% (pa,qa), 1j)
                termA -= QubitOperator('Y%d X%d'% (pa,qa), 1j)
                termA += QubitOperator('X%d Y%d'% (pb,qb), 1j)
                termA -= QubitOperator('Y%d X%d'% (pb,qb), 1j)

                termA -= hermitian_conjugated(termA)

                coeffA = 0

                for t in termA.terms:
                    coeff_t = termA.terms[t]
                    coeffA += coeff_t * coeff_t

                if np.abs(coeffA) > 1e-6:
                  self.fermi_ops.append(termA)

        pq = -1 
        for p in range(0,self.n_orb):
            pa = 2*p
            pb = 2*p+1
 
            for q in range(p,self.n_orb):
                qa = 2*q
                qb = 2*q+1
        
                pq += 1
        
                rs = -1 
                for r in range(0,self.n_orb):
                    ra = 2*r
                    rb = 2*r+1
                    
                    for s in range(r,self.n_orb):
                        sa = 2*s
                        sb = 2*s+1
                    
                        rs += 1
                    
                        if(pq > rs):
                            continue

                        OA = QubitOperator('X1', 0)
                        OB = QubitOperator('X1', 0)

                        # termA =  FermionOperator(((ra,1),(pa,0),(sa,1),(qa,0)), 2/np.sqrt(12))

                        OA += QubitOperator('Y%d X%d X%d X%d'% (ra,sa,pa,qa), 1j*2/np.sqrt(12))
                        OA += QubitOperator('X%d Y%d X%d X%d'% (ra,sa,pa,qa), 1j*2/np.sqrt(12))
                        OA += QubitOperator('X%d X%d Y%d X%d'% (ra,sa,pa,qa), -1j*2/np.sqrt(12))
                        OA += QubitOperator('X%d X%d X%d Y%d'% (ra,sa,pa,qa), -1j*2/np.sqrt(12))
                        OA += QubitOperator('X%d Y%d Y%d Y%d'% (ra,sa,pa,qa), -1j*2/np.sqrt(12))
                        OA += QubitOperator('Y%d X%d Y%d Y%d'% (ra,sa,pa,qa), -1j*2/np.sqrt(12))
                        OA += QubitOperator('Y%d Y%d X%d Y%d'% (ra,sa,pa,qa), 1j*2/np.sqrt(12))
                        OA += QubitOperator('Y%d Y%d Y%d X%d'% (ra,sa,pa,qa), 1j*2/np.sqrt(12))

                        OA += QubitOperator('X%d X%d X%d X%d'% (ra,sa,pa,qa), 2/np.sqrt(12))
                        OA += QubitOperator('Y%d Y%d Y%d Y%d'% (ra,sa,pa,qa), 2/np.sqrt(12))
                        OA += QubitOperator('X%d X%d Y%d Y%d'% (ra,sa,pa,qa), -2/np.sqrt(12))
                        OA += QubitOperator('X%d Y%d X%d Y%d'% (ra,sa,pa,qa), 2/np.sqrt(12))
                        OA += QubitOperator('Y%d X%d X%d Y%d'% (ra,sa,pa,qa), 2/np.sqrt(12))
                        OA += QubitOperator('X%d Y%d Y%d X%d'% (ra,sa,pa,qa), 2/np.sqrt(12))
                        OA += QubitOperator('Y%d Y%d X%d X%d'% (ra,sa,pa,qa), -2/np.sqrt(12))
                        OA += QubitOperator('Y%d X%d Y%d X%d'% (ra,sa,pa,qa), 2/np.sqrt(12))

                        # termA += FermionOperator(((rb,1),(pb,0),(sb,1),(qb,0)), 2/np.sqrt(12))

                        OA += QubitOperator('Y%d X%d X%d X%d'% (rb,sb,pb,qb), 1j*2/np.sqrt(12))
                        OA += QubitOperator('X%d Y%d X%d X%d'% (rb,sb,pb,qb), 1j*2/np.sqrt(12))
                        OA += QubitOperator('X%d X%d Y%d X%d'% (rb,sb,pb,qb), -1j*2/np.sqrt(12))
                        OA += QubitOperator('X%d X%d X%d Y%d'% (rb,sb,pb,qb), -1j*2/np.sqrt(12))
                        OA += QubitOperator('X%d Y%d Y%d Y%d'% (rb,sb,pb,qb), -1j*2/np.sqrt(12))
                        OA += QubitOperator('Y%d X%d Y%d Y%d'% (rb,sb,pb,qb), -1j*2/np.sqrt(12))
                        OA += QubitOperator('Y%d Y%d X%d Y%d'% (rb,sb,pb,qb), 1j*2/np.sqrt(12))
                        OA += QubitOperator('Y%d Y%d Y%d X%d'% (rb,sb,pb,qb), 1j*2/np.sqrt(12))

                        OA += QubitOperator('X%d X%d X%d X%d'% (rb,sb,pb,qb), 2/np.sqrt(12))
                        OA += QubitOperator('Y%d Y%d Y%d Y%d'% (rb,sb,pb,qb), 2/np.sqrt(12))
                        OA += QubitOperator('X%d X%d Y%d Y%d'% (rb,sb,pb,qb), -2/np.sqrt(12))
                        OA += QubitOperator('X%d Y%d X%d Y%d'% (rb,sb,pb,qb), 2/np.sqrt(12))
                        OA += QubitOperator('Y%d X%d X%d Y%d'% (rb,sb,pb,qb), 2/np.sqrt(12))
                        OA += QubitOperator('X%d Y%d Y%d X%d'% (rb,sb,pb,qb), 2/np.sqrt(12))
                        OA += QubitOperator('Y%d Y%d X%d X%d'% (rb,sb,pb,qb), -2/np.sqrt(12))
                        OA += QubitOperator('Y%d X%d Y%d X%d'% (rb,sb,pb,qb), 2/np.sqrt(12))

                        # termA += FermionOperator(((ra,1),(pa,0),(sb,1),(qb,0)), 1/np.sqrt(12))

                        OA += QubitOperator('Y%d X%d X%d X%d'% (ra,sb,pa,qb), 1j/np.sqrt(12))
                        OA += QubitOperator('X%d Y%d X%d X%d'% (ra,sb,pa,qb), 1j/np.sqrt(12))
                        OA += QubitOperator('X%d X%d Y%d X%d'% (ra,sb,pa,qb), -1j/np.sqrt(12))
                        OA += QubitOperator('X%d X%d X%d Y%d'% (ra,sb,pa,qb), -1j/np.sqrt(12))
                        OA += QubitOperator('X%d Y%d Y%d Y%d'% (ra,sb,pa,qb), -1j/np.sqrt(12))
                        OA += QubitOperator('Y%d X%d Y%d Y%d'% (ra,sb,pa,qb), -1j/np.sqrt(12))
                        OA += QubitOperator('Y%d Y%d X%d Y%d'% (ra,sb,pa,qb), 1j/np.sqrt(12))
                        OA += QubitOperator('Y%d Y%d Y%d X%d'% (ra,sb,pa,qb), 1j/np.sqrt(12))

                        OA += QubitOperator('X%d X%d X%d X%d'% (ra,sb,pa,qb), 1/np.sqrt(12))
                        OA += QubitOperator('Y%d Y%d Y%d Y%d'% (ra,sb,pa,qb), 1/np.sqrt(12))
                        OA += QubitOperator('X%d X%d Y%d Y%d'% (ra,sb,pa,qb), -1/np.sqrt(12))
                        OA += QubitOperator('X%d Y%d X%d Y%d'% (ra,sb,pa,qb), 1/np.sqrt(12))
                        OA += QubitOperator('Y%d X%d X%d Y%d'% (ra,sb,pa,qb), 1/np.sqrt(12))
                        OA += QubitOperator('X%d Y%d Y%d X%d'% (ra,sb,pa,qb), 1/np.sqrt(12))
                        OA += QubitOperator('Y%d Y%d X%d X%d'% (ra,sb,pa,qb), -1/np.sqrt(12))
                        OA += QubitOperator('Y%d X%d Y%d X%d'% (ra,sb,pa,qb), 1/np.sqrt(12))

                        # termA += FermionOperator(((rb,1),(pb,0),(sa,1),(qa,0)), 1/np.sqrt(12))

                        OA += QubitOperator('Y%d X%d X%d X%d'% (rb,sa,pb,qa), 1j/np.sqrt(12))
                        OA += QubitOperator('X%d Y%d X%d X%d'% (rb,sa,pb,qa), 1j/np.sqrt(12))
                        OA += QubitOperator('X%d X%d Y%d X%d'% (rb,sa,pb,qa), -1j/np.sqrt(12))
                        OA += QubitOperator('X%d X%d X%d Y%d'% (rb,sa,pb,qa), -1j/np.sqrt(12))
                        OA += QubitOperator('X%d Y%d Y%d Y%d'% (rb,sa,pb,qa), -1j/np.sqrt(12))
                        OA += QubitOperator('Y%d X%d Y%d Y%d'% (rb,sa,pb,qa), -1j/np.sqrt(12))
                        OA += QubitOperator('Y%d Y%d X%d Y%d'% (rb,sa,pb,qa), 1j/np.sqrt(12))
                        OA += QubitOperator('Y%d Y%d Y%d X%d'% (rb,sa,pb,qa), 1j/np.sqrt(12))

                        OA += QubitOperator('X%d X%d X%d X%d'% (rb,sa,pb,qa), 1/np.sqrt(12))
                        OA += QubitOperator('Y%d Y%d Y%d Y%d'% (rb,sa,pb,qa), 1/np.sqrt(12))
                        OA += QubitOperator('X%d X%d Y%d Y%d'% (rb,sa,pb,qa), -1/np.sqrt(12))
                        OA += QubitOperator('X%d Y%d X%d Y%d'% (rb,sa,pb,qa), 1/np.sqrt(12))
                        OA += QubitOperator('Y%d X%d X%d Y%d'% (rb,sa,pb,qa), 1/np.sqrt(12))
                        OA += QubitOperator('X%d Y%d Y%d X%d'% (rb,sa,pb,qa), 1/np.sqrt(12))
                        OA += QubitOperator('Y%d Y%d X%d X%d'% (rb,sa,pb,qa), -1/np.sqrt(12))
                        OA += QubitOperator('Y%d X%d Y%d X%d'% (rb,sa,pb,qa), 1/np.sqrt(12))

                        # termA += FermionOperator(((ra,1),(pb,0),(sb,1),(qa,0)), 1/np.sqrt(12))
                        
                        OA += QubitOperator('Y%d X%d X%d X%d'% (ra,sb,pb,qa), 1j/np.sqrt(12))
                        OA += QubitOperator('X%d Y%d X%d X%d'% (ra,sb,pb,qa), 1j/np.sqrt(12))
                        OA += QubitOperator('X%d X%d Y%d X%d'% (ra,sb,pb,qa), -1j/np.sqrt(12))
                        OA += QubitOperator('X%d X%d X%d Y%d'% (ra,sb,pb,qa), -1j/np.sqrt(12))
                        OA += QubitOperator('X%d Y%d Y%d Y%d'% (ra,sb,pb,qa), -1j/np.sqrt(12))
                        OA += QubitOperator('Y%d X%d Y%d Y%d'% (ra,sb,pb,qa), -1j/np.sqrt(12))
                        OA += QubitOperator('Y%d Y%d X%d Y%d'% (ra,sb,pb,qa), 1j/np.sqrt(12))
                        OA += QubitOperator('Y%d Y%d Y%d X%d'% (ra,sb,pb,qa), 1j/np.sqrt(12))

                        OA += QubitOperator('X%d X%d X%d X%d'% (ra,sb,pb,qa), 1/np.sqrt(12))
                        OA += QubitOperator('Y%d Y%d Y%d Y%d'% (ra,sb,pb,qa), 1/np.sqrt(12))
                        OA += QubitOperator('X%d X%d Y%d Y%d'% (ra,sb,pb,qa), -1/np.sqrt(12))
                        OA += QubitOperator('X%d Y%d X%d Y%d'% (ra,sb,pb,qa), 1/np.sqrt(12))
                        OA += QubitOperator('Y%d X%d X%d Y%d'% (ra,sb,pb,qa), 1/np.sqrt(12))
                        OA += QubitOperator('X%d Y%d Y%d X%d'% (ra,sb,pb,qa), 1/np.sqrt(12))
                        OA += QubitOperator('Y%d Y%d X%d X%d'% (ra,sb,pb,qa), -1/np.sqrt(12))
                        OA += QubitOperator('Y%d X%d Y%d X%d'% (ra,sb,pb,qa), 1/np.sqrt(12))

                        # termA += FermionOperator(((rb,1),(pa,0),(sa,1),(qb,0)), 1/np.sqrt(12))
                                                                
                        OA += QubitOperator('Y%d X%d X%d X%d'% (rb,sa,pa,qb), 1j/np.sqrt(12))
                        OA += QubitOperator('X%d Y%d X%d X%d'% (rb,sa,pa,qb), 1j/np.sqrt(12))
                        OA += QubitOperator('X%d X%d Y%d X%d'% (rb,sa,pa,qb), -1j/np.sqrt(12))
                        OA += QubitOperator('X%d X%d X%d Y%d'% (rb,sa,pa,qb), -1j/np.sqrt(12))
                        OA += QubitOperator('X%d Y%d Y%d Y%d'% (rb,sa,pa,qb), -1j/np.sqrt(12))
                        OA += QubitOperator('Y%d X%d Y%d Y%d'% (rb,sa,pa,qb), -1j/np.sqrt(12))
                        OA += QubitOperator('Y%d Y%d X%d Y%d'% (rb,sa,pa,qb), 1j/np.sqrt(12))
                        OA += QubitOperator('Y%d Y%d Y%d X%d'% (rb,sa,pa,qb), 1j/np.sqrt(12))

                        OA += QubitOperator('X%d X%d X%d X%d'% (rb,sa,pa,qb), 1/np.sqrt(12))
                        OA += QubitOperator('Y%d Y%d Y%d Y%d'% (rb,sa,pa,qb), 1/np.sqrt(12))
                        OA += QubitOperator('X%d X%d Y%d Y%d'% (rb,sa,pa,qb), -1/np.sqrt(12))
                        OA += QubitOperator('X%d Y%d X%d Y%d'% (rb,sa,pa,qb), 1/np.sqrt(12))
                        OA += QubitOperator('Y%d X%d X%d Y%d'% (rb,sa,pa,qb), 1/np.sqrt(12))
                        OA += QubitOperator('X%d Y%d Y%d X%d'% (rb,sa,pa,qb), 1/np.sqrt(12))
                        OA += QubitOperator('Y%d Y%d X%d X%d'% (rb,sa,pa,qb), -1/np.sqrt(12))
                        OA += QubitOperator('Y%d X%d Y%d X%d'% (rb,sa,pa,qb), 1/np.sqrt(12))

                        # termB =  FermionOperator(((ra,1),(pa,0),(sb,1),(qb,0)),  1/2.0)

                        OB += QubitOperator('Y%d X%d X%d X%d'% (ra,sb,pa,qb), 1j/2)
                        OB += QubitOperator('X%d Y%d X%d X%d'% (ra,sb,pa,qb), 1j/2)
                        OB += QubitOperator('X%d X%d Y%d X%d'% (ra,sb,pa,qb), -1j/2)
                        OB += QubitOperator('X%d X%d X%d Y%d'% (ra,sb,pa,qb), -1j/2)
                        OB += QubitOperator('X%d Y%d Y%d Y%d'% (ra,sb,pa,qb), -1j/2)
                        OB += QubitOperator('Y%d X%d Y%d Y%d'% (ra,sb,pa,qb), -1j/2)
                        OB += QubitOperator('Y%d Y%d X%d Y%d'% (ra,sb,pa,qb), 1j/2)
                        OB += QubitOperator('Y%d Y%d Y%d X%d'% (ra,sb,pa,qb), 1j/2)

                        OB += QubitOperator('X%d X%d X%d X%d'% (ra,sb,pa,qb), 1/2)
                        OB += QubitOperator('Y%d Y%d Y%d Y%d'% (ra,sb,pa,qb), 1/2)
                        OB += QubitOperator('X%d X%d Y%d Y%d'% (ra,sb,pa,qb), -1/2)
                        OB += QubitOperator('X%d Y%d X%d Y%d'% (ra,sb,pa,qb), 1/2)
                        OB += QubitOperator('Y%d X%d X%d Y%d'% (ra,sb,pa,qb), 1/2)
                        OB += QubitOperator('X%d Y%d Y%d X%d'% (ra,sb,pa,qb), 1/2)
                        OB += QubitOperator('Y%d Y%d X%d X%d'% (ra,sb,pa,qb), -1/2)
                        OB += QubitOperator('Y%d X%d Y%d X%d'% (ra,sb,pa,qb), 1/2)

                        #BtermB += FermionOperator(((rb,1),(pb,0),(sa,1),(qa,0)),  1/2.0)

                        OB += QubitOperator('Y%d X%d X%d X%d'% (rb,sa,pb,qa), 1j/2)
                        OB += QubitOperator('X%d Y%d X%d X%d'% (rb,sa,pb,qa), 1j/2)
                        OB += QubitOperator('X%d X%d Y%d X%d'% (rb,sa,pb,qa), -1j/2)
                        OB += QubitOperator('X%d X%d X%d Y%d'% (rb,sa,pb,qa), -1j/2)
                        OB += QubitOperator('X%d Y%d Y%d Y%d'% (rb,sa,pb,qa), -1j/2)
                        OB += QubitOperator('Y%d X%d Y%d Y%d'% (rb,sa,pb,qa), -1j/2)
                        OB += QubitOperator('Y%d Y%d X%d Y%d'% (rb,sa,pb,qa), 1j/2)
                        OB += QubitOperator('Y%d Y%d Y%d X%d'% (rb,sa,pb,qa), 1j/2)

                        OB += QubitOperator('X%d X%d X%d X%d'% (rb,sa,pb,qa), 1/2)
                        OB += QubitOperator('Y%d Y%d Y%d Y%d'% (rb,sa,pb,qa), 1/2)
                        OB += QubitOperator('X%d X%d Y%d Y%d'% (rb,sa,pb,qa), -1/2)
                        OB += QubitOperator('X%d Y%d X%d Y%d'% (rb,sa,pb,qa), 1/2)
                        OB += QubitOperator('Y%d X%d X%d Y%d'% (rb,sa,pb,qa), 1/2)
                        OB += QubitOperator('X%d Y%d Y%d X%d'% (rb,sa,pb,qa), 1/2)
                        OB += QubitOperator('Y%d Y%d X%d X%d'% (rb,sa,pb,qa), -1/2)
                        OB += QubitOperator('Y%d X%d Y%d X%d'% (rb,sa,pb,qb), 1/2)

                        #BtermB += FermionOperator(((ra,1),(pb,0),(sb,1),(qa,0)), -1/2.0)

                        OB -= QubitOperator('Y%d X%d X%d X%d'% (ra,sb,pb,qa), 1j/2)
                        OB -= QubitOperator('X%d Y%d X%d X%d'% (ra,sb,pb,qa), 1j/2)
                        OB -= QubitOperator('X%d X%d Y%d X%d'% (ra,sb,pb,qa), -1j/2)
                        OB -= QubitOperator('X%d X%d X%d Y%d'% (ra,sb,pb,qa), -1j/2)
                        OB -= QubitOperator('X%d Y%d Y%d Y%d'% (ra,sb,pb,qa), -1j/2)
                        OB -= QubitOperator('Y%d X%d Y%d Y%d'% (ra,sb,pb,qa), -1j/2)
                        OB -= QubitOperator('Y%d Y%d X%d Y%d'% (ra,sb,pb,qa), 1j/2)
                        OB -= QubitOperator('Y%d Y%d Y%d X%d'% (ra,sb,pb,qa), 1j/2)

                        OB -= QubitOperator('X%d X%d X%d X%d'% (ra,sb,pb,qa), 1/2)
                        OB -= QubitOperator('Y%d Y%d Y%d Y%d'% (ra,sb,pb,qa), 1/2)
                        OB -= QubitOperator('X%d X%d Y%d Y%d'% (ra,sb,pb,qa), -1/2)
                        OB -= QubitOperator('X%d Y%d X%d Y%d'% (ra,sb,pb,qa), 1/2)
                        OB -= QubitOperator('Y%d X%d X%d Y%d'% (ra,sb,pb,qa), 1/2)
                        OB -= QubitOperator('X%d Y%d Y%d X%d'% (ra,sb,pb,qa), 1/2)
                        OB -= QubitOperator('Y%d Y%d X%d X%d'% (ra,sb,pb,qa), -1/2)
                        OB -= QubitOperator('Y%d X%d Y%d X%d'% (ra,sb,pb,qa), 1/2)

                        #BtermB += FermionOperator(((rb,1),(pa,0),(sa,1),(qb,0)), -1/2.0)

                        OB -= QubitOperator('Y%d X%d X%d X%d'% (rb,sa,pa,qb), 1j/2)
                        OB -= QubitOperator('X%d Y%d X%d X%d'% (rb,sa,pa,qb), 1j/2)
                        OB -= QubitOperator('X%d X%d Y%d X%d'% (rb,sa,pa,qb), -1j/2)
                        OB -= QubitOperator('X%d X%d X%d Y%d'% (rb,sa,pa,qb), -1j/2)
                        OB -= QubitOperator('X%d Y%d Y%d Y%d'% (rb,sa,pa,qb), -1j/2)
                        OB -= QubitOperator('Y%d X%d Y%d Y%d'% (rb,sa,pa,qb), -1j/2)
                        OB -= QubitOperator('Y%d Y%d X%d Y%d'% (rb,sa,pa,qb), 1j/2)
                        OB -= QubitOperator('Y%d Y%d Y%d X%d'% (rb,sa,pa,qb), 1j/2)

                        OB -= QubitOperator('X%d X%d X%d X%d'% (rb,sa,pa,qb), 1/2)
                        OB -= QubitOperator('Y%d Y%d Y%d Y%d'% (rb,sa,pa,qb), 1/2)
                        OB -= QubitOperator('X%d X%d Y%d Y%d'% (rb,sa,pa,qb), -1/2)
                        OB -= QubitOperator('X%d Y%d X%d Y%d'% (rb,sa,pa,qb), 1/2)
                        OB -= QubitOperator('Y%d X%d X%d Y%d'% (rb,sa,pa,qb), 1/2)
                        OB -= QubitOperator('X%d Y%d Y%d X%d'% (rb,sa,pa,qb), 1/2)
                        OB -= QubitOperator('Y%d Y%d X%d X%d'% (rb,sa,pa,qb), -1/2)
                        OB -= QubitOperator('Y%d X%d Y%d X%d'% (rb,sa,pa,qb), 1/2)
 

                        # for t in OA.terms:
                        #     if(OA.terms[t] - np.conj(OA.terms[t]) < 1e-6):
                        #       OA.terms[t] = 0
                        # for t in OB.terms:
                        #     if(OB.terms[t] - np.conj(OB.terms[t]) < 1e-6):
                        #       OB.terms[t] = 0
                        OA -= hermitian_conjugated(OA)

                        OB -= hermitian_conjugated(OB)

                        coeffA = 0
                        coeffB = 0

                        for t in OA.terms:
                            coeff_t = OA.terms[t]
                            coeffA += coeff_t * coeff_t

                        if np.abs(coeffA) > 1e-6:
                          self.fermi_ops.append(OA)

                        for t in OB.terms:
                            coeff_t = OB.terms[t]
                            coeffB += coeff_t * coeff_t
                            
                        if np.abs(coeffB) > 1e-6:
                          self.fermi_ops.append(OB)

                        # termA -= hermitian_conjugated(termA)
                        # termB -= hermitian_conjugated(termB)
                      
               
                        # termA = normal_ordered(termA)
                        # termB = normal_ordered(termB)
                        
                        # #Normalize
                        # for t in termA.terms:
                        #     coeff_t = termA.terms[t]
                        #     coeffA += coeff_t * coeff_t
                        # for t in termB.terms:
                        #     coeff_t = termB.terms[t]
                        #     coeffB += coeff_t * coeff_t

                        
                        # if termA.many_body_order() > 0:
                        #     termA = termA/np.sqrt(coeffA)
                        #     self.fermi_ops.append(termA)
                        
                        # if termB.many_body_order() > 0:
                        #     termB = termB/np.sqrt(coeffB)
                            # self.fermi_ops.append(termB)
        for op in self.fermi_ops:
            print(op)

        self.n_ops = len(self.fermi_ops)
        print(" Number of operators: ", self.n_ops)
        return 

class singlet_GSD_nospin(OperatorPool):
    def generate_SQ_Operators(self):
        """
        n_orb is number of spatial orbitals assuming that spin orbitals are labelled
        0a,0b,1a,1b,2a,2b,3a,3b,....  -> 0,1,2,3,...
        """
        
        print(" Form singlet GSD operators")
        
        self.fermi_ops = []
        for p in range(0,self.n_orb):
            pa = 2*p
            pb = 2*p+1
 
            for q in range(p,self.n_orb):
                qa = 2*q
                qb = 2*q+1
        
                termA  = FermionOperator(((pa,1),(qa,0)))
                termA -= hermitian_conjugated(termA)
                self.fermi_ops.append(termA)

                termA  = FermionOperator(((pb,1),(qb,0)))
                termA -= hermitian_conjugated(termA)
                self.fermi_ops.append(termA)
               
                termA = normal_ordered(termA)
                      
      
        pq = -1 
        for p in range(0,self.n_orb):
            pa = 2*p
            pb = 2*p+1
 
            for q in range(p,self.n_orb):
                qa = 2*q
                qb = 2*q+1
        
                pq += 1
        
                rs = -1 
                for r in range(0,self.n_orb):
                    ra = 2*r
                    rb = 2*r+1
                    
                    for s in range(r,self.n_orb):
                        sa = 2*s
                        sb = 2*s+1
                    
                        rs += 1
                    
                        if(pq > rs):
                            continue

                        termA  = FermionOperator(((ra,1),(pa,0),(sa,1),(qa,0)))
                        termA -= hermitian_conjugated(termA)
                        self.fermi_ops.append(termA)

                        termA  = FermionOperator(((rb,1),(pb,0),(sb,1),(qb,0)))
                        termA -= hermitian_conjugated(termA)
                        self.fermi_ops.append(termA)

                        termA  = FermionOperator(((ra,1),(pa,0),(sb,1),(qb,0)))
                        termA -= hermitian_conjugated(termA)
                        self.fermi_ops.append(termA)

                        termA  = FermionOperator(((rb,1),(pb,0),(sa,1),(qa,0)))
                        termA -= hermitian_conjugated(termA)
                        self.fermi_ops.append(termA)

                        termA  = FermionOperator(((ra,1),(pb,0),(sb,1),(qa,0)))
                        termA -= hermitian_conjugated(termA)
                        self.fermi_ops.append(termA)

                        termA  = FermionOperator(((rb,1),(pa,0),(sa,1),(qb,0)))
                        termA -= hermitian_conjugated(termA)
                        self.fermi_ops.append(termA)

        self.n_ops = len(self.fermi_ops)
        print(" Number of operators: ", self.n_ops)
        return 

class A(OperatorPool):
    def generate_SQ_Operators(self):

        self.fermi_ops = []

        self.sup_index = []
        self.left_ops = []
        self.right_ops = []
        self.scalar = []

        sup_ind = 1
        
        n_occ = self.n_occ
        n_vir = self.n_vir

                
        for p in range(0,2*self.n_orb):
            X = QubitOperator('X%d'% p, 0+1j)
            Y = QubitOperator('Y%d'% p, 0+1j)

            self.fermi_ops.append(X)
            self.sup_index.append(0)

        for p in range(0,2*self.n_orb):
            Z = QubitOperator('Z%d'% p, 0+1j)

            self.fermi_ops.append(Z)
            self.sup_index.append(0)

        for p in range(0,2*self.n_orb):

            for q in range(p+1,2*self.n_orb):

                ZZ = QubitOperator('Z%d Z%d'% (p, q), 0+1j)
                self.fermi_ops.append(ZZ)
                self.sup_index.append(0)

        for p in range(0,2*self.n_orb):
            for q in range(p+1,2*self.n_orb):

                XX = QubitOperator('X%d X%d'% (p, q), 0+1j)
                XY = QubitOperator('X%d Y%d'% (p, q), 0+1j)
                YX = QubitOperator('Y%d X%d'% (p, q), 0+1j)
                XZ = QubitOperator('X%d Z%d'% (p, q), 0+1j)
                YZ = QubitOperator('Y%d Z%d'% (p, q), 0+1j)
                YY = QubitOperator('Y%d Y%d'% (p, q), 0+1j)

                self.fermi_ops.append(XX)
                self.fermi_ops.append(YX)
                self.fermi_ops.append(XZ)
                self.fermi_ops.append(YZ)
                self.fermi_ops.append(YY)
                self.fermi_ops.append(XY)

                self.sup_index.append(0)
                self.sup_index.append(0)
                self.sup_index.append(0)
                self.sup_index.append(0)
                self.sup_index.append(0)
                self.sup_index.append(0)

                A =  QubitOperator('X%d X%d' % (p,q),1j/2)
                A += QubitOperator('Y%d Y%d' % (p,q),1j/2)
                self.sup_index.append(sup_ind)

                left = QubitOperator('Z%d' %q , 1j*np.pi/4)
                self.left_ops.append(left)

                right = QubitOperator('Z%d Z%d' %(p,q), -1j*np.pi/4)
                right += QubitOperator('Z%d' %p, -1j*np.pi/4)
                self.right_ops.append(right)

                scalar = np.exp(1j*np.pi/4)
                self.scalar.append(scalar)

                sup_ind += 1

                self.fermi_ops.append(A)


        for i in range(0,2*self.n_orb):
            for j in range(i+1, 2*self.n_orb):

                for k in range(j+1, 2*self.n_orb):

                    YXZ = QubitOperator('Y%d X%d Z%d'% (i, j, k), 1j)  
                    # XYZ = QubitOperator('X%d Y%d Z%d'% (i, j, k), 1j)
                    XZY = QubitOperator('X%d Z%d Y%d'% (i, j, k), 1j)
                    # YZX = QubitOperator('Y%d Z%d X%d'% (i, j, k), 1j)
                    ZXY = QubitOperator('Z%d X%d Y%d'% (i, j, k), 1j)
                    # ZYX = QubitOperator('Z%d X%d Y%d'% (i, j, k), 1j)
                    # ZZZ = QubitOperator('Z%d Z%d Z%d'% (i, j, k), 1j)
  
                    # self.fermi_ops.append(XYZ)
                    self.fermi_ops.append(YXZ)
                    self.sup_index.append(0)
                    self.fermi_ops.append(XZY)
                    self.sup_index.append(0)
                    # self.fermi_ops.append(YZX)  
                    self.fermi_ops.append(ZXY)
                    self.sup_index.append(0)
                    # self.fermi_ops.append(ZYX)
                    # self.fermi_ops.append(ZZZ) 

                    # XXY = QubitOperator('X%d X%d Y%d'% (i, j, k), 1j)
                    # XYY = QubitOperator('X%d Y%d Y%d'% (i, j, k), 1j)

                    # self.fermi_ops.append(XXY)
                    # self.fermi_ops.append(XYY)

        for p in range(0,2*self.n_orb):
            for q in range(p+1,2*self.n_orb):
                for r in range(q+1,2*self.n_orb):
                    for s in range(r+1,2*self.n_orb):
                        XYYY = QubitOperator('X%d Y%d Y%d Y%d'% (p, q, r, s), 1j)
                        YXYY = QubitOperator('Y%d X%d Y%d Y%d'% (p, q, r, s), 1j)
                        YYXY = QubitOperator('Y%d Y%d X%d Y%d'% (p, q, r, s), 1j)
                        YYYX = QubitOperator('Y%d Y%d Y%d X%d'% (p, q, r, s), 1j)

                        self.fermi_ops.append(XYYY)
                        self.fermi_ops.append(YXYY)
                        self.fermi_ops.append(YYXY)
                        self.fermi_ops.append(YYYX)

                        self.sup_index.append(0)
                        self.sup_index.append(0)
                        self.sup_index.append(0)
                        self.sup_index.append(0)

                        # XXXY = QubitOperator('X%d X%d X%d Y%d'% (p, q, r, s), 1j)
                        # YXXX = QubitOperator('Y%d X%d X%d X%d'% (p, q, r, s), 1j)
                        # XYXX = QubitOperator('X%d Y%d X%d X%d'% (p, q, r, s), 1j)
                        # XXYX = QubitOperator('X%d X%d Y%d X%d'% (p, q, r, s), 1j)

                        # self.fermi_ops.append(XXXY)
                        # self.fermi_ops.append(XXYX)
                        # self.fermi_ops.append(XYXX)
                        # self.fermi_ops.append(YXXX)

                        # ZZXY = QubitOperator('Z%d Z%d X%d Y%d'% (p, q, r, s), 1j)
                        # ZZYX = QubitOperator('Z%d Z%d Y%d X%d'% (p, q, r, s), 1j)
                        # XZZY = QubitOperator('X%d Z%d Z%d Y%d'% (p, q, r, s), 1j)
                        # YZZX = QubitOperator('Y%d Z%d Z%d X%d'% (p, q, r, s), 1j)
                        # ZYXZ = QubitOperator('Z%d Y%d X%d Z%d'% (p, q, r, s), 1j)
                        # ZXYZ = QubitOperator('Z%d X%d Y%d Z%d'% (p, q, r, s), 1j)
                        # XYZZ = QubitOperator('X%d Y%d Z%d Z%d'% (p, q, r, s), 1j)
                        # YXZZ = QubitOperator('Y%d X%d Z%d Z%d'% (p, q, r, s), 1j)
                        # XZYZ = QubitOperator('X%d Z%d Y%d Z%d'% (p, q, r, s), 1j)
                        # YZXZ = QubitOperator('Y%d Z%d X%d Z%d'% (p, q, r, s), 1j)
                        # ZXZY = QubitOperator('Z%d X%d Z%d Y%d'% (p, q, r, s), 1j)
                        # ZYZX = QubitOperator('Z%d Y%d Z%d X%d'% (p, q, r, s), 1j)

                        # self.fermi_ops.append(ZZXY)
                        # self.fermi_ops.append(ZZYX)
                        # self.fermi_ops.append(XZZY)
                        # self.fermi_ops.append(YZZX)
                        # self.fermi_ops.append(ZXYZ)
                        # self.fermi_ops.append(ZYXZ)
                        # self.fermi_ops.append(XYZZ)
                        # self.fermi_ops.append(YXZZ)
                        # self.fermi_ops.append(XZYZ)
                        # self.fermi_ops.append(YZXZ)
                        # self.fermi_ops.append(ZXZY)
                        # self.fermi_ops.append(ZYZX)

                        # XXYY = QubitOperator('X%d X%d Y%d Y%d'% (p, q, r, s), 1j)
                        # XYXY = QubitOperator('X%d Y%d X%d Y%d'% (p, q, r, s), 1j)
                        # XYYX = QubitOperator('X%d Y%d Y%d X%d'% (p, q, r, s), 1j)
                        # YYXX = QubitOperator('Y%d Y%d X%d X%d'% (p, q, r, s), 1j)
                        # YXXY = QubitOperator('Y%d X%d X%d Y%d'% (p, q, r, s), 1j)
                        # YXYX = QubitOperator('Y%d X%d Y%d X%d'% (p, q, r, s), 1j)

                        # self.fermi_ops.append(XXYY)
                        # self.fermi_ops.append(XYXY)
                        # self.fermi_ops.append(XYYX)
                        # self.fermi_ops.append(YYXX)
                        # self.fermi_ops.append(YXXY)
                        # self.fermi_ops.append(YXYX)

                        # XXXX = QubitOperator('X%d X%d X%d X%d'% (p, q, r, s), 1j)
                        # YYYY = QubitOperator('Y%d Y%d Y%d Y%d'% (p, q, r, s), 1j)

                        # self.fermi_ops.append(XXXX)
                        # self.fermi_ops.append(YYYY)                        
 
                
        # for op in self.fermi_ops:
        #     print(op)

        self.n_ops = len(self.fermi_ops)
        print(" Number of operators: ", self.n_ops)        
        return
