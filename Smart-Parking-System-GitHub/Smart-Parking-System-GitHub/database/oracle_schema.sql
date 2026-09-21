-- ============================================================
-- SMART PARKING SYSTEM - ORACLE XE 11G DATABASE SETUP
-- ============================================================
-- Run this script in the Oracle schema used by the Flask app.
-- Adjust the demo password before using outside a local project.

-- ---------------- PARKING USERS ----------------
CREATE TABLE parking_users (
    user_id NUMBER PRIMARY KEY,
    username VARCHAR2(50) UNIQUE NOT NULL,
    password VARCHAR2(100) NOT NULL,
    role VARCHAR2(20) DEFAULT 'USER' NOT NULL
);

INSERT INTO parking_users (user_id, username, password, role)
VALUES (1, 'admin', 'admin123', 'ADMIN');

-- ---------------- PARKING SLOTS ----------------
CREATE TABLE parking_slots (
    slot_id NUMBER PRIMARY KEY,
    slot_number VARCHAR2(20) UNIQUE NOT NULL,
    status VARCHAR2(20) DEFAULT 'AVAILABLE' NOT NULL,
    vehicle_number VARCHAR2(30),
    CONSTRAINT chk_parking_slot_status
        CHECK (status IN ('AVAILABLE', 'OCCUPIED'))
);

-- 20 initial parking slots
INSERT INTO parking_slots (slot_id, slot_number, status, vehicle_number) VALUES (1, 'P01', 'AVAILABLE', NULL);
INSERT INTO parking_slots (slot_id, slot_number, status, vehicle_number) VALUES (2, 'P02', 'AVAILABLE', NULL);
INSERT INTO parking_slots (slot_id, slot_number, status, vehicle_number) VALUES (3, 'P03', 'AVAILABLE', NULL);
INSERT INTO parking_slots (slot_id, slot_number, status, vehicle_number) VALUES (4, 'P04', 'AVAILABLE', NULL);
INSERT INTO parking_slots (slot_id, slot_number, status, vehicle_number) VALUES (5, 'P05', 'AVAILABLE', NULL);
INSERT INTO parking_slots (slot_id, slot_number, status, vehicle_number) VALUES (6, 'P06', 'AVAILABLE', NULL);
INSERT INTO parking_slots (slot_id, slot_number, status, vehicle_number) VALUES (7, 'P07', 'AVAILABLE', NULL);
INSERT INTO parking_slots (slot_id, slot_number, status, vehicle_number) VALUES (8, 'P08', 'AVAILABLE', NULL);
INSERT INTO parking_slots (slot_id, slot_number, status, vehicle_number) VALUES (9, 'P09', 'AVAILABLE', NULL);
INSERT INTO parking_slots (slot_id, slot_number, status, vehicle_number) VALUES (10, 'P10', 'AVAILABLE', NULL);
INSERT INTO parking_slots (slot_id, slot_number, status, vehicle_number) VALUES (11, 'P11', 'AVAILABLE', NULL);
INSERT INTO parking_slots (slot_id, slot_number, status, vehicle_number) VALUES (12, 'P12', 'AVAILABLE', NULL);
INSERT INTO parking_slots (slot_id, slot_number, status, vehicle_number) VALUES (13, 'P13', 'AVAILABLE', NULL);
INSERT INTO parking_slots (slot_id, slot_number, status, vehicle_number) VALUES (14, 'P14', 'AVAILABLE', NULL);
INSERT INTO parking_slots (slot_id, slot_number, status, vehicle_number) VALUES (15, 'P15', 'AVAILABLE', NULL);
INSERT INTO parking_slots (slot_id, slot_number, status, vehicle_number) VALUES (16, 'P16', 'AVAILABLE', NULL);
INSERT INTO parking_slots (slot_id, slot_number, status, vehicle_number) VALUES (17, 'P17', 'AVAILABLE', NULL);
INSERT INTO parking_slots (slot_id, slot_number, status, vehicle_number) VALUES (18, 'P18', 'AVAILABLE', NULL);
INSERT INTO parking_slots (slot_id, slot_number, status, vehicle_number) VALUES (19, 'P19', 'AVAILABLE', NULL);
INSERT INTO parking_slots (slot_id, slot_number, status, vehicle_number) VALUES (20, 'P20', 'AVAILABLE', NULL);

-- ---------------- PARKING HISTORY ----------------
CREATE TABLE parking_history (
    history_id NUMBER PRIMARY KEY,
    slot_number VARCHAR2(20) NOT NULL,
    vehicle_number VARCHAR2(30) NOT NULL,
    entry_time TIMESTAMP WITH TIME ZONE NOT NULL,
    exit_time TIMESTAMP WITH TIME ZONE,
    status VARCHAR2(20) NOT NULL,
    CONSTRAINT chk_parking_history_status
        CHECK (status IN ('PARKED', 'COMPLETED'))
);

CREATE SEQUENCE parking_history_seq
    START WITH 1
    INCREMENT BY 1
    NOCACHE
    NOCYCLE;

COMMIT;

-- ---------------- VERIFICATION ----------------
SELECT * FROM parking_users;
SELECT * FROM parking_slots ORDER BY slot_id;
SELECT * FROM parking_history ORDER BY history_id DESC;
