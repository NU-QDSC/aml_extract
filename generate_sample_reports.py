import pandas
import pathlib

RELEVANT_SECTIONS = [
    'Comments',
    'Interpretation',
    'Results'
]


def combine_section_name_with_note_text(row):
    if not row['section description'] or not row['note text']:
        return None
    else:
        return row['section description'] + ':\n' + row['note text']


sheets = pathlib.Path('data/cytogenetic_fish_pathology').glob('*.xlsx')
for sheet in sheets:
    data = pandas.read_excel(sheet)
    data['note text with section'] = data.apply(combine_section_name_with_note_text, axis=1)
    for report_identifier in data['pathology stable identifier value 1'].unique():
        sections = data.loc[(data['pathology stable identifier value 1'] == report_identifier) & (
            data['section description'].isin(RELEVANT_SECTIONS)) & (data['note text with section'] is not None)]
        if sections.shape[0] > 0:
            with open(f'data/sample_reports/{report_identifier}.txt', 'w') as f:
                f.write('\n\n'.join(sections['note text with section']))
