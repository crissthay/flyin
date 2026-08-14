from flyin.parse import Parse
from flyin.simulation import Simulation
from visual.visual import Visual

import sys


def main():
    #try:
    if len(sys.argv) < 2:
        print("ERROR - no argument found")
        sys.exit(1)

    config = Parse(sys.argv[1])
    config.open_read_file()
    config.type_lines()

    s = Simulation(config.hubs,
        config.connections,
        config.nb_drones,
        config.start_hub,
        config.end_hub,
        )
    s.create_drones()
    s.simulate()
    visual = Visual(
        config.hubs,
        config.start_hub,
        config.end_hub,
        s.drone_list
    )
    visual.load_images()
    
    
    #except:
        #pass
        
if __name__ == '__main__':
    main()