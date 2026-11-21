-- ========================================================
-- MEDAXIS – Hospital Management System
-- Seed / Fictional Demo Data (Indian Hospital Context)
-- ========================================================

USE medaxis_db;

-- 1. SEED ADMIN USER
-- Password hash for 'admin123' (PBKDF2 SHA256)
INSERT INTO admins (admin_id, username, password_hash, full_name, email, mobile, role, status) VALUES
(1, 'admin', 'pbkdf2:sha256:600000$medaxis$7f2d5e3c8a9b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d', 'Chief Medical Administrator', 'admin@medaxis.hospital', '+91 98765 43210', 'Super Administrator', 'active')
ON DUPLICATE KEY UPDATE full_name=VALUES(full_name);

-- 2. SEED 11 CLINICAL DEPARTMENTS
INSERT INTO departments (dept_id, dept_name, description, hod_name, contact_ext) VALUES
(1, 'General Medicine', 'Primary adult healthcare, infectious illness, diabetes, and preventive medicine', 'Dr. Rajesh Sharma', '101'),
(2, 'Cardiology', 'Comprehensive cardiovascular diagnostics, ECG, Echocardiography, and heart care', 'Dr. Vikram Malhotra', '102'),
(3, 'Neurology', 'Disorders of the brain, spinal cord, and peripheral nervous system', 'Dr. Ananya Iyer', '103'),
(4, 'Orthopedics', 'Bones, joint reconstruction, trauma surgery, and sports medicine', 'Dr. Rohan Gupta', '104'),
(5, 'Dermatology', 'Advanced skin, hair, nail disorders, and clinical cosmetology', 'Dr. Meera Reddy', '105'),
(6, 'Pediatrics', 'Neonatal, infant, child, and adolescent comprehensive healthcare', 'Dr. Sunita Kulkarni', '106'),
(7, 'Gynecology', 'Obstetrics, antenatal care, maternity, and women reproductive health', 'Dr. Priya Nambiar', '107'),
(8, 'ENT', 'Ear, Nose, Throat, audiology diagnostics, and head-neck interventions', 'Dr. Arvind Swaminathan', '108'),
(9, 'Ophthalmology', 'Comprehensive vision care, cataracts, retina diagnostics, and refractive correction', 'Dr. Neha Saxena', '109'),
(10, 'Dentistry', 'Orthodontics, restorative dentistry, maxillofacial hygiene, and dental surgery', 'Dr. Sameer Deshmukh', '110'),
(11, 'General Surgery', 'Minimally invasive laparoscopic, abdominal, trauma, and elective surgical procedures', 'Dr. Alok Verma', '111')
ON DUPLICATE KEY UPDATE dept_name=VALUES(dept_name);

-- 3. SEED DOCTORS
INSERT INTO doctors (doctor_id, doctor_code, dept_id, full_name, specialization, qualification, experience_years, email, mobile_number, consultation_fees, room_no, status) VALUES
(1, 'DOC-101', 1, 'Dr. Rajesh Sharma', 'Internal Medicine & Diabetology', 'MBBS, MD (General Medicine)', 14, 'dr.rajesh@medaxis.hospital', '9820123456', 600.00, 'Room 101', 'active'),
(2, 'DOC-102', 2, 'Dr. Vikram Malhotra', 'Interventional Cardiology', 'MBBS, MD, DM (Cardiology), FACC', 18, 'dr.vikram@medaxis.hospital', '9820234567', 1000.00, 'Room 205', 'active'),
(3, 'DOC-103', 3, 'Dr. Ananya Iyer', 'Clinical Neurology & Neurophysiology', 'MBBS, MD, DM (Neurology)', 12, 'dr.ananya@medaxis.hospital', '9820345678', 900.00, 'Room 302', 'active'),
(4, 'DOC-104', 4, 'Dr. Rohan Gupta', 'Orthopedic & Joint Replacement', 'MBBS, MS (Ortho), DNB', 15, 'dr.rohan@medaxis.hospital', '9820456789', 750.00, 'Room 108', 'active'),
(5, 'DOC-105', 5, 'Dr. Meera Reddy', 'Dermatology & Dermatosurgery', 'MBBS, MD (Dermatology, Venereology)', 9, 'dr.meera@medaxis.hospital', '9820567890', 650.00, 'Room 114', 'active'),
(6, 'DOC-106', 6, 'Dr. Sunita Kulkarni', 'Pediatrics & Neonatology', 'MBBS, DCH, MD (Pediatrics)', 11, 'dr.sunita@medaxis.hospital', '9820678901', 550.00, 'Room 120', 'active')
ON DUPLICATE KEY UPDATE doctor_code=VALUES(doctor_code);

-- 4. SEED DOCTOR AVAILABILITY
INSERT INTO doctor_availability (doctor_id, day_of_week, start_time, end_time, slot_duration_minutes, is_active) VALUES
(1, 'Monday', '09:00:00', '13:00:00', 20, 1),
(1, 'Wednesday', '09:00:00', '13:00:00', 20, 1),
(1, 'Friday', '09:00:00', '13:00:00', 20, 1),
(2, 'Monday', '10:00:00', '15:00:00', 30, 1),
(2, 'Tuesday', '10:00:00', '15:00:00', 30, 1),
(2, 'Thursday', '10:00:00', '15:00:00', 30, 1),
(3, 'Tuesday', '11:00:00', '16:00:00', 30, 1),
(3, 'Thursday', '11:00:00', '16:00:00', 30, 1),
(4, 'Wednesday', '09:30:00', '14:30:00', 20, 1),
(4, 'Saturday', '09:30:00', '14:30:00', 20, 1),
(5, 'Monday', '14:00:00', '18:00:00', 15, 1),
(5, 'Friday', '14:00:00', '18:00:00', 15, 1),
(6, 'Tuesday', '09:00:00', '13:00:00', 15, 1),
(6, 'Saturday', '09:00:00', '13:00:00', 15, 1)
ON DUPLICATE KEY UPDATE is_active=VALUES(is_active);

-- 5. SEED PATIENTS (Indian Format)
INSERT INTO patients (patient_id, patient_code, full_name, dob, age, gender, blood_group, mobile_number, email, address, city, state, pincode, status) VALUES
(1, 'MED-PAT-2026-0001', 'Aarav Mehta', '1988-04-12', 38, 'Male', 'B+', '9819123451', 'aarav.mehta@example.com', 'Flat 402, Shanti Heights, Link Road, Andheri West', 'Mumbai', 'Maharashtra', '400053', 'active'),
(2, 'MED-PAT-2026-0002', 'Priya Patel', '1994-08-23', 32, 'Female', 'O+', '9819234562', 'priya.patel@example.com', 'B-14, Neelkanth Valley, Ghatkopar East', 'Mumbai', 'Maharashtra', '400077', 'active'),
(3, 'MED-PAT-2026-0003', 'Rahul Verma', '1975-11-05', 51, 'Male', 'A+', '9819345673', 'rahul.verma@example.com', '12, Ashoka Enclave, Sector 14', 'Gurugram', 'Haryana', '122001', 'active'),
(4, 'MED-PAT-2026-0004', 'Sneha Iyer', '2001-02-17', 25, 'Female', 'AB+', '9819456784', 'sneha.iyer@example.com', '78, 4th Cross, Indiranagar', 'Bengaluru', 'Karnataka', '560038', 'active'),
(5, 'MED-PAT-2026-0005', 'Manoj Nair', '1962-09-30', 64, 'Male', 'O-', '9819567895', 'manoj.nair@example.com', 'Flat 101, Palm Meadows, Kaloor', 'Kochi', 'Kerala', '682017', 'active')
ON DUPLICATE KEY UPDATE patient_code=VALUES(patient_code);

-- 6. SEED PHARMACY MEDICINES INVENTORY (Real Indian Brands & Alerts)
INSERT INTO medicines (medicine_id, medicine_code, medicine_name, category, manufacturer, batch_number, available_quantity, min_stock_level, unit_price, mfg_date, expiry_date, stock_status) VALUES
(1, 'MED-RX-001', 'Dolo 650 (Paracetamol 650mg)', 'Antipyretics', 'Micro Labs Ltd', 'ML-D650-24B', 240, 50, 32.50, '2024-03-01', '2026-02-28', 'In Stock'),
(2, 'MED-RX-002', 'Azithral 500 (Azithromycin 500mg)', 'Antibiotics', 'Alembic Pharmaceuticals', 'AL-AZ5-99A', 14, 30, 118.00, '2024-05-15', '2026-04-30', 'Low Stock'),
(3, 'MED-RX-003', 'Pan-D (Pantoprazole + Domperidone)', 'Gastrointestinal', 'Alkem Laboratories', 'AK-PND-81C', 180, 40, 165.00, '2024-02-10', '2026-01-31', 'In Stock'),
(4, 'MED-RX-004', 'Telma 40 (Telmisartan 40mg)', 'Cardiovascular', 'Glenmark Pharmaceuticals', 'GL-TL4-33K', 8, 25, 95.00, '2024-01-20', '2026-12-15', 'Low Stock'),
(5, 'MED-RX-005', 'Augmentin 625 Duo (Amoxicillin + Clav)', 'Antibiotics', 'GlaxoSmithKline (GSK)', 'GSK-AG-104', 85, 20, 204.50, '2024-06-01', '2025-12-31', 'In Stock'),
(6, 'MED-RX-006', 'Glycomet GP2 (Metformin + Glimepiride)', 'Antidiabetic', 'USV Private Limited', 'USV-GP2-55', 120, 30, 142.00, '2024-04-10', '2026-03-31', 'In Stock'),
(7, 'MED-RX-007', 'Allegra 120mg (Fexofenadine)', 'Respiratory', 'Sanofi India Ltd', 'SNF-AL-702', 15, 20, 198.00, '2023-11-01', '2026-11-25', 'Low Stock'),
(8, 'MED-RX-008', 'Becosules Z Capsules (B-Complex + Zinc)', 'Vitamins & Supplements', 'Pfizer India', 'PFZ-BCZ-12', 320, 50, 48.00, '2024-01-01', '2026-12-31', 'In Stock'),
(9, 'MED-RX-009', 'Cipcal 500 (Calcium + Vitamin D3)', 'Vitamins & Supplements', 'Cipla Ltd', 'CIP-CP5-40', 0, 30, 89.00, '2023-08-01', '2025-07-31', 'Out of Stock'),
(10, 'MED-RX-010', 'Erythrocin 250 (Erythromycin)', 'Antibiotics', 'Abbott India', 'ABT-ER-009', 5, 20, 65.00, '2022-09-01', '2024-08-31', 'Expired')
ON DUPLICATE KEY UPDATE medicine_code=VALUES(medicine_code);

-- 7. SEED APPOINTMENTS
INSERT INTO appointments (appointment_id, appointment_code, patient_id, doctor_id, dept_id, appointment_date, appointment_time, consultation_fees, status, notes) VALUES
(1, 'MED-APT-2026-001', 1, 1, 1, CURDATE(), '09:30:00', 600.00, 'Booked', 'Routine diabetic follow-up and blood sugar check'),
(2, 'MED-APT-2026-002', 2, 5, 5, CURDATE(), '14:30:00', 650.00, 'Booked', 'Severe allergic contact dermatitis rash on forearms'),
(3, 'MED-APT-2026-003', 3, 2, 2, CURDATE(), '10:30:00', 1000.00, 'Booked', 'Exertional chest tightness, post-treadmill evaluation'),
(4, 'MED-APT-2026-004', 4, 3, 3, DATE_ADD(CURDATE(), INTERVAL 1 DAY), '11:30:00', 900.00, 'Booked', 'Migraine with aura episodes recurring weekly'),
(5, 'MED-APT-2026-005', 5, 4, 4, DATE_SUB(CURDATE(), INTERVAL 2 DAY), '10:00:00', 750.00, 'Completed', 'Right knee osteoarthritis assessment & intra-articular injection')
ON DUPLICATE KEY UPDATE appointment_code=VALUES(appointment_code);

-- 8. SEED LAB REPORTS
INSERT INTO lab_reports (report_id, report_code, patient_id, doctor_id, test_name, test_date, report_status, result_summary, reference_range) VALUES
(1, 'LAB-2026-101', 1, 1, 'HbA1c & Fasting Blood Sugar', CURDATE(), 'Completed', 'Fasting Blood Glucose: 132 mg/dL; HbA1c: 7.2% (Moderate control)', 'HbA1c < 5.7% (Normal)'),
(2, 'LAB-2026-102', 3, 2, 'Lipid Profile & 2D-Echocardiography', CURDATE(), 'In Progress', 'Serum Cholesterol: 228 mg/dL, LDL: 144 mg/dL. Echo report pending.', 'Total < 200 mg/dL'),
(3, 'LAB-2026-103', 5, 4, 'Bilateral Knee X-Ray (Standing AP/Lat)', DATE_SUB(CURDATE(), INTERVAL 2 DAY), 'Completed', 'Medial compartment joint space narrowing noted in Right Knee, Grade II Kellgren-Lawrence.', 'Normal Joint Space')
ON DUPLICATE KEY UPDATE report_code=VALUES(report_code);

-- 9. SEED PRESCRIPTIONS
INSERT INTO prescriptions (prescription_id, prescription_code, patient_id, doctor_id, appointment_id, diagnosis, doctor_notes, prescription_date, follow_up_date) VALUES
(1, 'RX-2026-001', 1, 1, 1, 'Type 2 Diabetes Mellitus with Mild Hyperglycemia', 'Maintain 45 minutes brisk walking. Strict low glycemic diet.', CURDATE(), DATE_ADD(CURDATE(), INTERVAL 30 DAY)),
(2, 'RX-2026-002', 5, 4, 5, 'Bilateral Osteoarthritis Knee (Right > Left)', 'Avoid deep squatting, use knee support brace while walking long distances.', DATE_SUB(CURDATE(), INTERVAL 2 DAY), DATE_ADD(CURDATE(), INTERVAL 45 DAY))
ON DUPLICATE KEY UPDATE prescription_code=VALUES(prescription_code);

-- 10. SEED PRESCRIPTION MEDICINES
INSERT INTO prescription_medicines (prescription_id, medicine_name, dosage, frequency, duration, instructions) VALUES
(1, 'Glycomet GP2 (Metformin + Glimepiride)', '1 Tablet', 'Twice daily before breakfast and dinner', '30 Days', 'Do not skip meals after taking tablet'),
(1, 'Becosules Z Capsules', '1 Capsule', 'Once daily post lunch', '30 Days', 'Take with full glass of water'),
(2, 'Dolo 650mg', '1 Tablet', 'As needed for acute knee pain (SOS)', '5 Days', 'Maximum 3 tablets in 24 hours'),
(2, 'Cipcal 500mg', '1 Tablet', 'Once daily at bedtime', '60 Days', 'Take with milk or water')
ON DUPLICATE KEY UPDATE item_id=VALUES(item_id);

-- 11. SEED MEDICAL HISTORY
INSERT INTO medical_history (patient_id, recorded_date, condition_name, description, treating_physician, is_chronic) VALUES
(1, '2021-04-10', 'Type 2 Diabetes Mellitus', 'Diagnosed during routine annual executive health checkup; managed with oral hypoglycemic agents.', 'Dr. Rajesh Sharma', 1),
(3, '2019-11-15', 'Mild Essential Hypertension', 'Occasional systolic elevation (140-145 mmHg). Prescribed lifestyle modification.', 'Dr. Vikram Malhotra', 1),
(5, '2018-06-20', 'Knee Osteoarthritis', 'Gradual onset bilateral knee pain after retired bank service.', 'Dr. Rohan Gupta', 1);

-- 12. SEED BILLS (Indian Hospital Billing in INR ₹)
INSERT INTO bills (bill_id, bill_number, patient_id, appointment_id, bill_date, consultation_charges, lab_charges, pharmacy_charges, other_charges, subtotal, tax_rate, tax_amount, total_amount, paid_amount, balance_amount, payment_status, notes) VALUES
(1, 'MED-INV-2026-001', 1, 1, CURDATE(), 600.00, 750.00, 380.00, 50.00, 1780.00, 5.00, 89.00, 1869.00, 1869.00, 0.00, 'Paid', 'Consultation, HbA1c lab tests, and 30-day oral medicine dispensation.'),
(2, 'MED-INV-2026-002', 3, 3, CURDATE(), 1000.00, 1800.00, 0.00, 100.00, 2900.00, 5.00, 145.00, 3045.00, 1500.00, 1545.00, 'Partially Paid', 'Cardiology initial consultation & 2D Echo charges. ₹1,500 advance settled via UPI.'),
(3, 'MED-INV-2026-003', 5, 5, DATE_SUB(CURDATE(), INTERVAL 2 DAY), 750.00, 900.00, 220.00, 0.00, 1870.00, 5.00, 93.50, 1963.50, 0.00, 1963.50, 'Pending', 'Orthopedic consultation and Bilateral Knee X-Ray imaging charges.')
ON DUPLICATE KEY UPDATE bill_number=VALUES(bill_number);

-- 13. SEED BILL ITEMS
INSERT INTO bill_items (item_id, bill_id, service_category, item_description, quantity, unit_price, total_price) VALUES
(1, 1, 'Consultation', 'General Medicine Consultation (Dr. Rajesh Sharma)', 1, 600.00, 600.00),
(2, 1, 'Laboratory', 'HbA1c & Fasting Blood Glucose Profile', 1, 750.00, 750.00),
(3, 1, 'Pharmacy', 'Glycomet GP2 + Becosules Z (30 Days Dispensation)', 1, 380.00, 380.00),
(4, 1, 'Other', 'Bio-Medical Waste & Hospital Registration Fee', 1, 50.00, 50.00),
(5, 2, 'Consultation', 'Senior Cardiology Specialist Consultation (Dr. Vikram Malhotra)', 1, 1000.00, 1000.00),
(6, 2, 'Laboratory', '2D Echocardiography & Color Doppler Diagnostic', 1, 1800.00, 1800.00),
(7, 2, 'Other', 'Cardiology Administrative Documentation Fee', 1, 100.00, 100.00),
(8, 3, 'Consultation', 'Senior Orthopedic Specialist Consultation (Dr. Rohan Gupta)', 1, 750.00, 750.00),
(9, 3, 'Laboratory', 'Digital Bilateral Knee Joint X-Ray (AP & Lateral Standing)', 1, 900.00, 900.00),
(10, 3, 'Pharmacy', 'Dolo 650 & Cipcal 500 Initial Dispensation', 1, 220.00, 220.00)
ON DUPLICATE KEY UPDATE item_id=VALUES(item_id);

-- 14. SEED PAYMENTS (UPI, Card, Cash)
INSERT INTO payments (payment_id, bill_id, patient_id, amount_paid, payment_method, transaction_ref, notes) VALUES
(1, 1, 1, 1869.00, 'UPI', 'UPI/2026/ICICI/994102914', 'Settled via Google Pay UPI at billing counter'),
(2, 2, 3, 1500.00, 'UPI', 'UPI/2026/HDFC/883109411', 'Advance deposit collected via PhonePe UPI');

