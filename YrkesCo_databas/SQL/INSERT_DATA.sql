-- Personuppgifter for Utbildningsledare
INSERT INTO Personuppgifter (Personnummer, E_post) VALUES
('202103150987', 'skywalker77@email.com'),
('199812240123', 'frosty.snowman@mail.net'),
('200506300456', 'dragonXfire@webmail.org'),
('201110290789', 'moonlight.shadow@inbox.com'),
('199905010321', 'echo.blaze@fastmail.com'),
('200307220654', 'nova.striker@outlook.net'),
('201809170987', 'cyber.phantom@techhub.io'),
('199702280222', 'storm.chaser@cloudmail.com'),
('202012120888', 'comet.rider@starrysky.org'); -- These are newly added (extra)


-- ADDRESSER-------------------------------------------------
-- Addresses for Konsultföretag
INSERT INTO Adress (Gatuadress, Postnummer, Stad, Land) VALUES
('Gata 1', '12345', 'Stockholm', 'Sweden'),
('Gata 2', '54321', 'Göteborg', 'Sweden');
-- Addresses for Anläggning
INSERT INTO Adress (Gatuadress, Postnummer, Stad, Land) VALUES
('Anläggning 1', '10000', 'Stockholm', 'Sweden'),
('Anläggning 2', '20000', 'Göteborg', 'Sweden');
-- Konsultföretag 
INSERT INTO KonsultForetag (Foretagsnamn, Org_nr, F_skatt, Adress_id) VALUES
('Konsult AB', '556677-8899', TRUE, 1),
('Tech Konsult AB', '112233-4455', TRUE, 2);

-- KONSULTER--------------
INSERT INTO Konsult (Fornamn, Efternamn, KonsultF_id, ArvodePerTimme) VALUES
('John', 'Doe', 1, 500.00),  -- KonsultF_id 1 (Konsult AB)
('Jane', 'Smith', 1, 550.00),  -- KonsultF_id 1 (Konsult AB)
('David', 'Brown', 2, 600.00);  -- KonsultF_id 2 (Tech Konsult AB)

-- UTBILDARE---------------
INSERT INTO Utbildare (Fornamn, Efternamn, Personuppgifter_id, Konsult_id, Konsult) VALUES
('Kokchun', 'Giang', 4, 1, TRUE),
('Jane', 'Smith', 5, 2, TRUE),
('David', 'Brown', 6, 3, TRUE),
('Emily', 'White', 7, NULL, FALSE),
('Chris', 'Black', 8, NULL, FALSE),
('Sarah', 'Green', 9, NULL, FALSE);

-- Utbildningsledare---------------
INSERT INTO UtbildningsLedare (Fornamn, Efternamn, Personuppgifter_id, Konsult_id, Konsult) VALUES
('Anna', 'Johansson', 1, NULL, FALSE),
('Erik', 'Svensson', 2, NULL, FALSE),
('Maria', 'Karlsson', 3, NULL, FALSE);

--Anläggning--------------------
INSERT INTO Anlaggning (Adress_id) VALUES
(1),  -- Address ID 1 for Stockholm
(2);  -- Address ID 2 for Göteborg

-- Programs-----------------------
INSERT INTO Program (Programnamn, Anlaggning_id) VALUES
('Web Development', 1),
('Data Engineering', 2),
('Cybersecurity', 1);


--Courses-------------
INSERT INTO Kurs (Kursnamn, Kurskod, YHP, Beskrivning, Utbildare_id, antalveckor) VALUES
('HTML & CSS', 'WD101', 20, 'Introduction to HTML & CSS', 2, 4),
('JavaScript', 'WD102', 20, 'Introduction to JavaScript', 2, 4),
('Python Basics', 'DE101', 20, 'Introduction to Python Programming', 4, 4),
('Big Data', 'DE102', 25, 'Understanding Big Data Technologies', 1, 5),
('Data Warehousing', 'DE103', 25, 'Data Warehousing and ETL', 6, 5),
('Network Security', 'CS101', 25, 'Introduction to Network Security', 4, 5),
('Ethical Hacking', 'CS102', 20, 'Basics of Ethical Hacking', 1, 3),
('Cybersecurity Policies', 'CS103', 30, 'Cybersecurity Policy and Management', 6, 6),
('SEO & SEM', 'DM101', 15, 'Search Engine Optimization and Marketing', 4, 3),
('Frontend Development', 'FD101', 35, 'Introduction to HTML, CSS, and JavaScript', 3, 6),
('Backend Development', 'BD102', 35, 'Learn server-side development using Node.js', 2, 6),
('Data Analysis with Python', 'DA103', 20, 'Learn Python for data analysis and visualization', 1, 4),
('Database Management', 'DB104', 40, 'Learn about databases, SQL, and data management', 3, 7),
('Cybersecurity Fundamentals', 'CS105', 40, 'Introduction to cybersecurity principles and practices', 5, 8),
('Network Security', 'NS106', 40, 'Learn about securing networks and infrastructure', 2, 8),
('Digital Marketing Strategies', 'DM107', 30, 'Learn about digital marketing techniques and strategies', 4, 7),
('Social Media Marketing', 'SM108', 30, 'Learn how to market through social media platforms', 2, 7), 
('Data modellering', 'DE104', 30, 'Learn the process of diagramming data flows, creating database structures', 1, 6);

INSERT INTO Klass (Klassnamn, Program_id, Utbildningsledare_id) VALUES
('WebD23', 5, 1),
('WebD24', 5, 1),
('WebD25', 5, 1),
('DE23', 6, 2),
('DE24', 6, 2),
('DE25', 6, 2),
('CS23', 7, 3),
('CS24', 7, 3),
('CS25', 7, 3);


-- Program-Kurs relationships (Each program has at least 3 courses)
INSERT INTO ProgramKurs (Program_id, Kurs_id) VALUES
(5, 1),
(5, 9),
(5, 10),
(5, 16),
(5, 17),
(6, 3),
(6, 4),
(6, 5), 
(6, 11),
(6, 12),
(6, 13), 
(6, 18),
(7, 2),
(7, 6),
(7, 7),
(7, 8),
(7, 14),
(7, 15);

-- Students --------------------
INSERT INTO Student (Fornamn, Efternamn, Personuppgifter_id, Klass_id) VALUES
('Oliver', 'Andersson', 10, 1),
('Liam', 'Berg', 11, 1),
('Ella', 'Carlsson', 12, 1),
('Mia', 'Ekström', 13, 2),
('Oskar', 'Fransson', 14, 2),
('Noah', 'Gustafsson', 15, 2),
('Ava', 'Hansson', 16, 3),
('Lucas', 'Ivarsson', 17, 3),
('Isabella', 'Johansson', 18, 3),
('Elliot', 'Karlsson', 19, 4),
('Stella', 'Lundberg', 20, 4),
('Alma', 'Magnusson', 21, 4),
('Matilda', 'Nilsson', 22, 5),
('Maja', 'Olsson', 23, 5),
('Ellen', 'Pettersson', 24, 5),
('Sofia', 'Rosén', 25, 6),
('Elin', 'Sjöberg', 26, 6),
('Freja', 'Törnqvist', 27, 6),
('Liam', 'Forsberg', 29, 7),
('Ella', 'Nyström', 30, 7),
('Noah', 'Lindqvist', 31, 7),
('Freja', 'Sundberg', 32, 8),
('Viktor', 'Ekström', 33, 8),
('Alva', 'Hedlund', 34, 8),
('Felix', 'Bergman', 35, 9),
('Saga', 'Ljunggren', 37, 9),
('Melvin', 'Nordström', 38, 9);







