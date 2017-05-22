from communicator import Communicator

if __name__=="__main__":
    try:
        comm=Communicator()
        while True:continue
    except KeyboardInterrupt as e:
        print("<Ctrl-c> = user quit")
    finally:
        print("Exiting...")