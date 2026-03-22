# Data Processing Knowledge

## Observations & Insights
- First segmentation found about 1600 blobs per frame but only matched about 300.
- Strategy: Omit/emit the largest particles during segmentation to improve results.

## Prompts for Reference
> is there a file that saves the progress of the data processing project? besides the adding of features, this is a place i run data processing for the last experiment, before i do another better one. add that i am in the middle of the second segmentation. the first segmentation found about 1600 blobs per frame and only matched about 300, i want to increase the matched particles to be closer to the blobs found in segmentation, so i will run a second segmentation for all cameras. additionally, i want to keep track of things i notice in the segmentation part, like that the right side of the tank is lighted more than the left side, robably because the light source was closer. maybe i should have decreased the power a little. the water werent clean. a good thing i did in the segmentation was to emit the largest particles. save this prompt for later reference. set up a place where you keep my notes, divide to experiment notes, and data processing notes, then go through this prompt and extract notes. maybe adding a light skill that would do this in the same manner, the note saving, that skill will improve over time.
