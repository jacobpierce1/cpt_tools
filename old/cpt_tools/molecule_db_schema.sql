CREATE TABLE molecule_masses (
       mass REAL NOT NULL,
       Z TEXT NOT NULL,
       N TEXT NOT NULL,
       isomer_labels TEXT,
       molecule_name TEXT NOT NULL
);


-- allow for faster queries
CREATE INDEX mass_index on molecule_masses( mass );


CREATE TABLE metadata ( 
       min_cf_yield_fraction REAL NOT NULL,
       min_half_life REAL NOT NULL,
       small_molecule_size INTEGER NOT NULL,
       database_complete INTEGER NOT NULL,
       generation_time REAL NOT NULL,
       timestamp TEXT NOT NULL
 );
