""" Create a Prediction File from a Manifest for a Model to
    Generate Predictions
"""
import json
import os
import csv
import argparse

from utils import file_path_splitter, file_path_generator

#For Testing
# args = dict()
# args['manifest'] = "/home/packerc/shared/zooniverse/Manifests/KAR/KAR_S1__manifest__complete.json"
# args['machine_learning_file'] = "/home/packerc/shared/zooniverse/Manifests/KAR/KAR_S1_machine_learning_input.csv"
# args['max_images_per_capture'] = 3

if __name__ == "__main__":

    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest", type=str, required=True,
        help="Path to manifest file (.json)")
    parser.add_argument(
        "--machine_learning_file", type=str, default=None,
        help="Input file for the model to create predictions for (.csv). \
              Default is to create a file X_machine_learning_input.csv in\
              the manifest directory.")
    parser.add_argument(
        "--max_images_per_capture", type=int, default=3,
        help="The maximum number of images per capture event (default 3)")

    args = vars(parser.parse_args())

    for k, v in args.items():
        print("Argument %s: %s" % (k, v))

    # Check Inputs
    if not os.path.exists(args['manifest']):
        raise FileNotFoundError("manifest: %s not found" %
                                args['manifest'])

    # Create / Check path of prediction file
    if args['machine_learning_file'] is None:
        file_name_parts = file_path_splitter(args['manifest'])
        args['machine_learning_file'] = file_path_generator(
            dir=os.path.dirname(args['manifest']),
            id=file_name_parts['id'],
            batch=file_name_parts['batch'],
            name='machine_learning_input',
            file_delim=file_name_parts['file_delim'],
            file_ext='csv'
        )
        print("Machine learning file is %s" % args['machine_learning_file'])
    else:
        output_dir = os.path.dirname(args['machine_learning_file'])
        if not os.path.isdir(output_dir):
            raise FileNotFoundError(
                "Path to store predictions: %s is not a dir" % output_dir)

    # Read the Manifest
    with open(args['manifest'], 'r') as f:
        manifest = json.load(f)

    print("Found %s capture events in %s" %
          (len(manifest.keys()), args['manifest']))

    print("Writing file to %s" % args['machine_learning_file'])
    with open(args['machine_learning_file'], 'w') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        # write header
        n_images = args['max_images_per_capture']
        image_cols = ['image%s' % x for x in range(1,  n_images + 1)]
        header = ['capture_id'] + image_cols
        csvwriter.writerow(header)
        # Write each capture event and the associated images
        for capture_id, mani_data in manifest.items():
            row_to_write = [capture_id]
            images_to_write = ['' for i in range(0, n_images)]
            for i, image in enumerate(mani_data['images']['original_images']):
                try:
                    images_to_write[i] = image
                except:
                    print("WARNING - image no %s for capture %s not found" %
                          (i, capture_id))
            row_to_write += images_to_write
            csvwriter.writerow(row_to_write)

    os.chmod(args['machine_learning_file'], 0o660)