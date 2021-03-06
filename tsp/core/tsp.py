from random import randrange

from tsp.core import GeneticAlgorithm
from tsp.core.util import cached


class TravellingSalesman(GeneticAlgorithm):
    class Traits(GeneticAlgorithm.Traits):
        class Mutate(GeneticAlgorithm.Traits.Mutate):
            def random_swap(self, elements):
                neighbor = elements[:]

                i, j = randrange(1, len(elements) -
                                 1), randrange(1, len(elements) - 1)
                neighbor[i], neighbor[j] = neighbor[j], neighbor[i]

                return neighbor

            def shift_1(self, elements):
                neighbor = elements[:]

                i, j = randrange(1, len(elements) -
                                 1), randrange(1, len(elements) - 1)

                neighbor.insert(j, neighbor.pop(i))

                return neighbor

            def reverse_random_sublist(self, elements):
                neighbor = elements[:]

                i = randrange(1, len(elements) - 1)
                j = randrange(1, len(elements) - 1)

                i, j = min([i, j]), max([i, j])

                neighbor[i:j] = neighbor[i:j][::-1]

                return neighbor

        class Crossover(GeneticAlgorithm.Traits.Crossover):
            def cut_and_stitch(self, individual_a, individual_b):
                individual_a, individual_b

                offspring = individual_a[1:len(individual_a) // 2]
                for b in individual_b[1:-1]:
                    if b not in offspring:
                        offspring.append(b)

                return [individual_a[0]] + offspring + [individual_b[0]]

        class Select(GeneticAlgorithm.Traits.Select):
            def random_top_half(self, population):
                return population[randrange(0, len(population) // 2)]

        class Fitness(GeneticAlgorithm.Traits.Fitness):
            def inverse_cost(self, individual):
                return 1.0 / self.cost(individual)

            def unweighted_mst(self, individual):
                v = len(individual) - 1

                return ((v * v) - v + 1) / self.cost(individual)

            def weighted_mst(self, individual):
                return self.heuristic(individual) / self.cost(individual)

        class Metric:
            def euclidean(self, p1, p2):
                return (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2

            def manhattan(self, p1, p2):
                return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

            def data(self, p1, p2):
                return p1["dists"][p2["index"]]

        class Heuristic:
            @cached
            def kruskal(self, route):  # FIXME
                edges = []
                for u in route[:-1]:
                    for v in route[:-1]:
                        if u != v:
                            edges.append((u, v, self.metric(u, v)))

                edges.sort(key=lambda edge: edge[2])

                cost, components = 0, {v: set([v]) for v in route}

                for u, v, d in edges:
                    if not components[u].intersection(components[v]):
                        cost += d

                        components[u] = components[u].union(components[v])
                        components[v] = components[u]

                        for root, component in components.items():
                            if u in component or v in component:
                                for vertex in component:
                                    components[root] = components[root].union(
                                        components[vertex])

                return cost

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def cost(self, route):
        return sum([
            self.metric(route[i], route[i + 1])
            for i in range(len(route) - 1)
        ])

    def genetic_algorithm(self, *args, **kwargs):
        depot, cities = args[0], args[1]

        initial_solution = self.find_solution([depot] + cities)
        fittest = GeneticAlgorithm.fit(self, list(initial_solution) + [depot])
        return fittest, self.cost(fittest)


class TravellingSalesmanTimeWindows(TravellingSalesman):
    class Traits(TravellingSalesman.Traits):
        class Fitness(TravellingSalesman.Traits.Fitness):
            def inverse_cost(self, individual):
                pen = self.penalty(individual)
                c = 0.5 * self.cost(individual) + 0.5 * pen

                return 1.0 / c if pen == 0 else -1

            def unweighted_mst(self, individual):
                pen = self.penalty(individual)
                v = len(individual) - 1

                c = 0.5 * self.cost(individual) + 0.5 * pen

                return ((v * v) - v + 1) / c if pen == 0 else -1

            def weighted_mst(self, individual):  # fixme
                c = 0.5 * self.cost(individual) + 0.5 * \
                    self.penalty(individual)

                return self.heuristic(individual) / c

        class Service:
            def service(self, point):
                return 0

        class Timewindow:
            def time_window(self, point):
                return point["twindow"][0], point["twindow"][1]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def partial_cost(self, a, b):
        return self.service(a) + self.metric(a, b)

    def cost(self, route):
        return sum([
            self.partial_cost(route[i], route[i + 1])
            for i in range(len(route) - 1)
        ])

    def partial_penalty(self, arrival, a, b):
        arrival += self.partial_cost(a, b)

        beg, end = self.timewindow(b)

        start_of_service = max(arrival, beg)

        penalty = max(0, start_of_service + self.service(b) - end)

        return arrival, penalty

    def penalty(self, route):
        arrival, penalty = 0, 0

        for i in range(len(route) - 1):
            arrival, p = self.partial_penalty(arrival, route[i], route[i + 1])
            penalty += p

        return penalty
