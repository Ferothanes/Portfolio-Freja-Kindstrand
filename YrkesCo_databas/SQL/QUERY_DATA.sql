-- Each program should have multiple courses attached. 
-- What program has what courses?
SELECT P.Programnamn, K.Kursnamn
FROM Program P
JOIN ProgramKurs PK ON P.Program_id = PK.Program_id
JOIN Kurs K ON PK.Kurs_id = K.Kurs_id
ORDER BY P.Programnamn, K.Kursnamn;


-- Each utbildningsledare is in charge of 3 klasser
-- Which utbildningsledare is responsible for what klasser?
SELECT 
    UL.Fornamn, 
    UL.Efternamn, 
    K.Klassnamn
FROM UtbildningsLedare UL
JOIN Klass K ON UL.Utbildningsledare_id = K.Utbildningsledare_id
ORDER BY UL.Utbildningsledare_id;

-- Utbildningsledares personuppgifter
SELECT 
    UL.Fornamn, 
    UL.Efternamn, 
    P.Personnummer, 
    P.E_post
FROM UtbildningsLedare UL
JOIN Personuppgifter P ON UL.Personuppgifter_id = P.Personuppgifter_id;

-- What educators are consultants?
SELECT U.Konsult, U.Fornamn, U.Efternamn
FROM Utbildare U
WHERE U.Konsult = TRUE;

--Each program should have 3 klasses, 
--Which klasses are connected to what programs?
SELECT
    Klass.Klassnamn,
    Program.Programnamn
FROM
    Klass
JOIN
    Program ON Klass.Program_id = Program.Program_id;

-------------------------------------------------------------------------------------

-- What students belong to what class? - I've added 3 students to each class for now 
SELECT 
    s.Student_id, 
    s.Fornamn, 
    s.Efternamn, 
    k.Klassnamn
FROM Student s
JOIN Klass k ON s.Klass_id = k.Klass_id
ORDER BY k.Klassnamn, s.Student_id;

--What educator has what course?
SELECT 
    U.Fornamn, 
    U.Efternamn, 
    K.Kursnamn
FROM Utbildare U
JOIN Kurs K ON U.Utbildare_id = K.Utbildare_id;

-- How many points does each course have? and how long is it?
SELECT 
    Kursnamn, 
    antalveckor, 
    YHP, 
    Beskrivning
FROM Kurs
ORDER BY antalveckor DESC;


--What are the utbildares personuppgifter?
SELECT 
    U.Fornamn, 
    U.Efternamn, 
    P.Personnummer, 
    P.E_post
FROM Utbildare U
JOIN Personuppgifter P ON U.Personuppgifter_id = P.Personuppgifter_id;

-- What are the students personuppgifter, view with klassnamn?
SELECT 
    K.Klassnamn, 
    S.Fornamn, 
    S.Efternamn, 
    P.Personnummer, 
    P.E_post
FROM Student S
JOIN Personuppgifter P ON S.Personuppgifter_id = P.Personuppgifter_id
JOIN Klass K ON S.Klass_id = K.Klass_id
ORDER BY K.Klassnamn, S.Student_id;

-- Klassnamn och programnamn 
SELECT P.Programnamn, K.Klassnamn
FROM Program P
JOIN Klass K ON P.Program_id = K.Program_id
ORDER BY P.Program_id, K.Klassnamn;


-- Query information on spesific teacher
SELECT K.Kursnamn, U.Fornamn, U.Efternamn, P.E_post
FROM Utbildare U
JOIN Personuppgifter P ON U.Personuppgifter_id = P.Personuppgifter_id
JOIN Kurs K ON U.Utbildare_id = K.Utbildare_id
WHERE U.Fornamn = 'Kokchun';




