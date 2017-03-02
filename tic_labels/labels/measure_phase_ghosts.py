#!/usr/bin/env python
"""
Sorts a Label CSV file. This function is primarily used for viewing contents of CSV file.
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

     parser = argparse.ArgumentParser(prog='sort')

     parser.add_argument("in_csv",    help="Label NIFTI filename ")
     parser.add_argument("--out",     help="Filename of CSV output file containing label stats", default=None)
     parser.add_argument("--sort",    help="Labels to sort", type=str, nargs=1, default = 'label' )

     parser.add_argument("--sort_direction",    help="Sorting direction: 0=descending, 1=ascending (default=1)", type=int, nargs=1, default = [1] )
     parser.add_argument("--limits",            help="Limits of sorted values", type=float, nargs=2, default = None )
     parser.add_argument("--stats",             help="Stats to report", type=str, nargs="*", default=None)
     parser.add_argument("--labels",            help="Labels to report", type=float, nargs="*", default=None)


     parser.add_argument("-v","--verbose",  help="Verbose flag",      action="store_true", default=False )
     parser.add_argument("-a","--verbose_all",  help="Display all rows",      action="store_true", default=False )

     parser.add_argument("--nan",  help="Keep NAN values",      action="store_true", default=False )


     inArgs = parser.parse_args()

     pd.set_option('expand_frame_repr', False)
         
     df_stats  = pd.read_csv(inArgs.in_csv)

     if inArgs.labels is not None:
         df_stats = df_stats[df_stats['label'].isin(inArgs.labels)]
         
     if inArgs.stats is not None:
         stats_list = inArgs.stats
     else:
         stats_list = list(df_stats.columns.values)

     if inArgs.limits is not None:
         df_limits = df_stats[  (df_stats[inArgs.sort[0] ] >= inArgs.limits[0]) & (df_stats[inArgs.sort[0] ] <= inArgs.limits[1]) ]
     else:
         df_limits = df_stats

     df_sorted = df_limits.sort_values( inArgs.sort, ascending=inArgs.sort_direction ).reset_index()

     if not inArgs.nan:
         df_sorted = df_sorted.dropna()

     if inArgs.verbose:

         if inArgs.verbose_all:
             pd.set_option('display.max_rows',len(df_stats))

         print
         print (df_sorted[ stats_list  ])
         print


     if not inArgs.out == None:
         df_sorted[ stats_list ].to_csv(inArgs.out, index=False ) 

