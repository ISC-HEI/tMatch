-- Insert roles
INSERT INTO "roles" ("name") VALUES
('sysadmin'),
('program director'),
('secretary'),
('teacher'),
('student');

-- ─────────────────────────────────────────────
-- PROGRAMS
-- ─────────────────────────────────────────────
INSERT INTO "programs" ("name") VALUES
('ISC'),
('SYND'),
('LSE'),
('ETE');
 
-- ─────────────────────────────────────────────
-- USERS
-- ─────────────────────────────────────────────
INSERT INTO "users" ("ldap_uid") VALUES
('john.doe'),
('jane.smith'),
('alice.johnson'),
('bob.williams'),
('charlie.brown'),
('diana.prince'),
('evan.rogers'),
('fiona.green'),
('leny');
 
-- ─────────────────────────────────────────────
-- PROGRAM MEMBERSHIPS
-- ─────────────────────────────────────────────
INSERT INTO "program_memberships" ("user_id", "role_id", "program_id") VALUES
(1, 4, 1),
(1, 4, 2),
(2, 4, 3),
(2, 5, 1),
(3, 5, 1),
(4, 5, 1),
(5, 5, 2),
(6, 5, 2),
(7, 5, 3),
(8, 5, 4),
(9, 3, 2),
(9, 4, 1),
(9, 5, 1),
(9, 5, 3);
 
-- ─────────────────────────────────────────────
-- KEYWORDS
-- ─────────────────────────────────────────────
INSERT INTO "keywords" ("name") VALUES
('python'),            -- 1
('web'),               -- 2
('mobile'),            -- 3
('ai'),                -- 4
('database'),          -- 5
('security'),          -- 6
('iot'),               -- 7
('cloud'),             -- 8
('devops'),            -- 9
('data-science'),      -- 10
('embedded-systems'),  -- 11
('automation'),        -- 12
('robotics'),          -- 13
('plc'),               -- 14
('power-electronics'), -- 15
('mechatronics'),      -- 16
('cad'),               -- 17
('smart-grid'),        -- 18
('bioinformatics'),    -- 19
('biomedical'),        -- 20
('medical-devices'),   -- 21
('signal-processing'); -- 22
 
-- ─────────────────────────────────────────────
-- PROJECTS
-- program_id: ISC=1, SYND=2, LSE=3, ETE=4
-- ─────────────────────────────────────────────
INSERT INTO "projects" ("created_by", "teacher_id", "title", "description", "specifications", "program_id") VALUES
 
-- ISC (5 projects)
(1, 1, 'E-commerce Platform',
 'Build a full-featured e-commerce platform with cart, checkout, and payment integration',
 '/specs/ecommerce_v1', 1),                                                                  -- 1
(1, 1, 'Smart Home Mobile App',
 'Develop a mobile app to control smart home devices remotely',
 '/specs/smarthome_app', 1),                                                                 -- 2
(2, 2, 'AI Chatbot System',
 'Create an AI-powered chatbot for customer support using NLP',
 '/specs/ai_chatbot', 1),                                                                    -- 3
(2, 2, 'Secure File Sharing',
 'Implement a secure file sharing system with encryption',
 '/specs/secure_files', 1),                                                                  -- 4
(1, 1, 'Cloud DevOps Pipeline',
 'Build a CI/CD pipeline with containerised deployments, automated testing and live monitoring',
 '/specs/cloud_devops', 1),                                                                  -- 5
 
-- SYND (5 projects)
(1, 1, 'IoT Weather Station',
 'Design an IoT weather station with sensors and cloud reporting',
 '/specs/iot_weather', 2),                                                                   -- 6
(1, 1, 'Industrial Sensor Network',
 'Deploy a mesh of industrial sensors with an edge-computing layer and a real-time dashboard',
 '/specs/industrial_sensors', 2),                                                            -- 7
(1, 1, 'Motor Drive Control System',
 'Design a power-electronics motor drive controlled by a PLC with closed-loop speed regulation',
 '/specs/motor_drive', 2),                                                                   -- 8
(1, 1, 'Smart Grid Load Balancer',
 'Implement automated load-balancing algorithms for a local smart-grid testbed',
 '/specs/smart_grid', 2),                                                                    -- 9
(1, 1, 'Robotic Quality Inspection Cell',
 'Build a robotic arm cell for automated visual quality inspection of machined parts using CAD models as reference',
 '/specs/robot_inspection', 2),                                                              -- 10
 
-- LSE (5 projects)
(2, 2, 'Biomedical Signal Analyser',
 'Develop a tool to acquire, filter and classify ECG/EEG signals using embedded DSP techniques',
 '/specs/bio_signal', 3),                                                                    -- 11
(2, 2, 'Genomic Data Pipeline',
 'Build a bioinformatics workflow for variant calling and annotation on whole-genome sequencing data',
 '/specs/genomic_pipeline', 3),                                                              -- 12
(2, 2, 'Lab Automation System',
 'Design a robotic liquid-handling system with scheduling software for high-throughput laboratory workflows',
 '/specs/lab_automation', 3),                                                                -- 13
(2, 2, 'Remote Medical Device Monitor',
 'Create a secure IoT platform for remote monitoring and alerting of connected medical devices',
 '/specs/med_device_monitor', 3),                                                            -- 14
(2, 2, 'AI Cell-Culture Optimiser',
 'Train an AI model to predict and optimise cell-culture conditions from time-lapse microscopy data',
 '/specs/cell_culture_ai', 3);                                                               -- 15
 
-- ─────────────────────────────────────────────
-- PROJECTS ↔ KEYWORDS
-- ─────────────────────────────────────────────
INSERT INTO "projects_keywords" ("project_id", "keyword_id") VALUES
 
-- 1 · E-commerce Platform
(1, 1),   -- python
(1, 2),   -- web
(1, 5),   -- database
 
-- 2 · Smart Home Mobile App
(2, 3),   -- mobile
(2, 7),   -- iot
 
-- 3 · AI Chatbot System
(3, 1),   -- python
(3, 4),   -- ai
(3, 10),  -- data-science
 
-- 4 · Secure File Sharing
(4, 6),   -- security
(4, 2),   -- web
 
-- 5 · Cloud DevOps Pipeline
(5, 8),   -- cloud
(5, 9),   -- devops
(5, 2),   -- web
 
-- 6 · IoT Weather Station
(6, 7),   -- iot
(6, 1),   -- python
(6, 8),   -- cloud
 
-- 7 · Industrial Sensor Network
(7, 7),   -- iot
(7, 11),  -- embedded-systems
(7, 12),  -- automation
(7, 8),   -- cloud
 
-- 8 · Motor Drive Control System
(8, 15),  -- power-electronics
(8, 14),  -- plc
(8, 16),  -- mechatronics
 
-- 9 · Smart Grid Load Balancer
(9, 18),  -- smart-grid
(9, 15),  -- power-electronics
(9, 12),  -- automation
 
-- 10 · Robotic Quality Inspection Cell
(10, 13), -- robotics
(10, 17), -- cad
(10, 12), -- automation
 
-- 11 · Biomedical Signal Analyser
(11, 20), -- biomedical
(11, 22), -- signal-processing
(11, 11), -- embedded-systems
 
-- 12 · Genomic Data Pipeline
(12, 19), -- bioinformatics
(12, 1),  -- python
(12, 10), -- data-science
 
-- 13 · Lab Automation System
(13, 12), -- automation
(13, 13), -- robotics
(13, 5),  -- database
 
-- 14 · Remote Medical Device Monitor
(14, 21), -- medical-devices
(14, 7),  -- iot
(14, 6),  -- security
 
-- 15 · AI Cell-Culture Optimiser
(15, 4),  -- ai
(15, 20), -- biomedical
(15, 10); -- data-science
