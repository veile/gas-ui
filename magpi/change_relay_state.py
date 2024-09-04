# Import Module
import argparse
import numpy as np
import smbus


def get_state(byte):
    state = bin(255 - byte)[2:]
    state = list(state)
    state = list(map(int, state))

    while len(state) < 6:
        state.append(0)

    if len(state) > 6:
        state = state[:6]

    return np.array(state, dtype=bool)


def get_hex(r):
    add = 0
    for i, v in enumerate(r):
        if v:
            add += 2 ** i
    return int(255 - add)


# Switch function
def switch(idx):
    activated[idx] = ~activated[idx]
    bus.write_byte(0x20, get_hex(activated))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Control OSA relays from command line",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('action', metavar='a', help="Write/Read the state using either 'w' or 'r'")
    parser.add_argument('relay', metavar='r', type=int, help='Choose relay 0-5')

    args = parser.parse_args()

    # Adding relay interface
    bus = smbus.SMBus(1)

    # Keep track of the button state on/off
    activated = get_state(bus.read_byte(0x20))

    if args.action == 'w':
        switch(args.relay)
        print(f'{args.relay} is now set to {activated[args.relay]}')

    elif args.action == 'r':
        print(activated[args.relay])

    else:
        raise Exception(f'Action {args.action} unknown')
