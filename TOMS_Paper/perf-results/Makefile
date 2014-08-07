SVGFILES := $(wildcard helmholtz/*.svg elasticity/*.svg hyperelasticity/*.svg poisson/*.svg)

all: $(SVGFILES:%.svg=%.pdf)

%.pdf: %.svg
	inkscape --export-pdf=$@ $<
