
data/extracted_treatments-%.txt: extract_text.py resources/%.pdf
	mkdir -p data
	python $^ $@

TREATMENTS_FILES = data/extracted_treatments-Soh_and_Parnell-2015.txt \
						data/extracted_treatments-Ashton-2011.txt \
						data/extracted_treatments-Mustaqim-2023.txt \
						data/extracted_treatments-Merrill_and_Perry-1939.txt

extract_treatments: $(TREATMENTS_FILES)

data/extracted_treatments.txt: concat.py $(TREATMENTS_FILES)
	python $^ $@

all: data/extracted_treatments.txt

clean: 
	rm -r data