CREATE TABLE molecule_masses (
       A INTEGER,
       mass REAL NOT NULL,
       label TEXT NOT NULL
);


-- allow for fast queries
CREATE INDEX A_index on molecule_masses( A );


CREATE TABLE metadata ( 
       min_cf_yield_fraction REAL NOT NULL,
       min_half_life REAL NOT NULL,
       max_atoms_per_molecule INTEGER NOT NULL,
       database_complete INTEGER NOT NULL,
       generation_time REAL NOT NULL,
       timestamp TEXT NOT NULL
 );
