from flyin.parse import Parse
import sys


def main():
    #try:
    if len(sys.argv) < 2:
        print("ERROR - no argument found")
        sys.exit(1)

    config = Parse(sys.argv[1])
    config.open_read_file()
    config.type_lines()

    print(config.hubs)
    print(config.connections)
    #except:
        #pass
        
if __name__ == '__main__':
    main()