import plotly.graph_objects as go
import json

# Parse the data
data_json = {"hackathon_scoring_data": [
  {"criteria": "Functionality", "achieved": 20, "maximum": 20, "description": "Fully functional AI sourcing agent with complete workflow"},
  {"criteria": "Completion", "achieved": 20, "maximum": 20, "description": "Complete end-to-end solution with all components implemented"},
  {"criteria": "Innovation", "achieved": 14, "maximum": 14, "description": "Novel multi-agent approach using CrewAI framework"},
  {"criteria": "User Experience", "achieved": 12, "maximum": 12, "description": "Intuitive CLI interface with rich formatting and progress indicators"},
  {"criteria": "Code Quality", "achieved": 12, "maximum": 12, "description": "Clean, documented, modular code with comprehensive testing"},
  {"criteria": "Technical Difficulty", "achieved": 12, "maximum": 12, "description": "Advanced AI multi-agent system with sophisticated orchestration"},
  {"criteria": "Scalability", "achieved": 10, "maximum": 10, "description": "Cloud-ready architecture with Docker and microservices design"},
  {"criteria": "Presentation", "achieved": 10, "maximum": 10, "description": "Professional documentation, README, and project structure"},
  {"criteria": "Impact & Usefulness", "achieved": 10, "maximum": 10, "description": "Addresses real-world procurement challenges with measurable value"}
]}

scoring_data = data_json["hackathon_scoring_data"]

# Extract data and calculate percentages
criteria = [item["criteria"] for item in scoring_data]
achieved = [item["achieved"] for item in scoring_data]
maximum = [item["maximum"] for item in scoring_data]
percentages = [(a/m)*100 for a, m in zip(achieved, maximum)]

# Determine colors based on percentage ranges using green, yellow, red
colors = []
for pct in percentages:
    if pct >= 90:
        colors.append('#28a745')  # Green for scores >= 90%
    elif pct >= 70:
        colors.append('#ffc107')  # Yellow for scores 70-89%
    else:
        colors.append('#dc3545')  # Red for scores < 70%

# Create text labels showing achieved/maximum (percentage%)
text_labels = [f"{a}/{m} ({p:.0f}%)" for a, m, p in zip(achieved, maximum, percentages)]

# Create horizontal bar chart
fig = go.Figure()

fig.add_trace(go.Bar(
    y=criteria,
    x=achieved,
    orientation='h',
    marker_color=colors,
    text=text_labels,
    textposition='outside',
    cliponaxis=False,
    hovertemplate='<b>%{y}</b><br>Score: %{x}/%{customdata}<br>Achievement: %{text}<br><extra></extra>',
    customdata=maximum
))

# Update layout
fig.update_layout(
    title="AI Sourcing Agent - Hackathon Scoring Analysis",
    xaxis_title="Score",
    yaxis_title="Criteria",
    showlegend=False
)

# Save the chart
fig.write_image("hackathon_scoring_chart.png")