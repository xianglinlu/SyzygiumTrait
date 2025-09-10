import argparse
import pandas as pd

def main():
    parser = argparse.ArgumentParser(description="Concatenate multiple files into one output file.")
    
    # All but the last argument: input files
    parser.add_argument("input_files", nargs="+", help="List of input files to concatenate")
    
    # Last argument: output file
    parser.add_argument("output_file", help="Output file")

    args = parser.parse_args()

    # Just to show parsing worked
    print("Input files:", args.input_files)  
    print("Output file:", args.output_file)  

    for input_file in args.input_files:
        print(f"Processing file: {input_file}")
        df = pd.read_csv(input_file, encoding="utf-8-sig")
        print(df)
        if input_file == args.input_files[0]:
            df_all = df
        else:
            df_all = pd.concat([df_all, df], ignore_index=True)

    print("Combined DataFrame:")
    print(df_all)
    df_all.to_csv(args.output_file, encoding="utf-8-sig", index=False)
    
if __name__ == "__main__":
    main()
