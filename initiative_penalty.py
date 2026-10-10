# simulate and pair initiative bonus values with rulesets that express penalties

from datetime import datetime
from pathlib import Path

# bonus_values = [5,10,15,20,25, 30]
bonus_values = range(1,25,1)
d10_avg = 5.5
d10_avg_disadvantage = 3.85
d10_avg_halfing = 3

LOG_DIR = Path(__file__).resolve().parent / "simdata_logs"
LOG_DIR.mkdir(exist_ok=True)

def initiative_sim():

    # initiative baseline
    def _base_sim():
        results_0 = []
        for bval in bonus_values:
            
            c_resu = d10_avg + bval
            results_0.append(c_resu)
        return results_0
    _base_sim_results = _base_sim()

    # simulation with settings
    def _initiative_sim(name = None,
                    d10_disadvantage = False, 
                    half_bonus = False,
                    half_total = False, 
                    half_d10   = False,
                    rounddown = False,
                    maxBonus = 99):

        if maxBonus == 99:
            maxBonus_niceName = "no"
        else:
            maxBonus_niceName = str(maxBonus)

        settingsData = {    "name"       : name,
                            "d10 disadv.": d10_disadvantage,
                            "half bonus" : half_bonus,
                            "half total" : half_total,
                            "half d10"   : half_d10,
                            "rounddown"  : rounddown,
                            "max Bonus"  : maxBonus_niceName}
        
        result_values = []

        if d10_disadvantage:
            d10val = d10_avg_disadvantage
        else:
            d10val = d10_avg
        if half_d10 and not d10_disadvantage:
            d10val = d10_avg_halfing
        if half_d10 and d10_disadvantage:
            d10val = int(d10val/2)
            

        for bval in bonus_values:
            if bval > maxBonus: bval = maxBonus

            if half_bonus:
                bval = bval / 2
                if rounddown:
                    bval = int(bval)
                else:
                    bval = int(bval) + 1

            c_resu = d10val + bval
            if half_total:
                c_resu = c_resu / 2
                if rounddown:
                    c_resu = int(c_resu)
                else:
                    c_resu = int(c_resu) + 1

            result_values.append(c_resu)


        return result_values, settingsData


    results_A, settings_A = _initiative_sim(
        name="Light|B",
        d10_disadvantage=True)
    
    results_B, settings_B = _initiative_sim(
        name="Medium",
        d10_disadvantage=False,
        half_bonus=True,
        half_total=False,
        rounddown=False,
    )

    results_C, settings_C = _initiative_sim(
        name="Heavy",
        d10_disadvantage=True,
        half_bonus=False,
        half_total=True,
        rounddown=True,
    )

    results_D, settings_D = _initiative_sim(
        name="Heavy",
        half_d10=True,
        half_bonus=True,
        rounddown=True,
    )

    def visualize_initiative_data(results_0, *data_sets):
        import matplotlib.pyplot as plt

        figure, (values_axis, change_axis) = plt.subplots(
            2, 1, sharex=True, figsize=(12.8, 8.64)
        )
        baseline_line = values_axis.plot(
            bonus_values, results_0, marker=".", label="No Armor & Light Armor"
        )[0]

        def annotate_fifth_steps(axis, values, line):
            for bonus, value in zip(bonus_values, values):
                if bonus % 5 == 0:
                    axis.annotate(
                        f"{value:.1f}",
                        (bonus, value),
                        textcoords="offset points",
                        xytext=(0, 3),
                        ha="center",
                        fontsize=8,
                        color=line.get_color(),
                    )

        annotate_fifth_steps(values_axis, results_0, baseline_line)

        percent_changes = {}
        for index, (results, settings_data) in enumerate(data_sets, start=1):
            name = settings_data.get("name") or f"Data set {index}"
            active_settings = [
                key
                for key, value in settings_data.items()
                if key != "name" and value is True
            ]
            max_bonus = settings_data.get("max Bonus", "no")
            if max_bonus != "no":
                active_settings.append(f"max bonus {max_bonus}")
            label = f"{name} ({', '.join(active_settings)})" if active_settings else name

            percent_change = [
                (value - baseline) / baseline * 100
                for baseline, value in zip(results_0, results)
            ]
            percent_changes[name] = percent_change
            values_line = values_axis.plot(bonus_values, results, label=label)[0]
            change_line = change_axis.plot(
                bonus_values,
                percent_change,
                color=values_line.get_color(),
                label=f"{name} vs No Armor",
            )[0]
            annotate_fifth_steps(values_axis, results, values_line)
            annotate_fifth_steps(change_axis, percent_change, change_line)

        values_axis.set_title("Initiative Results by Bonus")
        values_axis.set_ylabel("Average initiative")
        values_axis.grid(True, alpha=0.3)
        values_axis.legend()

        change_axis.axhline(0, color="black", linewidth=1)
        change_axis.set_xlabel("Initiative bonus")
        change_axis.set_ylabel("Change from No Armor (%)")
        change_axis.grid(True, alpha=0.3)
        change_axis.legend()

        figure.tight_layout()
        filename = LOG_DIR / (
            f"initiative_comparison_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.svg"
        )
        figure.savefig(filename, format="svg", bbox_inches="tight")
        plt.close(figure)
        return percent_changes

    percent_changes = visualize_initiative_data(
        _base_sim_results,
        # (results_A, settings_A),
        (results_B, settings_B),
        # (results_C, settings_C),
        (results_D, settings_D),
    )
    return {
        "0": _base_sim_results,
        "A": results_A,
        "B": results_B,
        "C": results_C,
        "percent_changes": percent_changes,
    }

initiative_sim()