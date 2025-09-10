from pypdf import PdfReader
import argparse
import pandas as pd
import re

TREATMENT_START_PATTERN_NUMBERED = r'^\s*[0-9]+\.\s(Syzygium\s+[a-z\-]+).*$'
# An un-numbered species treatement will have a binomial starting the line
# followed by a space and an opening bracket for a parenthetical author citation
# or a simple author citation
TREATMENT_START_PATTERN_UNNUMBERED = r'^\s*(Syzygium\s+[a-z\-]+)\s+\(.*\).*$|^\s*(Syzygium\s+[a-z\-]+)\s+[A-Z].*$'

def extractSyzygiumSpeciesName(s, speciesAccountsNumbered=True):
    """
    Extract species name from a line that starts a Syzygium taxonomic treatment.
    Looks for 'Syzygium' followed by one Latin species epithet.
    """
    speciesName = None
    if s is not None:
        # Match lines starting with "Syzygium" followed by a lowercase species epithet
        patt = TREATMENT_START_PATTERN_UNNUMBERED
        if speciesAccountsNumbered:
            patt = TREATMENT_START_PATTERN_NUMBERED
        m = re.match(patt, s).group(1)
        if m is not None:
            speciesName = m
    return speciesName



def identifyTreatments(df, speciesAccountsNumbered=True):
    # Define regular expression patterns to find the start lines of taxon treatments
    species_treatment_patt = TREATMENT_START_PATTERN_UNNUMBERED
    if speciesAccountsNumbered:
        species_treatment_patt = TREATMENT_START_PATTERN_NUMBERED

    # Make a new column to hold the taxon_id_and_name
    df['taxon_id_and_name']=[None]*len(df)
    #  As we're using filldown, we want to set the endpoint after the taxon
    # treatments. This prevents the last taxon treatment being filled down right
    # to the end of the article
    mask=(df.line.str.match(r'^INCOMPLETELY KNOWN SPECIES\s*$'))
    df.loc[mask, 'taxon_id_and_name'] = 'na'

    # As above - find the lines which indicate the start of an species treatment
    mask=(df.line.str.match(species_treatment_patt, case=True, flags=0, na=None))
    print(df[mask][['page_number','line']])
    # Use the utility function to extract the taxon name and number from the text
    # of the line
    mask = (df.taxon_id_and_name.isnull() & mask)
    df.loc[mask, 'taxon_id_and_name'] = df[mask].line.apply(extractSyzygiumSpeciesName, speciesAccountsNumbered=speciesAccountsNumbered)

    
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

    # Get the filename part of the input file using os filename
    import os
    input_filename = os.path.basename(args.input_file)
    print(f"Input file: {input_filename}")

    # Extract pages and store with their page number in a dictionary
    pages = dict()

    for i, page in enumerate(reader.pages):
        if i ==0:
            continue  # Skip the first page
        page_number = page.page_number + 1
        page_text = page.extract_text()
        try:
            print(page_text)
        except:
            print(f"Could not print page {page_number}")
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
    
    # Determine if the literature contains numbered species accounts
    speciesAccountsNumbered = bool(re.search(r'^\s*[0-9]+\.\s*Syzygium\s+[a-z\-]+.*$', df_lines.line.str.cat(sep='\n'), flags=re.MULTILINE))
    print(f"Species accounts numbered: {speciesAccountsNumbered}")

    df_lines = identifyTreatments(df_lines, speciesAccountsNumbered=speciesAccountsNumbered)
    df_treatments = df_lines.groupby('taxon_id_and_name') ['line'].agg(' '.join).reset_index()


    # Display the result
    print(df_treatments)
    print(type(df_treatments))
    df_treatments['source_file'] = input_filename
    df_treatments[['source_file', 'taxon_id_and_name', 'line']].to_csv(args.output_file, encoding="utf-8-sig",index=False)

if __name__ == "__main__":
    main()
