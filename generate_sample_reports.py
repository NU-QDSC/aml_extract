import pandas as pd

data = pd.read_excel('data/cytogenetics_pathology_v4/AML Cytogenetic Pathology Cases.xlsx')
# bone_data = pd.read_excel('data/cytogenetic_fish_pathology_v3/AML Bone Marrow Pathology Cases Filtered by Aspirate Adequacy and NMH.xlsx')
# data = fish_data.loc[fish_data['west mrn'].isin(bone_data['nmhc mrn'])]

n = data.shape[0]
print(f'Processing {n} report excerpts for patients with adequate bone marrow aspirate sample')
filenames = (['data/report_excerpts_v4/'] * n) + data['snomed name'] + (['__'] * n) + data['source system'] + (
            ['__'] * n) + data['pathology case source system id'].astype('str') + (['.txt'] * n)
for index, note_text in data['note text'].items():
    with open(filenames[index], 'w') as f:
        f.write(note_text)
