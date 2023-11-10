import pandas
import pathlib


CYTOGENETICS_RELEVANT_SECTIONS = [
    'Final Diagnosis',
    'Addendum',
    'Comment'
]


FISH_RELEVANT_SECTIONS = [
    'FISH Results',
    'Addendum',
    'Comments',
    'Interpretation',
    'Cytogenetics Amendment/Addendum',
    'Cytogenetics Interpretation',
    'Cytogenetics Results Summary'
]


def combine_section_name_with_note_text(row):
    if not row['section description'] or not row['note text']:
        return None
    else:
        return row['section description'] + ':\n' + row['note text']

sheets = pathlib.Path('data/cytogenetic_fish_pathology').glob('*.xlsx')
for sheet in sheets:
    print('hello booch')
    print(sheet)
    data = pandas.read_excel(sheet)
    data['note text with section'] = data.apply(combine_section_name_with_note_text, axis=1)
    for report_identifier in data['pathology stable identifier value 1'].unique():
        relevant_sections = []
        snomed_name = data['snomed name'].iloc[0]
        if snomed_name == 'Cytogenetic procedure':
            relevant_sections = CYTOGENETICS_RELEVANT_SECTIONS
        elif snomed_name == 'Fluorescence in situ hybridization':
            relevant_sections = FISH_RELEVANT_SECTIONS
        sections = data.loc[(data['pathology stable identifier value 1'] == report_identifier) & (
            data['section description'].isin(relevant_sections)) & (data['note text with section'] is not None)]
        if sections.shape[0] > 0:
            with open(f'data/sample_reports/{report_identifier}.txt', 'w') as f:
                f.write('\n\n'.join(sections['note text with section']))
