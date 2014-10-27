"""
Python implementation of Lai's 3j program originally developed for Maple.
As nearly as I can tell, there are no checks of the triangle conditions, so
it's up to the user to verify that all arguments lead to an allowed 3j symbol.

The sum of the azimuthal quantum numbers is explicitly checked to be zero.

The output has been tested against Anthony Stone's Wigner Coefficient Calculator

http://www-stone.ch.cam.ac.uk/wigner.html

for a few cases.  More extensive testing would be needed to ensure that this
module was road worthy.

Literature: Lai, S.-T. "Computation of Algebraic Formulas for Wigner 3-j, 6-j,
and 9-j Symbols by Maple" International Journal of Quantum Chemistry,
52:593--607 (1994)

Written:  KAE Department of Physics, University at Albany 26 Oct 08
Uses:     numpy, scipy
Returns:  Wigner 3J coefficient in s and sets flag true if arguments OK.
### Note from Ruben: disabled flags
Future:   Explicitly check triangle conditions
Modified: 27 Oct 08 (implements Future)

"""

from numpy import *
from scipy import *

def W3J(J1,J,J2,M1,M,M2):

    # set flags to determine allowed 3j symbols based on calling arguments
    
    if ((abs(J1-J) <= J2) and (J2 <= J1+J)):
        tri = True
    else:
        tri = False

    if ((M1 in arange(-J1, J1+1)) and (M in arange(-J, J+1)) and \
        (M2 in arange(-J2, J2+1))):
        mem = True
    else:
        mem = False

    if (floor(J1 + J + J2) == J1 + J + J2):
        perim = True
    else:
        perim = False

    if (M1 + M + M2 == 0):
        mag = True
    else:
        mag = False

    # now compute allowed 3j symbol, return 0 if not allowed

    flag = tri and mem and perim and mag
    
    if (flag):
        delta = sqrt(factorial(J1+J2-J)*factorial(J1-J2+J)* \
                     factorial(-J1+J2+J)/factorial(J1+J+J2+1))

        a = sqrt(factorial(J2+M2)*factorial(J2-M2)/factorial(J+M)/\
                 factorial(J-M)/factorial(J1-M-M2)/factorial(J1+M+M2))
        s0 = 0

        u  = -J1+J2+J
                
        z1 = max(-J1-M-M2,u-J2-M2,0)
        z2 = min(J+J2-M-M2,J2-M2,u)
        
        for z in arange(z1,z2+1):
            if ((0 <= J+J2-M-M2-z) and (0 <= J2-M2-z) and \
                (0 <= u-z) and (0 <= J2+M2-u+z)):
                s0 = s0 + (-1)**(2*J-J1-M1+z) * \
                     factorial(J+J2-M-M2-z)*factorial(J1+M+M2+z)/\
                     factorial(z)/factorial(J2-M2-z)/factorial(u-z)/\
                     factorial(J2+M2-u+z)

        s = a*delta*s0

    else:
        s = 0

    return s #,flag



def factorial(n):

    if n==0:
        return 1
    elif n<0:
        return 0
    elif n == 1:
        return 1
    
    else:
        return n * factorial(n-1)


"""
Python implementation of Lai's 6j program originally developed for Maple.
As nearly as I can tell, there are no checks of the triangle conditions, so
it's up to the user to verify that all arguments lead to an allowed 3j symbol.

The output has been tested against Anthony Stone's Wigner Coefficient Calculator

http://www-stone.ch.cam.ac.uk/wigner.html

for a few cases.  More extensive testing would be needed to ensure that this
module was road worthy.

Literature: Lai, S.-T. "Computation of Algebraic Formulas for Wigner 3-j, 6-j,
and 9-j Symbols by Maple" International Journal of Quantum Chemistry,
52:593--607 (1994)

Arguments are called in the order

           { e a f }
           { b d c }

according to the notation in Lai's paper

Written:  KAE Department of Physics, University at Albany 26 Oct 08
Uses:     numpy, scipy
Calls:    Delta (sqrt of ratios of factorials), Triangle (tests triangle
          conditions)
Returns:  Wigner 6J coefficient in s1, flag True if all constraints satisfied
### Note from Ruben: disabled flags
Future:   Explicitly check triangle conditions
Modified: 27 Oct 08 implement future

"""



def W6J(e,a,f,b,d,c):
    if (Triangle(e,a,f) and Triangle(e,d,c) and Triangle(b,a,c) and \
        Triangle(b,d,f)):
        flag = True
    else:
        flag = False

    if flag:
        aa = factorial(a+b+c+1)*factorial(b+d+f+1)/\
             factorial(a+b-c)/factorial(c-d+e)/factorial(c+d-e)/\
             factorial(-e+a+f)/factorial(e-a+f)/factorial(b+d-f)
        v  = min(2*b,-a+b+c,b-d+f)
        s0 = 0.
        for n in arange(0,v+1):
            s0 = s0 +(-1)**n*factorial(2*b-n)/factorial(n)* \
                 factorial(b+c-e+f-n)/factorial(-a+b+c-n)* \
                 factorial(b+c+e+f+1-n)/factorial(b-d+f-n)/\
                 factorial(a+b+c+1-n)/factorial(b+d+f+1-n)

        s1 = ((-1)**(b+c+e+f))*Delta(a,b,c)*Delta(c,d,e)*Delta(a,e,f)* \
             Delta(b,d,f)*aa*s0

    else:
        s1 = 0.

    return s1#,flag


def factorial(n):

    if n==0:
        return 1
    elif n<0:
        return 0
    elif n == 1:
        return 1
    
    else:
        return n * factorial(n-1)



def Delta(a,b,c):
    d = sqrt(factorial(a+b-c)*factorial(a-b+c)/factorial(a+b+c+1)*\
             factorial(-a+b+c))
    return d


def factorial(n):

    if n==0:
        return 1
    elif n<0:
        return 0
    elif n == 1:
        return 1
    
    else:
        return n * factorial(n-1)



"""

Tests the triangle inequalities in Messiah, A. "Quantum Mechanics" v. 2,
pg. 1062 (North-Holland, Amsterdam) 1962.  Returns True if the inequalities
are satisfied, false if not.  Also tests if the triad sums to an integer

Written:  KAE University at Albany Physics Department 26 Oct 08

"""
from numpy import *

def Triangle(x,y,z):
    if floor(x+y+z) == x+y+z and z <= x+y and abs(x-y) <= z:
        test = True
    else:
        test = False

    return test
