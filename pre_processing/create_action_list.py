""" Create Action List
    - identify possible issues
    - recommend possible actions
    - export issues
"""
import os
import argparse
from collections import OrderedDict
import logging
import pandas as pd

from pre_processing.utils import (
    plot_site_roll_timelines, read_image_inventory,
    image_check_stats,
    export_inventory_to_csv)
from logger import create_logfile_name, setup_logger
from global_vars import pre_processing_flags as flags

# args = dict()
#
# args['inventory_grouped'] = '/home/packerc/shared/season_captures/ENO/captures/ENO_S1_captures_grouped.csv'
# args['action_list_csv'] = '/home/packerc/shared/season_captures/ENO/captures/ENO_S1_images_with_issues.csv'
# args['no_older_than_year'] = 2017
# args['no_newer_than_year'] = 2019
# args['ignore_excluded_images'] = False
# args['plot_timelines'] = True

if __name__ == '__main__':

    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory_grouped", type=str, required=True)
    parser.add_argument("--action_list_csv", type=str, required=True)
    parser.add_argument("--plot_timelines", action='store_true')
    args = vars(parser.parse_args())

    # check existence of root dir
    if not os.path.isfile(args['inventory_grouped']):
        raise FileNotFoundError(
            "inventory_grouped {} does not exist -- must be a file".format(
                args['inventory_grouped']))

    log_file_name = create_logfile_name('create_action_list')
    log_file_path = os.path.join(
        os.path.dirname(args['action_list_csv']), log_file_name)
    setup_logger(log_file_path)
    # setup_logger()
    logger = logging.getLogger(__name__)

    # read grouped data
    inventory = read_image_inventory(
        args['inventory_grouped'],
        unique_id='image_path_original')

    header = list(inventory[list(inventory.keys())[0]].keys())

    # check columns
    check_columns = [x for x in header if x.startswith('image_check__')]
    basic_checks = \
        ['image_check__{}'.format(x) for x in flags['image_checks_basic']]
    time_checks = \
        ['image_check__{}'.format(x) for x in flags['image_checks_time']]

    # Action columns
    action_cols = [
        'action_site',
        'action_roll',
        'action_from_image',
        'action_to_image',
        'action_to_take',
        'action_to_take_reason',
        'datetime_current',
        'datetime_new']

    # create check columns
    inventory_with_issues = OrderedDict()
    for image_path_original, image_data in inventory.items():
        automatic_status = {x: '' for x in action_cols}
        at_least_one_basic_check = \
            any([float(image_data[x]) == 1 for x in
                basic_checks if x in check_columns])
        at_least_one_time_check = \
            any([float(image_data[x]) == 1 for x in
                time_checks if x in check_columns])
        # generate check-string
        time_checks_list = \
            [x.replace('image_check__', '') for x in
             time_checks if x in check_columns and float(image_data[x]) == 1]
        basic_checks_list = \
            [x.replace('image_check__', '') for x in
             basic_checks if x in check_columns and float(image_data[x]) == 1]
        all_check_string = '#'.join(basic_checks_list + time_checks_list)
        if at_least_one_basic_check:
            automatic_status['action_to_take'] = 'delete'
        elif at_least_one_time_check:
            automatic_status['action_to_take'] = 'inspect'
        automatic_status['action_to_take_reason'] = all_check_string
        image_data.update(automatic_status)
        # export problematic cases only
        if at_least_one_basic_check or at_least_one_time_check:
            inventory_with_issues[image_path_original] = image_data
        # populate action columns
        automatic_status['action_from_image'] = image_data['image_name_new']
        automatic_status['action_to_image'] = image_data['image_name_new']

    # Export cases with issues
    logger.info("Images with potential issues")
    image_check_stats(inventory_with_issues, logger)

    first_cols = ['season', 'site', 'roll', 'image_rank_in_roll',
                  'capture', 'image_rank_in_capture',
                  'image_name_new']
    first_cols += action_cols

    export_inventory_to_csv(
        inventory_with_issues,
        args['action_list_csv'],
        first_cols=first_cols)

    # create plot for site/roll timelines
    if args['plot_timelines']:
        df = pd.DataFrame.from_dict(inventory, orient='index')
        plot_file_name = 'site_roll_timelines.pdf'
        plot_file_path = os.path.join(
            os.path.dirname(args['inventory_grouped']), plot_file_name)
        plot_site_roll_timelines(
            df=df,
            output_path=plot_file_path,
            date_col='datetime',
            date_format=flags['time_formats']['output_datetime_format'])

# # create CSV to invalidate specific rolls
# header_to_invalidate = [
#     'site', 'season',
#     'from_image', 'to_image',
#     'from_date_time', 'to_date_time',
#     'invalidate_images',
#     'delete_images',
#     'comment']