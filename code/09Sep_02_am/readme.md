Nodes don't actually matter.
What matters is whether face-blocks are residential.
And whether we have a connected network of residential face-blocks.
On a tertiary road both sides of the street form a single face-block.
On a more major road, each side of the street is a distinct face-block.

So we can tessellate by more major roads,
and within the resulting tiles,
nothing will be divided by major roads...?

(Actually not true.
Because a major road might merely penetrate a tile
without dividing it.
In that case 
for the purpose of defining face-blocks,
we need to treat it as two roads shifted slightly
perpendicular to the direction of the road.)

Anyway, then we can find the connected graph
of residential face-blocks.
(We still need to think about 
the 'penetrating major road issue' here.)

These connected graphs of residential face-blocks
are what Grannis calls 'communities'.
Then we need to find how these connect into islands.
Grannis focusses on intersections,
but actually pedestrians cross busy roads at *crossings*.
Crossing location data is included in OS MasterMap
but not in OS OpenMapLocal.
Nevertheless, we can surely assume that a major-road segment
with face-blocks on both sides has a crossing somewhere,
regardless of whether it is a tunnel or a pedestrian crossing,
and regardless of exactly where it is.

We can then connect communities across major roads
with face-blocks on opposite sides,
and find the islands of connected communities.

We should be able to do this 
for the whole of Britian by the end of today.
Or tomorrow. Or the next day.
No later.

So. First let's get coastlines for mainland Britain.
Then rivers, railways, motorways, A Roads, B Roads, minor roads.
And tesselate.
#1.

Then figure out the penetrating major road question.
#2

Then do nearest neighbours to find which face-blocks are residential.
Ignore 'Secondary Access Roads'.
Ignore properties a certain distance from their nearest road.
#3.

Then find connected graph of residential face-blocks within n-tile.
What @RGrannis2012 calls a 't-community'.
His 't' is for 'tertiary'; mine will be for 'tile'.
#4.

Then find connected graph of t-communities across more major roads.
What @RGrannis2012 calls 'islands'.
Do I have a better term? 
'Super-communities'? 'Conjunctions'? 'Majorities'?
#5.

Then...?
Get summary statistics for all of these
(tiles, communities, )
and k-means cluster them!
Or not.