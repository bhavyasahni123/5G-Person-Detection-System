# Private 5G Enabled Intelligent Video Analytics System

## Overview

This project implements a real-time video analytics system built on a private 5G network. It integrates a SIM-enabled 5G camera with an edge-based machine learning pipeline to perform person detection, tracking, and counting.

The system leverages key 5G capabilities such as network slicing, edge computing (MEC), and local breakout via UPF to achieve low latency, improved security, and full data locality.

---

## System Architecture

![System Architecture](assets/system_architecture.png)

### Explanation

The 5G camera operates as user equipment and continuously streams video over the uplink. The gNodeB forwards this stream to the UPF, which performs local breakout and routes the data directly to the MEC server.

At the MEC server, video is decoded and processed through detection, tracking, and counting stages. The final analytics output is delivered to the monitoring dashboard.

---

## 5G Network Design

![5G Network Design](assets/network_design.png)

### Explanation

The system uses network slicing to separate traffic. The eMBB slice carries high-bandwidth video data, while the URLLC slice handles latency-sensitive control signals.

Both streams are managed within the private 5G network and processed at the edge, ensuring reliable and low-latency operation.

---

## Machine Learning Pipeline

![Machine Learning Pipeline](assets/ml_pipeline.png)

### Explanation

The pipeline starts with RTSP stream ingestion followed by frame decoding and buffering. The YOLO model performs person detection, and detected objects are passed to a tracking module.

The tracking system assigns unique IDs to individuals, enabling accurate counting and preventing duplication. The final output includes counts and real-time performance metrics.

---

## Key Features

* Real-time person detection using YOLO
* Multi-object tracking with persistent IDs
* Unique people counting
* RTSP video processing over 5G
* Edge-based inference using MEC
* Separation of video and control traffic

---

## Implementation Details

* OpenCV for RTSP video ingestion
* Ultralytics YOLO for detection
* Custom centroid tracking algorithm
* Frame skipping for performance optimization
* Real-time FPS monitoring

---

## Hardware Setup

* 5G SIM-enabled camera
* Private 5G core (gNodeB, UPF)
* MEC server for running ML inference

---

## Results

The system achieves stable real-time performance with consistent detection and counting accuracy. Processing at the edge ensures low latency and predictable behavior compared to cloud-based systems.

---

## Comparison

| Feature       | WiFi Systems | Cloud Systems       | Proposed System |
| ------------- | ------------ | ------------------- | --------------- |
| Latency       | Variable     | High                | Low             |
| Security      | Limited      | External dependency | SIM-based       |
| Data Location | Local        | Cloud               | Fully Local     |
| Reliability   | Low          | Medium              | High            |

---

## Applications

* Smart campus monitoring
* Industrial safety and surveillance
* Occupancy tracking
* Edge AI and 5G research

---

## Future Work

* Multi-camera integration
* Behavior analysis and anomaly detection
* Real-time alert systems
* Adaptive QoS using analytics feedback
* Hardware acceleration (GPU/FPGA)

---


