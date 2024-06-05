# Human_Fall_Detection-using-MATLAB-and-ThinkSpeak
This project involves developing a fall detection system using MATLAB. The core functionality of this project is to analyze a video feed, detect falls, and send the detection data to ThingSpeak for further analysis and monitoring. Here is an overview of how the system works:

Video processing: The system reads a video file (falling.mp4) I have taken this from the Kaggle dataset video.
It processes each frame of the video

Foreground and blob detection: Foreground to isolate moving objects from the background and blob analysis to identify and analyze moving objects
Motion History Image: MHI is created and updated with each frame to track the movement speed and direction.
Fall detection: fall detects by analyzing the horizontal motion in MHI
Data transmission to thinkspeak: This shows the frame number and speed of motion I put a limit of 0 to 100, which enables remote monitoring and logging of it
