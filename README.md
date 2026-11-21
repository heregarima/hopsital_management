# MEDAXIS – Hospital Management System

> **Tagline:** *Simplifying Hospital Operations. Connecting Better Care.*  
> **Platform:** Internal Hospital Staff & Administration Portal (Non Patient-Facing)  
> **Currency:** Indian Rupees (₹) | **Date Format:** DD-MM-YYYY

---

## 🏥 Project Overview

**MEDAXIS** is an enterprise-grade hospital administration portal engineered specifically for healthcare administrators, medical superintendents, front-desk receptionists, and accounts officers in India. The platform centralizes patient intake, appointment queuing with collision prevention, departmental doctor management, dynamic pharmacy inventory tracking, and itemized billing.

---

## 🛠️ Technology Architecture

### 1. Backend Architecture (C++ REST API Server)
- **Primary Web Backend:** Native **C++11/C++14** (`backend/medaxis_server.cpp`) with Winsock2 networking (`-lws2_32`).
- **RESTful Endpoints:** Standard JSON API communicating with the frontend:
  - `GET /api/dashboard/stats` & `GET /api/dashboard/alerts`
  - `GET /api/patients` & `POST /api/patients`
  - `GET /api/patients/:id` (Patient 360° Dossier across 6 tabs)
  - `GET /api/doctors` & `GET /api/doctors/departments`
  - `GET /api/appointments`, `POST /api/appointments`, `PUT /api/appointments/:id/reschedule`, `PUT /api/appointments/:id/cancel`
  - `GET /api/pharmacy` & `POST /api/pharmacy`
  - `GET /api/billing`, `POST /api/billing`, `POST /api/billing/:id/pay`
- **Build Scripts:** `backend/Makefile` and `backend/build.bat`.

### 2. Database Architecture (MySQL 8.x)
- **Schema File:** [`database/medaxis_schema.sql`](database/medaxis_schema.sql)
- **Normalized 3NF Relational Tables (15 Tables):**
  1. `admins` – Staff administrator credentials & roles.
  2. `departments` – 11 core Indian hospital departments.
  3. `doctors` – Medical specialist roster, qualifications, room allocations, consultation fees.
  4. `doctor_availability` – Day-of-week duty slots & durations.
  5. `patients` – Full demographics, 10-digit mobile, 6-digit PIN, Indian state/UT, auto-age.
  6. `appointments` – Booking records with slot collision prevention.
  7. `lab_reports` – Diagnostics, tests, ranges, and reports.
  8. `prescriptions` – Doctor consultation records and diagnoses.
  9. `prescription_medicines` – Line items for prescribed drug dosage and frequencies.
  10. `medical_history` – Chronic conditions and past diagnoses.
  11. `medicines` – Pharmacy inventory with batch numbers, manufacturers, and stock alerts.
  12. `bills` – Itemized hospital invoices in INR (₹) with 5% GST calculations.
  13. `bill_items` – Individual service categories (Consultation, Lab, Pharmacy, Bed).
  14. `payments` – Transaction settlements via UPI, Cash, or Cards.
- **Demo Seed File:** [`database/medaxis_seed.sql`](database/medaxis_seed.sql) populated with authentic Indian names, real pharmaceutical brands (Dolo 650, Azithral, Pan-D, Telma 40, Glycomet), and realistic clinical logs.

### 3. Frontend Architecture
- **Palette:** Deep Navy Blue (`#0B192C` / `#0F172A`), White, Soft Light Blue (`#E0F2FE`), and Subtle Teal (`#0D9488`).
- **Typography & Layout:** Clean Inter typography, minimal icons, responsive flexbox/grid cards, and `@media print` stylesheets.

---

## 📋 Modules & Capabilities

### 1. Main Dashboard
- **6 Real-time Stat Cards:** Total Patients, Total Doctors, Today's Appointments, Pending Appointments, Available Pharmacy Stock (Units), and Pending Payments (in ₹).
- **Critical Alerts Row:** 
  - *Low Stock Warnings:* Medicines where quantity $\le$ minimum stock level.
  - *Expiry Warnings:* Medicines expiring within 30 days and expired stock lockouts.
- **Activity Tables:** Today's appointment schedule and recent patient registrations.

### 2. Module 1: Register New Patient
- **Indian Standard Validation:**
  - Date of Birth with client-side **auto-age calculation**.
  - Strict 10-digit Indian Mobile validation (`^[6-9]\d{9}$`).
  - Strict 6-digit Indian PIN Code validation (`^[1-9][0-9]{5}$`).
  - Dropdown containing all **28 Indian States & 8 Union Territories**.
- **Unique Patient Identifier:** Automatically generates sequential `MED-PAT-2026-XXXX`.

### 3. Module 2: Patient Details (Patient 360° Dossier)
- Searchable patient directory with gender and date filtering.
- **6-Tab Dossier Modal:**
  1. *Personal Information:* Full demographics, address, emergency contact.
  2. *Appointments:* Past, upcoming, and cancelled visits.
  3. *Lab Reports:* Diagnostics, status, test ranges, and findings.
  4. *Prescriptions:* Doctor diagnoses and prescribed drug tables.
  5. *Medical History:* Past chronic conditions and treatment summaries.
  6. *Billing History:* Invoices, payment settlements, and outstanding balances.

### 4. Module 3: Doctor Management
- **11 Departments:** General Medicine, Cardiology, Neurology, Orthopedics, Dermatology, Pediatrics, Gynecology, ENT, Ophthalmology, Dentistry, and General Surgery.
- Full credentials display: MBBS, MD, DM, experience in years, consultation fee in ₹, room/cabin, and duty schedules.

### 5. Module 4: Appointment Booking Engine
- **Workflow:** Select patient $\rightarrow$ Select department $\rightarrow$ Select doctor $\rightarrow$ Pick date & slot.
- **Collision Prevention:** Blocks duplicate bookings for the same doctor at the same slot.
- Quick **Reschedule** and **Cancel** actions with audit trails.

### 6. Module 5: Pharmacy Management
- Inventory table showing Batch Number, Manufacturer, Available Stock, Min Stock Level, Unit Price (₹), Mfg Date, Expiry Date, and Stock Status.
- Real-time stock status pills: `In Stock`, `Low Stock` ($\le$ minimum stock level), and `Expired` (locked from issuance).

### 7. Module 6: Billing & Payment Management
- Linked to Patient ID.
- Multi-category charges breakdown: Consultation Fees, Lab Charges, Pharmacy Charges, and Other Hospital Charges.
- Auto-calculation: Subtotal, 5% GST Tax, Net Total in INR (₹), Amount Paid, and Balance Due.
- Payment modes: UPI (Google Pay / PhonePe / Paytm), Cash, Debit Card, Credit Card.
- **Printable Tax Invoice / Receipt:** Formatted with hospital GSTIN, patient details, and authorized signature.

---

## 🚀 How to Run the Project

### Option A: 1-Click Launch (Recommended for Windows)
Simply double-click:
👉 **[`run.bat`](run.bat)**

Or in PowerShell:
```powershell
cd "C:\Users\thega\OneDrive\Desktop\hms"
& "C:\Users\thega\anaconda3\python.exe" server.py
```
Open **`http://localhost:5000`** in your browser.

### Option B: Compiling the Native C++ Backend
Using MinGW GCC:
```cmd
cd "C:\Users\thega\OneDrive\Desktop\hms\backend"
build.bat
```
Run:
```cmd
medaxis_server.exe 8080
```
Open **`http://localhost:8080`** in your browser.

---

## 🗄️ Setting Up MySQL

1. Start your **MySQL Server** (via XAMPP or MySQL Workbench).
2. Create and import the database:
   ```bash
   mysql -u root -p < database/medaxis_schema.sql
   mysql -u root -p < database/medaxis_seed.sql
   ```
*(Note: If MySQL is not running yet during initial testing, the application automatically uses the embedded SQLite database at `database/medaxis.sqlite` with identical schema and data, ensuring you can test immediately).*

