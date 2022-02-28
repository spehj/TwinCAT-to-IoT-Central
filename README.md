# TwinCAT PLC connected to the Azure IoT Central Application

This is an edge computing application.

The TwinCAT device is connected to Microsoft Azure IoT central application using Raspberry Pi as an edge device.

We can see the data computed on the edge and see results in real time on the Azure IoT Central Dashboard.

We can also control the process and change variable values on the PLC from the Web Application from anywhere in the world.

<br/>
<br/>

This application is just an example of an Edge application. We are monitoring the effectiveness of the production process by calculating the overall equipment effectiveness (OEE) indicators at the edge of the network

<br/>
<br/>

## TwinCAT device with simulated production line
![proizvodna-inija-simulacija-v2](https://user-images.githubusercontent.com/62114221/156035010-d7dbbbdc-5d50-4a15-bb87-2b6169efe18b.png | width = 200)

The TwinCAT environment runs a production line simulation based on the  PackML state model. For connection between Raspberry Pi and TwinCAT device, PyADS library has been used.

## Azure IoT Central Application
<img src="https://user-images.githubusercontent.com/62114221/156036157-f68033eb-818f-44aa-865a-03d750f6ec70.png" width="200">

Calculated data are then transferred to the Azure IoT Central web application, where the operator has remote supervisory control over the effectiveness of the process.



