"""
Main file for the CLI for Synthetic Image
Generator using Image Compositions
"""
import functions.foreground_extraction as fg_ex

def main():
    dir_path = './Data/Classes'
    ck = fg_ex.FgExtractor(dir_path,
            'ChromaKey', 'False')
    print(ck.print_settings())
    ck.prepare_folders()
    ck.extract_foregrounds()

if __name__ == '__main__':
    main()