#!/usr/bin/env python

"""

"""
import pandas
import argparse
import os

#
# Main Function
#

if __name__ == "__main__":

     ## Parsing Arguments
     #
     #

     usage = "usage: %prog [options] arg1 arg2"

     parser = argparse.ArgumentParser(prog='display_stats')

     parser.add_argument("in_csv",  help='CSV filename')
     parser.add_argument('-o',"--out",  help='CSV filename', type=str, default=None)
     parser.add_argument('-c',"--columns",  help='CSV filename', nargs='*', default=None)
     parser.add_argument("--head",    help='Number of lines to display.', type=int, default=None)
     parser.add_argument('-l',"--list",    help='List column names.', action="store_true", default=False )
     parser.add_argument("--sort",    help="Labels to sort", type=str, nargs=1, default = None )
     parser.add_argument("--sort_direction",    help="Sorting direction: 0=descending, 1=ascending (default=1)", type=int, nargs=1, default = [1] )

#     parser.add_argument('-v',"--verbose",  help="Verbose flag",      action="store_true", default=False )

     inArgs = parser.parse_args()

     if os.path.isfile(inArgs.in_csv):
          df = pandas.read_csv(inArgs.in_csv)     

     #
     #
     #

     pandas.set_option('expand_frame_repr', False)
     pandas.set_option('display.max_rows',len(df))

     if inArgs.columns==None:
          columns = list(df.columns.values)
     else:
          columns=inArgs.columns

     if inArgs.list:
          print(list(df.columns.values))
     else:

          if inArgs.sort in df.columns.values:
               df_sorted = df.sort_values( inArgs.sort, ascending=inArgs.sort_direction ).reset_index()
          else:
               print('\n Warning: sort column is not in data frame \n')
               df_sorted = df

          print(df_sorted[columns])


     if inArgs.out:
          df_sorted[columns].to_csv(inArgs.out, header=columns, index=None)
