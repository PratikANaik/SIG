"""
Main file for the CLI for Synthetic Image
Generator using Image Compositions
"""
import numbers
import functions.foreground_extraction as fg_ex
import functions.image_composer as im_co
import functions.annotator as annot
import os

def main():
    print(os.getcwd())
    res = (640,480)
    loc = ['Racket', 'Person', 'Pizza']
    ImgComp = im_co.ImgComposer(resolution=res,
                            classes_to_include=loc,
                            num_of_images=2,
                            max_objects_in_image=4,
                            output_directory='./Output/Composed',
                            efo_directory='./Output/EFObjects')
    ImgComp.compose()
    annot.annotate(image_dir='./Output/Composed',
        annotation_dir='./Output/Annotations',
        dataset_name='test')

if __name__ == '__main__':
    main()