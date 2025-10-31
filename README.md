

# Comparative Study of Rule-Based Strategies in a Two-Player, Three-Dice Ludo Variant 

###  Overview
This project presents a **simulation-based comparative analysis** of *rule-driven gameplay algorithms* in a two-player, three-dice variant of **Ludo** with dynamic board sizes and variable token configurations.  
All simulations were implemented in **Python**, running **10,000 games** under multiple configurations, and results were stored in a **MySQL database** for further analysis.

---

###  Objectives
- To evaluate and compare the effectiveness of four deterministic gameplay algorithms:
  - **Aggressive Strategy:** Prioritizes captures and high-risk advancement.  
  - **Responsible-Pair Strategy:** Focuses on safety and pairing.  
  - **Mixed Strategy:** Combines both approaches probabilistically.  
  - **Smart Strategy:** Adapts rules dynamically to board conditions.  
- To analyze **first-move advantage**, **capture correlation**, and **strategy efficiency** using statistical methods.

---

###  Tech Stack
**Python**, **MySQL**, **NumPy**, **Pandas**, **Matplotlib**, **Seaborn**, **SciPy**

---

###  Simulation Details
- Simulated **10,000 games** across:
  - Board sizes: 7×7, 9×9, 11×11, 13×13  
  - Token counts: 2–4 per player  
  - Move limits: 18–36 per player  
- Logged results include:
  - Game outcomes (win/loss)  
  - Score differentials and capture counts  
  - Strategy used and configuration metadata  

---

###  Statistical Insights
- **First-move advantage** statistically significant on smaller boards.  
- **Player 2 advantage** emerges as board size and move count increase.  
- **Smart Strategy** consistently produced the most balanced win rates across configurations.  
- Capture frequency strongly correlated with higher win probabilities.

---

###  Analysis
- **Hypothesis Testing:** Binomial Test for win-rate significance.  
- **Correlation Studies:** Spearman correlation between captures and wins.  
- **Visualization:** Heatmaps, box plots, violin plots and win-rate curves for strategy comparison.

---

###  Statistical Evaluation
- **Hypothesis Testing:** Two-tailed Binomial Test at α = 0.05  
- **Performance Metrics:** Win rate, average points, mean captures  
- **Visual Analysis:** Heatmaps, violin plots, win-rate curves  

---


