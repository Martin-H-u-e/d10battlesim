import numpy as np #type: ignore
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent / "simdata_logs"
LOG_DIR.mkdir(exist_ok=True)

np.random.seed(42)
# rnd_seed = np.random.randint(1, 100)
# np.random.seed(rnd_seed)
sims = 200
rounddown = True
simulate_playerHP = True

upgrade_tier_amounts = 3
armor_tier_names = ["Normal","Special","Uniques"]
L_desired_avg_5d10_armor_values_perTier = [12.00, 39.50, 54.60]
M_desired_avg_5d10_armor_values_perTier = [31.00, 54.65, 65.50]
H_desired_avg_5d10_armor_values_perTier = [47.00, 63.70, 72.10]

TRUE_DMG = 0 # can never be reduced, so it is added to the final damage after all reductions
USE_LOWEST_DIE_MAX = True
PLAYER_BASE_HP = 100

# light armor parameters per upgrade tier
L_HARDNESS          = [ 6, 8, 9]    # threshhold, if ignoring possible
L_IGNORE_DIE_COUNT  = [ 2, 3, 3]
L_LOWEST_DIE_MAX    = [ 8, 5, 3]
# L_LOWEST_DIE_MAX    = [ 5, 5, 5]
l_reduction_count = None

# medium armor parameters per upgrade tier
M_HARDNESS          = [ 7, 9,  10]
M_IGNORE_DIE_COUNT  = [ 3, 3,  3]
M_LOWEST_DIE_MAX    = [ 7, 4,  2]
# M_LOWEST_DIE_MAX    = [ 5, 5, 5]

M_TOTAL_IGNORE_ONCE = [False,False,False]
M_UNREST_HALVING_ONCE = [False,False,False]
m_reduction_count = None

# heavy armor parameters per upgrade tier
H_HARDNESS          = [ 8, 9, 10]
H_IGNORE_DIE_COUNT  = [ 4, 4, 4]
H_HALVING_DIE_COUNT = [ 0, 0, 0]
H_TOTAL_IGNORE_ONCE = [False,False,False]
H_LOWEST_DIE_MAX    = [6, 3, 1]
# H_LOWEST_DIE_MAX    = [ 5, 5, 5]

def reduce_dice_for_tier(row, tier, rounddownYN):
    keep_l = list(row)
    if USE_LOWEST_DIE_MAX and keep_l[0] > L_LOWEST_DIE_MAX[tier]:
        keep_l[0] = L_LOWEST_DIE_MAX[tier]
    ignore_count_l = 0
    for i in range(len(keep_l) - 1, 0, -1):
        if ignore_count_l >= L_IGNORE_DIE_COUNT[tier]:
            break
        if keep_l[i] < L_HARDNESS[tier]:
            keep_l[i] = None
            ignore_count_l += 1
    halve_count_l = 0
    for i in range(len(keep_l) - 1, 0, -1):
        if halve_count_l >= (l_reduction_count or 0):
            break
        if keep_l[i] is not None and keep_l[i] < L_HARDNESS[tier]:
            keep_l[i] = int(keep_l[i] / 2.0)
            if not rounddownYN:
                keep_l[i] += 1
            halve_count_l += 1
    light_damage = sum(value for value in keep_l if value is not None) + TRUE_DMG

    keep_m = list(row)
    if USE_LOWEST_DIE_MAX and keep_m[0] > M_LOWEST_DIE_MAX[tier]:
        keep_m[0] = M_LOWEST_DIE_MAX[tier]
    ignore_count_m = 0
    for i in range(len(keep_m) - 1, 0, -1):
        if M_UNREST_HALVING_ONCE[tier] and ignore_count_m == 0:
            if keep_m[i] is not None:
                keep_m[i] = int(keep_m[i] / 2.0)
            else:
                break
            if not rounddownYN:
                keep_m[i] += 1
            ignore_count_m += 1
        if M_TOTAL_IGNORE_ONCE[tier] and ignore_count_m == 0:
            keep_m[i] = None
            ignore_count_m += 1
        if ignore_count_m >= M_IGNORE_DIE_COUNT[tier]:
            break
        if keep_m[i] is not None and keep_m[i] < M_HARDNESS[tier]:
            keep_m[i] = None
            ignore_count_m += 1
    medium_damage = sum(value for value in keep_m if value is not None) + TRUE_DMG

    keep_h = list(row)
    if USE_LOWEST_DIE_MAX and keep_h[0] > H_LOWEST_DIE_MAX[tier]:
        keep_h[0] = H_LOWEST_DIE_MAX[tier]
    ignore_count_h = 0
    for i in range(len(keep_h) - 1, 0, -1):
        if H_TOTAL_IGNORE_ONCE[tier] and ignore_count_h == 0:
            keep_h[i] = None
            ignore_count_h += 1
        if ignore_count_h >= H_IGNORE_DIE_COUNT[tier]:
            break
        if keep_h[i] is not None and keep_h[i] < H_HARDNESS[tier]:
            keep_h[i] = None
            ignore_count_h += 1
    halve_count_h = 0
    for i in range(len(keep_h) - 1, 0, -1):
        if halve_count_h >= H_HALVING_DIE_COUNT[tier]:
            break
        if keep_h[i] is not None and keep_h[i] < H_HARDNESS[tier]:
            keep_h[i] = int(keep_h[i] / 2.0)
            if not rounddownYN:
                keep_h[i] += 1
            halve_count_h += 1
    heavy_damage = sum(value for value in keep_h if value is not None) + TRUE_DMG

    return light_damage, medium_damage, heavy_damage


SIMPLE_TIER_THRESHOLDS = {
    "L": [2, 3, 4],
    "M": [5, 6, 7],
    "H": [8, 9, 10],
}


def reduce_dice_for_tier_simple(row, tier, rounddownYN=True):
    """Apply the simplified armor rule set: ignore every die result below the threshold.

    Rules are:
      L1: 2, L2: 3, L3: 4
      M1: 5, M2: 6, M3: 7
      H1: 8, H2: 9, H3: 10

    The `rounddownYN` argument is accepted for compatibility with the existing API,
    but the simplified model does not use any halving or layered reduction rules.
    """
    if not 0 <= tier < upgrade_tier_amounts:
        raise ValueError(f"tier must be between 0 and {upgrade_tier_amounts - 1}")

    keep_l = [value for value in row if value >= SIMPLE_TIER_THRESHOLDS["L"][tier]]
    keep_m = [value for value in row if value >= SIMPLE_TIER_THRESHOLDS["M"][tier]]
    keep_h = [value for value in row if value >= SIMPLE_TIER_THRESHOLDS["H"][tier]]

    light_damage = sum(keep_l) + TRUE_DMG
    medium_damage = sum(keep_m) + TRUE_DMG
    heavy_damage = sum(keep_h) + TRUE_DMG
    return light_damage, medium_damage, heavy_damage


def simulate_player_hp_survival(
    dice_counts,
    chunks,
    rounddownYN=True,
    reduction_func=None,
):
    if reduction_func is None:
        reduction_func = reduce_dice_for_tier

    armor_types = ("L", "M", "H")
    survival_totals = {
        (pool_size, tier, armor_type): 0
        for pool_size in dice_counts
        for tier in range(upgrade_tier_amounts)
        for armor_type in armor_types
    }
    base_survival_totals = {pool_size: 0 for pool_size in dice_counts}

    for _ in range(chunks):
        hit_points = {
            key: PLAYER_BASE_HP for key in survival_totals
        }
        base_hit_points = {
            pool_size: PLAYER_BASE_HP for pool_size in dice_counts
        }
        survived_rounds = {}
        base_survived_rounds = {}
        round_number = 0

        while (
            any(current_hp >= 1 for current_hp in hit_points.values())
            or any(current_hp >= 1 for current_hp in base_hit_points.values())
        ):
            round_number += 1
            for pool_size in dice_counts:
                active_players = [
                    key for key, current_hp in hit_points.items()
                    if key[0] == pool_size and current_hp >= 1
                ]
                base_is_alive = base_hit_points[pool_size] >= 1
                if not active_players and not base_is_alive:
                    continue

                rolled_dice = np.sort(np.random.randint(1, 11, size=pool_size))
                if base_is_alive:
                    base_hit_points[pool_size] -= (
                        int(np.sum(rolled_dice)) + TRUE_DMG
                    )
                    if base_hit_points[pool_size] < 1:
                        base_survived_rounds[pool_size] = round_number - 1
                if not active_players:
                    continue

                for tier in range(upgrade_tier_amounts):
                    damages = reduction_func(rolled_dice, tier, rounddownYN)
                    for armor_type, damage in zip(armor_types, damages):
                        key = (pool_size, tier, armor_type)
                        if hit_points[key] < 1:
                            continue
                        hit_points[key] -= damage
                        if hit_points[key] < 1:
                            survived_rounds[key] = round_number - 1

        for key, rounds in survived_rounds.items():
            survival_totals[key] += rounds
        for pool_size, rounds in base_survived_rounds.items():
            base_survival_totals[pool_size] += rounds

    survival_averages = {
        key: total_rounds / chunks
        for key, total_rounds in survival_totals.items()
    }
    base_survival_averages = {
        pool_size: total_rounds / chunks
        for pool_size, total_rounds in base_survival_totals.items()
    }
    return survival_averages, base_survival_averages


def run_d10_defense_simulation(
    dice_counts,
    rounddownYN=True,
    simulate_playerHP=False,
    run_simple_sim=False,
):
    dice_counts = list(dice_counts)
    simdata = []
    reduction_func = (
        reduce_dice_for_tier_simple if run_simple_sim else reduce_dice_for_tier
    )
    rolls_by_pool_size = {
        dc: np.random.randint(1, 11, size=(sims, dc))
        for dc in dice_counts
    }

    for tier in range(upgrade_tier_amounts):
        for dc in dice_counts:
            rolls = rolls_by_pool_size[dc]
            base_sum = np.sum(rolls, axis=1)
            sorted_rolls = np.sort(rolls, axis=1) # ascending
            
            l_res, m_res, h_res = [], [], []

            for row in sorted_rolls:
                light_damage, medium_damage, heavy_damage = reduction_func(
                    row, tier, rounddownYN
                )
                l_res.append(light_damage)
                m_res.append(medium_damage)
                h_res.append(heavy_damage)

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

    if simulate_playerHP:
        survival_averages, base_survival_averages = simulate_player_hp_survival(
            dice_counts,
            chunks=sims,
            rounddownYN=rounddownYN,
            reduction_func=reduction_func,
        )
        for data in simdata:
            for armor_type in ("L", "M", "H"):
                data[f"{armor_type}_survived_rounds"] = survival_averages[
                    (data["pool_size"], data["upgrade_tier"], armor_type)
                ]
            data["base_survived_rounds"] = base_survival_averages[
                data["pool_size"]
            ]

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
        survival_fields = [
            f"{armor_type}_survived_rounds"
            for armor_type in ("L", "M", "H")
        ] + ["base_survived_rounds"]
        if simdataCpy and all(
            field in simdataCpy[0] for field in survival_fields
        ):
            fieldnames.extend(survival_fields)
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
            numeric_fields = [
                "base_avg", "avg_nrml_dmg", "L_avg", "M_avg", "H_avg",
                "L_red", "M_red", "H_red", "L_to_M_red", "M_to_H_red",
            ]
            numeric_fields.extend(
                field for field in survival_fields if field in data
            )
            for key in numeric_fields:
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


def visualize_blocked_damage_grouped_bar_chart(
    simdata,
    armor_types=None,
    selected_tiers=None,
    y_max=60,
    show_percentage_offset=True,
    group_legend_by_armor_type=False,
    show_survived_rounds=False,
    fix_survived_rounds_y_max=False,
    survived_rounds_y_max=25,
):
    import matplotlib.pyplot as plt

    tier_colors = {
        "L": ["#a5d6a7", "#66bb6a", "#2e7d32"],
        "M": ["#90caf9", "#42a5f5", "#1565c0"],
        "H": ["#ef9a9a", "#ef5350", "#c62828"],
    }
    armor_fields = {"L": "L_avg", "M": "M_avg", "H": "H_avg"}
    armor_labels = {"L": "Light", "M": "Medium", "H": "Heavy"}
    target_mitigation = {
        "L": L_desired_avg_5d10_armor_values_perTier,
        "M": M_desired_avg_5d10_armor_values_perTier,
        "H": H_desired_avg_5d10_armor_values_perTier,
    }
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
    displayed_bar_count = len(displayed_armor_tiers) + int(show_survived_rounds)
    bar_width = min(0.8 / displayed_bar_count, 0.2)
    base_averages = np.array([
        records_by_key[(0, pool_size)]["base_avg"] for pool_size in pool_sizes
    ])
    if TRUE_DMG > 0:
        total_averages = base_averages + TRUE_DMG
        base_average_label = "base total avg."
    else:
        total_averages = base_averages
        base_average_label = "total avg. dmg"
    visible_reference_lines = total_averages <= y_max
    chart_y_max = y_max
    if show_survived_rounds:
        if fix_survived_rounds_y_max:
            chart_y_max = survived_rounds_y_max
        else:
            survival_values = [
                records_by_key[(tier, pool_size)][f"{armor_type}_survived_rounds"]
                for armor_type, tier in displayed_armor_tiers
                for pool_size in pool_sizes
            ]
            survival_values.extend(
                records_by_key[(0, pool_size)]["base_survived_rounds"]
                for pool_size in pool_sizes
            )
            chart_y_max = max(1, int(np.ceil(max(survival_values) * 1.15)))

    plt.figure(figsize=(17, 8.9))
    first_position = -(displayed_bar_count - 1) * bar_width / 2
    armor_position_offset = int(show_survived_rounds)
    bar_positions = {}
    bar_tops = {}
    for bar_index, (armor_type, tier) in enumerate(displayed_armor_tiers):
        field = armor_fields[armor_type]
        positions = (
            group_positions
            + first_position
            + (bar_index + armor_position_offset) * bar_width
        )
        if show_survived_rounds:
            bar_values = np.array([
                records_by_key[(tier, pool_size)][
                    f"{armor_type}_survived_rounds"
                ]
                for pool_size in pool_sizes
            ])
            blocked_percentages = np.zeros(len(pool_sizes))
        else:
            blocked_damage = np.array([
                records_by_key[(tier, pool_size)]["avg_nrml_dmg"]
                - records_by_key[(tier, pool_size)][field]
                for pool_size in pool_sizes
            ])
            bar_values = blocked_damage
            blocked_percentages = blocked_damage / total_averages * 100
        bar_positions[(armor_type, tier)] = positions
        bar_tops[(armor_type, tier)] = bar_values
        tier_name = records_by_key[(tier, pool_sizes[0])]["upgrade_tier_name"]

        plt.bar(
            positions,
            bar_values,
            width=bar_width,
            color=tier_colors[armor_type][tier],
            label=f"{tier_name} {armor_labels[armor_type]}",
        )

        for bar_index, (position, bar_value, pool_size) in enumerate(
            zip(positions, bar_values, pool_sizes)
        ):
            if bar_value > 0:
                if show_survived_rounds:
                    base_rounds = records_by_key[(0, pool_size)][
                        "base_survived_rounds"
                    ]
                    percent_increase = (bar_value / base_rounds - 1) * 100
                    label = f"{bar_value:.1f}\n{percent_increase:+.1f}%"
                else:
                    percentage = blocked_percentages[bar_index]
                    label = f"{percentage:.1f}%"
                    if show_percentage_offset and pool_size == 5:
                        target = target_mitigation[armor_type][tier]
                        difference = percentage - target
                        label = (
                            f"{percentage:.1f}%\nTarget {target:.1f}%\n"
                            f"{difference:+.1f} pp"
                        )
                plt.text(
                    float(position),
                    bar_value / 2,
                    label,
                    ha="center",
                    va="center",
                    fontsize=6 if pool_size == 5 else 7,
                )
        if not show_survived_rounds:
            plt.hlines(
                total_averages[visible_reference_lines],
                positions[visible_reference_lines] - bar_width / 2,
                positions[visible_reference_lines] + bar_width / 2,
                color="black",
                linewidth=1.0,
            )
            if TRUE_DMG > 0:
                plt.hlines(
                    base_averages[visible_reference_lines],
                    positions[visible_reference_lines] - bar_width / 2,
                    positions[visible_reference_lines] + bar_width / 2,
                    color="black",
                    linestyle=":",
                    linewidth=1.0,
                )

    if show_survived_rounds:
        base_survived_rounds = np.array([
            records_by_key[(0, pool_size)]["base_survived_rounds"]
            for pool_size in pool_sizes
        ])
        base_positions = group_positions + first_position
        plt.bar(
            base_positions,
            base_survived_rounds,
            width=bar_width,
            color="#555555",
            label="No Armor",
        )
        for position, rounds in zip(base_positions, base_survived_rounds):
            if rounds > 0:
                plt.text(
                    float(position),
                    rounds / 2,
                    f"{rounds:.1f}",
                    ha="center",
                    va="center",
                    fontsize=7,
                    color="white",
                )

    tier_line_colors = {
        "Normal": "grey",
        "Special": "pink",
        "Uniques": "magenta",
    }
    for tier in range(upgrade_tier_amounts):
        available_armor_types = [
            armor_type
            for armor_type in ("L", "M", "H")
            if (armor_type, tier) in bar_positions
        ]
        for pool_index in range(len(pool_sizes)):
            if len(available_armor_types) < 2:
                continue
            line_positions = [
                bar_positions[(armor_type, tier)][pool_index]
                for armor_type in available_armor_types
            ]
            line_tops = [
                bar_tops[(armor_type, tier)][pool_index]
                for armor_type in available_armor_types
            ]
            tier_name = records_by_key[(tier, pool_sizes[0])]["upgrade_tier_name"]
            plt.plot(
                line_positions,
                line_tops,
                color=tier_line_colors.get(tier_name, "grey"),
                linewidth=0.8,
                zorder=3,
                label="_nolegend_",
            )

    if not show_survived_rounds:
        for group_position, base_average, total_average in zip(
            group_positions, base_averages, total_averages
        ):
            if total_average + 0.15 >= y_max:
                continue
            plt.text(
                float(group_position),
                total_average + 0.15,
                "total avg. dmg" if TRUE_DMG > 0 else base_average_label,
                ha="center",
                va="bottom",
                fontsize=7,
                color="black",
                rotation=0,
            )
            if TRUE_DMG > 0:
                plt.text(
                    float(group_position),
                    total_average - 0.15,
                    f"+{TRUE_DMG:g} dmg",
                    ha="center",
                    va="top",
                    fontsize=7,
                    color="black",
                    rotation=0,
                )
                plt.text(
                    float(group_position),
                    base_average + 0.15,
                    base_average_label,
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
    plt.ylabel("Average rounds survived" if show_survived_rounds else "Damage blocked")
    plt.title(
        "Average Rounds Survived by Armor Group and Upgrade Tier"
        if show_survived_rounds
        else "Damage Blocked by Armor Group and Upgrade Tier"
    )
    plt.grid(axis="y", alpha=0.3)
    plt.ylim(0, chart_y_max)
    base_params = f"Simulation Parameters:\n  Number of sims: {sims}\n  L reduction count: {l_reduction_count}\n  L ignore count: {L_IGNORE_DIE_COUNT}\n  M reduction count: {m_reduction_count}\n  M ignore count: {M_IGNORE_DIE_COUNT}\n  M ignore once: {M_TOTAL_IGNORE_ONCE}\n  M halve once: {M_UNREST_HALVING_ONCE}\n  H ignore count: {H_IGNORE_DIE_COUNT}\n  H ignore once: {H_TOTAL_IGNORE_ONCE}\n  H halving count: {H_HALVING_DIE_COUNT}\n\n  L threshold: {L_HARDNESS}\n  L lowest die max: {L_LOWEST_DIE_MAX}\n  M threshold: {M_HARDNESS}\n  M lowest die max: {M_LOWEST_DIE_MAX}\n  H threshold: {H_HARDNESS}\n  H lowest die max: {H_LOWEST_DIE_MAX}\n  Use lowest max: {USE_LOWEST_DIE_MAX}\n  True-dmg: {TRUE_DMG}\n\n  Rounddown: {rounddown}"
    plt.text(
        0.02,
        0.98,
        base_params,
        transform=plt.gca().transAxes,
        fontsize=8,
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
    )
    if group_legend_by_armor_type:
        plt.legend(
            ncol=4 if show_survived_rounds else 3,
            loc="upper center",
            bbox_to_anchor=(0.5, 0.99),
        )
    else:
        plt.legend()
    plt.tight_layout()

    output_suffix = "9bar_survived_rounds" if show_survived_rounds else "9bar"
    output_file = LOG_DIR / f"d10battlesim_{tier_name.lower()}_{output_suffix}.svg"
    plt.savefig(output_file, format="svg", bbox_inches="tight")
    plt.close() 

    print(" 9 bar chart saved to:")
    print(f"  {output_file}")


dice_amounts = [2, 3, 4, 5, 6, 7, 8, 9, 10]
simdata = run_d10_defense_simulation(
    dice_amounts,
    rounddownYN=rounddown,
    simulate_playerHP=simulate_playerHP,
    run_simple_sim=False
)

# write_simdata_to_txt_file(simdata)
# write_simdata_to_CSV_googleSheet(simdata)

# visualize_simdata(simdata, display_groups_separately=True)
# visualize_simdata_by_upgrade_tier(simdata) # <---

visualize_blocked_damage_grouped_bar_chart(
    simdata,
    y_max=56,
    show_percentage_offset=False,
    group_legend_by_armor_type=True,
)
if simulate_playerHP:
    visualize_blocked_damage_grouped_bar_chart(
        simdata,
        y_max=25,
        show_percentage_offset=False,
        group_legend_by_armor_type=True,
        show_survived_rounds=True,
        fix_survived_rounds_y_max=True,
        survived_rounds_y_max=25
    )
# visualize_blocked_damage_grouped_bar_chart(simdata,armor_types=["L","M","H"],selected_tiers={"L":1,"M":1,"H":1})