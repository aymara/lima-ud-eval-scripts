#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import argparse

from conllu import parse

EMPTY = '_'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--gold', type=str, help='Gold (.conllu)')
    parser.add_argument('-p', '--pred', type=str, help='Predictions (.conllu)')
    parser.add_argument('-s', '--sort', default=False, action='store_true', help='Sort by F1')
    parser.add_argument('-e', '--errors', default=False, action='store_true', help='Print errors')
    parser.add_argument('-w', '--width', type=int, help='Max line width')
    parser.add_argument('-f', '--filter', type=str, help='Filter words (upos=NOUN;Gender=Masc)')
    args = parser.parse_args()

    gold = parse(open(args.gold, "r", encoding="utf-8").read())
    pred = parse(open(args.pred, "r", encoding="utf-8").read())

    if len(gold) != len(pred):
        sys.stderr.write('Error: number of sentences in corpora isn\'t equal: '
                         'len(gold)==%d, len(pred)==%d\n' % (len(gold), len(pred)))
        sys.exit(1)

    filter = None
    if args.filter is not None:
        sys.stderr.write('Filter: %s\n' % args.filter)
        filter = parse_filter(args.filter)

    stat = { 'upos': {}, 'feats': {}, 'dep': {} }
    compare(stat, gold, pred, filter)

    metrics = {}
    calc_tag_stat(stat['upos'], 'UPOS', metrics)
    calc_feat_stat(stat['feats'], metrics)
    calc_feat_stat(stat['dep'], metrics)

    print_metrics(metrics, sort_metrics=args.sort, print_errors=args.errors, max_line_len=args.width)


def parse_filter(s):
    res = {}
    filters = s.split(';')
    for f in filters:
        (left, right) = f.split('=')
        if left in res:
            sys.stderr.write('Error: incorrect filter (\"%s\" mentioned at least twice)\n' % left)
            sys.exit(1)
        if left == 'upos':
            res['upos'] = right
        else:
            if 'feats' not in res:
                res['feats'] = {}
            if left in res['feats']:
                sys.stderr.write('Error: incorrect filter (\"%s\" mentioned at least twice)\n' % left)
                sys.exit(1)
            res['feats'][left] = right
    return res


def apply_filter(token, filter):
    for k in filter:
        if k == 'feats':
            for f in filter['feats']:
                if token['feats'] is None:
                    return False
                if f not in token['feats']:
                    return False
                if token['feats'][f] is None:
                    return False
                val = token['feats'][f]
                if val != filter['feats'][f]:
                    return False
        elif k == 'upos':
            if token['upostag'] is None:
                return False
            upostag = token['upostag']
            if upostag != filter['upos']:
                return False

    return True


def compare(stat, gold, pred, filter = None):
    total_words = 0
    for i in range(len(gold)):
        gold_sent = gold[i]
        pred_sent = pred[i]

        alignment = align(gold_sent, pred_sent)
        for pair in alignment:
            if filter is not None and not apply_filter(pair['gold'], filter):
                continue
            compare_tags(stat['upos'], pair['gold']['upostag'], pair['pred']['upostag'])
            compare_feats(stat['feats'], pair['gold']['feats'], pair['pred']['feats'])
            compare_dep(stat['dep'], pair['gold'], pair['pred'])
            total_words += 1

    add_emtpy_count(stat['upos'], total_words)
    for f in stat['feats']:
        add_emtpy_count(stat['feats'][f], total_words)


def add_emtpy_count(stat, total_words):
     feature_expressed = 0
     for gold_value in stat:
         for pred_value in stat[gold_value]:
             feature_expressed += stat[gold_value][pred_value]
     if feature_expressed != total_words:
         if EMPTY not in stat:
             stat[EMPTY] = {}
         if EMPTY not in stat[EMPTY]:
             stat[EMPTY][EMPTY] = 0
         stat[EMPTY][EMPTY] += total_words - feature_expressed


def compare_tags(stat, gold, pred):
    if gold not in stat:
        stat[gold] = {}
    if pred not in stat:
        stat[pred] = {}
    if pred not in stat[gold]:
        stat[gold][pred] = 0
    if gold not in stat[pred]:
        stat[pred][gold] = 0
    stat[gold][pred] += 1


def compare_feats(stat, gold, pred):
    if gold is None:
        gold = {}
    if pred is None:
        pred = {}
    gold_ = gold
    pred_ = pred
    for k in gold:
        if k not in pred_:
            pred_[k] = EMPTY
    for k in pred:
        if k not in gold:
            gold_[k] = EMPTY
    for k in gold_:
        if k not in stat:
            stat[k] = {}
        compare_tags(stat[k], gold_[k], pred_[k])


def compare_dep(stat, gold, pred):
    gold_root, pred_root = 'No', 'No'
    if 0 == gold['head']:
        gold_root = 'Yes'
    if 0 == pred['head']:
        pred_root = 'Yes'

    if 'IsRoot' not in stat:
        stat['IsRoot'] = {}
    compare_tags(stat['IsRoot'], gold_root, pred_root)


def align(gold, pred):
    pairs = []

    gi, pi = 0, 0
    while gi < len(gold) and pi < len(pred):
        gtok = gold[gi]
        ptok = pred[pi]

        if gtok['id'] == ptok['id']:
            pairs.append({ 'gold': gtok, 'pred': ptok })
            gi += 1
            pi += 1
        elif isinstance(gtok['id'], tuple):
            if '-' in gtok['id'][1]:
                gi += 1
                continue
            elif '.' in gtok['id'][1]:
                gi += 1
                continue
            else:
                sys.stderr.write('Error: can\'t parse token id in gold file: \'%s\'\n' % str(gtok))
                sys.exit(1)
        elif isinstance(ptok['id'], tuple):
            if '-' in ptok['id'][1]:
                pi += 1
                continue
            elif '.' in ptok['id'][1]:
                pi += 1
                continue
            else:
                sys.stderr.write('Error: can\'t parse token id in pred file: \'%s\'\n' % str(ptok))
                sys.exit(1)

    while gi < len(gold):
        tok = gold[gi]
        if isinstance(tok['id'], tuple) and tok['id'][1] in '.-':
            gi += 1
            continue
        else:
            sys.stderr.write('Error: extra data in gold sentence: %s\n' % str(gold))
            sys.exit(1)

    while pi < len(pred):
        tok = gold[pi]
        if isinstance(tok['id'], tuple) and tok['id'][1] in '.-':
            pi += 1
            continue
        else:
            sys.stderr.write('Error: extra data in pred sentence: %s\n' % str(pred))
            sys.exit(1)

    return pairs


def calc_tag_stat(stat, category, results):
    for tag in sorted(list(stat.keys())):
        k = list(stat[tag].keys())
        tag_in_gold, tag_in_pred, f1, pr, rc = calc_f1(stat, tag)
        value = {
            'count': {
                'gold': tag_in_gold,
                'pred': tag_in_pred,
            },
            'precision': pr,
            'recall': rc,
            'f1': f1,
            'errors': collect_errors(stat, tag)
        }
        results['%s=%s' % (category, tag)] = value


def calc_feat_stat(stat, results):
    for feat_name in sorted(list(stat.keys())):
        calc_tag_stat(stat[feat_name], feat_name, results)


def collect_errors(stat, tag):
    d = {}

    if tag not in stat:
        return d

    total = 0
    for k in stat[tag]:
        total += stat[tag][k]

    if 0 == total:
        return d

    for k in stat[tag]:
        if k == tag:
            continue
        d[k] = float(stat[tag][k]) * 100 / total

    return d


def calc_f1(stat, tag):
    tp, fp, tn, fn = 0, 0, 0, 0
    pr, rc, f1 = 0, 0, 0
    tag_in_gold, tag_in_pred = 0, 0

    if tag in stat:
        if tag in stat[tag]:
            tp = stat[tag][tag]

        for x in stat[tag]:
            tag_in_gold += stat[tag][x]

        if 0 == tag_in_gold:
            rc = 0
        else:
            rc = float(tp) / tag_in_gold

        for x in stat:
            if tag in stat[x]:
                tag_in_pred += stat[x][tag]

        if 0 == tag_in_pred:
            pr = 0
        else:
            pr = float(tp) / tag_in_pred

        if 0 == pr or 0 == rc:
            f1 = 0
        else:
            f1 = 2 * pr * rc / (pr + rc)

    return tag_in_gold, tag_in_pred, f1, pr, rc


def print_metrics(metrics, sort_metrics=False, print_errors=False, max_line_len=None):
    metrics_order = list(metrics.keys())

    max_len = 6
    for name in metrics_order:
        if len(name) > max_len:
            max_len = len(name)

    max_count_len = 9
    for name in metrics_order:
        for k in metrics[name]['count']:
            l = len(str(metrics[name]['count'][k]))
            if l > max_count_len:
                max_count_len = l

    columns = [ 'Metric', 'Raw gold', 'Raw pred', 'Precision', 'Recall', 'F1']
    header = '\t'.join([' ' * (max_len - len(columns[0])) + columns[0],
                 ' ' * (max_count_len - len(columns[1])) + columns[1],
                 ' ' * (max_count_len - len(columns[2])) + columns[2],
                 ' ' * (9 - len(columns[3])) + columns[3],
                 ' ' * (9 - len(columns[4])) + columns[4],
                 ' ' * (9 - len(columns[5])) + columns[5]])

    if print_errors:
        header += '  ' + 'Errors'

    print(header)

    if sort_metrics:
        metrics_order.sort(key=lambda x: metrics[x]['f1']) #, reverse=True)

    for name in metrics_order:
        v = metrics[name]
        padded_name = ' ' * (max_len - len(name)) + name
        line = '%s\t%s\t%s\t%9.2f\t%9.2f\t%9.2f' \
               % (padded_name,
                  ' ' * (max_count_len - len(str(v['count']['gold']))) + str(v['count']['gold']),
                  ' ' * (max_count_len - len(str(v['count']['pred']))) + str(v['count']['pred']),
                  v['precision']*100, v['recall']*100, v['f1']*100)

        if print_errors:
            max_error_str_len = None
            if max_line_len is not None:
                max_error_str_len = max_line_len - len(line) + 2
            if max_error_str_len is None or max_error_str_len > 0:
                line += '  ' + format_error_line(v['errors'], max_error_str_len)

        print(line)


def format_error_line(errors, max_len=None):
    s = ''
    k = sorted(errors.keys(), key=lambda x: errors[x], reverse=True)

    for name in k:
        old_s = s
        if len(s) > 0:
            s += ' '
        s += '%s:%.2f' % (name, errors[name])
        if max_len is not None and len(s) > max_len - 4:
            s = old_s + ' ...'
            break

    return s


if __name__ == '__main__':
    main()
