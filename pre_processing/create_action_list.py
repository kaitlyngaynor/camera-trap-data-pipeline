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
from utils.logger import set_logging
from config.cfg import cfg


flags = cfg['pre_processing_flags']


def at_least_one_specific_check(image_data, check_columns, checks_to_find):
    """ Find specific checks """
    return any([float(image_data[x]) == 1 for x in
                checks_to_find if x in check_columns])


def generate_check_string(image_data, check_columns, checks_to_find):
    """ Generate a string of checks """
    return [x.replace('image_check__', '') for x in
            checks_to_find if x in check_columns and float(image_data[x]) == 1]


def _issue_is_resolved(image_data):
    """ Determine if issue was already resolved """
    # Issue resolved if image is invalid
    try:
        invalid = image_data['image_is_invalid']
    except KeyError:
        invalid = ''
    if invalid == '1':
        return True
    # Issue resolved if image was flagged as ok
    try:
        last_action = image_data['action_taken'].split('#')[-1]
        return (last_action == 'ok')
    except KeyError:
        return False

# args = dict()
#
# args['captures'] = '/home/packerc/shared/season_captures/ENO/captures/ENO_S1_captures_grouped.csv'
# args['action_list_csv'] = '/home/packerc/shared/season_captures/ENO/captures/ENO_S1_images_with_issues.csv'
# args['no_older_than_year'] = 2017
# args['no_newer_than_year'] = 2019
# args['ignore_excluded_images'] = False
# args['plot_timelines'] = True

# args = dict()
# args['captures'] = '/home/packerc/shared/season_captures/MAD/captures/MAD_S1_captures_updated2.csv'
# args['captures_updated'] = '/home/packerc/shared/season_captures/MAD/captures/MAD_S1_captures_updated2.csv'
# args['no_older_than_year'] = 0000
# args['no_newer_than_year'] = 9999


if __name__ == '__main__':

    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--captures", type=str, required=True)
    parser.add_argument("--action_list_csv", type=str, required=True)
    parser.add_argument("--log_dir", type=str, default=None)
    parser.add_argument(
        "--log_filename", type=str, default='create_action_list')
    parser.add_argument("--plot_timelines", action='store_true')
    args = vars(parser.parse_args())

    # check existence of root dir
    if not os.path.isfile(args['captures']):
        raise FileNotFoundError(
            "captures {} does not exist -- must be a file".format(
                args['captures']))

    # logging
    set_logging(args['log_dir'], args['log_filename'])
    logger = logging.getLogger(__name__)

    # read grouped data
    inventory = read_image_inventory(
        args['captures'],
        unique_id='image_path_original')

    header = list(inventory[list(inventory.keys())[0]].keys())

    # check columns
    check_columns = [x for x in header if x.startswith('image_check__')]
    to_delete_checks = \
        ['image_check__{}'.format(x)
         for x in flags['image_checks_propose_delete']]
    to_invalidate_checks = \
        ['image_check__{}'.format(x)
         for x in flags['image_checks_propose_invalidate']]
    time_checks = \
        ['image_check__{}'.format(x)
         for x in flags['image_checks_propose_time']]

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
        has_deletion = at_least_one_specific_check(
            image_data,
            check_columns,
            to_delete_checks)
        has_invalidation = at_least_one_specific_check(
            image_data,
            check_columns,
            to_invalidate_checks)
        has_time_check = at_least_one_specific_check(
            image_data,
            check_columns,
            time_checks)

        # generate check-string
        all_checks_list = generate_check_string(
            image_data, check_columns, check_columns)
        all_check_string = '|'.join(all_checks_list)
        if has_deletion:
            automatic_status['action_to_take'] = 'delete'
        elif has_invalidation:
            automatic_status['action_to_take'] = 'invalidate'
        elif has_time_check:
            automatic_status['action_to_take'] = 'inspect'
        automatic_status['action_to_take_reason'] = all_check_string

        # populate action columns
        automatic_status['action_from_image'] = image_data['image_name']
        automatic_status['action_to_image'] = image_data['image_name']
        image_data.update(automatic_status)

        # check if image was in previous action lists and was flagged as ok
        issue_is_resolved = _issue_is_resolved(image_data)
        # export problematic cases only
        has_issue = (has_deletion or has_invalidation or has_time_check)
        if has_issue and not issue_is_resolved:
            inventory_with_issues[image_path_original] = image_data

    # Export cases with issues
    logger.info("Images with potential issues")
    image_check_stats(inventory_with_issues)

    first_cols = ['season', 'site', 'roll', 'image_rank_in_roll',
                  'capture', 'image_rank_in_capture',
                  'image_name']
    info_cols = [
     'datetime', 'datetime_exif', 'datetime_file_creation',
     'days_to_last_image_taken', 'days_to_next_image_taken',
     'image_path', 'image_path_rel']

    first_cols += action_cols
    first_cols += info_cols

    # add a dummy record if no issues found
    if len(inventory_with_issues.keys()) == 0:
        random_record = inventory[list(inventory.keys())[0]]
        empty_record = {k: '' for k in random_record.keys()}
        inventory_with_issues['dummy'] = empty_record
        logger.info("No issues found - creating empty action list")

    # keep only relevant columns
    inventory_with_issues_short = OrderedDict()
    for image, image_data in inventory_with_issues.items():
        inventory_with_issues_short[image] = {
            k: image_data[k] for k in first_cols}

    export_inventory_to_csv(
        inventory_with_issues_short,
        args['action_list_csv'],
        first_cols=first_cols)

    # create plot for site/roll timelines
    if args['plot_timelines']:
        df = pd.DataFrame.from_dict(inventory, orient='index')
        plot_file_name = 'site_roll_timelines.pdf'
        plot_file_path = os.path.join(
            os.path.dirname(args['captures']), plot_file_name)
        plot_site_roll_timelines(
            df=df,
            output_path=plot_file_path,
            date_col='datetime',
            date_format=flags['time_formats']['output_datetime_format'])
