from typing import List

class Node():
    def __init__(self, person, parent, movie):
        self.person = person
        self.parent = parent
        self.movie = movie


class StackFrontier():
    def __init__(self):
        self.frontier: List[Node] = []

    def add(self, node):
        self.frontier.append(node)

    def contains_state(self, person):
        return any(node.person == person for node in self.frontier)

    def empty(self):
        return len(self.frontier) == 0

    def remove(self) -> Node:
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[-1]
            self.frontier = self.frontier[:-1]
            return node


class QueueFrontier(StackFrontier):

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node
