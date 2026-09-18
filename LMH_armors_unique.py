import numpy as np #type: ignore

np.random.seed(42)
sims = 10000
l_reduction_threshold = 9
l_reduction_count = 4

m_ignore_threshold = 10
m_ignore_count = 2
m_reduction_threshold = 10
m_reduction_count = 1

def run_upgraded_simulation(dice_counts):
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

def write_simdata_to_file(simdata, filename="simdata.txt"):
    """Capture simulation output and write to file"""
    import sys
    from io import StringIO
    
    old_stdout = sys.stdout
    sys.stdout = buffer = StringIO()
    
    for dice_count in [2, 3, 4, 5, 6, 7, 8, 9, 10]:
        run_upgraded_simulation([dice_count])
    
    output = buffer.getvalue()
    sys.stdout = old_stdout
    
    with open(filename, 'w') as f:
        f.write(output)
    
    print(output)
    print(f"Simulation data written to {filename}")


# visualize the data using matplotlib
def visualize_simdata(simdata):
    import matplotlib.pyplot as plt
    
    pool_sizes = [data["pool_size"] for data in simdata]
    l_avgs = [data["L_avg"] for data in simdata]
    m_avgs = [data["M_avg"] for data in simdata]
    h_avgs = [data["H_avg"] for data in simdata]
    
    plt.figure(figsize=(10, 6))
    plt.plot(pool_sizes, l_avgs, marker='o', label='Light (L)')
    plt.plot(pool_sizes, m_avgs, marker='s', label='Medium (M)')
    plt.plot(pool_sizes, h_avgs, marker='^', label='Heavy (H)')
    plt.xlabel('Pool Size')
    plt.ylabel('Average Value')
    plt.title('Simulation Results by Pool Size')
    plt.legend()
    plt.grid(True)
    plt.show()

simdata = []

dice_amounts = [2, 3, 4, 5, 6, 7, 8, 9, 10]
for dice_count in dice_amounts:
    result = run_upgraded_simulation([dice_count])
    simdata.append(result)

write_simdata_to_file(simdata, filename="simdata.txt")

visualize_simdata(simdata)