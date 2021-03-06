import sys

from random import randrange
from time import time, sleep
from multiprocessing import Process, cpu_count, Manager, Value

from tsp.random.tsp import TSPRandom


def read_file(filename: str):
    f = open("tsp/resources/" + filename, "r")
    n_cities = int(f.readline())
    cities = [{} for _ in range(n_cities)]
    for i in range(n_cities):
        cities[i]["index"] = i
        cities[i]["dists"] = [float(x) for x in f.readline().strip().split()]
    for i in range(n_cities):
        cities[i]["twindow"] = [int(x) for x in f.readline().strip().split()]
    return cities


def run(tsp, cities, dictionary, process_number):
    with process_number.get_lock():
        process_number.value += 1

    sol = {}
    sol["sol"], sol["time"], sol["cost"] = tsp.find_solution(cities)

    with process_number.get_lock():
        process_number.value -= 1

    if sol["sol"] == None:
        return

    if "time" in dictionary:
        best_cost = dictionary["cost"]
        if sol["cost"] < best_cost:
            dictionary["sol"] = sol["sol"]
            dictionary["time"] = sol["time"]
            dictionary["cost"] = sol["cost"]
    else:
        dictionary["sol"] = sol["sol"]
        dictionary["time"] = sol["time"]
        dictionary["cost"] = sol["cost"]


if __name__ == '__main__':
    try:
        file_name = sys.argv[1]
        MAX_TIME = float(sys.argv[2])
    except IndexError:
        raise SystemExit(f"Usage: {sys.argv[0]} <test_file_name> <max_time_in_seconds>")

    cities = read_file(file_name)
    max_process_number = cpu_count()
    dictionary = Manager().dict()
    start_time = time()
    process_number = Value('i', 0)

    while time() - start_time < MAX_TIME:
        with process_number.get_lock():
            pn = process_number.value
        for i in range (max_process_number - pn):
            tsp = TSPRandom(
                max_errors = randrange(50, 500),
                max_time = min(MAX_TIME, MAX_TIME - (time() - start_time)),
                early_arrive = randrange(2)
            )
            process = Process(target=run, args=(tsp, cities, dictionary, process_number))
            process.start()
        sleep(0.1)        

    print("Execution time:", time() - start_time)
    print(dictionary)
