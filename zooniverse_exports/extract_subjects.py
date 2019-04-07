""" Extract Subjects Data
    - Zooniverse 'subjects' export
    - Raw Subject-Data Example:
    subject_id,project_id,workflow_id,subject_set_id,metadata,locations,classifications_count,retired_at,retirement_reason,created_at,updated_at
        17510222,5115,4979,18231,"{""#roll"":1,""#site"":""J04"",
            ""Image 1"":""6562_6082_5649.JPG"",
            ""Image 2"":""6116_9310_6586.JPG"",
            ""Image 3"":""4600_9071_9361.JPG"",
            ""license"":""SnapshotSafari"",""#capture"":6,
            ""attribution"":""University of Minnesota Lion Center +
                SnapshotSafari + Singita Grumeti""}",
            "{""0"":""https://panoptes-uploads.zooniverse.org/production/subject_location/f26d4b0a-81f8-4203-bd90-c85d659a05bb.jpeg"",
              ""1"":""https://panoptes-uploads.zooniverse.org/production/subject_location/16f9fa0f-95b1-4425-9d27-55878a33f39e.jpeg"",
              ""2"":""https://panoptes-uploads.zooniverse.org/production/subject_location/7ed39f2d-70b4-4d5e-ae1a-29215832a47e.jpeg""}",
              17,2018-11-13 08:17:58 UTC,consensus,2018-01-28 02:27:23 UTC,2018-01-28 02:27:23 UTC
"""
import csv
import os
import logging
import argparse
from collections import OrderedDict

from logger import setup_logger, create_log_file
from utils import print_nested_dict, set_file_permission
from zooniverse_exports import extractor
from config.cfg import cfg

flags = cfg['subject_extractor_flags']


if __name__ == '__main__':

    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--subject_csv", type=str, required=True)
    parser.add_argument("--output_csv", type=str, required=True)
    parser.add_argument("--log_dir", type=str, default=None)
    parser.add_argument("--log_filename", type=str, default='extract_subjects')

    args = vars(parser.parse_args())

    ######################################
    # Check Input
    ######################################

    if not os.path.isfile(args['subject_csv']):
        raise FileNotFoundError("subject_csv: {} not found".format(
                                args['subject_csv']))

    ######################################
    # Configuration
    ######################################

    # logging
    if args['log_dir'] is not None:
        log_file_path = create_log_file(args['log_dir'], args['log_filename'])
        setup_logger(log_file_path)
    else:
        setup_logger()
    logger = logging.getLogger(__name__)

    # logging flags
    print_nested_dict('', flags)

    # Read Subject CSV
    n_images_per_subject = list()
    subject_info = OrderedDict()
    subject_data_header = set()
    with open(args['subject_csv'], "r") as ins:
        csv_reader = csv.reader(ins, delimiter=',', quotechar='"')
        header_subject = next(csv_reader)
        row_name_to_id_mapper_sub = {x: i for i, x in enumerate(header_subject)}
        for line_no, line in enumerate(csv_reader):
            subject_id = line[row_name_to_id_mapper_sub['subject_id']]
            # Extract Location / URL Data
            locations_dict = extractor.extract_key_from_json(
                line, 'locations', row_name_to_id_mapper_sub)
            # append 'url' to key-names: 0->url0
            location_keys = list(locations_dict.keys())
            location_keys.sort()
            for i in range(0, len(location_keys)):
                locations_dict['zooniverse_url_{}'.format(i)] = \
                    locations_dict.pop('{}'.format(i))
            # extract metadata
            metadata_dict = extractor.extract_key_from_json(
                line, 'metadata', row_name_to_id_mapper_sub)
            # get other information
            retired_at = line[row_name_to_id_mapper_sub['retired_at']]
            retirement_reason = line[row_name_to_id_mapper_sub['retirement_reason']]
            # handle legacy case when 'created_at' was not in Zooniverse exports
            try:
                created_at = line[row_name_to_id_mapper_sub['created_at']]
            except:
                created_at = ''
            # collect all subject data
            subject_data_all = {
                'subject_id': subject_id,
                'retired_at': retired_at,
                'retirement_reason': retirement_reason,
                'created_at': created_at,
                **locations_dict,
                **metadata_dict
            }
            # gather all subject info to add
            subject_info_to_add = OrderedDict()
            # add subject_id per default
            subject_info_to_add['subject_id'] = subject_id
            # add location data if specified
            if flags['SUBJECT_ADD_LOCATION_DATA']:
                for location_key in locations_dict.keys():
                    subject_info_to_add[location_key] = \
                        subject_data_all[location_key]
            # add the specified meta-data
            for field in flags['SUBJECT_METADATA_TO_ADD']:
                try:
                    subject_info_to_add[field] = subject_data_all[field]
                except:
                    subject_info_to_add[field] = ''
            for field in flags['SUBJECT_DATA_TO_ADD']:
                try:
                    subject_info_to_add[field] = subject_data_all[field]
                except:
                    subject_info_to_add[field] = ''
            subject_info_to_add = extractor.rename_dict_keys(
                subject_info_to_add, flags['SUBJECT_DATA_NAME_MAPPER'])
            subject_data_header = subject_data_header.union(
                subject_info_to_add.keys())
            subject_info[subject_id] = subject_info_to_add

    subject_data_header = list(subject_data_header)
    subject_data_header.sort()

    # Output all combined records
    with open(args['output_csv'], 'w') as f:
        csv_writer = csv.writer(f, delimiter=',')
        logger.info("Writing output to {}".format(args['output_csv']))
        csv_writer.writerow(subject_data_header)
        tot = len(subject_info.keys())
        for line_no, subject_data in enumerate(subject_info.values()):
            # Arrange subject data in a list and use '' for missing data
            to_write = list()
            for x in subject_data_header:
                try:
                    to_write.append(subject_data[x])
                except:
                    to_write.append('')
            csv_writer.writerow(to_write)
            # print status
            if ((line_no % 10000) == 0) and (line_no > 0):
                print("Wrote {:,} records".format(line_no))
        logger.info("Wrote {} records to {}".format(
            line_no, args['output_csv']))

    # change permmissions to read/write for group
    set_file_permission(args['output_csv'])
