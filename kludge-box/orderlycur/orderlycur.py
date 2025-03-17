#!/usr/bin/env python3
# Copyright and related rights waived under CC0
# (<http://creativecommons.org/publicdomain/zero/1.0/>)
'''
Verifying currency orderliness for change-making

The "change-making problem" asks us to find the optimal way to make change
using a some currency, i.e. the way that uses the fewest coins to represent
a given value.  A currency is "orderly" (a.k.a.  "canonical", "standard", or
"greedy") if a greedy algorithm can be relied upon to make optimal change.

This module can check a currency for orderliness and make optimal change
with orderly currencies.  There are two key data structures expected by
these functions:

currency:
  The set of denominations ("coin values") that make up the currency.  Every
  currency must contains a ones (1) denomination.
  
  Must be a list of positive integers, sorted in descending order (with 1 as
  the last element), with no duplicates.

coinrep:
  A multiset of coins from a currency, together representing some value.
  Associates each denomination with a non-negative integer denoting the
  number of coins (possibly zero) of that denomination that are used.
  
  Represented as a list of 2-tuples consisting of a denomination followed by
  the count.  The list must be sorted in descending order of denomination,
  with exactly one entry for each of the original currency's denominations.
  Unused denominations are represented with a count of zero.


Bibliography:

D. Pearson. A Polynomial-time Algorithm for the Change-Making Problem.
    Operations Reseach Letters, 33(3):231-234, 2005.
    <http://graal.ens-lyon.fr/~abenoit/algo09/coins2.pdf>

A. & M. Adamaszek.  Combinatorics of the change-making problem.
    European Journal of Combinatorics, 31:47-63, 2010.
    <http://www.sciencedirect.com/science/article/pii/S0195669809001292>

cs.stackexchange: "When can a greedy algorithm solve the coin change problem?"
    <http://cs.stackexchange.com/questions/6552/when-can-a-greedy-algorithm-solve-the-coin-change-problem>
'''

from itertools import combinations_with_replacement

def coinrep_value(coinrep):
    '''Get the total value of the coins in coinrep.'''
    return sum(denom * count for (denom, count) in coinrep)

def coinrep_count(coinrep):
    '''Get the number of coins in coinrep.'''
    return sum(count for (denom, count) in coinrep)

def grdy_coinrep(value, currency):
    '''
    Represent a value using coins in a currency.

    Uses the greedy algorithm to produce a coinrep representing the given
    value using the denominations in given currency.  If the currency is
    orderly, then this coinrep is guaranteed to optimal (i.e. use the
    minimum number of coins necessary).

    Use is_orderly() or orderly_conterex() to determine if a currency is
    orderly.
    '''
    coinrep = []
    remaining = value
    for denom in currency:
        count, remaining = divmod(remaining, denom)
        coinrep.append((denom, count))
    return coinrep

def orderly_counterex(currency):
    '''
    Determine if a currency is orderly, give a counterexample if not.

    If the currency is not orderly, this function returns a counterexample
    to prove it: it identifies a value for which grdy_coinrep() does not
    produce an optimal representation (uses more coins than needed) and
    returns a coinrep that represents that value with fewer coins.
    
    If the currency is orderly, then return None.
    
    Implements the algorithm from:
        D. Pearson. A Polynomial-time Algorithm for the Change-Making
        Problem.  Operations Reseach Letters, 33(3):231-234, 2005.
        <http://graal.ens-lyon.fr/~abenoit/algo09/coins2.pdf>
    '''
    def mk_candidate(i, j):
        candidate = []
        template = grdy_coinrep(currency[i - 1] - 1, currency)

        for denom, count in template[:j]:
            candidate.append((denom, count))

        denom, count = template[j]
        candidate.append((denom, count + 1))

        for denom, count in template[j+1:]:
            candidate.append((denom, 0))

        return candidate

    def is_counterexample(candidate):
        value = coinrep_value(candidate)
        ref = grdy_coinrep(value, currency)
        return coinrep_count(candidate) < coinrep_count(ref)

    n = len(currency)
    for i, j in combinations_with_replacement(range(1, n), 2):
        candidate = mk_candidate(i, j)
        if is_counterexample(candidate):
            return candidate
    return None

def is_orderly(currency):
    '''
    Determines if a currency is orderly.

    See orderly_counterex()
    '''
    return orderly_counterex(currency) is None

if __name__ == '__main__':
    import sys
    currency = sorted(set(int(arg) for arg in sys.arg), reverse=True)
    counterex = orderly_counterex(currency)
    if currency is None:
        print('Currency is orderly.')
    else:
        value = conrep_value(counterex)
        ref = grdy_coinrep(value, currency)
        print('Currency is not orderly.')
