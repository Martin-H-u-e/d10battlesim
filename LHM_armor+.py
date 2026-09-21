import numpy as np #type: ignore
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent / "simdata_logs"
LOG_DIR.mkdir(exist_ok=True)

np.random.seed(42)
sims = 10000
rounddown = True

upgrade_tier_amounts = 3
armor_tier_names = ["Normal","Special","Uniques"]

TRUE_DMG = 0 # can never be reduced, so it is added to the final damage after all reductions

# light armor parameters per upgrade tier
L_HARDNESS          = [ 6, 6, 7]    # threshhold, if ignoring possible
L_IGNORE_DIE_COUNT  = [ 1, 2, 3]
l_reduction_count = None

# medium armor parameters per upgrade tier
M_HARDNESS          = [ 7, 8, 9]
M_IGNORE_DIE_COUNT  = [ 2, 3, 3]
M_TOTAL_IGNORE_ONCE = [False,False,False]
M_UNREST_HALVING_ONCE = [False,False,False]
m_reduction_count = None

# heavy armor parameters per upgrade tier
H_HARDNESS          = [ 9,10,10]
H_IGNORE_DIE_COUNT  = [ 2, 2, 3]
H_TOTAL_IGNORE_ONCE = [False,True,True]



def run_d10_defense_simulation(dice_counts, rounddownYN=True):
    simdata = []

    for tier in range(upgrade_tier_amounts):
        for dc in dice_counts:
            rolls = np.random.randint(1, 11, size=(sims, dc))
            base_sum = np.sum(rolls, axis=1)
            sorted_rolls = np.sort(rolls, axis=1) # ascending
            
            l_res, m_res, h_res = [], [], []
            
            for row in sorted_rolls:
                # Protected lowest die is row[0]
                # Eligible dice are row[1:]
                
                # --- Light (L) ---------------------------------------------- Light (L) ---
                keep_l = list(row)
                i_count = 0
                # Apply ignores first (best value)
                for i in range(len(keep_l)-1, 0, -1):
                    if i_count >= L_IGNORE_DIE_COUNT[tier]: break
                    if keep_l[i] < L_HARDNESS[tier]:
                        keep_l[i] = None
                        i_count += 1
                # Apply halving next
                h_count_l = 0
                for i in range(len(keep_l)-1, 0, -1):
                    if h_count_l >= (l_reduction_count or 0): break
                    if keep_l[i] is not None and keep_l[i] < L_HARDNESS[tier]:
                        keep_l[i] = int(keep_l[i] / 2.0)
                        if not rounddownYN:
                            keep_l[i] = keep_l[i] + 1
                        h_count_l += 1
                l_res.append(sum([x for x in keep_l if x is not None]) + TRUE_DMG)
                # ^^^ Light (L) ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ Light (L) ^^^

                # --- Medium (M) ---------------------------------------------- Medium(M) ---
                keep_m = list(row)
                i_count_m = 0
                # Apply ignores (best value remaining)
                for i in range(len(keep_m)-1, 0, -1):
                    # First: Apply possible unrestriced halbings first
                    if M_UNREST_HALVING_ONCE[tier] and i_count_m == 0:
                        if keep_m[i] is not None:
                            keep_m[i] = int(keep_m[i] / 2.0)
                        else:
                            break
                        if not rounddownYN:
                            keep_m[i] += 1
                        i_count_m += 1
                    if M_TOTAL_IGNORE_ONCE[tier] and i_count_m == 0:
                        keep_m[i] = None
                        i_count_m += 1
                    if i_count_m >= M_IGNORE_DIE_COUNT[tier]: break
                    if keep_m[i] is not None and keep_m[i] < M_HARDNESS[tier]:
                        keep_m[i] = None
                        i_count_m += 1
                m_res.append(sum([x for x in keep_m if x is not None]) + TRUE_DMG)
                # ^^^ Medium (M) ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ Medium(M) ^^^

                # --- Heavy (H) ---------------------------------------------- Heavy (H) ---
                keep_h = list(row)
                i_count_h = 0
                for i in range(len(keep_h)-1, 0, -1):
                    if H_TOTAL_IGNORE_ONCE[tier] and i_count_h == 0:
                        keep_h[i] = None
                        i_count_h += 1
                    if i_count_h >= H_IGNORE_DIE_COUNT[tier]: break
                    if keep_h[i] is not None and keep_h[i] < H_HARDNESS[tier]:
                        keep_h[i] = None
                        i_count_h += 1
                h_res.append(sum([x for x in keep_h if x is not None]) + TRUE_DMG)
                # ^^^ Heavy (H) ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ Heavy (H) ^^^
                
            base_mean = np.mean(base_sum)
            if TRUE_DMG > 0:
                mean_nrml_dmg = base_mean + TRUE_DMG
            else:
                mean_nrml_dmg = base_mean

            perc_red_l = (1 - np.mean(l_res)/mean_nrml_dmg)*100
            perc_red_m = (1 - np.mean(m_res)/mean_nrml_dmg)*100
            perc_red_h = (1 - np.mean(h_res)/mean_nrml_dmg)*100
            m_to_l = perc_red_l - perc_red_m
            h_to_m = perc_red_m - perc_red_h
            print(f"=== {armor_tier_names[tier]} | Pool: {dc}d10 (Base Avg: {base_mean:.2f}) ===")
            print(f"  L: Avg {np.mean(l_res):.2f} (Red: {mean_nrml_dmg - np.mean(l_res):.2f}, {perc_red_l:.1f}%)")
            print(f"   % red.  L compared to M: {m_to_l:.1f}%")
            print(f"  M: Avg {np.mean(m_res):.2f} (Red: {mean_nrml_dmg - np.mean(m_res):.2f}, {perc_red_m:.1f}%)")
            print(f"   % red.  M compared to H: {h_to_m:.1f}%")
            print(f"  H: Avg {np.mean(h_res):.2f} (Red: {mean_nrml_dmg - np.mean(h_res):.2f}, {perc_red_h:.1f}%)")
            print()
            simdata.append({
                "upgrade_tier": tier,
                "upgrade_tier_name": armor_tier_names[tier],
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
                })

    return simdata


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
    print(f"  M ignore count: {M_IGNORE_DIE_COUNT}")
    print(f"  H ignore count: {H_IGNORE_DIE_COUNT}")
    print()
    print(f"  L threshold: {L_HARDNESS}")
    print(f"  M threshold: {M_HARDNESS}")
    print(f"  H threshold: {H_HARDNESS}")
    print()
    print(f"  Extra true damage (cannot be reduced): {TRUE_DMG}")
    print()


    # print the simdata to stdout
    for data in simdata:
        print(f"=== {data['upgrade_tier_name']} | Pool: {data['pool_size']}d10 (Base Avg: {data['base_avg']:.2f}) ===")
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
        csvfile.write(f"#   M ignore count: {M_IGNORE_DIE_COUNT}\n")
        csvfile.write(f"#   H ignore count: {H_IGNORE_DIE_COUNT}\n")
        csvfile.write(f"#   L threshold: {L_HARDNESS}\n")
        csvfile.write(f"#   M threshold: {M_HARDNESS}\n")
        csvfile.write(f"#   H threshold: {H_HARDNESS}\n")
        csvfile.write(f"#   True-dmg: {TRUE_DMG}\n\n")

        # use semicolon as delimiter for CSV file
        writer = csv.writer(csvfile, delimiter=';')

        fieldnames = ["upgrade_tier", "upgrade_tier_name", "pool_size", "base_avg", "avg_nrml_dmg", "L_avg", "M_avg", "H_avg", "L_red", "M_red", "H_red", "L_to_M_red", "M_to_H_red"]
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
def visualize_simdata(simdata, display_groups_separately=False):
    import matplotlib.pyplot as plt

    tiers = {
        tier: sorted(
            (data for data in simdata if data["upgrade_tier"] == tier),
            key=lambda data: data["pool_size"],
        )
        for tier in range(upgrade_tier_amounts)
    }
    tier_colors = {
        "L": ["#a5d6a7", "#66bb6a", "#2e7d32"],
        "M": ["#90caf9", "#42a5f5", "#1565c0"],
        "H": ["#ef9a9a", "#ef5350", "#c62828"],
    }
    armor_fields = {"L": "L_avg", "M": "M_avg", "H": "H_avg"}
    markers = {"L": "o", "M": "s", "H": "^"}

    base_tier = next((records for records in tiers.values() if records), [])
    base_params = f"Simulation Parameters:\n  Number of sims: {sims}\n  L reduction count: {l_reduction_count}\n  L ignore count: {L_IGNORE_DIE_COUNT}\n  M reduction count: {m_reduction_count}\n  M ignore count: {M_IGNORE_DIE_COUNT}\n  H ignore count: {H_IGNORE_DIE_COUNT}\n\n  L threshold: {L_HARDNESS}\n  M threshold: {M_HARDNESS}\n  H threshold: {H_HARDNESS}\n\n  True-dmg: {TRUE_DMG}\n\n  Rounddown: {rounddown}"

    def plot_group(armor_type=None):
        plt.figure(figsize=(18, 10))
        title = "All Upgrade Tiers" if armor_type is None else f"{armor_type} Armor - All Upgrade Tiers"
        plt.title(f"Total Damage received - {title}")
        plt.xlabel("Attack d10 pool sizes")
        plt.ylabel("Average Damage received")
        plt.grid(True)

        pool_sizes = [data["pool_size"] for data in base_tier]
        plt.plot(
            pool_sizes,
            [data["base_avg"] for data in base_tier],
            color="black",
            marker=".",
            linestyle=":",
            label="Base Avg",
        )

        groups = armor_fields if armor_type is None else {armor_type: armor_fields[armor_type]}
        for tier, records in tiers.items():
            if not records:
                continue
            tier_name = records[0]["upgrade_tier_name"]
            tier_pool_sizes = [data["pool_size"] for data in records]
            for group_name, field in groups.items():
                plt.plot(
                    tier_pool_sizes,
                    [data[field] for data in records],
                    color=tier_colors[group_name][tier],
                    marker=markers[group_name],
                    label=f"{tier_name} {group_name}",
                )

        if TRUE_DMG > 0:
            plt.plot(
                pool_sizes,
                [data["avg_nrml_dmg"] for data in base_tier],
                color="black",
                marker=".",
                linestyle="--",
                label="Base Avg + True Damage",
            )

        plt.text(
            0.02,
            0.98,
            base_params,
            transform=plt.gca().transAxes,
            fontsize=8,
            verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
        )
        plt.legend()

    if display_groups_separately:
        for armor_type in armor_fields:
            plot_group(armor_type)
    else:
        plot_group()

    plt.show()


def visualize_simdata_by_upgrade_tier(simdata):
    import matplotlib.pyplot as plt

    tier_colors = {
        "L": ["#a5d6a7", "#66bb6a", "#2e7d32"],
        "M": ["#90caf9", "#42a5f5", "#1565c0"],
        "H": ["#ef9a9a", "#ef5350", "#c62828"],
    }
    armor_fields = {"L": "L_avg", "M": "M_avg", "H": "H_avg"}
    armor_labels = {"L": "Light", "M": "Medium", "H": "Heavy"}
    markers = {"L": "o", "M": "s", "H": "^"}
    output_files = []

    for tier in range(upgrade_tier_amounts):
        tier_data = sorted(
            (data for data in simdata if data["upgrade_tier"] == tier),
            key=lambda data: data["pool_size"],
        )
        if not tier_data:
            continue

        tier_name = tier_data[0]["upgrade_tier_name"]
        pool_sizes = [data["pool_size"] for data in tier_data]
        base_avgs = [data["base_avg"] for data in tier_data]

        figure, axis = plt.subplots(figsize=(18, 10))
        axis.set_title(f"Total Damage received - {tier_name} Upgrade Tier")
        axis.set_xlabel("Attack d10 pool sizes")
        axis.set_ylabel("Average Damage received")
        axis.set_ylim(0, 45)
        axis.grid(True)
        axis.plot(
            pool_sizes,
            base_avgs,
            color="black",
            marker=".",
            linestyle=":",
            label="Base Avg",
        )

        for armor_type, field in armor_fields.items():
            axis.plot(
                pool_sizes,
                [data[field] for data in tier_data],
                color=tier_colors[armor_type][tier],
                marker=markers[armor_type],
                label=f"{armor_labels[armor_type]} ({armor_type})",
            )

        if TRUE_DMG > 0:
            axis.plot(
                pool_sizes,
                [data["avg_nrml_dmg"] for data in tier_data],
                color="black",
                marker=".",
                linestyle="--",
                label="Base Avg + True Damage",
            )

        base_params = f"Simulation Parameters:\n  Number of sims: {sims}\n  L reduction count: {l_reduction_count}\n  L ignore count: {L_IGNORE_DIE_COUNT}\n  M reduction count: {m_reduction_count}\n  M ignore count: {M_IGNORE_DIE_COUNT}\n  M ignore once: {M_TOTAL_IGNORE_ONCE}\n  H ignore count: {H_IGNORE_DIE_COUNT}\n  H ignore once: {H_TOTAL_IGNORE_ONCE}\n\n  L threshold: {L_HARDNESS}\n  M threshold: {M_HARDNESS}\n  H threshold: {H_HARDNESS}\n\n  True-dmg: {TRUE_DMG}\n\n  Rounddown: {rounddown}"
        axis.text(
            0.02,
            0.98,
            base_params,
            transform=axis.transAxes,
            fontsize=8,
            verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
        )
        axis.legend()
        figure.tight_layout()

        output_file = LOG_DIR / f"d10battlesim_{tier_name.lower()}_upgrade_tier.svg"
        figure.savefig(output_file, format="svg", bbox_inches="tight")
        output_files.append(output_file)
        plt.close(figure)

    print("Tier visualizations saved to:")
    for output_file in output_files:
        print(f"  {output_file}")


def visualize_blocked_damage_bar_chart(simdata):
    import matplotlib.pyplot as plt

    tier_colors = {
        "L": ["#a5d6a7", "#66bb6a", "#2e7d32"],
        "M": ["#90caf9", "#42a5f5", "#1565c0"],
        "H": ["#ef9a9a", "#ef5350", "#c62828"],
    }
    armor_fields = {"L": "L_avg", "M": "M_avg", "H": "H_avg"}
    pool_sizes = sorted({data["pool_size"] for data in simdata})
    records_by_key = {
        (data["upgrade_tier"], data["pool_size"]): data for data in simdata
    }
    positions = np.arange(len(pool_sizes))
    bottoms = np.zeros(len(pool_sizes))
    bar_width = 0.8
    base_averages = np.array([
        records_by_key[(0, pool_size)]["base_avg"] for pool_size in pool_sizes
    ])

    plt.figure(figsize=(18, 10))
    plt.hlines(
        base_averages,
        positions - bar_width / 2,
        positions + bar_width / 2,
        color="black",
        linewidth=2,
        label="Total Average Damage (no reduction)",
    )
    for armor_type, field in armor_fields.items():
        for tier in range(upgrade_tier_amounts):
            blocked_damage = np.array([
                data["base_avg"] - data[field]
                for pool_size in pool_sizes
                for data in [records_by_key[(tier, pool_size)]]
            ])
            blocked_percentages = blocked_damage / base_averages * 100
            tier_name = records_by_key[(tier, pool_sizes[0])]["upgrade_tier_name"]
            plt.bar(
                positions,
                blocked_damage,
                bottom=bottoms,
                color=tier_colors[armor_type][tier],
                width=bar_width,
                label=f"{tier_name} {armor_type}",
            )
            for position, bottom, blocked, percentage in zip(
                positions, bottoms, blocked_damage, blocked_percentages
            ):
                if blocked > 0:
                    plt.text(
                        float(position),
                        bottom + blocked / 2,
                        f"{percentage:.1f}%",
                        ha="center",
                        va="center",
                        fontsize=8,
                    )
            bottoms += blocked_damage

    plt.xticks(positions, [f"{pool_size}d10" for pool_size in pool_sizes])
    plt.xlabel("Attack d10 pool sizes")
    plt.ylabel("Damage blocked")
    plt.title("Damage Blocked by All Armor Tiers")
    plt.grid(axis="y", alpha=0.3)
    plt.legend()
    plt.tight_layout()

    output_file = LOG_DIR / f"d10battlesim_{tier_name.lower()}_9bar.svg"
    plt.savefig(output_file, format="svg", bbox_inches="tight")
    plt.close()

    print(" 9 bar chart saved to:")
    print(f"  {output_file}")


def visualize_blocked_damage_grouped_bar_chart(
    simdata,
    armor_types=None,
    selected_tiers=None,
):
    import matplotlib.pyplot as plt

    tier_colors = {
        "L": ["#a5d6a7", "#66bb6a", "#2e7d32"],
        "M": ["#90caf9", "#42a5f5", "#1565c0"],
        "H": ["#ef9a9a", "#ef5350", "#c62828"],
    }
    armor_fields = {"L": "L_avg", "M": "M_avg", "H": "H_avg"}
    armor_labels = {"L": "Light", "M": "Medium", "H": "Heavy"}
    if armor_types is None:
        armor_types = list(armor_fields)
    else:
        armor_types = list(armor_types)

    invalid_armor_types = set(armor_types) - set(armor_fields)
    if invalid_armor_types:
        raise ValueError(f"Unknown armor types: {sorted(invalid_armor_types)}")

    selected_tiers = selected_tiers or {}
    invalid_tier_types = set(selected_tiers) - set(armor_fields)
    if invalid_tier_types:
        raise ValueError(f"Unknown armor types in selected_tiers: {sorted(invalid_tier_types)}")

    displayed_armor_tiers = []
    for armor_type in armor_types:
        tier = selected_tiers.get(armor_type)
        if tier is None:
            displayed_armor_tiers.extend(
                (armor_type, tier_index)
                for tier_index in range(upgrade_tier_amounts)
            )
        elif not isinstance(tier, int) or not 0 <= tier < upgrade_tier_amounts:
            raise ValueError(
                f"Tier for {armor_type} must be an integer from "
                f"0 to {upgrade_tier_amounts - 1}"
            )
        else:
            displayed_armor_tiers.append((armor_type, tier))

    if not displayed_armor_tiers:
        raise ValueError("At least one armor type must be selected")

    pool_sizes = sorted({data["pool_size"] for data in simdata})
    records_by_key = {
        (data["upgrade_tier"], data["pool_size"]): data for data in simdata
    }

    group_positions = np.arange(len(pool_sizes), dtype=float)
    bar_width = min(0.8 / len(displayed_armor_tiers), 0.2)
    base_averages = np.array([
        records_by_key[(0, pool_size)]["base_avg"] for pool_size in pool_sizes
    ])

    plt.figure(figsize=(18, 10))
    first_position = -(len(displayed_armor_tiers) - 1) * bar_width / 2
    for bar_index, (armor_type, tier) in enumerate(displayed_armor_tiers):
        field = armor_fields[armor_type]
        positions = group_positions + first_position + bar_index * bar_width
        blocked_damage = np.array([
            records_by_key[(tier, pool_size)]["base_avg"]
            - records_by_key[(tier, pool_size)][field]
            for pool_size in pool_sizes
        ])
        blocked_percentages = blocked_damage / base_averages * 100
        tier_name = records_by_key[(tier, pool_sizes[0])]["upgrade_tier_name"]

        plt.bar(
            positions,
            blocked_damage,
            width=bar_width,
            color=tier_colors[armor_type][tier],
            label=f"{tier_name} {armor_labels[armor_type]}",
        )

        for position, blocked, percentage in zip(
            positions, blocked_damage, blocked_percentages
        ):
            if blocked > 0:
                plt.text(
                    float(position),
                    blocked / 2,
                    f"{percentage:.1f}%",
                    ha="center",
                    va="center",
                    fontsize=7,
                )
        plt.hlines(
            base_averages,
            positions - bar_width / 2,
            positions + bar_width / 2,
            color="black",
            linewidth=1.0,
        )

    for group_position, base_average in zip(group_positions, base_averages):
        plt.text(
            float(group_position),
            base_average + 0.15,
            "total avg. dmg",
            ha="center",
            va="bottom",
            fontsize=7,
            color="black",
            rotation=0,
        )

    plt.xticks(
        group_positions,
        [f"{pool_size}d10" for pool_size in pool_sizes],
    )
    plt.xlabel("Attack d10 pool sizes")
    plt.ylabel("Damage blocked")
    plt.title("Damage Blocked by Armor Group and Upgrade Tier")
    plt.grid(axis="y", alpha=0.3)
    base_params = f"Simulation Parameters:\n  Number of sims: {sims}\n  L reduction count: {l_reduction_count}\n  L ignore count: {L_IGNORE_DIE_COUNT}\n  M reduction count: {m_reduction_count}\n  M ignore count: {M_IGNORE_DIE_COUNT}\n  M ignore once: {M_TOTAL_IGNORE_ONCE}\n  M halve once: {M_UNREST_HALVING_ONCE}\n  H ignore count: {H_IGNORE_DIE_COUNT}\n  H ignore once: {H_TOTAL_IGNORE_ONCE}\n\n  L threshold: {L_HARDNESS}\n  M threshold: {M_HARDNESS}\n  H threshold: {H_HARDNESS}\n\n  True-dmg: {TRUE_DMG}\n\n  Rounddown: {rounddown}"
    plt.text(
        0.02,
        0.98,
        base_params,
        transform=plt.gca().transAxes,
        fontsize=8,
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
    )
    plt.legend()
    plt.tight_layout()

    output_file = LOG_DIR / f"d10battlesim_{tier_name.lower()}_9bar.svg"
    plt.savefig(output_file, format="svg", bbox_inches="tight")
    plt.close() 

    print(" 9 bar chart saved to:")
    print(f"  {output_file}")


dice_amounts = [2, 3, 4, 5, 6, 7, 8]
simdata = run_d10_defense_simulation(dice_amounts, rounddownYN=rounddown)

# write_simdata_to_txt_file(simdata)
# write_simdata_to_CSV_googleSheet(simdata)

# visualize_simdata(simdata, display_groups_separately=True)
# visualize_simdata_by_upgrade_tier(simdata) # <---

# visualize_blocked_damage_bar_chart(simdata)

visualize_blocked_damage_grouped_bar_chart(simdata)
# visualize_blocked_damage_grouped_bar_chart(simdata,armor_types=["L","M","H"],selected_tiers={"L":1,"M":1,"H":1})