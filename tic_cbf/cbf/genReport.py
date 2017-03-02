#!/usr/bin/env python

import os
from jinja2 import Environment, FileSystemLoader
from collections import OrderedDict

PATH = os.path.dirname(os.path.abspath(__file__))

TEMPLATE_ENVIRONMENT = Environment(
                                   autoescape=False,
                                   loader=FileSystemLoader(os.path.join(PATH, 'templates')),
                                   trim_blocks=False)


def renderTemplate(template_filename, context):
    return TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)


def generateResults():
    pass

def read_json():

    #define configuration. this section can be seperated to another file and imported as a module
    pageTitle= "pcasl_raw report"
    sourcePath='pcasl_raw_dir/'

    with open(sourcePath+'cbf_stats.txt', 'r') as myfile:
        stats=myfile.read().replace('\n', '').split()

    [globalCBF,outputVersion,totalVol,discardedVol,stdFiltering,meanFiltering]=stats[1:]
    imageMotionCorrection=[sourcePath+name+".png" for name in ['rot','trans','disp','mean_perf']]

    hcsCBF='cbf_brain_hcs'
    hCBF='cbf_brain_h'
    hNonBrain='scalp_h'
    hcsDiscarded='discarded_cbf_hcs'

    dict_cbf = OrderedDict((('pageTitle', pageTitle),
                            ('outputVersion', outputVersion),
                            ('globalCBF', float(globalCBF)),  # or can be converted to int by using int(globalCBF)
                            ('totalVol', float(totalVol)),
                            ('discardedVol', float(discardedVol)),
                            ('stdFiltering', float(stdFiltering)),
                            ('meanFiltering', float(meanFiltering)),
                            ('imageMotionCorrection', imageMotionCorrection),
                            ('hcsCBF', sourcePath + hcsCBF + '.png'),
                            ('hCBF', sourcePath + hCBF + '.png'),
                            ('hNonBrain', sourcePath + hNonBrain + '.png'),
                            ('hcsDiscarded', sourcePath + hcsDiscarded + '.png')
                            ))

    return dict_cbf

def createReportHtml():
    
    fname = 'cbfReport.html'
    context = read_json()

    # {
    #     'pageTitle'     : pageTitle,
    #     'outputVersion' : outputVersion,
    #     'globalCBF'     : float(globalCBF),#or can be converted to int by using int(globalCBF)
    #     'totalVol'      : float(totalVol),
    #     'discardedVol'  : float(discardedVol),
    #     'stdFiltering'  : float(stdFiltering),
    #     'meanFiltering' : float(meanFiltering),
    #     'imageMotionCorrection' :imageMotionCorrection,
    #     'hcsCBF'                :sourcePath+hcsCBF+".png",
    #     'hCBF'                  :sourcePath+hCBF+".png",
    #     'hNonBrain'             :sourcePath+hNonBrain+".png",
    #     'hcsDiscarded'          :sourcePath+hcsDiscarded+".png",
    # }

    #now write the output html with the defined configuration
    with open(fname, 'w') as f:
        html = renderTemplate('cbf_template2.html', context)
        f.write(html)

def main():
    createReportHtml()

#############################################################################

if __name__ == "__main__":
    main()
