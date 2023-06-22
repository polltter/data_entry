import re
from extract_text import extract_text_content, find_indicator, crop_pdf, crop_to_image
import os
import pickle
import json


def get_all_reports(path, reps):
    """
    Fills a list with all the reports in given path
    """
    for item in os.listdir(path):
        if os.path.isdir(f'{path}/{item}'):
            get_all_reports(f'{path}/{item}', reps)
        else:
            reps.append(f'{path}/{item}')


def find_failed_reports(every_one: dict):
    """
    Gets a dictionary where:
     - each key is a regular expression
     - each item is a dict where:
       - each key is a report
       - each item is a list of tuples with the matches for that report and that
         regex.
    Returns a dict where each key corresponds to a regex and each item is a list of
    reports where that regex didn't match with anything
    """
    where_regex_failed = {}
    for repo in every_one:
        failed_reports = []
        for report in every_one[repo]:
            if not len(every_one[repo][report]):
                failed_reports.append(report)
            print(repo, report, len(every_one[repo][report]))
        where_regex_failed[repo] = failed_reports
    return where_regex_failed

def load_reports(path: str = None):
    """
    Loads all the reports stored on a pickle file
    and in case there's a new report in the reports folder, it'll fetch that text
    from the new pdf
    """
    try:
        with open('report_data.pickle', 'rb') as file:
            content = pickle.load(file)
        print('oi')
    except FileNotFoundError:
        content = {}
    if path is None:
        reports = []
        get_all_reports('reports', reports)
        for report in reports:
            if not content[report.split('/')[-1]]:
                content[report.split('/')[-1]] = (extract_text_content(report))
        with open('report_data.pickle', 'wb') as file:
            pickle.dump(content, file)
        return content
    else:
        try:
            return {path.split('/')[-1]: extract_text_content(path)}
        except FileNotFoundError:
            print("No file with that name!")


def all_regex_one_report(report: list or dict, expressions: dict):
    """
    gets the extracted content of a report and finds all the matches
    for a set of different expressions
    """
    all_tup = {}
    if type(report) is dict:
        first = list(report.keys())
        report = report[first[0]]
    for key in expressions:
        all_tup[key] = find_indicator(report, expressions[key])
    return all_tup


def all_reports_one_regex(report: dict, expression: str):
    """
    finds all the matches for a given expression in a set of different reports
    """
    all_tup = {}
    for key in report:
        all_tup[key] = find_indicator(report[key], expression)
    return all_tup


def all_in_all(report: dict, regexes: dict):
    """
    goes through a set a regex expressions and for each one finds the matches
    on a set of reports
    """
    all_in = {}
    for regex in regexes:
        all_in[regex] = all_reports_one_regex(report, regexes[regex])
    return all_in


def find_path(filename):
    """
    returns the path of a given report
    """
    rep = []
    get_all_reports('reports', rep)
    for r in rep:
        if filename in r:
            return r


def get_indices(matches: dict, report: str):
    indices = []
    for tup in matches[report]:
        indices.append(tup[0])
    return indices


def get_matches(expr: str, repo: dict):
    """
    finds the match of an expression in a dict of tuples
    """
    for tup in repo:
        try:
            a = {"Text": tup[0], "Match": re.search(expr, tup[0])[0], "Page": tup[2]}
            yield a
        except TypeError:
            pass

def save_to_json(filepath: str, file_to_save: dict):
    with open(filepath, 'w') as f:
        json.dump(file_to_save, f, indent=3)


def save_expression(filepath: str, expressions: list):
    with open(filepath, 'w') as f:
        f.writelines(expressions)


def get_images(report: str, matches: list, indicator: str):
    for index in matches:
        crop_pdf(find_path(report), 150, 150, matches, index[0], indicator)
        crop_to_image()


def test_new_regex(new_regex: str, old_regex: str, reports: dict, to_print: bool):
    compare = {'old': old_regex, 'new': new_regex}
    results = all_in_all(reports, compare)
    if to_print:
        for r in results['old']:
            print(r, "\told:", len(results['old'][r]), "new:",len(results['new'][r]))
    return results


def failed_reports(one_re_all_rep: dict) -> list:
    """
    Check what report did not match to a certain regular expression
    """
    failed_reports_list = []
    for report in one_re_all_rep:
        if not len(one_re_all_rep[report]):
            failed_reports_list.append(report)
    return failed_reports_list


if __name__ == '__main__':
    print(load_reports())