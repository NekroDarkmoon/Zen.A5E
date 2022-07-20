cogs: list = []


tables: dict = {
    'feats': f'''
        name TEXT PRIMARY KEY,
        perquisite TEXT,
        description TEXT NOT NULL
    '''
}

indexes: list[str] = [
    'CREATE INDEX IF NOT EXISTS feats_name_trgm_idx ON feats USING GIN (name gin_trgm_ops)',
    'CREATE INDEX IF NOT EXISTS feats_name_lower_idx ON feats (LOWER(name))'
]
