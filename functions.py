import time


def measure(filename, tcs):
    start = time.time()
    
    while (time.time() - start) < 600:

        
        with open('running_flag', 'r') as f:
            exp_running_flag = bool(int(f.read()))
        if not exp_running_flag:
            return f'<span style="color:red;">Measurement <span style="font-weight: 600;">{filename[:-4]}</span> stopped<span>'

        temperatures = '\t'.join(list(map(str, tcs.get_T())))

        output = f'{time.time()}\t'+temperatures

        with open(filename, 'a') as file:
            file.write(output + "\n")

        time.sleep(0.4)

    return f'Measurement {filename[:-4]} finished'
