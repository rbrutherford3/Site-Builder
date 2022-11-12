import sys

from spiffindustries import main as spiffindustries_main
from baltaa import main as baltaa_main
from chess import main as chess_main
from lesley import main as lesley_main
from pdfpublisher import main as pdfpublisher_main
from pizzapricer import main as pizzapricer_main
from taskmaster import main as taskmaster_main

def main(development: bool):
    if development:
        spiffindustries_main(True)
        baltaa_main(True)
        chess_main(True)
        lesley_main(True)
        pdfpublisher_main(True)
        pizzapricer_main(True)
        taskmaster_main(True)
    else:
        spiffindustries_main(False)
        baltaa_main(False)
        chess_main(False)
        lesley_main(False)
        pdfpublisher_main(False)
        pizzapricer_main(False)
        taskmaster_main(False)
        
if __name__ == '__main__':
    if len(sys.argv) > 1:
        if (sys.argv[1] == '--development' or sys.argv[1] == '-d'):
            main(True)
        else:
            print("Invalid option: enter '-d' or '--development' for development servers")
    else:
        main(False)
