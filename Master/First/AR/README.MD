# Augmented Reality Paintings App (Unity + Vuforia)

## Important Note

⚠️ This repository uses **Git LFS (Large File Storage)**.  
To correctly download and use this project, you must clone it using Git:

```bash
git clone <repo-url>
```

## Overview

This project is an Augmented Reality (AR) application developed in Unity using Vuforia for image recognition.

The application recognizes paintings through the device camera and displays additional information about each artwork in real time. When a supported painting is detected, the app display contextual details such as title, author, historical background, and other relevant information.

## Built With

- Unity  
- Vuforia Engine  

## Technical Implementation Details

### Vuforia Image Target System

The application is built on **Vuforia Engine**, which provides marker-based Augmented Reality through its Image Target tracking system.

The workflow is structured as follows:

1. **Target Database Creation**
   - A project is created on the Vuforia Developer Portal.
   - A custom database is generated for Image Targets.
   - Artwork images are uploaded and analyzed by Vuforia’s feature detection algorithm.

2. **Database Integration in Unity**
   - The generated database is downloaded and imported into Unity.
   - Image Targets are instantiated in the scene and linked to specific dataset entries.

3. **Tracking Pipeline**
   - Vuforia performs feature matching between the camera feed and stored image features.
   - When a match is found, the system estimates the **pose (position + orientation)** of the image target.
   - Tracking is then maintained using Vuforia’s extended tracking system.

---

### AR Content Rendering 

Once an Image Target is detected, its associated virtual content is rendered as a child of the tracked object.

#### informational slides

Artwork information is presented using pre-designed informational slides:

- Pre-designed informational slides (created externally)
- Each slide exported as an image
- Images applied as textures on Unity **3D Plane objects**
- Planes attached as children of the Image Target

---

### Scene Structure

Each AR artwork is structured as:

- Image Target (Vuforia)
  - Plane (Information Panel)
    - Material (Slide Texture)

When tracking is lost, the entire hierarchy is hidden automatically by Vuforia’s tracking state management.

---

## Demo

A demonstration of the application is available in:

- `AR_demo.mp4`

## Project Context

This project was developed as part of the Augmented Reality course at the University of Genoa (UNIGE).

## License

This project is for educational purposes only.