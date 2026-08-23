from flyin.parse import Parse
from flyin.simulation import Simulation
from visual.visual import Visual

import sys


def main():
    args = sys.argv[1:]

    capacity_info = "--capacity-info" in args
    if capacity_info:
        args.remove("--capacity-info")

    if len(args) < 1:
        print("ERROR - no argument found")
        sys.exit(1)

    config = Parse(args[0])
    config.open_read_file()
    config.type_lines()

    s = Simulation(
        config.hubs,
        config.connections,
        config.nb_drones,
        config.start_hub,
        config.end_hub,
    )

    s.create_drones()
    s.simulate(capacity_info=capacity_info)

    visual = Visual(
        config.hubs,
        config.start_hub,
        config.end_hub,
        s.drone_list,
        config.connections,
        s,
    )
    visual.run()


if __name__ == '__main__':
    main()