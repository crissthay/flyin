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

    #print(config.hubs)
    #print(config.connections)
    s = Simulation(config.hubs,
        config.connections,
        config.nb_drones,
        config.start_hub,
        config.end_hub,
        )
    s.create_drones()
    path = s.bfs()
    s.simulate()
    visual = Visual()
    visual.load_images()
    

    #print(s.end_hub.drones)
    #print(path)
    #print(s.drone_list)
    #print(s.start_hub.drones)
    #print(s.start_hub.max_drones)
    
    #except:
        #pass
        
if __name__ == '__main__':
    main()