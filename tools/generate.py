# -*- coding: utf-8 -*-
import json
from optparse import OptionParser
from jinja2 import Environment, FileSystemLoader
import os

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-s", "--srcFile", dest="srcFile",
                      help="", metavar="FILE")
    parser.add_option("-d", "--destDir", dest="destDir",
                      help="", metavar="DIR")
    parser.add_option("-c", "--cfgDir", dest="cfgFile",
                      help="", metavar="CFG")
    
    (options, args) = parser.parse_args()

    
    env = Environment(loader=FileSystemLoader(os.path.dirname(options.srcFile)))
    template = env.get_template(os.path.basename(options.srcFile))

    with open(options.cfgFile) as data_file:    
        cfg = json.load(data_file)

    output = template.render(cfg=cfg)
    
    out_file_name = os.path.join(options.destDir, os.path.basename(options.srcFile))
    if out_file_name[-3:] == '.in':
        out_file_name = out_file_name[:-3]

    with open(out_file_name, "wb") as fh:
        fh.write(output)
    
    print "Wrote " + out_file_name


