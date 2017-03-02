#!/usr/bin/env python
"""
Joins two CSV files on a common label. 
"""
import sys
import pandas as pd
import argparse
import labels


#
# Main Function
#

if __name__ == "__main__":

     ## Parsing Arguments
     
     usage = "usage: %prog [options] arg1 arg2"

     parser = argparse.ArgumentParser(prog='merge')

     parser.add_argument("in_csv1",   help="CSV file 1")
     parser.add_argument("in_csv2",   help="CSV file 2")
     parser.add_argument("out",       help="Output file")

     parser.add_argument("-v","--verbose",  help="Verbose flag",      action="store_true", default=False )
     parser.add_argument("-a","--verbose_all",  help="Display all rows",      action="store_true", default=False )

     inArgs = parser.parse_args()

     pd.set_option('expand_frame_repr', False)
         
     df1  = pd.read_csv(inArgs.in_csv1)
     df2  = pd.read_csv(inArgs.in_csv2)

     df3  = df1.merge(df2, how='left',left_on='label', right_on='label')

     out_filename = inArgs.out
     df3.to_csv(out_filename, index=False)                 

