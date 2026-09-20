import numpy as np #type: ignore
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent / "simdata_logs"
LOG_DIR.mkdir(exist_ok=True)

np.random.seed(42)
sims = 10000
rounddown = True

l_threshold = 9
l_ignore_count = 0
l_reduction_count = 4

m_threshold = 10
m_ignore_count = 2
m_reduction_count = 2

h_ignore_count = 4
h_threshold = 11

true_dmg = 0 # can never be reduced, so it is added to the final damage after all reductions

armor_type_names = ["Normal","Special","Uniques"]


def run_d10_defense_simulation(dice_counts, rounddownYN=True):
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
            i_count = 0
            # Apply ignores first (best value)
            for i in range(len(keep_l)-1, 0, -1):
                if i_count >= l_ignore_count: break
                if keep_l[i] < l_threshold:
                    keep_l[i] = None
                    i_count += 1
            # Apply halving next
            h_count_l = 0
            for i in range(len(keep_l)-1, 0, -1):
                if h_count_l >= l_reduction_count: break
                if keep_l[i] is not None and keep_l[i] < l_threshold:
                    keep_l[i] = int(keep_l[i] / 2.0)
                    if not rounddownYN:
                        keep_l[i] = keep_l[i] + 1
                    h_count_l += 1
            l_res.append(sum([x for x in keep_l if x is not None]) + true_dmg)
            
            # --- Medium (M): Ignore 2, Halve 1, <10 ---
            keep_m = list(row)
            i_count = 0
            # Apply ignores first (best value)
            for i in range(len(keep_m)-1, 0, -1):
                if i_count >= m_ignore_count: break
                if keep_m[i] < m_threshold:
                    keep_m[i] = None
                    i_count += 1
            # Apply halving next
            h_count_m = 0
            for i in range(len(keep_m)-1, 0, -1):
                if h_count_m >= m_reduction_count: break
                if keep_m[i] is not None and keep_m[i] < m_threshold:
                    keep_m[i] = int(keep_m[i] / 2.0)
                    if not rounddownYN:
                        keep_m[i] = keep_m[i] + 1
                    h_count_m += 1
            m_res.append(sum([x for x in keep_m if x is not None]) + true_dmg)
            
            # --- Heavy (H): Ignore 3, no threshold ---
            keep_h = list(row)
            i_count_h = 0
            for i in range(len(keep_h)-1, 0, -1):
                if i_count_h >= h_ignore_count: break
                if keep_h[i] is not None and keep_h[i] < h_threshold:
                    keep_h[i] = None
                    i_count_h += 1
            h_res.append(sum([x for x in keep_h if x is not None]) + true_dmg)
            
        base_mean = np.mean(base_sum)
        if true_dmg > 0:
            mean_nrml_dmg = base_mean + true_dmg
        else:
            mean_nrml_dmg = base_mean

        perc_red_l = (1 - np.mean(l_res)/mean_nrml_dmg)*100
        perc_red_m = (1 - np.mean(m_res)/mean_nrml_dmg)*100
        perc_red_h = (1 - np.mean(h_res)/mean_nrml_dmg)*100
        m_to_l = perc_red_l - perc_red_m
        h_to_m = perc_red_m - perc_red_h
        print(f"=== Pool: {dc}d10 (Base Avg: {base_mean:.2f}) ===")
        print(f"  L: Avg {np.mean(l_res):.2f} (Red: {mean_nrml_dmg - np.mean(l_res):.2f}, {perc_red_l:.1f}%)")
        print(f"   % red.  L compared to M: {m_to_l:.1f}%")
        print(f"  M: Avg {np.mean(m_res):.2f} (Red: {mean_nrml_dmg - np.mean(m_res):.2f}, {perc_red_m:.1f}%)")
        print(f"   % red.  M compared to H: {h_to_m:.1f}%")
        print(f"  H: Avg {np.mean(h_res):.2f} (Red: {mean_nrml_dmg - np.mean(h_res):.2f}, {perc_red_h:.1f}%)")
        print()
        return {
            "pool_size": dc,
            "base_avg": base_mean,
            "avg_nrml_dmg": mean_nrml_dmg,
            "L_avg": np.mean(l_res),
            "M_avg": np.mean(m_res),
            "H_avg": np.mean(h_res),
            "L_red": perc_red_l,
            "M_red": perc_red_m,
            "H_red": perc_red_h,
            "L_to_M_red": m_to_l,
            "M_to_H_red": h_to_m
        }

def write_simdata_to_txt_file(simdata):
    """Capture simulation output and write to text file"""
    import sys
    from io import StringIO

    #add timestamp to the filename
    from datetime import datetime
    filename = LOG_DIR / f"d10battlesim_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"

    # redirect stdout to capture print output
    old_stdout = sys.stdout
    sys.stdout = mystdout = StringIO()

    # add base parameter header to the output
    print(f"Simulation Parameters:")
    print(f"  Number of simulations: {sims}")
    print(f"  L reduction count: {l_reduction_count}")
    print(f"  M reduction count: {m_reduction_count}")
    print(f"  M ignore count: {m_ignore_count}")
    print(f"  H ignore count: {h_ignore_count}")
    print()
    print(f"  L threshold: {l_threshold}")
    print(f"  M threshold: {m_threshold}")
    print(f"  H threshold: {h_threshold}")
    print()
    print(f"  Extra true damage (cannot be reduced): {true_dmg}")
    print()


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

def write_simdata_to_CSV_googleSheet(simdata):
    #wire the simdata to a CSV file

    import csv
    #add timestamp to the filename
    from datetime import datetime
    filename = LOG_DIR / f"d10battlesim_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"

    # work only on a copy of the simdata to avoid modifying the original data
    simdataCpy = [dict(data) for data in simdata]

    with open(filename, 'w', newline='') as csvfile:

        # include base parameters in the CSV file as a comment at the top of the file
        csvfile.write(f"# Simulation Parameters:\n")
        csvfile.write(f"#   Number of sims: {sims}\n")
        csvfile.write(f"#   L reduction count: {l_reduction_count}\n")
        csvfile.write(f"#   M reduction count: {m_reduction_count}\n")
        csvfile.write(f"#   M ignore count: {m_ignore_count}\n")
        csvfile.write(f"#   H ignore count: {h_ignore_count}\n")
        csvfile.write(f"#   L threshold: {l_threshold}\n")
        csvfile.write(f"#   M threshold: {m_threshold}\n")
        csvfile.write(f"#   H threshold: {h_threshold}\n")
        csvfile.write(f"#   True-dmg: {true_dmg}\n\n")

        # use semicolon as delimiter for CSV file
        writer = csv.writer(csvfile, delimiter=';')

        fieldnames = ["pool_size", "base_avg", "avg_nrml_dmg", "L_avg", "M_avg", "H_avg", "L_red", "M_red", "H_red", "L_to_M_red", "M_to_H_red"]
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
            for key in ["base_avg", "avg_nrml_dmg", "L_avg", "M_avg", "H_avg", "L_red", "M_red", "H_red", "L_to_M_red", "M_to_H_red"]:
                data[key] = str(data[key]).replace('.', ',')

        for data in simdataCpy:
            writer.writerow(data)

    print(f"Simdata got written successfully as CSV to {filename}.")



# visualize the data using matplotlib
def visualize_simdata(simdata, vis_type="total_dmg_lines"):
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
    avgs_w_true_dmg = [data["avg_nrml_dmg"] for data in simdata]

    match vis_type:
        case "total_dmg_lines":
            #plt.figure(figsize=(15, 8.5))
            plt.figure(figsize=(18, 10))
            plt.title(f'Total Damage recieved - {armor_type_names[2]} Upgrades')
            plt.xlabel(f'Number of d10 dice - {sims} Simulations')
            plt.ylabel('Average Damage recieved')
            plt.legend()
            plt.grid(True)

            # include base parameters in a legend box in the upper left corner of the graph
            base_params = f"Simulation Parameters:\n  Number of sims: {sims}\n  L reduction count: {l_reduction_count}\n  L irgnore count: {l_ignore_count}\n  M reduction count: {m_reduction_count}\n  M ignore count: {m_ignore_count}\n  H ignore count: {h_ignore_count}\n\n  L threshold: {l_threshold}\n  M threshold: {m_threshold}\n  H threshold: {h_threshold}\n\n  True-dmg: {true_dmg}\n\n Rounddown: {rounddown}"
            # base_params = f"Simulation Parameters:\n  Number of sims: {sims}\n  L reduction count: {l_reduction_count}\n  L irgnore count: {l_ignore_count}\n  M reduction count: {m_reduction_count}\n  M ignore count: {m_ignore_count}\n  H ignore count: {h_ignore_count}\n\n  L threshold: {l_threshold}\n  M threshold: {m_threshold}\n  H threshold: {h_threshold}\n\n  True-dmg: {true_dmg}\n\n Rounddown: {rounddown}\n\n M - roundDOWN!"
            plt.text(0.02, 0.98, base_params, transform=plt.gca().transAxes, fontsize=8, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

            if true_dmg > 0:
                base_line_style = (0, (1, 10))  # loosely dotted line
            else:
                base_line_style = 'solid'

            plt.plot(pool_sizes, base_avgs, marker='.', linestyle=base_line_style, label='Base Avg')
            plt.plot(pool_sizes, l_avgs, marker='o', label='Light (L)')
            plt.plot(pool_sizes, m_avgs, marker='s', label='Medium (M)')
            plt.plot(pool_sizes, h_avgs, marker='^', label='Heavy (H)')

            if true_dmg > 0: # add avergaes with true damage value as dashed lines
                plt.plot(pool_sizes, avgs_w_true_dmg, marker='.', linestyle='dashed', label='Base Avg + True Damage')

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

dice_amounts = [2, 3, 4, 5, 6, 7, 8]
for dice_count in dice_amounts:
    result = run_d10_defense_simulation([dice_count],rounddownYN=rounddown)
    simdata.append(result)

write_simdata_to_txt_file(simdata)

write_simdata_to_CSV_googleSheet(simdata)

visualize_simdata(simdata)