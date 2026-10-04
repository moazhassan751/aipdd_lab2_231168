# Smart Surveillance and Attendance System

This repository contains the submission for Lab 02 of the AI Project Design and Development course at AIR University Islamabad. The project focuses on a smart AI-powered surveillance and attendance system that can detect people and objects in live video, recognize registered faces, log attendance, and trigger alerts when required.

## Project Overview

The system is designed for two practical use cases:

- Attendance monitoring using face recognition
- Security monitoring using person or weapon detection

It covers the full design process, including functional and non-functional requirements, system boundary specification, data-flow modeling, modular architecture, and a unified architecture document.

## Repository Contents

- `ARCHITECTURE.md` — system design specification, requirements, DFDs, and class architecture
- `modules/` — Python module skeletons representing the core system components

### Core Modules

- `data_ingestion.py` — captures video frames from source streams
- `image_preprocessor.py` — resizes and normalizes input frames for model consumption
- `model_inference_engine.py` — loads the AI model and handles post-processing of detections
- `alert_logger.py` — logs events and sends alert messages
- `attendance_manager.py` — matches face embeddings and tracks attendance records
- `pipeline.py` — orchestrates the end-to-end flow
- `types_common.py` — shared dataclasses for frames, detections, and results
- `test_modules.py` — sample tests verifying module behavior

## Lab Tasks Included

### Task 1: Requirements Breakdown
- 5 functional requirements
- 5 non-functional requirements

### Task 2: System Boundary and I/O Mapping
- actors and users
- input/output specification
- operational constraints

### Task 3: Data-Flow Diagram
- Level 0 and Level 1 DFD overview
- process-to-storage and alert data flow

### Task 4: Modular Architecture Blueprint
- DataIngestion
- ImagePreprocessor
- ModelInferenceEngine
- AlertLogger
- Python interface skeletons and method contracts

### Task 5: Final System Design Document
- consolidated `ARCHITECTURE.md` document prepared as the final deliverable

## Notes

This lab intentionally keeps the implementation as a design-level placeholder rather than a production-ready deployment. The modules are structured to reflect realistic system boundaries and interfaces while remaining lightweight and easy to extend for future model integration.

## Author

moazhassan
