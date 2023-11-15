import pandas as pd
import pathlib

sheets = pathlib.Path('data/cytogenetic_fish_pathology').glob('*.xlsx')
for sheet in sheets:
    print('Processing:', sheet)
    data = pd.read_excel(sheet)

    n = data.shape[0]
    filenames = (['data/report_excerpts/'] * n) + data['snomed name'] + (['_'] * n) + data['source system'] + (
                ['_'] * n) + data['pathology case source system id'].astype('str') + (['.txt'] * n)
    for index, note_text in data['note text'].items():
        with open(filenames[index], 'w') as f:
            f.write(note_text)
