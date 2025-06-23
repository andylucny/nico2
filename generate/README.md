# software for the paper 
# "Generating and Customizing Robotic Arm Trajectories using Neural Networks"

generation of trajectories (for the legibility experiment):

<pre>
python generate.py 1
python generate.py 2
python generate.py 3
python generate.py 4
python generate.py 5
python generate.py 6
python generate.py 7
</pre>

or 

<pre>
generate.bat
</pre>

the generated trajectories are: generated1.txt, ..., generated7.txt

evaluation and visualization:

<pre>
python evaluation.py
</pre>

![The generated trajectories](trajectories.png)

replay:

<pre>
cd ..\replay
python replay.py
</pre>

[![Watch the teaser video](https://www.youtube.com/watch?v=UIqqin3cJfs/hqdefault.jpg)](https://www.youtube.com/watch?v=UIqqin3cJfs)


See also [comparison to the classic IK](https://github.com/andylucny/nico2/tree/main/generate-ikpy) -
[![watch video](https://www.youtube.com/watch?v=PnguzMA5pDo/hqdefault.jpg)](https://www.youtube.com/watch?v=PnguzMA5pDo)

See also [other project based on this novel method](https://github.com/andylucny/nico2/tree/main/generate-letters) -
[![watch video](https://www.youtube.com/watch?v=PsnmP7Kvx8g/hqdefault.jpg)](https://www.youtube.com/watch?v=PsnmP7Kvx8g)
