from pypdf import PdfReader
import argparse
import pandas as pd
import re

def extractSyzygiumSpeciesName(s):
    """
    Extract species name from a line that starts a Syzygium taxonomic treatment.
    Looks for 'Syzygium' followed by one Latin species epithet.
    """
    speciesName = None
    if s is not None:
        # Match lines starting with "Syzygium" followed by a lowercase species epithet
        patt = r'^[0-9]+\.\s(Syzygium\s+[a-z\-]+).*$'
        m = re.match(patt, s).group(1)
        if m is not None:
            speciesName = m
    return speciesName



def identifyTreatments(df):
    # Define regular expression patterns to find the start lines of taxon treatments
    species_treatment_patt = r'^[0-9]+\.\s(Syzygium\s+[a-z\-]+).*$'

    # Make a new column to hold the taxon_id_and_name
    df['taxon_id_and_name']=[None]*len(df)
    #  As we're using filldown, we want to set the endpoint after the taxon
    # treatments. This prevents the last taxon treatment being filled down right
    # to the end of the article
    mask=(df.line.str.match(r'^INCOMPLETELY KNOWN SPECIES\s*$'))
    df.loc[mask, 'taxon_id_and_name'] = 'na'

    # As above - find the lines which indicate the start of an species treatment
    mask=(df.line.str.match(species_treatment_patt, case=True, flags=0, na=None))
    # Use the utility function to extract the taxon name and number from the text
    # of the line
    mask = (df.taxon_id_and_name.isnull() & mask)
    df.loc[mask, 'taxon_id_and_name'] = df[mask].line.apply(extractSyzygiumSpeciesName)

    # Fill down the taxon name and number values
    df.taxon_id_and_name = df.taxon_id_and_name.ffill()

    mask = (df.taxon_id_and_name.notnull() & (df.taxon_id_and_name.isin(['na']) == False))
    df.loc[mask,'taxon_id'] = df[mask].taxon_id_and_name.apply(lambda x: x.split(' ', maxsplit=1)[0])
    df.loc[mask,'taxon_name'] = df[mask].taxon_id_and_name.apply(lambda x: x.split(' ', maxsplit=1)[1])

    return df


def main():
    # Open the PDF file for reading
    parser = argparse.ArgumentParser(description="Extracts qualitative traits")
    parser.add_argument('input_file', help="PDF file of monograph and literature")
    parser.add_argument('output_file', help="Where to save the output")
    args = parser.parse_args()
    reader= PdfReader(args.input_file)

    # Extract pages and store with their page number in a dictionary
    pages = dict()
    for i, page in enumerate(reader.pages):
        page_number = page.page_number + 1
        page_text = page.extract_text()
        pages[page_number] = page_text

    # Make a dataframe from the pages dictionary
    df_pages = pd.DataFrame(data={'page_number':pages.keys(),'page_text':pages.values()})

    print(df_pages)


    # Make a new column which holds the individual lines in each page
    # First as a list of lines
    df_pages['line'] = df_pages['page_text'].apply(lambda x: x.split('\n'))
    # Now "explode" the list of lines so that each line is in its own row
    # in the dataframe
    df_lines = df_pages.explode('line')
    # page text can be dropped as no longer needed
    df_lines.drop(columns=['page_text'],inplace=True)
    
    df_lines = identifyTreatments(df_lines)
    df_treatments = df_lines.groupby('taxon_id_and_name') ['line'].agg(' '.join).reset_index()


    # Display the result
    print(df_treatments)
    print(type(df_treatments))
    df_treatments.to_csv(args.output_file, encoding="utf-8-sig")

if __name__ == "__main__":
    main()
