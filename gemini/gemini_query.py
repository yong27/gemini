#!/usr/bin/env python

import os
import sys
from itertools import tee, ifilterfalse

# gemini imports
import GeminiQuery
from gemini_subjects import get_family_dict
from gemini_constants import *
from gemini_region import add_region_to_query
from gemini_subjects import Subject

def all_samples_predicate(args):
    """ returns a predicate that returns True if, for a variant,
    the only samples that have the variant have a given phenotype
    """
    subjects = get_subjects(args).values()
    return select_subjects_predicate(subjects, args)

def family_wise_predicate(args):
    gq = GeminiQuery.GeminiQuery(args.db, out_format=args.format)
    families = get_family_dict(gq.c)
    predicates = []
    for f in families.values():
        family_names = [x.name for x in f]
        subjects = get_subjects_in_family(args, f).values()
        predicates.append(select_subjects_predicate(subjects, args,
                                                    family_names))
    def predicate(row):
        return sum([p(row) for p in predicates]) >= args.min_kindreds
    return predicate

def select_subjects_predicate(subjects, args, subset=None):
    subjects = set([s.name for s in subjects])
    predicates = []
    if "all" in args.in_subject:
        predicates.append(variant_in_all_subjects(subjects))
    if "none" in args.in_subject:
        predicates.append(variant_not_in_subjects(subjects))
    if "only" in args.in_subject:
        predicates.append(variant_only_in_subjects(subjects, subset))
    if "any" in args.in_subject:
        predicates.append(variant_in_any_subject(subjects))
    def predicate(row):
        return all([p(row) for p in predicates])
    return predicate

def get_subjects(args):
    """
    return a dictionary of subjects, optionally using the
    subjects_query argument to filter them.

    """
    gq = GeminiQuery.GeminiQuery(args.db, out_format=args.format)
    query = "SELECT * FROM samples"
    if args.sample_filter:
        query += " WHERE " + args.sample_filter
    gq.c.execute(query)
    samples_dict = {}
    for row in gq.c:
        subject = Subject(row)
        samples_dict[subject.name] = subject
    return samples_dict

def get_subjects_in_family(args, family):
    subjects = get_subjects(args)
    family_names = [f.name for f in family]
    subject_dict = {}
    for subject in subjects:
        if subject in family_names:
            subject_dict[subject] = subjects[subject]
    return subject_dict


def variant_in_any_subject(subjects):
    def predicate(row):
        return subjects.intersection(samples_with_variant(row)) != set()
    return predicate

def variant_in_all_subjects(subjects):
    def predicate(row):
        return subjects.issubset(samples_with_variant(row))
    return predicate

def variant_only_in_subjects(subjects, subset=None):
    def predicate(row):
        if subset:
            check = set(subset).intersection(samples_with_variant(row))
        else:
            check = samples_with_variant(row)
        return check and subjects.issuperset(check)
    return predicate

def variant_not_in_subjects(subjects):
    def predicate(row):
        return subjects.intersection(samples_with_variant(row)) == set()
    return predicate


def samples_with_variant(row):
    return row['variant_samples']

def queries_variants(query):
    return "variants" in query.lower()

def get_predicates(args):
    predicates = []
    if args.family_wise:
        predicates.append(family_wise_predicate(args))
    elif args.sample_filter:
        predicates.append(all_samples_predicate(args))
    return predicates


def needs_genotypes(args):
    return args.show_variant_samples or args.family_wise or args.sample_filter

def modify_query(args):
    if args.region:
        add_region_to_query(args)

def run_query(args):

    predicates = get_predicates(args)
    modify_query(args)
    gq = GeminiQuery.GeminiQuery(args.db, out_format=args.format)
    gq.run(args.query, args.gt_filter, args.show_variant_samples,
           args.sample_delim, predicates, needs_genotypes(args))

    if args.use_header and gq.header:
        print gq.header

    for row in gq:
        print row

def query(parser, args):

    if (args.db is None):
        parser.print_help()

    if os.path.exists(args.db):
        run_query(args)

def partition(pred, iterable):
    'Use a predicate to partition entries into false entries and true entries'
    # partition(is_odd, range(10)) --> 0 2 4 6 8   and  1 3 5 7 9
    t1, t2 = tee(iterable)
    return ifilterfalse(pred, t1), filter(pred, t2)

if __name__ == "__main__":
    main()
