fig = plt.figure(figsize=(20, 10))
ax1 = fig.add_subplot(211)

sns.lineplot(x="date", y="filler", color="#EEEEEE", data=for_tl, ax=ax1)
plt.xticks(rotation=20, ha="right")
ax1.set(xticks=for_tl.date.unique(), yticks=[], xlabel="Date", ylabel="", ylim=(0, 3))
plt.title("Timeline of Events for weeks 4-5 of Love Island 2019")

for key, item in storyline.items():
    ax1.axvline(item["date"], color=item["color"], linewidth=item["t"], alpha=0.6)
    ax1.text(item["date"], 2 * item["h"] / 3, key, fontsize=14, weight="bold")
