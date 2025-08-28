# SyzygiumTrait

## Overview
Floristic accounts require a combination of understanding the works of previous taxonomists, interpreted in light of new specimens or specimens from an area for which a new flora is being prepared. The output of this research is trait data that in the digital age is typically compiled as a database. 
However, it’s always exhausting and time-consuming for scientists to extract trait information of species from extensive articles and monographs. It would be helpful if there’s a tool that can extract, even organize this biological information automatically. 
In the era of AI, it’s possible to deal with this issue with LLM. We want to design a tool, or a universal prompt, that can organize existing descriptions into an Excel spreadsheet, to act as a baseline for taxonomic review alongside examination of additional specimens and new trait information. 
Kew Science is committed to assemble Floristic accounts of Syzygium for several southeast Asian regional Floras. This project uses digitally available taxonomic literature and Large Language Models to mobilise trait data for its use in preparation of the Flora of Singapore.

## Timeline
July 2025: Amy Fiddes and Nicky Nicolson just finished a similar project “CalamusTraits”, exploring how to use LLMs to transition between trait matrices and textual descriptions of Calamus species, with the aim of speeding up the taxonomic process. 

Fig. flow chart of CalamusTraits’ extraction part
Fig is a simplified flow chart to explain how Amy and Nicky extract and structure the information of Calamus. 
Literature Sources
The original list of species for treating in the Flora of Singapore was taken from {eve to add the paper}. 33 of these species have descriptions in two floristic accounts, these are A revision of Syzygium [Sol and Parnell. 2015.] & Tree Flora of Sabah and Sarawak [Soepadmo et al. 2011.] Protologues were accessed from the biodiversity heritage library (BHL). 
Process
The processing LLM is OLLAMA; we also experimented with chatGPT pro (medium level)
We took part of the Calamus script as a prototype and further modified it to fit in our material, hoping to meet universal needs, not just specific for one type of article or genus. The original Calamus code is highly fitted for the Calamus monograph [Henderson. 2020]. The Calamus monograph is unusual as it includes an extensive appendix (a trait matrix) with value ranking standard for each trait. Our literature resources do not include these elements. As a result our workflow had fewer steps, as we only extracted the pure text and used the LLM to split it and fill it into corresponding cells. 
In this project I modified the Calamus code. I deleted all functions that were too specific for the input files, preventing hard-coding. I also rewrote the prompt. The original prompt linked to custom made dictionaries for each trait (according to the matrices). Instead, my prompt returns the original content of the literature word for word (verbatim). 

How to Run the Scripts
The scripts require connection to a LLM on a HPC cluster. Follow these instructions for installation LLM install on HPC
The following instructions assume that you have cloned the repository to a machine where you have: (a) a local installation of Python, (b) the build tool make and (c) a command line terminal program to run the following commands:
Set up a virtual environment: python -m venv env and activate it: source env/Scripts/activate
Install the libraries: pip install -r requirements.txt
Copy your source PDF to the directory, simplify the file name (eg. Syzygium.pdf)
In the directory, run the extraction script:  python extract_text.py SOURCE_FILE_NAME.pdf EXTRACTED_TEXT_FILE_NAME.csv 
This step extract texts in pdf and list them line by line to one csv file
Open an editor, modify the PROMPT section in run_ollama.py to meet your demand, and save it.
Connect to HPC ( LLM install on HPC )
In the directory, run the ollama executive script:  python run_ollama.py EXTRACTED_TEXT_FILE_NAME.csv OUTPUT_FILE_NAME.csv
This step use LLM to organize species’ information automatically.


Tip: use the --model_name option to run the scripts with a different ollama model. Default is set to llama3.3

Result
Automatically ignore unrelated content
CalamusTrait cleaned up all of the unrelated content (footer, header, caption etc). However, in this project, we tried to delete the function because it’s too specific for different materials. 
It turns out that, though the input text is not pure enough, OLLAMA can recognize the main points of description and extract them well.
Transform unit

Same prompt, but ChatGPT doesn’t work.
We put the same prompt into ChatGPT, and the result 
Coverage/Accuracy
Discussion/notes/comments
Problems with chatGPT
Anything else
The results have not been fully manually validated
Errors may exist due to LLM extraction or source inconsistencies
Future work should include thorough validation and integration with curated biodiversity databases
