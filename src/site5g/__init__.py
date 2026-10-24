"""site5g - indoor 5G coverage planning from a BIM (IFC) building model.

Modules
-------
materials     wall material -> radio attenuation (dB) lookup table
ifc_loader    read walls and rooms out of an IFC file (geometry + materials)
propagation   path-loss maths and the wall-crossing counter
planner       coverage map and greedy access-point placement
sample_ifc    generate a small office-floor IFC so you can try everything
viz           coverage heat-map figure
cli           the ``site5g`` command-line tool
"""

__version__ = "0.1.0"
