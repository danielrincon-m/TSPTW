from random import randrange
from collections import deque
from time import time


class TSPRandom:
    def __init__(self, *args, **kwargs) -> None:
        self.errors = 0
        self.MAX_ERRORS = kwargs.get('max_errors', 1000)
        self.MAX_TIME = kwargs.get('max_time', 1)
        self.EARLY_ARRIVE = kwargs.get('early_arrive', 0)

    def get_cost(self, individual, visited_nodes):
        cost = 0
        for i in range(len(visited_nodes)):
            last_node = self.get_node(individual, visited_nodes[i])
            curr_node = self.get_node(individual, visited_nodes[(i + 1) % len(visited_nodes)])
            cost += last_node["dists"][curr_node["index"]]
        return cost

    def get_node(self, individual: list, index: int):
        for i in individual:
            if i["index"] == index:
                return i

    def get_time_window(self, individual: list, index: int):
        node = self.get_node(individual, index)
        return node["twindow"][0], node["twindow"][1]

    def possible_nodes(self, time: float, individual: list, unvisited_nodes: list, origin_node: int):
        valid_nodes = []
        for i in unvisited_nodes:
            arrival_time = time + individual[origin_node]["dists"][i]
            start, end = self.get_time_window(individual, i)
            if self.EARLY_ARRIVE == 0:
                if start <= arrival_time <= end:
                    valid_nodes.append(i)
            else:
                if arrival_time <= end:
                    valid_nodes.append(i)
        return valid_nodes

    def get_random_solution(self, curr_time: float, individual: list, unvisited_nodes: list, visited_nodes: deque):
        if len(unvisited_nodes) == 0:
            first_node = self.get_node(individual, visited_nodes[0])
            last_node = self.get_node(individual, visited_nodes[-1])
            full_time = curr_time + last_node["dists"][first_node["index"]]
            cost = self.get_cost(individual, visited_nodes)
            return " ".join(str(visited_nodes[i]) for i in range(1, len(visited_nodes))), full_time, cost
        valid_nodes = self.possible_nodes(
            curr_time, individual, unvisited_nodes, visited_nodes[-1])
        while self.errors <= self.MAX_ERRORS:
            if len(valid_nodes) == 0 and len(unvisited_nodes) != 0:
                self.errors += 1
                return None

            elt = valid_nodes[randrange(len(valid_nodes))]
            last_node = self.get_node(individual, visited_nodes[-1])

            start, end = self.get_time_window(individual, elt)
            arrive_time = curr_time + last_node["dists"][elt]
            new_time = arrive_time if arrive_time > start else start

            unvisited_nodes.remove(elt)
            valid_nodes.remove(elt)
            visited_nodes.append(elt)

            result = self.get_random_solution(
                new_time, individual, unvisited_nodes, visited_nodes)
            if result == None:
                unvisited_nodes.append(visited_nodes.pop())
            else:
                return result
        return None

    def find_solution(self, individual):
        solution = None
        start_time = time()
        while (solution == None):
            self.errors = 0
            unvisited_nodes = [i for i in range(1, len(individual))]
            visited_nodes = deque()
            visited_nodes.append(0)
            solution = self.get_random_solution(
                0, individual, unvisited_nodes, visited_nodes)
            if time() - start_time > self.MAX_TIME:
                solution = None, None, None
                break
        return solution


class TSPSwap:
    def __init__(self, *args, **kwargs) -> None:
        pass

    def send_front(self, index: int, individual: list):
        individual.insert(1, individual.pop(index))

    def send_back(self, index: int, individual: list):
        individual.append(individual.pop(index))

    def swap_front(self, index: int, individual: list):
        individual[index], individual[index +
                                      1] = individual[index + 1], individual[index]

    def random_swap(self, index: int, travel_time: float, individual: list):
        num = randrange(4)
        if num == 0:
            travel_time -= individual[index -
                                      2]["dists"][individual[index - 1]["index"]]
            self.swap_back(index, individual)
            index -= 1
        elif num == 1:
            self.swap_front(index, individual)
        elif num == 2:
            travel_time = 0
            self.send_front(index, individual)
            index = 1
        else:
            self.send_back(index, individual)
        return index, travel_time

    def swap_back(self, index: int, individual: list):
        individual[index], individual[index -
                                      1] = individual[index - 1], individual[index]

    def check_window(self, start, travel_time, index, individual):
        first_point = individual[index - 1]
        second_point = individual[index]
        distance = first_point["dists"][second_point["index"]]
        if start:
            return travel_time + distance >= second_point["twindow"][0]
        else:
            return travel_time + distance <= second_point["twindow"][1]

    def find_solution(self, individual):
        travel_time = 0
        index = 1
        while (index < len(individual)):
            valid_start = self.check_window(
                True, travel_time, index, individual)
            valid_end = self.check_window(
                False, travel_time, index, individual)
            if not valid_start or not valid_end:
                if index == len(individual) - 1:
                    travel_time = 0
                    self.send_front(index, individual)
                    index = 1
                elif index == 1:
                    num = randrange(3)
                    if num == 0:
                        self.send_back(index, individual)
                    else:
                        self.send_front(len(individual) - 1, individual)
                else:
                    index, travel_time = self.random_swap(
                        index, travel_time, individual)
            else:
                travel_time += individual[index -
                                          1]["dists"][individual[index]["index"]]
                index += 1
            print(str(index) + ":" + str([i["index"] for i in individual]))
