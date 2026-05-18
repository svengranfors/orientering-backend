-- =============================================
-- Orienteringsarrangören -- Databasschema
-- =============================================
-- Kör denna fil för att återskapa hela databasen från scratch.
-- Tabeller skapas i rätt ordning pga foreign key-beroenden.

-- Roller (huvudfunktionärer)
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    description TEXT
);

-- Tävlingar
CREATE TABLE competitions (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    competition_type VARCHAR NOT NULL,
    date DATE NOT NULL,
    organizer VARCHAR NOT NULL
);

-- Processmallar (knutna till tävlingstyp)
CREATE TABLE process_templates (
    id SERIAL PRIMARY KEY,
    competition_type VARCHAR NOT NULL,
    name VARCHAR NOT NULL,
    description TEXT,
    sort_order INTEGER NOT NULL DEFAULT 0,
    template_version INTEGER NOT NULL DEFAULT 1
);

-- Aktivitetsmallar (knutna till processmall och roll)
CREATE TABLE activity_templates (
    id SERIAL PRIMARY KEY,
    process_template_id INTEGER REFERENCES process_templates(id),
    role_id INTEGER REFERENCES roles(id),
    name VARCHAR NOT NULL,
    description TEXT,
    default_due_offset_days INTEGER,
    is_required BOOLEAN NOT NULL DEFAULT true,
    sort_order INTEGER NOT NULL DEFAULT 0
);

-- Tillsättningar (person i roll för specifik tävling)
CREATE TABLE assignments (
    id SERIAL PRIMARY KEY,
    competition_id INTEGER REFERENCES competitions(id),
    role_id INTEGER REFERENCES roles(id),
    person_name VARCHAR NOT NULL
);

-- Tävlingsprocesser (instanser av processmallar per tävling)
CREATE TABLE competition_processes (
    id SERIAL PRIMARY KEY,
    competition_id INTEGER REFERENCES competitions(id),
    process_template_id INTEGER REFERENCES process_templates(id),
    status VARCHAR NOT NULL DEFAULT 'not_started',
    progress INTEGER NOT NULL DEFAULT 0
);

-- Aktiviteter (instanser av aktivitetsmallar per tävlingsprocess)
CREATE TABLE activities (
    id SERIAL PRIMARY KEY,
    competition_process_id INTEGER REFERENCES competition_processes(id),
    activity_template_id INTEGER REFERENCES activity_templates(id),
    assignment_id INTEGER REFERENCES assignments(id) NULL,
    status VARCHAR NOT NULL DEFAULT 'not_started',
    priority VARCHAR NOT NULL DEFAULT 'normal',
    due_date DATE,
    completed_at TIMESTAMPTZ,
    blocked_by_activity_id INTEGER REFERENCES activities(id) NULL,
    notes TEXT
);

-- =============================================
-- Behörigheter (Supabase anon-användare)
-- =============================================
GRANT SELECT, INSERT, UPDATE, DELETE ON public.roles TO anon;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.competitions TO anon;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.process_templates TO anon;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.activity_templates TO anon;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.assignments TO anon;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.competition_processes TO anon;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.activities TO anon;

GRANT USAGE, SELECT ON SEQUENCE roles_id_seq TO anon;
GRANT USAGE, SELECT ON SEQUENCE competitions_id_seq TO anon;
GRANT USAGE, SELECT ON SEQUENCE process_templates_id_seq TO anon;
GRANT USAGE, SELECT ON SEQUENCE activity_templates_id_seq TO anon;
GRANT USAGE, SELECT ON SEQUENCE assignments_id_seq TO anon;
GRANT USAGE, SELECT ON SEQUENCE competition_processes_id_seq TO anon;
GRANT USAGE, SELECT ON SEQUENCE activities_id_seq TO anon;

-- =============================================
-- RLS-policies (Row Level Security)
-- =============================================
CREATE POLICY "Allow all for anon" ON public.roles
FOR ALL TO anon USING (true) WITH CHECK (true);

CREATE POLICY "Allow all for anon" ON public.competitions
FOR ALL TO anon USING (true) WITH CHECK (true);

CREATE POLICY "Allow all for anon" ON public.process_templates
FOR ALL TO anon USING (true) WITH CHECK (true);

CREATE POLICY "Allow all for anon" ON public.activity_templates
FOR ALL TO anon USING (true) WITH CHECK (true);

CREATE POLICY "Allow all for anon" ON public.assignments
FOR ALL TO anon USING (true) WITH CHECK (true);

CREATE POLICY "Allow all for anon" ON public.competition_processes
FOR ALL TO anon USING (true) WITH CHECK (true);

CREATE POLICY "Allow all for anon" ON public.activities
FOR ALL TO anon USING (true) WITH CHECK (true);

-- =============================================
-- Grunddata -- Huvudfunktionärer
-- =============================================
INSERT INTO roles (name, description) VALUES
('Tävlingsledare', 'Ansvarar för tävlingens övergripande genomförande och leder ledningsgruppen'),
('Banläggare', 'Ansvarar för banlägning och kartor'),
('Arenaansvarig', 'Ansvarar för arenan och publikområdet'),
('IT/Resultat/Sekretariat', 'Ansvarar för tidtagning, resultathantering och sekretariat'),
('Startchef', 'Ansvarar för startfunktionen'),
('Funktionärsansvarig', 'Ansvarar för rekrytering och samordning av funktionärer'),
('Markägare-/myndighetskontakter', 'Ansvarar för kontakter med markägare och myndigheter');