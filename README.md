# KiddoCab: Comprehensive App Description

## 1. Executive Summary
KiddoCab is a smart, real-time school transportation and safety mobile application designed to bridge the communication gap between schools, transport drivers, and parents. The app ensures complete transparency, absolute child safety, and seamless transit management through live GPS tracking, instant attendance logging, and role-based portals.

## 2. Core Objectives & Mission
- **Safety First:** Provide parents with absolute peace of mind by offering live tracking and verified check-ins for their children during daily commutes.
- **Operational Efficiency:** Streamline route management, student manifests, and attendance tracking for school drivers to minimize delays and errors.
- **Modern UI/UX:** Deliver a clean, accessible, and high-contrast mobile experience optimized for quick glances on the road or at home.

## 3. User Roles & Key Features

### 👤 Parent Portal
Designed for guardians to monitor their child's daily school commute in real-time.
- **Live ETA & Status Banners:** Instant notification cards showing whether the bus is en route, delayed, or minutes away from the designated stop.
- **Child Status Tracking:** Visual timeline/badges displaying whether the student is at home, boarded, in transit, or safely arrived at school.
- **Live GPS Tracking Map:** An interactive map view streaming real-time vehicle coordinates so parents can see the exact location of the van.
- **Emergency & Communication Tools:** Quick-access options to contact the driver or view trip histories.

### 🚐 Driver Portal
Designed for school van or bus drivers to manage routes and ensure passenger accountability without causing distractions.
- **Active Route Overview:** Displays the current operational route details (e.g., Morning Pickup #3).
- **Live GPS Broadcast:** A prominent toggle button to start or pause real-time location streaming back to the school and parents.
- **Student Manifest & FRS Check-In:** A scrollable checklist of students assigned to the route, featuring status chips (Picked Up, Waiting, Absent) and integration points for door sensors or face recognition check-ins.

## 4. Design System & Visual Identity
- **Primary Color (Deep Trust Blue - #1E3A8A):** Represents security, reliability, and institutional trust, used for headers, primary buttons, and navigation bars.
- **Accent Color (Warm Amber / School Bus Yellow - #F59E0B):** Captures attention for transit highlights, warnings, and key branding elements.
- **Success/Safety Color (Mint Green - #10B981):** Used for positive status updates, such as successful student pickups and active connections.
- **Background Tone (Off-White / Light Gray - #F3F4F6):** Reduces eye strain and allows content cards to stand out clearly.

## 5. Technical Architecture & Tech Stack
- **Framework:** Developed using Flutter for high-performance, cross-platform deployment across both Android and iOS devices from a single codebase.
- **Design Principles:** Adheres to Material 3 guidelines, prioritizing clean typography, rounded containers, soft shadows, and high-contrast accessibility.
- **Backend Integration:** Interfaces with Supabase for secure role-based authentication (Parent vs. Driver) and real-time database/location streaming.
