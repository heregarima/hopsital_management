import os
import json
import sqlite3
import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse

# Try importing pymysql for MySQL connectivity
try:
    import pymysql
    import pymysql.cursors
    HAS_PYMYSQL = True
except ImportError:
    HAS_PYMYSQL = False

PORT = 5000
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')
SQLITE_DB = os.path.join(BASE_DIR, 'database', 'medaxis.sqlite')

# Database Configuration
MYSQL_HOST = 'localhost'
MYSQL_PORT = 3306
MYSQL_USER = 'root'
MYSQL_PASSWORD = ''
MYSQL_DB = 'medaxis_db'

def get_db():
    """Connect to MySQL if available, or fall back to SQLite with identical schema and data."""
    if HAS_PYMYSQL:
        try:
            conn = pymysql.connect(
                host=MYSQL_HOST,
                port=MYSQL_PORT,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=MYSQL_DB,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True
            )
            return conn, 'mysql'
        except Exception:
            pass

    # SQLite Fallback
    is_new = not os.path.exists(SQLITE_DB) or os.path.getsize(SQLITE_DB) == 0
    os.makedirs(os.path.dirname(SQLITE_DB), exist_ok=True)
    conn = sqlite3.connect(SQLITE_DB)
    conn.row_factory = sqlite3.Row
    if is_new:
        init_sqlite(conn)
    return conn, 'sqlite'

def query_db(query, args=(), one=False):
    conn, engine = get_db()
    cursor = conn.cursor()
    formatted_query = query
    if engine == 'sqlite':
        formatted_query = query.replace('%s', '?').replace('CURDATE()', "DATE('now')").replace('NOW()', "DATETIME('now')")
    cursor.execute(formatted_query, args)
    if engine == 'sqlite':
        rows = [dict(row) for row in cursor.fetchall()]
    else:
        rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return (rows[0] if rows else None) if one else rows

def execute_db(query, args=(), return_id=False):
    conn, engine = get_db()
    cursor = conn.cursor()
    formatted_query = query
    if engine == 'sqlite':
        formatted_query = query.replace('%s', '?').replace('CURDATE()', "DATE('now')").replace('NOW()', "DATETIME('now')")
    cursor.execute(formatted_query, args)
    if engine == 'sqlite':
        conn.commit()
        last_id = cursor.lastrowid
    else:
        last_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return last_id if return_id else True

def init_sqlite(conn):
    """Initializes local SQLite schema with full Indian demo data."""
    cur = conn.cursor()
    cur.executescript('''
    CREATE TABLE IF NOT EXISTS admins (
        admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        mobile TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'Administrator',
        status TEXT NOT NULL DEFAULT 'active',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS departments (
        dept_id INTEGER PRIMARY KEY AUTOINCREMENT,
        dept_name TEXT UNIQUE NOT NULL,
        description TEXT,
        hod_name TEXT,
        contact_ext TEXT
    );

    CREATE TABLE IF NOT EXISTS doctors (
        doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
        doctor_code TEXT UNIQUE NOT NULL,
        dept_id INTEGER NOT NULL,
        full_name TEXT NOT NULL,
        specialization TEXT NOT NULL,
        qualification TEXT NOT NULL,
        experience_years INTEGER DEFAULT 0,
        email TEXT UNIQUE NOT NULL,
        mobile_number TEXT NOT NULL,
        consultation_fees REAL DEFAULT 500.00,
        room_no TEXT,
        status TEXT DEFAULT 'active'
    );

    CREATE TABLE IF NOT EXISTS patients (
        patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_code TEXT UNIQUE NOT NULL,
        full_name TEXT NOT NULL,
        dob TEXT NOT NULL,
        age INTEGER NOT NULL,
        gender TEXT NOT NULL,
        blood_group TEXT NOT NULL,
        mobile_number TEXT UNIQUE NOT NULL,
        email TEXT,
        address TEXT NOT NULL,
        city TEXT NOT NULL,
        state TEXT NOT NULL,
        pincode TEXT NOT NULL,
        status TEXT DEFAULT 'active',
        registered_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS appointments (
        appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        appointment_code TEXT UNIQUE NOT NULL,
        patient_id INTEGER NOT NULL,
        doctor_id INTEGER NOT NULL,
        dept_id INTEGER NOT NULL,
        appointment_date TEXT NOT NULL,
        appointment_time TEXT NOT NULL,
        consultation_fees REAL NOT NULL,
        status TEXT DEFAULT 'Booked',
        notes TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS lab_reports (
        report_id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_code TEXT UNIQUE NOT NULL,
        patient_id INTEGER NOT NULL,
        doctor_id INTEGER,
        test_name TEXT NOT NULL,
        test_date TEXT NOT NULL,
        report_status TEXT DEFAULT 'Pending',
        result_summary TEXT,
        reference_range TEXT,
        document_path TEXT
    );

    CREATE TABLE IF NOT EXISTS prescriptions (
        prescription_id INTEGER PRIMARY KEY AUTOINCREMENT,
        prescription_code TEXT UNIQUE NOT NULL,
        patient_id INTEGER NOT NULL,
        doctor_id INTEGER NOT NULL,
        appointment_id INTEGER,
        diagnosis TEXT NOT NULL,
        doctor_notes TEXT,
        prescription_date TEXT NOT NULL,
        follow_up_date TEXT
    );

    CREATE TABLE IF NOT EXISTS prescription_medicines (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        prescription_id INTEGER NOT NULL,
        medicine_name TEXT NOT NULL,
        dosage TEXT NOT NULL,
        frequency TEXT NOT NULL,
        duration TEXT NOT NULL,
        instructions TEXT
    );

    CREATE TABLE IF NOT EXISTS medical_history (
        history_id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        recorded_date TEXT NOT NULL,
        condition_name TEXT NOT NULL,
        description TEXT,
        treating_physician TEXT,
        is_chronic INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS medicines (
        medicine_id INTEGER PRIMARY KEY AUTOINCREMENT,
        medicine_code TEXT UNIQUE NOT NULL,
        medicine_name TEXT NOT NULL,
        category TEXT NOT NULL,
        manufacturer TEXT NOT NULL,
        batch_number TEXT NOT NULL,
        available_quantity INTEGER NOT NULL DEFAULT 0,
        min_stock_level INTEGER NOT NULL DEFAULT 20,
        unit_price REAL NOT NULL DEFAULT 0.00,
        mfg_date TEXT NOT NULL,
        expiry_date TEXT NOT NULL,
        stock_status TEXT DEFAULT 'In Stock'
    );

    CREATE TABLE IF NOT EXISTS bills (
        bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
        bill_number TEXT UNIQUE NOT NULL,
        patient_id INTEGER NOT NULL,
        appointment_id INTEGER,
        bill_date TEXT NOT NULL,
        consultation_charges REAL DEFAULT 0.00,
        lab_charges REAL DEFAULT 0.00,
        pharmacy_charges REAL DEFAULT 0.00,
        other_charges REAL DEFAULT 0.00,
        subtotal REAL DEFAULT 0.00,
        tax_rate REAL DEFAULT 5.00,
        tax_amount REAL DEFAULT 0.00,
        total_amount REAL DEFAULT 0.00,
        paid_amount REAL DEFAULT 0.00,
        balance_amount REAL DEFAULT 0.00,
        payment_status TEXT DEFAULT 'Pending',
        notes TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS payments (
        payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        bill_id INTEGER NOT NULL,
        patient_id INTEGER NOT NULL,
        amount_paid REAL NOT NULL,
        payment_method TEXT DEFAULT 'Cash',
        transaction_ref TEXT,
        payment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        notes TEXT
    );
    ''')

    # Seed Admin
    cur.execute("INSERT OR IGNORE INTO admins (admin_id, username, password_hash, full_name, email, mobile, role) VALUES (1, 'admin', 'admin123', 'Chief Medical Administrator', 'admin@medaxis.hospital', '+91 98765 43210', 'Super Administrator')")

    # Seed 11 Departments
    cur.executescript('''
    INSERT OR IGNORE INTO departments (dept_id, dept_name, description, hod_name, contact_ext) VALUES
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
    (11, 'General Surgery', 'Minimally invasive laparoscopic, abdominal, trauma, and elective surgery', 'Dr. Alok Verma', '111');

    INSERT OR IGNORE INTO doctors (doctor_id, doctor_code, dept_id, full_name, specialization, qualification, experience_years, email, mobile_number, consultation_fees, room_no) VALUES
    (1, 'DOC-101', 1, 'Dr. Rajesh Sharma', 'Internal Medicine & Diabetology', 'MBBS, MD', 14, 'dr.rajesh@medaxis.hospital', '9820123456', 600.00, 'Room 101'),
    (2, 'DOC-102', 2, 'Dr. Vikram Malhotra', 'Interventional Cardiology', 'MBBS, MD, DM, FACC', 18, 'dr.vikram@medaxis.hospital', '9820234567', 1000.00, 'Room 205'),
    (3, 'DOC-103', 3, 'Dr. Ananya Iyer', 'Clinical Neurology', 'MBBS, MD, DM', 12, 'dr.ananya@medaxis.hospital', '9820345678', 900.00, 'Room 302'),
    (4, 'DOC-104', 4, 'Dr. Rohan Gupta', 'Orthopedic & Joint Replacement', 'MBBS, MS (Ortho)', 15, 'dr.rohan@medaxis.hospital', '9820456789', 750.00, 'Room 108'),
    (5, 'DOC-105', 5, 'Dr. Meera Reddy', 'Dermatology & Dermatosurgery', 'MBBS, MD', 9, 'dr.meera@medaxis.hospital', '9820567890', 650.00, 'Room 114'),
    (6, 'DOC-106', 6, 'Dr. Sunita Kulkarni', 'Pediatrics & Neonatology', 'MBBS, DCH, MD', 11, 'dr.sunita@medaxis.hospital', '9820678901', 550.00, 'Room 120');

    INSERT OR IGNORE INTO patients (patient_id, patient_code, full_name, dob, age, gender, blood_group, mobile_number, email, address, city, state, pincode) VALUES
    (1, 'MED-PAT-2026-0001', 'Aarav Mehta', '1988-04-12', 38, 'Male', 'B+', '9819123451', 'aarav.mehta@example.com', 'Flat 402, Shanti Heights, Link Road, Andheri West', 'Mumbai', 'Maharashtra', '400053'),
    (2, 'MED-PAT-2026-0002', 'Priya Patel', '1994-08-23', 32, 'Female', 'O+', '9819234562', 'priya.patel@example.com', 'B-14, Neelkanth Valley, Ghatkopar East', 'Mumbai', 'Maharashtra', '400077'),
    (3, 'MED-PAT-2026-0003', 'Rahul Verma', '1975-11-05', 51, 'Male', 'A+', '9819345673', 'rahul.verma@example.com', '12, Ashoka Enclave, Sector 14', 'Gurugram', 'Haryana', '122001'),
    (4, 'MED-PAT-2026-0004', 'Sneha Iyer', '2001-02-17', 25, 'Female', 'AB+', '9819456784', 'sneha.iyer@example.com', '78, 4th Cross, Indiranagar', 'Bengaluru', 'Karnataka', '560038'),
    (5, 'MED-PAT-2026-0005', 'Manoj Nair', '1962-09-30', 64, 'Male', 'O-', '9819567895', 'manoj.nair@example.com', 'Flat 101, Palm Meadows, Kaloor', 'Kochi', 'Kerala', '682017');

    INSERT OR IGNORE INTO medicines (medicine_id, medicine_code, medicine_name, category, manufacturer, batch_number, available_quantity, min_stock_level, unit_price, mfg_date, expiry_date, stock_status) VALUES
    (1, 'MED-RX-001', 'Dolo 650 (Paracetamol 650mg)', 'Antipyretics', 'Micro Labs Ltd', 'ML-D650-24B', 240, 50, 32.50, '2024-03-01', '2026-02-28', 'In Stock'),
    (2, 'MED-RX-002', 'Azithral 500 (Azithromycin 500mg)', 'Antibiotics', 'Alembic Pharmaceuticals', 'AL-AZ5-99A', 14, 30, 118.00, '2024-05-15', '2026-04-30', 'Low Stock'),
    (3, 'MED-RX-003', 'Pan-D (Pantoprazole + Domperidone)', 'Gastrointestinal', 'Alkem Laboratories', 'AK-PND-81C', 180, 40, 165.00, '2024-02-10', '2026-01-31', 'In Stock'),
    (4, 'MED-RX-004', 'Telma 40 (Telmisartan 40mg)', 'Cardiovascular', 'Glenmark Pharmaceuticals', 'GL-TL4-33K', 8, 25, 95.00, '2024-01-20', '2026-12-15', 'Low Stock'),
    (5, 'MED-RX-005', 'Augmentin 625 Duo (Amoxicillin + Clav)', 'Antibiotics', 'GSK India', 'GSK-AG-104', 85, 20, 204.50, '2024-06-01', '2025-12-31', 'In Stock'),
    (6, 'MED-RX-006', 'Glycomet GP2 (Metformin + Glimepiride)', 'Antidiabetic', 'USV Private Limited', 'USV-GP2-55', 120, 30, 142.00, '2024-04-10', '2026-03-31', 'In Stock'),
    (7, 'MED-RX-007', 'Allegra 120mg (Fexofenadine)', 'Respiratory', 'Sanofi India Ltd', 'SNF-AL-702', 15, 20, 198.00, '2023-11-01', '2026-11-25', 'Low Stock'),
    (8, 'MED-RX-008', 'Becosules Z Capsules (B-Complex)', 'Vitamins & Supplements', 'Pfizer India', 'PFZ-BCZ-12', 320, 50, 48.00, '2024-01-01', '2026-12-31', 'In Stock'),
    (9, 'MED-RX-009', 'Cipcal 500 (Calcium + Vitamin D3)', 'Vitamins & Supplements', 'Cipla Ltd', 'CIP-CP5-40', 0, 30, 89.00, '2023-08-01', '2025-07-31', 'Out of Stock'),
    (10, 'MED-RX-010', 'Erythrocin 250 (Erythromycin)', 'Antibiotics', 'Abbott India', 'ABT-ER-009', 5, 20, 65.00, '2022-09-01', '2024-08-31', 'Expired');

    INSERT OR IGNORE INTO appointments (appointment_id, appointment_code, patient_id, doctor_id, dept_id, appointment_date, appointment_time, consultation_fees, status, notes) VALUES
    (1, 'MED-APT-2026-001', 1, 1, 1, DATE('now'), '09:30', 600.00, 'Booked', 'Routine diabetic follow-up'),
    (2, 'MED-APT-2026-002', 2, 5, 5, DATE('now'), '14:30', 650.00, 'Booked', 'Allergic dermatitis skin rash'),
    (3, 'MED-APT-2026-003', 3, 2, 2, DATE('now'), '10:30', 1000.00, 'Booked', 'Exertional chest tightness'),
    (4, 'MED-APT-2026-004', 4, 3, 3, DATE('now', '+1 day'), '11:30', 900.00, 'Booked', 'Recurrent migraine evaluation'),
    (5, 'MED-APT-2026-005', 5, 4, 4, DATE('now', '-2 day'), '10:00', 750.00, 'Completed', 'Right knee osteoarthritis assessment');

    INSERT OR IGNORE INTO lab_reports (report_id, report_code, patient_id, doctor_id, test_name, test_date, report_status, result_summary, reference_range) VALUES
    (1, 'LAB-2026-101', 1, 1, 'HbA1c & Fasting Blood Glucose', DATE('now'), 'Completed', 'Fasting Blood Glucose: 132 mg/dL; HbA1c: 7.2% (Moderate control)', 'HbA1c < 5.7% (Normal)'),
    (2, 'LAB-2026-102', 3, 2, 'Lipid Profile & 2D-Echocardiography', DATE('now'), 'In Progress', 'Serum Cholesterol: 228 mg/dL, LDL: 144 mg/dL. Echo report pending.', 'Total < 200 mg/dL'),
    (3, 'LAB-2026-103', 5, 4, 'Bilateral Knee X-Ray (Standing)', DATE('now', '-2 day'), 'Completed', 'Medial joint space narrowing noted in Right Knee, Grade II.', 'Normal Joint Space');

    INSERT OR IGNORE INTO prescriptions (prescription_id, prescription_code, patient_id, doctor_id, appointment_id, diagnosis, doctor_notes, prescription_date, follow_up_date) VALUES
    (1, 'RX-2026-001', 1, 1, 1, 'Type 2 Diabetes Mellitus with Mild Hyperglycemia', 'Maintain 45 minutes brisk walking. Strict low glycemic diet.', DATE('now'), DATE('now', '+30 day')),
    (2, 'RX-2026-002', 5, 4, 5, 'Bilateral Osteoarthritis Knee (Right > Left)', 'Avoid deep squatting, use knee support brace while walking.', DATE('now', '-2 day'), DATE('now', '+45 day'));

    INSERT OR IGNORE INTO prescription_medicines (item_id, prescription_id, medicine_name, dosage, frequency, duration, instructions) VALUES
    (1, 1, 'Glycomet GP2 (Metformin + Glimepiride)', '1 Tablet', 'Twice daily before meals', '30 Days', 'Do not skip meals'),
    (1, 1, 'Becosules Z Capsules', '1 Capsule', 'Once daily post lunch', '30 Days', 'Take with water'),
    (2, 2, 'Dolo 650mg', '1 Tablet', 'SOS for knee pain', '5 Days', 'Max 3 tablets daily');

    INSERT OR IGNORE INTO medical_history (history_id, patient_id, recorded_date, condition_name, description, treating_physician, is_chronic) VALUES
    (1, 1, '2021-04-10', 'Type 2 Diabetes Mellitus', 'Diagnosed during routine annual checkup; managed with oral hypoglycemics.', 'Dr. Rajesh Sharma', 1),
    (2, 3, '2019-11-15', 'Essential Hypertension', 'Occasional systolic elevation (140-145 mmHg). Lifestyle modification advised.', 'Dr. Vikram Malhotra', 1);

    INSERT OR IGNORE INTO bills (bill_id, bill_number, patient_id, appointment_id, bill_date, consultation_charges, lab_charges, pharmacy_charges, other_charges, subtotal, tax_rate, tax_amount, total_amount, paid_amount, balance_amount, payment_status, notes) VALUES
    (1, 'MED-INV-2026-001', 1, 1, DATE('now'), 600.00, 750.00, 380.00, 50.00, 1780.00, 5.00, 89.00, 1869.00, 1869.00, 0.00, 'Paid', 'Consultation, HbA1c tests, and pharmacy dispensation.'),
    (2, 'MED-INV-2026-002', 3, 3, DATE('now'), 1000.00, 1800.00, 0.00, 100.00, 2900.00, 5.00, 145.00, 3045.00, 1500.00, 1545.00, 'Partially Paid', 'Cardiology initial consultation & 2D Echo charges. ₹1,500 advance settled via UPI.'),
    (3, 'MED-INV-2026-003', 5, 5, DATE('now', '-2 day'), 750.00, 900.00, 220.00, 0.00, 1870.00, 5.00, 93.50, 1963.50, 0.00, 1963.50, 'Pending', 'Orthopedic consultation and Bilateral Knee X-Ray imaging charges.');

    INSERT OR IGNORE INTO payments (payment_id, bill_id, patient_id, amount_paid, payment_method, transaction_ref, notes) VALUES
    (1, 1, 1, 1869.00, 'UPI', 'UPI/2026/ICICI/994102914', 'Settled via Google Pay UPI at billing counter'),
    (2, 2, 3, 1500.00, 'UPI', 'UPI/2026/HDFC/883109411', 'Advance deposit collected via PhonePe UPI');
    ''')
    conn.commit()

class MedaxisHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # 1. API: Dashboard Statistics
        if path == '/api/dashboard/stats':
            pat_count = query_db("SELECT COUNT(*) as c FROM patients", one=True)['c']
            doc_count = query_db("SELECT COUNT(*) as c FROM doctors WHERE status = 'active'", one=True)['c']
            today_apt = query_db("SELECT COUNT(*) as c FROM appointments WHERE appointment_date = DATE('now')", one=True)['c']
            pending_apt = query_db("SELECT COUNT(*) as c FROM appointments WHERE status = 'Booked'", one=True)['c']
            med_stock = query_db("SELECT SUM(available_quantity) as c FROM medicines WHERE stock_status != 'Expired'", one=True)['c'] or 0
            pending_pay = query_db("SELECT SUM(balance_amount) as c FROM bills WHERE payment_status != 'Paid'", one=True)['c'] or 0.0

            return self.send_json({
                'status': 'success',
                'data': {
                    'total_patients': pat_count,
                    'total_doctors': doc_count,
                    'today_appointments': today_apt,
                    'pending_appointments': pending_apt,
                    'pharmacy_stock': med_stock,
                    'pending_payments': float(pending_pay)
                }
            })

        # 2. API: Dashboard Alerts
        if path == '/api/dashboard/alerts':
            low_stock = query_db("SELECT * FROM medicines WHERE available_quantity <= min_stock_level AND stock_status != 'Expired'")
            expiring = query_db("SELECT * FROM medicines WHERE expiry_date <= DATE('now', '+30 day') AND expiry_date >= DATE('now')")
            expired = query_db("SELECT * FROM medicines WHERE expiry_date < DATE('now') OR stock_status = 'Expired'")
            recent_patients = query_db("SELECT * FROM patients ORDER BY patient_id DESC LIMIT 5")
            today_appointments = query_db("""
                SELECT a.*, p.full_name as patient_name, p.patient_code, d.full_name as doctor_name, d.room_no, dept.dept_name
                FROM appointments a
                JOIN patients p ON a.patient_id = p.patient_id
                JOIN doctors d ON a.doctor_id = d.doctor_id
                JOIN departments dept ON a.dept_id = dept.dept_id
                WHERE a.appointment_date = DATE('now')
                ORDER BY a.appointment_time ASC
            """)
            recent_bills = query_db("""
                SELECT b.*, p.full_name as patient_name, p.patient_code
                FROM bills b
                JOIN patients p ON b.patient_id = p.patient_id
                ORDER BY b.bill_id DESC LIMIT 5
            """)

            return self.send_json({
                'status': 'success',
                'data': {
                    'low_stock': low_stock,
                    'expiring_medicines': expiring,
                    'expired_medicines': expired,
                    'recent_patients': recent_patients,
                    'today_appointments': today_appointments,
                    'recent_bills': recent_bills
                }
            })

        # 3. API: Patients
        if path == '/api/patients':
            search = query.get('search', [''])[0].strip()
            gender = query.get('gender', [''])[0].strip()
            sql = "SELECT * FROM patients WHERE 1=1"
            params = []
            if search:
                sql += " AND (full_name LIKE %s OR patient_code LIKE %s OR mobile_number LIKE %s)"
                params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
            if gender:
                sql += " AND gender = %s"
                params.append(gender)
            sql += " ORDER BY patient_id DESC"
            patients = query_db(sql, tuple(params))
            return self.send_json({'status': 'success', 'data': patients})

        # 4. API: Patient 360 Dossier
        if path.startswith('/api/patients/'):
            pat_id = path.split('/')[-1]
            patient = query_db("SELECT * FROM patients WHERE patient_id = %s", (pat_id,), one=True)
            if not patient:
                return self.send_json({'status': 'error', 'message': 'Patient not found'}, 404)
            
            apts = query_db("""
                SELECT a.*, d.full_name as doctor_name, d.specialization, dept.dept_name
                FROM appointments a
                JOIN doctors d ON a.doctor_id = d.doctor_id
                JOIN departments dept ON a.dept_id = dept.dept_id
                WHERE a.patient_id = %s ORDER BY a.appointment_date DESC
            """, (pat_id,))

            labs = query_db("SELECT * FROM lab_reports WHERE patient_id = %s ORDER BY test_date DESC", (pat_id,))
            
            prescs = query_db("""
                SELECT p.*, d.full_name as doctor_name
                FROM prescriptions p
                JOIN doctors d ON p.doctor_id = d.doctor_id
                WHERE p.patient_id = %s ORDER BY p.prescription_date DESC
            """, (pat_id,))
            for p in prescs:
                p['medicines'] = query_db("SELECT * FROM prescription_medicines WHERE prescription_id = %s", (p['prescription_id'],))

            history = query_db("SELECT * FROM medical_history WHERE patient_id = %s ORDER BY recorded_date DESC", (pat_id,))
            bills = query_db("SELECT * FROM bills WHERE patient_id = %s ORDER BY bill_date DESC", (pat_id,))

            return self.send_json({
                'status': 'success',
                'data': {
                    'patient': patient,
                    'appointments': apts,
                    'lab_reports': labs,
                    'prescriptions': prescs,
                    'medical_history': history,
                    'bills': bills
                }
            })

        # 5. API: Doctors & Departments
        if path == '/api/doctors':
            dept_id = query.get('dept_id', [''])[0].strip()
            sql = "SELECT d.*, dept.dept_name FROM doctors d JOIN departments dept ON d.dept_id = dept.dept_id WHERE 1=1"
            params = []
            if dept_id:
                sql += " AND d.dept_id = %s"
                params.append(dept_id)
            sql += " ORDER BY d.full_name ASC"
            doctors = query_db(sql, tuple(params))
            departments = query_db("SELECT * FROM departments ORDER BY dept_name ASC")
            return self.send_json({'status': 'success', 'data': {'doctors': doctors, 'departments': departments}})

        # 6. API: Appointments
        if path == '/api/appointments':
            status = query.get('status', [''])[0].strip()
            sql = """
                SELECT a.*, p.full_name as patient_name, p.patient_code, p.mobile_number as patient_mobile,
                       d.full_name as doctor_name, d.specialization, d.room_no, dept.dept_name
                FROM appointments a
                JOIN patients p ON a.patient_id = p.patient_id
                JOIN doctors d ON a.doctor_id = d.doctor_id
                JOIN departments dept ON a.dept_id = dept.dept_id
                WHERE 1=1
            """
            params = []
            if status:
                sql += " AND a.status = %s"
                params.append(status)
            sql += " ORDER BY a.appointment_date DESC, a.appointment_time ASC"
            apts = query_db(sql, tuple(params))
            return self.send_json({'status': 'success', 'data': apts})

        # 7. API: Pharmacy
        if path == '/api/pharmacy':
            category = query.get('category', [''])[0].strip()
            status = query.get('status', [''])[0].strip()
            sql = "SELECT * FROM medicines WHERE 1=1"
            params = []
            if category:
                sql += " AND category = %s"
                params.append(category)
            if status == 'low_stock':
                sql += " AND available_quantity <= min_stock_level AND stock_status != 'Expired'"
            elif status == 'expired':
                sql += " AND (expiry_date < DATE('now') OR stock_status = 'Expired')"
            elif status == 'in_stock':
                sql += " AND available_quantity > min_stock_level AND expiry_date >= DATE('now')"
            sql += " ORDER BY medicine_name ASC"
            meds = query_db(sql, tuple(params))
            return self.send_json({'status': 'success', 'data': meds})

        # 8. API: Billing
        if path == '/api/billing':
            sql = """
                SELECT b.*, p.full_name as patient_name, p.patient_code, p.mobile_number as patient_mobile
                FROM bills b
                JOIN patients p ON b.patient_id = p.patient_id
                ORDER BY b.bill_id DESC
            """
            bills = query_db(sql)
            return self.send_json({'status': 'success', 'data': bills})

        # Static file fallback
        if path == '/' or path == '/index.html':
            self.path = '/frontend/index.html'
        else:
            self.path = '/frontend' + path

        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get('Content-Length', 0))
        raw_body = self.rfile.read(length).decode('utf-8') if length > 0 else '{}'
        try:
            body = json.loads(raw_body)
        except Exception:
            body = urllib.parse.parse_qs(raw_body)

        # 1. API: Login
        if path == '/api/auth/login':
            user = body.get('username', '')
            pwd = body.get('password', '')
            if user == 'admin' and (pwd == 'admin123' or pwd == 'admin'):
                return self.send_json({'status': 'success', 'message': 'Authentication successful', 'data': {'user': 'Administrator'}})
            return self.send_json({'status': 'error', 'message': 'Invalid credentials. Use admin / admin123'}, 401)

        # 2. API: Register Patient
        if path == '/api/patients':
            name = body.get('full_name', '').strip()
            dob = body.get('dob', '')
            age = int(body.get('age', 0))
            gender = body.get('gender', 'Male')
            bg = body.get('blood_group', 'O+')
            mobile = body.get('mobile_number', '').strip()
            email = body.get('email', '').strip()
            address = body.get('address', '').strip()
            city = body.get('city', '').strip()
            state = body.get('state', '').strip()
            pincode = body.get('pincode', '').strip()

            if not name or not dob or not mobile or not pincode:
                return self.send_json({'status': 'error', 'message': 'Required fields missing'}, 400)

            # Check duplicate mobile
            existing = query_db("SELECT patient_id FROM patients WHERE mobile_number = %s", (mobile,), one=True)
            if existing:
                return self.send_json({'status': 'error', 'message': 'A patient with this mobile number is already registered'}, 409)

            # Generate Patient Code
            count = query_db("SELECT COUNT(*) as c FROM patients", one=True)['c'] + 1
            code = f"MED-PAT-2026-{count:04d}"

            pat_id = execute_db("""
                INSERT INTO patients (patient_code, full_name, dob, age, gender, blood_group, mobile_number, email, address, city, state, pincode)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (code, name, dob, age, gender, bg, mobile, email, address, city, state, pincode), return_id=True)

            return self.send_json({'status': 'success', 'message': f'Patient registered successfully! Patient ID: {code}', 'data': {'patient_id': pat_id, 'patient_code': code}})

        # 3. API: Book Appointment
        if path == '/api/appointments':
            pat_id = body.get('patient_id')
            doc_id = body.get('doctor_id')
            dept_id = body.get('dept_id')
            apt_date = body.get('appointment_date')
            apt_time = body.get('appointment_time')
            notes = body.get('notes', '').strip()

            if not pat_id or not doc_id or not apt_date or not apt_time:
                return self.send_json({'status': 'error', 'message': 'Please fill all appointment parameters'}, 400)

            # Double booking collision check
            collision = query_db("""
                SELECT appointment_id FROM appointments 
                WHERE doctor_id = %s AND appointment_date = %s AND appointment_time = %s AND status = 'Booked'
            """, (doc_id, apt_date, apt_time), one=True)

            if collision:
                return self.send_json({'status': 'error', 'message': 'This doctor is already booked for the selected time slot. Please choose another time.'}, 409)

            doc = query_db("SELECT consultation_fees, dept_id FROM doctors WHERE doctor_id = %s", (doc_id,), one=True)
            fees = doc['consultation_fees'] if doc else 500.00
            if not dept_id and doc:
                dept_id = doc['dept_id']

            count = query_db("SELECT COUNT(*) as c FROM appointments", one=True)['c'] + 1
            code = f"MED-APT-2026-{count:04d}"

            apt_id = execute_db("""
                INSERT INTO appointments (appointment_code, patient_id, doctor_id, dept_id, appointment_date, appointment_time, consultation_fees, status, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'Booked', %s)
            """, (code, pat_id, doc_id, dept_id, apt_date, apt_time, fees, notes), return_id=True)

            return self.send_json({'status': 'success', 'message': f'Appointment #{code} confirmed successfully!', 'data': {'appointment_code': code}})

        # 4. API: Reschedule Appointment
        if path.startswith('/api/appointments/') and path.endswith('/reschedule'):
            apt_id = path.split('/')[-2]
            new_date = body.get('appointment_date')
            new_time = body.get('appointment_time')

            apt = query_db("SELECT doctor_id FROM appointments WHERE appointment_id = %s", (apt_id,), one=True)
            if not apt:
                return self.send_json({'status': 'error', 'message': 'Appointment not found'}, 404)

            # Collision check
            collision = query_db("""
                SELECT appointment_id FROM appointments 
                WHERE doctor_id = %s AND appointment_date = %s AND appointment_time = %s AND status = 'Booked' AND appointment_id != %s
            """, (apt['doctor_id'], new_date, new_time, apt_id), one=True)

            if collision:
                return self.send_json({'status': 'error', 'message': 'Slot conflict! Another patient is booked at this time.'}, 409)

            execute_db("UPDATE appointments SET appointment_date = %s, appointment_time = %s, status = 'Rescheduled' WHERE appointment_id = %s",
                       (new_date, new_time, apt_id))
            return self.send_json({'status': 'success', 'message': 'Appointment rescheduled successfully!'})

        # 5. API: Cancel Appointment
        if path.startswith('/api/appointments/') and path.endswith('/cancel'):
            apt_id = path.split('/')[-2]
            execute_db("UPDATE appointments SET status = 'Cancelled' WHERE appointment_id = %s", (apt_id,))
            return self.send_json({'status': 'success', 'message': 'Appointment marked as Cancelled.'})

        # 6. API: Add Medicine to Pharmacy
        if path == '/api/pharmacy':
            name = body.get('medicine_name', '').strip()
            category = body.get('category', 'Other')
            mfg = body.get('manufacturer', '').strip()
            batch = body.get('batch_number', '').strip()
            qty = int(body.get('available_quantity', 0))
            min_stock = int(body.get('min_stock_level', 20))
            price = float(body.get('unit_price', 0.0))
            mfg_date = body.get('mfg_date', '')
            exp_date = body.get('expiry_date', '')

            status = 'In Stock'
            if qty <= 0:
                status = 'Out of Stock'
            elif qty <= min_stock:
                status = 'Low Stock'

            count = query_db("SELECT COUNT(*) as c FROM medicines", one=True)['c'] + 1
            code = f"MED-RX-{count:03d}"

            med_id = execute_db("""
                INSERT INTO medicines (medicine_code, medicine_name, category, manufacturer, batch_number, available_quantity, min_stock_level, unit_price, mfg_date, expiry_date, stock_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (code, name, category, mfg, batch, qty, min_stock, price, mfg_date, exp_date, status), return_id=True)

            return self.send_json({'status': 'success', 'message': f'Medicine {name} added to pharmacy inventory!', 'data': {'medicine_code': code}})

        # 7. API: Generate Bill
        if path == '/api/billing':
            pat_id = body.get('patient_id')
            c_fees = float(body.get('consultation_charges', 0.0))
            l_fees = float(body.get('lab_charges', 0.0))
            p_fees = float(body.get('pharmacy_charges', 0.0))
            o_fees = float(body.get('other_charges', 0.0))
            tax_rate = float(body.get('tax_rate', 5.0))
            paid = float(body.get('paid_amount', 0.0))
            method = body.get('payment_method', 'Cash')

            subtotal = c_fees + l_fees + p_fees + o_fees
            tax_amount = round(subtotal * (tax_rate / 100.0), 2)
            total = subtotal + tax_amount
            balance = max(0.0, total - paid)
            status = 'Paid' if balance <= 0.01 else ('Partially Paid' if paid > 0 else 'Pending')

            count = query_db("SELECT COUNT(*) as c FROM bills", one=True)['c'] + 1
            code = f"MED-INV-2026-{count:03d}"
            today = datetime.date.today().isoformat()

            bill_id = execute_db("""
                INSERT INTO bills (bill_number, patient_id, bill_date, consultation_charges, lab_charges, pharmacy_charges, other_charges, subtotal, tax_rate, tax_amount, total_amount, paid_amount, balance_amount, payment_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (code, pat_id, today, c_fees, l_fees, p_fees, o_fees, subtotal, tax_rate, tax_amount, total, paid, balance, status), return_id=True)

            if paid > 0:
                execute_db("INSERT INTO payments (bill_id, patient_id, amount_paid, payment_method) VALUES (%s, %s, %s, %s)",
                           (bill_id, pat_id, paid, method))

            return self.send_json({'status': 'success', 'message': f'Invoice #{code} generated successfully!', 'data': {'bill_number': code, 'bill_id': bill_id}})

        # 8. API: Collect Payment on Bill
        if path.startswith('/api/billing/') and path.endswith('/pay'):
            bill_id = path.split('/')[-2]
            amount = float(body.get('amount_paid', 0.0))
            method = body.get('payment_method', 'Cash')
            ref = body.get('transaction_ref', '')

            bill = query_db("SELECT * FROM bills WHERE bill_id = %s", (bill_id,), one=True)
            if not bill:
                return self.send_json({'status': 'error', 'message': 'Invoice not found'}, 404)

            new_paid = float(bill['paid_amount']) + amount
            new_balance = max(0.0, float(bill['total_amount']) - new_paid)
            new_status = 'Paid' if new_balance <= 0.01 else 'Partially Paid'

            execute_db("UPDATE bills SET paid_amount = %s, balance_amount = %s, payment_status = %s WHERE bill_id = %s",
                       (new_paid, new_balance, new_status, bill_id))

            execute_db("INSERT INTO payments (bill_id, patient_id, amount_paid, payment_method, transaction_ref) VALUES (%s, %s, %s, %s, %s)",
                       (bill_id, bill['patient_id'], amount, method, ref))

            return self.send_json({'status': 'success', 'message': f'Payment of ₹{amount:,.2f} recorded via {method}!'})

        return self.send_json({'status': 'error', 'message': 'Invalid endpoint'}, 404)

if __name__ == '__main__':
    os.chdir(BASE_DIR)
    conn, engine = get_db()
    conn.close()
    print("=" * 70)
    print("  + MEDAXIS – Hospital Management System")
    print("  * Tagline    : Simplifying Hospital Operations. Connecting Better Care.")
    print(f"  * Engine     : {engine.upper()} (Connected)")
    print(f"  * Server URL : http://localhost:{PORT}")
    print("  * Demo Admin : admin / admin123")
    print("=" * 70)
    httpd = HTTPServer(('0.0.0.0', PORT), MedaxisHandler)
    httpd.serve_forever()

