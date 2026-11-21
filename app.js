/**
 * ========================================================
 * MEDAXIS – Hospital Management System
 * Client-side Controller & Dynamic REST API Client
 * ========================================================
 */

const API_BASE = '/api';

// Indian States & Union Territories
const INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
    "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
    "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
    "Andaman and Nicobar Islands", "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu",
    "Delhi (NCT)", "Jammu and Kashmir", "Ladakh", "Lakshadweep", "Puducherry"
];

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initIndianStatesDropdown();
    initPatientFormCalculations();
    loadDashboard();
});

// 1. Navigation Controller
function initNavigation() {
    const navLinks = document.querySelectorAll('.menu-link[data-view]');
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetViewId = link.getAttribute('data-view');
            switchView(targetViewId);
        });
    });
}

function switchView(viewId) {
    document.querySelectorAll('.menu-link').forEach(l => l.classList.remove('active'));
    document.querySelectorAll('.module-view').forEach(v => v.classList.remove('active'));

    const activeLink = document.querySelector(`.menu-link[data-view="${viewId}"]`);
    const activeView = document.getElementById(viewId);

    if (activeLink) activeLink.classList.add('active');
    if (activeView) activeView.classList.add('active');

    // Trigger on-demand loaders
    if (viewId === 'view-dashboard') loadDashboard();
    if (viewId === 'view-patient-details') loadPatients();
    if (viewId === 'view-doctor-management') loadDoctors();
    if (viewId === 'view-appointments') loadAppointments();
    if (viewId === 'view-pharmacy') loadPharmacy();
    if (viewId === 'view-billing') loadBilling();
}

// 2. Dashboard Loader
function loadDashboard() {
    // A. 6 Stat Cards
    fetch(`${API_BASE}/dashboard/stats`)
        .then(res => res.json())
        .then(res => {
            if (res.status === 'success') {
                const d = res.data;
                document.getElementById('statTotalPatients').textContent = d.total_patients;
                document.getElementById('statTotalDoctors').textContent = d.total_doctors;
                document.getElementById('statTodayApts').textContent = d.today_appointments;
                document.getElementById('statPendingApts').textContent = d.pending_appointments;
                document.getElementById('statPharmacyStock').textContent = d.pharmacy_stock.toLocaleString('en-IN') + ' units';
                document.getElementById('statPendingPayments').textContent = '₹' + d.pending_payments.toLocaleString('en-IN', {minimumFractionDigits: 2});
            }
        })
        .catch(err => console.error('Dashboard stats fetch error:', err));

    // B. Alerts & Activity Feeds
    fetch(`${API_BASE}/dashboard/alerts`)
        .then(res => res.json())
        .then(res => {
            if (res.status === 'success') {
                const d = res.data;
                
                // Low Stock Alerts
                const lowStockList = document.getElementById('dashLowStockList');
                if (d.low_stock.length === 0) {
                    lowStockList.innerHTML = '<div style="color:#059669; font-weight:600;">✓ All medicine inventory at optimal levels</div>';
                } else {
                    lowStockList.innerHTML = d.low_stock.map(m => `
                        <div>• <strong>${m.medicine_name}</strong>: ${m.available_quantity} left (Min: ${m.min_stock_level}) - <span class="badge badge-warning">Low Stock</span></div>
                    `).join('');
                }

                // Expiring Medicines
                const expiringList = document.getElementById('dashExpiringList');
                if (d.expiring_medicines.length === 0 && d.expired_medicines.length === 0) {
                    expiringList.innerHTML = '<div style="color:#059669; font-weight:600;">✓ No medicines nearing expiry in 30 days</div>';
                } else {
                    let html = d.expiring_medicines.map(m => `
                        <div>• <strong>${m.medicine_name}</strong> expires on ${m.expiry_date} - <span class="badge badge-danger">Expiring Soon</span></div>
                    `).join('');
                    html += d.expired_medicines.map(m => `
                        <div>• <strong>${m.medicine_name}</strong> (Batch: ${m.batch_number}) - <span class="badge badge-danger" style="background:#000; color:#FFF;">EXPIRED (LOCKED)</span></div>
                    `).join('');
                    expiringList.innerHTML = html;
                }

                // Today's Appointments Table
                const aptTbody = document.getElementById('dashTodayAptTbody');
                if (d.today_appointments.length === 0) {
                    aptTbody.innerHTML = '<tr><td colspan="5" style="text-align:center; padding:16px; color:#94A3B8;">No appointments scheduled for today.</td></tr>';
                } else {
                    aptTbody.innerHTML = d.today_appointments.map(a => `
                        <tr>
                            <td><strong>${a.appointment_time}</strong></td>
                            <td><strong>${a.patient_name}</strong><br><small style="color:#64748B;">${a.patient_code}</small></td>
                            <td>${a.doctor_name}</td>
                            <td>${a.room_no || 'Room 101'}</td>
                            <td><span class="badge ${a.status === 'Booked' ? 'badge-info' : 'badge-success'}">${a.status}</span></td>
                        </tr>
                    `).join('');
                }

                // Recent Patient Registrations
                const patTbody = document.getElementById('dashRecentPatTbody');
                if (d.recent_patients.length === 0) {
                    patTbody.innerHTML = '<tr><td colspan="4" style="text-align:center; padding:16px; color:#94A3B8;">No patients registered yet.</td></tr>';
                } else {
                    patTbody.innerHTML = d.recent_patients.map(p => `
                        <tr>
                            <td><strong>${p.patient_code}</strong></td>
                            <td><a href="#" onclick="openPatientDossier(${p.patient_id}); return false;" style="font-weight:600; color:#0D9488;">${p.full_name}</a></td>
                            <td>${p.gender}, ${p.age}y</td>
                            <td>+91 ${p.mobile_number}</td>
                        </tr>
                    `).join('');
                }
            }
        })
        .catch(err => console.error('Dashboard alerts fetch error:', err));
}

// 3. Indian States Dropdown Population
function initIndianStatesDropdown() {
    const stateSelect = document.getElementById('patStateSelect');
    if (stateSelect) {
        stateSelect.innerHTML = '<option value="">-- Select State / Union Territory --</option>' +
            INDIAN_STATES.map(s => `<option value="${s}">${s}</option>`).join('');
    }
}

// 4. Register Patient Form Logic (Auto Age & Indian Validations)
function initPatientFormCalculations() {
    const dobInput = document.getElementById('patDob');
    const ageInput = document.getElementById('patAge');
    const patForm = document.getElementById('patientRegisterForm');

    if (dobInput && ageInput) {
        dobInput.addEventListener('change', () => {
            const dob = new Date(dobInput.value);
            if (!isNaN(dob.getTime())) {
                const today = new Date();
                let age = today.getFullYear() - dob.getFullYear();
                const m = today.getMonth() - dob.getMonth();
                if (m < 0 || (m === 0 && today.getDate() < dob.getDate())) {
                    age--;
                }
                ageInput.value = Math.max(0, age);
            }
        });
    }

    if (patForm) {
        patForm.addEventListener('submit', (e) => {
            e.preventDefault();

            const mobile = document.getElementById('patMobile').value.trim();
            const pincode = document.getElementById('patPincode').value.trim();
            const alertBox = document.getElementById('patientFormAlert');

            // Indian Mobile Validation (10 digits starting with 6-9)
            const mobileRegex = /^[6-9]\d{9}$/;
            if (!mobileRegex.test(mobile)) {
                alertBox.className = 'alert alert-danger';
                alertBox.textContent = 'Invalid Mobile Number: Must be a valid 10-digit Indian mobile starting with 6, 7, 8, or 9.';
                alertBox.style.display = 'block';
                return;
            }

            // Indian PIN Code Validation (6 digits)
            const pinRegex = /^[1-9][0-9]{5}$/;
            if (!pinRegex.test(pincode)) {
                alertBox.className = 'alert alert-danger';
                alertBox.textContent = 'Invalid PIN Code: Must be a valid 6-digit Indian postal PIN code.';
                alertBox.style.display = 'block';
                return;
            }

            const payload = {
                full_name: document.getElementById('patName').value.trim(),
                dob: document.getElementById('patDob').value,
                age: parseInt(document.getElementById('patAge').value),
                gender: document.getElementById('patGender').value,
                blood_group: document.getElementById('patBloodGroup').value,
                mobile_number: mobile,
                email: document.getElementById('patEmail').value.trim(),
                address: document.getElementById('patAddress').value.trim(),
                city: document.getElementById('patCity').value.trim(),
                state: document.getElementById('patStateSelect').value,
                pincode: pincode
            };

            fetch(`${API_BASE}/patients`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            })
            .then(res => res.json())
            .then(res => {
                if (res.status === 'success') {
                    alertBox.className = 'alert alert-success';
                    alertBox.innerHTML = `<strong>Registration Successful!</strong> ${res.message} (Assigned ID: <strong>${res.data.patient_code}</strong>)`;
                    alertBox.style.display = 'block';
                    patForm.reset();
                    // Reload patients list in background
                    loadPatients();
                } else {
                    alertBox.className = 'alert alert-danger';
                    alertBox.textContent = res.message || 'Error registering patient.';
                    alertBox.style.display = 'block';
                }
            })
            .catch(err => {
                alertBox.className = 'alert alert-danger';
                alertBox.textContent = 'Network error: ' + err;
                alertBox.style.display = 'block';
            });
        });
    }
}

// 5. Patient Directory & 6-Tab Dossier
function loadPatients() {
    const search = document.getElementById('patientSearchInput') ? document.getElementById('patientSearchInput').value : '';
    const gender = document.getElementById('patientGenderFilter') ? document.getElementById('patientGenderFilter').value : '';

    let url = `${API_BASE}/patients?`;
    if (search) url += `search=${encodeURIComponent(search)}&`;
    if (gender) url += `gender=${encodeURIComponent(gender)}&`;

    fetch(url)
        .then(res => res.json())
        .then(res => {
            if (res.status === 'success') {
                const tbody = document.getElementById('patientDirectoryTbody');
                if (res.data.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; padding:24px; color:#94A3B8;">No patients found matching criteria.</td></tr>';
                    return;
                }
                tbody.innerHTML = res.data.map(p => `
                    <tr>
                        <td><strong>${p.patient_code}</strong></td>
                        <td><strong>${p.full_name}</strong></td>
                        <td>${p.age} yrs</td>
                        <td>${p.gender}</td>
                        <td><span class="badge badge-secondary" style="font-weight:700;">${p.blood_group}</span></td>
                        <td>+91 ${p.mobile_number}</td>
                        <td>${p.registered_at.split(' ')[0]}</td>
                        <td>
                            <button class="btn btn-outline btn-sm" onclick="openPatientDossier(${p.patient_id})">
                                View 360° Profile
                            </button>
                        </td>
                    </tr>
                `).join('');
            }
        });
}

function openPatientDossier(patientId) {
    fetch(`${API_BASE}/patients/${patientId}`)
        .then(res => res.json())
        .then(res => {
            if (res.status === 'success') {
                const d = res.data;
                const p = d.patient;

                // Fill Header
                document.getElementById('dossierPatName').textContent = p.full_name;
                document.getElementById('dossierPatCode').textContent = p.patient_code;
                document.getElementById('dossierPatMeta').textContent = `${p.gender} • ${p.age} Years • Blood Group ${p.blood_group} • Mobile: +91 ${p.mobile_number}`;

                // 1. Personal Information Tab
                document.getElementById('tabPersonalContent').innerHTML = `
                    <div class="form-grid-3" style="font-size:0.9rem;">
                        <div><label class="stat-label">Full Name</label><div><strong>${p.full_name}</strong></div></div>
                        <div><label class="stat-label">Patient Identifier</label><div><strong>${p.patient_code}</strong></div></div>
                        <div><label class="stat-label">Date of Birth / Age</label><div>${p.dob} (${p.age} years)</div></div>
                        <div><label class="stat-label">Gender</label><div>${p.gender}</div></div>
                        <div><label class="stat-label">Blood Group</label><div><span class="badge badge-secondary" style="font-weight:700;">${p.blood_group}</span></div></div>
                        <div><label class="stat-label">Mobile Contact</label><div>+91 ${p.mobile_number}</div></div>
                        <div><label class="stat-label">Email Address</label><div>${p.email || 'Not provided'}</div></div>
                        <div><label class="stat-label">City & State</label><div>${p.city}, ${p.state}</div></div>
                        <div><label class="stat-label">PIN Code</label><div>${p.pincode}</div></div>
                    </div>
                    <div style="margin-top:16px;">
                        <label class="stat-label">Complete Residential Address</label>
                        <div style="font-size:0.9rem; color:#334155;">${p.address}</div>
                    </div>
                `;

                // 2. Appointments Tab
                document.getElementById('tabAppointmentsContent').innerHTML = d.appointments.length === 0 ? 
                    '<p style="color:#94A3B8;">No appointments found for this patient.</p>' :
                    `<table class="table"><thead><tr><th>Date & Time</th><th>Doctor</th><th>Department</th><th>Fees</th><th>Status</th></tr></thead><tbody>` +
                    d.appointments.map(a => `
                        <tr>
                            <td><strong>${a.appointment_date}</strong> (${a.appointment_time})</td>
                            <td>${a.doctor_name}</td>
                            <td>${a.dept_name}</td>
                            <td>₹${parseFloat(a.consultation_fees).toFixed(2)}</td>
                            <td><span class="badge ${a.status === 'Completed' ? 'badge-success' : (a.status === 'Cancelled' ? 'badge-danger' : 'badge-info')}">${a.status}</span></td>
                        </tr>
                    `).join('') + `</tbody></table>`;

                // 3. Lab Reports Tab
                document.getElementById('tabLabContent').innerHTML = d.lab_reports.length === 0 ?
                    '<p style="color:#94A3B8;">No diagnostic laboratory reports registered.</p>' :
                    `<table class="table"><thead><tr><th>Test Code</th><th>Test Name</th><th>Date</th><th>Findings / Results</th><th>Status</th></tr></thead><tbody>` +
                    d.lab_reports.map(l => `
                        <tr>
                            <td><strong>${l.report_code}</strong></td>
                            <td><strong>${l.test_name}</strong></td>
                            <td>${l.test_date}</td>
                            <td>${l.result_summary}</td>
                            <td><span class="badge ${l.report_status === 'Completed' ? 'badge-success' : 'badge-warning'}">${l.report_status}</span></td>
                        </tr>
                    `).join('') + `</tbody></table>`;

                // 4. Prescriptions Tab
                document.getElementById('tabPrescriptionContent').innerHTML = d.prescriptions.length === 0 ?
                    '<p style="color:#94A3B8;">No prescription records available.</p>' :
                    d.prescriptions.map(rx => `
                        <div style="border:1px solid #E2E8F0; border-radius:8px; padding:16px; margin-bottom:14px; background:#FAFCFE;">
                            <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                                <strong>${rx.prescription_code} — Dr. ${rx.doctor_name}</strong>
                                <span style="font-size:0.8rem; color:#64748B;">Date: ${rx.prescription_date}</span>
                            </div>
                            <div style="font-size:0.85rem; color:#0F766E; font-weight:700; margin-bottom:6px;">Diagnosis: ${rx.diagnosis}</div>
                            <table class="table" style="font-size:0.82rem;">
                                <thead><tr><th>Medicine Name</th><th>Dosage</th><th>Frequency</th><th>Duration</th></tr></thead>
                                <tbody>${rx.medicines.map(m => `<tr><td><strong>${m.medicine_name}</strong></td><td>${m.dosage}</td><td>${m.frequency}</td><td>${m.duration}</td></tr>`).join('')}</tbody>
                            </table>
                        </div>
                    `).join('');

                // 5. Medical History Tab
                document.getElementById('tabHistoryContent').innerHTML = d.medical_history.length === 0 ?
                    '<p style="color:#94A3B8;">No prior chronic illness or medical history logged.</p>' :
                    d.medical_history.map(h => `
                        <div style="border-left:3px solid #0D9488; padding:8px 12px; margin-bottom:8px; background:#F8FAFC;">
                            <strong>${h.condition_name}</strong> (Recorded on ${h.recorded_date})<br>
                            <span style="font-size:0.85rem; color:#475569;">${h.description}</span>
                        </div>
                    `).join('');

                // 6. Billing History Tab
                document.getElementById('tabBillingContent').innerHTML = d.bills.length === 0 ?
                    '<p style="color:#94A3B8;">No invoices generated for this patient.</p>' :
                    `<table class="table"><thead><tr><th>Invoice #</th><th>Date</th><th>Total Amount</th><th>Paid Amount</th><th>Balance Due</th><th>Status</th></tr></thead><tbody>` +
                    d.bills.map(b => `
                        <tr>
                            <td><strong>${b.bill_number}</strong></td>
                            <td>${b.bill_date}</td>
                            <td>₹${parseFloat(b.total_amount).toFixed(2)}</td>
                            <td style="color:#059669; font-weight:700;">₹${parseFloat(b.paid_amount).toFixed(2)}</td>
                            <td style="color:#DC2626; font-weight:700;">₹${parseFloat(b.balance_amount).toFixed(2)}</td>
                            <td><span class="badge ${b.payment_status === 'Paid' ? 'badge-success' : 'badge-warning'}">${b.payment_status}</span></td>
                        </tr>
                    `).join('') + `</tbody></table>`;

                // Open Modal or Switch to dossier container
                document.getElementById('patientDossierModal').classList.add('active');
            }
        });
}

// 6. Doctor Management Loader
function loadDoctors() {
    const deptId = document.getElementById('docDeptFilter') ? document.getElementById('docDeptFilter').value : '';
    let url = `${API_BASE}/doctors`;
    if (deptId) url += `?dept_id=${deptId}`;

    fetch(url)
        .then(res => res.json())
        .then(res => {
            if (res.status === 'success') {
                const docs = res.data.doctors;
                const depts = res.data.departments;

                // Populate filter if empty
                const filterSelect = document.getElementById('docDeptFilter');
                if (filterSelect && filterSelect.options.length <= 1) {
                    depts.forEach(d => {
                        const opt = document.createElement('option');
                        opt.value = d.dept_id;
                        opt.textContent = d.dept_name;
                        filterSelect.appendChild(opt);
                    });
                }

                // Render Doctor Cards
                const grid = document.getElementById('doctorsRosterGrid');
                grid.innerHTML = docs.map(doc => `
                    <div class="card" style="margin-bottom:0;">
                        <div class="card-body">
                            <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:12px;">
                                <div>
                                    <h3 style="font-size:1.05rem; font-weight:700;">${doc.full_name}</h3>
                                    <div style="font-size:0.8rem; color:#0D9488; font-weight:600;">${doc.specialization}</div>
                                </div>
                                <span class="badge badge-success">Active</span>
                            </div>
                            <div style="font-size:0.82rem; color:#475569; display:flex; flex-direction:column; gap:5px; border-top:1px solid #E2E8F0; padding-top:10px;">
                                <div><strong>Dept:</strong> ${doc.dept_name}</div>
                                <div><strong>Qualification:</strong> ${doc.qualification} (${doc.experience_years} yrs exp)</div>
                                <div><strong>Cabin / Room:</strong> ${doc.room_no || 'Room 101'}</div>
                                <div><strong>Consultation Fees:</strong> <span style="font-size:0.95rem; font-weight:800; color:#0B192C;">₹${parseFloat(doc.consultation_fees).toFixed(2)}</span></div>
                                <div><strong>Schedule:</strong> ${doc.working_days || 'Mon, Wed, Fri'}</div>
                                <div><strong>Contact:</strong> +91 ${doc.mobile_number}</div>
                            </div>
                        </div>
                    </div>
                `).join('');
            }
        });
}

// 7. Appointment Booking & Collision Check
function loadAppointments() {
    const status = document.getElementById('aptStatusFilter') ? document.getElementById('aptStatusFilter').value : '';
    let url = `${API_BASE}/appointments`;
    if (status) url += `?status=${encodeURIComponent(status)}`;

    fetch(url)
        .then(res => res.json())
        .then(res => {
            if (res.status === 'success') {
                const tbody = document.getElementById('appointmentRegistryTbody');
                tbody.innerHTML = res.data.map(a => `
                    <tr>
                        <td><strong>${a.appointment_code}</strong></td>
                        <td><strong>${a.appointment_date}</strong><br><small style="color:#64748B;">${a.appointment_time}</small></td>
                        <td><strong>${a.patient_name}</strong><br><small style="color:#64748B;">${a.patient_code}</small></td>
                        <td>${a.doctor_name}<br><small style="color:#64748B;">${a.dept_name}</small></td>
                        <td>₹${parseFloat(a.consultation_fees).toFixed(2)}</td>
                        <td><span class="badge ${a.status === 'Completed' ? 'badge-success' : (a.status === 'Cancelled' ? 'badge-danger' : 'badge-info')}">${a.status}</span></td>
                        <td>
                            ${a.status === 'Booked' ? `
                                <button class="btn btn-outline btn-sm" onclick="rescheduleAppointmentPrompt(${a.appointment_id})">Reschedule</button>
                                <button class="btn btn-outline btn-sm" style="color:#DC2626;" onclick="cancelAppointment(${a.appointment_id})">Cancel</button>
                            ` : `<span style="font-size:0.75rem; color:#94A3B8;">No action</span>`}
                        </td>
                    </tr>
                `).join('');
            }
        });

    // Populate patient and doctor dropdowns in booking modal
    populateBookingDropdowns();
}

function populateBookingDropdowns() {
    fetch(`${API_BASE}/patients`)
        .then(r => r.json())
        .then(r => {
            const select = document.getElementById('bookPatientSelect');
            if (select) {
                select.innerHTML = '<option value="">-- Choose Patient --</option>' +
                    r.data.map(p => `<option value="${p.patient_id}">${p.full_name} (${p.patient_code}) - Mobile: ${p.mobile_number}</option>`).join('');
            }
        });

    fetch(`${API_BASE}/doctors`)
        .then(r => r.json())
        .then(r => {
            const select = document.getElementById('bookDoctorSelect');
            if (select) {
                select.innerHTML = '<option value="">-- Choose Doctor --</option>' +
                    r.data.doctors.map(d => `<option value="${d.doctor_id}" data-fees="${d.consultation_fees}">${d.full_name} (${d.specialization}) - ₹${d.consultation_fees}</option>`).join('');
            }
        });
}

function submitBooking() {
    const patId = document.getElementById('bookPatientSelect').value;
    const docId = document.getElementById('bookDoctorSelect').value;
    const date = document.getElementById('bookAptDate').value;
    const time = document.getElementById('bookAptTime').value;
    const notes = document.getElementById('bookAptNotes').value;
    const alertBox = document.getElementById('bookAlert');

    if (!patId || !docId || !date || !time) {
        alertBox.className = 'alert alert-danger';
        alertBox.textContent = 'Please fill all fields.';
        alertBox.style.display = 'block';
        return;
    }

    fetch(`${API_BASE}/appointments`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ patient_id: patId, doctor_id: docId, appointment_date: date, appointment_time: time, notes: notes })
    })
    .then(res => res.json())
    .then(res => {
        if (res.status === 'success') {
            alert(res.message);
            document.getElementById('bookAppointmentModal').classList.remove('active');
            loadAppointments();
        } else {
            alertBox.className = 'alert alert-danger';
            alertBox.textContent = res.message;
            alertBox.style.display = 'block';
        }
    });
}

function cancelAppointment(aptId) {
    if (confirm('Are you sure you want to cancel this appointment?')) {
        fetch(`${API_BASE}/appointments/${aptId}/cancel`, { method: 'PUT' })
            .then(res => res.json())
            .then(res => {
                alert(res.message);
                loadAppointments();
            });
    }
}

// 8. Pharmacy Management
function loadPharmacy() {
    const cat = document.getElementById('pharmCategoryFilter') ? document.getElementById('pharmCategoryFilter').value : '';
    const status = document.getElementById('pharmStatusFilter') ? document.getElementById('pharmStatusFilter').value : '';

    let url = `${API_BASE}/pharmacy?`;
    if (cat) url += `category=${encodeURIComponent(cat)}&`;
    if (status) url += `status=${encodeURIComponent(status)}&`;

    fetch(url)
        .then(res => res.json())
        .then(res => {
            if (res.status === 'success') {
                const tbody = document.getElementById('pharmacyInventoryTbody');
                tbody.innerHTML = res.data.map(m => `
                    <tr style="${m.stock_status === 'Expired' ? 'background:#FEF2F2;' : ''}">
                        <td><strong>${m.medicine_code}</strong></td>
                        <td>
                            <strong>${m.medicine_name}</strong><br>
                            <small style="color:#64748B;">Mfg: ${m.manufacturer} • Batch: ${m.batch_number}</small>
                        </td>
                        <td><span class="badge badge-secondary">${m.category}</span></td>
                        <td>
                            <strong style="color:${m.available_quantity <= m.min_stock_level ? '#DC2626' : '#0B192C'}; font-size:0.95rem;">
                                ${m.available_quantity}
                            </strong> (Min: ${m.min_stock_level})
                        </td>
                        <td><strong>₹${parseFloat(m.unit_price).toFixed(2)}</strong></td>
                        <td>${m.mfg_date}</td>
                        <td><strong>${m.expiry_date}</strong></td>
                        <td>
                            <span class="badge ${m.stock_status === 'In Stock' ? 'badge-success' : (m.stock_status === 'Low Stock' ? 'badge-warning' : 'badge-danger')}">
                                ${m.stock_status}
                            </span>
                        </td>
                    </tr>
                `).join('');
            }
        });
}

// 9. Billing & Payments in INR (₹)
function loadBilling() {
    fetch(`${API_BASE}/billing`)
        .then(res => res.json())
        .then(res => {
            if (res.status === 'success') {
                const tbody = document.getElementById('billingLedgerTbody');
                tbody.innerHTML = res.data.map(b => `
                    <tr>
                        <td><strong>${b.bill_number}</strong></td>
                        <td>${b.bill_date}</td>
                        <td><strong>${b.patient_name}</strong><br><small style="color:#64748B;">${b.patient_code}</small></td>
                        <td><strong>₹${parseFloat(b.total_amount).toFixed(2)}</strong></td>
                        <td style="color:#059669; font-weight:700;">₹${parseFloat(b.paid_amount).toFixed(2)}</td>
                        <td style="color:#DC2626; font-weight:700;">₹${parseFloat(b.balance_amount).toFixed(2)}</td>
                        <td><span class="badge ${b.payment_status === 'Paid' ? 'badge-success' : (b.payment_status === 'Partially Paid' ? 'badge-warning' : 'badge-danger')}">${b.payment_status}</span></td>
                        <td>
                            <button class="btn btn-outline btn-sm" onclick="printReceipt('${b.bill_number}', '${b.patient_name}', '${b.patient_code}', ${b.total_amount}, ${b.paid_amount}, ${b.balance_amount}, '${b.bill_date}')">
                                Print Receipt
                            </button>
                        </td>
                    </tr>
                `).join('');
            }
        });

    // Populate billing patient dropdown
    fetch(`${API_BASE}/patients`)
        .then(r => r.json())
        .then(r => {
            const select = document.getElementById('billPatientSelect');
            if (select) {
                select.innerHTML = '<option value="">-- Choose Patient --</option>' +
                    r.data.map(p => `<option value="${p.patient_id}">${p.full_name} (${p.patient_code}) - Mobile: +91 ${p.mobile_number}</option>`).join('');
            }
        });
}

function calculateBillTotals() {
    const c = parseFloat(document.getElementById('billConsultationCharges').value) || 0;
    const l = parseFloat(document.getElementById('billLabCharges').value) || 0;
    const p = parseFloat(document.getElementById('billPharmacyCharges').value) || 0;
    const o = parseFloat(document.getElementById('billOtherCharges').value) || 0;
    const taxRate = parseFloat(document.getElementById('billTaxRate').value) || 0;
    const paid = parseFloat(document.getElementById('billPaidAmount').value) || 0;

    const subtotal = c + l + p + o;
    const taxAmount = (subtotal * taxRate) / 100.0;
    const total = subtotal + taxAmount;
    const balance = Math.max(0, total - paid);

    document.getElementById('calcSubtotal').textContent = '₹' + subtotal.toFixed(2);
    document.getElementById('calcTaxAmount').textContent = '₹' + taxAmount.toFixed(2);
    document.getElementById('calcTotal').textContent = '₹' + total.toFixed(2);
    document.getElementById('calcBalance').textContent = '₹' + balance.toFixed(2);
}

function submitInvoice() {
    const patId = document.getElementById('billPatientSelect').value;
    const c = parseFloat(document.getElementById('billConsultationCharges').value) || 0;
    const l = parseFloat(document.getElementById('billLabCharges').value) || 0;
    const p = parseFloat(document.getElementById('billPharmacyCharges').value) || 0;
    const o = parseFloat(document.getElementById('billOtherCharges').value) || 0;
    const taxRate = parseFloat(document.getElementById('billTaxRate').value) || 5;
    const paid = parseFloat(document.getElementById('billPaidAmount').value) || 0;
    const method = document.getElementById('billPaymentMethod').value;

    if (!patId) {
        alert('Please select a patient.');
        return;
    }

    fetch(`${API_BASE}/billing`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            patient_id: patId,
            consultation_charges: c,
            lab_charges: l,
            pharmacy_charges: p,
            other_charges: o,
            tax_rate: taxRate,
            paid_amount: paid,
            payment_method: method
        })
    })
    .then(r => r.json())
    .then(r => {
        if (r.status === 'success') {
            alert(r.message);
            document.getElementById('createBillModal').classList.remove('active');
            loadBilling();
        } else {
            alert(r.message || 'Error creating invoice.');
        }
    });
}

function printReceipt(billNo, patientName, patientCode, total, paid, balance, date) {
    const printArea = document.getElementById('printableReceiptArea');
    printArea.innerHTML = `
        <div style="padding:30px; font-family:'Inter', sans-serif; color:#0B192C;">
            <div style="border-bottom:2px solid #0D9488; padding-bottom:16px; margin-bottom:20px; display:flex; justify-content:space-between; align-items:flex-start;">
                <div>
                    <h2 style="font-size:1.6rem; font-weight:800; color:#0B192C;">+ MEDAXIS HOSPITAL</h2>
                    <p style="font-size:0.85rem; color:#64748B;">Simplifying Hospital Operations. Connecting Better Care.<br>GSTIN: 27AABCM8821N1ZS • Helpline: 1800-MEDAXIS</p>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:1.2rem; font-weight:800; color:#0D9488;">OFFICIAL TAX INVOICE</div>
                    <div style="font-size:0.85rem;"><strong>Invoice #:</strong> ${billNo}</div>
                    <div style="font-size:0.85rem;"><strong>Date:</strong> ${date}</div>
                </div>
            </div>

            <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:6px; padding:12px 16px; margin-bottom:20px; display:grid; grid-template-columns:1fr 1fr;">
                <div><strong>Patient Name:</strong> ${patientName}</div>
                <div><strong>Patient ID:</strong> ${patientCode}</div>
            </div>

            <table style="width:100%; border-collapse:collapse; margin-bottom:24px; font-size:0.9rem;">
                <tr style="background:#F1F5F9; border-bottom:1px solid #CBD5E1;">
                    <th style="padding:10px; text-align:left;">Description</th>
                    <th style="padding:10px; text-align:right;">Amount (INR)</th>
                </tr>
                <tr style="border-bottom:1px solid #E2E8F0;">
                    <td style="padding:10px;">Total Bill Amount (Including GST 5%)</td>
                    <td style="padding:10px; text-align:right; font-weight:700;">₹${parseFloat(total).toFixed(2)}</td>
                </tr>
                <tr style="border-bottom:1px solid #E2E8F0; color:#059669;">
                    <td style="padding:10px;">Amount Settled</td>
                    <td style="padding:10px; text-align:right; font-weight:700;">₹${parseFloat(paid).toFixed(2)}</td>
                </tr>
                <tr style="background:#FEF2F2; font-weight:800; color:#DC2626;">
                    <td style="padding:10px;">Outstanding Balance Due</td>
                    <td style="padding:10px; text-align:right;">₹${parseFloat(balance).toFixed(2)}</td>
                </tr>
            </table>

            <div style="margin-top:60px; display:flex; justify-content:space-between; align-items:flex-end;">
                <div style="font-size:0.75rem; color:#94A3B8;">Computer-generated tax receipt from MEDAXIS Admin Portal.</div>
                <div style="text-align:center; width:220px;">
                    <div style="border-top:1px solid #334155; margin-bottom:4px;"></div>
                    <div style="font-size:0.8rem; font-weight:700;">Authorized Accounts Officer</div>
                </div>
            </div>
        </div>
    `;

    window.print();
}

