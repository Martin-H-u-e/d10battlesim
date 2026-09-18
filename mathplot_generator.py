# read and format data from a txt file
# then generate a plot using matplotlib

import matplotlib.pyplot as plt


def generate_plot_from_simdata(filename="simdata.txt"):
    # Read and format data from the text file
    with open(filename, 'r') as f:
        data = f.read()

    # Parse the data (this is a simplified example - you may need to adjust based on your actual data format)
    lines = data.split('\n')
    pools = []
    l_values = []
    m_values = []
    h_values = []

    for line in lines:
        if line.startswith("=== Pool:"):
            pool_size = int(line.split()[3].rstrip('d10'))
            pools.append(pool_size)
        elif line.startswith("  L:"):
            l_value = float(line.split()[2])
            l_values.append(l_value)
        elif line.startswith("  M:"):
            m_value = float(line.split()[2])
            m_values.append(m_value)
        elif line.startswith("  H:"):
            h_value = float(line.split()[2])
            h_values.append(h_value)

    # Generate the plot
    plt.figure(figsize=(10, 6))
    plt.plot(pools, l_values, marker='o', label='Light (L)')
    plt.plot(pools, m_values, marker='s', label='Medium (M)')
    plt.plot(pools, h_values, marker='^', label='Heavy (H)')
    plt.xlabel('Pool Size')
    plt.ylabel('Average Value')
    plt.title('Simulation Results by Pool Size')
    plt.legend()
    plt.grid(True)
    plt.show()

generate_plot_from_simdata()