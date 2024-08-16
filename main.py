import pandas as pd
from bokeh.plotting import figure, show, output_file, save
from bokeh.models import HoverTool, ColumnDataSource, FactorRange, Select
from bokeh.layouts import column, row
from bokeh.io import curdoc

# Load the dataset
df = pd.read_csv('Titanic-Dataset.csv')

# Data Preparation
# Handle missing values
df['Age'].fillna(df['Age'].median(), inplace=True)
df['Embarked'].fillna(df['Embarked'].mode()[0], inplace=True)
df['Cabin'].fillna('Unknown', inplace=True)

# Create AgeGroup column
bins = [0, 12, 18, 35, 60, 80]
labels = ['Child', 'Teen', 'Young Adult', 'Adult', 'Senior']
df['AgeGroup'] = pd.cut(df['Age'], bins, labels=labels)

# Calculate SurvivalRate
df['Survived'] = df['Survived'].astype(int)
survival_rate = df.groupby('AgeGroup', observed=False)['Survived'].mean() * 100
df['SurvivalRate'] = df['AgeGroup'].map(survival_rate)


# Visualization Functions
def plot_age_group_survival():
    age_groups = df['AgeGroup'].unique()
    age_groups = [group for group in age_groups if pd.notna(group)]
    survival_rates = df.groupby('AgeGroup', observed=False)['Survived'].mean() * 100

    source = ColumnDataSource(data=dict(
        age_group=age_groups,
        survival_rate=survival_rates
    ))

    p = figure(x_range=age_groups, height=400, width=600, title="Survival Rates by Age Group",
               toolbar_location=None, tools="")

    p.vbar(x='age_group', top='survival_rate', width=0.9, source=source, legend_field="age_group",
           line_color='white', fill_color='blue')

    p.add_tools(HoverTool(tooltips=[("Age Group", "@age_group"), ("Survival Rate", "@survival_rate%")]))

    p.y_range.start = 0
    p.xgrid.grid_line_color = None
    p.yaxis.axis_label = 'Survival Rate (%)'
    p.xaxis.axis_label = 'Age Group'
    p.legend.orientation = "horizontal"
    p.legend.location = "top_center"

    return p


def plot_class_gender_survival():
    survival_rate_class_gender = df.groupby(['Pclass', 'Sex'], observed=False)['Survived'].mean().unstack() * 100
    survival_rate_class_gender = survival_rate_class_gender.reset_index()

    classes = ['1st', '2nd', '3rd']
    genders = ['female', 'male']
    data = {'classes': classes}
    for gender in genders:
        data[gender] = survival_rate_class_gender[gender].values

    x = [(cls, gender) for cls in classes for gender in genders]
    counts = sum(zip(data['female'], data['male']), ())

    source = ColumnDataSource(data=dict(x=x, counts=counts))

    p = figure(x_range=FactorRange(*x), height=400, width=600, title="Survival Rates by Class and Gender",
               toolbar_location=None, tools="")

    p.vbar(x='x', top='counts', width=0.9, source=source, line_color='white', fill_color='navy')

    p.add_tools(HoverTool(tooltips=[("Class, Gender", "@x"), ("Survival Rate", "@counts%")]))

    p.y_range.start = 0
    p.xgrid.grid_line_color = None
    p.yaxis.axis_label = 'Survival Rate (%)'
    p.xaxis.axis_label = 'Class, Gender'
    p.xaxis.major_label_orientation = 1

    return p


def plot_fare_survival():
    classes = ['1st', '2nd', '3rd']
    colors = {'1': 'red', '2': 'green', '3': 'blue'}
    df['color'] = df['Pclass'].map(lambda x: colors[str(x)])

    source = ColumnDataSource(df)

    p = figure(height=400, width=600, title="Fare vs. Survival Status",
               toolbar_location=None, tools="")

    p.scatter(x='Fare', y='Survived', size=8, color='color', alpha=0.6, source=source, legend_field='Pclass')

    p.add_tools(HoverTool(tooltips=[("Fare", "@Fare"), ("Survived", "@Survived"), ("Class", "@Pclass")]))

    p.y_range.start = -0.1
    p.y_range.end = 1.1
    p.xaxis.axis_label = 'Fare'
    p.yaxis.axis_label = 'Survived'
    p.legend.title = 'Class'
    p.legend.location = "top_right"

    return p


# Interactivity and Filtering
def update_plot(attr, old, new):
    selected_class = select_class.value
    selected_gender = select_gender.value

    filtered_df = df.copy()

    if selected_class != 'All':
        filtered_df = filtered_df[filtered_df['Pclass'] == int(selected_class)]
    if selected_gender != 'All':
        filtered_df = filtered_df[filtered_df['Sex'] == selected_gender]

    age_group_plot = plot_age_group_survival()
    class_gender_plot = plot_class_gender_survival()
    fare_survival_plot = plot_fare_survival()

    layout.children[1] = age_group_plot
    layout.children[2] = class_gender_plot
    layout.children[3] = fare_survival_plot


# Dropdown for filtering
select_class = Select(title="Class", value="All", options=["All", "1", "2", "3"])
select_gender = Select(title="Gender", value="All", options=["All", "male", "female"])

select_class.on_change('value', update_plot)
select_gender.on_change('value', update_plot)

# Initial plots
age_group_plot = plot_age_group_survival()
class_gender_plot = plot_class_gender_survival()
fare_survival_plot = plot_fare_survival()

# Layout
layout = column(row(select_class, select_gender), age_group_plot, class_gender_plot, fare_survival_plot)
curdoc().add_root(layout)

# Save plots as HTML files
output_file("age_group_survival.html")
save(age_group_plot)

output_file("class_gender_survival.html")
save(class_gender_plot)

output_file("fare_survival.html")
save(fare_survival_plot)

# Display plots
show(layout)
