import pandas as pd
import pathlib

sheets = pathlib.Path('data/cytogenetic_fish_pathology').glob('*.xlsx')
for sheet in sheets:
    print('Processing:', sheet)
    data = pd.read_excel(sheet, converters = {'west mrn': str})

    n = data.shape[0]
    filenames = (['data/report_excerpts/'] * n) + data['west mrn'].astype('str') + (['__'] * n) + data['snomed name'] + (['__'] * n) + data['source system'] + (
                ['__'] * n) + data['pathology case source system id'].astype('str') + (['.txt'] * n)
    for index, note_text in data['note text'].items():
        with open(filenames[index], 'w') as f:
            f.write(note_text)
