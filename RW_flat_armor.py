import numpy as np #type: ignore
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent / "simdata_logs"
LOG_DIR.mkdir(exist_ok=True)

np.random.seed(1)
sims = 10

l_group_label = "Light (L)"
m_group_label = "Medium (M)"
h_group_label = "Heavy (H)"

# ignored dice values for each armor type
l_dice_group = [1,2,3]
m_dice_group = [1,2,3,4,5,6]
h_dice_group = [1,2,3,4,5,6,7,8,9]

true_dmg = 0 # can never be reduced, so it is added to the final damage after all reductions


def run_RW_flat_armor_simulation(dice_counts):
    for dc in dice_counts:
        rolls = np.random.randint(1, 11, size=(sims, dc))
        base_sum = np.sum(rolls, axis=1)
        sorted_rolls = np.sort(rolls, axis=1) # ascending
        
        l_res1, l_res2, l_res3 = [], [], []
        m_res4, m_res5, m_res6 = [], [], []
        h_res7, h_res8, h_res9 = [], [], []
        
        for row in sorted_rolls:
            
            # --- Light (L): ignores dice results 1 then 2 and then 3, no halving, no threshold ---
            iteations = 3
            start_value = 1
            for i in range(iteations):
                keep_l = list(row)
                for i in range(len(keep_l)):
                    if keep_l[i] < start_value:
                        keep_l[i] = None
                if i == 1:
                    l_res1.append((sum([x for x in keep_l if x is not None]) + true_dmg))
                if i == 2:
                    l_res2.append((sum([x for x in keep_l if x is not None]) + true_dmg))
                if i == 3:
                    l_res3.append((sum([x for x in keep_l if x is not None]) + true_dmg))
                start_value += 1
            
            
            # --- Medium (M): ignores dice results below 4, then below 5, then below 6, no halving, no threshold ---
            iteations = 3
            start_value = 4
            for i in range(iteations):
                keep_m = list(row)
                for i in range(len(keep_m)):
                    if keep_m[i] < start_value:
                        keep_m[i] = None
                if i == 1:
                    m_res4.append((sum([x for x in keep_m if x is not None]) + true_dmg))
                if i == 2:
                    m_res5.append((sum([x for x in keep_m if x is not None]) + true_dmg))
                if i == 3:
                    m_res6.append((sum([x for x in keep_m if x is not None]) + true_dmg))
                start_value += 1


            # --- Heavy (H): ignores dice results below 7, then below 8, then below 9, no halving, no threshold ---
            iteations = 3
            start_value = 7
            for i in range(iteations):
                keep_h = list(row)
                for i in range(len(keep_h)):
                    if keep_h[i] < start_value:
                        keep_h[i] = None
                if i == 1:
                    h_res7.append((sum([x for x in keep_h if x is not None]) + true_dmg))
                if i == 2:
                    h_res8.append((sum([x for x in keep_h if x is not None]) + true_dmg))
                if i == 3:
                    h_res9.append((sum([x for x in keep_h if x is not None]) + true_dmg))
                start_value += 1

        base_mean = np.mean(base_sum)
        if true_dmg > 0:
            mean_nrml_dmg = base_mean + true_dmg
        else:
            mean_nrml_dmg = base_mean

        perc_red_l1 = (1 - np.mean(l_res1)/mean_nrml_dmg)*100
        perc_red_l2 = (1 - np.mean(l_res2)/mean_nrml_dmg)*100
        perc_red_l3 = (1 - np.mean(l_res3)/mean_nrml_dmg)*100
        perc_red_m4 = (1 - np.mean(m_res4)/mean_nrml_dmg)*100
        perc_red_m5 = (1 - np.mean(m_res5)/mean_nrml_dmg)*100
        perc_red_m6 = (1 - np.mean(m_res6)/mean_nrml_dmg)*100
        perc_red_h7 = (1 - np.mean(h_res7)/mean_nrml_dmg)*100
        perc_red_h8 = (1 - np.mean(h_res8)/mean_nrml_dmg)*100
        perc_red_h9 = (1 - np.mean(h_res9)/mean_nrml_dmg)*100

        print(f"=== Pool: {dc}d10 (Base Avg: {base_mean:.2f}) ===")
        for i in range(3):
            print(f"  {l_group_label}  (ignore < {i+1}): Avg {np.mean([l_res1, l_res2, l_res3][i]):.2f} (Red: {mean_nrml_dmg - np.mean([l_res1, l_res2, l_res3][i]):.2f}, { [perc_red_l1, perc_red_l2, perc_red_l3][i]:.1f}%)")
        for i in range(3):
            print(f"  {m_group_label} (ignore < {i+4}): Avg {np.mean([m_res4, m_res5, m_res6][i]):.2f} (Red: {mean_nrml_dmg - np.mean([m_res4, m_res5, m_res6][i]):.2f}, { [perc_red_m4, perc_red_m5, perc_red_m6][i]:.1f}%)")
        for i in range(3):
            print(f"  {h_group_label}  (ignore < {i+7}): Avg {np.mean([h_res7, h_res8, h_res9][i]):.2f} (Red: {mean_nrml_dmg - np.mean([h_res7, h_res8, h_res9][i]):.2f}, { [perc_red_h7, perc_red_h8, perc_red_h9][i]:.1f}%)")

        print()
        return {
            "pool_size": dc,
            "base_avg": base_mean,
            "avg_nrml_dmg": mean_nrml_dmg,
            "L_avg": np.mean([l_res1, l_res2, l_res3][2]),
            "M_avg": np.mean([m_res4, m_res5, m_res6][2]),
            "H_avg": np.mean([h_res7, h_res8, h_res9][2]),
            "L_1_red%": perc_red_l1,
            "L_2_red%": perc_red_l2,
            "L_3_red%": perc_red_l3,
            "M_4_red%": perc_red_m4,
            "M_5_red%": perc_red_m5,
            "M_6_red%": perc_red_m6,
            "H_7_red%": perc_red_h7,
            "H_8_red%": perc_red_h8,
            "H_9_red%": perc_red_h9,
            # "L2_to_L1_red%": perc_red_l2 - perc_red_l1,
            # "L3_to_L2_red%": perc_red_l3 - perc_red_l2,
            # "M4_to_L3_red%": perc_red_m4 - perc_red_l3,
            # "M5_to_M4_red%": perc_red_m5 - perc_red_m4,
            # "M6_to_M5_red%": perc_red_m6 - perc_red_m5,
            # "H7_to_M6_red%": perc_red_h7 - perc_red_m6,
            # "H8_to_H7_red%": perc_red_h8 - perc_red_h7,
            # "H9_to_H8_red%": perc_red_h9 - perc_red_h8
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
    avgs_w_true_dmg = [data["avg_nrml_dmg"] for data in simdata]
    l_1 = [data["L_1_red%"] for data in simdata]
    l_2 = [data["L_2_red%"] for data in simdata]
    l_3 = [data["L_3_red%"] for data in simdata]
    m_4 = [data["M_4_red%"] for data in simdata]
    m_5 = [data["M_5_red%"] for data in simdata]
    m_6 = [data["M_6_red%"] for data in simdata]
    h_7 = [data["H_7_red%"] for data in simdata]
    h_8 = [data["H_8_red%"] for data in simdata]
    h_9 = [data["H_9_red%"] for data in simdata]
    l_avgs = [data["L_avg"] for data in simdata]
    m_avgs = [data["M_avg"] for data in simdata]
    h_avgs = [data["H_avg"] for data in simdata]
    one_to_9data = [l_1, l_2, l_3, m_4, m_5, m_6, h_7, h_8, h_9]

    match vis_type:
        case "total_dmg_lines":
            #plt.figure(figsize=(15, 8.5))
            plt.figure(figsize=(18, 10))
            plt.title('Total Damage recieved - RW Flat Armor Simulation')
            plt.xlabel('Number of d10 dice - 10000 Simulations')
            plt.ylabel('Average Damage recieved')
            plt.legend()
            plt.grid(True)

            for v in one_to_9data:
                plt.plot(pool_sizes, v, marker='o', linestyle='dashed', alpha=0.5)

            plt.show()

simdata = []

dice_amounts = [2, 3, 4, 5, 6, 7, 8, 9, 10]
for dice_count in dice_amounts:
    result = run_RW_flat_armor_simulation([dice_count])
    simdata.append(result)

# write_simdata_to_txt_file(simdata)

# write_simdata_to_CSV_googleSheet(simdata)

visualize_simdata(simdata)