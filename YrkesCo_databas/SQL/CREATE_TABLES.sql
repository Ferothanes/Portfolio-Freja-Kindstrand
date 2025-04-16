-- Table: Personuppgifter
CREATE TABLE Personuppgifter (
    Personuppgifter_id SERIAL PRIMARY KEY NOT NULL,
    Personnummer CHAR(12) NOT NULL UNIQUE,
    E_post VARCHAR(255) NOT NULL UNIQUE
);

-- Table: Adress
CREATE TABLE Adress (
    Adress_id SERIAL PRIMARY KEY NOT NULL,
    Gatuadress VARCHAR(100) NOT NULL,
    Postnummer CHAR(10),
    Stad VARCHAR(50) NOT NULL,
    Land VARCHAR(50) NOT NULL
);

-- Table: KonsultForetag
CREATE TABLE KonsultForetag (
    KonsultF_id SERIAL PRIMARY KEY NOT NULL,
    Foretagsnamn VARCHAR(100) NOT NULL,
    Org_nr VARCHAR(12) NOT NULL UNIQUE,
    F_skatt BOOLEAN NOT NULL,
    Adress_id INT NOT NULL,
    FOREIGN KEY (Adress_id) REFERENCES Adress(Adress_id) ON DELETE CASCADE  -- Deleting a KonsultFöretag will delete its address
);

-- Table: Anlaggning
CREATE TABLE Anlaggning (
    Anlaggning_id SERIAL PRIMARY KEY NOT NULL,
    Adress_id INT NOT NULL,
    FOREIGN KEY (Adress_id) REFERENCES Adress(Adress_id) ON DELETE CASCADE  -- Deleting a Anläggning will delete its address
);

-- Table: Program
CREATE TABLE Program (
    Program_id SERIAL PRIMARY KEY NOT NULL,
    Programnamn VARCHAR(100) NOT NULL,
    Anlaggning_id INT NOT NULL,
    FOREIGN KEY (Anlaggning_id) REFERENCES Anlaggning(Anlaggning_id) ON DELETE CASCADE  
);

-- Table: UtbildningsLedare
CREATE TABLE UtbildningsLedare (
    Utbildningsledare_id SERIAL PRIMARY KEY NOT NULL,
    Fornamn VARCHAR(50) NOT NULL,
    Efternamn VARCHAR(50) NOT NULL,
    Personuppgifter_id INT NOT NULL UNIQUE, -- One-to-One cardinality with personuppgifter, we add UNIQUE to ensure only one related record exists. 
    Konsult_id INT,
    Konsult BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (Personuppgifter_id) REFERENCES Personuppgifter(Personuppgifter_id) ON DELETE CASCADE,  -- Deleting an UtbildningsLedare will delete the associated Personuppgifter
    FOREIGN KEY (Konsult_id) REFERENCES Konsult(Konsult_id)
);

-- Table: Utbildare
CREATE TABLE Utbildare (
    Utbildare_id SERIAL PRIMARY KEY NOT NULL,
    Fornamn VARCHAR(50) NOT NULL,
    Efternamn VARCHAR(50) NOT NULL,
    Personuppgifter_id INT NOT NULL UNIQUE, -- One-to-One cardinality, we add UNIQUE to ensure only one related record exists. 
    Konsult_id INT,
    Konsult BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (Personuppgifter_id) REFERENCES Personuppgifter(Personuppgifter_id) ON DELETE CASCADE, -- Deleting an Utbildare will delete associated Personuppgifter
    FOREIGN KEY (Konsult_id) REFERENCES Konsult(Konsult_id) 
);

-- Table: Konsult
CREATE TABLE Konsult (
    Konsult_id SERIAL PRIMARY KEY NOT NULL,
    Fornamn VARCHAR(50) NOT NULL,
    Efternamn VARCHAR(50) NOT NULL,
    KonsultF_id INT NOT NULL,
    ArvodePerTimme DECIMAL(10, 2) NOT NULL,  -- allows for up to 10 digits, with 2 decimal places
    FOREIGN KEY (KonsultF_id) REFERENCES KonsultForetag(KonsultF_id) 
);

-- Table: Student
CREATE TABLE Student (
    Student_id SERIAL PRIMARY KEY NOT NULL,
    Fornamn VARCHAR(50) NOT NULL,
    Efternamn VARCHAR(50) NOT NULL,
    Personuppgifter_id INT NOT NULL UNIQUE, -- One-to-One cardinality, we add UNIQUE to ensure only one related record exists. 
    Klass_id INT NOT NULL, 
    FOREIGN KEY (Personuppgifter_id) REFERENCES Personuppgifter(Personuppgifter_id) ON DELETE CASCADE, -- Deleting an Student will delete associated Personuppgifter
    FOREIGN KEY (Klass_id) REFERENCES Klass(Klass_id)
);

-- Table: Klass
CREATE TABLE Klass (
    Klass_id SERIAL PRIMARY KEY NOT NULL,
    Klassnamn VARCHAR(50) NOT NULL,
    Program_id INT NOT NULL,
    Utbildningsledare_id INT NOT NULL,
    FOREIGN KEY (Program_id) REFERENCES Program(Program_id),
    FOREIGN KEY (Utbildningsledare_id) REFERENCES UtbildningsLedare(Utbildningsledare_id) 
);

-- Table: Kurs
CREATE TABLE Kurs (
    Kurs_id SERIAL PRIMARY KEY NOT NULL,
    Kursnamn VARCHAR(100) NOT NULL,
    Kurskod VARCHAR(10) NOT NULL UNIQUE,
    YHP INT NOT NULL,
    Beskrivning VARCHAR (255),
    Utbildare_id INT NOT NULL,
    FOREIGN KEY (Utbildare_id) REFERENCES Utbildare(Utbildare_id),
    AntalVeckor INT (2)
);

-- Table: ProgramKurs
CREATE TABLE ProgramKurs (
    Program_id INT NOT NULL,
    Kurs_id INT NOT NULL,
    PRIMARY KEY (Program_id, Kurs_id), -- composite primary key (program_id & kurs_id)
    FOREIGN KEY (Program_id) REFERENCES Program(Program_id),
    FOREIGN KEY (Kurs_id) REFERENCES Kurs(Kurs_id) 
);

