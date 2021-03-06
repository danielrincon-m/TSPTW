import time

from logging import getLogger
from random import random

from tsp.core.util import Model


class GeneticAlgorithm(Model):
    class Traits(Model.Traits):
        class Mutate:
            pass

        class Crossover:
            pass

        class Fitness:
            pass

        class Select:
            pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.MUTATION_PROBABILITY = kwargs.get('mutation_probability', 0.3)
        self.FITNESS_THRESHOLD = kwargs.get('fitness_threshold', 0.65)

        self.POPULATION_SIZE = kwargs.get('population_size', 50)
        # self.MAX_ITERATIONS = kwargs.get('max_iterations', 1000)

        self.MAX_TIME = kwargs.get('max_time', 60)

        self.logger = getLogger(self.__class__.__name__)

    def fit(self, individual):
        start_time = time.time()
        population = [individual]

        for _ in range(self.POPULATION_SIZE - 1):
            population.append(self.mutate(individual))

        fitest, max_fitness = None, 0
        i = 0
        while time.time() - start_time < self.MAX_TIME:
            self.logger.info('Iteration: %04d' % (i,))
            self.logger.info(
                'Fitest: %s, Fitness: %5.3f' % (
                    fitest,
                    max_fitness
                )
            )
            i += 1

            _fitness = {
                id(individual): self.fitness(individual)
                for individual in population
            }

            population.sort(key=lambda p: _fitness[id(p)], reverse=True)

            _fitest = population[0]
            _max_fitness = _fitness[id(population[0])]
            if (_max_fitness > max_fitness):
                fitest, max_fitness = _fitest, _max_fitness

            if max_fitness > self.FITNESS_THRESHOLD:
                break

            successors = []
            for j in range(self.POPULATION_SIZE):
                father = self.select(population)
                mother = self.select(population)

                child = self.crossover(father, mother)

                if random() < self.MUTATION_PROBABILITY:
                    child = self.mutate(child)

                successors.append(child)

            population = successors

        return fitest
