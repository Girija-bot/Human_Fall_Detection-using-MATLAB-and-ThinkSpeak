# Human_Fall_Detection-using-MATLAB-and-ThinkSpeak
This project involves developing a fall detection system using MATLAB. The core functionality of this project is to analyze a video feed, detect falls, and send the detection data to ThingSpeak for further analysis and monitoring. Here is an overview of how the system works:

Video processing: The system reads a video file (falling.mp4) I have taken this from the Kaggle dataset video.
It processes each frame of the video

Foreground and blob detection: Foreground to isolate moving objects from the background and blob analysis to identify and analyze moving objects
Motion History Image: MHI is created and updated with each frame to track the movement speed and direction.
Fall detection: fall detects by analyzing the horizontal motion in MHI
Data transmission to thinkspeak: This shows the frame number and speed of motion I put a limit of 0 to 100, which enables remote monitoring and logging of it
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
Simulation on Python using CoAP protocol:
Introduction: CoAP, short for Constrained Application Protocol, is a messaging
protocol designed specifically for resource-limited devices in the Internet of Things
(IoT). Think of it as a leaner version of HTTP built for devices with minimal
processing power and battery life.
Lightweight: CoAP uses a small header and compact data encoding, minimizing the
data footprint and network bandwidth required for communication.
UDP-based: It operates on UDP (User Datagram Protocol) which is connectionless,
making it efficient for quick exchanges without the overhead of establishing
connections.
Simple message format: CoAP messages follow a request-response model similar
to HTTP, but with a simplified structure for faster processing.
Flexibility: CoAP offers support for multicast communication, allowing a single
message to reach multiple devices simultaneously, which is useful in sensor
networks.
Important libraries to be installed
For the CoAP Cleint and Server
aiocoap: This is the asynchronous CoAP library used for both client and server
implementations.
pip install aiocoap
For the Flask Web Application:
Flask: This is a web framework for Python
opencv-python: This is for computer vision tasks using OpenCV
numpy: This is for numerical operations in Python
pip install Flask opencv-python numpy 



