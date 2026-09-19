import numpy as np #type: ignore
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent / "simdata_logs"
LOG_DIR.mkdir(exist_ok=True)

np.random.seed(1)
sims = 10000

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
def visualize_simdata(simdata, vis_type="total_dmg_lines"):
    import matplotlib.pyplot as plt

    pool_sizes = [data["pool_size"] for data in simdata]
    base_avgs = [data["base_avg"] for data in simdata]
    plt.figure(figsize=(18, 10))
    plt.title("Average Damage by Armor Value - RW Flat Armor Simulation")
    plt.xlabel("Number of d10 dice")
    plt.ylabel("Average Damage")
    plt.grid(True)

    plt.plot(pool_sizes, base_avgs, linestyle=":",marker="x", label="Base Damage")
    if true_dmg > 0:
        true_damage_avgs = [data["avg_nrml_dmg"] for data in simdata]
        plt.plot(pool_sizes, true_damage_avgs, linestyle=":", marker="x", label="Base Damage + True Damage")

    for armor_value in range(1, total_reduction_size + 1):
        averages = [data[f"armor_{armor_value}_avg"] for data in simdata]
        plt.plot(pool_sizes, averages, marker="o", label=f"Armor {armor_value}")

    plt.legend()
    plt.show()

simdata = []

dice_amounts = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
for dice_count in dice_amounts:
    result = run_RW_flat_armor_simulation([dice_count])
    simdata.append(result)

# write_simdata_to_txt_file(simdata)

# write_simdata_to_CSV_googleSheet(simdata)

visualize_simdata(simdata)