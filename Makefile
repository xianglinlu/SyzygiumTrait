
data/extracted_treatments.txt: extract_text.py resources/Soh_and_Parnell-2015.pdf
	mkdir -p data
	python $^ $@

extract_treatments: data/extracted_treatments.txt

clean: 
	rm -r data