CREATE TABLE "users"(
    "id" BIGSERIAL NOT NULL,
    "ldap_id" VARCHAR(255) NOT NULL
);

ALTER TABLE
    "users" ADD PRIMARY KEY("id");
CREATE TABLE "projects"(
    "id" BIGSERIAL NOT NULL,
    "created_by" BIGINT NOT NULL,
    "teacher_id" BIGINT NOT NULL,
    "title" VARCHAR(255) NOT NULL,
    "description" VARCHAR(255) NOT NULL,
    "specifications" VARCHAR(255) NOT NULL
);

COMMENT
ON TABLE
    "projects" IS 'specifications is a symlink';
ALTER TABLE
    "projects" ADD PRIMARY KEY("id");
ALTER TABLE
    "projects" ADD CONSTRAINT "projects_title_unique" UNIQUE("title");
ALTER TABLE
    "projects" ADD CONSTRAINT "projects_specifications_unique" UNIQUE("specifications");
CREATE TABLE "students_projects"(
    "id" BIGSERIAL NOT NULL,
    "student_id" BIGINT NOT NULL,
    "project_id" BIGINT NOT NULL,
    "value" INTEGER NOT NULL
);

COMMENT
ON TABLE
    "students_projects" IS 'unique(student_id, project_id)';
ALTER TABLE
    "students_projects" ADD PRIMARY KEY("id");

ALTER TABLE
    "students_projects" ADD CONSTRAINT "students_projects_unique" UNIQUE("project_id", "student_id");

CREATE TABLE "keywords"(
    "id" BIGSERIAL NOT NULL,
    "name" VARCHAR(255) NOT NULL
);
ALTER TABLE
    "keywords" ADD PRIMARY KEY("id");
ALTER TABLE
    "keywords" ADD CONSTRAINT "keywords_name_unique" UNIQUE("name");
CREATE TABLE "keywords_projects"(
    "id" BIGSERIAL NOT NULL,
    "project_id" BIGINT NOT NULL,
    "keyword_id" BIGINT NOT NULL
);
COMMENT
ON TABLE
    "keywords_projects" IS 'unique(keyword_id, project_id)';
ALTER TABLE
    "keywords_projects" ADD PRIMARY KEY("id");
ALTER TABLE
    "keywords_projects" ADD CONSTRAINT "keywords_projects_unique" UNIQUE("keyword_id", "project_id");
CREATE TABLE "roles"(
    "id" BIGSERIAL NOT NULL,
    "name" VARCHAR(255) NOT NULL
);
COMMENT
ON TABLE
    "roles" IS 'sysadmin, program director, secretary, teacher, student';
ALTER TABLE
    "roles" ADD PRIMARY KEY("id");
CREATE TABLE "program"(
    "id" BIGSERIAL NOT NULL,
    "name" VARCHAR(255) NOT NULL
);
COMMENT
ON TABLE
    "program" IS 'isc, synd, etc...';
ALTER TABLE
    "program" ADD PRIMARY KEY("id");
CREATE TABLE "users_roles_programs"(
    "id" BIGSERIAL NOT NULL,
    "user_id" BIGINT NOT NULL,
    "role_id" BIGINT NOT NULL,
    "program_id" BIGINT NOT NULL
);
COMMENT
ON TABLE
    "users_roles_programs" IS 'john is a teacher in ISC but a student in synd...';
ALTER TABLE
    "users_roles_programs" ADD PRIMARY KEY("id");
ALTER TABLE
    "students_projects" ADD CONSTRAINT "students_projects_project_id_foreign" FOREIGN KEY("project_id") REFERENCES "projects"("id");
ALTER TABLE
    "users_roles_programs" ADD CONSTRAINT "users_roles_programs_role_id_foreign" FOREIGN KEY("role_id") REFERENCES "roles"("id");
ALTER TABLE
    "projects" ADD CONSTRAINT "projects_created_by_foreign" FOREIGN KEY("created_by") REFERENCES "users"("id");
ALTER TABLE
    "students_projects" ADD CONSTRAINT "students_projects_student_id_foreign" FOREIGN KEY("student_id") REFERENCES "users"("id");
ALTER TABLE
    "users_roles_programs" ADD CONSTRAINT "users_roles_programs_program_id_foreign" FOREIGN KEY("program_id") REFERENCES "program"("id");
ALTER TABLE
    "projects" ADD CONSTRAINT "projects_teacher_id_foreign" FOREIGN KEY("teacher_id") REFERENCES "users"("id");
ALTER TABLE
    "keywords_projects" ADD CONSTRAINT "keywords_projects_project_id_foreign" FOREIGN KEY("project_id") REFERENCES "projects"("id");
ALTER TABLE
    "users_roles_programs" ADD CONSTRAINT "users_roles_programs_user_id_foreign" FOREIGN KEY("user_id") REFERENCES "users"("id");
ALTER TABLE
    "keywords_projects" ADD CONSTRAINT "keywords_projects_keyword_id_foreign" FOREIGN KEY("keyword_id") REFERENCES "keywords"("id");

-- Insert roles
INSERT INTO "roles" ("name") VALUES
('sysadmin'),
('program director'),
('secretary'),
('teacher'),
('student');

-- Insert programs
INSERT INTO "programs" ("name") VALUES
('ISC'),
('SYND'),
('LSE'),
('ETE');

-- Insert users (2 teachers, 6 students)
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

-- Insert user roles per program (teacher role for teachers, student for students)
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
(9, 3, 2);

-- Insert keywords
INSERT INTO "keywords" ("name") VALUES
('python'),
('web'),
('mobile'),
('ai'),
('database'),
('security'),
('iot'),
('cloud'),
('devops'),
('data-science');

-- Insert projects
INSERT INTO "projects" ("created_by", "teacher_id", "title", "description", "specifications") VALUES
(1, 1, 'E-commerce Platform', 'Build a full-featured e-commerce platform with cart, checkout, and payment integration', '/specs/ecommerce_v1'),
(1, 1, 'Smart Home Mobile App', 'Develop a mobile app to control smart home devices remotely', '/specs/smarthome_app'),
(2, 2, 'AI Chatbot System', 'Create an AI-powered chatbot for customer support using NLP', '/specs/ai_chatbot'),
(2, 2, 'Secure File Sharing', 'Implement a secure file sharing system with encryption', '/specs/secure_files'),
(1, 1, 'IoT Weather Station', 'Design an IoT weather station with sensors and cloud reporting', '/specs/iot_weather');

-- Insert keywords_projects (linking keywords to projects)
INSERT INTO "projects_keywords" ("project_id", "keyword_id") VALUES
(1, 1),
(1, 2),
(1, 5),
(2, 3),
(2, 7),
(3, 1),
(3, 4),
(3, 10),
(4, 6),
(4, 2),
(5, 7),
(5, 1),
(5, 8);

-- Insert students_projects (student grades for projects)
INSERT INTO "project_ratings" ("student_id", "project_id", "value") VALUES
(3, 1, 85),
(4, 1, 90),
(3, 2, 78),
(4, 2, 82),
(5, 4, 88),
(6, 4, 92),
(5, 5, 75),
(7, 3, 95);
