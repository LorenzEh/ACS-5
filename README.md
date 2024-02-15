# ***U.S. County-Level Data Retrieval from the ACS-5 API & Basic Data Exploration***

This project stems from my master’s thesis research, which involved conducting Exploratory Spatial Data Analysis (ESDA) of county level ACS-5 data. Throughout this process, a significant observation emerged: notable disparities exist in the data quality across various regions and variables. A prevailing trend indicates that sparsely populated counties and more specialized variables tend to exhibit lower data quality. To comprehensively understand data quality, streamline the creation of a geoJSON data frame, and gain insights into variable (spatial) distributions and relationships, four distinct functions were developed.

## **Description**

The initial function serves as the primary tool for users, facilitating the retrieval of county-level data from the ACS-5 API. It provides insights into data quality while seamlessly generating a geoJSON data frame. Function 2 automates the creation of boxplots, offering visual representations of the data's distribution. Function 3 generates a scatterplot matrix, allowing users to explore bivariate relationships among variables. Lastly, function 4 produces basic maps displaying variable values for each county across the contiguous USA, Alaska, Hawaii, and Puerto Rico.

*There are three prerequisites necessary for the proper functioning of the code:*

1. A valid API Key.
2. A corresponding shapefile for the requested years.
3. While not mandatory for the functionality of the functions, possessing a basic understanding of ACS-5 is highly beneficial.

Once these preliminary steps are satisfied, you can proceed to visit [https://api.census.gov/data/2019/acs/acs5/subject/variables.json](https://api.census.gov/data/2021/acs/acs5/subject/variables.json) (adjusting the year as needed) to select and explore the variables of interest.

## **Function 1**

### *What can be done with it:*
Request data from the ACS-5 API, calculate the CVs, and create a GeoJSON data frame.

### *Functionality:*
The function takes 5 inputs:

1. **year:**
   - The ACS-5 data should be interpreted as a measurement covering the entirety of the specified time range rather than representing a single point within that period (U.S. Census Bureau, 2020, p. 22). For instance, if you input the year 2019, you're obtaining data for the period spanning from 2015 to 2019. Therefore, it's inappropriate to consider this data as solely representative of the individual years 2015, 2016, 2017, 2018, or 2019; rather, it should be understood as reflecting the entire duration.

2. **variables:**
   - Variables are entered as a list, where each variable is followed by a user-defined custom name. This custom name, entered after the original variable name, can be chosen freely by the user. Utilizing custom names aids in distinguishing between variables, enhancing clarity and organization.

3. **include_moe_columns:**
   - Set True to include MOE columns, else they are not included in the data frame.

4. **include_cv_columns:**
   - Set True to include CV columns, else they are not included in the data frame.

5. **states:**
   - Include a list of States to get data from specific states only.

### *Example Usage:*
![Example Image](https://github.com/LorenzEh/ACS-5/assets/113586171/0ad0608e-44d1-4bb4-9903-55fdd6cae36f)

This example shows how to create the GeoJSON data frame, called “df,” including 4 variables (as mentioned before, the original variable name is followed by the custom name), the MOE, and CV columns for the contiguous USA (the “states” list consists of all states of the contiguous USA).

### *Output:*
The function will first print the number of rows requested from the API. Conversely, it will print certain statistics for each variable. These include:

1. Number of estimates (non-missing values)
2. Missing values (percent of missing values and total missing values)
3. Number of estimates which are zero or missing (percent of estimates zero or missing and total number of estimates which are zero)
4. Percent of CVs > 30

The assessment of U.S. Census data quality involves the utilization of Margin of Errors (MOEs). The U.S. Census Bureau provides MOEs of each estimation at a confidence level of 90%. The MOEs can easily be transformed to Standard Errors (SEs) by dividing the MOEs by 1.645. Subsequently, the Coefficients of Variation (CVs) can be computed by dividing the SEs by the estimate and multiplying it with 100. (U.S. Census Bureau, 2020, p. 55)

Given the nature of many of the ACS-5 variables as rate data or percentage which frequently have 0 as an estimate, division-by-0 errors might occur when calculating the CVs. Therefore, the percentage of CVs > 30 is calculated by dividing the Count of CVs > 30 by the Count of Estimates not zero or missing:

$$Percent\\ of\\ CVs > 30 = \\frac{Count\\ of\\ CVs > 30}{Count\\ of\\ Estimates\\ not\\ zero\\ or\\ missing} \\times 100$$

With Count of CVs > 30 being:

$$Count\\ of\\ CVs > 30 = \\sum_{i = 1}^{n}\\left\\{ \\begin{matrix} 1\\ if\\ df\\left[cv\\_ var\\right]_{i} > 30\\\\ 0\\ otherwise \\\\ \\end{matrix} \\right.$$

And Count of Estimates not zero or missing being:

$$Count\\ of\\ Estimates\\ not\\ zero\\ or\\ missing = \\sum_{i=1}^{n} \\left\\{ \\begin{array}{ll} 1 & \\text{if } df[var]_{i} = \\text{null or } df[var]_{i} = 0 \\\\ 0 & \\text{otherwise} \\end{array} \\right.$$

The example output shows that the total number of missing values and estimates which have zero as value is split between “Percent of Missing Values” and “Percent of Estimates zero or missing”. This gives a sense of how many CVs were calculated without running into a division-by-0 error:

![Example Image 2](https://github.com/LorenzEh/ACS-5/assets/113586171/5765d82c-54fd-4ac9-a815-430a1818de3b)

*Italicized Text:* It´s possible to calculate aggregated CVs of multiple counties following the procedure outlined in the U.S. Census Bureau's general handbook on data usage by (U.S. Census Bureau, 2020, p. 60):

1. Computing the SE of each estimate:

$$SE = \\frac{MOE}{1.645}$$

2. Determining the total SE by aggregating the SEs of each estimate:

$$SE({\\widehat{X}}_{1} + {\\widehat{X}}_{2} + ...  + {\\widehat{X}}_{n}) = \\sqrt{[SE({\\widehat{X}}_{1})]^2 + [SE({\\widehat{X}}_{2})]^2  + ...  + [SE({\\widehat{X}}_{n})]^2}$$

3. Calculating the total CV by dividing the aggregated SE with the aggregated estimate ($\\widehat{X} = \\sum_{i = 1}^{n}X_{i}$) and multiplying it with 100:

$$CV = \\frac{SE}{\\widehat{X}} \\times 100$$

Calculating the aggregated CV for each variable in the contiguous USA offers the advantage that the aggregated estimates are very unlikely to be zero. This contrasts with calculating CVs for each estimate separately, where divide-by-0 errors may occur. However, a cautious approach is warranted when interpreting the figures presented in the table. Firstly, it's crucial to note that deriving the CV from aggregated data is most effective when dealing with a limited number of geographies. Secondly, this approach does not account for the covariance and correlation between the estimates. (U.S. Census Bureau, 2020, p. 61)

This approach has not been included in the function, as it was found, that it tends to give very low CV percentages for large geographies. This could potentially lead users to feel falsely assured when working with ACS-5 data. Therefore, the more conservative method of counting individual CVs over 30 was included. Nonetheless, I included code which you can use to calculate the aggregated CVs.

Lastly, Function 1 created a geo data frame, with the requested columns, and the geography column from the shapefile. As mentioned before, the shapefile has to be downloaded manually and the code needs to be adjusted accordingly (Lines XX-XX)

## **Function 2**

### *What can be done with it:*
Create boxplots for each variable.

### *Functionality:*
Call the function on the whole data frame to get a boxplot for each variable which contains estimates.

### *Output:*
Simple boxplots.

## **Function 3**

### *What can be done with it:*
Create a scatterplot matrix of the variables which contain the estimates.

### *Functionality:*
Call the function on the whole data frame to get a scatterplot matrix and the correlation coefficients for each variable which contain estimates. The variables are standardized before the procedure using scikit-learn's Standard-Scalar (scikit-learn 2024):

$$Z = \\frac{(x - \\overline{x})}{\\sigma(x)}$$

This involves calculating the standardized values (Z) by subtracting the variable mean (\\overline{x}) from the variable value (x) and dividing it by its standard deviation (\\sigma(x)).

### *Output:*
Scatterplot matrix of the standardized variables.

## **Function 4**

### *What can be done with it:*
Create individual maps for the contiguous USA, Alaska, Hawaii, and Puerto Rico.

### *Functionality:*
Call the function with a single variable to get insights of the spatial distribution of the variable. The function will automatically differentiate between the different party of USA and create a map for each of the contiguous parts.

### *Output:*
Individual maps for contiguous USA, Alaska, Hawaii, and Puerto Rico and a color bar legend.

## **Material Used:**

scikit-learn. (2024). sklearn.preprocessing.StandardScaler. Retrieved January 22, 2024, from scikit-learn: [https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html)

U.S. Census Bureau. (2020). *Understanding and Using American Community Survey Data: What All Data Users Need to Know.* Washington, DC: U.S. Government Publishing Office.
