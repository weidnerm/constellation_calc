import datetime
import time
import ephem
import argparse

def main():
    parser= argparse.ArgumentParser(description='constellation visibility calculator')
    parser.add_argument('--date', default='now', help='date of calculation mm/dd/yyyy')
    
    args = parser.parse_args()
    

if __name__ == "__main__":
    main()
    
