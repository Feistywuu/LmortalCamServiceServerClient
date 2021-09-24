import time

# testing concurrency of python files in pycharm


def main():

    sum = 0
    while True:

        time.sleep(0.3)
        if sum%5 == 0:
            print('currently running')

        sum += 1


main()

