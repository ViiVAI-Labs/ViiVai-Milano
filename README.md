# ViiVai Milano: Grid Displays for media and communication
API and examples for Haptic Grid Displays

<img src="images/haptic-media.png" width="500" height="336">

## What are Haptic Grid Displays
Haptic Grid Displays are common in research and development settings, enabling the control of haptic content on the skin using multichannel haptic actuators arranged in spatial arrays. One advantage of grid displays is their ability to increase information transfer compared to a single actuator. Higher information throughput supports users to perform virtual tasks with greater efficiency. Another benefit of grid displays is the ability to provide structured spatial haptic feedback, correlating physical and media events to coherent haptic events, thus improving both immersion and causality with the virtual and/or augmented content.

<img src="images/hapticgrids.png" width="500" height="305">

Haptic Grid displays vary in sizes and forms, and have been used on fingertips, tongue, forearm, wrist, waist, torso, back, and almost all skin surfaces. The goal of these displays is to increase communication throughput by providing mentally correlated tactile messages for language communication, for navigation, to render spatially distributed interpersonal affective touch, or to render spatial surrounding content for games, movies, and immersive media.

## Nomenclature

Each channel of the multichannel haptic grid display is defined in [IEEE_HapticHardware.py](IEEE/IEEE_HapticHardware.py). 

1. def setHapticOutput(act, g, act_index): -> act\
Map haptic output to the physical grid

__act__: An np.array of dimension equal to the number of haptic channels in the grid\
__g__: gain for each channel\
__act_index__: indexing of each channel

2. def setupHapticDictionary(device_type, border = SimpleNamespace(x, y, w, h))

2. 

🎥 **Demo Video**  
[Click to watch the demo](images/HapticGenAI_demo.mp4)
<!-- [![Click to watch the demo](images/GenAI_frame.png)](images/HapticGenAI_demo.mp4) -->

[![Watch the video](images/GenAI_frame.png)](https://www.youtube.com/watch?v=CgmsDfiV6Aw)