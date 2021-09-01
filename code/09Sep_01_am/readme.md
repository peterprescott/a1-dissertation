- need to redo neighbourhood enclosures with proper coastline (restrict to mainland britain) and minor roads as divisions
- load onto postgres 13- postgis 3, and you should get allegedly get better parallelization
- but either way just try parallelization...
- still need voronoi cells
- and faceblock as class
- and intersections
- and graph analysis

some voronoi progress.
but.
there is obviously something wrong 
with my `nbhd.geometry.cellularize` function
because.
i end up with empty bits.
actually no, that's not it.
the problem with `cellularize` is just that
it's not clean around the edges.
the empty bits are because some (two) of the tiles 
don't contain enough uprn (need four).

now i can easily make it *look* as if this isn't a problem
by making the tessellated tiles a background.

but that is not a *solution*.

so to fix it.
i need to deal with the ~few uprn~ exceptions.
not too hard.
and i need to figure out what is going on with the edges.

do i need to do this now?
yes. because then i can colour face-blocks in a padded out way
(with voronoi cells)
that will make more clear what is going on.
and figures which make clear what is going on
are exactly what i need.

okay.

so we've solved the edges problem.
just need to tidy it up...

hmm, meh.
AA04_SmallScale.ipynb suggests something is still not working.