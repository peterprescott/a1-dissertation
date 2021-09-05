
So we can successfully find connected neighbourhoods of residential
face-blocks. Our method is clearly articulated in code.
First we find the nearest road for each UPRN, and the nearest building.

Ah, I need to fix my `nearest_neighbours()` code. Try this:

```
    def nearest_neighbours(self, 
    			tablename1, tablename2, polygon, number=1):
        sql = f'''
        SELECT dbtable1.*,
               dbtable2.*,
               ST_Distance(dbtable1.geometry, dbtable2.geometry) AS dist
        FROM ({self._contains_query(tablename1, polygon)}) AS dbtable1
        CROSS JOIN LATERAL (
          SELECT dbtable2.* 
          FROM ({self._contains_query(tablename2, polygon)}) AS dbtable2
          ORDER BY dbtable2.geometry <-> dbtable1.geometry
          LIMIT {number} 
        ) AS dbtable2;
        '''
        return self.query(sql, spatial=True)
```

Then I eliminate non-building properties (this could actually be done
in the original query by setting `'WHERE ST_Distance(dbtable1.geometry,
dbtable2.geometry) == 0'.`

Then I eliminate non-residential buildings, by first counting the number
of UPRN for each building, and then dividing the building polygon's area
by that number to get a `footprint_per_uprn` value. If this is greater
than the given threshold, I exclude them.

It would be interesting to find nearest buildings and nearest names.
To see which are schools, etc.

Then we establish whether street segments are residential,
on the basis of `segment_length_per_uprn`.

(If we inverted these, there would be no need to exclude zeros...
Eg. `uprn_per_footprint_area`, `uprn_per_segment_length`.
But then it becomes less interpretable.)

And we include short streets in our analysis. 
