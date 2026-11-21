-- ========================================================
-- MEDAXIS – Hospital Management System
-- Database Schema (MySQL 8.x / MariaDB)
-- Normalized 3NF Architecture with Foreign Key Constraints
-- ========================================================

CREATE DATABASE IF NOT EXISTS medaxis_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE medaxis_db;

-- 1. ADMINS TABLE
CREATE TABLE IF NOT EXISTS admins (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    mobile VARCHAR(20) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'Administrator',
    status ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
    last_login TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 2. DEPARTMENTS TABLE (11 Core Hospital Departments)
CREATE TABLE IF NOT EXISTS departments (
    dept_id INT AUTO_INCREMENT PRIMARY KEY,
    dept_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    hod_name VARCHAR(100),
    contact_ext VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 3. DOCTORS TABLE
CREATE TABLE IF NOT EXISTS doctors (
    doctor_id INT AUTO_INCREMENT PRIMARY KEY,
    doctor_code VARCHAR(20) NOT NULL UNIQUE,
    dept_id INT NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    specialization VARCHAR(100) NOT NULL,
    qualification VARCHAR(100) NOT NULL,
    experience_years INT NOT NULL DEFAULT 0,
    email VARCHAR(100) NOT NULL UNIQUE,
    mobile_number VARCHAR(15) NOT NULL,
    consultation_fees DECIMAL(10, 2) NOT NULL DEFAULT 500.00,
    room_no VARCHAR(20),
    status ENUM('active', 'on_leave', 'inactive') NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id) ON DELETE RESTRICT,
    INDEX idx_doc_dept (dept_id),
    INDEX idx_doc_status (status)
) ENGINE=InnoDB;

-- 4. DOCTOR AVAILABILITY SCHEDULE TABLE
CREATE TABLE IF NOT EXISTS doctor_availability (
    avail_id INT AUTO_INCREMENT PRIMARY KEY,
    doctor_id INT NOT NULL,
    day_of_week ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday') NOT NULL,
    start_time TIME NOT NULL DEFAULT '09:00:00',
    end_time TIME NOT NULL DEFAULT '17:00:00',
    slot_duration_minutes INT NOT NULL DEFAULT 20,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON DELETE CASCADE,
    UNIQUE KEY uk_doc_day (doctor_id, day_of_week)
) ENGINE=InnoDB;

-- 5. PATIENTS TABLE (Indian Context Validation)
CREATE TABLE IF NOT EXISTS patients (
    patient_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_code VARCHAR(30) NOT NULL UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    dob DATE NOT NULL,
    age INT NOT NULL,
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    blood_group ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-') NOT NULL,
    mobile_number VARCHAR(15) NOT NULL UNIQUE,
    email VARCHAR(100),
    address TEXT NOT NULL,
    city VARCHAR(50) NOT NULL,
    state VARCHAR(50) NOT NULL,
    pincode VARCHAR(10) NOT NULL,
    status ENUM('active', 'discharged') NOT NULL DEFAULT 'active',
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_pat_code (patient_code),
    INDEX idx_pat_mobile (mobile_number)
) ENGINE=InnoDB;

-- 6. APPOINTMENTS TABLE (Collision Prevention & Slot Allocation)
CREATE TABLE IF NOT EXISTS appointments (
    appointment_id INT AUTO_INCREMENT PRIMARY KEY,
    appointment_code VARCHAR(30) NOT NULL UNIQUE,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    dept_id INT NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    consultation_fees DECIMAL(10, 2) NOT NULL,
    status ENUM('Booked', 'Rescheduled', 'Cancelled', 'Completed') NOT NULL DEFAULT 'Booked',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON DELETE CASCADE,
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id) ON DELETE RESTRICT,
    INDEX idx_apt_date_time (doctor_id, appointment_date, appointment_time),
    INDEX idx_apt_status (status)
) ENGINE=InnoDB;

-- 7. LAB REPORTS TABLE
CREATE TABLE IF NOT EXISTS lab_reports (
    report_id INT AUTO_INCREMENT PRIMARY KEY,
    report_code VARCHAR(30) NOT NULL UNIQUE,
    patient_id INT NOT NULL,
    doctor_id INT,
    test_name VARCHAR(150) NOT NULL,
    test_date DATE NOT NULL,
    report_status ENUM('Pending', 'In Progress', 'Completed', 'Delivered') NOT NULL DEFAULT 'Pending',
    result_summary TEXT,
    reference_range VARCHAR(100),
    document_path VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- 8. PRESCRIPTIONS TABLE
CREATE TABLE IF NOT EXISTS prescriptions (
    prescription_id INT AUTO_INCREMENT PRIMARY KEY,
    prescription_code VARCHAR(30) NOT NULL UNIQUE,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    appointment_id INT,
    diagnosis TEXT NOT NULL,
    doctor_notes TEXT,
    prescription_date DATE NOT NULL,
    follow_up_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON DELETE CASCADE,
    FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- 9. PHARMACY MEDICINES & INVENTORY TABLE
CREATE TABLE IF NOT EXISTS medicines (
    medicine_id INT AUTO_INCREMENT PRIMARY KEY,
    medicine_code VARCHAR(30) NOT NULL UNIQUE,
    medicine_name VARCHAR(150) NOT NULL,
    category ENUM('Antibiotics', 'Analgesics', 'Antipyretics', 'Cardiovascular', 'Antidiabetic', 'Respiratory', 'Dermatological', 'Gastrointestinal', 'Vitamins & Supplements', 'Other') NOT NULL,
    manufacturer VARCHAR(100) NOT NULL,
    batch_number VARCHAR(50) NOT NULL,
    available_quantity INT NOT NULL DEFAULT 0,
    min_stock_level INT NOT NULL DEFAULT 20,
    unit_price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    mfg_date DATE NOT NULL,
    expiry_date DATE NOT NULL,
    stock_status ENUM('In Stock', 'Low Stock', 'Out of Stock', 'Expired') NOT NULL DEFAULT 'In Stock',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_med_expiry (expiry_date),
    INDEX idx_med_stock (available_quantity)
) ENGINE=InnoDB;

-- 10. PRESCRIPTION MEDICINES DETAIL TABLE
CREATE TABLE IF NOT EXISTS prescription_medicines (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    prescription_id INT NOT NULL,
    medicine_name VARCHAR(150) NOT NULL,
    dosage VARCHAR(50) NOT NULL,
    frequency VARCHAR(50) NOT NULL,
    duration VARCHAR(50) NOT NULL,
    instructions TEXT,
    FOREIGN KEY (prescription_id) REFERENCES prescriptions(prescription_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 11. PATIENT MEDICAL HISTORY TABLE
CREATE TABLE IF NOT EXISTS medical_history (
    history_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    recorded_date DATE NOT NULL,
    condition_name VARCHAR(150) NOT NULL,
    description TEXT,
    treating_physician VARCHAR(100),
    is_chronic BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 12. BILLS TABLE (Indian Hospital Financial Ledger)
CREATE TABLE IF NOT EXISTS bills (
    bill_id INT AUTO_INCREMENT PRIMARY KEY,
    bill_number VARCHAR(30) NOT NULL UNIQUE,
    patient_id INT NOT NULL,
    appointment_id INT,
    bill_date DATE NOT NULL,
    consultation_charges DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    lab_charges DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    pharmacy_charges DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    other_charges DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    subtotal DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    tax_rate DECIMAL(5, 2) NOT NULL DEFAULT 5.00,
    tax_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    total_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    paid_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    balance_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    payment_status ENUM('Paid', 'Partially Paid', 'Pending') NOT NULL DEFAULT 'Pending',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id) ON DELETE SET NULL,
    INDEX idx_bill_pat (patient_id),
    INDEX idx_bill_status (payment_status)
) ENGINE=InnoDB;

-- 13. BILL ITEMS BREAKDOWN
CREATE TABLE IF NOT EXISTS bill_items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    bill_id INT NOT NULL,
    service_category ENUM('Consultation', 'Laboratory', 'Pharmacy', 'Nursing & Bed', 'Procedures', 'Other') NOT NULL,
    item_description VARCHAR(200) NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    unit_price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    total_price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    FOREIGN KEY (bill_id) REFERENCES bills(bill_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 14. PAYMENTS TRANSACTION TABLE
CREATE TABLE IF NOT EXISTS payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    bill_id INT NOT NULL,
    patient_id INT NOT NULL,
    amount_paid DECIMAL(10, 2) NOT NULL,
    payment_method ENUM('Cash', 'UPI', 'Debit Card', 'Credit Card', 'Net Banking', 'Other') NOT NULL DEFAULT 'Cash',
    transaction_ref VARCHAR(100),
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payment_status ENUM('Success', 'Pending', 'Failed') NOT NULL DEFAULT 'Success',
    notes TEXT,
    FOREIGN KEY (bill_id) REFERENCES bills(bill_id) ON DELETE CASCADE,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
) ENGINE=InnoDB;

