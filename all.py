import sys, os

from spiffindustries import main as spiffindustries_main, start as spiffindustries_start
from baltaa import main as baltaa_main
from chess import main as chess_main, start as chess_start
from lesley import main as lesley_main
from pdfpublisher import main as pdfpublisher_main, start as pdfpublisher_start
from pizzapricer import main as pizzapricer_main
from taskmaster import main as taskmaster_main

def main(development: bool, test: bool = False):
    if development:
        spiffindustries_main(True)
        baltaa_main(True)
        chess_main(True)
        lesley_main(True)
        pdfpublisher_main(True)
        pizzapricer_main(True)
        taskmaster_main(True)
    else:
        spiffindustries_main(False, test)
        baltaa_main(False, test)
        chess_main(False, test)
        lesley_main(False, test)
        pdfpublisher_main(False, test)
        pizzapricer_main(False, test)
        taskmaster_main(False, test)
    chess_start()
    pdfpublisher_start()
    spiffindustries_start()
        
if __name__ == '__main__':
    error_msg = "Invalid options: enter '-d' or '--development' for development servers and '-t' or '--test' for test certifications (production only)"
    if len(sys.argv) == 2:
        if (sys.argv[1] == '--development' or sys.argv[1] == '-d'):
            main(True)
        elif (sys.argv[1] == '--test' or sys.argv[1] == '-t'):
            main(False, True)
        else:
            print(error_msg)
    elif len(sys.argv) > 2:
        print(error_msg)
    else:
        main(False)
