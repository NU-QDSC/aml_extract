import pandas as pd
import pathlib

sheets = pathlib.Path('data/cytogenetic_fish_pathology').glob('*.xlsx')
for sheet in sheets:
    print('Processing:', sheet)
    data = pd.read_excel(sheet)

    for index, row in data.iterrows():
        source_system = row['source system']
        snomed_name = row['snomed name']
        note_text = row['note text']
        pathology_case_source_system_id = row['pathology case source system id']

        # Construct a unique filename for each row
        filename = f'data/sample_reports/{snomed_name}_{source_system}_{pathology_case_source_system_id}.txt'

        with open(filename, 'w') as f:
            f.write(note_text)
