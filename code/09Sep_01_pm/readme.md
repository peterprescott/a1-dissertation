# what i should do

so after lunch.
- face-blocks.
- intersections.
- graph theory.
- statistics.

there area also building analysis things that could be done:
- terraced house
- semi-detached
- detached
- flat
- uprn without building footprints



# what i am doing

experimenting with plotting names on neighbourhood.

importing green space table for neighbourhood.
wondering whether i've actually loaded it correctly into the database.
wondering whether i should do that again (no!)

but I do need to tesselate britain again
with proper coastline
and i do need to think about the different types of roads

minor roads and a roads
local roads and restricted local access roads
secondary access roads


~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~

okay so there are some basic statistics that we could gather:
'rds', 'uprn', 'bdgs', 'intersections', 'rdsegments', 
'uniqueroads', 'mean_rd_segment', 'median_rd_segment', 'total_rd_length', 'area', 'convex_hull_area', 'road_types', 'road_name_endings', 'density (mean)' 'density(median')

and then we can work out the 'majorness' (need better word) of intersections
based on max(majorness of connection road)
seems inefficient but I have done the PoC for this case.

then still need to do 

------------------------------

i have found it is difficult to remove secondaryroads from the nearest neighbour analysis
because it is embedded as a postgis query
and my postgis is weak
and roadFunction has a capital
and... well. anyway.
perhaps i could just remove secondaryroads right at the beginning.

-------------------------------