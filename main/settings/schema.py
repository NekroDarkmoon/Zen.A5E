cogs: list = []


tables: dict = {
    'feats': f'''
        name TEXT PRIMARY KEY,
        perquisite TEXT,
        description TEXT NOT NULL
    '''
}

indexes: list = [
    # Tags
]
