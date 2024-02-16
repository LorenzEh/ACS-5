import requests
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
import geopandas as gpd
plt.rcParams['figure.figsize'] = [15, 15]

def fetch_data(year, variables, include_moe_columns=False, include_cv_columns=False, states=None):
    
    r"""
    
Request data from the ACS-5 API, check the CVs and create a GeoJSON data frame.
        
Preliminaries:
            
        1.) Get an ACS API Key
        2.) Download Shapefile. Important: County shapes might change over the years. 
        Therefore, download the right shapefile from https://www2.census.gov/geo/tiger/ and change the code 
        accordingly: 
    
        s = gpd.read_file(r"C:\Users\loren\Desktop\MA alt\Masterarbeit Indien 2\Masterarbeit\Dataframes\Shapefiles\cb_2019_us_county_20m\cb_2019_us_county_20m.shp") # download shapefile and 
        s["FIPS"] = s["STATEFP"] + s["COUNTYFP"]
        s = s[["FIPS", "geometry"]]
        
Functionalty & Input:
    
        df = fetch_data(2019,                                                       Enter year here 
                        variables = ["S1501_C02_002E", "Less than High School",     Enter variable names here:
                                     "S1902_C02_008E", "Public assistance",         "Variable name1", "Custom Name1" 
                                     "S2507_C02_010E", "House Median Value",        "Variable name2", "Custom Name2" 
                                     "S1703_C04_001E", "Poverty determined"],       (...)
                        include_moe_columns=True,                                   Set True if MOE columns should be in df
                        include_cv_columns=True,                                    Set True if CV columns should be in df
                        states = ["01", "02", "03", "04"])                          Include States as a list of strings
        
        
Output:
            
        1.) Print
        ________________________________________
        ----------Number of rows: 3220----------                                    Total number of estimates (rows) in the dataframe 
        ________________________________________
        ________________________________________
        Variable: Custom Name                                                       Variable name
        Number of Estimates = 1337                                                  Number of estimates of that variable (non missing values)
        Percent of Missing Values: 58.47826086956521                                Percentage of missing values (including total count of missing values)
        Percent of Estimates zero or missing 58.47826086956521                      Percentage of estimate"s which are either missing or have the value "0" (including total count of estimates which are 0)
        Percent of CVs > 30 = 0.0                                                   Percentage of CVs over 30 
        ________________________________________
            
            
        2.) Data Frame
        GeoJSON data frame with the columns requested and "Name", "FIPS" and "geometry column".
"""
    
    try:
        # Extract variable names and display names from the input list
        variable_names = variables[::2]
        display_names = variables[1::2]

        # Construct the list of columns to fetch
        moe_columns = [col.replace("E", "M") for col in variable_names if "E" in col]
        all_columns = variable_names + moe_columns
    
        url = f"https://api.census.gov/data/{year}/acs/acs5/subject"

        # Include states in the request if specified
        if states:
            data_frames = []
            for state in states:
                params = {
                    "get": "NAME," + ','.join(all_columns),   
                    "for": "county:*",
                    "in": f"state:{state}",
                    "key": "ENTER YOUR KEY HERE"
                }
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    state_df = pd.DataFrame(data[1:], columns=data[0])
                    data_frames.append(state_df)
                else:
                    print(f"API request for state {state} failed with status code:", response.status_code)

            df = pd.concat(data_frames, ignore_index=True)
        else:
            params = {
                "get": "NAME," + ','.join(all_columns),
                "for": "county:*",
                "key": "73f8a9893ed1829820a5f19d3f078b3308871681" # Add your API Key here
            }
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                df = pd.DataFrame(data[1:], columns=data[0])
            else:
                print("API request failed with status code:", response.status_code)

        numeric_cols = [col for col in df.columns if col not in ["NAME", "state", "county", "fips"]]

        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df[col] = df[col].apply(lambda x: np.nan if x < 0 else x)

        for var in variable_names:
            moe_var = var.replace("E", "M")
            se_var = var.replace("E", "SE")
            cv_var = var.replace("E", "CV")

            df[se_var] = df[moe_var] / 1.645
            df[cv_var] = (df[se_var] / df[var]) * 100
            df[cv_var].replace([np.inf, -np.inf], np.nan, inplace=True)
            
        rows = len(df)
        
        print("________________________________________")
        print(f"---------Number of rows: {rows}-----------")
        print("________________________________________")
        
        for var, display_name in zip(variable_names, display_names):
            
            # Number of Estimates
            number_of_estimates = df[var].notnull().sum()
            
            # Missing Values
            missing_values = df[var].isnull().sum()
            percent_missing_values = missing_values / rows * 100
            
            # 0 Estimates
            zero_estimates = (df[var] == 0).sum()
            
            # 0 + Missing
            zero_plus_missing = zero_estimates + missing_values
            percent_zero_or_missing = zero_plus_missing / rows * 100
            
            # Calculate statistics using normal variables 
            number_of_estimates_not_0_or_missing = df[(df[var] != 0) & (~df[var].isnull())].shape[0]
            cv_var = var.replace("E", "CV")
            cv_over_30_count = df[(df[cv_var] > 30)].shape[0] 
            percent_over_30 = (cv_over_30_count / number_of_estimates_not_0_or_missing) * 100 
            
            print("________________________________________")
            print(f"Variable: {display_name}")
            print(f"Number of Estimates = {number_of_estimates}")
            # print(f"Missing Values: {missing_values}")
            # print(f"Number of Estimate == 0: {zero_estimates}")
            print(f"Percent of Missing Values: {percent_missing_values} ({missing_values} values missing)")
            # print(f"Estimates zero or missing: {zero_plus_missing}")
            print(f"Percent of Estimates zero or missing: {percent_zero_or_missing} ({zero_estimates} values zero)")
            # print(f"CVs > 30 = {cv_over_30_count}")
            # print(f"Number of Estimates not 0 or Missing: {number_of_estimates_not_0_or_missing}") do i need this? 
            print(f"Percent of CVs > 30: {percent_over_30} ({cv_over_30_count} CVs >30)")
            print("________________________________________")

        # Create output dataframe with custom column names
        output_df = df[variable_names]
        if display_names:
            output_df.columns = display_names

        if include_moe_columns:
            output_df_moe = df[moe_columns]
            moe_renamed_cols = [f"MOE {display_name}" for display_name in display_names]
            output_df_moe.columns = moe_renamed_cols
            output_df = pd.concat([output_df, output_df_moe], axis=1)

        if include_cv_columns:
            output_df_cv = df[[var.replace("E", "CV") for var in variable_names]]
            cv_renamed_cols = [f"CV {display_name}" for display_name in display_names]
            output_df_cv.columns = cv_renamed_cols
            output_df = pd.concat([output_df, output_df_cv], axis=1)

        output_df["FIPS"] = df["state"] + df["county"]
        output_df["Name"] = df["NAME"] 
        
        # Transform to geodataframe (Change as described at the first comment of the function):
        s = gpd.read_file(r"PATH TO YOUR SHAPEFILE") # download shapefile and 
        s["FIPS"] = s["STATEFP"] + s["COUNTYFP"]
        s = s[["FIPS", "geometry"]]

        output_df = pd.merge(output_df, s, on = "FIPS", how='inner')
        output_df = gpd.GeoDataFrame(output_df, geometry = "geometry")

        return output_df

    except Exception as e:
        print("An error occurred:", e)


def boxplot(df):
    
    """
    use boxplot(df) to create a boxplot for each variable which contains estimates
    """
    try:
        # Get the list of columns that are not MOE or CV columns, and exclude 'Name' and 'FIPS'
        variables_to_plot = [col for col in df.columns 
                             if ('MOE' not in col) 
                             and ('CV' not in col) 
                             and (col not in ['Name', 'FIPS', "geometry"])]
    
        # Plotting individual boxplots for each variable
        for variable in variables_to_plot:
            plt.figure(figsize=(12, 6))
            sns.boxplot(data=df[variable], orient='h', showfliers=False, width=0.7, palette='pastel')
            plt.title(f"{variable}")
            plt.tight_layout()
            plt.show()

    except Exception as e:
        print("An error occurred:", e)

def plot_correlation_matrix(data):
    
    """
    use plot_correlation_matrix(df) to create a correlation matrix with each variable which contains estimates
    """
    try:
        # Get the list of columns that are not MOE or CV columns, and exclude 'Name' and 'FIPS'
        variables_to_include = [col for col in data.columns 
                                if ('MOE' not in col) 
                                and ('CV' not in col) 
                                and (col not in ['Name', 'FIPS', "geometry"])]

        correlation_data = data[variables_to_include].copy()

        # Standardize the variables
        scaler = StandardScaler()
        correlation_data_standardized = pd.DataFrame(scaler.fit_transform(correlation_data), columns=variables_to_include)

        # Plot the pairplot for visualizing slopes and data points
        sns.set(style="white")
        pairplot = sns.pairplot(correlation_data_standardized, 
                                kind="reg", 
                                markers=".", 
                                diag_kind="kde",
                                plot_kws={"scatter_kws": {"s": 1},
                                          "line_kws": {"color": "blue",
                                                       "alpha" : 0.6}})
        
        # Add correlation coefficients as annotations
        for i, var1 in enumerate(variables_to_include):
            for j, var2 in enumerate(variables_to_include):              
                if i != j:
                    corr_coef = correlation_data_standardized[[var1, var2]].corr().iloc[0, 1]
                    pairplot.axes[i, j].annotate(f"Corr: {corr_coef:.2f}", xy=(0.5, 0.95), 
                                                 xycoords="axes fraction", ha="center", fontsize=8)

        pairplot.fig.suptitle("Pairplot with Regression Lines, and Correlation Coefficients", y=1.02)

        # Set x and y labels using variable names
        for i, ax in enumerate(pairplot.axes.flatten()):
            ax.set_xlabel(variables_to_include[i % len(variables_to_include)])
            ax.set_ylabel(variables_to_include[i // len(variables_to_include)])

    except Exception as e:
        print("An error occurred:", e)

# Basic mapping: 

def check_plot(df, col):
    """
    use check_plot(df, "variable") to create individual maps of contigous USA, Hawaii, ALaska and Puero Rico
    """
    plt.rcParams.update({"font.size": 15, "legend.fontsize": "small"})

    # Plot for FIPS codes not starting with '02', '72', or '15'
    filtered_fips = df[~df["FIPS"].str.startswith(("02", "72", "15"))]
    if not filtered_fips.empty:
        fig, ax = plt.subplots(figsize=(20, 20))
        filtered_fips.plot(column=col, 
                     legend=True, ax=ax, 
                     legend_kwds={'shrink': 0.3},
                     linewidth = 0.1,
                     figsize=(100, 100),
                     cmap="plasma",
                     missing_kwds={
                         "color": "lightgrey",
                         "edgecolor": "grey",
                         "hatch": "///",
                         "label": "Missing values"})
        ax.set_title("Contiguous USA")
        ax.set_axis_off() 
        plt.show()

    # Plot for FIPS codes starting with '02'
    fips_02 = df[df["FIPS"].str.startswith("02")]
    if not fips_02.empty:
        fig, ax = plt.subplots(figsize=(20, 20))
        fips_02.plot(column=col, 
                     legend=True, ax=ax, 
                     legend_kwds={'shrink': 0.3},
                     linewidth = 0.1,
                     figsize=(100, 100),
                     cmap="plasma",
                     missing_kwds={
                         "color": "lightgrey",
                         "edgecolor": "grey",
                         "hatch": "///",
                         "label": "Missing values"})
        ax.set_title("Alaska")
        ax.set_axis_off() 
        ax.set_xlim([-180, -130])
        plt.show()

    # Plot for FIPS codes starting with '72'
    fips_72 = df[df["FIPS"].str.startswith("72")]
    if not fips_72.empty:
        fig, ax = plt.subplots(figsize=(20, 20))
        fips_72.plot(column=col, 
                     legend=True, ax=ax, 
                     legend_kwds={'shrink': 0.3},
                     linewidth = 0.1,
                     figsize=(100, 100),
                     cmap="plasma",
                     missing_kwds={
                         "color": "lightgrey",
                         "edgecolor": "grey",
                         "hatch": "///",
                         "label": "Missing values"})
        ax.set_title("Puerto Rico")
        ax.set_axis_off() 
        plt.show()

    # Plot for FIPS codes starting with '15'
    fips_15 = df[df["FIPS"].str.startswith("15")]
    if not fips_15.empty:
        fig, ax = plt.subplots(figsize=(20, 20))
        fips_15.plot(column=col, 
                     legend=True, ax=ax, 
                     legend_kwds={'shrink': 0.3},
                     linewidth = 0.1,
                     figsize=(100, 100),
                     cmap="plasma",
                     missing_kwds={
                         "color": "lightgrey",
                         "edgecolor": "grey",
                         "hatch": "///",
                         "label": "Missing values"})
    
        ax.set_title("Hawaii")
        ax.set_axis_off() 
        plt.show()
        
# Example usage

df = fetch_data(2019, 
                variables = ["S1501_C02_002E", "Less than High School", 
                             "S1902_C02_008E", "Public assistance", 
                             "S2507_C02_010E", "House Median Value",
                             "S1703_C04_001E", "Poverty determined",
                             "S0103_C02_085E", "Poverty older than 65"],
                include_moe_columns=True, 
                include_cv_columns=True,
                states = ["01", "04", "05", "06", "08", "09", "10", "11", "12", "13", "16", "17",
                          "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", 
                          "30", "31", "32", "33", "34", "35", "36", "37", "38", "39", "40", "41", 
                          "42", "44", "45", "46", "47", "48", "49", "50", "51", "53", "54", "55", 
                          "56"])

boxplot(df)
plot_correlation_matrix(df)
check_plot(df, "Less than High School")

# extra function to calculate the aggregated CVs

def calculate_aggregated_cv(df):
    cv_results = {}
    
    variables_to_include = [col for col in df.columns 
                            if ('CV' not in col) 
                            and (col not in ['Name', 'FIPS', "geometry"])
                            and col.startswith("MOE ")]

    for moe_col in variables_to_include:
        # Extract the corresponding estimate column name
        col = moe_col.replace("MOE ", "")
        
        # Check if the corresponding estimate column exists
        if col in df.columns:
            # Step 1: Compute SE for each estimate
            df['SE ' + col] = df[moe_col] / 1.645
            
            # Step 2: Accumulate the squared SEs
            total_se_squared = (df['SE ' + col] ** 2).sum()
            
            # Step 3: Calculate the total SE for the current column
            total_se = total_se_squared ** 0.5
            
            # Step 4: Calculate the total CV for the current column
            total_cv = (total_se / df[col].sum()) * 100
            
            # Store the result in the dictionary
            cv_results[col] = total_cv

    return cv_results

# Call the function and store the results, you need the MOE column in the dataframe to make this work. 
aggregated_cv_results = calculate_aggregated_cv(df)