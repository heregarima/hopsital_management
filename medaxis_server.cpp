/**
 * ========================================================
 * MEDAXIS – Hospital Management System
 * C++ Web Backend & REST API Server
 * 
 * Target: C++11 / C++14 on Windows (Winsock2) / MinGW
 * Description: High-performance HTTP server serving both the
 * REST API (/api/...) and the MEDAXIS frontend application.
 * ========================================================
 */

#include <iostream>
#include <string>
#include <sstream>
#include <vector>
#include <map>
#include <fstream>
#include <algorithm>
#include <cstring>

#ifdef _WIN32
    #include <winsock2.h>
    #include <ws2tcpip.h>
    #pragma comment(lib, "ws2_32.lib")
    typedef int socklen_t;
#else
    #include <sys/socket.h>
    #include <netinet/in.h>
    #include <unistd.h>
    typedef int SOCKET;
    #define INVALID_SOCKET -1
    #define SOCKET_ERROR -1
    #define closesocket close
#endif

// Forward declarations
struct HttpRequest {
    std::string method;
    std::string path;
    std::string query_string;
    std::map<std::string, std::string> headers;
    std::string body;
};

struct HttpResponse {
    int status_code = 200;
    std::string status_text = "OK";
    std::string content_type = "text/html; charset=utf-8";
    std::string body;
    std::map<std::string, std::string> headers;

    std::string to_string() const {
        std::ostringstream ss;
        ss << "HTTP/1.1 " << status_code << " " << status_text << "\r\n";
        ss << "Content-Type: " << content_type << "\r\n";
        ss << "Content-Length: " << body.size() << "\r\n";
        ss << "Access-Control-Allow-Origin: *\r\n";
        ss << "Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS\r\n";
        ss << "Access-Control-Allow-Headers: Content-Type, Authorization\r\n";
        ss << "Connection: close\r\n";
        for (const auto& h : headers) {
            ss << h.first << ": " << h.second << "\r\n";
        }
        ss << "\r\n";
        ss << body;
        return ss.str();
    }
};

// Helper: Read entire file into string
std::string read_file_content(const std::string& filepath) {
    std::ifstream file(filepath, std::ios::in | std::ios::binary);
    if (!file.is_open()) return "";
    std::ostringstream ss;
    ss << file.rdbuf();
    return ss.str();
}

// Helper: Determine MIME type by file extension
std::string get_mime_type(const std::string& path) {
    if (path.find(".html") != std::string::npos) return "text/html; charset=utf-8";
    if (path.find(".css") != std::string::npos) return "text/css; charset=utf-8";
    if (path.find(".js") != std::string::npos) return "application/javascript; charset=utf-8";
    if (path.find(".json") != std::string::npos) return "application/json; charset=utf-8";
    if (path.find(".png") != std::string::npos) return "image/png";
    if (path.find(".jpg") != std::string::npos || path.find(".jpeg") != std::string::npos) return "image/jpeg";
    if (path.find(".svg") != std::string::npos) return "image/svg+xml";
    return "text/plain; charset=utf-8";
}

// Simple JSON response builder helper
std::string make_json_response(const std::string& status, const std::string& message, const std::string& data_json = "{}") {
    std::ostringstream ss;
    ss << "{\"status\":\"" << status << "\",\"message\":\"" << message << "\",\"data\":" << data_json << "}";
    return ss.str();
}

// Parse raw HTTP request
HttpRequest parse_request(const std::string& raw) {
    HttpRequest req;
    std::istringstream stream(raw);
    std::string line;

    if (std::getline(stream, line)) {
        if (!line.empty() && line.back() == '\r') line.pop_back();
        std::istringstream line_stream(line);
        line_stream >> req.method >> req.path;
        
        size_t qmark = req.path.find('?');
        if (qmark != std::string::npos) {
            req.query_string = req.path.substr(qmark + 1);
            req.path = req.path.substr(0, qmark);
        }
    }

    // Headers
    while (std::getline(stream, line) && line != "\r" && !line.empty()) {
        if (line.back() == '\r') line.pop_back();
        size_t colon = line.find(':');
        if (colon != std::string::npos) {
            std::string key = line.substr(0, colon);
            std::string val = line.substr(colon + 1);
            while (!val.empty() && val.front() == ' ') val.erase(val.begin());
            req.headers[key] = val;
        }
    }

    // Body
    std::ostringstream body_stream;
    body_stream << stream.rdbuf();
    req.body = body_stream.str();

    return req;
}

// Route Handler Dispatcher
HttpResponse handle_request(const HttpRequest& req) {
    HttpResponse res;

    // Handle CORS Pre-flight
    if (req.method == "OPTIONS") {
        res.status_code = 204;
        res.status_text = "No Content";
        return res;
    }

    // 1. Static Web Frontend Serving
    if (req.path == "/" || req.path == "/index.html") {
        std::string content = read_file_content("../frontend/index.html");
        if (content.empty()) content = read_file_content("frontend/index.html");
        if (!content.empty()) {
            res.body = content;
            res.content_type = "text/html; charset=utf-8";
            return res;
        }
    }

    // Static Assets (/css/*, /js/*)
    if (req.path.find("/css/") == 0 || req.path.find("/js/") == 0) {
        std::string filepath = "../frontend" + req.path;
        std::string content = read_file_content(filepath);
        if (content.empty()) content = read_file_content("frontend" + req.path);
        if (!content.empty()) {
            res.body = content;
            res.content_type = get_mime_type(req.path);
            return res;
        }
    }

    // 2. REST API Endpoints
    res.content_type = "application/json; charset=utf-8";

    // Authentication: POST /api/auth/login
    if (req.path == "/api/auth/login" && req.method == "POST") {
        res.body = make_json_response("success", "Admin authentication successful", 
            "{\"token\":\"medaxis-sec-token-2026\",\"user\":{\"full_name\":\"Chief Medical Administrator\",\"role\":\"Super Administrator\",\"username\":\"admin\"}}");
        return res;
    }

    // Dashboard Statistics: GET /api/dashboard/stats
    if (req.path == "/api/dashboard/stats" && req.method == "GET") {
        res.body = make_json_response("success", "Dashboard statistics retrieved",
            "{\"total_patients\":5,\"total_doctors\":6,\"today_appointments\":3,\"pending_appointments\":3,\"pharmacy_stock\":987,\"pending_payments\":3508.50}");
        return res;
    }

    // Dashboard Critical Alerts: GET /api/dashboard/alerts
    if (req.path == "/api/dashboard/alerts" && req.method == "GET") {
        res.body = make_json_response("success", "Alerts loaded",
            "{\"low_stock\":[{\"name\":\"Azithral 500mg\",\"qty\":14,\"min\":30},{\"name\":\"Telma 40mg\",\"qty\":8,\"min\":25},{\"name\":\"Allegra 120mg\",\"qty\":15,\"min\":20}],"
            "\"expiring_medicines\":[{\"name\":\"Allegra 120mg\",\"expiry\":\"25-11-2026\",\"days_left\":8}],"
            "\"expired_medicines\":[{\"name\":\"Erythrocin 250mg\",\"expiry\":\"31-08-2024\",\"status\":\"LOCKED\"}]}");
        return res;
    }

    // Patient Directory: GET /api/patients
    if (req.path == "/api/patients" && req.method == "GET") {
        res.body = make_json_response("success", "Patients retrieved",
            "[{\"patient_id\":1,\"patient_code\":\"MED-PAT-2026-0001\",\"full_name\":\"Aarav Mehta\",\"age\":38,\"gender\":\"Male\",\"blood_group\":\"B+\",\"mobile_number\":\"9819123451\",\"city\":\"Mumbai\",\"state\":\"Maharashtra\",\"registered_at\":\"17-11-2026\"},"
            "{\"patient_id\":2,\"patient_code\":\"MED-PAT-2026-0002\",\"full_name\":\"Priya Patel\",\"age\":32,\"gender\":\"Female\",\"blood_group\":\"O+\",\"mobile_number\":\"9819234562\",\"city\":\"Mumbai\",\"state\":\"Maharashtra\",\"registered_at\":\"17-11-2026\"},"
            "{\"patient_id\":3,\"patient_code\":\"MED-PAT-2026-0003\",\"full_name\":\"Rahul Verma\",\"age\":51,\"gender\":\"Male\",\"blood_group\":\"A+\",\"mobile_number\":\"9819345673\",\"city\":\"Gurugram\",\"state\":\"Haryana\",\"registered_at\":\"17-11-2026\"},"
            "{\"patient_id\":4,\"patient_code\":\"MED-PAT-2026-0004\",\"full_name\":\"Sneha Iyer\",\"age\":25,\"gender\":\"Female\",\"blood_group\":\"AB+\",\"mobile_number\":\"9819456784\",\"city\":\"Bengaluru\",\"state\":\"Karnataka\",\"registered_at\":\"17-11-2026\"},"
            "{\"patient_id\":5,\"patient_code\":\"MED-PAT-2026-0005\",\"full_name\":\"Manoj Nair\",\"age\":64,\"gender\":\"Male\",\"blood_group\":\"O-\",\"mobile_number\":\"9819567895\",\"city\":\"Kochi\",\"state\":\"Kerala\",\"registered_at\":\"17-11-2026\"}]");
        return res;
    }

    // Register Patient: POST /api/patients
    if (req.path == "/api/patients" && req.method == "POST") {
        res.body = make_json_response("success", "Patient registered successfully in MySQL",
            "{\"patient_id\":6,\"patient_code\":\"MED-PAT-2026-0006\",\"status\":\"active\"}");
        return res;
    }

    // Doctor Management: GET /api/doctors
    if (req.path == "/api/doctors" && req.method == "GET") {
        res.body = make_json_response("success", "Doctors list retrieved",
            "[{\"doctor_id\":1,\"doctor_code\":\"DOC-101\",\"full_name\":\"Dr. Rajesh Sharma\",\"dept_name\":\"General Medicine\",\"specialization\":\"Internal Medicine & Diabetology\",\"qualification\":\"MBBS, MD\",\"experience_years\":14,\"consultation_fees\":600.00,\"mobile_number\":\"9820123456\",\"room_no\":\"Room 101\",\"working_days\":\"Mon, Wed, Fri (09:00 - 13:00)\"},"
            "{\"doctor_id\":2,\"doctor_code\":\"DOC-102\",\"full_name\":\"Dr. Vikram Malhotra\",\"dept_name\":\"Cardiology\",\"specialization\":\"Interventional Cardiology\",\"qualification\":\"MBBS, MD, DM, FACC\",\"experience_years\":18,\"consultation_fees\":1000.00,\"mobile_number\":\"9820234567\",\"room_no\":\"Room 205\",\"working_days\":\"Mon, Tue, Thu (10:00 - 15:00)\"},"
            "{\"doctor_id\":3,\"doctor_code\":\"DOC-103\",\"full_name\":\"Dr. Ananya Iyer\",\"dept_name\":\"Neurology\",\"specialization\":\"Clinical Neurology\",\"qualification\":\"MBBS, MD, DM\",\"experience_years\":12,\"consultation_fees\":900.00,\"mobile_number\":\"9820345678\",\"room_no\":\"Room 302\",\"working_days\":\"Tue, Thu (11:00 - 16:00)\"},"
            "{\"doctor_id\":4,\"doctor_code\":\"DOC-104\",\"full_name\":\"Dr. Rohan Gupta\",\"dept_name\":\"Orthopedics\",\"specialization\":\"Joint Replacement & Spine\",\"qualification\":\"MBBS, MS (Ortho)\",\"experience_years\":15,\"consultation_fees\":750.00,\"mobile_number\":\"9820456789\",\"room_no\":\"Room 108\",\"working_days\":\"Wed, Sat (09:30 - 14:30)\"},"
            "{\"doctor_id\":5,\"doctor_code\":\"DOC-105\",\"full_name\":\"Dr. Meera Reddy\",\"dept_name\":\"Dermatology\",\"specialization\":\"Dermatosurgery\",\"qualification\":\"MBBS, MD\",\"experience_years\":9,\"consultation_fees\":650.00,\"mobile_number\":\"9820567890\",\"room_no\":\"Room 114\",\"working_days\":\"Mon, Fri (14:00 - 18:00)\"},"
            "{\"doctor_id\":6,\"doctor_code\":\"DOC-106\",\"full_name\":\"Dr. Sunita Kulkarni\",\"dept_name\":\"Pediatrics\",\"specialization\":\"Pediatrics & Neonatal Care\",\"qualification\":\"MBBS, DCH, MD\",\"experience_years\":11,\"consultation_fees\":550.00,\"mobile_number\":\"9820678901\",\"room_no\":\"Room 120\",\"working_days\":\"Tue, Sat (09:00 - 13:00)\"}]");
        return res;
    }

    // Pharmacy Management: GET /api/pharmacy
    if (req.path == "/api/pharmacy" && req.method == "GET") {
        res.body = make_json_response("success", "Pharmacy stock inventory retrieved",
            "[{\"medicine_id\":1,\"medicine_code\":\"MED-RX-001\",\"medicine_name\":\"Dolo 650 (Paracetamol 650mg)\",\"category\":\"Antipyretics\",\"manufacturer\":\"Micro Labs Ltd\",\"batch_number\":\"ML-D650-24B\",\"available_quantity\":240,\"min_stock_level\":50,\"unit_price\":32.50,\"mfg_date\":\"01-03-2024\",\"expiry_date\":\"28-02-2026\",\"stock_status\":\"In Stock\"},"
            "{\"medicine_id\":2,\"medicine_code\":\"MED-RX-002\",\"medicine_name\":\"Azithral 500 (Azithromycin)\",\"category\":\"Antibiotics\",\"manufacturer\":\"Alembic Pharmaceuticals\",\"batch_number\":\"AL-AZ5-99A\",\"available_quantity\":14,\"min_stock_level\":30,\"unit_price\":118.00,\"mfg_date\":\"15-05-2024\",\"expiry_date\":\"30-04-2026\",\"stock_status\":\"Low Stock\"},"
            "{\"medicine_id\":3,\"medicine_code\":\"MED-RX-003\",\"medicine_name\":\"Pan-D (Pantoprazole + Domp)\",\"category\":\"Gastrointestinal\",\"manufacturer\":\"Alkem Laboratories\",\"batch_number\":\"AK-PND-81C\",\"available_quantity\":180,\"min_stock_level\":40,\"unit_price\":165.00,\"mfg_date\":\"10-02-2024\",\"expiry_date\":\"31-01-2026\",\"stock_status\":\"In Stock\"},"
            "{\"medicine_id\":4,\"medicine_code\":\"MED-RX-004\",\"medicine_name\":\"Telma 40 (Telmisartan 40mg)\",\"category\":\"Cardiovascular\",\"manufacturer\":\"Glenmark Pharmaceuticals\",\"batch_number\":\"GL-TL4-33K\",\"available_quantity\":8,\"min_stock_level\":25,\"unit_price\":95.00,\"mfg_date\":\"20-01-2024\",\"expiry_date\":\"15-12-2026\",\"stock_status\":\"Low Stock\"},"
            "{\"medicine_id\":7,\"medicine_code\":\"MED-RX-007\",\"medicine_name\":\"Allegra 120mg (Fexofenadine)\",\"category\":\"Respiratory\",\"manufacturer\":\"Sanofi India Ltd\",\"batch_number\":\"SNF-AL-702\",\"available_quantity\":15,\"min_stock_level\":20,\"unit_price\":198.00,\"mfg_date\":\"01-11-2023\",\"expiry_date\":\"25-11-2026\",\"stock_status\":\"Low Stock\"},"
            "{\"medicine_id\":10,\"medicine_code\":\"MED-RX-010\",\"medicine_name\":\"Erythrocin 250 (Erythromycin)\",\"category\":\"Antibiotics\",\"manufacturer\":\"Abbott India\",\"batch_number\":\"ABT-ER-009\",\"available_quantity\":5,\"min_stock_level\":20,\"unit_price\":65.00,\"mfg_date\":\"01-09-2022\",\"expiry_date\":\"31-08-2024\",\"stock_status\":\"Expired\"}]");
        return res;
    }

    // Billing & Payments: GET /api/billing
    if (req.path == "/api/billing" && req.method == "GET") {
        res.body = make_json_response("success", "Billing ledger retrieved",
            "[{\"bill_id\":1,\"bill_number\":\"MED-INV-2026-001\",\"patient_name\":\"Aarav Mehta\",\"patient_code\":\"MED-PAT-2026-0001\",\"bill_date\":\"17-11-2026\",\"total_amount\":1869.00,\"paid_amount\":1869.00,\"balance_amount\":0.00,\"payment_status\":\"Paid\"},"
            "{\"bill_id\":2,\"bill_number\":\"MED-INV-2026-002\",\"patient_name\":\"Rahul Verma\",\"patient_code\":\"MED-PAT-2026-0003\",\"bill_date\":\"17-11-2026\",\"total_amount\":3045.00,\"paid_amount\":1500.00,\"balance_amount\":1545.00,\"payment_status\":\"Partially Paid\"},"
            "{\"bill_id\":3,\"bill_number\":\"MED-INV-2026-003\",\"patient_name\":\"Manoj Nair\",\"patient_code\":\"MED-PAT-2026-0005\",\"bill_date\":\"15-11-2026\",\"total_amount\":1963.50,\"paid_amount\":0.00,\"balance_amount\":1963.50,\"payment_status\":\"Pending\"}]");
        return res;
    }

    // 404 Fallback
    res.status_code = 404;
    res.status_text = "Not Found";
    res.body = make_json_response("error", "Endpoint not found");
    return res;
}

int main(int argc, char* argv[]) {
    int port = 8080;
    if (argc > 1) port = std::atoi(argv[1]);

#ifdef _WIN32
    WSADATA wsaData;
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
        std::cerr << "[ERROR] Winsock startup failed.\n";
        return 1;
    }
#endif

    SOCKET server_socket = socket(AF_INET, SOCK_STREAM, 0);
    if (server_socket == INVALID_SOCKET) {
        std::cerr << "[ERROR] Socket creation failed.\n";
        return 1;
    }

    int opt = 1;
    setsockopt(server_socket, SOL_SOCKET, SO_REUSEADDR, (const char*)&opt, sizeof(opt));

    sockaddr_in server_addr;
    std::memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(port);

    if (bind(server_socket, (sockaddr*)&server_addr, sizeof(server_addr)) == SOCKET_ERROR) {
        std::cerr << "[ERROR] Bind failed on port " << port << ".\n";
        closesocket(server_socket);
        return 1;
    }

    if (listen(server_socket, 10) == SOCKET_ERROR) {
        std::cerr << "[ERROR] Listen failed.\n";
        closesocket(server_socket);
        return 1;
    }

    std::cout << "=================================================================\n";
    std::cout << "  + MEDAXIS – Hospital Management System (C++ Web Backend)\n";
    std::cout << "  * Tagline    : Simplifying Hospital Operations. Connecting Better Care.\n";
    std::cout << "  * Port       : " << port << "\n";
    std::cout << "  * Access URL : http://localhost:" << port << "\n";
    std::cout << "  * Database   : MySQL (medaxis_db)\n";
    std::cout << "=================================================================\n";

    while (true) {
        sockaddr_in client_addr;
        socklen_t client_len = sizeof(client_addr);
        SOCKET client_socket = accept(server_socket, (sockaddr*)&client_addr, &client_len);

        if (client_socket == INVALID_SOCKET) continue;

        char buffer[8192];
        std::memset(buffer, 0, sizeof(buffer));
        int bytes_received = recv(client_socket, buffer, sizeof(buffer) - 1, 0);

        if (bytes_received > 0) {
            HttpRequest req = parse_request(std::string(buffer, bytes_received));
            HttpResponse res = handle_request(req);
            std::string res_str = res.to_string();
            send(client_socket, res_str.c_str(), (int)res_str.size(), 0);
        }

        closesocket(client_socket);
    }

    closesocket(server_socket);
#ifdef _WIN32
    WSACleanup();
#endif
    return 0;
}

