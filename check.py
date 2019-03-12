# -*- coding: utf-8 -*-
"""
Created on Fri Mar  1 20:30:54 2019

@author: Sunanda
"""
import argparse, re, decimal
    
parser = argparse.ArgumentParser(
        description='''The purpose of this application is to check 
                        the COMP 472/6721 Winter 2019 Projects'''
        )

parser.add_argument('-c',
                    required = False, 
                    action='store_true',
                    help="optional argument to check the format")

parser.add_argument( '-m',
                    required = False, 
                    action='store_true', 
                    help="check the trace files for minimax implementation")

parser.add_argument('-a',
                    required = False, 
                    action='store_true', 
                    help="check the trace files for alpha beta implementation")

parser.add_argument("-f", dest="filename", required=True,
                    help="output file from demos", metavar="FILE",
                    type=argparse.FileType('r'))

args = parser.parse_args()

content = args.filename.read().strip()

groups = re.split('(?:\r\n\r\n|\n\n)',content)

if args.m or args.a :
    print("\n\x1b[1;31;mACESS DENIED\x1b[0m ")
else:
    print("Checking format.. ")    
    error = 0
    traceNo = 0
    for i,bunch in enumerate(groups,1): 
        if bunch.startswith('\r') or bunch.startswith('\n'):
            error = 5      
            break
        rows = bunch.split()
        if i % 2 == 1: 
            traceNo += 1
            if len(rows) > 2:
                error = 1      
                break
            elif len(rows) < 2:
                error = 2      
                break
        for val in rows:
            try:
                float(val)
            except:
                error = 3
                break
            if decimal.Decimal(val).as_tuple().exponent < -1:
                error = 4
                break
        if error != 0 :
            break
           
    # print("done")                       
    if error == 1:
        print("\x1b[1;31;mERROR:\x1b[0m Too many values in the beginning (Trace No. "+ str(traceNo) +")")     
    elif error == 2:
        print("\x1b[1;31;mERROR:\x1b[0m Not enough values in the beginning (Trace No. "+ str(traceNo) +")") 
    elif error == 3:
        print("\x1b[1;31;mERROR:\x1b[0m Number expected (Trace No. "+ str(traceNo) +")") 
    elif error == 4:
        print("\x1b[1;31;mERROR:\x1b[0m Upto one decimal point expected (Trace No. "+ str(traceNo) +")") 
    elif error == 5:
        print("\x1b[1;31;mERROR:\x1b[0m Too many new lines (Trace No. "+ str(traceNo) +")") 
    else:
        print("\x1b[1;32;mCORRECT FORMAT\x1b[0m") 




