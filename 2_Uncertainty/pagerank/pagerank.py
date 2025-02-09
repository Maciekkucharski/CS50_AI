import os
import random
import re
import sys
from typing import List, Set, Dict

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()
    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}
    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )
    return pages


def transition_model(corpus: Dict[str,Set[str]], page: str, damping_factor: float):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    page_at_random = (1 - damping_factor)/(len(list(corpus.keys())))
    model = {p: page_at_random for p in corpus.keys()}
    if len(corpus[page]) == 0:
        return model
    page_from_site = damping_factor * (1/len(corpus[page]))
    for p in corpus[page]:
        model[p] += page_from_site
    return model


def sample_pagerank(corpus: Dict[str,Set[str]], damping_factor: float, n: int):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    
    page = random.choice(list(corpus.keys()))
    final_result = {p: 0 for p in corpus.keys()}
    for _ in range(n):
        transitions = transition_model(corpus, page, damping_factor)
        sorted_keys = sorted(corpus.keys())
        weights = [transitions[key] for key in sorted_keys]
        picked_website = random.choices(sorted_keys, weights=weights, k=1)[0]
        final_result[picked_website]+=1
        page = picked_website
    return {key: value / sum(final_result.values()) for key, value in final_result.items()}

def iterate_pagerank(corpus: Dict[str,Set[str]], damping_factor: float):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    probabilities = {page : 1/len(corpus.keys()) for page in corpus}
    base_probabilitiey = (1-damping_factor)/len(corpus.keys())
    while True:
        new_probabilities = {}
        for page in corpus:
            pages_linked_to_page = [p for p, links in corpus.items() if page in links]
            iterative_sum = damping_factor*sum([probabilities[p]/len(corpus[p]) for p in pages_linked_to_page])
            new_probabilities[page] =  base_probabilitiey + iterative_sum
        total_diff = all([abs(new_probabilities[page] - probabilities[page]<0.001) for page in corpus])
        if total_diff:
            break
        probabilities = new_probabilities
    total_rank = sum(new_probabilities.values())
    return {page: rank / total_rank for page, rank in new_probabilities.items()}

if __name__ == "__main__":
    main()
