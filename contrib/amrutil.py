import importlib.util  # needed for amr.peg
import os
import sys

sys.path.insert(0, os.path.dirname(importlib.util.find_spec("smatch.smatch").origin))  # to find amr.py from smatch
from smatch import smatch
sys.path.pop(0)


def parse(*args, **kwargs):
    if parse.AMR is None:
        prev_dir = os.getcwd()
        os.chdir(os.path.dirname(importlib.util.find_spec("src.amr").origin))  # to find amr.peg
        try:
            from src.amr import AMR
        finally:
            os.chdir(prev_dir)
        parse.AMR = AMR
    return parse.AMR(*args, **kwargs)
parse.AMR = None


def evaluate(guessed, ref, converter=None, verbose=False, amr_id=None, **kwargs):
    """
    Compare two AMRs and return scores, possibly printing them too.
    :param guessed: AMR object to evaluate
    :param ref: reference AMR object to compare to
    :param converter: optional function to apply to inputs before evaluation
    :param amr_id: ID of AMR pair
    :param verbose: whether to print the results
    :return: Scores object
    """
    def _read_amr(amr):
        return "".join(str(amr).splitlines())
    del kwargs
    if converter is not None:
        guessed = converter(guessed)
        ref = converter(ref)
    smatch.verbose = verbose
    return Scores(smatch.process_amr_pair((_read_amr(guessed), _read_amr(ref), amr_id)))


class Scores(object):
    def __init__(self, counts):
        self.counts = counts
        self.precision, self.recall, self.f1 = smatch.compute_f(*counts)

    def average_f1(self, *args, **kwargs):
        del args, kwargs
        return self.f1

    @staticmethod
    def aggregate(scores):
        """
        Aggregate multiple Scores instances
        :param scores: iterable of Scores
        :return: new Scores with aggregated scores
        """
        return Scores(map(sum, zip(*[s.counts for s in scores])))

    def print(self, *args, **kwargs):
        print("Precision: %.3f\nRecall: %.3f\nF1: %.3f" % (self.precision, self.recall, self.f1), *args, **kwargs)

    def fields(self):
        return ["%.3f" % float(f) for f in (self.precision, self.recall, self.f1)]

    def titles(self):
        return self.field_titles()

    @staticmethod
    def field_titles(*args, **kwargs):
        del args, kwargs
        return ["precision", "recall", "f1"]

    def __str__(self):
        print(",".join(self.fields()))
