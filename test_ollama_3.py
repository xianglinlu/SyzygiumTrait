import argparse
import json
import ollama
import pandas as pd
import textwrap

# Ensure long text output is visible
pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_rows', None)

SYSTEM_MESSAGE = "You are an expert botanist. You can extract and encode data from text to JSON."

# Prompt with multiple examples
PROMPT ='''
    You are an expert botanist. You can extract and encode data 
    from text. You are supplied with the description of 
    species ("description"), and a output file name.
    Make a csv file containing all species's traits, separated by comma. 
    Do not fabricate data. 
    If you cannot score the variable, set the value to null. 
    Do not include any extra text. Do not generate columns that are not mention below. Follow the format of the  
    following examples.

    ### Example 1:
    description: "1. Syzygium acuminatissimum (Blume) DC. Plate 5B. (Latin, acuminatissimus = very pointed;"
    response: {{"species": "Syzygium acuminatissimum"}}


    ### Example 2:
    description: "
    Leaves often subopposite,  thinly leathery, drying dull pale brown ,   165 glistening above , not distinctly wrinkled , sparsely minutely pitted above, without dots or with minute scattered black dots beneath ;
    blades elliptic to occasionally lanceolate , (3.5â€“) 8â€“13  1.5â€“4 cm, base narrowly wedge-shaped tapering , apex acuminate , acumen c. 2 cm long, slender; 
    midrib not sharply angled beneath ; main lateral veins  unequal, c. 12 pairs , hardly or not furrowed above , distinctly raised beneath but slender, ascending, basal pair short; 
    intercostal venation visible throughout ; intramarginal veins close to margin , hardly looped; petioles c. 8 mm long , slender."
    response: {{
        "lamina length (range) cm": "'(3.5–)8–13",
        "lamina width (range) cm": "'1.5–4",
        "lamina shape": "elliptic to occasionally lanceolate",
        "base shape": "narrowly cuneate (wedge-shaped)",
        "apex shape": "acuminate (with slender 2 cm acumen)",
        "midrib": "not sharply angled beneath",
        "secondary venation": "~12 pairs, ascending, unequal, slender, raised beneath",
        "marginal vein": "intramarginal, close to margin, hardly looped",
        "petiole (range)": "~0.8 cm"

    }}

    ### Example 3:
    description: "
    Inflorescences paniculate, terminal or subterminal- axillary, to 6 cm long; rachis slender, 2â€“3x-branched."
    response: {{
      "infl. length (range) mm": "up to 60",
      "bract shape": "",
    }}

    ### Example 4:
    description: "
    Flowers bunched on the rachis branchlets; 
    buds club-shaped , to 5 mm long , to 3 mm diameter ; pseudostalk c. 3 mm long, slender; calyx lobes 4, broa dly hemispherical, cupped, deci duous; 
    stamens many, exserted to c. 4 mm long, anthers subglobose or broader than long, locules spreading from the base , end-porous; 
    style exserting to c. 4 mm long.  
    "
    response: {{
    "petal color": "",
    "total flower length": "'~8-9",
    "floral tube width at mid point mm": "",
    "floral tube shape": "",
    "pseudo-stalk length mm": "'3",
    "calyx lobe number": "'4",
    "calyx lobe nature": "broadly hemispherical, cupped, deciduous",
    "calyx lobe length mm": "'~1.5-2",
    "calyx lobe width mm": "'~2-3",
    "calyx lobe shape": "broadly hemispherical",
    "petal shape": "",
    "petal length mm": "",
    "petal width mm": "",
    "petal other": "",
    "stamen length mm": "up to 4",
    "anther dehiscence": "end-porous, locules spreading from base",
    "style length mm": "4",
    "placentation": "",
    }}

    ### Example 5:
    description: "
    Fruits c. 15 mm diameter, generally bilobed often misshapen, with minute raised cal yx-rim, ripening pinkish to purple. 
    Seeds with intrusive tissue interlocking the cotyledons 
"
    response: {{
    "Fruit shape": "generally bilobed, often misshapen",
    "Fruit length cm": "1.5",
    "Fruit width cm": "1.5",
    "Fruit texture": "minute raised calyx-rim",
    "nature of fruiting calyx": "persistent minute raised calyx-rim",
    "Fruit notes": "ripening pinkish to purple; generally bilobed, often misshapen; seeds with intrusive tissue interlocking cotyledons"
    }}
                         
    Generate the JSON for the following:\n
    description: {}\n
'''

def main():
    parser = argparse.ArgumentParser(description="Extracts qualitative traits")
    parser.add_argument('input_file', help="CSV file with taxon descriptions")
    parser.add_argument('output_file', help="Where to save the output")
    parser.add_argument('--model_name', default='llama3.3', help="Model name (default: llama3.3)")
    args = parser.parse_args()

    ollama_client = ollama.Client(host='http://127.0.0.1:13422')

    # Load input data
    df_treatment = pd.read_csv(args.input_file)
    print(f"Columns: {df_treatment.columns}")
    print(f"Total rows: {len(df_treatment)}")

    # Output dataframe
    df_output = pd.DataFrame()
    for _, row in df_treatment.iterrows():
        traits = {}
        description = row['line']
        chat_completion = ollama_client.chat(
        model=args.model_name,
        messages=[
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": PROMPT.format(description)}
        ],
        options={"temperature": 0},
        format="json"
        )
        output = chat_completion['message']['content']
        print(output)
        try:
            trait_dict = json.loads(output)
            traits.update(trait_dict)
        except json.JSONDecodeError:
            print(f"[ERROR]")
            print(output)

        df_taxon = pd.DataFrame([traits])
        df_output=pd.concat([df_output, df_taxon])
        print('-' * 60)

    df_output.to_csv(args.output_file, index=False, encoding="utf-8-sig")
    print(f"Output written to {args.output_file}")



if __name__ == "__main__":
    main()
