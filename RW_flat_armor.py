import numpy as np #type: ignore
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent / "simdata_logs"
LOG_DIR.mkdir(exist_ok=True)

np.random.seed(1)
sims = 1000

l_group_label = "Light (L)"
m_group_label = "Medium (M)"
h_group_label = "Heavy (H)"

# ignored dice values for each armor group
l_dice_group = [1,2,3]
m_dice_group = [1,2,3,4,5,6]
h_dice_group = [1,2,3,4,5,6,7,8,9]

total_reduction_size = 9

true_dmg = 0 # can never be reduced, so it is added to the final damage after all reductions


def run_RW_flat_armor_simulation(dice_counts):
    for dc in dice_counts:
        rolls = np.random.randint(1, 11, size=(sims, dc))
        sorted_rolls = np.sort(rolls, axis=1) # ascending
        base_avg = float(np.mean(np.sum(rolls, axis=1)))

        average_damage = {}
        for armor_value in range(1, total_reduction_size + 1):
            reduced_rolls = np.where(sorted_rolls <= armor_value, 0, sorted_rolls)
            average_damage[armor_value] = float(np.mean(np.sum(reduced_rolls, axis=1)))

        return {
            "pool_size": dc,
            "base_avg": base_avg,
            "avg_nrml_dmg": base_avg + true_dmg,
            **{
                f"armor_{armor_value}_avg": average
                for armor_value, average in average_damage.items()
            },
        }
            

# visualize the data using matplotlib
def visualize_simdata_figure1(simdata, vis_type="total_dmg_lines"):
    import matplotlib.pyplot as plt

    pool_sizes = [data["pool_size"] for data in simdata]
    base_avgs = [data["base_avg"] for data in simdata]
    plt.figure(figsize=(18, 10))
    plt.title("Average Damage by Armor Value - RW Flat Armor Simulation")
    plt.xlabel("Number of d10 dice")
    plt.ylabel("Average Damage")
    plt.grid(True)

    line_handles = []
    reduction_labels = []

    base_line = plt.plot(
        pool_sizes, base_avgs, linestyle=":", marker="x", label="Base Damage"
    )[0]
    line_handles.append(base_line)
    reduction_labels.append("Base Damage: 0.00% reduction")

    if true_dmg > 0:
        true_damage_avgs = [data["avg_nrml_dmg"] for data in simdata]
        true_damage_line = plt.plot(
            pool_sizes,
            true_damage_avgs,
            linestyle=":",
            marker="x",
            label="Base Damage + True Damage",
        )[0]
        true_damage_increase = np.mean(
            [
                (true_average - base_average) / base_average * 100
                for base_average, true_average in zip(base_avgs, true_damage_avgs)
                if base_average
            ]
        )
        line_handles.append(true_damage_line)
        reduction_labels.append(
            f"Base Damage + True Damage: +{true_damage_increase:.2f}% damage"
        )

    group_colors = {
        "L": "green",
        "M": "blue",
        "H": "red",
    }
    group_ranges = {
        "L": range(1, 4),
        "M": range(4, 7),
        "H": range(7, 10),
    }
    armor_reductions = []

    for armor_value in range(1, total_reduction_size + 1):
        averages = [data[f"armor_{armor_value}_avg"] for data in simdata]
        group = "L" if armor_value <= 3 else "M" if armor_value <= 6 else "H"
        armor_line = plt.plot(
            pool_sizes,
            averages,
            marker="o",
            color=group_colors[group],
            label=f"Armor {armor_value}",
        )[0]
        average_reduction = np.mean( # type:ignore
            [
                (base_average - armor_average) / base_average * 100
                for base_average, armor_average in zip(base_avgs, averages)
                if base_average
            ]
        )
        line_handles.append(armor_line)
        reduction_labels.append(
            f"Armor {armor_value}: {average_reduction:.2f}% reduction"
        )
        armor_reductions.append(average_reduction)

    group_averages = {
        group: [
            np.mean([data[f"armor_{armor_value}_avg"] for armor_value in armor_values])
            for data in simdata
        ]
        for group, armor_values in group_ranges.items()
    }

    def average_reduction(source, target):
        reductions = [
            (source_average - target_average) / source_average * 100
            for source_average, target_average in zip(
                group_averages[source], group_averages[target]
            )
            if source_average
        ]
        return float(np.mean(reductions)) if reductions else 0.0

    # l_to_m = average_reduction("L", "M")
    # m_to_h = average_reduction("M", "H")
    # l_to_h = average_reduction("L", "H")
    # reduction_summary = (
    #     "Average group damage reduction:\n"
    #     f"L to M: {l_to_m:.2f}%\n"
    #     f"M to H: {m_to_h:.2f}%\n"
    #     f"L to H: {l_to_h:.2f}%"
    # )
    # plt.text(
    #     0.02,
    #     0.98,
    #     reduction_summary,
    #     transform=plt.gca().transAxes,
    #     verticalalignment="top",
    #     bbox={"boxstyle": "round", "facecolor": "white", "alpha": 0.8},
    # )

    chart = plt.gca()
    chart.legend(loc="upper left")
    chart.add_artist(chart.get_legend()) # type:ignore
    chart.legend(
        line_handles,
        reduction_labels,
        title="Average Damage Change",
        loc="upper left",
        bbox_to_anchor=(1.02, 1),
    )
    plt.subplots_adjust(right=0.75)

    reduction_chart = plt.gcf().add_axes([0.78, 0.11, 0.15, 0.45]) # type:ignore
    reduction_chart.plot(
        range(1, total_reduction_size + 1),
        armor_reductions,
        marker="o",
        color="black",
    )
    reduction_chart.set_title("Reduction by Armor", fontsize=9)
    reduction_chart.set_xlabel("Armor", fontsize=8)
    reduction_chart.set_ylabel("Reduction (%)", fontsize=8)
    reduction_chart.tick_params(axis="both", labelsize=8)
    reduction_chart.grid(True, alpha=0.5)
    plt.show()


def visualize_simdata_figure2(simdata):
    import matplotlib.pyplot as plt

    pool_sizes = np.array([data["pool_size"] for data in simdata])
    armor_colors = {
        **dict(zip(range(1, 4), ["#02bc0c", "#3ab340", "#6fa972"])),
        **dict(zip(range(4, 7), ["#5178a4", "#1786e8", "#033797"])),
        **dict(zip(range(7, 10), ["#e85e5b", "#e53935", "#db0909"])),
    }

    plt.figure(figsize=(18, 10))
    for armor_value in range(1, total_reduction_size + 1):
        blocked_averages = [
            data["base_avg"] - data[f"armor_{armor_value}_avg"]
            for data in simdata
        ]
        plt.bar(
            pool_sizes,
            blocked_averages,
            width=1 - (armor_value - 1) * 0.1,
            alpha=0.75,
            color=armor_colors[armor_value],
            edgecolor="white",
            linewidth=0.5,
            label=f"Armor {armor_value}",
        )

    for index, data in enumerate(simdata):
        plt.hlines(
            data["base_avg"],
            pool_sizes[index] - 0.25,
            pool_sizes[index] + 0.25,
            color="grey",
            linewidth=1,
            zorder=10,
            label="Unblocked base damage" if index == 0 else "_nolegend_",
        )

    plt.title("Average Damage Blocked by Armor - RW Flat Armor Simulation")
    plt.xlabel("Number of d10 dice")
    plt.ylabel("Average Damage Blocked")
    plt.xticks(pool_sizes)
    plt.grid(axis="y", alpha=0.3)
    plt.legend(title="Armor Value", loc="upper left", bbox_to_anchor=(1.02, 1))
    plt.subplots_adjust(right=0.85)
    plt.show()

simdata = []

dice_amounts = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
for dice_count in dice_amounts:
    result = run_RW_flat_armor_simulation([dice_count])
    simdata.append(result)

# write_simdata_to_txt_file(simdata)

# write_simdata_to_CSV_googleSheet(simdata)

visualize_simdata_figure1(simdata)
# visualize_simdata_figure2(simdata)