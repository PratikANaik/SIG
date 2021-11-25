"""
Main file for the CLI for Synthetic Image
Generator using Image Compositions
"""
import functions.foreground_extraction as fg_ex

def main():
    dir_path = '/home/pratikan/Synthetic_Image_Generation/SIG/Data/Classes'
    ck = fg_ex.FgExtractor(dir_path,
            'ChromaKey', 'False')
    ck.print_settings()
    ck.extract_foregrounds()

if __name__ == '__main__':
    main()