TREATMENTS_FILES = data/extracted_treatments-Soh_and_Parnell-2015.txt \
						data/extracted_treatments-Ashton-2011.txt \
						data/extracted_treatments-Mustaqim-2023.txt \
						data/extracted_treatments-Merrill_and_Perry-1939.txt

data/extracted_treatments-%.txt: extract_text.py resources/%.pdf
	mkdir -p data
	python $^ $@

data/extracted_treatments.txt: concat.py $(TREATMENTS_FILES)
	python $^ $@

extract_treatments: $(TREATMENTS_FILES)

TRAITS_FILES = data/extracted_traits-Soh_and_Parnell-2015.txt \
						data/extracted_traits-Ashton-2011.txt \
						data/extracted_traits-Mustaqim-2023.txt \
						data/extracted_traits-Merrill_and_Perry-1939.txt

data/extracted_traits-%.txt: run_ollama.py data/extracted_treatments-%.txt
	mkdir -p data
	python $^ $@


data/extracted_traits.txt: concat.py $(TRAITS_FILES)
	python $^ $@

extract_traits: $(TRAITS_FILES)

all: data/extracted_treatments.txt data/extracted_traits.txt

clean: 
	rm -r data