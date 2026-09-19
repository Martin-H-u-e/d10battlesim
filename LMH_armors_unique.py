import numpy as np #type: ignore

np.random.seed(42)
sims = 1000
l_reduction_threshold = 9
l_reduction_count = 4

m_ignore_threshold = 10
m_ignore_count = 2
m_reduction_threshold = 10
m_reduction_count = 1

def run_upgraded_simulation_uniques(dice_counts):
    for dc in dice_counts:
        rolls = np.random.randint(1, 11, size=(sims, dc))
        base_sum = np.sum(rolls, axis=1)
        sorted_rolls = np.sort(rolls, axis=1) # ascending
        
        l_res, m_res, h_res = [], [], []
        
        for row in sorted_rolls:
            # Protected lowest die is row[0]
            # Eligible dice are row[1:]
            
            # --- Light (L): Halve 4, <9 ---
            keep_l = list(row)
            h_count = 0
            for i in range(len(keep_l)-1, 0, -1): # stop at 1 to protect 0
                if h_count >= l_reduction_count: break
                if keep_l[i] < l_reduction_threshold:
                    keep_l[i] = keep_l[i] / 2.0
                    h_count += 1
            l_res.append(sum(keep_l))
            
            # --- Medium (M): Ignore 2, Halve 1, <10 ---
            keep_m = list(row)
            i_count = 0
            # Apply ignores first (best value)
            for i in range(len(keep_m)-1, 0, -1):
                if i_count >= m_ignore_count: break
                if keep_m[i] < m_ignore_threshold:
                    keep_m[i] = None
                    i_count += 1
            # Apply halving next
            h_count_m = 0
            for i in range(len(keep_m)-1, 0, -1):
                if h_count_m >= m_reduction_count: break
                if keep_m[i] is not None and keep_m[i] < m_reduction_threshold:
                    keep_m[i] = keep_m[i] / 2.0
                    h_count_m += 1
            m_res.append(sum([x for x in keep_m if x is not None]))
            
            # --- Heavy (H): Ignore 3, no threshold ---
            keep_h = list(row)
            i_count_h = 0
            for i in range(len(keep_h)-1, 0, -1):
                if i_count_h >= 3: break
                keep_h[i] = None
                i_count_h += 1
            h_res.append(sum([x for x in keep_h if x is not None]))
            
        base_mean = np.mean(base_sum)
        perc_red_l = (1 - np.mean(l_res)/base_mean)*100
        perc_red_m = (1 - np.mean(m_res)/base_mean)*100
        perc_red_h = (1 - np.mean(h_res)/base_mean)*100
        m_to_l = perc_red_l - perc_red_m
        h_to_m = perc_red_m - perc_red_h
        print(f"=== Pool: {dc}d10 (Base Avg: {base_mean:.2f}) ===")
        print(f"  L: Avg {np.mean(l_res):.2f} (Red: {base_mean - np.mean(l_res):.2f}, {perc_red_l:.1f}%)")
        print(f"   % red.  L compared to M: {m_to_l:.1f}%")
        print(f"  M: Avg {np.mean(m_res):.2f} (Red: {base_mean - np.mean(m_res):.2f}, {perc_red_m:.1f}%)")
        print(f"   % red.  M compared to H: {h_to_m:.1f}%")
        print(f"  H: Avg {np.mean(h_res):.2f} (Red: {base_mean - np.mean(h_res):.2f}, {perc_red_h:.1f}%)")
        print()
        return {
            "pool_size": dc,
            "base_avg": base_mean,
            "L_avg": np.mean(l_res),
            "M_avg": np.mean(m_res),
            "H_avg": np.mean(h_res),
            "L_red": perc_red_l,
            "M_red": perc_red_m,
            "H_red": perc_red_h,
            "L_to_M_red": m_to_l,
            "M_to_H_red": h_to_m
        }

def write_simdata_to_txt_file(simdata, filename="simdata.txt"):
    """Capture simulation output and write to text file"""
    import sys
    from io import StringIO
    # take argument simdata and write to text file
    # redirect stdout to capture print output
    old_stdout = sys.stdout
    sys.stdout = mystdout = StringIO()

    # print the simdata to stdout
    for data in simdata:
        print(f"=== Pool: {data['pool_size']}d10 (Base Avg: {data['base_avg']:.2f}) ===")
        print(f"  L: Avg {data['L_avg']:.2f} (Red: {data['base_avg'] - data['L_avg']:.2f}, {data['L_red']:.1f}%)")
        print(f"   % red.  L compared to M: {data['L_to_M_red']:.1f}%")
        print(f"  M: Avg {data['M_avg']:.2f} (Red: {data['base_avg'] - data['M_avg']:.2f}, {data['M_red']:.1f}%)")
        print(f"   % red.  M compared to H: {data['M_to_H_red']:.1f}%")
        print(f"  H: Avg {data['H_avg']:.2f} (Red: {data['base_avg'] - data['H_avg']:.2f}, {data['H_red']:.1f}%)")
        print()
    
    with open(filename, 'w') as f:
        f.write(mystdout.getvalue())
    
    print(mystdout.getvalue())
    print(f"Simulation data written to {filename}")

def write_simdata_to_CSV_googleSheet(simdata, filename="simdata.csv"):

    # work only on a copy of the simdata to avoid modifying the original data
    simdataCpy = [dict(data) for data in simdata]

    #wire the simdata to a CSV file
    import csv

    with open(filename, 'w', newline='') as csvfile:

        # use semicolon as delimiter for CSV file
        writer = csv.writer(csvfile, delimiter=';')

        fieldnames = ["pool_size", "base_avg", "L_avg", "M_avg", "H_avg", "L_red", "M_red", "H_red", "L_to_M_red", "M_to_H_red"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # convert reduction values to actual percentages for CSV output and divide by 100 to get the actual percentage values
        for data in simdataCpy:
            data["L_red"] = round(data["L_red"] / 100, 2)
            data["M_red"] = round(data["M_red"] / 100, 2)
            data["H_red"] = round(data["H_red"] / 100, 2)
            data["L_to_M_red"] = round(data["L_to_M_red"] / 100, 2)
            data["M_to_H_red"] = round(data["M_to_H_red"] / 100, 2)

            # 2. Format numbers: convert floats to strings and replace '.' with ','
            for key in ["base_avg", "L_avg", "M_avg", "H_avg", "L_red", "M_red", "H_red", "L_to_M_red", "M_to_H_red"]:
                data[key] = str(data[key]).replace('.', ',')

        for data in simdataCpy:
            writer.writerow(data)

    print(f"Simdata got written successfully as CSV to {filename}.")



# visualize the data using matplotlib
def visualize_simdata(simdata):
    import matplotlib.pyplot as plt



    # Data
    pool_sizes = [data["pool_size"] for data in simdata]
    base_avgs = [data["base_avg"] for data in simdata]
    l_avgs = [data["L_avg"] for data in simdata]
    m_avgs = [data["M_avg"] for data in simdata]
    h_avgs = [data["H_avg"] for data in simdata]
    l_reds = [data["L_red"] for data in simdata]
    m_reds = [data["M_red"] for data in simdata]
    h_reds = [data["H_red"] for data in simdata]
    m_to_l_reds = [-data["L_to_M_red"] for data in simdata]    
    h_to_m_reds = [-data["M_to_H_red"] for data in simdata]
    
    plt.figure(figsize=(15, 8.5))
    plt.title('Total Damage recieved - Uniques Upgrades')
    plt.xlabel('Number of d10 dice - (sims) Simulations')
    plt.ylabel('Average Damage recieved')
    plt.legend()
    plt.grid(True)

    plt.plot(pool_sizes, base_avgs, marker='x', label='Base Avg')
    plt.plot(pool_sizes, l_avgs, marker='o', label='Light (L)')
    plt.plot(pool_sizes, m_avgs, marker='s', label='Medium (M)')
    plt.plot(pool_sizes, h_avgs, marker='^', label='Heavy (H)')

    # place inverted percentage values on the graph for each point inkluding the reductions for L, M, H and the reductions between L to M and M to H
    percent_font_size = 7
    # pair up the percentage reductions with their corresponding damage reduction towards the previous tier (L to M and M to H) and place them between the data points
    l_to_m_reductions = list(zip(m_reds, m_to_l_reds))
    m_to_h_reductions = list(zip(h_reds, h_to_m_reds))

    for i, txt in enumerate(l_reds):
        plt.annotate(f"-{txt:.1f}%", (pool_sizes[i], l_avgs[i]), textcoords="offset points", xytext=(0,10), ha='center', fontsize=percent_font_size)

    # annotate the percentage reduction reduction and the percentage reduction towards the previous tier (L to M) between the data points in a new line
    for i, data in enumerate(l_to_m_reductions):
        plt.annotate(f"(+{data[1]:.1f}%)\n-{data[0]:.1f}%", (pool_sizes[i], m_avgs[i]), textcoords="offset points", xytext=(0,10), ha='center', fontsize=percent_font_size, color='blue')
    for i, data in enumerate(m_to_h_reductions):
        plt.annotate(f"(+{data[1]:.1f}%)\n-{data[0]:.1f}%", (pool_sizes[i], h_avgs[i]), textcoords="offset points", xytext=(0,10), ha='center', fontsize=percent_font_size, color='red')

    plt.show()

simdata = []

dice_amounts = [2, 3, 4, 5, 6, 7, 8, 9, 10]
for dice_count in dice_amounts:
    result = run_upgraded_simulation_uniques([dice_count])
    simdata.append(result)

write_simdata_to_txt_file(simdata, filename="simdata.txt")

write_simdata_to_CSV_googleSheet(simdata, filename="simdata.csv")

visualize_simdata(simdata)