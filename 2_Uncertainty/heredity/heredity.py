import csv
import itertools
import sys
from typing import List, Dict, Set, Any
PROBS = {
    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },
    "trait": {
        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },
        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },
        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01,
}

def main():
    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])
    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }
    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):
        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue
        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):
                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)
    # Ensure probabilities sum to 1
    normalize(probabilities)
    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]

def get_gene_numer(person_name: str, one_gene: List, two_genes: List,):
    return 1 if person_name in one_gene else 2 if person_name in two_genes else 0

def get_gene_probability(person_name: str, people: Dict, one_gene: List, two_genes: List,):
    gene_number = get_gene_numer(person_name, one_gene, two_genes)
    if not (people[person_name]["mother"] and people[person_name]["father"]):
        return PROBS['gene'][gene_number] 
    else:
        mother_gene_number = get_gene_numer(people[person_name]["mother"], one_gene, two_genes)
        father_gene_number = get_gene_numer(people[person_name]["father"], one_gene, two_genes)

        mother_passing_gene = 0 + PROBS["mutation"] if mother_gene_number==0 else 0.5 if mother_gene_number==1 else 1-PROBS["mutation"]
        father_passing_gene = 0 + PROBS["mutation"] if father_gene_number==0 else 0.5 if father_gene_number==1 else 1-PROBS["mutation"]

        return mother_passing_gene*father_passing_gene if person_name in two_genes else mother_passing_gene*(1-father_passing_gene) + father_passing_gene*(1-mother_passing_gene) if person_name in one_gene else (1-mother_passing_gene) *(1-father_passing_gene)

def joint_probability(people: Dict, one_gene: List, two_genes: List, have_trait: List):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    probability = 1
    for person_name in people:
        gene_number = 1 if person_name in one_gene else 2 if person_name in two_genes else 0
        trait = person_name in have_trait
        gene_probability = get_gene_probability(person_name, people, one_gene, two_genes)
        trait_probability = PROBS['trait'][gene_number][trait]
        probability *= gene_probability * trait_probability
    return probability

def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        if person in one_gene:
            probabilities[person]['gene'][1] += p
        elif person in two_genes:
            probabilities[person]['gene'][2] += p
        else:
            probabilities[person]['gene'][0] += p
        probabilities[person]['trait'][person in have_trait] += p

def normalize_dict(dict_to_noralize: Dict[Any,float]):
    s = sum(dict_to_noralize.values())
    for key in dict_to_noralize:
        dict_to_noralize[key] /= s

def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        normalize_dict(probabilities[person]['gene'])
        normalize_dict(probabilities[person]['trait'])

if __name__ == "__main__":
    main()
