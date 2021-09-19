# TwinCAT-to-IoT-Central

This is a project which connects TwinCAT device with Microsoft Azure IoT central application using Raspberry Pi as an edge device.

This code was used in an example of monitoring the effectiveness of the production process by calculating the overall equipment effectiveness (OEE)
indicators at the edge of the network. The TwinCAT environment runs a production line simulation based on the  PackML state model. The TwinCAT device is connected 
to a Raspberry Pi computer running a program written in Python programming language, which captures data from the production process and calculates OEE indicators in
real-time. For connection between Raspberry Pi and TwinCAT device, I used PyADS library. Calculated data are then transferred to the Azure IoT Central web application, where the operator has remote supervisory control over the effectiveness of the process.


This code is supposed to run on a Raspberry Pi.
