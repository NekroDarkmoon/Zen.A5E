cogs: list = []


tables: dict = {
    'feats': f'''
        name TEXT PRIMARY KEY,
        perquisite TEXT,
        description TEXT NOT NULL,
        type TEXT
    ''',

    'conditions': f'''
        name TEXT PRIMARY KEY,
        description TEXT NOT NULL
    ''',

    'maneuvers': f'''
        name TEXT PRIMARY KEY,
        description TEXT NOT NULL,
        extra JSON DEFAULT '{{}}'::jsonb
    ''',

    'spells': f'''
        name TEXT PRIMARY KEY,
        description TEXT NOT NULL,
        type TEXT,
        extra JSON DEFAULT '{{}}'::jsonb
    '''
}

indexes: list[str] = [
    'CREATE INDEX IF NOT EXISTS feats_name_trgm_idx ON feats USING GIN (name gin_trgm_ops)',
    'CREATE INDEX IF NOT EXISTS feats_name_lower_idx ON feats (LOWER(name))'
]
