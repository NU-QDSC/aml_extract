# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import spacy
import llm
from sentence_transformers import SentenceTransformer, util
import csv
import math
from random import sample
from pathlib import Path
from datetime import datetime
import os

nlp = spacy.load("en_core_sci_lg")
embedder = SentenceTransformer("allenai-specter", device="mps")
model = llm.get_model("llama2-hermes")


def split_line(line):
    if len(cells := line.split('|')) < 2:
        cells = [row for row in csv.reader([line])][0]
    cells = [c.strip() for c in cells]
    return [c for c in cells]


def extract_genetic_abnormalities(text):
    response = model.prompt(text, system="""Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:
Detect the genetic abnormalities from the following pathology report. Respond in CSV format with the following columns: genetic_abnormality_name, status, percentage. For each genetic abnormality detected, respond as a new row with the name of the genetic abnormality. The status column refers to the presence of that specific genetic abnormality and should be POSITIVE if it is found or NEGATIVE if it is not detected. The percentage column should be filled in with the percentage of abnormal cells, but only if the information is available.

### Response:""")
    genetic_abnormalities = []
    header_index = {"genetic_abnormality_name": None, "status": None, "percentage": None}
    for line in response.text().splitlines():
        cells = split_line(line)
        if header_index["genetic_abnormality_name"] is None:
            lower_cells = [c.lower() for c in cells]
            header_index['genetic_abnormality_name'] = lower_cells.index(
                'genetic_abnormality_name') if 'genetic_abnormality_name' in lower_cells else lower_cells.index(
                'genetic abnormality name') if 'genetic abnormality name' in lower_cells else None
            header_index["status"] = lower_cells.index('status') if 'status' in lower_cells else None
            header_index["percentage"] = lower_cells.index('percentage') if 'percentage' in lower_cells else None
        else:
            try:
                row = {
                    "genetic_abnormality_name": cells[header_index['genetic_abnormality_name']],
                    "status": cells[header_index['status']],
                    "percentage": cells[header_index['percentage']].replace('%', '') if header_index['percentage'] is not None and header_index['percentage'] < len(cells) else None
                }
                if not row["genetic_abnormality_name"].replace('-', ''):
                    continue
                if row["percentage"]:
                    try:
                        row["percentage"] = float(row["percentage"])
                    except ValueError:
                        row["percentage"] = None
                genetic_abnormalities.append(row)
            except IndexError:
                break
    return response.text(), genetic_abnormalities


def find_top_phrases(spacy_doc, queries):
    query_lengths = [nlp(q).__len__() for q in queries]
    phrases = [spacy_doc[i:i + l] for l in range(min(query_lengths), max(query_lengths) + 11)
               for i in range(spacy_doc.__len__() - l + 1)]
    query_embeddings = util.normalize_embeddings(embedder.encode(queries, convert_to_tensor=True, device="mps"))
    phrase_embeddings = util.normalize_embeddings(embedder.encode([p.text for p in phrases],
                                                                  convert_to_tensor=True, device="mps"))
    results = util.semantic_search(query_embeddings=query_embeddings, corpus_embeddings=phrase_embeddings,
                                   score_function=util.dot_score)
    return results, phrases


def composite_score(abnormality):
    return math.trunc((1 - abnormality["score"]) * sum([0.5 for token in nlp(abnormality["genetic_abnormality_name"]) if token.is_stop]) * 1000)


def detect_best_match(abnormalities):
    return sorted(sorted(abnormalities, key=lambda a: a["span"].__len__(), reverse=True), key=composite_score)[0]


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # for report in list(Path('data/report_excerpts_v3').glob('?.txt')):
    for report in list(Path('data/report_excerpts_v3').glob('*.txt')):
        report_name = report.name
        report_name = report_name.replace('.txt', '')

        file_name = f'data/results/{report_name}.csv'
        file_exists = os.path.exists(file_name)
        if file_exists == True:
            print(f'File already exists: {file_name}')
        if file_exists == False:
            try:
                print(f'We have a new file: {file_name}')
                with open(file_name, mode='w') as extract_file:
                    extract_writer = csv.writer(extract_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    extract_writer.writerow(['Report Excerpt', 'Genetic Abnormality Name', 'Status', 'Percentage', 'Matched OG Phrase', 'Score'])
                    print(report.stem)
                    doc = nlp(open(report, 'r').read())
                    duped_abnormalities = []
                    for i in range(3):
                        try:
                            resp_text, genetic_abnormalities = extract_genetic_abnormalities(doc.text)
                            print(resp_text)
                            if len(genetic_abnormalities) > 0:
                                results, phrases = find_top_phrases(doc, [
                                    f'{ga["genetic_abnormality_name"]} {ga["percentage"]}%' if ga["percentage"] else ga["genetic_abnormality_name"]
                                    for ga in genetic_abnormalities])
                                for idx, ga in enumerate(genetic_abnormalities):
                                    if results[idx][0]["score"] > 0.95:
                                        unmatched = True
                                        span = phrases[results[idx][0]["corpus_id"]]
                                        location = range(span.start_char, span.end_char + 1)
                                        abnormality = dict(ga, **{"span": phrases[results[idx][0]["corpus_id"]],
                                                                  "score": results[idx][0]["score"]})
                                        for da in duped_abnormalities:
                                            if len(range(max(location[0], da["location"][0]), min(location[-1], da["location"][-1]) + 1)) > min(len(location), len(da["location"]))/4 and (abnormality["percentage"] is None or da["abnormalities"][0]["percentage"] is None or abnormality["percentage"] == da["abnormalities"][0]["percentage"]):
                                                da["abnormalities"].append(abnormality)
                                                da.update({"location": range(min(location[0], da["location"][0]),
                                                                             max(location[-1], da["location"][-1]) + 1)})
                                                unmatched = False
                                        if unmatched:
                                            duped_abnormalities.append({"location": location, "abnormalities": [abnormality]})
                        except KeyError as exception:
                            print(f'KeyError: {exception}')
                            continue
                    for da in duped_abnormalities:
                        abnormality = detect_best_match(da["abnormalities"])
                        extract_writer.writerow(
                            [report.stem, abnormality["genetic_abnormality_name"], abnormality["status"],
                             abnormality["percentage"],
                             abnormality["span"].text, abnormality["score"]])
                    print(duped_abnormalities)
            except KeyError as exception:
                print(f'Outside: KeyError: {exception}')
                continue
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
