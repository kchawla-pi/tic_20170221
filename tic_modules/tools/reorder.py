#!/usr/bin/env python
"""
Measure phase ghosts by taking the ratio of the phase background to the frequency background.
"""
import sys
import pandas
import argparse
import labels

def calculate_phase_ghosts(in_csv, verbose=False):

     # Read in CSV file
     df = pandas.read_csv(in_csv)

     if verbose:
          pandas.set_option('expand_frame_repr', False)
          print('\n')
          print(df)
          print('\n')

     df_pivot = df.pivot('time', 'label')['mean']

     df_pivot['phase/freq'] = abs(df_pivot[200]/df_pivot[100])
     df_pivot['phase/background'] = abs(df_pivot[200]/df_pivot[300])
     df_pivot['freq/background'] = abs(df_pivot[100]/df_pivot[300])

     df_pivot = df_pivot.sort_values( inArgs.sort, ascending=True )

     df_pivot.reset_index(inplace=True)

     if verbose:
          print('\n')
          print(df_pivot)
          print('\n')

     return df_pivot


#
# Main Function
#

if __name__ == '__main__':

     ## Parsing Arguments
     
     usage = 'usage: %prog [options] arg1 arg2'

     parser = argparse.ArgumentParser(prog='calculate_phase_ghosts')

     parser.add_argument('in_csv',    help='Background labels ')

     parser.add_argument('-s','--sort',    help='Labels to sort', type=str, nargs=1, default = 'phase/freq' )
     parser.add_argument('-v','--verbose',  help='Verbose flag',      action='store_true', default=False )

     inArgs = parser.parse_args()

     calculate_phase_ghosts(inArgs.in_csv, inArgs.verbose)


