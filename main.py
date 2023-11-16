# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import spacy
from langchain.llms import Ollama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from genetic_abnormalities import GeneticAbnormalities
import json
from json import JSONDecodeError
from sentence_transformers import SentenceTransformer, util
import csv
import math
from random import sample
from pathlib import Path
from datetime import datetime

nlp = spacy.load("en_core_sci_lg")
embedder = SentenceTransformer("allenai-specter", device="mps")
parser = PydanticOutputParser(pydantic_object=GeneticAbnormalities)
prompt = PromptTemplate(
    template="""You are an expert cancer pathologist and are working on very important medical research that can improve patients quality of life. Extract the specified information from any given pathology report using the following format.
    
    {format_instructions}
    
    Pathology report:
    {pathology_report}""",
    input_variables=["pathology_report"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)
system_prompt = """You are an expert cancer pathologist and are working on very important medical research that can improve patients quality of life. Extract the specified information from any given pathology report using the following response format. Use the example pathology report and example response as a guide.

### Response Format
{format_instructions}

### Example Pathology Report
|| Section:Cytogenetics Results Summary ||
Abnormal female complex karyotype showing previously reported abnormalities including the der(1;5) resulting in deletion of 5q, the add(17p) resulting in deletion of TP53 with new aberrations.    


|| Section:Cytogenetics Interpretation ||
A highly complex karyotype characterized by the der(1;5) resulting in deletion of 5q, the add(17p) resulting in the deletion of TP53, along with additional numerical and structural abnormalities, was observed in the diagnostic bone marrow sample  
(6/21/2022) and in two previous post-treatment bone marrow samples (7/25/2022, 8/29/2022). The add(6)(p21) and i(13q) were noted in two previous bone marrow samples (8/29/2022, 11/16/2022). The add(21p) noted in this sample could represent further  
karyotypic evolution. Clinical correlation is recommended.   
     
FISH analysis of this sample was positive for positive for deletion of the long arm of chromosome 5 (EGR1, 5q31, 91%), and deletion of TP53 (17p13.1, 93.5%) negative for loss of chromosome 5.

### Example Response
{{
	"genetic_abnormalities": [
		{{
			"name": "long arm chromosome 5 deletion (EGR1, 5q31)",
			"status": "POSITIVE",
			"percentage": 91
		}},
		{{
			"name": "TP53 deletion (17p13.1)",
			"status": "POSITIVE",
			"percentage": 93.5
		}},
		{{
			"name": "chromosome 5 loss",
			"status": "NEGATIVE",
			"percentage": null
		}}
	]
}}""".format(format_instructions=parser.get_format_instructions())


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
    return math.trunc((1 - abnormality["score"]) * sum([0.5 for token in nlp(abnormality["name"]) if token.is_stop]) * 1000)


def detect_best_match(abnormalities):
    return sorted(sorted(abnormalities, key=lambda a: a["span"].__len__(), reverse=True), key=composite_score)[0]


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    with open(f'data/results/aml_extract_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv', mode='w') as extract_file:
        extract_writer = csv.writer(extract_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        extract_writer.writerow(['Report Excerpt', 'Genetic Abnormality Name', 'Status', 'Percentage', 'Matched OG Phrase', 'Score'])
        for report in sample(list(Path('data/report_excerpts').glob('*.txt')), 10):  # list(Path('data/report_excerpts').glob('Fluorescence in situ hybridization_cerner_central_48700083.*'))
            print(report.stem)
            doc = nlp(open(report, 'r').read())
            duped_abnormalities = []
            for i in range(5):
                try:
                    model = Ollama(model="mistral", system=system_prompt, callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]), repeat_penalty=1.5, stop=["\n\n\n", "\n     "])
                    json_response = json.loads(model("Parse the following pathology report:\n" + doc.text))
                    print("\n")
                    genetic_abnormalities = json_response.get("genetic_abnormalities") or json_response.get("Genetic_Abnormalities") or json_response.get("GeneticAbnormalities") or json_response.get("geneticabnormalities") or json_response.get("GENETIC_ABNORMALITIES") or json_response.get("GENETICABNORMALITIES")
                    if type(genetic_abnormalities) == list and len(genetic_abnormalities) > 0 and type(genetic_abnormalities[0]) == dict:
                        name_key = 'Name' if 'Name' in genetic_abnormalities[0] else 'NAME' if 'NAME' in genetic_abnormalities[0] else 'name'
                        status_key = 'Status' if 'Status' in genetic_abnormalities[0] else 'STATUS' if 'STATUS' in genetic_abnormalities[0] else 'status'
                        percentage_key = 'Percentage' if 'Percentage' in genetic_abnormalities[0] else 'PERCENTAGE' if 'PERCENTAGE' in genetic_abnormalities[0] else 'percentage'

                        results, phrases = find_top_phrases(doc, [
                            f'{ga[name_key]} {ga.get(percentage_key)}%' if ga.get(percentage_key) else ga[name_key]
                            for ga in genetic_abnormalities])
                        for idx, ga in enumerate(genetic_abnormalities):
                            if results[idx][0]["score"] > 0.95:
                                unmatched = True
                                span = phrases[results[idx][0]["corpus_id"]]
                                location = range(span.start_char, span.end_char + 1)
                                abnormality = dict(**{"name": ga[name_key], "status": ga.get(status_key),
                                                      "percentage": ga.get(percentage_key)},
                                                   **{"span": phrases[results[idx][0]["corpus_id"]],
                                                      "score": results[idx][0]["score"]})
                                for da in duped_abnormalities:
                                    if len(range(max(location[0], da["location"][0]), min(location[-1], da["location"][-1]) + 1)) > min(len(location), len(da["location"]))/4 and (abnormality["percentage"] is None or da["abnormalities"][0]["percentage"] is None or abnormality["percentage"] == da["abnormalities"][0]["percentage"]):
                                        da["abnormalities"].append(abnormality)
                                        da.update({"location": range(min(location[0], da["location"][0]),
                                                                     max(location[-1], da["location"][-1]) + 1)})
                                        unmatched = False
                                if unmatched:
                                    duped_abnormalities.append({"location": location, "abnormalities": [abnormality]})
                except (KeyError, JSONDecodeError) as exception:
                    print(f'KeyError: {exception}')
                    continue
            for da in duped_abnormalities:
                abnormality = detect_best_match(da["abnormalities"])
                extract_writer.writerow(
                    [report.stem, abnormality["name"], abnormality["status"],
                     abnormality["percentage"],
                     abnormality["span"].text, abnormality["score"]])
            print(duped_abnormalities)
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
