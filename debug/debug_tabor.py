import sys 
sys.path.append( './code/' )

import tabor
tabor_mgr = tabor.Tabor()
tabor_mgr.load_params( 68, 5,
                      [ 1600.0, 656252.0, 657844.5 ],
                     [ -140.0, 0.0, 0.0 ],
                     [ 0.0005, 0.2, 0.5 ],
                     [ 1, 100, 208 ],
                     [ 3, 1, 1 ])

# import tdc
# tdc_mgr = tdc.TDC()