This software library implements data-acquisition and real-time data analysis for the CPT phase imaging mass measurement technique. 


system requirements :

Qt5 (cross-platform gui)




Fix wxMathPlot.cpp :
https://sourceforge.net/p/wxmathplot/discussion/297266/thread/627f9652/?limit=25
"In mathplot.cpp, change all references from "::wxLogError" to "wxLogError". This is because wxLogError is a macro rather than a function."
