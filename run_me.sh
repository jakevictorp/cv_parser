#!/bin/bash -v


for document in jkw ls
do
  python3 timeline_from_cv.py -i $document -n 25
done


# There are still some glitches with the regular expressions in timeline_from_cv.py, but it should still have reasonably high event/date detection accuracy.
# Because the rules are all hand-written, there are probably some quick fixes that could be solved by a pair of fresh eyes. 
