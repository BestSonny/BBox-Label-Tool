#!/bin/sh
# This is a comment!
find . -name "*.txt.gt" | xargs sed -i "s/class7-4axle/class7/g"
echo c7-4 cleaned
find . -name "*.txt.gt" | xargs sed -i "s/class7-5axle/class7/g"
echo c7-5 cleaned
find . -name "*.txt.gt" | xargs sed -i "s/class7-6axle/class7/g"
echo c7-6 cleaned
find . -name "*.txt.gt" | xargs sed -i "s/class7-7axle/class7/g"
echo c7-7 cleaned
find . -name "*.txt.gt" | xargs sed -i "s/class7-more/class7/g"
echo c7-more cleaned
find . -name "*.txt.gt" | xargs sed -i "s/class8-3axle/class8/g"
echo c8-3 cleaned
find . -name "*.txt.gt" | xargs sed -i "s/class8-4axle/class8/g"
echo c8-4 cleaned
find . -name "*.txt.gt" | xargs sed -i "s/class9/class9/g"
echo c9 cleaned
find . -name "*.txt.gt" | xargs sed -i "s/class10-6axle/class10/g"
echo c10-6 cleaned
find . -name "*.txt.gt" | xargs sed -i "s/class10-more/class10/g"
echo c10-more cleaned
find . -name "*.txt.gt" | xargs sed -i "s/class11-5axle/class11/g"
echo c11-5 cleaned
find . -name "*.txt.gt" | xargs sed -i "s/class11-few/class11/g"
echo c11-few cleaned
find . -name "*.txt.gt" | xargs sed -i "s/class13-7axle/class13/g"
echo c13-7 cleaned
find . -name "*.txt.gt" | xargs sed -i "s/class13-more/class13/g"
echo c13-more cleaned
echo FINISHED CLEANING
