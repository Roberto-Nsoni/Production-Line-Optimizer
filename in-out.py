from yogi import *
from sys import *

def main ( ) :
    # Llegim dades del canal estàndar d'entrada
    a = read(int)
    b = read(int)

    # escrivim a l'arxiu indicat en el primer argument de la línia de comandes
    with open(sys.argv[1],"w") as f:    
        print(a+b,file=f)
        print(a-b,file=f)

main()